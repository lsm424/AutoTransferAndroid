#encoding=utf-8
import os
import time
import subprocess
import re

from common.MyError import MyError
from common.log import logger
import threading

class Driver:
    lock = threading.Lock()
    def __init__(self):
        self._pattern_activity = re.compile(r'{.+?/(.+?)}')
        self._pattern_package = re.compile(r'([a-z|A-Z|\.]+)/.+?}')
        ret, content = self.__execute('dumpsys window | grep app |grep init')
        if ret == -1:
            raise MyError('获取屏幕尺寸失败')
        logger.info(content)
        ret = re.findall(re.compile(r'app=(\d+)x(\d+)'), content)
        if len(ret) == 0:
            raise MyError('匹配屏幕尺寸失败, %s' % content)
        ret.sort(key=lambda x: x[1])
        self._width = int(ret[0][0])
        self._height = int(ret[0][1])
        logger.info(f'屏幕宽{self._width}, 高：{self._height}')

    # 屏幕宽度
    def width(self):
        return self._width

    # 屏幕高度
    def height(self):
        return self._height

    # 停止app
    def stop_app(self, pakcage):
        ret = self.__execute('am force-stop %s' % pakcage)
        time.sleep(0.5)
        return ret

    # 启动app
    def start_app(self, package, mainactivity):
        return self.__execute('am start -n %s/%s' % (package, mainactivity))

    # 获取界面信息
    def get_xml(self):
        #time.sleep(0.1)
        ret, output = self.__execute('rm -f /sdcard/ui.xml; uiautomator dump /sdcard/ui.xml')
        if os.path.exists('/sdcard/ui.xml'):
            return open('/sdcard/ui.xml', 'r').read()
        logger.error('获取xml失败, %s' % output)
        return ''

    def is_app_started(self, package):
        ret, output = self.__execute('dumpsys window windows | grep Current')
        return package in output

    def click(self, x, y, double=False):
        self.__execute('input tap %d %d' % (x, y))
        if double:
            time.sleep(0.1)
            self.__execute('input tap %d %d' % (x, y))

    def screencap(self):
        filename = '/sdcard/screencap.png'
        self.__execute('rm -f %s; screencap -p %s' % (filename, filename))
        return filename

    def swip(self, x1, y1, x2, y2, time=0.4):
        self.__execute(f'input swipe {x1 * self._width} {y1 * self._height} {x2 * self._width} {y2 * self._height} {int(time * 1000)}')

    def swip_pos(self, x1, y1, x2, y2, time=0.5):
        self.__execute(f'input swipe {x1} {y1} {x2} {y2} {int(time * 1000)}')

    def get_cur_activity(self):
        ret, output = self.__execute('dumpsys window | grep mCurrentFocus')
        if ret != 0:
            logger.warning('get current activity failed')
            return ''
        ret = re.findall(self._pattern_activity, output)
        if len(ret) != 1:
            logger.warning(f'匹配activity失败，{output}')
            return ''
        return ret[0]

    def get_cur_packge(self):
        ret, output = self.__execute('dumpsys window | grep mCurrentFocus')
        if ret != 0:
            logger.warning('get current activity failed')
            return ''
        ret = re.findall(self._pattern_package, output)
        if len(ret) != 1:
            logger.warning(f'匹配package失败，{output}')
            return ''
        return ret[0]

    def back(self):
        self.__execute('input keyevent 4')

    def input_text(self, text):
        self.__execute(f"am broadcast -a ADB_INPUT_TEXT --es msg '{text}'")

    def input_text_by_adb(self, text):
        self.__execute(f"input text {text}")

    # 电量屏幕
    def power_on_screen(self):
        Driver.lock.acquire()
        ret, output = self.__execute('dumpsys power  | grep "Display Power"')
        if ret == 0 and 'OFF' in output:
            self.__execute('input keyevent 26')
        Driver.lock.release()

    # 屏幕解锁
    def unlock(self):
        Driver.lock.acquire()
        ret, output = self.__execute('dumpsys window policy |grep "isStatusBarKeyguard"')
        if ret == 0 and 'true' in output:
            self.__execute('input keyevent 82')
            time.sleep(0.4)
        Driver.lock.release()


    def __execute(self, cmd):
        try:
            ret = subprocess.getstatusoutput(cmd)
            logger.info('%s   [ret]%s' % (cmd, ret))
            return ret
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            logger.info('run over')
            output = p.stdout.read()
            logger.info('run over')

            p.wait()
            errout = p.stderr.read()
            p.stdout.close()
            p.stderr.close()
            return p.returncode, output.decode('utf-8')
        except BaseException as e:
            logger.error('excute %s failed, %s' % (cmd, e))
            return -1, str(e)


