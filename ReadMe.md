<!-- ------------------------------------------------------------------------
Copyright (c) 2023 project Chinese string up puzzle
This project is licensed under GNU GPL version 2.0 or above 
author: buaaxiao
-- ------------------------------------------------------------------------- -->
source_path: https://github.com/buaaxiao/chinese_string_up_puzzle.git 

<!-- 成语库生成 -->
py chinese_string_engine.py dict > data/data.json

<!-- mac打包： -->
pip install Pillow;
rm -rf build dist logs xcommon/__pycache__;
pyinstaller -i image/icon.png --windowed --clean --noconfirm --noconsole --add-data ./data:data --add-data ./image:image chinese_string_up_puzzle.py;
pyinstaller --clean --noconfirm chinese_string_up_puzzle.spec

<!-- clean: -->
rm -rf build dist logs xcommon/__pycache__

<!-- <TODO> -->
<TODO>安卓、苹果手机APP打包
