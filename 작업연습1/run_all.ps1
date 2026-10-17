# 작업연습1 전체 실행: ① 만들기 → ② 분석하기 → ⑤ 시험하기
# (④ 다시 만들기는 사람이 grade_calc.py 를 직접 고치는 단계)
# 4_도전_네이티브 는 1분 정도 걸려서 따로 실행:  .\4_도전_네이티브\run.ps1

Write-Host '===== ① 만들기 ====='
& "$PSScriptRoot\1_원본만들기\build.ps1"
Write-Host ''
Write-Host '===== ② 분석하기 ====='
& "$PSScriptRoot\2_분석하기\analyze.ps1"
Write-Host ''
Write-Host '===== ⑤ 시험하기 ====='
python -I "$PSScriptRoot\3_다시만들기\compare.py"
