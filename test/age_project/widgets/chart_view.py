from utils.font_helper import *
from PyQt6.QtCharts import (
    QBarSet,
    QBarSeries,
    QChart,
    QBarCategoryAxis,
    QValueAxis,
    QChartView,
)
from PyQt6.QtGui import QBrush, QFont, QPainter
from PyQt6.QtCore import Qt, QMargins, QRectF, QPointF

import os
import sys

# Get the absolute path of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the deploy directory to sys.path
sys.path.extend([current_dir, os.path.dirname(current_dir)])


class CommunityAgeChart(QChart):
    def __init__(self, data_provider):
        super().__init__()
        self.data_provider = data_provider
        self.init_ui()
        self.adjust_for_member_count()

    def init_ui(self):
        self.setTitle("西牛贺洲社区居民年龄分布")
        self.setTitleFont(FontHelper.get_chinese_font(14, QFont.Weight.Bold))

        # 使用HTML格式设置带颜色的标题
        subtitle = (
            "(按组别显示颜色，年龄≥60岁名字显示为<font color='#d4af37'>金色</font>)"
        )
        self.setTitleBrush(QBrush(Qt.GlobalColor.black))  # 主标题颜色
        self.setTitle(subtitle)  # 设置带HTML格式的副标题

        self.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        self.update_chart_data()

    def update_chart_data(self):
        self.removeAllSeries()

        barset = QBarSet("居民年龄")
        for age in self.data_provider.ages:
            barset << age

        series = QBarSeries()
        series.append(barset)
        self.addSeries(series)

        # Update x-axis with current member names
        if not hasattr(self, "axisX"):
            self.axisX = QBarCategoryAxis()
            self.addAxis(self.axisX, Qt.AlignmentFlag.AlignBottom)
        else:
            self.axisX.clear()

        self.axisX.append(self.data_provider.names)
        self.axisX.setTitleText("居民姓名")
        series.attachAxis(self.axisX)

        # Update y-axis
        if not hasattr(self, "axisY"):
            self.axisY = QValueAxis()
            self.addAxis(self.axisY, Qt.AlignmentFlag.AlignLeft)

        self.axisY.setTitleText("年龄（岁）")
        self.axisY.setLabelFormat("%d")
        self.axisY.setRange(
            0,
            self.data_provider.max_age
            + (10 if self.data_provider.max_age < 50 else 20),
        )
        series.attachAxis(self.axisY)

        self.adjust_for_member_count()

    def adjust_for_member_count(self):
        member_count = self.data_provider.member_count

        if member_count > 15:
            self.setMargins(QMargins(5, 30, 5, 30))
            self.axisX.setLabelsAngle(-45)
        else:
            self.setMargins(QMargins(10, 40, 10, 30))
            self.axisX.setLabelsAngle(0)

        x_font_size = 8 if member_count > 20 else 10
        self.axisX.setLabelsFont(FontHelper.get_chinese_font(x_font_size))
        self.axisX.setTitleFont(
            FontHelper.get_chinese_font(x_font_size, QFont.Weight.Bold)
        )
        self.axisY.setLabelsFont(FontHelper.get_chinese_font(10))
        self.axisY.setTitleFont(FontHelper.get_chinese_font(10, QFont.Weight.Bold))

        self.axisX.setLabelsVisible(False)


class DynamicChartView(QChartView):
    def __init__(self, data_provider, parent=None):
        super().__init__(parent)
        self.data_provider = data_provider
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.init_dynamic_settings()

    def init_dynamic_settings(self):
        member_count = self.data_provider.member_count
        self.bar_margin_ratio = 0.2 if member_count > 15 else 0.1
        self.font_size = 8 if member_count > 20 else 10
        self.min_bar_width = 30

    def calculate_bar_width(self, plot_width, bar_count):
        min_width = self.min_bar_width
        calculated_width = plot_width / max(bar_count, 1)
        return max(calculated_width, min_width)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        chart = self.chart()

        if not chart.series():
            return

        series = chart.series()[0]
        if not isinstance(series, QBarSeries):
            return

        barsets = series.barSets()
        if not barsets:
            return

        barset = barsets[0]
        plot_area = chart.plotArea()
        bar_count = barset.count()

        bar_width = self.calculate_bar_width(plot_area.width(), bar_count)
        margin = bar_width * self.bar_margin_ratio

        font = FontHelper.get_chinese_font(self.font_size)
        painter.setFont(font)

        # Make sure we're using the current member list
        current_members = self.data_provider.members

        for i in range(bar_count):
            value = barset.at(i)
            if value <= 0:
                continue

            member = current_members[i]
            color = self.data_provider.get_color(member)

            x = plot_area.left() + i * bar_width + margin
            height = (
                value / chart.axes(Qt.Orientation.Vertical)[0].max()
            ) * plot_area.height()
            rect = QRectF(
                x, plot_area.bottom() - height, bar_width - 2 * margin, height
            )

            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(rect)

            if height > 20:
                painter.setPen(Qt.GlobalColor.white)
                label_pos = rect.topLeft() + QPointF(5, -5)
                painter.drawText(label_pos, f"{value}")

        # Draw member names below bars
        for i in range(bar_count):
            member = current_members[i]
            name_color = self.data_provider.get_name_color(member)
            label_pos = QPointF(
                plot_area.left() + i * bar_width + bar_width / 2,
                plot_area.bottom() + 20,
            )
            painter.setPen(name_color)
            painter.drawText(label_pos, member.name)
