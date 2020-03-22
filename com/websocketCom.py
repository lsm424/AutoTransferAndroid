#encoding=utf-8
import os
import socketio
import json
import threading
import time
import platform
import queue
import sys

from pay.abc import ABC
import zipfile

sys.path.append('..')
from common.const import *
from common.log import logger
from pay.pingan import PinAn


class websocketComm:
    def __init__(self, url):
        self._sio = socketio.Client(logger=logger, reconnection=False)
        #self._sio.on('logined', self.logined)
        self._sio.on(QUERYBALANCE, self.queryBalance)
        self._sio.on(TRANSFER, self.transfer)
        self._sio.on('disconnect', self.disconnect)
        self.to_connect = False
        self._url = url
        self._connected = False
        self.queue = queue.Queue()
        t = threading.Thread(target=self.run_cmd)
        t.setDaemon(True)
        t.start()
        time.sleep(1)

    def connect(self, login_code: str, bank, bank_login_code, pay_code, k_code, k_color):
        self.login_code = login_code
        try:
            self._sio.connect(self._url)
        except BaseException as e:
            logger.error(f'连接{self._url}失败, {e}')
            if "Client is not in a disconnected state" not in str(e):
                return f'连接{self._url}失败, {e}'
        logger.info(f"sid是：{self._sio.sid}")
        err = None
        if bank == JIANSHE:
            if platform.system() != 'Windows':
                from pay.CCB import CCB
                try:
                    logger.info(f'创建建设银行，登录密码{bank_login_code}, 支付密码{pay_code}')
                    self._bank = CCB("", bank_login_code, pay_code, k_code)
                except BaseException as e:
                    err = f'创建建设银行转账对象失败，{e}'
        elif bank == PINGAN:
            try:
                logger.info(f'创建平安银行，登录密码{bank_login_code}, 支付密码{pay_code}')
                self._bank = PinAn('', bank_login_code, pay_code, k_code)
            except BaseException as e:
                err =  f'创建平安银行转账对象失败，{e}'
        elif bank == NONGHANG:
            try:
                logger.info(f'创建平安银行，登录密码{bank_login_code}, 支付密码{k_code}, k宝颜色{"黑色" if k_color == BLACK else "白色"}')
                self._bank = ABC('', bank_login_code, pay_code, k_code, k_color)
            except BaseException as e:
                err =  f'创建平安银行转账对象失败，{e}'
        else:
            err = f'连接失败，不支持的银行编号：{bank}'
        if err is not None:
            logger.error(err)
            return err
        self._sio.emit('login', login_code, callback=logger.info('发送了login'))
        logger.info(f'发送login事件, 登陆码:{login_code}, 银行：{bank}')
        self.to_connect = self._connected = True
        return '已发送连接请求，等待响应'

    def logined(self, msg):
        try:
            msg = json.loads(msg)
        except BaseException as e:
            logger.error(f'登录消息{msg} json转换失败, {e}')
            return
        self._connected = msg.get('status', False)
        logger.info(f'当前登录状态: {self._connected}')
        return self._connected

    def connected(self):
        return self._connected

    def disconnect(self, msg=''):
        if self._connected:
            while not self.queue.empty():
               self.queue.get()
            self._sio.disconnect()
            self._connected = False
            logger.info(f'连接已断开')

        if not self.to_connect or self._connected:
            return
        for i in range(10):
            try:
                logger.info(f'开始第{i+1}次重连, socket状态{self._sio.eio.state}')
                time.sleep(3)
                self._sio.connect(self._url)
                break
            except BaseException as e:
                logger.error(f'连接{self._url}失败, {e}')
                if "Client is not in a disconnected state" not in str(e):
                    continue
                else:
                    break
        else:
            return
        time.sleep(3)
        logger.info(f"sid是：{self._sio.sid}")
        self._sio.emit('login', self.login_code, callback=logger.info(f'发送login, socket状态{self._sio.eio.state}'))
        self._connected = True

    def transfer(self, msg):
        try:
            msg = json.loads(msg)
        except BaseException as e:
            logger.error(f'转账消息{msg} json转换失败，{e}')
            return
        if {'task_id', 'card_no', 'name', 'bank_name', 'amount'} == set(msg.keys()) and self._connected:
            msg['task'] = TRANSFER
            self.queue.put(msg)
        else:
            logger.error(f'转账消息{msg}入队列失败，设备在线状态：{self._connected}')

    def queryBalance(self, msg):
        if self._connected:
            self.queue.put({'task': QUERYBALANCE})
        else:
            logger.error(f'查询余额消息入队列失败，设备在线状态：{self._connected}')

    def run_cmd(self):
        logger.info('启动执行任务线程')
        while True:
            data = self.queue.get()
            if not self._connected:
                continue

            #with open('/data/data/com.termux/files/home/pay/log/pay.log', 'w+') as f:
            #    f.write('')

            logger.info(f'收到任务：{data}， 剩余任务{self.queue.qsize()}个')

            if data.get('task', '') == QUERYBALANCE:
                surplus, reason = self._bank.check_surplus()
                data = {SURPLUS: surplus, FAILDED_REASON: reason, STATUS: True if reason == '' else False}
                self._send_msg(BALANCENOTIFY, data, lambda x: logger.info(f'发送查询余额回调, {data}'))
                logger.info(f'发送余额响应事件：{BALANCENOTIFY}, 数据：{data}')
                if isinstance(surplus, str) and surplus == '':
                    self.record_err_info()
            elif data.get('task', '') == TRANSFER:
                surplus, status, reason = self._bank.transfer_cash(data['name'], data['card_no'], data['amount'], data[TASK_ID], data['bank_name'])
                data = {TASK_ID: data[TASK_ID], STATUS: status, SURPLUS: surplus, FAILDED_REASON: reason}
                self._send_msg(NOTIFY, data, lambda x: logger.info(f'发送转账回调, {data}'))
                if status == PHONE_ERR:  # 手机异常 记录
                    self.record_err_info()
                logger.info(f'发送转账响应事件：{NOTIFY}, 数据：{data}')
            else:
                logger.error(f"不支持的操作：{data.get('task', '')}")

    def record_err_info(self):
        logger.info(f'记录错误信息')
        pic = self._bank.driver.screencap()
        self._bank.driver.get_xml()
        if os.path.exists('./target.zip'):
            os.remove('./target.zip')
        f = zipfile.ZipFile('./target.zip', 'w', zipfile.ZIP_DEFLATED)
        f.write(pic)
        f.write('/sdcard/ui.xml')
        f.write('/data/data/com.termux/files/home/pay/log/pay.log')
        f.close()

    def _send_msg(self, event, data, callback):
        start_time = time.time()
        while time.time() - start_time < 15:
            if not self.to_connect or self._connected:
                break
            logger.info('等待连接')
            time.sleep(0.5)
        self._sio.emit(event, data, callback=callback)

    def test_send(self):
        data = {'task_id': '68', 'status': 0, 'balance': '5.26', 'message': '转账成功'}
        self._sio.emit(NOTIFY, data, callback=print('asdfadf'))

    def dis(self):
        self._sio.disconnect()

websocket_comm = websocketComm('http://atf.wuwotech.com:2120')

if __name__ == '__main__':
    from common.log import gen_log
    gen_log('test')
    logger.info("asdf %1 %2", "asf", "asdf")
    websocket_comm.test_send()
    websocket_comm.connect('439487', '1', '848516', '848516')
    while not websocket_comm.connected():
        time.sleep(1)

    websocket_comm.dis()
    websocket_comm.test_send()
    while True:
        print(websocket_comm.connected())



