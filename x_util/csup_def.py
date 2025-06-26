# coding:utf-8
#############################################
# -author:shaw                              #
# -date:2025-05-26                          #
#############################################


# Get the absolute path of the current file
import os
import sys


current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the deploy directory to sys.path
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))


class XCSUDef:
    # name, Required, default="", type=str
    common_def = [
        ("his_dispaly_user", False, "我方", str),
        ("his_dispaly_ai", False, "电脑", str),
        ("progam_title", False, "成语接龙", str),
        ("progam_size_fix", False, 0, int),
        ("auto_timer_interval", False, 1, float),
    ]

    function_def = [
        ("word", False, 1, int),
        ("lzpinyin", False, 1, int),
        ("pinyin", False, 1, int),
        ("multi", False, 1, int),
        ("battlesingle", False, 1, int),
        ("auto", False, 1, int),
        ("promote", False, 1, int),
    ]
