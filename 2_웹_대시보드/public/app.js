// PC 하드웨어 웹 대시보드 클라이언트 스크립트

const CIRCLE_CIRCUMFERENCE = 264; // 2 * PI * 42

async function fetchHardwareData() {
  try {
    const res = await fetch('/api/hardware', { cache: 'no-store' });
    if (!res.ok) throw new Error('서버 응답 오류: ' + res.status);
    const data = await res.json();
    updateUI(data);
  } catch (err) {
    console.error('하드웨어 데이터 조회 실패:', err);
    document.getElementById('last-update-time').innerText = '데이터 연결 재시도 중...';
  }
}

function updateUI(data) {
  // 1. 헤더 정보
  if (data.os) {
    document.getElementById('system-os-text').innerText = `${data.os} • ${data.cpu_name || 'Ryzen 7 5800H'}`;
  }
  document.getElementById('last-update-time').innerText = `최근 갱신: ${data.timestamp}`;

  // 2. 메모리(RAM) 원형 게이지
  const mem = data.memory || {};
  const usedPct = mem.used_pct || 0;
  const offset = CIRCLE_CIRCUMFERENCE - (CIRCLE_CIRCUMFERENCE * (usedPct / 100));
  
  const circleFill = document.getElementById('ram-circle-fill');
  circleFill.style.strokeDashoffset = offset;

  // 임계치에 따른 색상
  if (usedPct >= 85) {
    circleFill.style.stroke = 'var(--danger)';
  } else if (usedPct >= 70) {
    circleFill.style.stroke = 'var(--warning)';
  } else {
    circleFill.style.stroke = 'var(--accent)';
  }

  document.getElementById('ram-usage-pct').innerText = `${usedPct}%`;
  document.getElementById('ram-total-val').innerText = `${mem.total_gb || '--'} GB`;
  document.getElementById('ram-used-val').innerText = `${mem.used_gb || '--'} GB`;
  document.getElementById('ram-free-val').innerText = `${mem.free_gb || '--'} GB`;

  // 3. 물리 디스크 요약
  const disks = data.disks || [];
  document.getElementById('disk-count-text').innerText = `${disks.length}개 물리 드라이브`;
  
  const allSsd = disks.every(d => d.type === 'SSD');
  document.getElementById('disk-types-text').innerText = allSsd 
    ? '⚡ NVMe 초고속 SSD 100% 구성 (HDD 없음)' 
    : 'SSD 및 HDD 혼합 구성';

  const quickList = document.getElementById('physical-disk-quick-list');
  quickList.innerHTML = disks.map(d => `
    <div class="disk-item-pill">
      <span><strong>#${d.id}</strong> ${escapeHtml(d.name)}</span>
      <span class="badge ${d.health === 'Healthy' ? 'badge-success' : 'badge-warning'}">${d.type} • ${d.size_gb} GB</span>
    </div>
  `).join('');

  // 4. 실시간 디스크 I/O
  const ioContainer = document.getElementById('io-metrics-list');
  const ioPerf = data.io_perf || [];
  if (ioPerf.length === 0) {
    ioContainer.innerHTML = `<div class="disk-meta-text">I/O 활성 상태 측정 대기 중...</div>`;
  } else {
    ioContainer.innerHTML = ioPerf.map(io => `
      <div class="io-disk-row">
        <div class="io-disk-name">
          <span>디스크 ${escapeHtml(io.disk)}</span>
          <span class="badge badge-sm">활성률 ${io.busy_pct}%</span>
        </div>
        <div class="io-rates">
          <div class="io-rate-badge io-read">
            <span>↓ 읽기:</span>
            <strong>${io.read_mb_s} MB/s</strong>
          </div>
          <div class="io-rate-badge io-write">
            <span>↑ 쓰기:</span>
            <strong>${io.write_mb_s} MB/s</strong>
          </div>
        </div>
      </div>
    `).join('');
  }

  // 5. 볼륨 목록
  const volsContainer = document.getElementById('volumes-container');
  const vols = data.volumes || [];
  volsContainer.innerHTML = vols.map(v => {
    let barClass = '';
    if (v.used_pct >= 85) barClass = 'danger';
    else if (v.used_pct >= 70) barClass = 'warning';

    return `
      <div class="volume-card">
        <div class="volume-card-header">
          <div class="volume-letter-box">
            <div class="volume-badge">${v.letter.replace(':', '')}</div>
            <div>
              <div class="volume-label">${escapeHtml(v.label)} (${v.letter})</div>
              <div class="volume-fs">${v.fs} 파일시스템</div>
            </div>
          </div>
          <span class="badge badge-primary">${v.used_pct}% 사용됨</span>
        </div>
        <div class="progress-bar-bg">
          <div class="progress-bar-fill ${barClass}" style="width: ${v.used_pct}%;"></div>
        </div>
        <div class="volume-stats-row">
          <span>사용: <strong>${v.used_gb} GB</strong></span>
          <span>남은 여유: <strong class="text-success">${v.free_gb} GB</strong></span>
          <span>총: ${v.total_gb} GB</span>
        </div>
      </div>
    `;
  }).join('');

  // 6. RAM 슬롯 상세
  const slotsContainer = document.getElementById('ram-slots-container');
  const slots = data.ram_modules || [];
  document.getElementById('ram-slots-count').innerText = `${slots.length}개 장착됨`;
  slotsContainer.innerHTML = slots.map((s, idx) => `
    <div class="slot-card-item">
      <div class="slot-main">
        <div class="slot-name">슬롯 #${idx + 1} • ${escapeHtml(s.manufacturer)}</div>
        <div class="slot-sub">파트번호: ${escapeHtml(s.part_number || 'N/A')}</div>
      </div>
      <div class="slot-badge-box">
        <div class="slot-capacity">${s.capacity_gb} GB</div>
        <span class="badge badge-sm">${s.speed_mhz} MHz</span>
      </div>
    </div>
  `).join('');

  // 7. 물리 디스크 상세
  const pdisksContainer = document.getElementById('physical-disks-container');
  const totalDiskCap = disks.reduce((acc, cur) => acc + (cur.size_gb || 0), 0);
  document.getElementById('disks-total-capacity').innerText = `총 ${totalDiskCap.toFixed(1)} GB`;

  pdisksContainer.innerHTML = disks.map(d => `
    <div class="pdisk-card-item">
      <div class="pdisk-main">
        <div class="pdisk-name">#${d.id} ${escapeHtml(d.name)}</div>
        <div class="pdisk-sub">인터페이스: ${d.bus} • 구동 상태: ${d.status}</div>
      </div>
      <div class="pdisk-badge-box">
        <div class="pdisk-size">${d.size_gb} GB</div>
        <span class="badge ${d.health === 'Healthy' ? 'badge-success' : 'badge-warning'}">● ${d.health}</span>
      </div>
    </div>
  `).join('');
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// 2초 간격 자동 갱신
fetchHardwareData();
setInterval(fetchHardwareData, 2000);
