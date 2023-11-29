#!/usr/bin/env python3
# -*- coding : utf-8-*-
# coding:unicode_escape

import re
import json
import numpy
import random
import pypinyin
import sqlite3
import atexit
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from xcommon.xlog import *
from chinese_string_enum import *

# '''成语引擎'''
class Chinese_string_engine(object):
    def __init__(self, data_pathfile, default_module=enum_Puzzle_Module.Model_All):
        self.puzzle_model = default_module
        self.data_pathfile = data_pathfile
        # self._load_data()
        self._init_database(data_pathfile)
        self.table_name = 'stringup_dict'
        self.multi_table_name = 'multipinyin_dict'
        atexit.register(self.exit_handler)

    def exit_handler(self):
        LOG_TRACE('Exiting program')
        self.cursor.close()
        self.conn.close()

    def set_model(self, puzzle_model):
        self.puzzle_model = puzzle_model

    def _init_database(self, db_path):
        LOG_TRACE("_init_database:" + db_path)
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        # strsql = "SELECT * FROM stringup_dict limit 2"
        # self.do_query_dict(strsql=strsql)

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
                # LOG_TRACE(idiom_key)
                for idiom in self.idiom_dict_data[idiom_key].keys():
                    # LOG_TRACE(idiom)
                    sqlcolumn = ''
                    sqlvalue = ''
                    for key in self.dict_column.keys():
                        vkey = self.dict_column[key]
                        if vkey in self.idiom_dict_data[idiom_key][idiom].keys():
                            sqlcolumn += '`' + key + '`,'
                            sqlvalue += '\'' + self.idiom_dict_data[idiom_key][idiom][vkey] + '\','
                    sqlcolumn = sqlcolumn.rstrip(',')
                    sqlvalue = sqlvalue.rstrip(',')
                    sqlcolumn += ',`pinyin_fst_lz`'
                    sqlvalue += ',\'' + pypinyin.lazy_pinyin(idiom)[0] + '\''
                    sqlcolumn += ',`pinyin_fst`'
                    pinyin_fst = ''.join(pypinyin.pinyin(idiom)[0])
                    # LOG_TRACE(pinyin_fst)
                    sqlvalue += ',\'' + pinyin_fst + '\''
                    sqlcolumn = sqlcolumn.strip(',')
                    sqlvalue = sqlvalue.strip(',')
                    sql = 'INSERT OR IGNORE INTO `' + self.table_name + '` ('
                    sql += sqlcolumn
                    sql += ')'
                    sql += 'values('
                    sql += sqlvalue
                    sql += ')'
                    # LOG_TRACE(sql)
                    self.cursor.execute(sql)

                    mulpinyin = pypinyin.pinyin(idiom[0], heteronym=True)[0]
                    for mpy in mulpinyin:
                        sql = "INSERT OR IGNORE INTO `" + self.multi_table_name + "` (world, pinyin) values("
                        sql +=  "'" + idiom[0] + "',"
                        sql +=  "'" + mpy + "'"
                        sql += ')'
                        # LOG_TRACE(sql)
                        self.cursor.execute(sql)

                    self.conn.commit()
                
            return 1
        except Exception as e:
            LOG_ERROR('>> Creat Error:', e)
            return 0

    def _load_data(self):
        data_filepath = progam_path + './data/data.json'
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

    def _do_query_dict(self, strsql):
        LOG_TRACE("do_query_dict:" + strsql)
        self.cursor.execute(strsql)

        results = []
        rows = self.cursor.fetchall()
        if rows:
            column_names = [description[0] for description in self.cursor.description]
            for row in rows:
                result = dict(zip(column_names, row))
                results.append(result)
            
            # 输出结果
            for result in results:
                print(result)

        return results
    
    def _get_nextIdiom(self, idiom, except_dict=[], puzzle_model=enum_Puzzle_Module.Model_All, call_back=0):
        LOG_TRACE(idiom, puzzle_model, except_dict)
        pinyin = ''.join(pypinyin.pinyin(idiom)[-1])
        lzpinyin = pypinyin.lazy_pinyin(idiom)[-1]
        mulpinyin = pypinyin.pinyin(idiom[-1], heteronym=True)[0]
        LOG_TRACE(pinyin, lzpinyin, mulpinyin)

        results = []
        # 同字同音匹配模式
        if enum_Puzzle_Module.Model_All == puzzle_model:
            strsql = "SELECT * FROM `" + self.table_name + "` a where SUBSTR(a.idiom, 1, 1) = '" + idiom[-1] + "'"
            strsql += " and pinyin_fst = '" + pinyin + "'"

        # 同字匹配模式
        elif enum_Puzzle_Module.Model_Word == puzzle_model:
            strsql = "SELECT * FROM `" + self.table_name + "` a where SUBSTR(a.idiom, 1, 1) = '" + idiom[-1] + "'" 

        # 同音匹配模式
        elif enum_Puzzle_Module.Model_Pinyin == puzzle_model:
            strsql = "SELECT * FROM `" + self.table_name + "` a where a.pinyin_fst = '" + pinyin + "'" 

        # 同拼匹配模式
        elif enum_Puzzle_Module.Model_LzPinyin == puzzle_model:
            strsql = "SELECT * FROM `" + self.table_name + "` a where a.pinyin_fst_lz = '" + lzpinyin + "'" 

        # 多音匹配模式
        elif enum_Puzzle_Module.Model_Multi == puzzle_model:
            strsql = "SELECT * FROM `" + self.table_name + "` a where a.pinyin_fst = '" + lzpinyin + "'" 
        
        else:
            return results

        if 0 != len(except_dict):
            LOG_TRACE(except_dict)
            strsql += " and a.idiom not in('" + "','".join(except_dict) + "')"
        if 0 == call_back:
            strsql += " limit 1"
        results = self._do_query_dict(strsql)
        LOG_TRACE(results)

        promote_results = []
        if 0 == call_back:
            promote_except_dict = except_dict
            if 0 != len(results):
                promote_except_dict.append(results[0]['idiom'])
                promote_results, _ = self._get_nextIdiom(results[0]['idiom'], promote_except_dict, puzzle_model, 1)
            LOG_TRACE("promote_results")
            LOG_TRACE(promote_results)
        
        return results, promote_results

    def get_nextIdom(self, idiom, except_dict=[]):
        if None == idiom:
            return None
        
        strsql = "SELECT * FROM `" + self.table_name + "` where idiom like '" + idiom + "'"
        if 0 != len(except_dict):
            LOG_TRACE(except_dict)
            strsql += " and idiom not in('" + "','".join(except_dict) + "')"
        strsql += " limit 1"
        results = self._do_query_dict(strsql)
        LOG_TRACE(results)
        return results

    def get_nextIdomByKey(self, idiom_key, except_dict=[]):
        if None == idiom_key:
            return None
        
        strsql = "SELECT * FROM `" + self.table_name + "` where idiom like '" + idiom_key + "%'"
        if 0 != len(except_dict):
            LOG_TRACE(except_dict)
            strsql += " and idiom not in('" + "','".join(except_dict) + "')"
        strsql += " limit 1"
        results = self._do_query_dict(strsql)
        LOG_TRACE(results)
        return results

    def _get_answerText(self, result):
        LOG_TRACE(self.dict_column)

        text_ret = ''
        for column in self.dict_column:
            LOG_TRACE(result[column])
            if None != result[column]:
                text_ret += self.dict_column[column] + ':' + result[column] + '\n'

        return text_ret.strip('\n')

    def _get_spell(self, result):
        return result['pinyin_all']
    
    def _get_idiom(self, result):
        return result['idiom']

    def get_idiom_instance(self, idiom):
        strsql = "SELECT * FROM `" + self.table_name + "` where idiom = '" + idiom + "'"
        results = self._do_query_dict(strsql)
        return results

    def check_idiom(self, idiom, idiom_check):
        LOG_TRACE(idiom, idiom_check)
        idiom_head_pinyin = ''.join(pypinyin.pinyin(idiom)[0])
        idiom_check_tail_pinyin = ''.join(pypinyin.pinyin(idiom_check)[-1])
        LOG_TRACE(idiom_head_pinyin, idiom_check_tail_pinyin)
        if enum_Puzzle_Module.Model_All == self.puzzle_model and (idiom[0] != idiom_check[-1] or idiom_head_pinyin != idiom_check_tail_pinyin):
            return enum_Puzzle_Unmatch.Unmatch_All, "首尾字及拼音匹配失败"

        if enum_Puzzle_Module.Model_Word == self.puzzle_model and idiom[0] != idiom_check[-1]:
            return enum_Puzzle_Unmatch.Unmatch_Word, "首尾字匹配失败"

        idiom_head_lzpinyin = pypinyin.lazy_pinyin(idiom)[0]
        idiom_check_tail_lzpinyin = pypinyin.lazy_pinyin(idiom_check)[-1]
        LOG_TRACE(idiom_head_lzpinyin, idiom_check_tail_lzpinyin)
        if enum_Puzzle_Module.Model_LzPinyin == self.puzzle_model and idiom_head_lzpinyin != idiom_check_tail_lzpinyin:
            return enum_Puzzle_Unmatch.Unmatch_LzPinyin, "首尾字拼音模糊匹配失败"

        if enum_Puzzle_Module.Model_Pinyin == self.puzzle_model and idiom_head_pinyin != idiom_check_tail_pinyin:
            return enum_Puzzle_Unmatch.Unmatch_Pinyin, "首尾字拼音精确匹配失败"

        mulpinyin = pypinyin.pinyin(idiom_check[-1], heteronym=True)[0]
        if enum_Puzzle_Module.Model_Multi == self.puzzle_model and idiom_head_pinyin not in mulpinyin:
            return enum_Puzzle_Unmatch.Unmatch_Multi, "首尾多音字匹配失败"

        return 0, "匹配成功"

    def get_model(self):
        return self.puzzle_model
    

