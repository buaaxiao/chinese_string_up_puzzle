#!/usr/bin/env python3
# -*- coding : utf-8-*-
# coding:unicode_escape

import json
import random
import numpy
import pypinyin
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from chinese_string_const import *
from xcommon.xlog import *

# 成语引擎


class Chinese_string_engine(object):
    def __init__(self, data_pathfile, default_module):
        self._load_data(data_pathfile)
        self.puzzle_model = default_module

    def set_model(self, puzzle_model):
        self.puzzle_model = puzzle_model

    # '''读取成语数据'''
    def _load_data(self, data_pathfile):
        with open(data_pathfile) as f:
            self.idiom_dict = json.load(f)

    # '''生成字典'''
    def _generate_dict(self, data_pathfile):
        with open(data_pathfile) as f:
            self.idiom_dict = json.load(f)

        idiom_dict_data = self.idiom_dict['idiom']
        ins_dict = {}
        mulpy_dict = {}
        for idiom_key in list(idiom_dict_data.keys()):
            mulpinyin = pypinyin.pinyin(idiom_key, heteronym=True)[0]
            for xmul_py in mulpinyin:
                if xmul_py not in mulpy_dict:
                    mulpy_dict[xmul_py] = []
                mulpy_dict[xmul_py] += list(idiom_dict_data[idiom_key].keys())

            for idiom_dict in idiom_dict_data:
                ins_dict |= idiom_dict_data[idiom_dict]

        LOG_TRACE(ins_dict)
        LOG_TRACE(mulpy_dict)

        self.idiom_dict['instance'] = ins_dict
        self.idiom_dict['mulpinyin'] = mulpy_dict
        LOG_INFO(self.idiom_dict)

    def _get_nextIdiom(self, idiom, except_dict=[]):
        LOG_TRACE(idiom, self.puzzle_model, except_dict)
        pinyin = ''.join(pypinyin.pinyin(idiom)[-1])
        lzpinyin = pypinyin.lazy_pinyin(idiom)[-1]
        mulpinyin = pypinyin.pinyin(idiom[-1], heteronym=True)[0]
        LOG_TRACE(pinyin, lzpinyin, mulpinyin)

        idiom_dict_data = self.idiom_dict['idiom']
        idiom_answer = None
        answer_list = []
        # 同字同音匹配模式
        if enum_Puzzle_Module.Model_All == self.puzzle_model and idiom[-1] in idiom_dict_data:
            idiom_data_list = list(idiom_dict_data[idiom[-1]])
            answer_list = list(filter(
                lambda x: ''.join(pypinyin.pinyin(x)[0]) == pinyin, idiom_data_list))

        # 同字匹配模式
        elif enum_Puzzle_Module.Model_Word == self.puzzle_model and idiom[-1] in idiom_dict_data:
            answer_list = list(idiom_dict_data[idiom[-1]])

        elif not set(mulpinyin).isdisjoint(self.idiom_dict['mulpinyin'].keys()) and (enum_Puzzle_Module.Model_LzPinyin == self.puzzle_model or enum_Puzzle_Module.Model_Pinyin == self.puzzle_model or enum_Puzzle_Module.Model_Multi == self.puzzle_model):
            answer_list_tmp = []
            key_list = list(filter(
                lambda key: key in mulpinyin, self.idiom_dict['mulpinyin'].keys()))
            for key in key_list:
                answer_list_tmp += self.idiom_dict['mulpinyin'][key]

            # 多音匹配模式
            if enum_Puzzle_Module.Model_Multi == self.puzzle_model:
                answer_list = list(filter(
                    lambda word: ''.join(pypinyin.pinyin(word)[0]) in mulpinyin, answer_list_tmp))

            # 同拼匹配模式
            elif enum_Puzzle_Module.Model_LzPinyin == self.puzzle_model:
                answer_list = list(filter(
                    lambda word: pypinyin.lazy_pinyin(word)[0] == lzpinyin, answer_list_tmp))

            # 同音匹配模式
            elif enum_Puzzle_Module.Model_Pinyin == self.puzzle_model:
                answer_list = list(filter(
                    lambda word: ''.join(pypinyin.pinyin(word)[0]) == pinyin, answer_list_tmp))

        if 0 != len(answer_list):
            idiom_answer = random.choice(
                list(filter(lambda x: x not in except_dict and x != idiom, answer_list)))
        LOG_TRACE(idiom_answer)
        LOG_TRACE(answer_list)

        return idiom_answer, answer_list

    def get_nextIdom(self, idiom, except_dict=[]):
        idiom_promote = None
        idiom_promote_dict = []
        ai_answer, _ = self._get_nextIdiom(
            idiom, except_dict)
        if None != ai_answer:
            idiom_promote, idiom_promote_dict = self._get_nextIdiom(
                ai_answer, except_dict)

        return ai_answer, idiom_promote, idiom_promote_dict

    def _get_answerText(self, idiom, except_dict=[]):
        answer_idiom_dict = self.get_idiom_instance(idiom)
        if None == answer_idiom_dict:
            return None

        text_ret = ''
        for x in list(filter(lambda key: key not in except_dict, answer_idiom_dict.keys())):
            text_ret += x + ':' + answer_idiom_dict[x] + '\n'

        return text_ret.strip('\n')

    def _get_spell(self, idiom):
        answer_idiom_dict = self.get_idiom_instance(idiom)
        if None == answer_idiom_dict:
            return None

        if USE_DICT_SPELL:
            spell = answer_idiom_dict[idiom]['拼音']
        else:
            spell = '%s' % ' '.join(
                numpy.hstack(pypinyin.pinyin(idiom)))

        return spell

    def get_idiom_instance(self, idiom):
        if idiom not in list(self.idiom_dict['instance'].keys()):
            return None
        return self.idiom_dict['instance'][idiom]

    def idiom_exists(self, idiom):
        return True if idiom in list(self.idiom_dict['instance'].keys()) else False

    def check_idiom(self, idiom, idiom_check):
        LOG_INFO(idiom, idiom_check)
        idiom_head_pinyin = ''.join(pypinyin.pinyin(idiom)[0])
        idiom_check_tail_pinyin = ''.join(pypinyin.pinyin(idiom_check)[-1])
        LOG_INFO(idiom_head_pinyin, idiom_check_tail_pinyin)
        if enum_Puzzle_Module.Model_All == self.puzzle_model and (idiom[0] != idiom_check[-1] or idiom_head_pinyin != idiom_check_tail_pinyin):
            return enum_Puzzle_Unmatch.Unmatch_All

        if enum_Puzzle_Module.Model_Word == self.puzzle_model and idiom[0] != idiom_check[-1]:
            return enum_Puzzle_Unmatch.Unmatch_Word

        idiom_head_lzpinyin = pypinyin.lazy_pinyin(idiom)[-1]
        idiom_check_tail_lzpinyin = pypinyin.lazy_pinyin(idiom_check)[-1]
        LOG_INFO(idiom_head_lzpinyin, idiom_check_tail_lzpinyin)
        if enum_Puzzle_Module.Model_LzPinyin == self.puzzle_model and idiom_head_lzpinyin != idiom_check_tail_lzpinyin:
            return enum_Puzzle_Unmatch.Unmatch_LzPinyin

        if enum_Puzzle_Module.Model_Pinyin == self.puzzle_model and idiom_head_pinyin != idiom_check_tail_pinyin:
            return enum_Puzzle_Unmatch.Unmatch_Pinyin

        mulpinyin = pypinyin.pinyin(idiom_check[-1], heteronym=True)[0]
        if enum_Puzzle_Module.Model_Multi == self.puzzle_model and idiom_head_pinyin not in mulpinyin:
            return enum_Puzzle_Unmatch.Unmatch_Multi

        return 0


# '''run'''
if TEST_FLAG:
    if __name__ == '__main__':
        data_filepath = progam_path + 'data/data.json'
        engine = Chinese_string_engine(data_filepath)
        idiom = '白雪难和'
        except_dict = {}
        LOG_INFO(engine._get_nextIdiom(
            idiom, enum_Puzzle_Module.Model_All, except_dict))
        LOG_INFO(engine._get_nextIdiom(
            idiom, enum_Puzzle_Module.Model_Word, except_dict))
        LOG_INFO(engine._get_nextIdiom(
            idiom, enum_Puzzle_Module.Model_LzPinyin, except_dict))
        LOG_INFO(engine._get_nextIdiom(
            idiom, enum_Puzzle_Module.Model_Pinyin, except_dict))
        LOG_INFO(engine._get_nextIdiom(
            idiom, enum_Puzzle_Module.Model_Multi, except_dict))

        LOG_INFO(engine._get_answerText(idiom))

        # LOG_INFO(engine.get_idiom_instance(idiom))
