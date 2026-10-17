import os
import sys
import json
import time
import platform
import subprocess
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

# 인코딩 처리
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def run_ps_json(cmd):
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

def get_hardware_payload():
    payload = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "os": f"{platform.system()} {platform.release()}",
        "cpu_name": platform.processor(),
        "disks": [],
        "volumes": [],
        "memory": {},
        "ram_modules": [],
        "io_perf": []
    }
    
    # 1. 물리 디스크
    disks = run_ps_json("Get-PhysicalDisk | Select-Object DeviceId, FriendlyName, MediaType, BusType, HealthStatus, OperationalStatus, Size")
    if disks:
        for d in disks:
            size_gb = round((d.get("Size") or 0) / (1024**3), 1)
            payload["disks"].append({
                "id": str(d.get("DeviceId", "?")),
                "name": d.get("FriendlyName", "Unknown Disk"),
                "type": d.get("MediaType", "SSD"),
                "bus": d.get("BusType", "NVMe"),
                "health": d.get("HealthStatus", "Healthy"),
                "status": d.get("OperationalStatus", "OK"),
                "size_gb": size_gb
            })
            
    # 2. 볼륨
    vols = run_ps_json("Get-Volume | Where-Object { $_.DriveLetter -ne $null } | Select-Object DriveLetter, FileSystemLabel, FileSystem, HealthStatus, Size, SizeRemaining")
    if vols:
        for v in vols:
            total = (v.get("Size") or 0) / (1024**3)
            free = (v.get("SizeRemaining") or 0) / (1024**3)
            used = max(0.0, total - free)
            used_pct = round((used / total * 100), 1) if total > 0 else 0
            payload["volumes"].append({
                "letter": f"{v.get('DriveLetter')}:",
                "label": v.get("FileSystemLabel") or "로컬 디스크",
                "fs": v.get("FileSystem", "NTFS"),
                "health": v.get("HealthStatus", "Healthy"),
                "total_gb": round(total, 1),
                "used_gb": round(used, 1),
                "free_gb": round(free, 1),
                "used_pct": used_pct
            })

    # 3. 메모리
    mem_data = run_ps_json("Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory")
    if mem_data:
        m = mem_data[0]
        total_kb = m.get("TotalVisibleMemorySize", 0)
        free_kb = m.get("FreePhysicalMemory", 0)
        used_kb = total_kb - free_kb
        payload["memory"] = {
            "total_gb": round(total_kb / (1024**2), 2),
            "used_gb": round(used_kb / (1024**2), 2),
            "free_gb": round(free_kb / (1024**2), 2),
            "used_pct": round((used_kb / total_kb * 100), 1) if total_kb > 0 else 0
        }
        
    # 4. RAM 모듈
    slots = run_ps_json("Get-CimInstance Win32_PhysicalMemory | Select-Object DeviceLocator, Manufacturer, Capacity, Speed, PartNumber")
    if slots:
        for s in slots:
            cap_gb = round((s.get("Capacity") or 0) / (1024**3), 1)
            payload["ram_modules"].append({
                "slot": s.get("DeviceLocator", "DIMM"),
                "manufacturer": s.get("Manufacturer") or "호환 메모리",
                "capacity_gb": cap_gb,
                "speed_mhz": s.get("Speed", 0),
                "part_number": (s.get("PartNumber") or "").strip()
            })
            
    # 5. I/O 성능
    io_data = run_ps_json("Get-CimInstance Win32_PerfFormattedData_PerfDisk_PhysicalDisk | Where-Object { $_.Name -ne '_Total' } | Select-Object Name, DiskReadBytesPerSec, DiskWriteBytesPerSec, PercentDiskTime")
    if io_data:
        for item in io_data:
            payload["io_perf"].append({
                "disk": item.get("Name", "Disk"),
                "read_mb_s": round((item.get("DiskReadBytesPerSec") or 0) / (1024**2), 2),
                "write_mb_s": round((item.get("DiskWriteBytesPerSec") or 0) / (1024**2), 2),
                "busy_pct": item.get("PercentDiskTime", 0)
            })
            
    return payload

class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def do_GET(self):
        if self.path == "/api/hardware":
            data = get_hardware_payload()
            encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
        else:
            super().do_GET()

    def log_message(self, format, *args):
        # 터미널 로그를 깔끔하게 유지하기 위해 단순화
        pass

def main():
    print(f"============================================================")
    print(f" 🌐 PC 하드웨어 실시간 웹 대시보드 서버가 시작되었습니다.")
    print(f"    - 주소: http://localhost:{PORT}")
    print(f"    - 브라우저를 자동으로 엽니다...")
    print(f"    - 종료하려면 [Ctrl+C]를 누르세요.")
    print(f"============================================================")
    
    server = HTTPServer(("0.0.0.0", PORT), DashboardHandler)
    
    # 1초 뒤 브라우저 자동 오픈
    def open_browser():
        time.sleep(1)
        webbrowser.open(f"http://localhost:{PORT}")
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n서버를 안전하게 종료합니다.")
        server.server_close()

if __name__ == "__main__":
    main()
