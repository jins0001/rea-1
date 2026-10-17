[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "PC 하드웨어 실시간 웹 대시보드"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
python "$scriptDir\server.py"
