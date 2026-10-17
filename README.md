# rsa 작업 폴더

REA(https://github.com/jins0001/rea) 저장소 공부용 폴더입니다.

```
rea-1/
├── README.md                  ← 지금 이 파일 (폴더 안내)
├── 1_파이썬_콘솔대시보드/        ← [프로젝트 1] 파이썬 실시간 콘솔 대시보드 (CLI, 막대그래프)
│   ├── run.bat / run.ps1      ← 원클릭 실행기
│   ├── src/analyzer.py        ← 메인 분석 스크립트
│   └── docs/                  ← 중학생 눈높이 설명서 (md, html)
├── 2_웹_대시보드/              ← [프로젝트 2] 실시간 로컬 웹 대시보드 (원형 게이지, 다크 네온 UI)
│   ├── run.bat / run.ps1      ← 원클릭 서버 실행 및 브라우저 열기
│   ├── server.py              ← 경량 웹서버 & API
│   ├── public/                ← 프론트엔드 (HTML/CSS/JS)
│   └── docs/                  ← 중학생 눈높이 설명서 (md, html)
├── 3_파워쉘_진단도구/          ← [프로젝트 3] 무설치 순수 PowerShell 진단 도구 + HTML 보고서 생성
│   ├── run.bat / run.ps1      ← 원클릭 진단 실행기
│   ├── Analyze-Hardware.ps1   ← 메인 진단 코드
│   └── docs/                  ← 중학생 눈높이 설명서 (md, html)
├── docs/
│   ├── REA_분석보고서.md       ← 분석 보고서 (마크다운)
│   └── REA_분석보고서.html     ← 분석 보고서 (브라우저로 열기)
├── notes/                     ← 질문과 답변 메모 (Q01, Q02, ...)
├── 작업연습1/                  ← exe만 보고 프로그램 다시 만들기 (원리·구성·프로세스·예시)
│   └── docs/                  ← 작업연습1 정리 (md, html)
├── 작업연습(악성코드분석)/      ← 무해한 훈련용 샘플로 정적 분석 → 보고서·IOC·YARA
├── workspace/                 ← 직접 스크립트 짜서 REA 실행하는 실습 폴더
│   ├── run_all.ps1
│   ├── scripts/
│   └── output/
└── samples/                   ← 연습용 분석 대상 (공개 라이선스 파일만)
    └── ApiDemos-debug.apk     ← Appium 공개 테스트 앱 (Apache 2.0)
```

## 설치된 도구 (2026-10-17)

| 도구 | 위치 |
| --- | --- |
| REA 6.4.0 | `npm install -g rea-agents@6.4.0` |
| Ghidra 12.1.4 | `D:\Tools\ghidra_12.1.4_PUBLIC` |
| jadx-headless-mcp 0.7.1 | `D:\Tools\jadx\` |

자세한 내용: [notes/Q06_Ghidra_JADX_설치와_Ghidra란.md](notes/Q06_Ghidra_JADX_설치와_Ghidra란.md)
