# 작업연습(악성코드분석) 전체 실행: 훈련용 샘플 빌드 → 정적 분석 → 보고서·IOC·YARA
Write-Host '===== ① 훈련용 샘플 만들기 ====='
& "$PSScriptRoot\1_훈련용샘플\build.ps1"
Write-Host ''
Write-Host '===== ②~⑤ 정적 분석 ====='
& "$PSScriptRoot\2_분석\analyze.ps1"
Write-Host ''
Write-Host "보고서: $PSScriptRoot\2_분석\분석보고서.md"
Write-Host "IOC 목록: $PSScriptRoot\3_탐지규칙\ioc_list.csv"
Write-Host "YARA 규칙: $PSScriptRoot\3_탐지규칙\training_sample.yar"
