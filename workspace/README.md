# workspace — REA 실습 폴더

직접 스크립트를 짜서 REA를 실행해 보는 곳입니다. 분석 대상은 **공개 라이선스 파일**만 씁니다.

```text
workspace/
├── run_all.ps1                 ← 전체 실습 한 번에 실행
├── scripts/
│   ├── 00_env.ps1              ← 공통 설정 (도구 위치, 결과 저장 함수)
│   ├── 01_apk_overview.ps1     ← APK 신분증 보기 (JADX)
│   ├── 02_apk_decompile.ps1    ← APK 함수 하나를 Java 코드로 복원 (JADX)
│   ├── 03_exe_overview.ps1     ← .exe 구조 보기 (Ghidra)
│   └── 04_summarize.py         ← 결과 JSON → 요약.md
└── output/                     ← 실행 결과 (JSON + 요약.md)
```

## 실행 방법

```powershell
powershell -ExecutionPolicy Bypass -File D:\SW\rsa\workspace\run_all.ps1
```

## 분석 대상

| 파일 | 라이선스 | 설명 |
| --- | --- | --- |
| `samples\ApiDemos-debug.apk` | Apache 2.0 | Appium 공개 테스트용 안드로이드 앱 |
| `D:\Tools\Git\usr\bin\true.exe` | GPL | 아무 일도 안 하는 아주 작은 프로그램 |

## 실행 흐름

```text
스크립트(.ps1) ──▶ rea 명령 ──▶ JADX / Ghidra ──▶ output\*.json ──▶ 04_summarize.py ──▶ 요약.md
```

## 참고

- Windows PowerShell 5.1은 BOM 없는 UTF-8 스크립트를 다른 인코딩으로 읽어서 한글이 깨집니다.
  그래서 `.ps1` 파일은 **BOM 있는 UTF-8**로 저장되어 있습니다.
