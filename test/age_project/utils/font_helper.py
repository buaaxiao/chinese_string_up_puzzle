from PyQt6.QtGui import (
    QFont,
)
import os
import sys

# Get the absolute path of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the deploy directory to sys.path
sys.path.extend([current_dir, os.path.dirname(current_dir)])


class FontHelper:
    @staticmethod
    def get_safe_font(font_names, size=10, weight=QFont.Weight.Normal, italic=False):
        font = QFont()
        available_fonts = QFont().families()

        for name in font_names:
            if name in available_fonts:
                font.setFamily(name)
                break

        font.setPointSize(size)
        font.setWeight(weight)
        font.setItalic(italic)
        return font

    @staticmethod
    def get_chinese_font(size=10, weight=QFont.Weight.Normal, italic=False):
        return FontHelper.get_safe_font(
            font_names=[
                "Microsoft YaHei",
                "SimHei",
                "NSimSun",
                "FangSong",
                "KaiTi",
                "Arial Unicode MS",
                "Arial",
                "sans-serif",
            ],
            size=size,
            weight=weight,
            italic=italic,
        )
