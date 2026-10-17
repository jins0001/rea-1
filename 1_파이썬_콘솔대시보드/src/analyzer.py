import os
import sys
import time
import json
import subprocess
import platform

# Windows 터미널 한글 및 유니코드 깨짐 방지
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class Color:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    BG_BLUE = '\033[44m'

def make_bar(percent, width=25):
    filled = int(width * (percent / 100.0))
    filled = max(0, min(width, filled))
    empty = width - filled
    
    if percent >= 90:
        color = Color.RED
    elif percent >= 75:
        color = Color.YELLOW
    else:
        color = Color.GREEN
        
    return f"{color}[{'■' * filled}{' ' * empty}]{Color.RESET} {percent:5.1f}%"

def run_ps_json(cmd):
    """PowerShell 명령을 실행하여 JSON 객체로 반환"""
    full_cmd = f"powershell -NoProfile -OutputFormat Text -Command \"[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; {cmd} | ConvertTo-Json -Depth 3 -Compress\""
    try:
        p = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=8)
        raw = p.stdout.strip()
        if not raw:
            return None
        data = json.loads(raw)
        return data if isinstance(data, list) else [data]
    except Exception:
        return []

def get_hardware_info():
    info = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "os": f"{platform.system()} {platform.release()}",
        "disks": [],
        "volumes": [],
        "memory": {},
        "ram_modules": [],
        "io_perf": []
    }
    
    # 1. 물리 디스크 정보 (SSD vs HDD, 버스 종류, 건강 상태)
    ps_disk_cmd = "Get-PhysicalDisk | Select-Object DeviceId, FriendlyName, MediaType, BusType, HealthStatus, OperationalStatus, Size"
    disks = run_ps_json(ps_disk_cmd)
    if disks:
        for d in disks:
            size_gb = round((d.get("Size") or 0) / (1024**3), 1)
            info["disks"].append({
                "id": str(d.get("DeviceId", "?")),
                "name": d.get("FriendlyName", "Unknown"),
                "type": d.get("MediaType", "Unspecified"),
                "bus": d.get("BusType", "Unknown"),
                "health": d.get("HealthStatus", "Unknown"),
                "status": d.get("OperationalStatus", "Unknown"),
                "size_gb": size_gb
            })
            
    # 2. 볼륨 및 드라이브 여유 공간 (C:, D:, E: 등)
    ps_vol_cmd = "Get-Volume | Where-Object { $_.DriveLetter -ne $null } | Select-Object DriveLetter, FileSystemLabel, FileSystem, HealthStatus, Size, SizeRemaining"
    vols = run_ps_json(ps_vol_cmd)
    if vols:
        for v in vols:
            total = (v.get("Size") or 0) / (1024**3)
            free = (v.get("SizeRemaining") or 0) / (1024**3)
            used = max(0.0, total - free)
            used_pct = round((used / total * 100), 1) if total > 0 else 0
            info["volumes"].append({
                "letter": f"{v.get('DriveLetter')}:",
                "label": v.get("FileSystemLabel") or "(이름 없음)",
                "fs": v.get("FileSystem", "NTFS"),
                "health": v.get("HealthStatus", "Healthy"),
                "total_gb": round(total, 1),
                "used_gb": round(used, 1),
                "free_gb": round(free, 1),
                "used_pct": used_pct
            })
            
    # 3. 전체 메모리 상태
    ps_mem_cmd = "Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory"
    mem_data = run_ps_json(ps_mem_cmd)
    if mem_data:
        m = mem_data[0]
        total_kb = m.get("TotalVisibleMemorySize", 0)
        free_kb = m.get("FreePhysicalMemory", 0)
        used_kb = total_kb - free_kb
        total_gb = round(total_kb / (1024**2), 2)
        used_gb = round(used_kb / (1024**2), 2)
        free_gb = round(free_kb / (1024**2), 2)
        used_pct = round((used_kb / total_kb * 100), 1) if total_kb > 0 else 0
        info["memory"] = {
            "total_gb": total_gb,
            "used_gb": used_gb,
            "free_gb": free_gb,
            "used_pct": used_pct
        }
        
    # 4. 물리 RAM 슬롯별 상세 (제조사, 클럭, 용량)
    ps_ram_slots = "Get-CimInstance Win32_PhysicalMemory | Select-Object DeviceLocator, Manufacturer, Capacity, Speed, PartNumber"
    slots = run_ps_json(ps_ram_slots)
    if slots:
        for s in slots:
            cap_gb = round((s.get("Capacity") or 0) / (1024**3), 1)
            info["ram_modules"].append({
                "slot": s.get("DeviceLocator", "DIMM"),
                "manufacturer": s.get("Manufacturer", "Unknown"),
                "capacity_gb": cap_gb,
                "speed_mhz": s.get("Speed", 0),
                "part_number": (s.get("PartNumber") or "").strip()
            })
            
    # 5. 디스크 실시간 I/O
    ps_io_cmd = "Get-CimInstance Win32_PerfFormattedData_PerfDisk_PhysicalDisk | Where-Object { $_.Name -ne '_Total' } | Select-Object Name, DiskReadBytesPerSec, DiskWriteBytesPerSec, PercentDiskTime"
    io_data = run_ps_json(ps_io_cmd)
    if io_data:
        for item in io_data:
            read_mb = round((item.get("DiskReadBytesPerSec") or 0) / (1024**2), 2)
            write_mb = round((item.get("DiskWriteBytesPerSec") or 0) / (1024**2), 2)
            info["io_perf"].append({
                "disk": item.get("Name", "Disk"),
                "read_mb_s": read_mb,
                "write_mb_s": write_mb,
                "busy_pct": item.get("PercentDiskTime", 0)
            })
            
    return info

