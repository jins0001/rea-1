# PowerShell 하드웨어 진단 스크립트
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "PC 하드웨어 진단 도구 (PowerShell)"

Clear-Host
Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host " [PC 하드웨어 정밀 진단 도구] SSD / HDD / RAM 분석기" -ForegroundColor White
Write-Host " Windows PowerShell 내장 WMI/CIM 진단 엔진 v1.0" -ForegroundColor DarkGray
Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. 기본 시스템 정보
$os = Get-CimInstance Win32_OperatingSystem
$cs = Get-CimInstance Win32_ComputerSystem
$timeStr = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")

Write-Host "▶ [1] 기본 시스템 정보" -ForegroundColor Yellow
Write-Host "---------------------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  • 컴퓨터 이름 : $($cs.Name)"
Write-Host "  • 운영체제    : $($os.Caption) ($($os.OSArchitecture))"
Write-Host "  • 진단 시각   : $timeStr"
Write-Host ""

# 2. 물리 디스크
Write-Host "▶ [2] 물리 디스크 (SSD / HDD) 상태" -ForegroundColor Yellow
Write-Host "---------------------------------------------------------------------------" -ForegroundColor DarkGray
$physicalDisks = Get-PhysicalDisk | Select-Object DeviceId, FriendlyName, MediaType, BusType, HealthStatus, OperationalStatus, Size

$diskRows = @()
foreach ($d in $physicalDisks) {
    $sizeGB = [math]::Round($d.Size / 1GB, 1)
    $typeColor = if ($d.MediaType -eq "SSD") { "Cyan" } else { "Magenta" }
    $healthColor = if ($d.HealthStatus -eq "Healthy") { "Green" } else { "Red" }

    Write-Host "  • [디스크 #$($d.DeviceId)] $($d.FriendlyName)" -ForegroundColor White
    Write-Host "    - 종류/버스 : [$($d.MediaType)] / $($d.BusType)" -ForegroundColor $typeColor
    Write-Host "    - 총 용량   : $sizeGB GB"
    Write-Host "    - 건강 상태 : ● $($d.HealthStatus) (상태: $($d.OperationalStatus))" -ForegroundColor $healthColor
    Write-Host ""

    $diskRows += "<tr><td><strong>#$($d.DeviceId)</strong> $($d.FriendlyName)</td><td><span class='badge badge-type'>$($d.MediaType)</span></td><td>$($d.BusType)</td><td><strong>$sizeGB GB</strong></td><td><span class='badge badge-health'>● $($d.HealthStatus)</span></td></tr>"
}

# 3. 볼륨
Write-Host "▶ [3] 볼륨 및 파티션 사용 현황" -ForegroundColor Yellow
Write-Host "---------------------------------------------------------------------------" -ForegroundColor DarkGray
$volumes = Get-Volume | Where-Object { $_.DriveLetter -ne $null } | Select-Object DriveLetter, FileSystemLabel, FileSystem, HealthStatus, Size, SizeRemaining

$volRows = @()
foreach ($v in $volumes) {
    $totalGB = [math]::Round($v.Size / 1GB, 1)
    $freeGB = [math]::Round($v.SizeRemaining / 1GB, 1)
    $usedGB = [math]::Round($totalGB - $freeGB, 1)
    $usedPct = if ($totalGB -gt 0) { [math]::Round(($usedGB / $totalGB) * 100, 1) } else { 0 }

    $barCount = [math]::Min(20, [math]::Max(0, [int]($usedPct / 5)))
    $emptyCount = 20 - $barCount
    $barStr = "[" + ("#" * $barCount) + (" " * $emptyCount) + "]"

    Write-Host "  [$($v.DriveLetter):] $barStr $usedPct%  $usedGB GB 사용 / $totalGB GB 전체 (여유: $freeGB GB) [$($v.FileSystem)]" -ForegroundColor White

    $volRows += "<tr><td><strong>$($v.DriveLetter):</strong></td><td>$($v.FileSystemLabel)</td><td>$($v.FileSystem)</td><td>$totalGB GB</td><td>$usedGB GB ($usedPct%)</td><td><strong style='color:#34d399;'>$freeGB GB</strong></td></tr>"
}
Write-Host ""

# 4. 메모리
Write-Host "▶ [4] 시스템 메모리 (RAM) 및 슬롯 상세" -ForegroundColor Yellow
Write-Host "---------------------------------------------------------------------------" -ForegroundColor DarkGray
$totalMemGB = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
$freeMemGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
$usedMemGB = [math]::Round($totalMemGB - $freeMemGB, 2)
$memPct = [math]::Round(($usedMemGB / $totalMemGB) * 100, 1)

Write-Host "  • 전체 메모리  : $totalMemGB GB"
Write-Host "  • 사용 중      : $usedMemGB GB ($memPct%)" -ForegroundColor Cyan
Write-Host "  • 남은 여유    : $freeMemGB GB" -ForegroundColor Green
Write-Host ""
Write-Host "  [메모리 슬롯 구성]" -ForegroundColor DarkCyan

