# 4단계(도전): 같은 프로그램을 Go로 만들어 기계어 exe로 빌드하고, REA로 분석해 C# 버전과 비교

$env:GHIDRA_INSTALL_DIR = 'D:\Tools\ghidra_12.1.4_PUBLIC'
$env:JAVA_HOME          = 'C:\Program Files\Eclipse Adoptium\jdk-21.0.12.101-hotspot'

$src = Join-Path $PSScriptRoot 'src'
$bin = Join-Path $PSScriptRoot 'bin'
$out = Join-Path $PSScriptRoot 'result'
New-Item -ItemType Directory -Force $bin, $out | Out-Null

# (1) 빌드
Push-Location $src
if (-not (Test-Path 'go.mod')) { go mod init gradecalc | Out-Null }
go build -o "$bin\gradecalc.exe" .
Pop-Location
$exe = "$bin\gradecalc.exe"
Write-Host ("빌드 완료: {0} ({1:N0} 바이트)" -f $exe, (Get-Item $exe).Length)
& $exe 90 85 77

function Save-Rea([string]$name, [string[]]$reaArgs) {
    $sw = [Diagnostics.Stopwatch]::StartNew()
    $text = & rea @reaArgs --format json 2>&1 | Out-String
    [IO.File]::WriteAllText((Join-Path $out "$name.json"), $text, [Text.UTF8Encoding]::new($false))
    Write-Host ("[{0}] 종료코드={1}, {2}초" -f $name, $LASTEXITCODE, [int]$sw.Elapsed.TotalSeconds)
}

# (2) 파일 신분증 (Ghidra 없이 바로)
#     ※ 'inspect-go-binary'(Go 전용 정보)는 저장소 최신 코드에만 있고 npm 6.4.0에는 아직 없음
Save-Rea 'artifact' @('inspect-artifact', $exe)
# (3) Ghidra로 grade 함수를 의사 코드(C 비슷한 코드)로 복원 — 1분 정도 걸림
Save-Rea 'ghidra_grade' @('decompile', $exe, 'main.grade', '--provider', 'ghidra')

# (4) 의사 코드만 따로 .c 파일로 저장해서 보기 쉽게
$j = Get-Content (Join-Path $out 'ghidra_grade.json') -Raw -Encoding utf8 | ConvertFrom-Json
[IO.File]::WriteAllText((Join-Path $out '의사코드_grade.c'), $j.normalized_result, [Text.UTF8Encoding]::new($false))
Write-Host "의사 코드: $out\의사코드_grade.c"
