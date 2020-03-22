#encoding=utf-8
import subprocess
import os
import sys
sys.path.append('..')
from common.log import logger
from common.MyError import MyError
from common.sqlite_util import Sqlite

class ShortMsg():
    def __init__(self):
        db_path = ['/data/user_de/0/com.android.providers.telephony/databases/mmssms.db',
                   '/data/data/com.android.providers.telephony/databases/mmssms.db',
                   '/data/user_de/0/com.android.providers.telephony/databases/mmssms.db']
        for db in db_path:
            self.db_path = os.path.join('/data', db)
            logger.info(f'尝试 {self.db_path}')
            db_obj = Sqlite(self.db_path)
            if not db_obj.connected():
                continue
            if db_obj.select('select address, date, date, body from sms where type=1 limit 1')[0] is True:
                logger.info(f'使用 {self.db_path}')
                return
        else:
            raise MyError(f'sms db 未找到: {db_list}')

    def getMsg(self, sender_num, date=0):
        self.__execute(f'rm -rf /sdcard/mmssms.db; cp {self.db_path} /sdcard/mmssms.db')
        db_obj = Sqlite('/sdcard/mmssms.db')
        if not db_obj.connected():
            logger.error(f'not connected db')
            return []
        ret, sms_data = db_obj.select(f'select body from sms  where address={sender_num} and  type=1 and date>{date * 1000} order by date desc')
        if ret is False:
            return []
        sms_data = list(map(lambda x: x[0], sms_data))
        #logger.info('%s msg: %s' % (sender_num, sms_data))
        return sms_data

    def __execute(self, cmd):
        try:
            logger.info('run cmd: %s' % cmd)
            #return subprocess.getstatusoutput(cmd)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output = p.stdout.read()
            p.wait()
            errout = p.stderr.read()
            p.stdout.close()
            p.stderr.close()
            return p.returncode, output.decode('utf-8')
        except BaseException as e:
            logger.error('excute %s failed, %s' % (cmd, e))
            return -1, str(e)

MsgManger = ShortMsg()
#print(MsgManger.getMsg('95533'))