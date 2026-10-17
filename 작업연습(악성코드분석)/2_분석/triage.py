"""정적 1차 분석(트리아지) — 의심 파일을 '실행하지 않고' 읽기만 해서 특징을 뽑습니다.

사용법: python -I triage.py <의심파일> <결과.json>
표준 라이브러리만 사용 (추가 설치 없음).
"""
import base64
import hashlib
import json
import math
import re
import struct
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

if sys.stdout:  # 창 프로그램(pythonw)에서 불러 쓸 때는 stdout이 없음
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------- 의심 API 사전
# API 이름 → (쉬운 설명, MITRE ATT&CK 기법 번호)
SUSPICIOUS_APIS = {
    "IsDebuggerPresent": ("디버거(분석 도구) 감지", "T1622 Debugger Evasion"),
    "CheckRemoteDebuggerPresent": ("디버거 감지", "T1622 Debugger Evasion"),
    "VirtualAlloc": ("실행 가능한 메모리 확보 가능", "T1055 Process Injection (준비 단계)"),
    "VirtualAllocEx": ("다른 프로세스에 메모리 확보", "T1055 Process Injection"),
    "WriteProcessMemory": ("다른 프로세스 메모리에 쓰기", "T1055 Process Injection"),
    "CreateRemoteThread": ("다른 프로세스에서 코드 실행", "T1055 Process Injection"),
    "InternetOpenUrlA": ("인터넷 주소 접속", "T1071.001 Web Protocols"),
    "InternetOpenUrlW": ("인터넷 주소 접속", "T1071.001 Web Protocols"),
    "URLDownloadToFileA": ("파일 내려받기", "T1105 Ingress Tool Transfer"),
    "URLDownloadToFileW": ("파일 내려받기", "T1105 Ingress Tool Transfer"),
    "RegSetValueExA": ("레지스트리 값 쓰기", "T1112 Modify Registry"),
    "RegSetValueExW": ("레지스트리 값 쓰기", "T1112 Modify Registry"),
    "CreateMutexA": ("중복 실행 방지 표시(뮤텍스)", "-"),
    "CreateMutexW": ("중복 실행 방지 표시(뮤텍스)", "-"),
    "CryptEncrypt": ("데이터 암호화", "T1486 Data Encrypted for Impact (랜섬웨어 가능성)"),
    "ShellExecuteA": ("다른 프로그램 실행", "T1106 Native API"),
    "WinExec": ("다른 프로그램 실행", "T1106 Native API"),
}

# ---------------------------------------------------------------- 지표(IOC) 패턴
IOC_PATTERNS = {
    "url": re.compile(r"https?://[A-Za-z0-9.\-]+(?::\d+)?(?:/[^\s\"'<>]*)?"),
    "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}(?::\d{1,5})?\b"),
    "registry": re.compile(r"(?:HKLM|HKCU|HKEY_[A-Z_]+|Software)\\[^\s\"']+", re.I),
    "file_path": re.compile(r"(?:%[A-Z]+%|[A-Z]:)\\[^\s\"'<>|]+\.(?:exe|dll|bat|ps1|vbs|js)", re.I),
    "mutex": re.compile(r"(?:Global|Local)\\[A-Za-z0-9_\-]{4,}"),
    "user_agent": re.compile(r"Mozilla/\d\.\d \([^)]+\)"),
    "base64": re.compile(r"\b[A-Za-z0-9+/]{20,}={0,2}(?![A-Za-z0-9+/])"),
}


def entropy(data):
    """엔트로피: 0(규칙적) ~ 8(완전히 뒤죽박죽). 7.2 이상이면 압축·암호화(패킹) 의심."""
    if not data:
        return 0.0
    counts = Counter(data)
    return -sum(c / len(data) * math.log2(c / len(data)) for c in counts.values())


