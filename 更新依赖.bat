CHCP 65001
@echo off

echo 更新中
runtime\python.exe -m pip  config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
runtime\python.exe -m pip  config set install.trusted-host pypi.tuna.tsinghua.edu.cn
runtime\python.exe -m pip install -r ./requirements.txt

pause