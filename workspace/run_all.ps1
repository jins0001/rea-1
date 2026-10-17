# 전체 실습을 한 번에 실행합니다.
#   사용법: PowerShell에서  D:\SW\rsa\workspace\run_all.ps1

$s = Join-Path $PSScriptRoot 'scripts'
& "$s\01_apk_overview.ps1"
& "$s\02_apk_decompile.ps1"
& "$s\03_exe_overview.ps1"
python -I "$s\04_summarize.py" | Out-Null
Write-Host "완료 → $PSScriptRoot\output\요약.md"
