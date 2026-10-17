"""트리아지 결과 + REA 결과를 합쳐서 분석보고서.md / IOC 목록(csv) / 탐지 규칙(yar)을 만듭니다.

사용법: python -I report.py <result 폴더> <탐지규칙 폴더>
"""
import csv
import json
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
RESULT = Path(sys.argv[1])
RULES = Path(sys.argv[2])
RULES.mkdir(parents=True, exist_ok=True)


def load(name):
    p = RESULT / f"{name}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return None


tri = load("triage_sample")
base = load("triage_baseline")
nb = (load("rea_native_boundaries") or {}).get("normalized_result")
mem = (load("rea_members") or {}).get("normalized_result")
f, pe = tri["file"], tri["pe"]

# ------------------------------------------------ 선언 vs 실제 호출 (REA)
declared = {}
if nb:
    for p in nb.get("pinvoke_imports", []):
        declared[p["member_token"]] = (p["import_scope_name"], p["import_name"])
called_tokens = {e["target_token"] for e in (mem or {}).get("call_edges", [])}
pinvoke_rows = [(dll, api, tok in called_tokens) for tok, (dll, api) in declared.items()]

# ------------------------------------------------ 위험 점수 (설명 가능한 단순 점수)
score, reasons = 0, []


def add(points, why):
    global score
    score += points
    reasons.append((points, why))


iocs = tri["iocs"]
if iocs["url"]:
    add(2, f"URL {len(iocs['url'])}개 포함")
if iocs["ipv4"]:
    add(2, f"IP 주소 {len(iocs['ipv4'])}개 포함")
if any("CurrentVersion\\Run" in r["value"] for r in iocs["registry"]):
    add(3, "자동 실행 레지스트리 경로(Run 키) 포함 — 지속성(T1547.001) 의심")
if iocs["file_path"]:
    add(2, "실행 파일 경로 포함 (특히 svchost 이름 흉내 → 위장 T1036 의심)")
if iocs["mutex"]:
    add(1, "뮤텍스 이름 포함 (중복 감염 방지용으로 자주 쓰임)")
if iocs["base64"]:
    add(1, "Base64로 숨긴 글자 포함")
if tri["suspicious_apis"]:
    add(len(tri["suspicious_apis"]), f"의심 API {len(tri['suspicious_apis'])}개 이름 존재")
high_entropy = [s for s in pe.get("sections", []) if s["entropy"] >= 7.2]
if high_entropy:
    add(3, "엔트로피 7.2 이상 구역 존재 — 패킹/암호화 의심")

# 판정은 두 축으로: ① 흔적 점수(글자·이름) ② 실제 행위 근거(REA 호출 분석)
called_any = any(c for _, _, c in pinvoke_rows)
if not pinvoke_rows:
    behavior = "확인 불가 (호출 분석 결과 없음)"
elif called_any:
    behavior = "있음 — 위험 API를 실제로 호출함"
else:
    behavior = "없음 — 위험 API를 선언만 하고 어디에서도 호출하지 않음"

if score >= 10 and called_any:
    verdict = "악성 의심 높음 — 격리 환경에서 동적 분석 필요"
elif score >= 5:
    verdict = "의심 — 흔적은 많으나 실제 행위 근거 부족, 추가 분석 필요" if not called_any else "악성 의심"
else:
    verdict = "낮음"

# ------------------------------------------------ IOC 목록 (공유용 CSV)
with open(RULES / "ioc_list.csv", "w", newline="", encoding="utf-8-sig") as fp:
    w = csv.writer(fp)
    w.writerow(["type", "value", "note"])
    w.writerow(["sha256", f["sha256"], f["name"]])
    w.writerow(["md5", f["md5"], f["name"]])
    for kind, items in iocs.items():
        for it in items:
            w.writerow([kind, it["value"], it.get("decoded", "")])

# ------------------------------------------------ YARA 탐지 규칙 초안
yara_strings = []
for i, it in enumerate(iocs["url"] + iocs["mutex"] + iocs["file_path"] + iocs["user_agent"]):
    v = it["value"].replace("\\", "\\\\").replace('"', '\\"')
    yara_strings.append(f'        $s{i} = "{v}" ascii wide')
yara = f"""rule Training_Sample_Indicators
{{
    meta:
        description = "훈련용 샘플 탐지 규칙 (연습용 초안)"
        sha256 = "{f['sha256']}"
        date = "{date.today().isoformat()}"
    strings:
{chr(10).join(yara_strings)}
    condition:
        uint16(0) == 0x5A4D and 2 of ($s*)
}}
"""
(RULES / "training_sample.yar").write_text(yara, encoding="utf-8")

