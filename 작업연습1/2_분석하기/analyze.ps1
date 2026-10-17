# 2단계: 완성품(.exe)만 가지고 속을 들여다보기
# 소스 코드(src 폴더)는 보지 않는다고 생각하고, exe 파일만 REA에 넣습니다.

$exe = Join-Path (Split-Path -Parent $PSScriptRoot) '1_원본만들기\bin\GradeCalc.exe'
$out = Join-Path $PSScriptRoot 'result'
New-Item -ItemType Directory -Force $out | Out-Null

function Save-Rea([string]$name, [string[]]$reaArgs) {
    $text = & rea @reaArgs --format json 2>&1 | Out-String
    [IO.File]::WriteAllText((Join-Path $out "$name.json"), $text, [Text.UTF8Encoding]::new($false))
    Write-Host "[$name] 종료코드=$LASTEXITCODE"
}

# (1) 이 파일은 무엇인가? (신분증)
Save-Rea 'artifact' @('inspect-managed-artifact', $exe)
# (2) 안에 어떤 함수들이 있고, 무엇을 하는가? (함수 목록 + 명령어)
Save-Rea 'members'  @('inspect-managed-members', $exe)

# (3) 사람이 읽기 쉬운 보고서로 정리
python -I (Join-Path $PSScriptRoot 'summarize.py') $exe