# '''run'''
if __name__ == '__main__':
    data_pathfile = progam_path + '/data/stringup.db'
    engine = Chinese_string_engine(data_pathfile)
    # idiom = '白雪'
    # except_dict = {}
    # LOG_INFO(engine.get_nextIdomByKey(idiom, except_dict))
    # LOG_TRACE(engine._get_nextIdiom(
    #     idiom, except_dict, enum_Puzzle_Module.Model_All))
    # LOG_TRACE(engine._get_nextIdiom(
    #     idiom, except_dict, enum_Puzzle_Module.Model_Word))
    # LOG_TRACE(engine._get_nextIdiom(
    #     idiom, except_dict, enum_Puzzle_Module.Model_LzPinyin))
    # LOG_TRACE(engine._get_nextIdiom(
    #     idiom, except_dict, enum_Puzzle_Module.Model_Pinyin))
    # LOG_TRACE(engine._get_nextIdiom(
    #     idiom, except_dict, enum_Puzzle_Module.Model_Multi))

    # LOG_TRACE(engine._get_answerText(idiom))
    # LOG_TRACE(engine.get_idiom_instance(idiom))

    if len(sys.argv) > 1 and 'dict' == sys.argv[1]:
        engine._generate_dict()

    # continue_dict = {
    #     # enum_Puzzle_Module.Model_All: 'all',
    #     enum_Puzzle_Module.Model_Word: 'word',
    #     enum_Puzzle_Module.Model_LzPinyin: 'lzpinyin',
    #     enum_Puzzle_Module.Model_Pinyin: 'pinyin',
    #     enum_Puzzle_Module.Model_Multi: 'multi',
    #     enum_Puzzle_Module.Model_BattleSingle: 'battlesingle',
    #     enumBarButton_Operate.Menu_ControlId_Work_Promote: 'promote',
    #     enumBarButton_Operate.Menu_ControlId_Work_Auto: 'auto',
    # }

    # for control_id in continue_dict:
    #     LOG_TRACE(type(control_id), type(continue_dict[control_id]))
    #     LOG_TRACE(control_id, continue_dict[control_id])

    # LOG_TRACE(pypinyin.pinyin('奥', heteronym=True)[0])
    # LOG_TRACE(pypinyin.pinyin('奥', heteronym=False)[0])
    # LOG_TRACE(pypinyin.lazy_pinyin('奥')[0])
