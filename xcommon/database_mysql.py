# -*- coding:utf-8 -*-
import sys
from dbutils.pooled_db import PooledDB
import pymysql
from timeit import default_timer
from imp import reload

from xcommon.xlog import *


class DB_MySQL_Pool:
    """db连接池"""
    __pool = None
    __MAX_CONNECTIONS = 100     # 创建连接池的最大数量
    __MIN_CACHED = 10           # 连接池中空闲连接的初始数量
    __MAX_CACHED = 20           # 连接池中空闲连接的最大数量
    __MAX_SHARED = 10           # 共享连接的最大数量
    __BLOCK = True              # 超过最大连接数量时候的表现，为True等待连接数量下降，为false直接报错处理
    __MAX_USAGE = 100           # 单个连接的最大重复使用次数
    __CHARSET = 'UTF8'
    '''
        set_session:可选的SQL命令列表，可用于准备
                    会话，例如[“将日期样式设置为...”，“设置时区...”]
                    重置:当连接返回池中时，应该如何重置连接
                    (False或None表示回滚以begin()开始的事务，
                    为安全起见，始终发出回滚命令)
    '''
    __RESET = True
    __SET_SESSION = ['SET AUTOCOMMIT = 1']  # 设置自动提交

    def __init__(self, host, port, user, password, database):
        LOG_TRACE(sys._getframe().f_code.co_name)
        if not self.__pool:
            self.__class__.__pool = PooledDB(creator=pymysql,
                                             host=host,
                                             port=port,
                                             user=user,
                                             password=password,
                                             database=database,
                                             maxconnections=self.__MAX_CONNECTIONS,
                                             mincached=self.__MIN_CACHED,
                                             maxcached=self.__MAX_CACHED,
                                             maxshared=self.__MAX_SHARED,
                                             blocking=self.__BLOCK,
                                             maxusage=self.__MAX_USAGE,
                                             setsession=self.__SET_SESSION,
                                             reset=self.__RESET,
                                             charset=self.__CHARSET)

    def get_connect(self):
        return self.__pool.connection()


class DB_MySQL(object):
    def __init__(self, host, port, user, password, database, _log_time=True, _log_label="总用时") -> None:
        LOG_TRACE(sys._getframe().f_code.co_name)
        self.__host = host
        self.__port = port
        self.__user = user
        self.__password = password
        self.__database = database
        self._log_time = _log_time
        self._log_label = _log_label
        self.connects_pool = DB_MySQL_Pool(
            host=self.__host, port=self.__port, user=self.__user, password=self.__password, database=self.__database)

    def __enter__(self):
        LOG_TRACE(sys._getframe().f_code.co_name)
        # 如果需要记录时间
        if self._log_time is True:
            self._start = default_timer()

        connect = self.connects_pool.get_connect()
        cursor = connect.cursor(pymysql.cursors.DictCursor)
        # connect.autocommit = False # 如果使用连接池 则不能在取出后设置 而应该在创建线程池时设置
        self._connect = connect
        self._cursor = cursor
        return self

    def __exit__(self, *exc_info):
        LOG_TRACE(sys._getframe().f_code.co_name)
        self._connect.commit()
        self._cursor.close()
        self._connect.close()

        if self._log_time is True:
            diff = default_timer() - self._start
            LOG_TRACE('-- %s: %.6f 秒' % (self._log_label, diff))

    def select_all(self, sql):
        """查询返回全部结果"""
        LOG_TRACE(sys._getframe().f_code.co_name)
        self._cursor.execute(sql)
        return self._cursor.fetchall()

    def select_one(self, sql):
        """查询返回单个结果"""
        LOG_TRACE(sys._getframe().f_code.co_name)
        self._cursor.execute(sql)
        return self._cursor.fetchone()

    def execute(self, sql):
        """执行语句"""
        LOG_TRACE(sys._getframe().f_code.co_name)
        res = self._cursor.execute(sql)
        return res

    def commit(self):
        """提交事务"""
        LOG_TRACE(sys._getframe().f_code.co_name)
        self._connect.commit()

