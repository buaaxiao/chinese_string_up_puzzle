#!/usr/bin/env python3
# -*- coding : utf-8-*-
# coding:unicode_escape

import re
import json
import numpy
import random
import pypinyin
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from xcommon.xlog import *
from chinese_string_enum import *


# '''成语引擎'''
class Chinese_string_engine(object):
    def __init__(self, data_pathfile, default_module=enum_Puzzle_Module.Model_All):
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
        LOG_TRACE(data_pathfile)
        fp = open(data_pathfile, 'r', encoding='gbk', errors='ignore')

        idiom_dict = {}
        idiom_instance = {}
        idiom_tmp = ''
        for line in fp.readlines():
            line = line.strip()
            if '<->' == line and '' != idiom_tmp:
                idiom_dict[idiom_tmp[0]][idiom_tmp] = idiom_instance.copy()
                idiom_tmp = ''
                idiom_instance.clear()
                continue

            item = re.split(r'\t+', line.rstrip('\t'))
            if len(item) != 2:
                continue

            if item[0] == '成语':
                idiom_tmp = item[1]
                if idiom_tmp[0] not in idiom_dict:
                    idiom_dict[idiom_tmp[0]] = {}
            idiom_instance[item[0]] = item[1]
        self.idiom_dict["idiom"] = idiom_dict

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
        print(str(self.idiom_dict).replace('\'', '"'))

    def _get_nextIdiom(self, idiom, except_dict=[], puzzle_model=enum_Puzzle_Module.Model_All):
        LOG_TRACE(idiom, puzzle_model, except_dict)
        pinyin = ''.join(pypinyin.pinyin(idiom)[-1])
        lzpinyin = pypinyin.lazy_pinyin(idiom)[-1]
        mulpinyin = pypinyin.pinyin(idiom[-1], heteronym=True)[0]
        LOG_TRACE(pinyin, lzpinyin, mulpinyin)

        idiom_dict_data = self.idiom_dict['idiom']
        idiom_answer = None
        answer_list = []
        # 同字同音匹配模式
        if enum_Puzzle_Module.Model_All == puzzle_model and idiom[-1] in idiom_dict_data:
            idiom_data_list = list(idiom_dict_data[idiom[-1]])
            answer_list = list(filter(
                lambda x: ''.join(pypinyin.pinyin(x)[0]) == pinyin, idiom_data_list))

        # 同字匹配模式
        elif enum_Puzzle_Module.Model_Word == puzzle_model and idiom[-1] in idiom_dict_data:
            answer_list = list(idiom_dict_data[idiom[-1]])

        elif not set(mulpinyin).isdisjoint(self.idiom_dict['mulpinyin'].keys()) and (enum_Puzzle_Module.Model_LzPinyin == puzzle_model or enum_Puzzle_Module.Model_Pinyin == puzzle_model or enum_Puzzle_Module.Model_Multi == puzzle_model):
            answer_list_tmp = []
            answer_list_pytmp = []
            key_list = list(filter(
                lambda key: key in mulpinyin, self.idiom_dict['mulpinyin'].keys()))
            for key in key_list:
                answer_list_tmp += self.idiom_dict['mulpinyin'][key]

            # 同音匹配模式
            if enum_Puzzle_Module.Model_Pinyin == puzzle_model or enum_Puzzle_Module.Model_Multi == puzzle_model:
                answer_list = list(filter(
                    lambda word: ''.join(pypinyin.pinyin(word)[0]) == pinyin, answer_list_tmp))
                answer_list_pytmp = answer_list

            # 同拼匹配模式
            if enum_Puzzle_Module.Model_LzPinyin == puzzle_model:
                if not answer_list_pytmp:
                    answer_list = list(filter(
                        lambda word: pypinyin.lazy_pinyin(word)[0] == lzpinyin, answer_list_tmp))
                else:
                    answer_list = answer_list_pytmp

            # 多音匹配模式
            if enum_Puzzle_Module.Model_Multi == puzzle_model:
                if not answer_list_pytmp:
                    answer_list = list(filter(
                        lambda word: ''.join(pypinyin.pinyin(word)[0]) in mulpinyin, answer_list_tmp))
                else:
                    answer_list = answer_list_pytmp

        if set(answer_list) < set(except_dict):
            answer_list = []

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
            idiom, except_dict, self.puzzle_model)
        if None != ai_answer:
            idiom_promote, idiom_promote_dict = self._get_nextIdiom(
                ai_answer, except_dict, self.puzzle_model)

        return ai_answer, idiom_promote, idiom_promote_dict

    def _get_answerText(self, idiom, except_dict=['成语', '拼音']):
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
        LOG_TRACE(idiom, idiom_check)
        idiom_head_pinyin = ''.join(pypinyin.pinyin(idiom)[0])
        idiom_check_tail_pinyin = ''.join(pypinyin.pinyin(idiom_check)[-1])
        LOG_TRACE(idiom_head_pinyin, idiom_check_tail_pinyin)
        if enum_Puzzle_Module.Model_All == self.puzzle_model and (idiom[0] != idiom_check[-1] or idiom_head_pinyin != idiom_check_tail_pinyin):
            return enum_Puzzle_Unmatch.Unmatch_All

        if enum_Puzzle_Module.Model_Word == self.puzzle_model and idiom[0] != idiom_check[-1]:
            return enum_Puzzle_Unmatch.Unmatch_Word

        idiom_head_lzpinyin = pypinyin.lazy_pinyin(idiom)[0]
        idiom_check_tail_lzpinyin = pypinyin.lazy_pinyin(idiom_check)[-1]
        LOG_TRACE(idiom_head_lzpinyin, idiom_check_tail_lzpinyin)
        if enum_Puzzle_Module.Model_LzPinyin == self.puzzle_model and idiom_head_lzpinyin != idiom_check_tail_lzpinyin:
            return enum_Puzzle_Unmatch.Unmatch_LzPinyin

        if enum_Puzzle_Module.Model_Pinyin == self.puzzle_model and idiom_head_pinyin != idiom_check_tail_pinyin:
            return enum_Puzzle_Unmatch.Unmatch_Pinyin

        mulpinyin = pypinyin.pinyin(idiom_check[-1], heteronym=True)[0]
        if enum_Puzzle_Module.Model_Multi == self.puzzle_model and idiom_head_pinyin not in mulpinyin:
            return enum_Puzzle_Unmatch.Unmatch_Multi

        return 0

    def get_model(self):
        return self.puzzle_model


