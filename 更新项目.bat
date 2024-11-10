CHCP 65001
@echo off

echo 更新portable git
.\PortableGit\bin\git.exe submodule update --init --recursive

echo 拉取项目更新中
.\PortableGit\bin\git.exe stash
.\PortableGit\bin\git.exe pull https://gitee.com/CodeCCSky/chatWithQing.git main

echo 更新完成
pause