#encoding=utf-8
import json
import time
import re
import traceback
import sys

import requests

sys.path.append('..')
from common.shortMsg import MsgManger
from common.driver import Driver
from common.log import logger
from common.MyError import MyError, UserError, NomoneyError, RePlayError
from common.ocr import OCR
from common.const import *
from common.keyBoardOcr import KeyBoardOcr

# 农业银行
class ABC:
    package = 'com.android.bankabc'
    main_activity = 'com.android.bankabc.homepage.HomeActivity' # 'com.android.bankabc.SplashActivity'
    apk_version = '4.1.1'

    login_digit_keyboard_templateSign = '78ca7d7b1c20f85bedacf65f61ddbc99'  # 登录键盘数字键盘的模板码
    login_char_keyboard_templateSign = '703be84400e3c37ae2533a9192c66e74'   # 登录键盘字符键盘的模板码
    login_digit2char = (0.6111, 0.942)
    login_char2digit = (0.1296, 0.942)
    login_btn = (0.8889, 0.942)
    login_digit_keyboard = {'key1': (0.1297, 0.6577), 'key2': (0.3722, 0.6577), 'key3': (0.6074, 0.6577),
                            'key4': (0.1297, 0.7609), 'key5': (0.3722, 0.7609), 'key6': (0.6074, 0.7609),
                            'key7': (0.1297, 0.8528), 'key8': (0.3722, 0.8528), 'key9': (0.6074, 0.8528), 'key10': (0.3722, 0.9651)}
    login_char_keyboard = {'key01': (0.0463, 0.6689), 'key02': (0.1509, 0.6689), 'key03': (0.25, 0.6689), 'key04': (0.3537, 0.6689),
                           'key05': (0.4444, 0.6689), 'key06': (0.5481, 0.6689), 'key07': (0.6481, 0.6689), 'key08': (0.7509, 0.6689),
                           'key09': (0.8528, 0.6689), 'key10': (0.9453, 0.6689), 'key11': (0.1019, 0.7816), 'key12': (0.2009, 0.7816),
                           'key13': (0.2991, 0.7816), 'key14': (0.3981, 0.7816), 'key15': (0.4981, 0.7816), 'key16': (0.6065, 0.7816),
                           'key17': (0.6991, 0.7816), 'key18': (0.8028, 0.7816), 'key19': (0.8972, 0.7816), 'key20': (0.2009, 0.8811),
                           'key21': (0.2991, 0.8811), 'key22': (0.3981, 0.8811), 'key23': (0.4981, 0.8811), 'key24': (0.6065, 0.8811),
                           'key25': (0.6991, 0.8811), 'key26': (0.8028, 0.8811)}

    white_pay_digit_keyboard_templateSign = 'cb9df66d98ee5a08702866d85cf66c99'    # 白色款支付键盘数字键盘的模板码
    white_pay_char_keyboard_templateSign = '1a889cefba4710dc980c27e6870ad3c3'     # 白色款支付键盘字符键盘的模板码
    white_pay_digit2char = (0.8740, 0.98)
    pay_btn = (0.6731, 0.5678)
    white_pay_digit_keyboard = {'key1': (0.1222, 0.8067), 'key2': (0.3722, 0.8067), 'key3': (0.6167, 0.8067), 'key4': (0.8740, 0.8067),
                          'key5': (0.1222, 0.8942), 'key6': (0.3722, 0.8942), 'key7': (0.6167, 0.8942), 'key8': (0.8740, 0.8528),
                          'key9': (0.1222, 0.98), 'key10': (0.3722, 0.98)}
    white_pay_char_keyboard = {'key01': (0.0491, 0.8062), 'key02': (0.1454, 0.8062), 'key03': (0.2417, 0.8062), 'key04': (0.3463, 0.8062), 'key05': (0.4519, 0.8062), 'key06': (0.5417, 0.8062), 'key07': (0.64, 0.8062), 'key08': (0.7472, 0.8062), 'key09': (0.8472, 0.8062), 'key10': (0.9426, 0.8062),
                         'key11': (0.0491, 0.8937), 'key12': (0.1454, 0.8937), 'key13': (0.2417, 0.8937), 'key14': (0.3463, 0.8937), 'key15': (0.4519, 0.8937), 'key16': (0.5417, 0.8937), 'key17': (0.64, 0.8937), 'key18': (0.7472, 0.8937), 'key19': (0.8472, 0.8937), 'key20': (0.9426, 0.8937),
                                                    'key21': (0.1454, 0.9778), 'key22': (0.2417, 0.9778), 'key23': (0.3463, 0.9778), 'key24': (0.4519, 0.9778), 'key25': (0.5417, 0.9778), 'key26': (0.64, 0.9778)}

    black_pay_digit_keyboard_templateSign = '854df9b3c1c0203d954eb0470cb59f01'    # 黑色款支付键盘数字键盘的模板码
    black_pay_char_keyboard_templateSign = ''     # 黑色款支付键盘字符键盘的模板码
    black_pay_digit2char = (0.8935, 0.9532)
    black_pay_digit_keyboard = {'key1': (0.1296, 0.7971), 'key2': (0.3704, 0.7971), 'key3': (0.6292, 0.7971), 'key4': (0.8704, 0.7971),
                          'key5': (0.1296, 0.8751), 'key6': (0.3704, 0.8751), 'key7': (0.6292, 0.8751), 'key8': (0.8704, 0.8751),
                          'key9': (0.1296, 0.9532), 'key10': (0.3704, 0.9532)}
    black_pay_char_keyboard = {}

    url = 'http://atf.wuwotech.com/api/equipment/kcard'
    def __init__(self, user, log_passwd, pay_passwd, k_passwd, k_color):
        self.k_passwd = k_passwd
        self.user = user
        self.passwd = pay_passwd
        self.login_passwd = log_passwd
        self.kcolor=  k_color
        self.driver = Driver()
        # 更新页面——关闭更新按钮
        self.__pattern_close = r'resource-id="com.chinamworld.main:id/close"\s+class="android.widget.ImageView".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        self.__pattern_udpate_text = r'更新.+?clickable="true"[\s\S]*clickable="true".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 首页——余额按钮
        self.__pattern_main_remainds = r'text="首页"resource-id="com.chinamworld.main:id/totalMoney".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 确认按钮
        self.__pattern_sure = r'text="\s*确定\s*".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        self.__pattern_next_pay = r'text="\s*下一步\s*".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 完成按钮
        self.__pattern_complish = r'text="\s*完成\s*".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 返回按钮
        self.__pattern_back = r'text="\s*返回\s*".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 首页——转账按钮
        self.__pattern_main_activity_transfer_btn = r'text="转账".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 待转账页面——转账按钮
        self.__pattern_transfer_btn = r'text="转账".+?class="android.widget.TextView".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 登录页面——登录按钮
        self.__pattern_login = r'text="登录".+?class="android.widget.Button".+?clickable="true".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 登录页面——密码控件
        self.__pattern_pw_edit = r'text="请输入登录密码".+?class="android.widget.EditText".+?clickable="true".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 登录页面——返回控件
        self.__pattern_back_edit = r'NAF="true".+?text="".+?class="android.widget.Button".+?clickable="true".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 转账页面——余额
        self.__pattern_remainds = r'text="可用金额\s*(.+?)\s*元" resource-id="" class="android.widget.TextView"'
        # 转账页面——收款人
        self.__pattern_reciver = r'text="请输入或选择收款方" resource-id="" class="android.widget.EditText".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 转账页面——收款账号
        self.__pattern_card = r'text="请输入账号或手机号" resource-id="" class="android.widget.EditText".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 转账页面——金额
        self.__pattern_money = r'text="请输入转账金额" resource-id="" class="android.widget.EditText".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 转账页面——下一步
        self.__pattern_next = r'text="下一步" resource-id="" class="android.widget.Button".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 收款银行
        self.__pattern_bank_name = r'text="请选择银行" resource-id="" class="android.widget.TextView".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        # 搜索
        self.__pattern_search = r'text="搜索" resource-id="com.android.bankabc:id/edt_search" class="android.widget.EditText".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'

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
        # 密码页面——取消按钮
        self.__pattern_cancle = r'text="取消" resource-id="android:id/button2".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
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

        self.__keyboardocr = KeyBoardOcr()

    def check_surplus(self):
        self.driver.power_on_screen()
        self.driver.unlock()
        logger.info('开始通过农业银行查询余额')
        # 回到首页
        try:
            xml = self._enter_main_page()

            # 从待转账页面进入转账页面
            xml = self.__enter_transfer(xml)

            # 转账页面
            return float(self.__transfer(xml, '', '', '', '', True)[0]), ''
        except BaseException as e:
            logger.error(f'查询余额失败，{e}')
            return '', str(e)

    def transfer_cash(self, reciver, card, money, taskid, bank_name):
        self.taskid = taskid
        self.driver.power_on_screen()
        self.driver.unlock()
        self._remainds = ''
        logger.info(f'开始通过平安银行给{reciver}的{bank_name}卡{card}转账{money}元')
        while True:
            try:
                xml = self._enter_main_page()

                # 从待转账页面进入转账页面
                xml = self.__enter_transfer(xml)

                # 转账页面
                self._remainds, xml = self.__transfer(xml, reciver, card, str(money), bank_name)

                # 支付
                xml = self.__pay(self.k_passwd, xml)

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
            except RePlayError as e:
                logger.info('重新开始操作app')
            except BaseException as e:
                e = f'其他原因: {e}'
                logger.error(e)
                logger.error(traceback.format_exc())
                return self._remainds, PHONE_ERR, str(e)

    def check_result(self, xml):
        start_time = time.time()
        while time.time() - start_time < 180:
            cur_activity = self.driver.get_cur_activity()
            xml = self.driver.get_xml()
            if self.__handle_random_page(cur_activity, xml):
                logger.info()
                start_time = time.time()
                continue
            elif '转账已受理' in xml or '转账成功' in xml:
                self.send_status(self.taskid, 0)
                ret = '转账成功'
                logger.info(ret)
                self.__click(re.findall(self.__pattern_complish, xml)[0])
                return True, ret
            elif '账号户名不符' in xml:
                self.send_status(self.taskid, 0)
                ret = '账号户名不符'
                logger.info(ret)
                self.__click(re.findall(self.__pattern_back, xml)[0])
                return False, ret
            elif '通讯中断啦' in xml:
                self.send_status(self.taskid, 0)
                raise UserError(f'用户未点击k宝的ok键')
            else:
                logger.warning('未知 activity %s' % cur_activity)
        raise MyError('查询转账结果超时')

    # 支付页面
    def __pay(self, code, xml):
        # 密码输入
        logger.info(f'输入支付密码 ')
        cur = DIGITAL if self.kcolor == WHITE else CHARACTER
        pay_digit2char = self.white_pay_digit2char if self.kcolor == WHITE else self.black_pay_digit2char   # 数字和字母键盘的切换按钮
        pay_digit_keyboard = self.white_pay_digit_keyboard if self.kcolor == WHITE else self.black_pay_digit_keyboard   #数字键盘
        pay_char_keyboard = self.white_pay_char_keyboard if self.kcolor == WHITE else self.black_pay_char_keyboard  # 字母键盘
        # 数字键盘识别码
        pay_digit_keyboard_templateSign = self.white_pay_digit_keyboard_templateSign if self.kcolor == WHITE else self.black_pay_digit_keyboard_templateSign
        # 字母键盘识别码
        pay_char_keyboard_templateSign = self.white_pay_char_keyboard_templateSign if self.kcolor == WHITE else self.black_pay_char_keyboard_templateSign
        pay_keyboard = pay_digit_keyboard if self.kcolor == WHITE else pay_char_keyboard    # 当前键盘
        keyboard = None
        for c in code:
            if c.isdigit() and cur == CHARACTER:  # 切换数字键盘
                logger.info(f'切换数字键盘 {c.isdigit()} {cur}')
                self.driver.click(pay_digit2char[0] * self.driver.width(),
                                  pay_digit2char[1] * self.driver.height())
                keyboard = KeyBoardOcr.Ocr(self.driver.screencap(), pay_digit_keyboard_templateSign)
                logger.info(f'百度识别的键盘位置为：{keyboard}')
                pay_keyboard = pay_digit_keyboard
                cur = DIGITAL
            elif c.isalpha() and cur == DIGITAL:  # 切换字母键盘
                logger.info(f'切换字母键盘 {c.isalpha()} {cur}')
                self.driver.click(pay_digit2char[0] * self.driver.width(),
                                  pay_digit2char[1] * self.driver.height())
                keyboard = KeyBoardOcr.Ocr(self.driver.screencap(), pay_char_keyboard_templateSign)
                logger.info(f'百度识别的键盘位置为：{keyboard}')
                pay_keyboard = pay_char_keyboard
                cur = CHARACTER

            if not keyboard:
                keyboard = KeyBoardOcr.Ocr(self.driver.screencap(),
                                           pay_digit_keyboard_templateSign if self.kcolor == WHITE else pay_char_keyboard_templateSign)
                logger.info(f'百度识别的键盘位置为：{keyboard}')

            for i in range(3):
                if c in keyboard:
                    pos = pay_keyboard[keyboard[c]]
                    pos = (int(pos[0] * self.driver.width()), int(pos[1] * self.driver.height()))
                    self.driver.click(pos[0], pos[1])
                    logger.info(f'{c}{pos}')
                    break
                keyboard = KeyBoardOcr.Ocr(self.driver.screencap(), pay_char_keyboard_templateSign if c.isalpha() else pay_digit_keyboard_templateSign)
            else:
                raise MyError('无法在支付%s键盘识别字母%s， %s' % ('数字' if cur==DIGITAL else '字母', c, keyboard))
        self.driver.click(self.pay_btn[0] * self.driver.width(), self.pay_btn[1] * self.driver.height())
        self.send_status(self.taskid, 2)

    # 处理随机弹出页面：如更新，登录
    def __handle_random_page(self, activity, xml='', back=False):
        xml = self.driver.get_xml() if xml == '' else xml
        if re.search(self.__pattern_sure, xml) and '会话超时' in xml:
            logger.info(f'会话超时，点击确定按钮')
            self.__click(re.findall(self.__pattern_sure, xml)[0])
            raise RePlayError('')
        elif re.search(self.__pattern_cancle, xml) and ('确定' not in xml or back):
            logger.info('点击取消')
            self.__click(re.findall(self.__pattern_cancle, xml)[0])
            return True
        elif re.search(self.__pattern_sure, xml):
            if back or '确定转账' in xml:
                if back and '确定转账' in xml:
                    return False
                if re.search(self.__pattern_sure, xml):
                    self.__click(re.findall(self.__pattern_sure, xml)[0])
                elif re.search(self.__pattern_next_pay, xml):
                    self.__click(re.findall(self.__pattern_next_pay, xml)[0])
                return True
            elif '请输入收款账户' in xml:
                raise UserError(f"用户未提供收款账户")
            elif '请输入收款方' in xml:
                raise UserError(f'用户未提供收款账户')
            elif '请选择或输入转账金额' in xml:
                raise UserError(f'用户未提供转账金额')
            elif '未搜索到您的k宝' in xml:
                raise UserError(f'未打开k宝')
            elif '蓝牙k宝连接顿开' in xml:
                raise UserError(f'蓝牙k宝连接顿开')
            else:
                return False
        elif back is True and  '继续转账' in xml and re.search(self.__pattern_complish, xml):
            logger.info(f'点击完成 ')
            self.__click(re.findall(self.__pattern_complish, xml)[0])
            return True
        elif (back is True or '会话超时，请重新登录' in xml) and re.search(self.__pattern_back, xml):
            logger.info(f'点击返回 ')
            self.__click(re.findall(self.__pattern_back, xml)[0])
            return True
        elif activity == 'com.android.bankabc.MainActivity' and re.search(self.__pattern_login, xml):
            if back is True:  # 在登录界面处于返回状态，则按返回图标，  返回键在此界面没有用
                if re.search(self.__pattern_back_edit, xml):
                    self.__click(re.findall(self.__pattern_back_edit, xml)[0])
                    return True
                else:
                    return False
            else:
                logger.info(f'进入登录页面')
                self.__click(re.findall(self.__pattern_pw_edit, xml)[0])
                time.sleep(1)
                cur = DIGITAL
                keyboard = KeyBoardOcr.Ocr(self.driver.screencap(), self.login_digit_keyboard_templateSign)
                login_keyboard = self.login_digit_keyboard
                for c in self.login_passwd:
                    if c.isdigit() and cur == CHARACTER:  # 切换数字键盘
                        logger.info(f'切换数字键盘 {c.isdigit()} {cur}')
                        self.driver.click(self.login_char2digit[0] * self.driver.width(),
                                          self.login_char2digit[1] * self.driver.height())
                        keyboard = KeyBoardOcr.Ocr(self.driver.screencap(), self.login_digit_keyboard_templateSign)
                        login_keyboard = self.login_digit_keyboard
                        cur = DIGITAL
                    elif c.isalpha() and cur == DIGITAL:  # 切换字母键盘
                        logger.info(f'切换字母键盘 {c.isalpha()} {cur}')
                        self.driver.click(self.login_digit2char[0] * self.driver.width(),
                                          self.login_digit2char[1] * self.driver.height())
                        keyboard = KeyBoardOcr.Ocr(self.driver.screencap(), self.login_char_keyboard_templateSign)
                        login_keyboard = self.login_char_keyboard
                        cur = CHARACTER

                    for i in range(3):
                        if c in keyboard:
                            pos = login_keyboard[keyboard[c]]
                            pos = (int(pos[0] * self.driver.width()), int(pos[1] * self.driver.height()))
                            self.driver.click(pos[0], pos[1])
                            logger.info(f'{c}{pos}')
                            break
                        templateSign = self.login_char_keyboard_templateSign if c.isalpha() else self.login_digit_keyboard_templateSign
                        keyboard = KeyBoardOcr.Ocr(self.driver.screencap(), templateSign)
                    else:
                        xml = self.driver.get_xml()
                        if re.search(self.__pattern_login, xml):
                            raise MyError('无法在登录%s键盘识别字母%s， %s' % ('数字' if cur==DIGITAL else '字母', c, keyboard))
                        elif '请输入或选择收款方' in xml:  # 此时进入了转账页面
                            logger.info(f'走出登录页面')
                            return True
                self.driver.click(self.login_btn[0] * self.driver.width(), self.login_btn[1] * self.driver.height())
                time.sleep(1)
            return True
        return False

    # 待转账页面进入正式转账页面
    def __enter_transfer(self, xml):
        start_time = time.time()
        while time.time() - start_time < 50:
            cur_activity = self.driver.get_cur_activity()
            xml = self.driver.get_xml()
            if self.__handle_random_page(cur_activity, xml):
                start_time = time.time()
                continue
            elif cur_activity == 'com.android.bankabc.MainActivity':  # 待转账页面和转账页面
                if re.search(self.__pattern_reciver, xml):
                    logger.info('进入正式转账页面')
                    return xml
                ret = re.findall(self.__pattern_transfer_btn, xml)
                if len(ret) == 2 and '他行转本行' in xml:
                    logger.info('点击待转账页面的转账按钮')
                    self.__click(ret[1])
            else:
                logger.warning('未知 activity %s' % cur_activity)
        raise MyError('从待转账页面进入转账页面超时')

    # 转账页面
    def __transfer(self, xml, name, card, money, bank_name, only4remainds=False):
        start_time = time.time()
        self._remainds = ''
        while time.time() - start_time < 100:
            cur_activity = self.driver.get_cur_activity()
            xml = self.driver.get_xml()
            if self.__handle_random_page(cur_activity, xml):
                start_time = time.time()
                continue
            elif '提交了一笔转相同' in xml and re.search(self.__pattern_sure, xml):
                self.__click(re.findall(self.__pattern_sure, xml)[0])
            elif cur_activity == 'com.android.bankabc.MainActivity' and '请输入转账金额' in xml:
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

                self._remainds = re.sub(r',', '', ret_remainds[0])
                logger.info(f'余额：{self._remainds}')
                if float(self._remainds) < float(money):
                    raise NomoneyError(f'余额不足{money}元，当前余额{self._remainds}元')

                logger.info('输入收款人 %s' % name)
                self.__click(ret_reciver[0], cnt=2)
                time.sleep(0.2)
                self.driver.input_text(name)
                time.sleep(0.2)

                logger.info('输入卡号 %s' % card)
                self.__click(ret_card[0], cnt=2)
                self.driver.input_text_by_adb(card)
                self.__click(ret_money[0], cnt=2)
                time.sleep(1)

                logger.info('输入金额 %s' % money)
                self.__click(ret_money[0], cnt=2)
                time.sleep(0.2)
                self.driver.input_text_by_adb(money)

                xml = self.driver.get_xml()
                if re.search(self.__pattern_bank_name, xml):
                    logger.info(f'未找到银行{bank_name}，搜索去找')
                    self.__click(re.findall(self.__pattern_bank_name, xml)[0], cnt=1)
                    search_time = time.time()
                    while time.time() - search_time < 10:
                        xml = self.driver.get_xml()
                        if not re.search(self.__pattern_search, xml):
                            continue
                        self.__click(re.findall(self.__pattern_search, xml)[0], cnt=1)
                        logger.info(f'输入银行{bank_name}')
                        self.driver.input_text(bank_name)

                        search_time = time.time()
                        pattern = f'text="\s*{bank_name}\s*" resource-id="com.android.bankabc:id/tv_title" class="android.widget.TextView".+?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
                        logger.info(f'用正则查找银行 {pattern}')
                        while time.time() - search_time < 10:
                            xml = self.driver.get_xml()
                            if not re.search(pattern, xml):
                                continue
                            self.__click(re.findall(pattern, xml)[0])
                            time.sleep(1)
                            break
                        else:
                            raise UserError(f'卡号{card}对应的银行{bank_name}不存在')
                        break
                    else:
                        raise MyError(f'进入银行选择界面超时')

                self.driver.swip(0.5, 0.7, 0.5, 0.3)
                xml = self.driver.get_xml()
                logger.info('点击下一步')
                ret_next = re.findall(self.__pattern_next, xml)
                if len(ret_next) == 0:
                    raise MyError("未能找到'下一步'按钮")
                self.__click(ret_next[0])
                # 发http请求通知打开k宝
                self.send_status(self.taskid, 1)
                start_time = time.time()
            elif '未搜索到您的K宝' in xml:
                self.send_status(self.taskid, 0)
                raise UserError('用户未打开k宝')
            elif '请输入K宝密码' in xml:
                logger.info('已进入付款页面')
                return self._remainds, xml
            else:
                logger.warning('未知 activity %s' % cur_activity)
        raise MyError('转账页面操作超时')

    # 进入首页
    def _enter_main_page(self):
        #self.driver.stop_app(ABC.package)
        package = self.driver.get_cur_packge()
        # 启动app
        if package != ABC.package:
            self.driver.start_app(ABC.package, ABC.main_activity)
            time.sleep(10)
            cur_time = time.time()
            while time.time() - cur_time <= 30:
                if self.driver.is_app_started('com.android.bankabc'):
                    logger.info('启动app成功')
                    break
                time.sleep(1)
            for i in range(3):
                if self.driver.is_app_started('com.android.bankabc'):
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
            elif cur_activity == 'com.android.bankabc.homepage.HomeActivity' and xml.count('NAF="true"') >= 5:  # 判断首页刷新完整
                self.driver.click(int(0.3704 * self.driver.width()), int(0.2899 * self.driver.height()))
                time.sleep(3)  # 预留界面响应时间
            elif cur_activity == 'com.android.bankabc.MainActivity'and '他行转本行' in xml:  # 待转账页面
                logger.info(f'进入待转账页面')
                return xml
            else:
                logger.info('点击返回键')
                self.driver.back()
        raise MyError('回到APP首页超时失败')

    def __click(self, pos, double=False, use_swip=False, time=0.5, cnt=1):
        click_x = (int(pos[0]) + int(pos[2])) // 2
        click_y = (int(pos[1]) + int(pos[3])) // 2
        if use_swip:
            self.driver.swip_pos(click_x, click_y, click_x+1, click_y+1, time)
        else:
            for i in range(cnt):
                self.driver.click(click_x, click_y, double)

        #logger.debug(f'clicked {click_x} {click_y}')

    def send_status(self, taskid, status):
        try:
            r = requests.get(url=f'http://atf.wuwotech.com/api/ele/kcard?taskId={taskid}&status={status}', )
            r.raise_for_status()
        except BaseException as e:
            logger.warning(f'发送k宝状态失败 taskid:{taskid} status: {status}')

if __name__=='__main__':
    driver = Driver()
    serial = '1234567890qwertyuiopasdfghjklzxcvbnm'
    for c in serial:
        x = int(ABC.login_key_board[c][0] * driver.width())
        y = int(ABC.login_key_board[c][1] * driver.height())
        print(c, x, y)
        driver.click(x, y)
