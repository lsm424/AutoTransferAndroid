#encoding=utf-8
import sqlite3
from common.log import logger

class Sqlite:
    def __init__(self, db):
        self.__connected = False
        try:
            self.conn = sqlite3.connect(db)
            self.curson = self.conn.cursor()
        except BaseException as e:
            logger.error(f'连接数据库 {db}失败, {e}')
            return
        self.__connected = True

    def __del__(self):
        if self.__connected:
            self.curson.close()
            self.conn.close()

    def connected(self):
        return self.__connected

    def select(self, cmd):
        try:
            logger.info(cmd)
            self.curson.execute(cmd)
            return True, self.curson.fetchall()
        except BaseException as e:
            logger.error(f'执行sql：{cmd} 失败, {e}')
            return False, []
