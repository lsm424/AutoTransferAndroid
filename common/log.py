#encoding=utf-8
import logging
import logging.handlers

logger = logging.getLogger("pay")

def gen_log(name):
    global logger
    logger = logging.getLogger(name)
    logger.setLevel(level = logging.DEBUG)
    rf_handler = logging.handlers.TimedRotatingFileHandler(filename="./log/%s.log" % name, when='D',interval=1)
    rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"))
    logger.addHandler(rf_handler)

