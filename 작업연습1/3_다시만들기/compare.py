"""원본 exe 와 다시 만든 grade_calc.py 에 똑같은 입력을 넣고, 출력이 똑같은지 시험합니다."""
import random
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parent / "1_원본만들기" / "bin" / "GradeCalc.exe"
REBUILT = HERE / "grade_calc.py"


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.stdout.strip(), p.returncode


# 시험 문제 만들기: 특별한 경우(경계값) + 무작위 300개
cases = [
    [], ["90"], ["89"], ["60", "59"], ["40", "100"], ["39", "100", "100"],
    ["95", "95"], ["95", "94"], ["100", "100", "100"], ["0"], ["101"], ["-1"], ["abc"],
    ["84", "85"], ["80", "81", "81", "95"],
]
rng = random.Random(2026)
for _ in range(300):
    cases.append([str(rng.randint(30, 100)) for _ in range(rng.randint(1, 6))])

same, diff = 0, []
for args in cases:
    a = run([str(ORIGINAL), *args])
    b = run([sys.executable, "-I", str(REBUILT), *args])
    if a == b:
        same += 1
    else:
        diff.append((args, a, b))

print(f"시험 {len(cases)}개 중 {same}개 일치, {len(diff)}개 불일치")
for args, a, b in diff[:10]:
    print(f"  입력 {' '.join(args)}")
    print(f"    원본     : {a[0]} (종료코드 {a[1]})")
    print(f"    다시 만든 것: {b[0]} (종료코드 {b[1]})")
sys.exit(0 if not diff else 1)