def print_dashboard(info):
    clear_screen()
    print(f"{Color.CYAN}{'=' * 75}{Color.RESET}")
    print(f"{Color.BOLD}{Color.WHITE} 🖥️  내 PC 하드웨어 정밀 분석 콘솔 대시보드 (SSD / HDD / 메모리){Color.RESET}")
    print(f"    기준 시각: {Color.YELLOW}{info['timestamp']}{Color.RESET}   |   운영체제: {Color.GREEN}{info['os']}{Color.RESET}")
    print(f"{Color.CYAN}{'=' * 75}{Color.RESET}\n")

    # [1] 물리 디스크 (SSD & HDD)
    print(f"{Color.BOLD}{Color.MAGENTA}▶ [1] 물리 디스크 분석 (Physical Disks){Color.RESET}")
    print(f"{'-' * 75}")
    if info["disks"]:
        for d in info["disks"]:
            type_color = Color.CYAN if d["type"] == "SSD" else Color.YELLOW
            health_color = Color.GREEN if d["health"] == "Healthy" else Color.RED
            print(f"  • {Color.BOLD}디스크 #{d['id']}{Color.RESET} {d['name']}")
            print(f"    - 구분/인터페이스 : {type_color}[{d['type']}]{Color.RESET} / {d['bus']}")
            print(f"    - 총 용량         : {d['size_gb']} GB")
            print(f"    - 건강 상태       : {health_color}● {d['health']} ({d['status']}){Color.RESET}")
    else:
        print("  (디스크 정보를 불러올 수 없습니다)")
    print()

    # [2] 드라이브별 용량 및 남은 공간 (Volumes)
    print(f"{Color.BOLD}{Color.CYAN}▶ [2] 드라이브 볼륨 및 사용률 (Volumes & Free Space){Color.RESET}")
    print(f"{'-' * 75}")
    if info["volumes"]:
        for v in info["volumes"]:
            bar = make_bar(v["used_pct"], width=22)
            print(f"  [{Color.BOLD}{v['letter']}{Color.RESET}] {bar}  "
                  f"{v['used_gb']:5.1f} GB 사용 / {v['total_gb']:5.1f} GB 전체 (여유: {Color.GREEN}{v['free_gb']:5.1f} GB{Color.RESET}) "
                  f"[{v['fs']}]")
    else:
        print("  (볼륨 정보를 불러올 수 없습니다)")
    print()

    # [3] 메모리 (RAM) 분석
    print(f"{Color.BOLD}{Color.GREEN}▶ [3] 시스템 메모리 분석 (RAM){Color.RESET}")
    print(f"{'-' * 75}")
    m = info.get("memory", {})
    if m:
        bar = make_bar(m["used_pct"], width=30)
        print(f"  • 실시간 사용률: {bar}")
        print(f"  • 전체 메모리  : {m['total_gb']} GB")
        print(f"  • 사용 중      : {Color.YELLOW}{m['used_gb']} GB{Color.RESET}")
        print(f"  • 남은 메모리  : {Color.GREEN}{m['free_gb']} GB{Color.RESET}")
        print()
        
    if info["ram_modules"]:
        print(f"  {Color.BOLD}장착된 RAM 모듈 슬롯 (물리 하드웨어 제원):{Color.RESET}")
        for idx, slot in enumerate(info["ram_modules"], 1):
            mfg = slot["manufacturer"] if slot["manufacturer"] != "Unknown" else "호환 메모리"
            print(f"    슬롯 {idx}: {Color.BOLD}{slot['capacity_gb']} GB{Color.RESET} | "
                  f"제조사: {mfg:12} | "
                  f"클럭: {slot['speed_mhz']} MHz | "
                  f"파트번호: {slot['part_number']}")
    print()

    # [4] 실시간 디스크 I/O 속도
    print(f"{Color.BOLD}{Color.YELLOW}▶ [4] 디스크 실시간 읽기/쓰기 속도 (Disk I/O Activity){Color.RESET}")
    print(f"{'-' * 75}")
    if info["io_perf"]:
        for io in info["io_perf"]:
            print(f"  • {io['disk']:12} | "
                  f"읽기: {Color.CYAN}{io['read_mb_s']:6.2f} MB/s{Color.RESET} | "
                  f"쓰기: {Color.MAGENTA}{io['write_mb_s']:6.2f} MB/s{Color.RESET} | "
                  f"활성률: {io['busy_pct']}%")
    else:
        print("  (I/O 정보를 불러오는 중...)")
    print(f"\n{Color.CYAN}{'=' * 75}{Color.RESET}")

def main():
    if "--report" in sys.argv:
        # 1회 출력 모드
        info = get_hardware_info()
        print_dashboard(info)
    else:
        # 실시간 모니터링 모드 (기본 3초 간격 갱신)
        try:
            print(f"{Color.CYAN}하드웨어 정보를 읽어오는 중입니다...{Color.RESET}")
            while True:
                info = get_hardware_info()
                print_dashboard(info)
                print(f"\n{Color.GRAY}[Ctrl+C 를 누르면 종료됩니다. 3초마다 자동 갱신 중]{Color.RESET}")
                time.sleep(3)
        except KeyboardInterrupt:
            print(f"\n{Color.GREEN}프로그램을 종료합니다.{Color.RESET}")

if __name__ == "__main__":
    main()