def extract_strings(data, min_len=5):
    ascii_ = [m.group().decode() for m in re.finditer(rb"[\x20-\x7e]{%d,}" % min_len, data)]
    wide = [m.group().decode("utf-16-le") for m in re.finditer(rb"(?:[\x20-\x7e]\x00){%d,}" % min_len, data)]
    seen, out = set(), []
    for s in ascii_ + wide:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def parse_pe(data):
    """PE(Windows 실행 파일) 머리말·구역·가져오는 함수(import) 읽기."""
    if data[:2] != b"MZ":
        return {"is_pe": False}
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe:pe + 4] != b"PE\x00\x00":
        return {"is_pe": False}
    machine, nsec, ts = struct.unpack_from("<HHI", data, pe + 4)
    opt_size, characteristics = struct.unpack_from("<HH", data, pe + 20)
    opt = pe + 24
    magic = struct.unpack_from("<H", data, opt)[0]
    is64 = magic == 0x20B
    subsystem = struct.unpack_from("<H", data, opt + 68)[0]
    dd = opt + (112 if is64 else 96)
    dirs = [struct.unpack_from("<II", data, dd + 8 * i) for i in range(16)]

    sections = []
    sec_off = opt + opt_size
    for i in range(nsec):
        o = sec_off + 40 * i
        name = data[o:o + 8].rstrip(b"\x00").decode(errors="replace")
        vsize, vaddr, rsize, rptr = struct.unpack_from("<IIII", data, o + 8)
        chars = struct.unpack_from("<I", data, o + 36)[0]
        sections.append({
            "name": name, "virtual_address": vaddr, "virtual_size": vsize,
            "raw_size": rsize, "raw_pointer": rptr,
            "entropy": round(entropy(data[rptr:rptr + rsize]), 2),
            "executable": bool(chars & 0x20000000), "writable": bool(chars & 0x80000000),
        })

    def rva_to_off(rva):
        for s in sections:
            if s["virtual_address"] <= rva < s["virtual_address"] + max(s["virtual_size"], s["raw_size"]):
                return rva - s["virtual_address"] + s["raw_pointer"]
        return None

    def cstr(off):
        end = data.index(b"\x00", off)
        return data[off:end].decode(errors="replace")

    imports = {}
    imp_rva = dirs[1][0]
    off = rva_to_off(imp_rva) if imp_rva else None
    while off is not None:
        oft, _, _, name_rva, ft = struct.unpack_from("<IIIII", data, off)
        if name_rva == 0:
            break
        dll = cstr(rva_to_off(name_rva))
        funcs, t = [], rva_to_off(oft or ft)
        step, flag = (8, 1 << 63) if is64 else (4, 1 << 31)
        while t is not None:
            v = struct.unpack_from("<Q" if is64 else "<I", data, t)[0]
            if v == 0:
                break
            funcs.append(f"#{v & 0xFFFF}" if v & flag else cstr(rva_to_off(v & 0x7FFFFFFF) + 2))
            t += step
        imports[dll] = funcs
        off += 20

    return {
        "is_pe": True,
        "machine": {0x14C: "x86 (32비트)", 0x8664: "x64 (64비트)", 0xAA64: "ARM64"}.get(machine, hex(machine)),
        "compile_time_utc": datetime.fromtimestamp(ts, timezone.utc).isoformat(),
        "is_dll": bool(characteristics & 0x2000),
        "subsystem": {2: "GUI(창 프로그램)", 3: "콘솔(명령창 프로그램)"}.get(subsystem, str(subsystem)),
        "is_dotnet": dirs[14][0] != 0,
        "sections": sections,
        "imports": imports,
    }


def find_iocs(strings):
    found = {k: [] for k in IOC_PATTERNS}
    for s in strings:
        for kind, pat in IOC_PATTERNS.items():
            for m in pat.findall(s):
                if kind == "ipv4":
                    octets = [int(p) for p in m.split(":")[0].split(".")]
                    if not all(0 <= p <= 255 for p in octets):
                        continue
                    # 오탐(잘못 잡음) 거르기: 1.0.0.0 같은 버전 번호, 0.x.x.x
                    if octets[0] == 0 or octets[2:] == [0, 0]:
                        continue
                item = {"value": m}
                if kind == "base64":
                    try:
                        dec = base64.b64decode(m, validate=True)
                        if all(32 <= b < 127 for b in dec):
                            item["decoded"] = dec.decode()
                        else:
                            continue
                    except Exception:
                        continue
                if item not in found[kind]:
                    found[kind].append(item)
    return found


def triage(target, max_bytes=None):
    """파일 하나를 트리아지해서 결과 사전을 돌려줍니다. (다른 프로그램에서 불러 쓰기용)
    max_bytes: 큰 파일은 앞부분만 읽기 (지문은 항상 전체로 계산)"""
    path = Path(target)
    size = path.stat().st_size
    h_md5, h_sha1, h_sha256 = hashlib.md5(), hashlib.sha1(), hashlib.sha256()
    with path.open("rb") as fp:                # 읽기만 함 — 절대 실행하지 않음
        for chunk in iter(lambda: fp.read(1 << 20), b""):
            h_md5.update(chunk)
            h_sha1.update(chunk)
            h_sha256.update(chunk)
    with path.open("rb") as fp:
        data = fp.read(max_bytes) if max_bytes else fp.read()
    try:
        pe = parse_pe(data)
    except (struct.error, ValueError, IndexError):
        pe = {"is_pe": True, "parse_error": "PE 구조가 깨졌거나 잘렸음 (변조·손상 의심)"}
    strings = extract_strings(data)
    all_names = set(strings)
    for funcs in pe.get("imports", {}).values():
        all_names.update(funcs)
    api_hits = [{"api": api, "meaning": desc, "attack": attack}
                for api, (desc, attack) in SUSPICIOUS_APIS.items() if api in all_names]
    return {
        "file": {
            "path": str(target), "name": path.name, "size": size,
            "md5": h_md5.hexdigest(), "sha1": h_sha1.hexdigest(), "sha256": h_sha256.hexdigest(),
            "entropy": round(entropy(data), 2),
            "partial_read": bool(max_bytes and size > max_bytes),
        },
        "pe": pe,
        "suspicious_apis": api_hits,
        "iocs": find_iocs(strings),
        "string_count": len(strings),
    }


def main(target, out_path):
    result = triage(target)
    Path(out_path).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[트리아지] {Path(target).name}: 글자 {result['string_count']}개, "
          f"의심 API {len(result['suspicious_apis'])}개 → {out_path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
