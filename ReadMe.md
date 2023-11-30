<!-- ------------------------------------------------------------------------
Copyright (c) 2023 project Chinese string up puzzle
This project is licensed under GNU GPL version 2.0 or above 
author: buaaxiao
-- ------------------------------------------------------------------------- -->
source_path: https://github.com/buaaxiao/chinese_string_up_puzzle.git 

<!-- 成语库生成 -->
py chinese_string_dict_generator.py

<!-- mac打包： -->
<!-- pip install Pillow; -->
rm -rf build dist logs xcommon/__pycache__;
pyinstaller -n ChineseStringUpPuzzle -i image/icon.png --windowed --clean --noconfirm --noconsole --add-data ./data:data --add-data ./image:image chinese_string_up_puzzle.py;
pyinstaller --clean --noconfirm ChineseStringUpPuzzle.spec
