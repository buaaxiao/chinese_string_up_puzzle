#!/usr/bin/env python3
# -*- coding : utf-8-*-
# coding:unicode_escape

import pypinyin
import sqlite3
import atexit
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from chinese_string_up_sqlgenerator import CSqlGenerator
from xcommon.xlog import *
from chinese_string_enum import *


# '''成语引擎'''
class Chinese_string_engine(object):

    def __init__(self, data_pathfile, default_module=enum_Puzzle_Module.Module_All):
        self.puzzle_module = default_module
        self.data_pathfile = data_pathfile
        self._init_database(data_pathfile)
        self.table_name = "stringup_dict"
        self.multi_table_name = "multipinyin_dict"
        self.cSqlGenerator = CSqlGenerator(self.table_name)
        atexit.register(self.exit_handler)

    def exit_handler(self):
        LOG_TRACE("Exiting program")
        self.cursor.close()
        self.conn.close()

    def set_model(self, puzzle_module):
        self.puzzle_module = puzzle_module

    def _init_database(self, db_path):
        LOG_TRACE("_init_database:" + db_path)
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        self.dict_column = {}
        self.dict_column["idiom"] = "成语"
        self.dict_column["pinyin_all"] = "拼音"
        self.dict_column["explain"] = "解释"
        self.dict_column["eg"] = "示例"
        self.dict_column["source"] = "出处"
        self.dict_column["emotion"] = "情感"
        self.dict_column["usage"] = "用法"
        self.dict_column["fanti"] = "繁体"

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
                LOG_TRACE(result)

        return results

    def get_nextIdiom(self, idiom, except_dict=[], limit_flag=1):
        results = []
        promote_results = []
        strsql = self.cSqlGenerator.gen_sql(
            self.puzzle_module, idiom, except_dict, limit_flag
        )

        LOG_INFO(strsql)
        results = self._do_query_dict(strsql)
        LOG_TRACE(results)

        if 1 == limit_flag:
            promote_except_dict = except_dict
            if 0 != len(results):
                promote_except_dict.append(results[0]["idiom"])
                promote_results, _ = self.get_nextIdiom(
                    results[0]["idiom"], promote_except_dict, 0
                )
            LOG_TRACE("promote_results")
            LOG_TRACE(promote_results)

        return results, promote_results

    def get_nextIdomByKey(self, idiom_key, except_dict=[]):
        if None == idiom_key:
            return None
        idiom_key = idiom_key + "%"
        strsql = self.cSqlGenerator.gen_nextsql(idiom_key, except_dict)
        results = self._do_query_dict(strsql)
        LOG_TRACE(results)
        return results

    def get_idiom_instance(self, idiom):
        idiom_key = idiom
        if None == idiom_key:
            return None
        strsql = self.cSqlGenerator.gen_nextsql(idiom_key)
        results = self._do_query_dict(strsql)
        LOG_TRACE(results)
        return results

    def get_answerText(self, result):
        LOG_TRACE(self.dict_column)

        text_ret = ""
        for column in self.dict_column:
            LOG_TRACE(result[column])
            if None != result[column]:
                text_ret += self.dict_column[column] + ":" + result[column] + "\n"

        return text_ret.strip("\n")

    def get_spell(self, result):
        return result["pinyin_all"]

    def get_idiom(self, result):
        return result["idiom"]

    def check_idiom(self, idiom, idiom_check):
        LOG_TRACE(idiom, idiom_check)
        idiom_head_pinyin = "".join(pypinyin.pinyin(idiom)[0])
        idiom_check_tail_pinyin = "".join(pypinyin.pinyin(idiom_check)[-1])
        LOG_TRACE(idiom_head_pinyin, idiom_check_tail_pinyin)
        if enum_Puzzle_Module.Module_All == self.puzzle_module and (
            idiom[0] != idiom_check[-1] or idiom_head_pinyin != idiom_check_tail_pinyin
        ):
            return enum_Puzzle_Unmatch.Unmatch_All, "首尾字及拼音匹配失败"

        if (
            enum_Puzzle_Module.Module_Word == self.puzzle_module
            and idiom[0] != idiom_check[-1]
        ):
            return enum_Puzzle_Unmatch.Unmatch_Word, "首尾字匹配失败"

        idiom_head_lzpinyin = pypinyin.lazy_pinyin(idiom)[0]
        idiom_check_tail_lzpinyin = pypinyin.lazy_pinyin(idiom_check)[-1]
        LOG_TRACE(idiom_head_lzpinyin, idiom_check_tail_lzpinyin)
        if (
            enum_Puzzle_Module.Module_LzPinyin == self.puzzle_module
            and idiom_head_lzpinyin != idiom_check_tail_lzpinyin
        ):
            return enum_Puzzle_Unmatch.Unmatch_LzPinyin, "首尾字拼音模糊匹配失败"

        if (
            enum_Puzzle_Module.Module_Pinyin == self.puzzle_module
            and idiom_head_pinyin != idiom_check_tail_pinyin
        ):
            return enum_Puzzle_Unmatch.Unmatch_Pinyin, "首尾字拼音精确匹配失败"

        mulpinyin = pypinyin.pinyin(idiom_check[-1], heteronym=True)[0]
        if (
            enum_Puzzle_Module.Module_Multi == self.puzzle_module
            and idiom_head_pinyin not in mulpinyin
        ):
            return enum_Puzzle_Unmatch.Unmatch_Multi, "首尾多音字匹配失败"

        return 0, "匹配成功"

    def get_model(self):
        return self.puzzle_module


