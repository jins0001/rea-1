# 정적 분석 전체 실행 — 대상 파일을 절대 실행하지 않습니다.
#   사용법: .\analyze.ps1                       (기본: 훈련용 샘플)
#           .\analyze.ps1 -Target D:\격리\의심.exe_  (다른 파일)
param(
    [string]$Target = (Join-Path (Split-Path -Parent $PSScriptRoot) '1_훈련용샘플\bin\TrainingSample.exe'),
    [string]$Baseline = 'D:\Tools\Git\usr\bin\true.exe'
)

$env:GHIDRA_INSTALL_DIR = 'D:\Tools\ghidra_12.1.4_PUBLIC'
$env:JAVA_HOME          = 'C:\Program Files\Eclipse Adoptium\jdk-21.0.12.101-hotspot'
$result = Join-Path $PSScriptRoot 'result'
$rules  = Join-Path (Split-Path -Parent $PSScriptRoot) '3_탐지규칙'
New-Item -ItemType Directory -Force $result | Out-Null

function Save-Rea([string]$name, [string[]]$reaArgs) {
    $text = & rea @reaArgs --format json 2>&1 | Out-String
    [IO.File]::WriteAllText((Join-Path $result "$name.json"), $text, [Text.UTF8Encoding]::new($false))
    Write-Host "[REA $name] 종료코드=$LASTEXITCODE"
}

Write-Host '== 1. 트리아지 (지문·구역·글자·지표) =='
python -I "$PSScriptRoot\triage.py" $Target   "$result\triage_sample.json"
python -I "$PSScriptRoot\triage.py" $Baseline "$result\triage_baseline.json"

Write-Host '== 2. REA 정적 분석 =='
Save-Rea 'rea_artifact' @('inspect-artifact', $Target)
$isDotnet = (Get-Content "$result\triage_sample.json" -Raw -Encoding utf8 | ConvertFrom-Json).pe.is_dotnet
if ($isDotnet) {
    Save-Rea 'rea_native_boundaries' @('inspect-managed-native-boundaries', $Target)   # 선언된 외부 함수
    Save-Rea 'rea_members'           @('inspect-managed-members', $Target)             # 실제 호출 관계
} else {
    Remove-Item "$result\rea_native_boundaries.json", "$result\rea_members.json" -ErrorAction SilentlyContinue
    Save-Rea 'rea_ghidra_overview' @('analyze', $Target, '--provider', 'ghidra')       # 네이티브: Ghidra
}
Save-Rea 'rea_pe_resources' @('inspect-pe-resources', $Target)

Write-Host '== 3. 보고서·IOC·탐지 규칙 =='
python -I "$PSScriptRoot\report.py" $result $rules
