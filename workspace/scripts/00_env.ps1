# 공통 설정: 다른 스크립트들이 맨 처음에 불러서 씁니다.
# (VS Code를 다시 켜기 전에도 동작하도록 도구 위치를 직접 지정)

$env:GHIDRA_INSTALL_DIR = 'D:\Tools\ghidra_12.1.4_PUBLIC'
$env:JAVA_HOME          = 'C:\Program Files\Eclipse Adoptium\jdk-21.0.12.101-hotspot'
$env:REA_JADX_MCP_JAR   = 'D:\Tools\jadx\jadx-headless-mcp-0.7.1-all.jar'

$Root    = Split-Path -Parent $PSScriptRoot          # D:\SW\rsa\workspace
$Samples = Join-Path (Split-Path -Parent $Root) 'samples'
$Output  = Join-Path $Root 'output'
New-Item -ItemType Directory -Force $Output | Out-Null

# REA 명령을 실행하고 결과를 JSON 파일로 저장하는 도우미 함수
function Invoke-Rea {
    param([string]$Name, [string[]]$ReaArgs)
    $file = Join-Path $Output "$Name.json"
    $sw = [Diagnostics.Stopwatch]::StartNew()
    $text = & rea @ReaArgs --format json 2>&1 | Out-String
    $code = $LASTEXITCODE
    [IO.File]::WriteAllText($file, $text, [Text.UTF8Encoding]::new($false))
    Write-Host ("[{0}] 종료코드={1}, {2}초 → {3}" -f $Name, $code, [int]$sw.Elapsed.TotalSeconds, $file)
}
