[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "PC 하드웨어 분석기 - 콘솔 대시보드"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
python "$scriptDir\src\analyzer.py"