$ramSlots = Get-CimInstance Win32_PhysicalMemory | Select-Object DeviceLocator, Manufacturer, Capacity, Speed, PartNumber
$ramRows = @()
$slotNum = 1
foreach ($s in $ramSlots) {
    $capGB = [math]::Round($s.Capacity / 1GB, 1)
    $mfg = if ([string]::IsNullOrWhiteSpace($s.Manufacturer) -or $s.Manufacturer -eq "Unknown") { "호환 메모리" } else { $s.Manufacturer }
    Write-Host "    슬롯 $slotNum : $capGB GB | 제조사: $mfg | 속도: $($s.Speed) MHz | 파트: $($s.PartNumber)" -ForegroundColor Gray

    $ramRows += "<tr><td>슬롯 #$slotNum ($($s.DeviceLocator))</td><td><strong>$mfg</strong></td><td><strong>$capGB GB</strong></td><td>$($s.Speed) MHz</td><td>$($s.PartNumber)</td></tr>"
    $slotNum++
}

Write-Host ""
Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host " 진단 완료! 상세 HTML 보고서를 생성합니다..." -ForegroundColor Green

# 5. HTML 보고서 파일 출력
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$reportPath = Join-Path $scriptDir "Hardware_Diagnostic_Report.html"

$diskHtml = $diskRows -join "`n"
$volHtml = $volRows -join "`n"
$ramHtml = $ramRows -join "`n"

$html = @"
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>내 PC 하드웨어 진단 리포트 (PowerShell)</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 30px; margin: 0; }
    .container { max-width: 950px; margin: 0 auto; background: #1e293b; border-radius: 16px; padding: 35px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    h1 { color: #38bdf8; margin-top: 0; font-size: 24px; border-bottom: 2px solid #334155; padding-bottom: 12px; }
    h2 { color: #818cf8; font-size: 18px; margin-top: 28px; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #334155; }
    th { background: #0f172a; color: #94a3b8; }
    .badge { padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: bold; }
    .badge-health { background: rgba(52, 211, 153, 0.2); color: #34d399; }
    .badge-type { background: rgba(56, 189, 248, 0.2); color: #38bdf8; }
    .stat-box { display: flex; gap: 20px; margin-top: 15px; }
    .stat-card { flex: 1; background: #0f172a; padding: 16px; border-radius: 10px; border: 1px solid #334155; text-align: center; }
    .stat-card .val { font-size: 22px; font-weight: bold; color: #38bdf8; margin-top: 6px; }
    .footer { text-align: center; color: #64748b; font-size: 12px; margin-top: 30px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>내 PC 하드웨어 정밀 진단 보고서</h1>
    <p style="color: #94a3b8;">생성 일시: $timeStr | 대상 OS: $($os.Caption)</p>

    <div class="stat-box">
      <div class="stat-card">
        <div>시스템 전체 메모리</div>
        <div class="val">$totalMemGB GB</div>
      </div>
      <div class="stat-card">
        <div>메모리 사용률</div>
        <div class="val" style="color: #fbbf24;">$memPct%</div>
      </div>
      <div class="stat-card">
        <div>장착된 물리 디스크</div>
        <div class="val">$($physicalDisks.Count)개 (SSD)</div>
      </div>
    </div>

    <h2>1. 물리 디스크 (SSD 및 HDD) 상세</h2>
    <table>
      <thead><tr><th>드라이브 이름</th><th>종류</th><th>인터페이스</th><th>용량</th><th>건강 상태</th></tr></thead>
      <tbody>
$diskHtml
      </tbody>
    </table>

    <h2>2. 볼륨 및 파티션 여유 공간</h2>
    <table>
      <thead><tr><th>드라이브</th><th>이름</th><th>형식</th><th>전체 용량</th><th>사용량</th><th>남은 여유</th></tr></thead>
      <tbody>
$volHtml
      </tbody>
    </table>

    <h2>3. 메모리(RAM) 모듈 슬롯 스펙</h2>
    <table>
      <thead><tr><th>슬롯 위치</th><th>제조사</th><th>용량</th><th>속도</th><th>파트 번호</th></tr></thead>
      <tbody>
$ramHtml
      </tbody>
    </table>

    <div class="footer">본 보고서는 Windows PowerShell 내장 WMI 진단 엔진으로 수집되었습니다.</div>
  </div>
</body>
</html>
"@

[System.IO.File]::WriteAllText($reportPath, $html, [System.Text.Encoding]::UTF8)
Write-Host " [보고서 저장 완료] $reportPath" -ForegroundColor DarkGray
Write-Host " [브라우저로 보고서를 엽니다...]" -ForegroundColor Cyan

try {
    Start-Process $reportPath
} catch {}