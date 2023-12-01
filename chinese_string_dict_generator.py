#!/usr/bin/env python3
# -*- coding : utf-8-*-
# coding:unicode_escape

import atexit
import json
import pypinyin
import sqlite3
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from chinese_string_up_sqlgenerator import CSqlGenerator
from xcommon.xlog import *
from chinese_string_enum import *


# '''成语引擎'''
class Chinese_string_db_generator(object):

    def __init__(self, data_pathfile):
        self.data_pathfile = data_pathfile
        self._init_database(data_pathfile)
        self.table_name = 'stringup_dict'
        self.multi_table_name = 'multipinyin_dict'
        atexit.register(self.exit_handler)

    def exit_handler(self):
        LOG_TRACE('Exiting program')
        self.cursor.close()
        self.conn.close()

    def _init_database(self, db_path):
        LOG_TRACE("_init_database:" + db_path)
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        self.dict_column = {}
        self.dict_column['idiom'] = '成语'
        self.dict_column['pinyin_all'] = '拼音'
        self.dict_column['explain'] = '解释'
        self.dict_column['eg'] = '示例'
        self.dict_column['source'] = '出处'
        self.dict_column['emotion'] = '情感'
        self.dict_column['usage'] = '用法'
        self.dict_column['fanti'] = '繁体'

    def _drop_table(self, table_name):
        try:
            sql = 'drop table `' + table_name + '`'
            LOG_TRACE(sql)
            self.cursor.execute(sql)
            return 1
        except Exception as e:
            LOG_ERROR('>> Creat Error:', e)
            return 0

    def _create_table(self):
        try:
            sql = 'CREATE TABLE IF NOT EXISTS `' + self.table_name + '''`(
                `id` INTEGER PRIMARY KEY,
                `idiom` VARCHAR(30) NOT NULL,
                `pinyin_all` VARCHAR(30),
                `pinyin_fst_lz` VARCHAR(30),
                `pinyin_fst` VARCHAR(128),
                `explain` VARCHAR(512),
                `eg` VARCHAR(1024),
                `source` VARCHAR(1024),
                `emotion` VARCHAR(128),
                `usage` VARCHAR(1024),
                `fanti` VARCHAR(30),
                `update_date` DATETIME DEFAULT current_timestamp
            );
            '''
            LOG_TRACE(sql)
            self.cursor.execute(sql)

            sql = 'CREATE TABLE IF NOT EXISTS `' + self.multi_table_name + '''`(
                `world` VARCHAR(4),
                `pinyin` VARCHAR(30),
                `update_date` DATETIME DEFAULT current_timestamp,
                PRIMARY KEY (`world`, `pinyin`)
            );
            '''
            LOG_TRACE(sql)
            self.cursor.execute(sql)
            return 1
        except Exception as e:
            LOG_ERROR('>> Creat Error:', e)
            return 0

    def _fill_data(self):
        try:
            for idiom_key in self.idiom_dict_data.keys():
                LOG_TRACE(idiom_key)
                for idiom in self.idiom_dict_data[idiom_key].keys():
                    LOG_TRACE(idiom)
                    sqlcolumn = ''
                    sqlvalue = ''
                    for key in self.dict_column.keys():
                        vkey = self.dict_column[key]
                        if vkey in self.idiom_dict_data[idiom_key][idiom].keys(
                        ):
                            sqlcolumn += '`' + key + '`,'
                            sqlvalue += '\'' + self.idiom_dict_data[idiom_key][
                                idiom][vkey] + '\','
                    sqlcolumn = sqlcolumn.rstrip(',')
                    sqlvalue = sqlvalue.rstrip(',')
                    sqlcolumn += ',`pinyin_fst_lz`'
                    sqlvalue += ',\'' + pypinyin.lazy_pinyin(idiom)[0] + '\''
                    sqlcolumn += ',`pinyin_fst`'
                    pinyin_fst = ''.join(pypinyin.pinyin(idiom)[0])
                    LOG_TRACE(pinyin_fst)
                    sqlvalue += ',\'' + pinyin_fst + '\''
                    sqlcolumn = sqlcolumn.strip(',')
                    sqlvalue = sqlvalue.strip(',')
                    sql = 'INSERT OR IGNORE INTO `' + self.table_name + '` ('
                    sql += sqlcolumn
                    sql += ')'
                    sql += 'values('
                    sql += sqlvalue
                    sql += ')'
                    LOG_TRACE(sql)
                    self.cursor.execute(sql)

                    mulpinyin = pypinyin.pinyin(idiom[0], heteronym=True)[0]
                    for mpy in mulpinyin:
                        sql = "INSERT OR IGNORE INTO `" + self.multi_table_name + "` (world, pinyin) values("
                        sql += "'" + idiom[0] + "',"
                        sql += "'" + mpy + "'"
                        sql += ')'
                        LOG_TRACE(sql)
                        self.cursor.execute(sql)

                self.conn.commit()

            return 1
        except Exception as e:
            LOG_ERROR('>> Creat Error:', e)
            return 0

    def _load_data(self):
        data_filepath = progam_path + './bak/data.json'
        with open(data_filepath) as f:
            self.idiom_dict = json.load(f)

        self.idiom_dict_data = self.idiom_dict['idiom']

    # '''生成字典''' --30078
    def _generate_dict(self):
        LOG_TRACE("_generate_dict:" + self.data_pathfile)

        self._load_data()
        self._drop_table(self.table_name)
        self._drop_table(self.multi_table_name)
        self._create_table()
        self._fill_data()


def main():
    result = []
    data_pathfile = progam_path + '/data/stringup.db'
    engine = Chinese_string_db_generator(data_pathfile)
    engine._generate_dict()

    return result


# '''run'''
if __name__ == '__main__':
    value = main()
    LOG_INFO("返回值:", value)
