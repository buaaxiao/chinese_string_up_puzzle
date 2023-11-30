#!/usr/bin/env python3
# -*- coding : utf-8-*-
# coding:unicode_escape

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from xcommon.xlog import *
from xcommon.xconfig import *
from chinese_string_enum import *
from chinese_string_engine import *

FINISH_TAIL = '-------结束-------'
PROMOTE_TAIL = '-------无提示-------'


# '''成语接龙'''
class Chinese_string_up_puzzle(QMainWindow):
    def _vip_control(self,  control_id, btn=None):
        LOG_TRACE(control_id, btn)
        continue_dict = {
            enum_Puzzle_Module.Module_Word: 'word',
            enum_Puzzle_Module.Module_LzPinyin: 'lzpinyin',
            enum_Puzzle_Module.Module_Pinyin: 'pinyin',
            enum_Puzzle_Module.Module_Multi: 'multi',
            enumBarButton_Operate.Menu_ControlId_Work_BattleSingle: 'battlesingle',
            enumBarButton_Operate.Menu_ControlId_Work_Promote: 'promote',
            enumBarButton_Operate.Menu_ControlId_Work_Auto: 'auto',
        }

        if control_id in continue_dict.keys():
            config_value = self.cConfigHandle.get_value_int(
                'function', continue_dict[control_id], 0)
            LOG_TRACE('config_value:', config_value)
            if 1 != config_value:
                QMessageBox.information(
                    self, 'Very Important Person', 'VIP功能', QMessageBox.StandardButton.Ok)
                if btn:
                    btn.setChecked(False)
                return True

        return False

    # 初始化
    def __init__(self, parent=None, **kwargs):
        LOG_INFO('---------------------------开始接龙---------------------------')
        super(Chinese_string_up_puzzle, self).__init__(parent)

        self.data_filepath = progam_path + './data/stringup.db'
        self.Chinese_string_engine = Chinese_string_engine(
            self.data_filepath, default_module=enum_Puzzle_Module.Module_All)
        
        # 模态注册
        self._init_model()
        # 读取配置文件
        self._init_config()
        # 添加模块菜单
        self._add_moduleMenuBar()
        # 添加显示菜单
        self._add_displayMenuBar()
        # 添加操作菜单
        self._add_operateMenuBar()
        # 初始化界面
        self._init_widget()
        # 初始化计时器
        self._init_timer()
        # 读取数据
        self._init_data()

    def _init_model(self):
        self.Module_set = []

    def _register_model(self, btn):
        self.Module_set.append(btn)

    def _do_model(self, bModel=False):
        for btn in self.Module_set:
            btn.setDisabled(bModel)

    def _init_config(self):
        self.cConfigHandle = xConfigHandle(cfg_path)
        self.display_user = '【' + self.cConfigHandle.get_value_str(
            'common', 'his_dispaly_user', '我方') + '】'
        self.display_ai = '【' + self.cConfigHandle.get_value_str(
            'common', 'his_dispaly_ai', '电脑') + '】'

    def _add_moduleMenuBar(self):
        menu = self.menuBar()

        self.module_action_all = QAction(
            QIcon(progam_path + './image/match_all.jpg'), '完全匹配', self)
        self.module_action_all.setStatusTip('完全匹配：支持首尾读音和字都匹配')
        self.module_action_all.setCheckable(True)
        self.module_action_all.setChecked(True)
        self.module_action = enum_Puzzle_Module.Module_All
        self.module_action_all.triggered.connect(
            lambda: self._on_ModuleMenuBarClick(self.module_action_all, enum_Puzzle_Module.Module_All))

        self.module_action_word = QAction(
            QIcon(progam_path + './image/match_word.jpg'), '字匹配', self)
        self.module_action_word.setStatusTip('字匹配：支持首尾字匹配')
        self.module_action_word.setCheckable(True)
        self.module_action_word.triggered.connect(
            lambda: self._on_ModuleMenuBarClick(self.module_action_word, enum_Puzzle_Module.Module_Word))

        self.module_action_lzpinyin = QAction(
            QIcon(progam_path + './image/match_lzpinyin.jpg'), '读音模糊匹配', self)
        self.module_action_lzpinyin.setStatusTip('读音模糊匹配：支持首尾读音模糊匹配')
        self.module_action_lzpinyin.setCheckable(True)
        self.module_action_lzpinyin.triggered.connect(
            lambda: self._on_ModuleMenuBarClick(self.module_action_lzpinyin, enum_Puzzle_Module.Module_LzPinyin))

        self.module_action_pinyin = QAction(
            QIcon(progam_path + './image/match_pinyin.jpg'), '读音匹配', self)
        self.module_action_pinyin.setStatusTip('读音匹配：支持首尾读音完全匹配')
        self.module_action_pinyin.setCheckable(True)
        self.module_action_pinyin.triggered.connect(
            lambda: self._on_ModuleMenuBarClick(self.module_action_pinyin, enum_Puzzle_Module.Module_Pinyin))

        self.module_action_multi = QAction(
            QIcon(progam_path + './image/match_multi.jpg'), '多音字匹配', self)
        self.module_action_multi.setStatusTip('多音字模式：支持首尾多音字匹配')
        self.module_action_multi.setCheckable(True)
        self.module_action_multi.triggered.connect(
            lambda: self._on_ModuleMenuBarClick(self.module_action_multi, enum_Puzzle_Module.Module_Multi))

        file_menu = menu.addMenu('模式选择(&m)')
        file_menu.addAction(self.module_action_all)
        self._register_model(self.module_action_all)
        file_menu.addAction(self.module_action_word)
        self._register_model(self.module_action_word)
        file_menu.addAction(self.module_action_lzpinyin)
        self._register_model(self.module_action_lzpinyin)
        file_menu.addAction(self.module_action_pinyin)
        self._register_model(self.module_action_pinyin)
        file_menu.addAction(self.module_action_multi)
        self._register_model(self.module_action_multi)

    def _on_ModuleMenuBarClick(self, btn, type):
        if self._vip_control(type, btn):
            return

        if not btn.isChecked():
            btn.setChecked(True)
            return

        self.Chinese_string_engine.set_model(type)

        if not enum_Puzzle_Module.Module_All.value & type.value:
            self.module_action_all.setChecked(False)
        if not enum_Puzzle_Module.Module_Word.value & type.value:
            self.module_action_word.setChecked(False)
        if not enum_Puzzle_Module.Module_LzPinyin.value & type.value:
            self.module_action_lzpinyin.setChecked(False)
        if not enum_Puzzle_Module.Module_Pinyin.value & type.value:
            self.module_action_pinyin.setChecked(False)
        if not enum_Puzzle_Module.Module_Multi.value & type.value:
            self.module_action_multi.setChecked(False)

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
        if self._vip_control(type, btn):
            return

        if not btn.isChecked():
            btn.setChecked(True)
            return

        LOG_TRACE(type)
        self.idiom_used_list.clear()
        if not enumBarButton_Display.Menu_ControlId_All.value & type.value:
            self.display_action_all.setChecked(False)
        else:
            for item in self.idiom_used['all']:
                if 'user' == item[0]:
                    self._insertOutput(self.display_user + item[1])
                elif 'ai' == item[0]:
                    self._insertOutput(self.display_ai + item[1])

        if not enumBarButton_Display.Menu_ControlId_USER.value & type.value:
            self.display_action_user.setChecked(False)
        else:
            for item in self.idiom_used['user']:
                self._insertOutput(self.display_user + item)

        if not enumBarButton_Display.Menu_ControlId_AI.value & type.value:
            self.display_action_ai.setChecked(False)
        else:
            for item in self.idiom_used['ai']:
                self._insertOutput(self.display_ai + item)

    def _add_operateMenuBar(self):
        menu = self.menuBar()

        self.operate_action_auto = QAction(
            QIcon(progam_path + './image/work_auto.jpg'), '自动接龙', self)
        self.operate_action_auto.setStatusTip('自动接龙：人工发起，电脑自动接龙并显示结果')
        self.operate_action_auto.setCheckable(True)
        self.operate_action_auto.triggered.connect(
            lambda: self._on_OperateMenuBarClick(self.operate_action_auto, enumBarButton_Operate.Menu_ControlId_Work_Auto))

        self.operate_action_promote = QAction(
            QIcon(progam_path + './image/work_promote.jpg'), '提示', self)
        self.operate_action_promote.setStatusTip('显示提示框')
        self.operate_action_promote.setCheckable(True)
        self.operate_action_promote.triggered.connect(
            lambda: self._on_OperateMenuBarClick(self.operate_action_promote, enumBarButton_Operate.Menu_ControlId_Work_Promote))

        self.operate_action_battlesingle = QAction(
            QIcon(progam_path + './image/work_battlesingle.jpg'), '单回合', self)
        self.operate_action_battlesingle.setStatusTip('单回合模式：一问一答')
        self.operate_action_battlesingle.setCheckable(True)
        self.operate_action_battlesingle.triggered.connect(
            lambda: self._on_OperateMenuBarClick(self.operate_action_battlesingle, enumBarButton_Operate.Menu_ControlId_Work_BattleSingle))

        file_menu = menu.addMenu('操作(&c)')
        file_menu.addAction(self.operate_action_auto)
        self._register_model(self.operate_action_auto)
        file_menu.addAction(self.operate_action_battlesingle)
        self._register_model(self.operate_action_battlesingle)
        file_menu.addAction(self.operate_action_promote)

    def _on_OperateMenuBarClick(self, btn, type):
        if self._vip_control(type, btn):
            return
        
        if enumBarButton_Operate.Menu_ControlId_Work_Auto.value & type.value:
            LOG_TRACE("set auto model")
            self.operate_action_battlesingle.setChecked(False)

        if enumBarButton_Operate.Menu_ControlId_Work_BattleSingle.value & type.value:
            LOG_TRACE("set auto model")
            self.operate_action_auto.setChecked(False)

        if enumBarButton_Operate.Menu_ControlId_Work_Promote.value & type.value:
            if btn.isChecked():
                self.idiom_promote_list.show()
                self.widget.setLayout(self.grid)
            else:
                self.idiom_promote_list.hide()
                self.widget.setLayout(self.grid)

            self.idiom_promote_list.clear()
            if btn.isChecked():
                if not self.answer_idiom_dict_promote:
                    self.idiom_promote_list.addItem(PROMOTE_TAIL)
                else:
                    for ele in self.answer_idiom_dict_promote:
                        self.idiom_promote_list.addItem(ele['idiom'])

    def _init_widget(self):
        self.setWindowTitle(self.cConfigHandle.get_value_str(
            'common', 'progam_title', '成语接龙'))

        if 1 == self.cConfigHandle.get_value_int('common', 'progam_size_fix', 0):
            self.setFixedSize(985, 609)
        else:
            self.setSizePolicy(QSizePolicy.Policy.Expanding,
                               QSizePolicy.Policy.Expanding)
            self.resize(1000, 618)
        self.user_input_label = QLabel('我方')
        self.user_input_edit = QLineEdit()
        self.user_input_edit.setPlaceholderText('我方输入')
        self._register_model(self.user_input_edit)
        self.user_input_button = QPushButton('确定')
        self.user_promote_button = QPushButton('补全')
        self._register_model(self.user_promote_button)

        self.restart_button = QPushButton('重新开始')
        self._register_model(self.restart_button)

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

        self.idiom_used_list = QListWidget()
        self.idiom_used_list.setFixedWidth(211)
        self._register_model(self.idiom_used_list)

        self.idiom_promote_list = QListWidget()
        self.idiom_promote_list.setFixedWidth(211)
        self._register_model(self.idiom_promote_list)

        # 按键绑定
        self.user_input_edit.returnPressed.connect(
            self.user_input_button.click)
        self.user_input_button.clicked.connect(self._ai_round)
        self.user_promote_button.clicked.connect(self._user_complete)
        self.restart_button.clicked.connect(
            lambda: self._restart())
        self.idiom_used_list.itemSelectionChanged.connect(
            lambda: self._selection_change(self.idiom_used_list))
        self.idiom_promote_list.itemSelectionChanged.connect(
            lambda: self._selection_change(self.idiom_promote_list))

        # 布局
        self.grid = QGridLayout()
        self.grid.setSpacing(12)
        self.grid.addWidget(self.user_input_label, 0, 0, 1, 1)
        self.grid.addWidget(self.user_input_edit, 0, 1, 1, 1)
        self.grid.addWidget(self.user_input_button, 0, 2, 1, 1)
        self.grid.addWidget(self.user_promote_button, 0, 3, 1, 1)
        self.grid.addWidget(self.user_spell_label, 1, 0, 1, 1)
        self.grid.addWidget(self.user_spell_edit, 1, 1, 1, 3)
        self.grid.addWidget(self.user_explain_label, 2, 0, 1, 1)
        self.grid.addWidget(self.user_explain_edit, 2, 1, 1, 3)
        self.grid.addWidget(self.ai_input_label, 3, 0, 1, 1)
        self.grid.addWidget(self.ai_input_edit, 3, 1, 1, 2)
        self.grid.addWidget(self.restart_button, 3, 3, 1, 1)
        self.grid.addWidget(self.ai_spell_label, 4, 0, 1, 1)
        self.grid.addWidget(self.ai_spell_edit, 4, 1, 1, 3)
        self.grid.addWidget(self.ai_explain_label, 5, 0, 1, 1)
        self.grid.addWidget(self.ai_explain_edit, 5, 1, 1, 3)
        self.grid.addWidget(self.idiom_used_list, 0, 4, 6, 1)
        self.grid.addWidget(self.idiom_promote_list, 0, 5, 6, 1)
        if not self.operate_action_promote.isChecked():
            self.idiom_promote_list.hide()

        self.widget = QWidget()
        self.widget.setLayout(self.grid)
        self.setCentralWidget(self.widget)

    def _restart(self):
        puzzle_module = self.Chinese_string_engine.get_model()
        self._init_data()
        self.Chinese_string_engine.set_model(puzzle_module)

    # '''数据加载'''
    def _init_data(self):
        LOG_INFO('数据加载')
        self.user_input_edit.clear()
        self.user_spell_edit.clear()
        self.user_explain_edit.clear()

        self.ai_input_edit.clear()
        self.ai_spell_edit.clear()
        self.ai_explain_edit.clear()

        self.idiom_used_list.clear()
        self.idiom_promote_list.clear()

        self.idiom = None
        self.ai_answer = None
        self.idiom_used = {}
        self.idiom_used['all'] = []
        self.idiom_used['user'] = []
        self.idiom_used['ai'] = []
        self.idiom_used['used'] = []
        self.answer_idiom_dict_promote = []

    def _init_timer(self):
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(lambda: self._do_auto())

    def _ai_round(self):
        if '停止' == self.user_input_button.text():
            self.user_input_button.setText("确定")
            self._do_model(False)
            self.auto_timer.stop()

        # 无输入或者输入未改变
        idiom = self.user_input_edit.text().strip()
        if not idiom or self.idiom == idiom:
            return

        # 输入检查
        flag, results = self._check_userInputValid(idiom)
        if False == flag or 0 == len(results):
            return

        self.idiom = idiom
        self._set_output(results[0], enum_Idiom_Output.ENUM_IDIOM_OUTPUT_USER)

        self.ai_results, self.answer_idiom_dict_promote = self.Chinese_string_engine.get_nextIdiom(
            self.idiom, self.idiom_used['used'])
        LOG_TRACE(self.ai_results)
        LOG_TRACE("self.answer_idiom_dict_promote")
        LOG_INFO(self.answer_idiom_dict_promote)
        if 0 == len(self.ai_results):
            self._congratulation(self.idiom)
        else:
            self._set_output(
                self.ai_results[0], enum_Idiom_Output.ENUM_IDIOM_OUTPUT_AI, self.answer_idiom_dict_promote)

        if self.operate_action_auto.isChecked():
            if 0 == len(self.answer_idiom_dict_promote):
                self._do_model(False)
                self.auto_timer.stop()
                self.user_input_button.setText("确定")
                self._insertOutput(FINISH_TAIL)
                LOG_INFO(FINISH_TAIL)
            else:
                self.auto_timer.start(self.cConfigHandle.get_value_int(
                    'common', 'auto_timer_interval', 1)*1000)
                self._do_model(True)
                self.user_input_button.setText("停止")

    def _user_complete(self):
        if not self.user_input_edit.text().strip():
            return
        results = self.Chinese_string_engine.get_nextIdomByKey(self.user_input_edit.text().strip(), self.idiom_used['used'])
        if 0 != len(results):
            self.user_input_edit.setText(results[0]['idiom'])
            self.user_input_button.clicked.emit()

    def _do_auto(self):
        if 0 != len(self.answer_idiom_dict_promote):
            self.user_input_edit.setText(self.answer_idiom_dict_promote[0]['idiom'])
            self.user_input_button.clicked.emit()

    def _set_output(self, result, type, answer_idiom_dict_promote=[]):
        LOG_TRACE(result)
        idiom = self.Chinese_string_engine.get_idiom(result)
        spell = self.Chinese_string_engine.get_spell(result)
        text = self.Chinese_string_engine.get_answerText(result)
        if enum_Idiom_Output.ENUM_IDIOM_OUTPUT_USER == type:
            if self.display_action_all.isChecked() or self.display_action_user.isChecked():
                self._insertOutput(self.display_user + idiom)
            self.user_spell_edit.setText(spell)
            self.user_explain_edit.setText(text)
            self.idiom_used['user'].append(idiom)
            self.idiom_used['used'].append(idiom)
            self.idiom_used['all'].append(['user', idiom])
            LOG_INFO(self.display_user + idiom)
        elif enum_Idiom_Output.ENUM_IDIOM_OUTPUT_AI == type:
            if self.display_action_all.isChecked() or self.display_action_ai.isChecked():
                self._insertOutput(self.display_ai + idiom)
            self.ai_input_edit.setText(idiom)
            self.ai_spell_edit.setText(spell)
            self.ai_explain_edit.setText(text)
            self.idiom_used['ai'].append(idiom)
            self.idiom_used['used'].append(idiom)
            self.idiom_used['all'].append(['ai', idiom])
            LOG_INFO(self.display_ai + idiom)
            self.idiom_promote_list.clear()
            if 0 == len(answer_idiom_dict_promote):
                self.idiom_promote_list.addItem(PROMOTE_TAIL)
            elif self.operate_action_promote.isChecked():
                for idPromote in answer_idiom_dict_promote:
                    self.idiom_promote_list.addItem(idPromote['idiom'])

    #  '''检测我方输入成语是否合法'''
    def _check_userInputValid(self, idiom):
        results = []
        # 成语已使用
        if idiom in self.idiom_used['used'] and not self.operate_action_battlesingle.isChecked() :
            QMessageBox.warning(
                self, '成语已使用', '你输入的成语已在本次接龙中使用, 请重新输入!', QMessageBox.StandardButton.Ok)
            return False, results

        results = self.Chinese_string_engine.get_idiom_instance(idiom)
        if 0 == len(results):
            QMessageBox.warning(
                self, '输入错误', '系统成语库中无该记录!', QMessageBox.StandardButton.Ok)
            return False, results

        if None != self.ai_answer:
            retCheck, chkmsg = self.Chinese_string_engine.check_idiom(
                idiom, self.ai_answer)
            if 0 != retCheck:
                QMessageBox.warning(
                    self, '输入错误', chkmsg, QMessageBox.StandardButton.Ok)
                return False, results

        return True, results

    def _congratulation(self, idiom, source_type=enum_Idiom_Source.ENUM_IDIOM_SOURCE_AI):
        if not self.operate_action_auto.isChecked() and source_type != enum_Idiom_Source.ENUM_IDIOM_SOURCE_AUTO:
            self._insertOutput(FINISH_TAIL)
            QMessageBox.information(
                self, '你赢啦', '恭喜，你的成语：\'%s\' 击败了电脑，获得胜利!' % idiom, QMessageBox.StandardButton.Ok)

    def _selection_change(self, textEdit):
        itemText = textEdit.currentItem().text()
        idiom_type = enum_Idiom_Type.ENUM_IDIOM_TYPE_PROMOTE
        if FINISH_TAIL == itemText or PROMOTE_TAIL == itemText:
            return
        elif itemText.startswith(self.display_user):
            idiom_type = enum_Idiom_Type.ENUM_IDIOM_TYPE_USER
            idiom = itemText[len(self.display_user):]
        elif itemText.startswith(self.display_ai):
            idiom = itemText[len(self.display_ai):]
            idiom_type = enum_Idiom_Type.ENUM_IDIOM_TYPE_AI
        else:
            idiom = itemText

        instance = self.Chinese_string_engine.get_idiom_instance(idiom)
        if 0 != len(instance):
            text = self.Chinese_string_engine.get_answerText(instance[0])
            spell = self.Chinese_string_engine.get_spell(instance[0])
            self.user_input_edit.setText(idiom)
            self.user_spell_edit.setText(spell)
            self.user_explain_edit.setText(text)

    def _insertOutput(self, output):
        self.idiom_used_list.addItem(output)
        if 0:
            self.idiom_used_list.scrollToBottom()


# '''run'''˝
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(progam_path + './image/icon.png'))
    client = Chinese_string_up_puzzle()
    client.show()
    sys.exit(app.exec())
