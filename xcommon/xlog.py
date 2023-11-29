# coding:utf-8
import os
import pwd
import sys
import datetime
import logging
import logging.handlers
from xcommon.xconfig import xConfigHandle

progam_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
cfg_path = progam_path + './data/config.xml'


class xLogger(object):
    def __init__(self, name, config_file='config.xml'):
        cConfigHandle = xConfigHandle(config_file)
        logpath = progam_path + \
            cConfigHandle.get_value_str('log', 'path', './logs')
        if not os.path.exists(logpath):
            os.mkdir(logpath)
        # 读取日志文件容量，转换为字节
        lognum = 10
        lognum = cConfigHandle.get_value_int('log', 'num', 10)

        logsize = 0
        logsize = cConfigHandle.get_value_int('log', 'size', 0)

        # 读取日志文件保存个数
        # 日志文件名：由用例脚本的名称，结合日志保存路径，得到日志文件的绝对路径
        logname = sys.argv[0].split(
            '/')[-1].split('.')[0] + datetime.datetime.now().strftime('_%Y_%m_%d_%H') + '.log'
        logname = sys.argv[0].split(
            '/')[-1].split('.')[0] + '.log'
        logname = os.path.join(logpath, logname)
        # 日志级别
        level = cConfigHandle.get_value_str('log', 'level', 'error').upper()
        if level == 'TRACE':
            level = 'DEBUG'

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.formatter = logging.Formatter(
            '[%(asctime)s][%(name)s][%(levelname)s] %(message)s'
        )

        if 1 == cConfigHandle.get_value_int('log', 'out_put_to_file', 0):
            # 创建一个FileHandler,存储日志文件
            if logsize != 0:
                fh = logging.handlers.RotatingFileHandler(
                    logname, maxBytes=logsize, backupCount=lognum, encoding='utf-8')
                fh.setLevel(level)
                fh.setFormatter(self.formatter)
                self.logger.addHandler(fh)
            else:
                fh = logging.handlers.TimedRotatingFileHandler(
                    filename=logname, when='H', interval=1, backupCount=lognum)

                fh.setLevel(level)
                fh.setFormatter(self.formatter)
                self.logger.addHandler(fh)

        if 1 == cConfigHandle.get_value_int('log', 'out_put_to_terminate', 0):
            # 创建一个StreamHandler,用于输出到控制台
            sh = logging.StreamHandler(stream=sys.stdout)
            sh.setLevel(level)
            sh.setFormatter(self.formatter)
            self.logger.addHandler(sh)

    def log_fuc(self, level, message):
        msg = message
        if level == 'TRACE':
            self.debug(msg)
        if level == 'DEBUG':
            self.debug(msg)
        if level == 'INFO':
            self.info(msg)
        if level == 'WARNING':
            self.warning(msg)
        if level == 'ERROR':
            self.error(msg)
        if level == 'CRITICAL':
            self.critical(msg)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)


user_name = pwd.getpwuid(os.getuid())[0]
logg = xLogger(user_name, cfg_path)


def LOG_DEBUG(*params_a):
    strRet = ''
    for each in params_a:
        strRet += ' ' + str(each)
    logg.log_fuc('DEBUG', strRet)


def LOG_TRACE(*params_a):
    strRet = ''
    for each in params_a:
        strRet += ' ' + str(each)
    logg.log_fuc('TRACE', strRet)


def LOG_INFO(*params_a):
    strRet = ''
    for each in params_a:
        strRet += ' ' + str(each)
    logg.log_fuc('INFO', strRet)


def LOG_WARNING(*params_a):
    strRet = ''
    for each in params_a:
        strRet += ' ' + str(each)
    logg.log_fuc('WARNING', strRet)


def LOG_ERROR(*params_a):
    strRet = ''
    for each in params_a:
        strRet += ' ' + str(each)
    logg.log_fuc('ERROR', strRet)


def LOG_CRITICAL(*params_a):
    strRet = ''
    for each in params_a:
        strRet += ' ' + str(each)
    logg.log_fuc('CRITICAL', strRet)
