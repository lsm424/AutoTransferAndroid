#encoding=utf-8
import time
import re
import traceback
import sys
sys.path.append('..')
from common.shortMsg import MsgManger
from common.driver import Driver
from common.log import logger
from common.MyError import MyError, UserError, NomoneyError
from common.ocr import OCR
from common.const import *

class CCB:
    package = 'com.chinamworld.main'
    main_activity = 'com.ccb.start.MainActivity'
    apk_version = '4.1.5'
    login_key_board = {'1': (0.061, 0.718), '2': (0.155, 0.718), '3': (0.26, 0.718), '4': (0.355, 0.718), '5': (0.455, 0.718),
                       '6': (0.555, 0.718), '7': (0.655, 0.718), '8': (0.755, 0.718), '9': (0.855, 0.718), '0': (0.944, 0.718),
                       'q': (0.061, 0.7984), 'w': (0.155, 0.7984), 'e': (0.26, 0.7984), 'r': (0.355, 0.7984),'t': (0.455, 0.7984),
                       'y': (0.555, 0.7984), 'u': (0.655, 0.7984), 'i': (0.755, 0.7984), 'o': (0.855, 0.7984),'p': (0.944, 0.7984),
                       'a': (0.155, 0.90625), 's': (0.26, 0.90625), 'd': (0.355, 0.90625), 'f': (0.455, 0.90625), 'g': (0.555, 0.90625),
                       'h': (0.655, 0.90625), 'j': (0.755, 0.90625), 'k': (0.855, 0.90625), 'l': (0.944, 0.90625),
                       'z': (0.213, 0.956), 'x': (0.314, 0.956), 'c': (0.407, 0.956), 'v': (0.489, 0.956),
                       'b': (0.6, 0.956), 'n': (0.692, 0.956), 'm': (0.801, 0.956), 'back': (0.926, 0.956)}
    code_key_board = {'1': (0.167, 0.725), '2': (0.5, 0.725), '3': (0.833, 0.725), '4': (0.167, 0.804), '5': (0.5, 0.804),
                       '6': (0.833, 0.804), '7': (0.167, 0.875), '8': (0.5, 0.875), '9': (0.833, 0.875), '0': (0.5, 0.978),
                      '.': (0.167, 0.978)}

    def __init__(self, user, log_passwd, pay_passwd, k_passwd=''):
        self.user = user
        self.passwd = pay_passwd
        self.login_passwd = log_passwd
        self.driver = Driver()
        # 更新页面——关闭更新按钮
        self.__pattern_close = r'resource-id="com.chinamworld.main:id/close"\s+class="android.widget.ImageView".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        self.__pattern_udpate_text = r'更新.+?clickable="true"[\s\S]*clickable="true".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 首页——余额按钮
        self.__pattern_main_remainds = r'text="首页"resource-id="com.chinamworld.main:id/totalMoney".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 首页——首页按钮
        self.__pattern_main_activity_main_page_btn = r'text="首页".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 首页——转账按钮
        self.__pattern_main_activity_transfer_btn = r'text="转账".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 待转账页面——转账按钮
        self.__pattern_transfer_btn = r'text="转账" resource-id="com.chinamworld.main:id/tv_function".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 登录页面——登录按钮
        self.__pattern_login = r'text="登录".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 登录页面——密码控件
        self.__pattern_pw_edit = r'resource-id="com.chinamworld.main:id/et_password".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 转账页面——余额
        self.__pattern_remainds = r'text="人民币\s+活期储蓄\s+(.+?)" resource-id="com.chinamworld.main:id/tv_pay_info"'
        # 转账页面——收款人
        self.__pattern_reciver = r'text="请输入收款户名" resource-id="com.chinamworld.main:id/et_cash_name".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 转账页面——收款账号
        self.__pattern_card = r'text="请输入收款账号或手机号" resource-id="com.chinamworld.main:id/et_collection_account".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 转账页面——金额
        self.__pattern_money = r'text="请输入转账金额" resource-id="com.chinamworld.main:id/et_tran_amount".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 收款银行
        self.__pattern_bank_name = r'text="请选择收款银行" resource-id="com.chinamworld.main:id/tv_bank" class="android.widget.TextView".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 搜索
        self.__pattern_search = r'index="0" text="" resource-id="com.chinamworld.main:id/search_mid_layout" class="android.widget.RelativeLayout".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 转账页面——下一步
        self.__pattern_next = r'text="下一步" resource-id="com.chinamworld.main:id/btn_right1".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 转账页面警告框——继续
        self.__pattern_continue = r'text="继续" resource-id="com.chinamworld.main:id/dlg_right_tv".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 支付页面——验证码控件
        self.__pattern_verify_code = r'resource-id="com.chinamworld.main:id/et_code".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 支付页面——确认按钮
        self.__pattern_ok = r'text="确定" resource-id="com.chinamworld.main:id/btn_confirm".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 支付页面——验证码序号
        self.__pattern_verify_seq = r'已向您手机号.+?发送序号为(\d+)的验证码'
        # 密码页面——密码控件
        self.__pattern_code = r'resource-id="com.chinamworld.main:id/et_code".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 密码页面——图形验证码控件
        self.__pattern_pic_code = r'text="请输入右侧图片的字符" resource-id="com.chinamworld.main:id/native_graph_et".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 密码页面——确认按钮
        self.__pattern_sure = r'text="确定" resource-id="com.chinamworld.main:id/btn_confirm".+?enabled="true".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 密码页面——取消按钮
        self.__pattern_cancle = r'text="取消" resource-id="com.chinamworld.main:id/btn_cancel".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 密码页面——图片区域
        self.__pattern_pic_rect = r'resource-id="com.chinamworld.main:id/native_graph_iv".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 查询结果页面——查询按钮
        self.__pattern_check_result_btn = r'text="查询转账结果" resource-id="com.chinamworld.main:id/btn_right3".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 查询结果页面——取消按钮
        self.__pattern_check_result_cancle_btn = r'text="取消" resource-id="com.chinamworld.main:id/dlg_left_tv".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 查询结果页面——确认按钮
        self.__pattern_check_result_sure_btn = r'text="确定" resource-id="com.chinamworld.main:id/dlg_right_tv".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 异常界面
        self.__pattern_exception = r'text="关闭"\s+resource-id="com.chinamworld.main:id/dlg_right_tv".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 支付页面——关闭框框
        self.__pattern_close_verify_page = r'resource-id="com.chinamworld.main:id/iv_close".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'

        '''
        try:
            self.driver.power_on_screen()
            self.driver.unlock()
            self._enter_main_page()
        except BaseException as e:
            logger.error(f'{e}')
        '''

    def check_surplus(self):
        self.driver.power_on_screen()
        self.driver.unlock()
        logger.info('开始通过建设银行查询余额')
        # 回到首页
        try:
            xml = self._enter_main_page()

            # 从首页进入待转账页面
            xml = self.__enter_prepare_transfer(xml)

            # 从待转账页面进入转账页面
            xml = self.__enter_transfer(xml)

            # 转账页面
            return float(self.__transfer(xml, '', '', '', '', True)[0]), ''
        except BaseException as e:
            logger.error(f'查询余额失败，{e}')
            return '', str(e)

    def transfer_cash(self, reciver, card, money, taskid, bank_name):
        self.driver.power_on_screen()
        self.driver.unlock()
        self._remainds = ''
        logger.info(f'开始通过建设银行给{reciver}的卡{card}转账{money}元')
        try:
            xml = self._enter_main_page()

            # 从首页进入待转账页面
            xml = self.__enter_prepare_transfer(xml)

            # 从待转账页面进入转账页面
            xml = self.__enter_transfer(xml)

            # 转账页面
            self._remainds, xml = self.__transfer(xml, reciver, card, str(money), bank_name)

            # 支付
            xml = self.__pay(self.passwd, xml)

            # 查询结果
            status, reason = self.check_result(xml)
            if status is True:
                self._remainds = round(float(self._remainds) - float(money), 2)
            return self._remainds, OK, reason
        except MyError as e:
            e = f'手机原因: {e}'
            logger.error(e)
            logger.error(traceback.format_exc())
            return self._remainds, PHONE_ERR, str(e)
        except NomoneyError as e:
            e = '卡余额不足'
            logger.error(e)
            logger.error(traceback.format_exc())
            return self._remainds, NO_MONEY, str(e)
        except UserError as e:
            e = f'用户原因: {e}'
            logger.error(e)
            logger.error(traceback.format_exc())
            return self._remainds, USER_ERR, str(e)
        except BaseException as e:
            e = f'其他原因: {e}'
            logger.error(e)
            logger.error(traceback.format_exc())
            return self._remainds, PHONE_ERR, str(e)

    def check_result(self, xml):
        start_time = time.time()
        while time.time() - start_time < 60:
            cur_activity = self.driver.get_cur_activity()
            xml = self.driver.get_xml()
            if self.__handle_random_page(cur_activity, xml):
                start_time = time.time()
                continue
            elif cur_activity == 'com.ccb.framework.security.base.successpage.CcbSuccessPageAct':
                check_result_btn = re.findall(self.__pattern_check_result_btn, xml)
                if len(check_result_btn) == 1:
                    self.__click(check_result_btn[0])
                elif '转账提交成功' in xml or re.search(r'转账成功(.+?)" resource-id="com.chinamworld.main:id/tv_dlg_content"', xml):
                    ret = '转账成功'
                    logger.info(ret)
                    return True, ret
                elif re.search(r'具体原因：(.+?)" resource-id="com.chinamworld.main:id/tv_dlg_content"', xml):
                    ret = re.findall(r'具体原因：(.+?)" resource-id="com.chinamworld.main:id/tv_dlg_content"', xml)[0]
                    logger.info(ret)
                    raise UserError(ret)
            else:
                logger.warning('未知 activity %s' % cur_activity)
        raise MyError('查询转账结果超时')

    # 支付页面
    def __pay(self, code, xml):
        # 密码输入
        def __input_code(xml, code):
            code_controler = re.findall(self.__pattern_code, xml)
            if len(code_controler) != 1:
                logger.error('未找到密码控件')
                return False
            # 输入密码
            self.__click(code_controler[0])
            time.sleep(0.5)
            for c in code:
                x = int(self.code_key_board[c][0] * self.driver.width())
                y = int(self.code_key_board[c][1] * self.driver.height())
                self.driver.click(x, y)

            # 验证码图片
            xml = self.driver.get_xml()
            pic_code = re.findall(self.__pattern_pic_code, xml)
            if len(pic_code) != 1:
                logger.error('未找到图形验证码控件')
                return False
            self.__click(pic_code[0])
            start_time = time.time()
            for i in range(10):
                pic_rect = re.findall(self.__pattern_pic_rect, xml)
                if len(pic_rect) != 1:
                    logger.error('未找到图片区域')
                    time.sleep(0.5)
                    continue
                pic_name = self.driver.screencap()
                ocr = OCR(pic_name)
                pic_rect = pic_rect[0]
                ocr.crop(int(pic_rect[0]), int(pic_rect[1]), int(pic_rect[2]), int(pic_rect[3]))
                ocr.binaryzation(113)
                ocr.save(pic_name + '.verify.png')
                verify_code = ocr.get_text(pic_name + '.verify.png').lower()

                logger.info(f'第{i+1}次输入图形验证码: {verify_code}')
                for c in verify_code:
                    if c==' ':
                        continue
                    x = int(self.login_key_board[c][0] * self.driver.width())
                    y = int(self.login_key_board[c][1] * self.driver.height())
                    self.driver.click(x, y)

                xml = self.driver.get_xml()
                sure = re.findall(self.__pattern_sure, xml)
                if len(sure) != 1:
                    logger.error('验证不正确')
                    for i in range(len(verify_code)):
                        x = int(self.login_key_board['back'][0] * self.driver.width())
                        y = int(self.login_key_board['back'][1] * self.driver.height())
                        self.driver.click(x, y)
                    self.__click(pic_rect)
                    time.sleep(0.5)
                else:
                    logger.info('验证码正确，点击确定')
                    self.__click(sure[0])
                    break
            return True

        start_time = time.time()
        while time.time() - start_time < 60:
            # 更新页面
            cur_activity = self.driver.get_cur_activity()
            xml = self.driver.get_xml()
            if self.__handle_random_page(cur_activity, xml):
                start_time = time.time()
                continue
            elif cur_activity == 'com.ccb.framework.security.transecurityverify.TransSecurityVerifyDialogAct':
                # 校验界面
                if len(re.findall(self.__pattern_pic_code, xml)) == 1:
                    logger.info('已进入密码输入页面')
                    if __input_code(xml, code):
                        start_time = time.time()
                        continue

                verify_code = re.findall(self.__pattern_verify_code, xml)
                if len(verify_code) != 1:
                    logger.error('未找到验证码控件')
                    continue
                verify_seq = re.findall(self.__pattern_verify_seq, xml)
                if len(verify_seq) != 1:
                    logger.error('未找到验证码序列号')
                    continue
                ok = re.findall(self.__pattern_ok, xml)
                if len(ok) != 1:
                    logger.error('未找到确认支付按钮')
                    continue
                verify_seq = verify_seq[0]
                logger.info('验证码序列号为%s' % verify_seq)
                #self.__click(verify_code[0], True)
                # 输入短信验证码
                temp_start = time.time()
                while time.time() - temp_start < 120:
                    msg_list = MsgManger.getMsg('95533')
                    if len(msg_list) == 0:
                        time.sleep(0.5)
                        continue
                    msg = msg_list[0]
                    pattern = f'序号{verify_seq}的验证码(\d+)，您向'
                    ret = re.findall(pattern, msg)
                    if len(ret) != 1:
                        logger.error(f'未能在短信 "{msg}"中匹配到 {pattern}')
                        time.sleep(1.5)
                        continue
                    if re.search(self.__pattern_verify_code, xml):
                        self.__click(re.findall(self.__pattern_verify_code, xml)[0], True)
                    logger.info(f'输入验证码{ret[0]}')
                    for c in ret[0]:
                        x = int(self.code_key_board[c][0] * self.driver.width())
                        y = int(self.code_key_board[c][1] * self.driver.height())
                        self.driver.click(x, y)
                    self.driver.back()
                    start_time = time.time()
                    break
                else:
                    raise MyError(f'未能收到序号为{verify_seq}的验证码')
                #time.sleep(30)
                logger.info('点击确认支付')
                self.__click(ok[0])
            elif cur_activity == 'com.ccb.framework.security.base.successpage.CcbSuccessPageAct':
                logger.info('转账已受理')
                return xml
            else:
                logger.warning('未知 activity %s' % cur_activity)
        raise MyError('支付超时')

    # 处理随机弹出页面：如更新，登录
    def __handle_random_page(self, activity, xml='', back=False):
        xml = self.driver.get_xml() if xml == '' else xml
        if activity == '':
            if len(re.findall(self.__pattern_udpate_text, xml)) == 1:
                ret = re.findall(self.__pattern_udpate_text, xml)
                logger.info('点击取消更新按钮')
                self.__click(ret[0])
                return True
            elif not back and len(re.findall(self.__pattern_continue, xml)) == 1:
                ret = re.findall(self.__pattern_continue, xml)
                logger.info('点击继续按钮')
                self.__click(ret[0])
                return True
        elif activity == 'com.ccb.start.view.startdialog.StartDialogActivity' or activity == 'com.ccb.transfer.transfer_home.view.TransferHomeAct':
            if re.search(self.__pattern_close, xml):
                logger.info('点击叉叉')
                self.__click(re.findall(self.__pattern_close, xml)[0])
                return True
            elif re.search(self.__pattern_udpate_text, xml):
                logger.info('取消更新按钮')
                self.__click(re.findall(self.__pattern_udpate_text, xml)[0])
                return True
        elif back is True and activity == 'com.ccb.transfer.smarttransfer.view.SmartTransferMainAct':
            if len(re.findall(self.__pattern_check_result_cancle_btn, xml)) == 1:
                ret = re.findall(self.__pattern_check_result_cancle_btn, xml)
                logger.info(f'点击转账页面的取消按钮')
                self.__click(ret[0])
                return True
            if len(re.findall(self.__pattern_check_result_sure_btn, xml)) == 1:
                ret = re.findall(self.__pattern_check_result_sure_btn, xml)
                logger.info('点击转账页面的确定按钮')
                self.__click(ret[0])
                return True
        elif back and activity == 'com.ccb.framework.security.base.successpage.CcbSuccessPageAct':
            if len(re.findall(self.__pattern_check_result_sure_btn, xml)) == 1:
                ret = re.findall(self.__pattern_check_result_sure_btn, xml)
                logger.info('点击转账结果页面的确定按钮')
                self.__click(ret[0])
                return True
            elif len(re.findall(self.__pattern_check_result_cancle_btn, xml)) == 1:
                ret = re.findall(self.__pattern_check_result_cancle_btn, xml)
                logger.info('点击转账结果页面的取消按钮')
                self.__click(ret[0])
                return True
        elif activity == 'com.ccb.start.MainActivity':
            if len(re.findall(self.__pattern_udpate_text, xml)) == 1:
                ret = re.findall(self.__pattern_udpate_text, xml)
                logger.info('点击取消更新按钮')
                self.__click(ret[0])
                return True
        elif activity == 'com.ccb.framework.security.login.internal.view.LoginActivity':
            if re.search(self.__pattern_close, xml):
                logger.info('点击叉叉')
                self.__click(re.findall(self.__pattern_close, xml)[0])
                return True
            elif re.search(self.__pattern_udpate_text, xml):
                logger.info('取消更新按钮')
                self.__click(re.findall(self.__pattern_udpate_text, xml)[0])
                return True
            logger.info('进入登录页面')
            ret = re.findall(self.__pattern_pw_edit, xml)
            if len(ret) != 1:
                logger.warning('未找到密码编辑框')
                return False
            logger.info('点击密码编辑框')
            self.__click(ret[0])
            time.sleep(0.5)  # 等待键盘弹出来

            # 匹配登录按钮
            ret = re.findall(self.__pattern_login, xml)
            if len(ret) != 1:
                logger.warning('未找到登录按钮')
                return False

            logger.info('输入密码中')
            for c in self.login_passwd:
                x = int(self.login_key_board[c][0] * self.driver.width())
                y = int(self.login_key_board[c][1] * self.driver.height())
                logger.info(f'{c}, {x}, {y}')
                self.driver.click(x, y)

            logger.info('点击登录按钮')
            self.__click(ret[0])
            time.sleep(2.5)
            return True
        elif re.search(self.__pattern_exception, xml):
            ret = re.findall(self.__pattern_exception, xml)[0]
            self.__click(ret)
            logger.info('点击关闭按钮')
            return True
        else:
            for error_text in ['收款方姓名与账户户名不一致', '交易金额低于总行允许的最低单笔限额']:
                if error_text in xml:
                    if back:
                        self.__click(re.findall(self.__pattern_check_result_sure_btn, xml)[0])
                    else:
                        raise UserError(error_text)
                    return True
            else:
                logger.info(f'未知，activity: {activity}')
        return False

    # 首页进入待转账页面
    def __enter_prepare_transfer(self, xml):
        start_time = time.time()
        main_page_clicked = False
        while time.time() - start_time < 50:
            # 更新页面
            cur_activity = self.driver.get_cur_activity()
            xml = self.driver.get_xml()
            if self.__handle_random_page(cur_activity, xml):
                start_time = time.time()
                continue
            elif cur_activity == 'com.ccb.start.MainActivity':
                '''
                # 匹配首页的首页按钮
                if not main_page_clicked:
                    ret = re.findall(self.__pattern_main_activity_main_page_btn, xml)
                    if len(ret) == 1:
                        logger.info('点击首页的首页按钮')
                        self.__click(ret[0])
                        main_page_clicked = True
                '''
                # 匹配的首页的转账按钮
                ret = re.findall(self.__pattern_main_activity_transfer_btn, xml)
                if len(ret) == 1:
                    logger.info('点击转账按钮')
                    self.__click(ret[0])
            elif cur_activity == 'com.ccb.transfer.transfer_home.view.TransferHomeAct':
                logger.info('已进入待转账页面')
                return xml
            else:
                logger.warning('未知 activity %s' % cur_activity)
        raise MyError('从首页进入转账页面超时')

    # 待转账页面进入正式转账页面
    def __enter_transfer(self, xml):
        start_time = time.time()
        while time.time() - start_time < 50:
            cur_activity = self.driver.get_cur_activity()
            xml = self.driver.get_xml()
            if self.__handle_random_page(cur_activity, xml):
                start_time = time.time()
                continue
            elif cur_activity == 'com.ccb.transfer.transfer_home.view.TransferHomeAct':
                ret = re.findall(self.__pattern_transfer_btn, xml)
                if len(ret) == 1:
                    logger.info('点击待转账页面的转账按钮')
                    self.__click(ret[0])
            elif cur_activity == 'com.ccb.transfer.smarttransfer.view.SmartTransferMainAct':
                logger.info('进入正式转账页面')
                return xml
            else:
                logger.warning('未知 activity %s' % cur_activity)
        raise MyError('从待转账页面进入转账页面超时')

    # 转账页面
    def __transfer(self, xml, name, card, money, bank_name, only4remainds=False):
        start_time = time.time()
        self._remainds = ''
        while time.time() - start_time < 80:
            cur_activity = self.driver.get_cur_activity()
            xml = self.driver.get_xml()
            if self.__handle_random_page(cur_activity, xml):
                start_time = time.time()
                continue
            elif cur_activity == 'com.ccb.transfer.smarttransfer.view.SmartTransferMainAct':
                if re.search(self.__pattern_continue, xml):
                    ret = re.findall(self.__pattern_continue, xml)[0]
                    logger.info('点击继续')
                    self.__click(ret)
                    continue
                if re.search(self.__pattern_check_result_sure_btn, xml):
                    ret = re.findall(self.__pattern_continue, xml)[0]
                    logger.info('点击确定')
                    self.__click(ret)
                    continue
                '''
                ret_remainds = xml.find('活期储蓄')
                if ret_remainds == -1:
                    xml = self.driver.get_xml()
                    ret_remainds = xml.find('活期储蓄')
                    if ret_remainds == -1:
                        logger.error(f'未找到余额, {cur_activity}, {xml}')
                        continue
                ret_remainds = xml[ret_remainds + len('活期储蓄') : ]
                ret_remainds = [float(ret_remainds[: ret_remainds.find('"')])]
                '''
                # 正则表达式不稳定
                ret_remainds = re.findall(self.__pattern_remainds, xml)
                if len(ret_remainds) != 1:
                    logger.error(f'未找到余额, {ret_remainds}')
                    continue

                if only4remainds:
                    logger.info(f'余额：{ret_remainds[0]}')
                    return re.sub(r',', '', ret_remainds[0]), xml

                ret_reciver = re.findall(self.__pattern_reciver, xml)
                if len(ret_reciver) != 1:
                    logger.error('未找到收款人控件')
                    continue
                ret_card = re.findall(self.__pattern_card, xml)
                if len(ret_card) != 1:
                    logger.error('未找到卡号控件')
                    continue
                ret_money = re.findall(self.__pattern_money, xml)
                if len(ret_money) != 1:
                    logger.error('未找到转账金额控件')
                    continue
                ret_next = re.findall(self.__pattern_next, xml)
                if len(ret_next) != 1:
                    logger.error('未找到下一步控件')
                    continue

                self._remainds = re.sub(r',', '', ret_remainds[0])
                logger.info(f'余额：{self._remainds}')
                if float(self._remainds) < float(money):
                    raise NomoneyError(f'余额不足{money}元，当前余额{self._remainds}元')

                logger.info('输入收款人 %s' % name)
                self.__click(ret_reciver[0])
                self.driver.input_text(name)

                logger.info('输入卡号 %s' % card)
                self.__click(ret_card[0])
                for c in card:
                    x = int(self.code_key_board[c][0] * self.driver.width())
                    y = int(self.code_key_board[c][1] * self.driver.height())
                    self.driver.click(x, y)
                self.driver.back()
                time.sleep(2)
                temp_start = time.time()
                while time.time() - temp_start < 30:
                    ret_money = re.findall(self.__pattern_money, self.driver.get_xml())
                    if len(ret_money) != 1:
                        time.sleep(2)
                        continue
                    logger.info('输入金额 %s' % money)
                    self.__click(ret_money[0])
                    for c in money:
                        x = int(self.code_key_board[c][0] * self.driver.width())
                        y = int(self.code_key_board[c][1] * self.driver.height())
                        self.driver.click(x, y)
                    self.driver.back()
                    time.sleep(0.5)
                    xml = self.driver.get_xml()
                    if re.search(self.__pattern_bank_name, xml):
                        raise UserError(f'未选择银行')
                    self.driver.swip(0.5, 0.7, 0.5, 0.3)
                    logger.info('点击下一步')
                    self.__click(ret_next[0])
                    start_time = time.time()
                    break
                else:
                    raise MyError(f'可能网络状况不佳，导致一直找不到输入金额的控件')
            elif cur_activity == 'com.ccb.framework.security.transecurityverify.TransSecurityVerifyDialogAct':
                logger.info('已进入付款页面')
                return self._remainds, xml
            else:
                logger.warning('未知 activity %s' % cur_activity)
        raise MyError('转账页面操作超时')

    # 进入首页
    def _enter_main_page(self):
        #self.driver.stop_app(CCB.package)
        package = self.driver.get_cur_packge()
        # 启动app
        if package != CCB.package:
            self.driver.start_app(CCB.package, CCB.main_activity)
            cur_time = time.time()
            while time.time() - cur_time <= 30:
                if self.driver.is_app_started(CCB.package):
                    logger.info('启动app成功')
                    break
                time.sleep(1)
            for i in range(3):
                if self.driver.is_app_started(CCB.package):
                    break
                time.sleep(0.5)
            else:
                raise MyError('启动APP失败')

        # 进入首页
        start_time = time.time()
        while time.time() - start_time < 30:
            cur_activity = self.driver.get_cur_activity()
            xml = self.driver.get_xml()
            if self.__handle_random_page(cur_activity, xml, True):  # 更新页面
                start_time = time.time()
                continue
            elif cur_activity != 'com.ccb.start.MainActivity':
                if cur_activity == 'com.ccb.framework.security.transecurityverify.TransSecurityVerifyDialogAct':
                    ret = re.findall(self.__pattern_cancle, xml)
                    if len(ret) == 1:
                        self.__click(ret[0])

                    ret = re.findall(self.__pattern_close_verify_page, xml)
                    logger.info(f'{ret}')
                    if len(ret) == 1:
                        self.__click(ret[0])
                elif cur_activity == 'com.ccb.framework.security.base.successpage.CcbSuccessPageAct':
                    ret = re.findall(self.__pattern_cancle, xml)
                    if len(ret) == 1:
                        self.__click(ret[0])
                logger.info('点击返回键')
                self.driver.back()
            else:
                logger.info('已进入首页')
                return xml
            time.sleep(0.5)
        raise MyError('回到APP首页超时失败')

    def __click(self, pos, double=False):
        click_x = (int(pos[0]) + int(pos[2])) // 2
        click_y = (int(pos[1]) + int(pos[3])) // 2
        self.driver.click(click_x, click_y, double)
        #logger.debug(f'clicked {click_x} {click_y}')


if __name__=='__main__':
    driver = Driver()
    serial = '1234567890qwertyuiopasdfghjklzxcvbnm'
    for c in serial:
        x = int(CCB.login_key_board[c][0] * driver.width())
        y = int(CCB.login_key_board[c][1] * driver.height())
        print(c, x, y)
        driver.click(x, y)
