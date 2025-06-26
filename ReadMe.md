<!-- ------------------------------------------------------------------------
Copyright (c) 2023 project Chinese string up puzzle
This project is licensed under GNU GPL version 2.0 or above
author: buaaxiao
-- ------------------------------------------------------------------------- -->

source_path:
<https://gitee.com/buaaxiao/chinese_string_up_puzzle.git>

pip3 install pypinyin
pip3 install PyQt6
pip3 install pyinstaller

mac pack:
pip3 install Pillow && py x_util/xTest.py clean && pyinstaller -n ChineseStringUpPuzzle -i image/icon.png --windowed --clean --noconfirm --noconsole --add-data ./data:data --add-data ./image:image chinese_string_up_puzzle.py && pyinstaller --clean --noconfirm ChineseStringUpPuzzle.spec
