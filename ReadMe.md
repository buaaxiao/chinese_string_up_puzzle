<!-- TODO>>>>输入优化：我方输入框回车即确定 -->
<!-- TODO>>>>配置优化：拼音自动生成 -->
<!-- TODO>>>>界面优化：增加模式选择菜单栏 -->
<!-- TODO>>>>已使用成语展示模式：支持历史显示模式选择：全部、我方、电脑 -->
<!-- TODO>>>>字匹配：支持首尾字匹配 -->
<!-- TODO>>>>模式变化之后继续接龙 -->
<!-- TODO>>>>电脑未接起来创新选择模式之后提示成语已使用 -->
<!-- TODO>>>>电脑答案去重 -->
<!-- TODO>>>>完全匹配：支持首尾读音和字都匹配 -->
<!-- TODO>>>>菜单选择不唯一问题 -->
<!-- TODO>>>>字典编码报错 -->
<!-- TODO>>>>字典文件改为json格式 -->
<!-- TODO>>>>增加日志记录 -->
<!-- TODO>>>>优化模式改变逻辑 -->
<!-- TODO>>>>非同字多音字模式：支持首尾多音字匹配 -->
<!-- TODO>>>>同字多音模式：支持首尾多音字匹配 -->
<!-- TODO>>>>优化多音字存储，提高初始化加载速度 -->
<!-- TODO>>>>智能提示 -->
<!-- TODO>>>>重开不清零 -->
<!-- TODO>>>>单回合模式 -->
<!-- TODO>>>>自动接龙 -->
<!-- TODO>>>>MVC模式设计 -->
<!-- TODO>>>>自动接龙提示已输入错误 -->
TODO>>>>语音播报
TODO>>>>生成接龙报告
TODO>>>>成语库配置

<!-- mac打包： -->
pip install Pillow;
rm -rf build dist logs xcommon/__pycache;
pyinstaller -i image/icon.png --windowed --clean --noconfirm --noconsole --add-data ./data:data --add-data ./image:image chinese_string_up_puzzle.py;
pyinstaller --clean --noconfirm chinese_string_up_puzzle.spec

<!-- clean: -->
rm -rf build dist logs xcommon/__pycache
