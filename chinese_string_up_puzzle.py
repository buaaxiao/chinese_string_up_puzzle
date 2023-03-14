#!/usr/bin/env python3
# -*- coding : utf-8-*-
# coding:unicode_escape

'''
#############################################
# -author: buaaxiao                         #
# -date: 2023-03-05                         #
# -program: Chinese string up puzzle        #
#############################################
'''

import sys
import random
import numpy
import pypinyin
import json
import enum
import pyttsx3
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from xcommon.xlog import *

# '''常量定义'''
HIS_DISPALY_USER = '【我方】'
HIS_DISPALY_AI = '【电脑】'
PROGAM_TITLE = '成语接龙'
PROGAM_SIZE_FIX = False
USE_DICT_SPELL = False
TTS_OPT = False
AUTO_TIMER_INTERVAL = 1

# '''枚举定义'''


class enumBarButton_Module(enum.Enum):
    Menu_ControlId_All = 0b1
    Menu_ControlId_Word = 0b10
    Menu_ControlId_LzPinyin = 0b100
    Menu_ControlId_Pinyin = 0b1000
    Menu_ControlId_Multi = 0b10000
    Menu_ControlId_BattleSingle = 0b100000


class enumBarButton_Display(enum.Enum):
    Menu_ControlId_All = 0b1
    Menu_ControlId_USER = 0b10
    Menu_ControlId_AI = 0b1000


class enumBarButton_Operate(enum.Enum):
    Menu_ControlId_Work_Auto = 0b1
    Menu_ControlId_Work_Promote = 0b10
    Menu_ControlId_Work_Continue = 0b100


class enum_Idiom_Source(enum.Enum):
    ENUM_IDIOM_SOURCE_USER = 0
    ENUM_IDIOM_SOURCE_AI = 1
    ENUM_IDIOM_SOURCE_AUTO = 2


class enum_Init_Type(enum.Enum):
    ENUM_INIT_STARTUP = 0
    ENUM_INIT_RESTART = 1
    ENUM_INIT_CONTINUE = 2

# '''成语接龙'''


