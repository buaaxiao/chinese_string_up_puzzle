#!/usr/bin/env python3
# -*- coding : utf-8-*-
# coding:unicode_escape

import pypinyin
from chinese_string_enum import enum_Puzzle_Module
from xcommon.xlog import *


class CSqlGenerator:

    def __init__(self, table_name):
        self.table_name = table_name
        self.functions = {}
        self.register_module(enum_Puzzle_Module.Module_All, self.function_all)
        self.register_module(enum_Puzzle_Module.Module_Word, self.function_word)
        self.register_module(enum_Puzzle_Module.Module_Pinyin, self.function_pinyin)
        self.register_module(enum_Puzzle_Module.Module_LzPinyin, self.function_lzpinyin)
        self.register_module(enum_Puzzle_Module.Module_Multi, self.function_multi)

    def register_module(self, module, function):
        self.functions[module] = function

    def gen_nextsql(self, idiom_key, except_dict=[]):
        strsql = (
            "select * from `"
            + self.table_name
            + "` where idiom like '"
            + idiom_key
            + "'"
        )
        if 0 != len(except_dict):
            LOG_TRACE(except_dict)
            strsql += " and idiom not in('" + "','".join(except_dict) + "')"
        strsql += " limit 1"
        return strsql

    def gen_sql(self, module, idiom, except_dict, limit_flag, *args, **kwargs):
        strsql = ""
        self.idiom = idiom
        if 0 == len(idiom):
            return strsql

        self.pinyin = "".join(pypinyin.pinyin(idiom)[-1])
        self.lzpinyin = pypinyin.lazy_pinyin(idiom)[-1]
        self.mulpinyin = pypinyin.pinyin(idiom[-1], heteronym=True)[0]

        LOG_INFO(self.pinyin, self.lzpinyin, self.mulpinyin)

        if module in self.functions:
            strsql = self.functions[module](*args, **kwargs)

            if 0 != len(except_dict):
                LOG_TRACE(except_dict)
                strsql += " and a.idiom not in('" + "','".join(except_dict) + "')"
            if 1 == limit_flag:
                strsql += " order by random() limit 1"
        else:
            strsql = self.default(*args, **kwargs)
        return strsql

    def default(self, *args, **kwargs):
        strsql = ""
        pass
        return strsql

    def function_all(self):
        strsql = (
            "select * from `"
            + self.table_name
            + "` a where substr(a.idiom, 1, 1) = '"
            + self.idiom[-1]
            + "'"
        )
        strsql += " and pinyin_fst = '" + self.pinyin + "'"
        return strsql

    def function_word(self):
        strsql = (
            "select * from `"
            + self.table_name
            + "` a where substr(a.idiom, 1, 1) = '"
            + self.idiom[-1]
            + "'"
        )
        return strsql

    def function_pinyin(self):
        strsql = (
            "select * from `"
            + self.table_name
            + "` a where a.pinyin_fst = '"
            + self.pinyin
            + "'"
        )
        return strsql

    def function_lzpinyin(self):
        strsql = (
            "select * from `"
            + self.table_name
            + "` a where a.pinyin_fst_lz = '"
            + self.lzpinyin
            + "'"
        )
        return strsql

    def function_multi(self):
        strsql = (
            "select * from `"
            + self.table_name
            + "` a where a.pinyin_fst in('"
            + "','".join(self.mulpinyin)
            + "')"
        )
        return strsql
