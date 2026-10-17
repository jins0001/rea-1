"""다시 만든 성적 계산기 (Python)

원본 소스(1_원본만들기/src)는 보지 않고, 2_분석하기/분석결과.md 만 보고 만들었습니다.
사용법: python grade_calc.py 90 85 77
"""
import sys

FAIL_LINE = 40       # 분석결과: Grade 함수의 숫자 40
PERFECT_LINE = 95    # 분석결과: Grade 함수의 숫자 95


def average(scores):
    # 분석결과: Average 함수에 덧셈(add)과 나눗셈(div) → 합계 ÷ 개수
    return sum(scores) / len(scores)


def letter_for(avg):
    # 분석결과: LetterFor 함수의 숫자 90, 80, 70, 60 과 글자 A, B, C, D, F
    if avg >= 90:
        return "A"
    if avg >= 80:
        return "B"
    if avg >= 70:
        return "C"
    if avg >= 60:
        return "D"
    return "F"


def grade(scores):
    # 분석결과: 숫자 40 다음에 바로 "F" → 과락
    if any(s < FAIL_LINE for s in scores):
        return "F"
    letter = letter_for(average(scores))
    # 분석결과: 숫자 95, 글자 "+", Concat(글자 붙이기)
    if all(s >= PERFECT_LINE for s in scores):
        return letter + "+"
    return letter


def format_one_decimal(x):
    # 분석결과: "average={0:F1}" → 소수점 한 자리
    # [1차 시험에서 발견] 84.25 를 원본은 84.3, Python 기본 f"{x:.1f}" 는 84.2 로 표시.
    # 원본(.NET)은 5에서 올림(반올림), Python 기본은 짝수 쪽으로 맞춤 → 올림 방식으로 고침.
    from decimal import Decimal, ROUND_HALF_UP
    return str(Decimal(repr(x)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def main(args):
    if not args:
        print("usage: GradeCalc.exe score1 score2 ...")
        return 1
    scores = []
    for a in args:
        try:
            v = int(a)
        except ValueError:
            v = -1
        if v < 0 or v > 100:
            print("error: scores must be 0-100")
            return 2
        scores.append(v)
    print(f"average={format_one_decimal(average(scores))} grade={grade(scores)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