class Chinese_string_up_puzzle(QMainWindow):
    # 暂未实现功能
    def _to_beContinue(self,  control_id, btn=None):
        self.continue_set = [
            # enumBarButton_Module.Menu_ControlId_Multi,
            # enumBarButton_Operate.Menu_ControlId_Work_Promote,
            # enumBarButton_Operate.Menu_ControlId_Work_Continue,
            # enumBarButton_Operate.Menu_ControlId_Work_Auto,
            enumBarButton_Module.Menu_ControlId_BattleSingle,
        ]

        if control_id in self.continue_set:
            QMessageBox.information(
                self, 'TODO', 'to be continue!', QMessageBox.StandardButton.Ok)
            if btn:
                btn.setChecked(False)
            return True

        return False

    def __init__(self, parent=None, **kwargs):
        LOG_INFO(
            '----------------------------------开始接龙----------------------------------')
        super(Chinese_string_up_puzzle, self).__init__(parent)
        if TTS_OPT:
            self.pt = pyttsx3.init()
        self.auto_timer = QTimer()

        # 初始化
        self._add_moduleMenuBar()
        self._add_displayMenuBar()
        self._add_operateMenuBar()
        self._init_widget()
        self._init_data(enum_Init_Type.ENUM_INIT_STARTUP)

    def _init_widget(self):
        self.setWindowTitle(PROGAM_TITLE)

        if PROGAM_SIZE_FIX:
            self.setFixedSize(985, 609)
        else:
            self.setSizePolicy(QSizePolicy.Policy.Expanding,
                               QSizePolicy.Policy.Expanding)
            self.resize(1000, 618)
        self.user_input_label = QLabel('我方')
        self.user_input_edit = QLineEdit()
        self.user_input_edit.setPlaceholderText('我方输入')
        self.user_input_button = QPushButton('确定')

        self.restart_button = QPushButton('重新开始')

        self.user_spell_label = QLabel('我方成语拼音')
        self.user_spell_edit = QLineEdit()
        self.user_spell_edit.setPlaceholderText('我方成语拼音')
        self.user_spell_edit.setReadOnly(True)

        self.user_explain_label = QLabel('我方成语释义')
        self.user_explain_edit = QTextEdit()
        self.user_explain_edit.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        self.user_explain_edit.setPlaceholderText('我方成语释义')
        self.user_explain_edit.setReadOnly(True)

        self.ai_input_label = QLabel('电脑方')
        self.ai_input_edit = QLineEdit()
        self.ai_input_edit.setPlaceholderText('电脑接龙')
        self.ai_input_edit.setReadOnly(True)

        self.ai_spell_label = QLabel('电脑方成语拼音')
        self.ai_spell_edit = QLineEdit()
        self.ai_spell_edit.setPlaceholderText('电脑方成语拼音')
        self.ai_spell_edit.setReadOnly(True)

        self.ai_explain_label = QLabel('电脑方成语释义')
        self.ai_explain_edit = QTextEdit()
        self.ai_explain_edit.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        self.ai_explain_edit.setPlaceholderText('电脑方成语释义')
        self.ai_explain_edit.setReadOnly(True)

        self.idiom_used_edit = QTextEdit()
        self.idiom_used_edit.setWordWrapMode(
            QTextOption.WrapMode.WordWrap)
        self.idiom_used_edit.setPlaceholderText('已使用成语')
        self.idiom_used_edit.setReadOnly(True)
        self.idiom_used_edit.setFixedWidth(211)

        self.idiom_promote_edit = QTextEdit()
        self.idiom_promote_edit.setWordWrapMode(
            QTextOption.WrapMode.WordWrap)
        self.idiom_promote_edit.setPlaceholderText('智能提示')
        self.idiom_promote_edit.setReadOnly(True)
        self.idiom_promote_edit.setFixedWidth(211)

        # 按键绑定
        self.user_input_edit.returnPressed.connect(
            self.user_input_button.click)
        self.user_input_button.clicked.connect(self._ai_round)
        self.restart_button.clicked.connect(
            lambda: self._init_data(enum_Init_Type.ENUM_INIT_RESTART))

        # 布局
        self.grid = QGridLayout()
        self.grid.setSpacing(12)
        self.grid.addWidget(self.user_input_label, 0, 0, 1, 1)
        self.grid.addWidget(self.user_input_edit, 0, 1, 1, 1)
        self.grid.addWidget(self.user_input_button, 0, 2, 1, 1)
        self.grid.addWidget(self.user_spell_label, 1, 0, 1, 1)
        self.grid.addWidget(self.user_spell_edit, 1, 1, 1, 2)
        self.grid.addWidget(self.user_explain_label, 2, 0, 1, 1)
        self.grid.addWidget(self.user_explain_edit, 2, 1, 1, 2)
        self.grid.addWidget(self.ai_input_label, 3, 0, 1, 1)
        self.grid.addWidget(self.ai_input_edit, 3, 1, 1, 1)
        self.grid.addWidget(self.restart_button, 3, 2, 1, 1)
        self.grid.addWidget(self.ai_spell_label, 4, 0, 1, 1)
        self.grid.addWidget(self.ai_spell_edit, 4, 1, 1, 2)
        self.grid.addWidget(self.ai_explain_label, 5, 0, 1, 1)
        self.grid.addWidget(self.ai_explain_edit, 5, 1, 1, 2)
        self.grid.addWidget(self.idiom_used_edit, 0, 3, 6, 1)
        self.grid.addWidget(self.idiom_promote_edit, 0, 4, 6, 1)

        self.widget = QWidget()
        self.widget.setLayout(self.grid)
        self.setCentralWidget(self.widget)

    def _add_moduleMenuBar(self):
        menu = self.menuBar()

        self.module_action_all = QAction(
            QIcon(progam_path + 'image/match_all.jpg'), '完全匹配', self)
        self.module_action_all.setStatusTip('完全匹配：支持首尾读音和字都匹配')
        self.module_action_all.setCheckable(True)
        self.module_action_all.setChecked(True)
        self.module_action = enumBarButton_Module.Menu_ControlId_All
        self.module_action_all.triggered.connect(
            lambda: self._on_ModuleMenuBarClick(self.module_action_all, enumBarButton_Module.Menu_ControlId_All))

        self.module_action_word = QAction(
            QIcon(progam_path + 'image/match_word.jpg'), '字匹配', self)
        self.module_action_word.setStatusTip('字匹配：支持首尾字匹配')
        self.module_action_word.setCheckable(True)
        self.module_action_word.triggered.connect(
            lambda: self._on_ModuleMenuBarClick(self.module_action_word, enumBarButton_Module.Menu_ControlId_Word))

        self.module_action_lzpinyin = QAction(
            QIcon(progam_path + 'image/match_lzpinyin.jpg'), '读音模糊匹配', self)
        self.module_action_lzpinyin.setStatusTip('读音模糊匹配：支持首尾读音模糊匹配')
        self.module_action_lzpinyin.setCheckable(True)
        self.module_action_lzpinyin.triggered.connect(
            lambda: self._on_ModuleMenuBarClick(self.module_action_lzpinyin, enumBarButton_Module.Menu_ControlId_LzPinyin))

        self.module_action_pinyin = QAction(
            QIcon(progam_path + 'image/match_pinyin.jpg'), '读音匹配', self)
        self.module_action_pinyin.setStatusTip('读音匹配：支持首尾读音完全匹配')
        self.module_action_pinyin.setCheckable(True)
        self.module_action_pinyin.triggered.connect(
            lambda: self._on_ModuleMenuBarClick(self.module_action_pinyin, enumBarButton_Module.Menu_ControlId_Pinyin))

        self.module_action_multi = QAction(
            QIcon(progam_path + 'image/match_multi.jpg'), '多音字匹配', self)
        self.module_action_multi.setStatusTip('多音字模式：支持首尾多音字匹配')
        self.module_action_multi.setCheckable(True)
        self.module_action_multi.triggered.connect(
            lambda: self._on_ModuleMenuBarClick(self.module_action_multi, enumBarButton_Module.Menu_ControlId_Multi))

        self.module_action_BattleSingle = QAction(
            QIcon(progam_path + 'image/match_battle_single.jpg'), '单回合', self)
        self.module_action_BattleSingle.setStatusTip('单回合模式：一问一答')
        self.module_action_BattleSingle.setCheckable(True)
        self.module_action_BattleSingle.triggered.connect(
            lambda: self._on_ModuleMenuBarClick(self.module_action_BattleSingle, enumBarButton_Module.Menu_ControlId_BattleSingle))

        file_menu = menu.addMenu('模式选择(&m)')
        file_menu.addAction(self.module_action_all)
        file_menu.addAction(self.module_action_word)
        file_menu.addAction(self.module_action_lzpinyin)
        file_menu.addAction(self.module_action_pinyin)
        file_menu.addAction(self.module_action_multi)
        file_menu.addAction(self.module_action_BattleSingle)

    def _on_ModuleMenuBarClick(self, btn, type):
        if self._to_beContinue(type, btn):
            return

        if not btn.isChecked():
            return

        # 模式改变之后继续接龙
        if self.module_action != type:
            LOG_INFO("switch", self.module_action, "to", type)
            if self.idiom in self.idiom_used['used']:
                # 电脑未接起来,重新选择模式之后提示成语已使用
                self.idiom_used['used'] = list(
                    filter(lambda x: x != self.idiom, self.idiom_used['used']))
                self.idiom = None
        self.module_action = type

        if not enumBarButton_Module.Menu_ControlId_All.value & type.value:
            self.module_action_all.setChecked(False)
        if not enumBarButton_Module.Menu_ControlId_Word.value & type.value:
            self.module_action_word.setChecked(False)
        if not enumBarButton_Module.Menu_ControlId_LzPinyin.value & type.value:
            self.module_action_lzpinyin.setChecked(False)
        if not enumBarButton_Module.Menu_ControlId_Pinyin.value & type.value:
            self.module_action_pinyin.setChecked(False)
        if not enumBarButton_Module.Menu_ControlId_Multi.value & type.value:
            self.module_action_multi.setChecked(False)
        if not enumBarButton_Module.Menu_ControlId_BattleSingle.value & type.value:
            self.module_action_BattleSingle.setChecked(False)

    def _add_displayMenuBar(self):
        menu = self.menuBar()

        self.display_action_all = QAction(
            QIcon(progam_path + 'image/show_all.jpg'), '全部', self)
        self.display_action_all.setStatusTip('展示全部历史记录')
        self.display_action_all.setCheckable(True)
        # 默认显示全部历史
        self.display_action_all.setChecked(True)
        self.display_action_all.triggered.connect(
            lambda: self._on_DisplayMenuBarClick(self.display_action_all, enumBarButton_Display.MenuControlId_All))

        self.display_action_user = QAction(
            QIcon(progam_path + 'image/show_user.jpg'), '我方', self)
        self.display_action_user.setStatusTip('展示我方历史记录')
        self.display_action_user.setCheckable(True)
        self.display_action_user.triggered.connect(
            lambda: self._on_DisplayMenuBarClick(self.display_action_user, enumBarButton_Display.Menu_ControlId_USER))

        self.display_action_ai = QAction(
            QIcon(progam_path + 'image/show_ai.jpg'), '电脑', self)
        self.display_action_ai.setStatusTip('展示电脑历史记录')
        self.display_action_ai.setCheckable(True)
        self.display_action_ai.triggered.connect(
            lambda: self._on_DisplayMenuBarClick(self.display_action_ai, enumBarButton_Display.Menu_ControlId_AI))

        file_menu = menu.addMenu('显示(&d)')
        file_menu.addAction(self.display_action_all)
        file_menu.addAction(self.display_action_user)
        file_menu.addAction(self.display_action_ai)

    def _on_DisplayMenuBarClick(self, btn, type):
        if self._to_beContinue(type, btn):
            return

        if not btn.isChecked():
            return

        LOG_TRACE(type)
        self.idiom_used_edit.clear()
        if not enumBarButton_Display.Menu_ControlId_All.value & type.value:
            self.display_action_all.setChecked(False)
        else:
            for item in self.idiom_used['all']:
                if item[0] == 'user':
                    self.idiom_used_edit.append(HIS_DISPALY_USER + item[1])
                elif item[0] == 'ai':
                    self.idiom_used_edit.append(HIS_DISPALY_AI + item[1])

        if not enumBarButton_Display.Menu_ControlId_USER.value & type.value:
            self.display_action_user.setChecked(False)
        else:
            for item in self.idiom_used['user']:
                self.idiom_used_edit.append(HIS_DISPALY_USER + item)

        if not enumBarButton_Display.Menu_ControlId_AI.value & type.value:
            self.display_action_ai.setChecked(False)
        else:
            for item in self.idiom_used['ai']:
                self.idiom_used_edit.append(HIS_DISPALY_AI + item)

    def _add_operateMenuBar(self):
        menu = self.menuBar()

        self.operate_action_auto = QAction(
            QIcon(progam_path + 'image/work_auto.jpg'), '自动接龙', self)
        self.operate_action_auto.setStatusTip('自动接龙：人工发起，电脑自动接龙并显示结果')
        self.operate_action_auto.setCheckable(True)
        # self.operate_action_auto.setChecked(True)
        self.operate_action_auto.triggered.connect(
            lambda: self._on_OperateMenuBarClick(self.operate_action_auto, enumBarButton_Operate.Menu_ControlId_Work_Auto))

        self.operate_action_promote = QAction(
            QIcon(progam_path + 'image/work_promote.jpg'), '显示提示', self)
        self.operate_action_promote.setStatusTip('显示提示框')
        self.operate_action_promote.setCheckable(True)
        # self.operate_action_promote.setChecked(True)
        self.operate_action_promote.triggered.connect(
            lambda: self._on_OperateMenuBarClick(self.operate_action_promote, enumBarButton_Operate.Menu_ControlId_Work_Promote))

        self.operate_action_continue = QAction(
            QIcon(progam_path + 'image/work_continue.jpg'), '重开不清零', self)
        self.operate_action_continue.setStatusTip('重开不清零')
        self.operate_action_continue.setCheckable(True)
        # self.operate_action_continue.setChecked(True)
        self.operate_action_continue.triggered.connect(
            lambda: self._on_OperateMenuBarClick(self.operate_action_continue, enumBarButton_Operate.Menu_ControlId_Work_Continue))

        file_menu = menu.addMenu('操作(&c)')
        file_menu.addAction(self.operate_action_auto)
        file_menu.addAction(self.operate_action_promote)
        file_menu.addAction(self.operate_action_continue)

    def _on_OperateMenuBarClick(self, btn, type):
        if self._to_beContinue(type, btn):
            return

        # if not btn.isChecked():
        #     return

        if enumBarButton_Operate.Menu_ControlId_Work_Auto.value & type.value:
            pass

        if enumBarButton_Operate.Menu_ControlId_Work_Promote.value & type.value:
            self.idiom_promote_edit.clear()
            if btn.isChecked():
                if not self.answer_idiom_dict_promote:
                    self.idiom_promote_edit.append('No Promote')
                else:
                    for ele in list(self.answer_idiom_dict_promote.keys()):
                        self.idiom_promote_edit.append(ele)

    # '''数据加载'''
    def _init_data(self, type):
        LOG_INFO('重新开始', type)
        if not self.operate_action_continue.isChecked():
            self.user_input_edit.clear()
            self.user_spell_edit.clear()
            self.user_explain_edit.clear()

            self.ai_input_edit.clear()
            self.ai_spell_edit.clear()
            self.ai_explain_edit.clear()
            self.idiom_used_edit.clear()

            self.idiom_promote_edit.clear()

        self.idiom = None
        self.ai_answer = None

        self.idiom_used = {}
        self.idiom_used['all'] = []
        self.idiom_used['user'] = []
        self.idiom_used['ai'] = []
        self.idiom_used['used'] = []

        self.answer_idiom_dict_promote = {}

        # 读取数据
        data_filepath = progam_path + 'data/data.json'
        self._load_data(data_filepath)

   # '''读取成语数据'''
    def _load_data(self, data_filepath):
        with open(data_filepath) as f:
            self.idiom_dict = json.load(f)

        idiom_dict_data = self.idiom_dict['idiom']
        py_dict = {}
        lzpy_dict = {}
        for idiom_key in list(idiom_dict_data.keys()):
            pinyin = pypinyin.pinyin(idiom_key)[0][0]
            if pinyin not in py_dict:
                py_dict[pinyin] = []
            py_dict[pinyin] += list(idiom_dict_data[idiom_key].keys())
            lzpinyin = pypinyin.lazy_pinyin(idiom_key)[0]
            if lzpinyin not in lzpy_dict:
                lzpy_dict[lzpinyin] = []
            lzpy_dict[lzpinyin] += list(idiom_dict_data[idiom_key].keys())
        LOG_DEBUG(py_dict)
        LOG_DEBUG(lzpy_dict)

        self.idiom_dict['pinyin'] = py_dict
        self.idiom_dict['lzpinyin'] = lzpy_dict
        LOG_DEBUG(self.idiom_dict)

  #  '''检测我方输入成语是否合法'''
    def _check_userInputValid(self, idiom):
        idiom_dict_data = self.idiom_dict['idiom']
        # 成语已使用
        if idiom in self.idiom_used['used']:
            QMessageBox.warning(
                self, '成语已使用', '你输入的成语已在本次接龙中使用, 请重新输入!', QMessageBox.StandardButton.Ok)
        # 无记录
        elif not (idiom[0] in idiom_dict_data and idiom in idiom_dict_data[idiom[0]]):
            QMessageBox.warning(
                self, '输入错误', '系统成语库中无该记录!', QMessageBox.StandardButton.Ok)
            return False

        if self.ai_answer:
            idiom_head_pinyin = ''.join(list(pypinyin.pinyin(idiom))[0])
            ai_answer_tail_pinyin = ''.join(
                list(pypinyin.pinyin(self.ai_answer))[-1])
            LOG_TRACE(idiom_head_pinyin, ai_answer_tail_pinyin)
            if self.module_action_all.isChecked() and (idiom[0] != self.ai_answer[-1] or idiom_head_pinyin != ai_answer_tail_pinyin):
                if self.module_action_all.isChecked():
                    QMessageBox.warning(
                        self, '输入错误', '首尾字及拼音匹配失败!', QMessageBox.StandardButton.Ok)
                    return False

            if self.module_action_word.isChecked() and idiom[0] != self.ai_answer[-1]:
                QMessageBox.warning(
                    self, '输入错误', '首尾字匹配失败!', QMessageBox.StandardButton.Ok)
                return False

            if self.module_action_lzpinyin.isChecked() and pypinyin.lazy_pinyin(idiom[0])[0] != pypinyin.lazy_pinyin(self.ai_answer[-1])[0]:
                QMessageBox.warning(
                    self, '输入错误', '首尾字拼音模糊匹配失败!',   QMessageBox.StandardButton.Ok)
                return False

            idiom_head_word_pinyin = ''.join(
                list(pypinyin.pinyin(idiom[0]))[0])
            ai_answer_tail_word_pinyin = ''.join(
                list(pypinyin.pinyin(self.ai_answer[-1]))[0])
            if self.module_action_pinyin.isChecked() and idiom_head_word_pinyin != ai_answer_tail_word_pinyin:
                QMessageBox.warning(
                    self, '输入错误', '首尾字拼音精确匹配失败!',  QMessageBox.StandardButton.Ok)
                return False

        return True

  #  '''电脑接龙'''
    def _ai_round(self):
        if self.auto_timer.isSignalConnected:
            self.auto_timer.stop()

        if self.operate_action_continue.isChecked():
            self._init_data(enum_Init_Type.ENUM_INIT_CONTINUE)

        idiom = self.user_input_edit.text().strip()
        # 无输入或未改变
        if not idiom or idiom == self.idiom:
            pass
        # 输入检查
        elif not self._check_userInputValid(idiom):
            self.user_input_edit.setText(idiom)
            pass
        else:
            idiom_dict_data = self.idiom_dict['idiom']
            self.idiom = idiom
            self._do_recordIdiom(
                enum_Idiom_Source.ENUM_IDIOM_SOURCE_USER, self.idiom, idiom_dict_data[idiom[0]][idiom])
            self.user_spell_edit.setText(self._get_spell(
                idiom_dict_data[idiom[0]], self.idiom))
            self.user_explain_edit.setText(
                '%s' % (self._get_answerText(idiom_dict_data[idiom[0]][idiom])))

            self.ai_answer, answer_idiom_dict = self._get_nextIdiom(
                self.idiom, enum_Idiom_Source.ENUM_IDIOM_SOURCE_AI)

            if None != self.ai_answer:
                self._do_recordIdiom(
                    enum_Idiom_Source.ENUM_IDIOM_SOURCE_AI, self.ai_answer, answer_idiom_dict[self.ai_answer])
                self.ai_input_edit.setText(self.ai_answer)
                self.ai_spell_edit.setText(
                    self._get_spell(answer_idiom_dict, self.ai_answer))
                self.ai_explain_edit.setText(
                    '%s' % (self._get_answerText(answer_idiom_dict[self.ai_answer])))

                tmp_answer, self.answer_idiom_dict_promote = self._get_nextIdiom(
                    self.ai_answer, enum_Idiom_Source.ENUM_IDIOM_SOURCE_AUTO)
                if self.operate_action_promote.isChecked():
                    self.idiom_promote_edit.clear()
                    if not self.answer_idiom_dict_promote:
                        self.idiom_promote_edit.append('No Promote')
                    else:
                        for ele in list(self.answer_idiom_dict_promote.keys()):
                            self.idiom_promote_edit.append(ele)

                if self.operate_action_auto.isChecked():
                    if not tmp_answer:
                        self.auto_timer.stop()
                        self.idiom_used_edit.append('-------结束-------')
                    else:
                        self.auto_timer.start(AUTO_TIMER_INTERVAL*1000)
                        self.auto_timer.timeout.connect(
                            lambda: self._do_auto(tmp_answer))

    def _do_auto(self, idiom):
        self.user_input_edit.setText(idiom)
        self.user_input_button.clicked.emit()

    def _get_nextIdiom(self, idiom, source_type=enum_Idiom_Source.ENUM_IDIOM_SOURCE_AI):
        idiom_dict_data = self.idiom_dict['idiom']
        pinyin = ''.join(list(pypinyin.pinyin(idiom))[-1])
        lzpinyin = pypinyin.lazy_pinyin(idiom[-1])[0]
        mulpinyin = pypinyin.pinyin(idiom[-1], heteronym=True)[0]

        if self.module_action_all.isChecked() and idiom[-1] in idiom_dict_data:
            idiom_data_list = list(idiom_dict_data[idiom[-1]])
            LOG_TRACE(idiom_data_list)
            # 同字同音列表
            answer_list = list(filter(lambda x: ''.join(
                list(pypinyin.pinyin(x))[0]) == pinyin, idiom_data_list))
        elif self.module_action_word.isChecked() and idiom[-1] in idiom_dict_data:
            answer_list = list(idiom_dict_data[idiom[-1]])
        elif self.module_action_lzpinyin.isChecked() and lzpinyin in list(self.idiom_dict['lzpinyin'].keys()):
            answer_list = self.idiom_dict['lzpinyin'][lzpinyin]
        elif self.module_action_pinyin.isChecked() and pinyin in list(self.idiom_dict['pinyin'].keys()):
            answer_list = self.idiom_dict['pinyin'][pinyin]
        elif self.module_action_multi.isChecked() and not set(mulpinyin).isdisjoint(self.idiom_dict['pinyin'].keys()):
            # 多音同音列表
            answer_list = []
            for xmul_py in mulpinyin:
                for py_tmp, word_list in self.idiom_dict['pinyin'].items():
                    if xmul_py == py_tmp:
                        answer_list += word_list
        else:
            self._congratulation(
                idiom, source_type)
            return None, {}

        LOG_TRACE(answer_list)

        # 电脑答案去重
        if 0 == len(answer_list) or set(answer_list) < set(self.idiom_used['used']):
            self._congratulation(
                idiom, enum_Idiom_Source.ENUM_IDIOM_SOURCE_AUTO)
            return None, {}

        idiom_answer = random.choice(
            list(filter(lambda x: x not in self.idiom_used['used'], answer_list)))
        answer_idiom_dict = idiom_dict_data[idiom_answer[0]]

        return idiom_answer, answer_idiom_dict

    def _get_answerText(self, answer):
        text_ret = ''
        for key in answer:
            if key != '成语' and key != '拼音':
                text_ret += key + '：' + answer[key]
                if key != list(answer.keys())[-1]:
                    text_ret += '\n'
        return text_ret

    def _do_recordIdiom(self, idiom_source, idiom, idiom_dict):
        if enum_Idiom_Source.ENUM_IDIOM_SOURCE_USER == idiom_source:
            if self.display_action_all.isChecked() or self.display_action_user.isChecked():
                # 修复模式发生变化之后记录显示的问题
                if idiom in self.idiom_used['user']:
                    return
                self.idiom_used_edit.append(HIS_DISPALY_USER + idiom)
            LOG_INFO(HIS_DISPALY_USER + idiom)
            self.idiom_used['user'].append(idiom)
            self.idiom_used['all'].append(['user', idiom])
            if TTS_OPT:
                self.pt.say(HIS_DISPALY_USER + idiom)
                self.pt.runAndWait()
        elif enum_Idiom_Source.ENUM_IDIOM_SOURCE_AI == idiom_source:
            if self.display_action_all.isChecked() or self.display_action_ai.isChecked():
                self.idiom_used_edit.append(HIS_DISPALY_AI + idiom)
            LOG_INFO(HIS_DISPALY_AI + idiom)
            self.idiom_used['ai'].append(idiom)
            self.idiom_used['all'].append(['ai', idiom])
            if TTS_OPT:
                self.pt.say(HIS_DISPALY_AI + idiom)
                self.pt.runAndWait()
        self.idiom_used['used'].append(idiom)

    def _get_spell(self, answer_idiom_dict, idiom):
        if USE_DICT_SPELL:
            spell = answer_idiom_dict[idiom]['拼音']
        else:
            spell = '%s' % ' '.join(
                numpy.hstack(pypinyin.pinyin(idiom)))

        return spell

    def _congratulation(self, idiom, source_type=enum_Idiom_Source.ENUM_IDIOM_SOURCE_AI):
        if not self.operate_action_auto.isChecked() and source_type != enum_Idiom_Source.ENUM_IDIOM_SOURCE_AUTO:
            self.idiom_used_edit.append('-------结束-------')
            QMessageBox.information(
                self, '你赢啦', '恭喜，你的成语：\'%s\' 击败了电脑，获得胜利!' % idiom, QMessageBox.StandardButton.Ok)


# '''run'''
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(progam_path + 'image/icon.png'))
    client = Chinese_string_up_puzzle()
    client.show()
    sys.exit(app.exec())
