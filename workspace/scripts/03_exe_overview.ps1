# 3단계: Windows 프로그램(.exe)을 Ghidra로 들여다보기
# 대상: Git에 들어 있는 true.exe (아무 일도 안 하고 "성공"만 알려 주는 아주 작은 GPL 공개 프로그램)

. "$PSScriptRoot\00_env.ps1"
$exe = 'D:\Tools\Git\usr\bin\true.exe'

Invoke-Rea -Name '03_exe_overview' -ReaArgs @(
    'analyze', $exe, '--provider', 'ghidra'
)
