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
