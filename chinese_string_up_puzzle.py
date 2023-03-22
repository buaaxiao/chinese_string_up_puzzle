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
import pyttsx3
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from chinese_string_engine import *
from chinese_string_const import *
from xcommon.xconfig import *
from xcommon.xlog import *


# '''成语接龙'''
class Chinese_string_up_puzzle(QMainWindow):
    # 暂未实现功能
    def _to_beContinue(self,  control_id, btn=None):
        LOG_TRACE(control_id, btn)
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

        if control_id in continue_dict.keys():
            config_value = self.cConfigHandle.get_value_int(
                'function', continue_dict[control_id], 0)
            LOG_TRACE('config_value:', config_value)
            if 1 != config_value:
                QMessageBox.information(
                    self, 'Very Important Person', 'VIP功能!', QMessageBox.StandardButton.Ok)
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
        self._init_config()
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(lambda: self._do_auto())

        # 初始化
        self._add_moduleMenuBar()
        self._add_displayMenuBar()
        self._add_operateMenuBar()
        self._init_widget()

        # 读取数据
        self._init_data()

    def _init_config(self):
        self.cConfigHandle = xConfigHandle(cfg_path)

    def _add_moduleMenuBar(self):
        menu = self.menuBar()

        self.module_action_all = QAction(
            QIcon(progam_path + './image/match_all.jpg'), '完全匹配', self)
        self.module_action_all.setStatusTip('完全匹配：支持首尾读音和字都匹配')
        self.module_action_all.setCheckable(True)
        self.module_action_all.setChecked(True)
        self.module_action = enum_Puzzle_Module.Model_All
        self.module_action_all.triggered.connect(
            lambda: self._on_ModuleMenuBarClick(self.module_action_all, enum_Puzzle_Module.Model_All))

        self.module_action_word = QAction(
            QIcon(progam_path + './image/match_word.jpg'), '字匹配', self)
        self.module_action_word.setStatusTip('字匹配：支持首尾字匹配')
        self.module_action_word.setCheckable(True)
        self.module_action_word.triggered.connect(
            lambda: self._on_ModuleMenuBarClick(self.module_action_word, enum_Puzzle_Module.Model_Word))

        self.module_action_lzpinyin = QAction(
            QIcon(progam_path + './image/match_lzpinyin.jpg'), '读音模糊匹配', self)
        self.module_action_lzpinyin.setStatusTip('读音模糊匹配：支持首尾读音模糊匹配')
        self.module_action_lzpinyin.setCheckable(True)
        self.module_action_lzpinyin.triggered.connect(
            lambda: self._on_ModuleMenuBarClick(self.module_action_lzpinyin, enum_Puzzle_Module.Model_LzPinyin))

        self.module_action_pinyin = QAction(
            QIcon(progam_path + './image/match_pinyin.jpg'), '读音匹配', self)
        self.module_action_pinyin.setStatusTip('读音匹配：支持首尾读音完全匹配')
        self.module_action_pinyin.setCheckable(True)
        self.module_action_pinyin.triggered.connect(
            lambda: self._on_ModuleMenuBarClick(self.module_action_pinyin, enum_Puzzle_Module.Model_Pinyin))

        self.module_action_multi = QAction(
            QIcon(progam_path + './image/match_multi.jpg'), '多音字匹配', self)
        self.module_action_multi.setStatusTip('多音字模式：支持首尾多音字匹配')
        self.module_action_multi.setCheckable(True)
        self.module_action_multi.triggered.connect(
            lambda: self._on_ModuleMenuBarClick(self.module_action_multi, enum_Puzzle_Module.Model_Multi))

        self.module_action_BattleSingle = QAction(
            QIcon(progam_path + './image/match_battle_single.jpg'), '单回合', self)
        self.module_action_BattleSingle.setStatusTip('单回合模式：一问一答')
        self.module_action_BattleSingle.setCheckable(True)
        self.module_action_BattleSingle.triggered.connect(
            lambda: self._on_ModuleMenuBarClick(self.module_action_BattleSingle, enum_Puzzle_Module.Model_BattleSingle))

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
            btn.setChecked(True)
            return

        self.Chinese_string_engine.set_model(type)

        if not enum_Puzzle_Module.Model_All.value & type.value:
            self.module_action_all.setChecked(False)
        if not enum_Puzzle_Module.Model_Word.value & type.value:
            self.module_action_word.setChecked(False)
        if not enum_Puzzle_Module.Model_LzPinyin.value & type.value:
            self.module_action_lzpinyin.setChecked(False)
        if not enum_Puzzle_Module.Model_Pinyin.value & type.value:
            self.module_action_pinyin.setChecked(False)
        if not enum_Puzzle_Module.Model_Multi.value & type.value:
            self.module_action_multi.setChecked(False)
        if not enum_Puzzle_Module.Model_BattleSingle.value & type.value:
            self.module_action_BattleSingle.setChecked(False)

    def _add_displayMenuBar(self):
        menu = self.menuBar()

        self.display_action_all = QAction(
            QIcon(progam_path + './image/show_all.jpg'), '全部', self)
        self.display_action_all.setStatusTip('展示全部历史记录')
        self.display_action_all.setCheckable(True)
        # 默认显示全部历史
        self.display_action_all.setChecked(True)
        self.display_action_all.triggered.connect(
            lambda: self._on_DisplayMenuBarClick(self.display_action_all, enumBarButton_Display.Menu_ControlId_All))

        self.display_action_user = QAction(
            QIcon(progam_path + './image/show_user.jpg'), '我方', self)
        self.display_action_user.setStatusTip('展示我方历史记录')
        self.display_action_user.setCheckable(True)
        self.display_action_user.triggered.connect(
            lambda: self._on_DisplayMenuBarClick(self.display_action_user, enumBarButton_Display.Menu_ControlId_USER))

        self.display_action_ai = QAction(
            QIcon(progam_path + './image/show_ai.jpg'), '电脑', self)
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
            btn.setChecked(True)
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
            QIcon(progam_path + './image/work_auto.jpg'), '自动接龙', self)
        self.operate_action_auto.setStatusTip('自动接龙：人工发起，电脑自动接龙并显示结果')
        self.operate_action_auto.setCheckable(True)
        self.operate_action_auto.triggered.connect(
            lambda: self._on_OperateMenuBarClick(self.operate_action_auto, enumBarButton_Operate.Menu_ControlId_Work_Auto))

        self.operate_action_promote = QAction(
            QIcon(progam_path + './image/work_promote.jpg'), '显示提示', self)
        self.operate_action_promote.setStatusTip('显示提示框')
        self.operate_action_promote.setCheckable(True)
        self.operate_action_promote.triggered.connect(
            lambda: self._on_OperateMenuBarClick(self.operate_action_promote, enumBarButton_Operate.Menu_ControlId_Work_Promote))

        file_menu = menu.addMenu('操作(&c)')
        file_menu.addAction(self.operate_action_auto)
        file_menu.addAction(self.operate_action_promote)

    def _on_OperateMenuBarClick(self, btn, type):
        if self._to_beContinue(type, btn):
            return

        if enumBarButton_Operate.Menu_ControlId_Work_Auto.value & type.value:
            LOG_TRACE("set auto model")

        if enumBarButton_Operate.Menu_ControlId_Work_Promote.value & type.value:
            self.idiom_promote_edit.clear()
            if btn.isChecked():
                if not self.answer_idiom_dict_promote:
                    self.idiom_promote_edit.append('No Promote')
                else:
                    for ele in self.answer_idiom_dict_promote:
                        self.idiom_promote_edit.append(ele)

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
            lambda: self._restart())

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

    def _restart(self):
        puzzle_model = self.Chinese_string_engine.get_model()
        self._init_data()
        self.Chinese_string_engine.set_model(puzzle_model)

    # '''数据加载'''
    def _init_data(self):
        LOG_INFO('数据加载')
        if not self.module_action_BattleSingle.isChecked():
            self.user_input_edit.clear()
            self.user_spell_edit.clear()
            self.user_explain_edit.clear()

            self.ai_input_edit.clear()
            self.ai_spell_edit.clear()
            self.ai_explain_edit.clear()

            self.idiom_used_edit.clear()
            self.idiom_promote_edit.clear()

        self.data_filepath = progam_path + './data/data.json'
        self.Chinese_string_engine = Chinese_string_engine(
            self.data_filepath, default_module=enum_Puzzle_Module.Model_All)

        self.idiom = None
        self.ai_answer = None
        self.idiom_used = {}
        self.idiom_used['all'] = []
        self.idiom_used['user'] = []
        self.idiom_used['ai'] = []
        self.idiom_used['used'] = []
        self.answer_idiom_dict_promote = {}

    def _ai_round(self):
        if '停止' == self.user_input_button.text():
            self.user_input_button.setText("确定")
            self.auto_timer.stop()

        if self.module_action_BattleSingle.isChecked():
            self._init_data()

        # 无输入或者输入未改变
        idiom = self.user_input_edit.text().strip()
        if not idiom or self.idiom == idiom:
            return

        # 输入检查
        if not self._check_userInputValid(idiom):
            return

        self.idiom = idiom
        self._set_output(self.idiom, enum_Idiom_Output.ENUM_IDIOM_OUTPUT_USER)

        self.ai_answer, self.idiom_promote, self.answer_idiom_dict_promote = self.Chinese_string_engine.get_nextIdom(
            self.idiom, self.idiom_used['used'])
        LOG_TRACE(self.ai_answer)
        if None == self.ai_answer:
            self._congratulation(self.idiom)
        else:
            self._set_output(
                self.ai_answer, enum_Idiom_Output.ENUM_IDIOM_OUTPUT_AI, self.answer_idiom_dict_promote)

        if self.operate_action_auto.isChecked():
            if None == self.idiom_promote:
                self.auto_timer.stop()
                self.user_input_button.setText("确定")
                self.idiom_used_edit.append('-------结束-------')
                LOG_INFO('-------结束-------')
            else:
                self.auto_timer.start(AUTO_TIMER_INTERVAL*1000)
                self.user_input_button.setText("停止")

    def _do_auto(self):
        self.user_input_edit.setText(self.idiom_promote)
        self.user_input_button.clicked.emit()

    def _set_output(self, idiom, type, answer_idiom_dict_promote=[]):
        spell = self.Chinese_string_engine._get_spell(idiom)
        text = self.Chinese_string_engine._get_answerText(
            idiom, ANSWER_EXCEPT_DICT)
        if enum_Idiom_Output.ENUM_IDIOM_OUTPUT_USER == type:
            if self.display_action_all.isChecked() or self.display_action_user.isChecked():
                self.idiom_used_edit.append(HIS_DISPALY_USER + idiom)
            self.user_spell_edit.setText(spell)
            self.user_explain_edit.setText(text)
            self.idiom_used['user'].append(idiom)
            self.idiom_used['used'].append(idiom)
            self.idiom_used['all'].append(['user', idiom])
            LOG_INFO(HIS_DISPALY_USER + idiom)
        elif enum_Idiom_Output.ENUM_IDIOM_OUTPUT_AI == type:
            if self.display_action_all.isChecked() or self.display_action_ai.isChecked():
                self.idiom_used_edit.append(HIS_DISPALY_AI + idiom)
            self.ai_input_edit.setText(idiom)
            self.ai_spell_edit.setText(spell)
            self.ai_explain_edit.setText(text)
            self.idiom_used['ai'].append(idiom)
            self.idiom_used['used'].append(idiom)
            self.idiom_used['all'].append(['ai', idiom])
            LOG_INFO(HIS_DISPALY_AI + idiom)
            if 0 == len(answer_idiom_dict_promote):
                self.idiom_promote_edit.setText("No Promote")
            elif self.operate_action_promote.isChecked():
                self.idiom_promote_edit.clear()
                for idPromote in answer_idiom_dict_promote:
                    self.idiom_promote_edit.append(idPromote)

    #  '''检测我方输入成语是否合法'''
    def _check_userInputValid(self, idiom):
        # 成语已使用
        if idiom in self.idiom_used['used']:
            QMessageBox.warning(
                self, '成语已使用', '你输入的成语已在本次接龙中使用, 请重新输入!', QMessageBox.StandardButton.Ok)
            return False

        if not self.Chinese_string_engine.idiom_exists(idiom):
            QMessageBox.warning(
                self, '输入错误', '系统成语库中无该记录!', QMessageBox.StandardButton.Ok)
            return False

        if None != self.ai_answer:
            retCheck = self.Chinese_string_engine.check_idiom(
                idiom, self.ai_answer)
            if enum_Puzzle_Unmatch.Unmatch_All == retCheck:
                QMessageBox.warning(
                    self, '输入错误', '首尾字及拼音匹配失败!', QMessageBox.StandardButton.Ok)
                return False

            if enum_Puzzle_Unmatch.Unmatch_Word == retCheck:
                QMessageBox.warning(
                    self, '输入错误', '首尾字匹配失败!', QMessageBox.StandardButton.Ok)
                return False

            if enum_Puzzle_Unmatch.Unmatch_LzPinyin == retCheck:
                QMessageBox.warning(
                    self, '输入错误', '首尾字拼音模糊匹配失败!',   QMessageBox.StandardButton.Ok)
                return False

            if enum_Puzzle_Unmatch.Unmatch_Pinyin == retCheck:
                QMessageBox.warning(
                    self, '输入错误', '首尾字拼音精确匹配失败!',  QMessageBox.StandardButton.Ok)
                return False

            if enum_Puzzle_Unmatch.Unmatch_Multi == retCheck:
                QMessageBox.warning(
                    self, '输入错误', '首尾多音字匹配失败!',  QMessageBox.StandardButton.Ok)
                return False

        return True

    def _congratulation(self, idiom, source_type=enum_Idiom_Source.ENUM_IDIOM_SOURCE_AI):
        if not self.operate_action_auto.isChecked() and source_type != enum_Idiom_Source.ENUM_IDIOM_SOURCE_AUTO:
            self.idiom_used_edit.append('-------结束-------')
            QMessageBox.information(
                self, '你赢啦', '恭喜，你的成语：\'%s\' 击败了电脑，获得胜利!' % idiom, QMessageBox.StandardButton.Ok)


# '''run'''
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(progam_path + './image/icon.png'))
    client = Chinese_string_up_puzzle()
    client.show()
    sys.exit(app.exec())