# '''run'''
if __name__ == '__main__':
    data_filepath = progam_path + './data/data.json'
    engine = Chinese_string_engine(data_filepath)
    idiom = '白雪难和'
    except_dict = {}
    LOG_TRACE(engine._get_nextIdiom(
        idiom, except_dict, enum_Puzzle_Module.Model_All))
    LOG_TRACE(engine._get_nextIdiom(
        idiom, except_dict, enum_Puzzle_Module.Model_Word))
    LOG_TRACE(engine._get_nextIdiom(
        idiom, except_dict, enum_Puzzle_Module.Model_LzPinyin))
    LOG_TRACE(engine._get_nextIdiom(
        idiom, except_dict, enum_Puzzle_Module.Model_Pinyin))
    LOG_TRACE(engine._get_nextIdiom(
        idiom, except_dict, enum_Puzzle_Module.Model_Multi))

    LOG_TRACE(engine._get_answerText(idiom))
    LOG_TRACE(engine.get_idiom_instance(idiom))

    if len(sys.argv) > 1 and 'dict' == sys.argv[1]:
        engine._generate_dict(progam_path + './data/data_source.txt')

    continue_dict = {
        # enum_Puzzle_Module.Model_All: 'all',
        enum_Puzzle_Module.Model_Word: 'word',
        enum_Puzzle_Module.Model_LzPinyin: 'lzpinyin',
        enum_Puzzle_Module.Model_Pinyin: 'pinyin',
        enum_Puzzle_Module.Model_Multi: 'multi',
        enum_Puzzle_Module.Model_BattleSingle: 'battlesingle',
        enumBarButton_Operate.Menu_ControlId_Work_Promote: 'promote',
        enumBarButton_Operate.Menu_ControlId_Work_Auto: 'auto',
    }

    for control_id in continue_dict:
        LOG_TRACE(type(control_id), type(continue_dict[control_id]))
        LOG_TRACE(control_id, continue_dict[control_id])

    LOG_TRACE(pypinyin.pinyin('奥', heteronym=True)[0])
    LOG_TRACE(pypinyin.pinyin('奥', heteronym=False)[0])
    LOG_TRACE(pypinyin.lazy_pinyin('奥')[0])
