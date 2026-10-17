"""REA 결과(result/members.json)와 exe 속 글자를 모아 분석결과.md 를 만듭니다."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
EXE = Path(sys.argv[1])

# 컴퓨터식 자료형 이름 → 쉬운 말
TYPE_WORDS = {
    "i4": "정수", "i4[]": "정수 묶음(배열)", "r8": "실수(소수점 숫자)",
    "string": "글자", "string[]": "글자 묶음(배열)", "void": "없음", "bool": "참/거짓",
}


def word(t):
    return TYPE_WORDS.get(t, t)


def user_strings(path):
    """.NET exe는 코드에 쓴 글자("A", "error..." 등)를 '#US'라는 구역에 모아 둡니다.
    그 구역을 찾아서 {번호표(토큰): 글자} 사전으로 돌려줍니다.
    코드 속 ldstr 명령은 글자 대신 이 번호표(예: 0x70000001)를 가리킵니다."""
    data = path.read_bytes()
    root = data.find(b"BSJB")                      # .NET 정보 구역의 시작 표시
    ver_len = int.from_bytes(data[root + 12:root + 16], "little")
    pos = root + 16 + ver_len + 2
    count = int.from_bytes(data[pos:pos + 2], "little")
    pos += 2
    heap = b""
    for _ in range(count):                         # 구역 목록에서 '#US' 찾기
        off = int.from_bytes(data[pos:pos + 4], "little")
        size = int.from_bytes(data[pos + 4:pos + 8], "little")
        end = data.index(b"\x00", pos + 8)
        name = data[pos + 8:end].decode("ascii")
        pos = (end + 4) & ~3
        if name == "#US":
            heap = data[root + off:root + off + size]
    result, i = {}, 1
    while i < len(heap):                           # [길이][UTF-16 글자][표시 1바이트] 반복
        b = heap[i]
        if b < 0x80:
            length, start = b, i + 1
        else:
            length, start = ((b & 0x3F) << 8) | heap[i + 1], i + 2
        if length == 0:
            break
        result[f"0x{0x70000000 + i:08x}"] = heap[start:start + length - 1].decode("utf-16-le")
        i = start + length
    return result


members = json.loads((HERE / "result" / "members.json").read_text(encoding="utf-8-sig"))
n = members["normalized_result"]
strings = user_strings(EXE)

lines = [
    "# 분석 결과 (exe 파일만 보고 알아낸 것)",
    "",
    f"- 파일: `{EXE.name}` ({n['artifact']['byte_length']:,} 바이트)",
    f"- 지문(SHA-256): `{n['artifact']['sha256'][:16]}...`",
    f"- 종류: .NET 프로그램 (런타임 {n['metadata']['version']})",
    "",
    "## 1. 어떤 묶음(클래스)이 있나",
    "",
]
for t in n["types"]:
    if t["name"] != "<Module>":
        lines.append(f"- `{t['full_name']}` — 함수 {t['method_list']['count']}개, 상수/변수 {t['field_list']['count']}개")

lines += ["", "## 2. 상수(이름 붙은 고정 숫자)", ""]
for f in n["fields"]:
    lines.append(f"- `{f['declaring_type']}.{f['name']}` ({word(f['signature']['field_type'])})")

lines += ["", "## 3. 함수마다 하는 일", ""]
for m in n["methods"]:
    sig = m["signature"]
    params = ", ".join(word(p) for p in sig["parameter_types"])
    nums = [a["operand"] for a in m["body"]["anchors"]
            if a["operand_kind"] == "constant" or a["opcode"] in ("ldc.i4.s", "ldc.r8")]
    texts = [f'"{strings.get(a["operand"], a["operand"])}"'
             for a in m["body"]["anchors"] if a["opcode"] == "ldstr"]
    calls = [e["target_name"] for e in n["call_edges"] if e["caller_token"] == m["token"]]
    ops = m["body"]["opcode_counts"]
    lines += [
        f"### `{m['name']}`",
        "",
        f"- 입력: {params or '없음'} → 출력: {word(sig['return_type'])}",
        f"- 명령어 {m['body']['instruction_count']}개",
        f"- 비교에 쓰는 숫자 (나오는 순서대로): {', '.join(nums) if nums else '없음'}",
        f"- 쓰는 글자 (나오는 순서대로): {', '.join(texts) if texts else '없음'}",
        f"- 부르는 함수: {', '.join(dict.fromkeys(calls)) if calls else '없음'}",
    ]
    if "div" in ops:
        lines.append("- 나눗셈(div)이 있음 → 평균 계산으로 추정")
    if ops.get("ret", 0) >= 3:
        lines.append(f"- 결과를 돌려주는 곳(ret)이 {ops['ret']}군데 → 조건에 따라 일찍 끝나는 길이 여러 개")
    lines.append("")

lines += ["## 4. exe 안에 들어 있는 글자 전체 (#US 구역)", "", "| 번호표 | 글자 |", "| --- | --- |"]
for token, s in strings.items():
    lines.append(f"| `{token}` | `{s}` |")

lines += [
    "",
    "## 5. 추리 (가설)",
    "",
    "| 단서 | 추리 |",
    "| --- | --- |",
    '| `LetterFor`: 숫자 90, 80, 70, 60 / 글자 "A","B","C","D","F" | 평균이 90↑ A, 80↑ B, 70↑ C, 60↑ D, 나머지 F |',
    '| `Grade`: 숫자 40 다음에 바로 "F" | 한 과목이라도 40 미만이면 바로 F (과락) |',
    '| `Grade`: 숫자 95, 글자 "+", `Concat`(글자 붙이기) | 모든 과목이 95 이상이면 등급 뒤에 "+" |',
    "| `Main`: 숫자 100, `TryParse`, 오류 글자 | 입력이 0~100 숫자가 아니면 오류 메시지 |",
    '| `Main`: 글자 "average={0:F1} grade={1}" | 평균은 소수점 한 자리로 출력 |',
    "",
    "> 가설은 3단계에서 **원본 exe와 똑같이 동작하는지 시험**해서 확인합니다.",
]

out = HERE / "분석결과.md"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"보고서 저장: {out}")
