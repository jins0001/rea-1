"""4단계: output 폴더의 JSON 결과를 읽어서 사람이 보기 쉬운 요약(output/요약.md)을 만듭니다."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
OUT = Path(__file__).resolve().parent.parent / "output"


def load(name):
    path = OUT / f"{name}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return {"_error": path.read_text(encoding="utf-8-sig")[:500]}


lines = ["# REA 실습 결과 요약", ""]

apk = load("01_apk_overview")
if apk and "normalized_result" in apk:
    n = apk["normalized_result"]
    lines += [
        "## 1. 안드로이드 앱 신분증",
        "",
        "| 항목 | 값 |",
        "| --- | --- |",
        f"| 패키지 이름 | `{n.get('package_name')}` |",
        f"| 버전 | {n.get('version_name')} |",
        f"| 최소 안드로이드 버전(SDK) | {n.get('min_sdk')} |",
        f"| 클래스 개수 | {n.get('class_count')} |",
        f"| 리소스 개수 | {n.get('resource_count')} |",
        f"| 요구 권한 수 | {len(n.get('permissions') or [])} |",
        "",
        "요구 권한: " + ", ".join(p.split(".")[-1] for p in n.get("permissions") or []),
        "",
    ]

cls = load("02a_apk_class")
if cls:
    s = json.dumps(cls, ensure_ascii=False)
    lines += ["## 2a. ApiDemos 클래스", "", f"- 결과 크기: {len(s):,} 글자", ""]

method = load("02b_apk_method")
if method:
    n = method.get("normalized_result") or {}
    code = (n.get("source") or {}).get("text")
    lines += [
        "## 2b. onCreate 함수 복원 결과 (JADX)",
        "",
        f"- 함수 모양: `{(n.get('method') or {}).get('reported_signature')}`",
        f"- 복원 상태: {(n.get('source') or {}).get('status')} / 신뢰도: {method.get('confidence')}",
        "",
    ]
    if code:
        lines += ["```java", code.strip()[:3000], "```", ""]
    else:
        lines += ["(코드 필드를 찾지 못함 — output/02b_apk_method.json 직접 확인)", ""]

exe = load("03_exe_overview")
if exe and "normalized_result" in exe:
    n = exe["normalized_result"]
    lines += [
        "## 3. true.exe (Ghidra)",
        "",
        f"- 형식: {exe.get('subject', {}).get('format')} / {exe.get('subject', {}).get('architecture')}",
        "",
        "| 구역 이름 | 시작 주소 | 크기(바이트) |",
        "| --- | --- | --- |",
    ]
    for seg in n.get("segments") or []:
        lines.append(f"| {seg.get('name')} | {seg.get('start')} | {seg.get('length')} |")
    lines.append("")

(OUT / "요약.md").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
