@echo off
chcp 65001 > nul
title PC 하드웨어 정밀 진단 도구 (PowerShell)
cls
echo [PowerShell 하드웨어 정밀 진단을 시작합니다...]
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Analyze-Hardware.ps1"
echo.
echo 아무 키나 누르면 창을 닫습니다.
pause > nul