# ------------------------------------------------ 보고서
L = [
    "# 악성코드 정적 분석 보고서 (훈련)",
    "",
    f"- 작성일: {date.today().isoformat()}",
    "- 분석 방식: **정적 분석** (파일을 실행하지 않고 읽기만 함)",
    "- 도구: 자체 트리아지 스크립트(triage.py), REA 6.4.0",
    "",
    "## 1. 요약",
    "",
    "| 항목 | 내용 |",
    "| --- | --- |",
    f"| 파일 이름 | `{f['name']}` |",
    f"| 판정 | **{verdict}** |",
    f"| ① 흔적 점수 | {score}점 (10점 이상 = 많음) |",
    f"| ② 실제 행위 근거 | {behavior} |",
    "",
    "## 2. 파일 정보",
    "",
    "| 항목 | 값 |",
    "| --- | --- |",
    f"| 크기 | {f['size']:,} 바이트 |",
    f"| MD5 | `{f['md5']}` |",
    f"| SHA-1 | `{f['sha1']}` |",
    f"| SHA-256 | `{f['sha256']}` |",
    f"| 종류 | PE, {pe.get('machine')}, {pe.get('subsystem')}, {'.NET' if pe.get('is_dotnet') else '네이티브'} |",
    f"| 컴파일 시각(UTC) | {pe.get('compile_time_utc')} |",
    f"| 전체 엔트로피 | {f['entropy']} / 8 |",
    "",
    "### 구역(섹션)",
    "",
    "| 이름 | 크기 | 엔트로피 | 실행 | 쓰기 |",
    "| --- | --- | --- | --- | --- |",
]
for s in pe.get("sections", []):
    L.append(f"| {s['name']} | {s['raw_size']} | {s['entropy']} | {'O' if s['executable'] else ''} | {'O' if s['writable'] else ''} |")

L += ["", "## 3. 침해 지표 (IOC)", "", "| 종류 | 값 | 비고 |", "| --- | --- | --- |"]
names = {"url": "URL", "ipv4": "IP", "registry": "레지스트리", "file_path": "파일 경로",
         "mutex": "뮤텍스", "user_agent": "User-Agent", "base64": "Base64"}
for kind, items in iocs.items():
    for it in items:
        L.append(f"| {names[kind]} | `{it['value']}` | {it.get('decoded', '')} |")

L += ["", "## 4. 의심 기능 (API 이름 기준)", "", "| API | 의미 | MITRE ATT&CK |", "| --- | --- | --- |"]
for a in tri["suspicious_apis"]:
    L.append(f"| `{a['api']}` | {a['meaning']} | {a['attack']} |")

L += ["", "## 5. 선언 vs 실제 호출 (REA 분석)", "",
      "| DLL | 함수 | 실제 호출 |", "| --- | --- | --- |"]
for dll, api, called in pinvoke_rows:
    L.append(f"| {dll} | `{api}` | {'⚠️ 호출함' if called else '❌ 호출 없음 (선언만)'} |")
if mem:
    L += ["", "실제 호출 관계:", ""]
    for e in mem["call_edges"]:
        L.append(f"- `{e['caller']}` → `{e['target_name']}`")

L += ["", "## 6. 흔적 점수 근거", "", "| 점수 | 이유 |", "| --- | --- |"]
for p, why in reasons:
    L.append(f"| {p:+d} | {why} |")

if base:
    L += ["", "## 7. 정상 프로그램과 비교", "", "| 항목 | 분석 대상 | 정상 비교(true.exe) |", "| --- | --- | --- |",
          f"| 의심 API | {len(tri['suspicious_apis'])}개 | {len(base['suspicious_apis'])}개 |",
          f"| URL / IP | {len(iocs['url'])} / {len(iocs['ipv4'])} | {len(base['iocs']['url'])} / {len(base['iocs']['ipv4'])} |",
          f"| 레지스트리 경로 | {len(iocs['registry'])} | {len(base['iocs']['registry'])} |"]

called_names = [api for _, api, c in pinvoke_rows if c]
if called_any:
    behavior_line = (f"- REA 호출 분석 결과 위험 API **{', '.join(called_names)}** 를 실제로 호출합니다. "
                     "단, 정상 프로그램도 쓰는 함수일 수 있으므로 호출 목적을 의사 코드로 확인해야 합니다.")
elif pinvoke_rows:
    behavior_line = "- 그러나 REA 호출 분석 결과 위험 API는 **선언만 되고 호출되지 않아**, 정적 분석만으로는 실제 악성 행위 근거가 없습니다."
else:
    behavior_line = "- 호출 관계를 확인하지 못했습니다(네이티브 파일). Ghidra 의사 코드로 위험 API 사용 위치를 확인해야 합니다."
L += ["", "## 8. 결론 및 권고", "",
      "- 파일 안에 C2 주소, 자동 실행 경로, 위장 파일명 등 **악성코드에서 흔한 흔적이 다수** 있습니다." if score >= 5
      else "- 악성코드에서 흔한 흔적이 거의 없습니다.",
      behavior_line,
      "- 실제 업무라면: ① 격리 가상머신에서 동적 분석 ② 산출된 IOC를 보안장비(방화벽·EDR)에 검색 ③ YARA 규칙으로 다른 PC 탐색",
      "",
      "## 9. 산출물", "",
      "- IOC 목록: `3_탐지규칙/ioc_list.csv`",
      "- 탐지 규칙 초안: `3_탐지규칙/training_sample.yar`",
      "- 원본 결과: `2_분석/result/*.json`",
      ]

out = RESULT.parent / "분석보고서.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"[보고서] 판정: {verdict} (흔적 {score}점, 행위 근거: {behavior}) → {out}")
