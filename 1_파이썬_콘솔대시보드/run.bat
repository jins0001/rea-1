@echo off
chcp 65001 > nul
title PC 하드웨어 분석기 - 콘솔 대시보드
cls
echo [하드웨어 분석기를 시작합니다...]
python "%~dp0src\analyzer.py"
pause
