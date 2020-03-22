#encoding=utf-8
import json
import os, sys, time
import threading
 
import re

from common.const import *
from common.driver import Driver
from pay.CCB import CCB
from pay.abc import ABC
from pay.pingan import PinAn


def createDaemon():
    # 产生子进程，而后父进程退出
    try:
        print(os.getpid())
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except BaseException as e:
        print('fork failed 1, %s' % e)
        sys.exit(0)

    print(os.getpid())
    # 修改子进程工作目录
    #os.chdir("/")
    # 创建新的会话，子进程成为会话的首进程
    os.setsid()
    # 修改工作目录的umask
    os.umask(0)

    # 创建孙子进程，而后子进程退出
    try:
        pid = os.fork()
        if pid > 0:
            print("Daemon PID %d" % pid)
            sys.exit(0)
    except BaseException as e:
        print('fork failed 2, %s' % e)
        sys.exit(1)
    print(os.getpid())


if __name__ == '__main__':
    createDaemon()
    from common.log import gen_log, logger
    gen_log('pay')
    #logger.info(ABC('', '84851612', '848516', '84851612', '2').transfer_cash('李思明', '6214857554967317', '0.01', '123', '招商银行'))
    #logger.info(CCB('', '848516', '848516').transfer_cash('李思明', '1', '0.01',  '123', '鞍山市商业银行'))
    from com.websocketCom import websocket_comm

    #websocket_comm._connected = True
    #websocket_comm.connect('123','3','12','12','12')
    #data = {'task_id': 123, 'card_no': 12, 'name':1, 'bank_name':'', 'amount':1}
    #websocket_comm.transfer(json.dumps(data))

    def _read_request_thread():
        logger.info(f'启动跟app通信线程, {os.getcwd()}')
        message_input = '/data/data/org.qtproject.example.BankPay/files/config/'
        message_output = '/data/data/org.qtproject.example.BankPay/files/respons/'

        while True:
            for config_file in sorted(os.listdir(message_input)):
                if not re.search(f'meg_(\d+).txt', config_file):
                    continue
                _id = re.findall(f'meg_(\d+).txt', config_file)[0]

                config_file = os.path.join(message_input, config_file)
                logger.info(f'read {config_file} {_id}')
                task = open(config_file, 'r').read()
                os.remove(config_file)
                try:
                    task = json.loads(task)
                except BaseException as e:
                    logger.error(f"错误的任务格式： {task}, {e}")
                    continue
                logger.info(f'收到app信息： {task}')
                job_type = task.get('task', '')
                if job_type == 'connected':
                    file = f"{message_output}/{_id}_{'1' if websocket_comm.connected() else '0'}" + '.txt'
                    logger.info(f'写connected消息{_id}的响应文件 {file}')
                    open(file, 'w+').write('')
                elif job_type == 'connect':
                    try:
                        websocket_comm.to_connect = False
                        websocket_comm.disconnect(force=True)
                        ret = '1'
                    except BaseException as e:
                        ret = '0'
                        pass
                    websocket_comm.connect(task[LOGIN_CODE], task[BANK], task[BANK_LOGIN_CODE], task[CODE], task[KCODE], task[KCOLOR])
                    file = f"{message_output}/{_id}_{ret}'.txt"
                    logger.info(f'写connect消息{_id}的响应文件 {file}')
                    open(message_output + _id + '_' + ret+'.txt', 'w+').write('')
                elif job_type == 'disconnect':
                    websocket_comm.to_connect = False
                    websocket_comm.disconnect()
                    file = f"{message_output}/{_id}_1'.txt"
                    logger.info(f'写disconnect消息{_id}的响应文件 {file}')
                    open(message_output + _id + '_1.txt', 'w+').write('')

    t = threading.Thread(target=_read_request_thread)
    t.setDaemon(True)
    t.start()

    def _screenon_thread():
        driver = Driver()
        while True:
            time.sleep(12)
            if websocket_comm.to_connect:
                driver.power_on_screen()
                driver.unlock()
    s = threading.Thread(target=_screenon_thread)
    s.setDaemon(True)
    s.start()
    '''
    from bottle import Bottle, run, request
    app = Bottle()

    # route()方法用于设定路由；类似spring路由配置
    @app.route('/connected')
    def connected():
        return '1' if websocket_comm.connected() else '0'

    #js.transfer_cash('李思明', '6222620640014891920', '0.01', '848516')
    # /connect?login_code=112262&user=xxx&code=848516&bank=1
    @app.route('/connect')
    def connect():
        if {LOGIN_CODE, USER, CODE, BANK} != set(request.args.keys()):
            logger.error(f'连接请求参数不正确，{request.args} 需包含 {LOGIN_CODE}, {USER}, {CODE}, {BANK}参数')
            return f'连接请求参数不正确，{request.args} 需包含 {LOGIN_CODE}, {USER}, {CODE}, {BANK}参数'
        return websocket_comm.connect(request.args[LOGIN_CODE], request.args[BANK], request.args[USER], request.args[CODE])

    @app.route('/disconnect')
    def disconnect():
        websocket_comm.disconnect()
        pid = os.getpid()
        logger.info(f'----------杀死进程{pid}')
        os.system(f'kill -9 {pid}')
        return '1'

    run(app, host='0.0.0.0', port=8080)
    '''
    while True:
        time.sleep(10)