def main():
    result = []
    data_pathfile = progam_path + "/data/stringup.db"
    engine = Chinese_string_engine(data_pathfile)

    idiom_index = "白雪"
    except_dict = []
    LOG_INFO(engine.get_nextIdomByKey(idiom_index, except_dict))
    engine.set_model(enum_Puzzle_Module.Module_All)
    LOG_TRACE(engine.get_nextIdiom(idiom_index, except_dict))
    engine.set_model(enum_Puzzle_Module.Module_Word)
    LOG_TRACE(engine.get_nextIdiom(idiom_index, except_dict))
    engine.set_model(enum_Puzzle_Module.Module_LzPinyin)
    LOG_TRACE(engine.get_nextIdiom(idiom_index, except_dict))
    engine.set_model(enum_Puzzle_Module.Module_Pinyin)
    LOG_TRACE(engine.get_nextIdiom(idiom_index, except_dict))
    engine.set_model(enum_Puzzle_Module.Module_Multi)
    LOG_TRACE(engine.get_nextIdiom(idiom_index, except_dict))

    idiom = "雪案萤灯"
    results = engine.get_idiom_instance(idiom)
    if 0 != len(results):
        result = results[0]
        LOG_INFO(engine.get_answerText(result))

    continue_dict = {
        enum_Puzzle_Module.Module_All: "all",
        enum_Puzzle_Module.Module_Word: "word",
        enum_Puzzle_Module.Module_LzPinyin: "lzpinyin",
        enum_Puzzle_Module.Module_Pinyin: "pinyin",
        enum_Puzzle_Module.Module_Multi: "multi",
        enum_Puzzle_Module.Module_BattleSingle: "battlesingle",
        enumBarButton_Operate.Menu_ControlId_Work_Promote: "promote",
        enumBarButton_Operate.Menu_ControlId_Work_Auto: "auto",
    }

    for control_id in continue_dict:
        LOG_TRACE(type(control_id), type(continue_dict[control_id]))
        LOG_TRACE(control_id, continue_dict[control_id])

    LOG_TRACE(pypinyin.pinyin("奥", heteronym=True)[0])
    LOG_TRACE(pypinyin.pinyin("奥", heteronym=False)[0])
    LOG_TRACE(pypinyin.lazy_pinyin("奥")[0])

    return result


# '''run'''
if __name__ == "__main__":
    value = main()
    LOG_INFO("返回值:", value)
