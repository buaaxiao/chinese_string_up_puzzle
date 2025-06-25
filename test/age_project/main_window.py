from utils.font_helper import *
from utils.data_manager import *
from widgets.member_table import *
from widgets.chart_view import *
from dataclasses import dataclass
from PyQt6.QtGui import (
    QColor,
    QFont,
)
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
    QComboBox,
    QPushButton,
    QButtonGroup,
    QRadioButton,
    QGroupBox,
    QDialog,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 定义组别及颜色
        self.group_colors = {
            "A组": QColor(52, 152, 219),
            "B组": QColor(155, 89, 182),
            "C组": QColor(26, 188, 156),
            "D组": QColor(186, 25, 23),
        }

        members = [
            CommunityMember("Xiao K", 20, "A组"),
            CommunityMember("Peter", 25, "B组"),
            CommunityMember("X", 30, "C组"),
            CommunityMember("test user5", 40, "D组"),
            CommunityMember("test user3", 50, "A组"),
            CommunityMember("Xiao Wang", 60, "B组"),
            CommunityMember("test user2", 68, "C组"),
            CommunityMember("test user1", 90, "D组"),
        ]
        self.community_data = CommunityData(members, self.group_colors)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # 左侧控制面板
        left_panel = QVBoxLayout()
        left_panel.setContentsMargins(5, 5, 5, 5)

        # 姓名查询
        search_layout = QVBoxLayout()
        search_label = QLabel("姓名查询：")
        search_label.setFont(FontHelper.get_chinese_font(10, QFont.Weight.Bold))
        self.search_combo = QComboBox()
        self.search_combo.setEditable(True)
        self.search_combo.addItems([""] + self.community_data.names)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_combo)

        # 排序选项
        sort_group = QGroupBox("排序选项：")
        sort_group.setFont(FontHelper.get_chinese_font(10, QFont.Weight.Bold))
        sort_layout = QVBoxLayout()

        self.sort_btn_group = QButtonGroup()
        self.random_btn = QRadioButton("随机")
        self.quick_btn = QRadioButton("快速排序(年龄升序)")
        self.merge_btn = QRadioButton("归并排序(年龄降序)")
        self.heap_btn = QRadioButton("堆排序(年龄升序)")
        self.group_btn = QRadioButton("组别排序")

        self.sort_btn_group.addButton(self.random_btn, 0)
        self.sort_btn_group.addButton(self.quick_btn, 1)
        self.sort_btn_group.addButton(self.merge_btn, 2)
        self.sort_btn_group.addButton(self.heap_btn, 3)
        self.sort_btn_group.addButton(self.group_btn, 4)

        sort_layout.addWidget(self.random_btn)
        sort_layout.addWidget(self.quick_btn)
        sort_layout.addWidget(self.merge_btn)
        sort_layout.addWidget(self.heap_btn)
        sort_layout.addWidget(self.group_btn)
        sort_group.setLayout(sort_layout)

        # 操作按钮
        button_layout = QHBoxLayout()
        self.reset_btn = QPushButton("重置数据")
        self.reset_btn.setFont(FontHelper.get_chinese_font(10))
        self.reset_btn.clicked.connect(self.reset_data)

        self.add_btn = QPushButton("添加成员")
        self.add_btn.setFont(FontHelper.get_chinese_font(10))
        self.add_btn.clicked.connect(self.show_add_member_dialog)

        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.add_btn)

        left_panel.addLayout(search_layout)
        left_panel.addWidget(sort_group)
        left_panel.addLayout(button_layout)

        # 成员表格
        self.member_table = MemberTableWidget(self.community_data, self)
        left_panel.addWidget(self.member_table)

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addLayout(left_panel)
        main_layout.addWidget(separator)

        # 右侧图表
        self.chart = CommunityAgeChart(self.community_data)
        self.chart_view = DynamicChartView(self.community_data)
        self.chart_view.setChart(self.chart)
        main_layout.addWidget(self.chart_view, stretch=1)

        # 信号连接
        self.search_combo.currentTextChanged.connect(self.filter_members)
        self.sort_btn_group.buttonClicked.connect(self.sort_members)

        # 设置随机排序为默认选中
        self.random_btn.click()

        self.resize(1100, 650)
        self.setWindowTitle("西牛贺洲社区居民年龄统计")

    def show_add_member_dialog(self):
        dialog = AddMemberDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:  # 等待对话框关闭
            # 获取输入值
            name = dialog.name_input.text().strip()
            age = int(dialog.age_input.text().strip())
            group = dialog.group_combo.currentText()
            self.add_new_member(name, age, group)

    def add_new_member(self, name: str, age: int, group: str):
        """添加新成员到数据中"""
        self.community_data.add_member(name, age, group)
        self.update_ui()

    def filter_members(self, text):
        if not text:
            self.community_data.reset_to_original()
        else:
            self.community_data.members = [
                m
                for m in self.community_data.original_members
                if text.lower() in m.name.lower()
            ]
        self.update_ui()

    def sort_members(self, btn):
        method = btn.text()
        self.community_data.sort_members(method)
        self.update_ui()

    def reset_data(self):
        self.community_data.reset_to_original()
        self.search_combo.setCurrentIndex(0)
        self.sort_btn_group.setExclusive(False)
        for btn in self.sort_btn_group.buttons():
            btn.setChecked(False)
        self.random_btn.click()
        self.sort_btn_group.setExclusive(True)
        self.update_ui()

    def update_ui(self):
        """更新整个界面，包括表格和图表"""
        self.member_table.populate_table()
        self.update_chart()
        # 更新搜索框中的姓名列表
        current_text = self.search_combo.currentText()
        self.search_combo.clear()
        self.search_combo.addItems([""] + self.community_data.names)
        if current_text in self.community_data.names:
            self.search_combo.setCurrentText(current_text)

    def update_chart(self):
        """专门更新图表"""
        self.chart.update_chart_data()
        self.chart_view.init_dynamic_settings()  # Update dynamic settings based on new data
        self.chart_view.update()
