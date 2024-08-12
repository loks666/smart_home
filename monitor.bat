@echo off
REM 激活 conda 环境
call conda activate smart_home

REM 停止旧服务
python F:\order\smart_home\smart_home\check_shutdown.py stop

REM 删除旧服务
python F:\order\smart_home\smart_home\check_shutdown.py remove

REM 安装新服务
python F:\order\smart_home\smart_home\check_shutdown.py install

REM 启动新服务
python F:\order\smart_home\smart_home\check_shutdown.py start

echo 服务已成功更新并启动。
pause
