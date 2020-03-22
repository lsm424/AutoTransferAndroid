#encoding=utf-8
import time
import re
import traceback
import os

import sys
sys.path.append('..')
from common.shortMsg import MsgManger
from common.driver import Driver
from common.log import logger
from common.MyError import MyError, UserError, NomoneyError
from common.ocr import OCR
from common.const import *


class PinAn:
    package = 'com.pingan.paces.ccms'
    main_activity = 'com.pingan.pocketbank.splash.PALoadingActivity'
    apk_version = '4.1.5'
    verify_edit = (0.3542, 0.5125)
    login_key_board_character= {'q': (0.069, 0.7319), 'w': (0.155, 0.7319), 'e': (0.26, 0.7319), 'r': (0.355, 0.7319),'t': (0.455, 0.7319),
                       'y': (0.555, 0.7319), 'u': (0.655, 0.7319), 'i': (0.755, 0.7319), 'o': (0.855, 0.7319),'p': (0.944, 0.7319),
                       'a': (0.111, 0.77579), 's': (0.2056, 0.77579), 'd': (0.3018, 0.77579), 'f': (0.4, 0.77579), 'g': (0.4944, 0.77579),
                       'h': (0.599, 0.77579), 'j': (0.6963, 0.77579), 'k': (0.795, 0.77579), 'l': (0.8889, 0.77579),
                       'z': (0.2056, 0.86336), 'x': (0.302, 0.86336), 'c': (0.399, 0.86336), 'v': (0.497, 0.86336),
                       'b': (0.598, 0.86336), 'n': (0.702, 0.86336), 'm': (0.797, 0.86336)}

    char2digital = (0.109, 0.9532)
    finish = (0.9139, 0.6566)
    login_key_board_digital = {'1': (0.1556, 0.6838), '2': (0.513, 0.6838), '3': (0.8278, 0.6838), '4': (0.1556, 0.7741), '5': (0.513, 0.7741),
                       '6': (0.8278, 0.7741), '7': (0.1556, 0.8645), '8': (0.513, 0.8645), '9': (0.8278, 0.8645), '0': (0.513, 0.956),
                        '.': (0.1556, 0.956)}

    def __init__(self, user, log_passwd, pay_passwd, k_passwd=''):
        self.user = user
        self.passwd = pay_passwd
        self.login_passwd = log_passwd
        self.driver = Driver()
        # 首页——首页按钮
        self.__pattern_main_activity_main_page_btn = r'text="首页".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 更新页面——关闭更新按钮
        self.__pattern_cancle = r'text="取消" resource-id="com.pingan.paces.ccms:id/btn_left".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 首页的编辑框
        self.__pattern_search = r'resource-id="com.pingan.paces.ccms:id/base_header_view_middle_search_tv".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]'
        # 编辑框的清空按钮
        self.__pattern_clear = r'text=""\s+resource-id="com.pingan.paces.ccms:id/launcher_header_delete_img"\s+class="android.widget.ImageView".+?clickable="true".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 编辑框的转账选项
        #self.__pattern_tansfer_btn = r'text="转账"\s+resource-id=""\s+class="android.view.View".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'   # 小米
        self.__pattern_tansfer_btn = r'resource-id=""\s+class="android.view.View"\s+package="com.pingan.paces.ccms"\s+content-desc="转账"\s+.+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'    # nexus 5
        # 待转账页面——转账
        #self.__pattern_tansfer = r'text="银行账号转账".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        self.__pattern_tansfer = r'content-desc="银行账号转账".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 转账页面——余额
        #self.__pattern_remainds = r'text="可用余额：([\d\.]+)元"'
        self.__pattern_remainds = r'content-desc="可用余额：([\d\.\,]+)元"'
        # 转账页面——继续转账按钮
        #self.__pattern_continue = r'text="继续转账\s*".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        self.__pattern_continue = r'content-desc="继续转账\s*".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 转账页面——确认按钮
        self.__pattern_sure = r'text="确认".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 转账页面——收款人
        self.__pattern_reciver = r'resource-id="nameInput".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 转账页面——卡号
        self.__pattern_card = r'resource-id="inputCardNum".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 转账页面——金额
        #self.__pattern_money = r'text="免手续费".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        self.__pattern_money = r'content-desc="免手续费".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 转账页面——下一步
        #self.__pattern_next = r'text="下一步".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        self.__pattern_next = r'content-desc="下一步".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 登录页面的登录密码编辑框
        #self.__pattern_login_code = r'text="登录密码".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'   # 6A
        self.__pattern_login_code = r'content-desc="登录密码".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'    # nexus 5
        # 登录页面的登录按钮
        #self.__pattern_login = r'text="登录"\s+resource-id="submit"\s+class="android.widget.Button".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'   # 6A
        self.__pattern_login = r'class="android.widget.Button"\s+package="com.pingan.paces.ccms"\s+content-desc="登录".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'      # nexus 5

        # 收不到短信验证码提示
        self.__pattern_sms_prompt = r'NAF="true" index="1" text="" resource-id="" class="android.view.View" package="com.pingan.paces.ccms".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 取消联系人
        self.__pattern_cancel_contact = r'resource-id="android:id/button1".+?content-desc="取消".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'

    def check_surplus(self):
        self.driver.power_on_screen()
        self.driver.unlock()
        logger.info('开始通过平安银行查询余额')
        # 回到首页
        try:
            self._enter_main_page()

            # 从首页进入待转账页面
            self.__enter_prepare_transfer()

            # 转账页面
            return float(self.__enter_transfer('', '', '', True)), ''
        except BaseException as e:
            logger.error(f'查询余额失败，{e}')
            logger.error(f"{traceback.print_exc()}")
            return '', str(e)

    def transfer_cash(self, reciver, card, money, taskid, bank_name):
        self.driver.power_on_screen()
        self.driver.unlock()
        self._remainds = ''
        logger.info(f'开始通过平安银行给{reciver}的卡{card}转账{money}元')
        try:
            # 回到首页
            self._enter_main_page()

            # 从首页进入待转账页面
            self.__enter_prepare_transfer()

            # 转账页面
            self.__enter_transfer(reciver, card, str(money))

            # 支付
            status, reason = self.__pay(self.passwd)
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

    def _enter_main_page(self):
        #self.driver.stop_app(PinAn.package)
        package = self.driver.get_cur_packge()
        logger.info(f"当前包名：{package}, 平安包名：{PinAn.package}")
        # 启动app
        if package != PinAn.package:
            self.driver.start_app(PinAn.package, PinAn.main_activity)
            cur_time = time.time()
            while time.time() - cur_time <= 30:
                if self.driver.is_app_started(PinAn.package):
                    logger.info('启动app成功')
                    break
                time.sleep(1)
            for i in range(3):
                if self.driver.is_app_started(PinAn.package):
                    break
                time.sleep(0.5)
            else:
                raise MyError('启动APP失败')
        # 进入首页
        start_time = time.time()
        while time.time() - start_time < 60:
            cur_activity = self.driver.get_cur_activity()
            if self.__handle_random_page(cur_activity):  # 更新页面
                start_time = time.time()
                continue
            elif cur_activity != 'com.pingan.launcher.activity.LauncherActivity':
                self.driver.back()
            else:
                logger.info('已进入首页')
                return
        raise MyError('回到APP首页超时失败')

    def __enter_prepare_transfer(self):
        start_time = time.time()
        while time.time() - start_time < 50:
            xml = self.driver.get_xml()
            # 更新页面
            cur_activity = self.driver.get_cur_activity()
            if self.__handle_random_page(cur_activity, xml):
                start_time = time.time()
                continue
            elif cur_activity == 'com.pingan.launcher.activity.LauncherActivity':
                # 匹配首页的首页按钮
                ret = re.findall(self.__pattern_search, xml)
                if len(ret) == 1:
                    logger.info('点击首页的搜索框')
                    self.__click(ret[0])
                else:
                    logger.warning(f'为在首页匹配到搜索框')
            elif cur_activity == 'com.pingan.core.base.VoiceSearchActivity':
                logger.info(f'进入搜索框')
                if re.search(self.__pattern_clear, xml):
                    logger.info(f'点击搜索框的清空图标')
                    self.__click(re.findall(self.__pattern_clear, xml)[0])
                self.driver.input_text('转账')
                # 匹配的首页的转账按钮
                time.sleep(1.5)
                xml = self.driver.get_xml()
                ret = re.findall(self.__pattern_tansfer_btn, xml)
                if len(ret) == 1:
                    logger.info(f'点击搜索框页面的转账按钮')
                    self.__click(ret[0])
                    start_time = time.time()
            elif cur_activity == 'com.pingan.core.base.PocketWebViewActivity':
                logger.info('已进入待转账页面')
                return
            else:
                logger.warning('未知 activity %s' % cur_activity)
        raise MyError('从首页进入转账页面超时')

    def __enter_transfer(self, name, card, money, only4remainds=False):
        start_time = time.time()
        self._remainds = ''
        while time.time() - start_time < 70:
            cur_activity = self.driver.get_cur_activity()
            xml = self.driver.get_xml()
            logger.info(f'---{cur_activity}')
            if self.__handle_random_page(cur_activity, xml):
                start_time = time.time()
                continue
            elif '取款密码' in xml:
                logger.info('进入支付页面')
                return
            elif re.search(self.__pattern_sure, xml):
                logger.info('点击确定')
                self.__click(re.findall(self.__pattern_sure, xml)[0])
                start_time = time.time()
            elif re.search(self.__pattern_continue, xml):
                logger.info('点击继续转账')
                ret = re.findall(self.__pattern_continue, xml)[0]
                self.__click(ret)
                start_time = time.time()
            elif '可用余额' in xml:
                logger.info('进入正式转账页面')
                ret_remainds = re.findall(self.__pattern_remainds, xml)
                if len(ret_remainds) != 1:
                    logger.error(f'未找到余额')
                    continue
                if only4remainds:
                    logger.info(f'余额：{ret_remainds[0]}')
                    return re.sub(',', '', ret_remainds[0])

                ret_reciver = re.findall(self.__pattern_reciver, xml)
                if len(ret_reciver) != 1:
                    logger.error('未找到收款人控件')
                    continue
                ret_card = re.findall(self.__pattern_card, xml)
                if len(ret_card) != 1:
                    logger.error('未找到卡号控件')
                    continue
                ret_next = re.findall(self.__pattern_next, xml)
                if len(ret_next) != 1:
                    logger.error('未找到下一步控件')
                    continue

                self._remainds = re.sub(',', '', ret_remainds[0])
                logger.info(f'余额：{self._remainds}')
                if float(self._remainds) < float(money):
                    raise NomoneyError(f'余额不足{money}元，当前余额{self._remainds}元')

                logger.info('输入卡号 %s' % card)
                self.__click(ret_card[0])
                self.driver.input_text(card)
                xml = self.driver.get_xml()
                if '请选择' in xml:
                    raise UserError(f'卡号不存在')

                logger.info('输入收款人 %s' % name)
                ret_reciver = re.findall(self.__pattern_reciver, xml)
                self.__click(ret_reciver[0])
                self.driver.input_text(name)

                xml = self.driver.get_xml()
                ret_money = re.findall(self.__pattern_money, xml)
                if len(ret_money) != 1:
                    logger.error('未找到转账金额控件')
                    raise MyError('未找到转账金额控件')
                logger.info('输入金额 %s' % money)
                self.__click(ret_money[0])
                time.sleep(1)
                for c in money:
                    x = int(self.login_key_board_digital[c][0] * self.driver.width())
                    y = int(self.login_key_board_digital[c][1] * self.driver.height())
                    self.driver.click(x, y)
                self.driver.click(self.finish[0] * self.driver.width(), self.finish[1] * self.driver.height())
                time.sleep(2)
                xml = self.driver.get_xml()
                if re.search(self.__pattern_cancel_contact, xml):
                    logger.info(f'点击取消联系人按钮')
                    self.__click(re.findall(self.__pattern_cancel_contact, xml)[0])
                    time.sleep(0.5)
                self.driver.swip(0.5, 0.7, 0.5, 0.3)
                ret_next = re.findall(self.__pattern_next,  self.driver.get_xml())
                if len(ret_next) != 1:
                    logger.error('未找到下一步控件')
                    raise MyError('未找到下一步控件')
                logger.info('点击下一步')
                self.__click(ret_next[0])
                start_time = time.time()
            elif cur_activity == 'com.pingan.core.base.PocketWebViewActivity':
                ret = re.findall(self.__pattern_tansfer, xml)
                if len(ret) == 1:
                    logger.info('点击待转账页面的转账按钮')
                    self.__click(ret[0])
            else:
                logger.warning(f'未知 activity {cur_activity}')
        raise MyError('从待转账页面进入转账页面超时')

    def __pay(self, code):
        start_time = time.time()
        while time.time() - start_time < 70:
            # 更新页面
            cur_activity = self.driver.get_cur_activity()
            xml = self.driver.get_xml()
            if self.__handle_random_page(cur_activity, xml):
                start_time = time.time()
                continue
            elif cur_activity == 'com.pingan.core.base.PocketWebViewActivity':
                if '"收不到验证码"' in xml and re.search(self.__pattern_sms_prompt, xml):
                    logger.info(f'取消收不到短信提醒框')
                    self.__click(re.findall(self.__pattern_sms_prompt, xml)[0])
                elif '的取款密码' in xml:
                    logger.info(f'输入取款密码')
                    for c in code:
                        x = int(self.login_key_board_digital[c][0] * self.driver.width())
                        y = int(self.login_key_board_digital[c][1] * self.driver.height())
                        self.driver.click(x, y)
                    msg_start_time = time.time()
                    self.driver.click(self.finish[0] * self.driver.width(), self.finish[1] * self.driver.height())
                    time.sleep(1)
                elif '验证码' in xml and '手机号' in xml and '查收' in xml:
                    logger.info('进入验证码输入界面')
                    temp_start = time.time()
                    while time.time() - temp_start < 120:
                        msg_list = MsgManger.getMsg('95511', int(msg_start_time))
                        if len(msg_list) == 0:
                            time.sleep(1)
                            continue
                        msg = msg_list[0]
                        pattern = f'动态码(\d+)，收款人'
                        ret = re.findall(pattern, msg)
                        if len(ret) != 1:
                            logger.error(f'未能在短信{msg}中匹配到 {pattern}')
                            time.sleep(0.5)
                            continue
                        logger.info('双击验证码编辑框')
                        self.__click([107, 837, 658, 1002], True)
                        logger.info(f'输入验证码{ret[0]}')
                        for c in ret[0]:
                            x = int(self.login_key_board_digital[c][0] * self.driver.width())
                            y = int(self.login_key_board_digital[c][1] * self.driver.height())
                            self.driver.click(x, y)
                        start_time = msg_start_time = time.time()
                        break
                    else:
                        raise MyError('120秒内未能收到短信验证码')
                elif '转账' in xml and '完成' in xml:
                    logger.info('进入转账查询结果界面')
                    if '转账提交成功' in xml:
                        '''
                        logger.info(f'转账成功，等待支付结果短信')
                        temp_start = time.time()
                        while time.time() - temp_start < 40:
                            msg_list = MsgManger.getMsg('106927995511', int(msg_start_time))
                            if len(msg_list) == 0:
                                time.sleep(0.3)
                                continue
                            ret = msg_list[0]
                            logger.info(ret)
                            return True, ret
                        '''
                        return True, ''
                    elif re.search(r'content-desc="转账失败"[\s\S]+?<node index="2".+?content-desc="(.+?)"', xml):
                        ret = re.findall(r'content-desc="转账失败"[\s\S]+?<node index="2".+?content-desc="(.+?)"',xml)[0]
                        logger.info(ret)
                        raise UserError(ret)
            else:
                logger.warning('未知 activity %s' % cur_activity)
        raise MyError('支付超时')

    def __handle_random_page(self, cur_activity, xml=''):
        if cur_activity == 'com.pingan.launcher.activity.LauncherActivity' or cur_activity == PinAn.main_activity:
            xml = self.driver.get_xml() if xml == '' else xml
            if re.search(self.__pattern_cancle, xml):
                logger.info(f'点击取消按钮')
                self.__click(re.findall(self.__pattern_cancle, xml)[0])
                return True
        elif cur_activity == 'com.pingan.core.base.PocketWebViewActivity':
            xml = self.driver.get_xml() if xml == '' else xml
            if re.search(self.__pattern_login_code, xml):
                logger.info(f'进入登录页面')
                self.__click(re.findall(self.__pattern_login_code, xml)[0], xml)
                logger.info(f'输入登录密码')
                cur = CHARACTER
                keyboard = self.login_key_board_character
                for c in self.login_passwd:
                    if c.isdigit() and cur == CHARACTER:
                        self.driver.click(self.char2digital[0] * self.driver.width(),
                                          self.char2digital[1] * self.driver.height())
                        time.sleep(0.5)
                        cur = DIGITAL
                        keyboard = self.login_key_board_digital
                    elif c.isalpha() and cur == DIGITAL:
                        self.driver.click(self.char2digital[0] * self.driver.width(),
                                          self.char2digital[1] * self.driver.height())
                        time.sleep(0.5)
                        cur = CHARACTER
                        keyboard = self.login_key_board_character
                    x = int(keyboard[c][0] * self.driver.width())
                    y = int(keyboard[c][1] * self.driver.height())
                    #self.driver.swip_pos(x, y, x+1, y+1, 1)
                    self.driver.click(x, y)
                self.driver.click(self.finish[0] * self.driver.width(),
                                    self.finish[1] * self.driver.height())
                time.sleep(0.3)
                logger.info('点击登录按钮')
                self.__click(re.findall(self.__pattern_login, self.driver.get_xml())[0])
                return True
        return False

    def __click(self, pos, double=False):
        click_x = (int(pos[0]) + int(pos[2])) // 2
        click_y = (int(pos[1]) + int(pos[3])) // 2
        self.driver.click(click_x, click_y, double)

if __name__ == '__main__':
    test='1234567890'
    d = Driver()
    for c in test:
        x = int(PinAn.login_key_board_digital[c][0] * d.width())
        y = int(PinAn.login_key_board_digital[c][1] * d.height())
        # self.driver.swip_pos(x, y, x+1, y+1, 1)
        d.swip_pos(x, y, x+1,y+1, 0.7)

    x = int(PinAn.finish[0] * d.width())
    y = int(PinAn.finish[1] * d.height())
    # self.driver.swip_pos(x, y, x+1, y+1, 1)
    d.swip_pos(x, y, x + 1, y + 1, 0.7)