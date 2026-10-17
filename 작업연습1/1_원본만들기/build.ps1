# 1단계: 소스 코드(.cs)를 완성품(.exe)으로 만들기 (컴파일)
# Windows에 기본으로 들어 있는 C# 컴파일러(csc.exe)를 사용합니다.

$csc = 'C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe'
$src = Join-Path $PSScriptRoot 'src\GradeCalc.cs'
$bin = Join-Path $PSScriptRoot 'bin'
New-Item -ItemType Directory -Force $bin | Out-Null

& $csc /nologo /optimize+ /out:"$bin\GradeCalc.exe" $src
if ($LASTEXITCODE -ne 0) { Write-Host '컴파일 실패'; exit 1 }

Write-Host "완성품: $bin\GradeCalc.exe"
Write-Host '--- 실행해 보기 ---'
& "$bin\GradeCalc.exe" 90 85 77
& "$bin\GradeCalc.exe" 99 98 97
& "$bin\GradeCalc.exe" 100 100 30
