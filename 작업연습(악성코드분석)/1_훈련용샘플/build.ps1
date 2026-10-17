# 훈련용 샘플 만들기 (무해함 — 안내 문구만 출력)
$csc = 'C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe'
$src = Join-Path $PSScriptRoot 'src\TrainingSample.cs'
$bin = Join-Path $PSScriptRoot 'bin'
New-Item -ItemType Directory -Force $bin | Out-Null

& $csc /nologo /optimize+ /out:"$bin\TrainingSample.exe" $src
if ($LASTEXITCODE -ne 0) { Write-Host '컴파일 실패'; exit 1 }
Write-Host "훈련용 샘플: $bin\TrainingSample.exe"
