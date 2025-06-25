from utils.font_helper import *
from typing import List, Tuple
from PyQt6.QtGui import QBrush
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QDialog,
)
from PyQt6.QtCore import Qt

import os
import sys

# Get the absolute path of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the deploy directory to sys.path
sys.path.extend([current_dir, os.path.dirname(current_dir)])


class MemberTableWidget(QTableWidget):
    def __init__(self, data_provider, parent=None):
        super().__init__(parent)
        self.data_provider = data_provider
        self.main_window = parent  # 保存对主窗口的引用
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["姓名", "年龄", "组别"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(
            QTableWidget.EditTrigger.DoubleClicked
            | QTableWidget.EditTrigger.EditKeyPressed
        )
        self.setFont(FontHelper.get_chinese_font(10))
        self.populate_table()

        # 连接单元格变化信号
        self.cellChanged.connect(self.on_cell_changed)

    def populate_table(self):
        self.blockSignals(True)  # 防止在填充数据时触发cellChanged信号
        self.clearContents()
        self.setRowCount(len(self.data_provider.members))

        for row, member in enumerate(self.data_provider.members):
            # 姓名列
            name_item = QTableWidgetItem(member.name)
            name_item.setForeground(QBrush(self.data_provider.get_name_color(member)))
            self.setItem(row, 0, name_item)

            # 年龄列
            age_item = QTableWidgetItem(str(member.age))
            age_item.setData(Qt.ItemDataRole.UserRole, member)  # 存储成员对象引用
            self.setItem(row, 1, age_item)

            # 组别列 - 使用下拉框
            group_combo = QComboBox()
            group_combo.addItems(self.data_provider.group_colors.keys())
            group_combo.setCurrentText(member.group)
            group_combo.currentTextChanged.connect(
                lambda text, r=row: self.on_group_changed(r, text)
            )
            self.setCellWidget(row, 2, group_combo)

            # 设置背景色
            self.set_row_color(row, member)

        self.blockSignals(False)

    def set_row_color(self, row, member):
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                item.setBackground(QBrush(self.data_provider.get_color(member)))

    def on_group_changed(self, row, new_group):
        member_item = self.item(row, 1)
        if not member_item:
            return

        member = member_item.data(Qt.ItemDataRole.UserRole)
        if not member:
            return

        member.group = new_group
        self.set_row_color(row, member)

        # 通知主窗口更新图表
        if hasattr(self.main_window, "update_ui"):
            self.main_window.update_ui()

    def on_cell_changed(self, row, column):
        print("row:{},column:{}".format(row, column))
        if column == 2:  # 组别列已经使用下拉框处理，跳过
            return

        item = self.item(row, column)
        print("item:{}".format(item))
        if not item:
            return

        member = item.data(Qt.ItemDataRole.UserRole)
        print("1.member:{}".format(member))
        if not member:
            return

        if column == 0:  # 姓名修改
            new_name = item.text()
            member.name = new_name
            print("2.member:{}".format(member))
            # 立即更新图表
            self.main_window.update_chart()
        elif column == 1:  # 年龄修改
            try:
                new_age = int(item.text())
                member.age = new_age
                # 更新名字颜色
                name_item = self.item(row, 0)
                name_item.setForeground(
                    QBrush(self.data_provider.get_name_color(member))
                )
                # 更新图表
                self.main_window.update_chart()
            except ValueError:
                item.setText(str(member.age))  # 恢复原值


class AddMemberDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加新成员")
        self.setFixedSize(300, 200)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 姓名输入
        name_layout = QHBoxLayout()
        name_label = QLabel("姓名:")
        name_label.setFont(FontHelper.get_chinese_font(10))
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # 年龄输入
        age_layout = QHBoxLayout()
        age_label = QLabel("年龄:")
        age_label.setFont(FontHelper.get_chinese_font(10))
        self.age_input = QLineEdit()
        age_layout.addWidget(age_label)
        age_layout.addWidget(self.age_input)
        layout.addLayout(age_layout)

        # 组别选择
        group_layout = QHBoxLayout()
        group_label = QLabel("组别:")
        group_label.setFont(FontHelper.get_chinese_font(10))
        self.group_combo = QComboBox()
        self.group_combo.addItems(["A组", "B组", "C组", "D组"])
        group_layout.addWidget(group_label)
        group_layout.addWidget(self.group_combo)
        layout.addLayout(group_layout)

        # 按钮
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("添加")
        self.add_btn.setFont(FontHelper.get_chinese_font(10))
        self.add_btn.clicked.connect(self.validate_input)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setFont(FontHelper.get_chinese_font(10))
        self.cancel_btn.clicked.connect(self.reject)  # 使用reject关闭对话框
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

    def validate_input(self):
        name = self.name_input.text().strip()
        age_text = self.age_input.text().strip()
        group = self.group_combo.currentText()

        if not name:
            QMessageBox.warning(self, "警告", "请输入姓名!")
            return

        try:
            age = int(age_text)
            if age <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "警告", "请输入有效的年龄(正整数)!")
            return

        self.accept()
