# 작업연습(악성코드분석) — 의심 파일 정적 분석하기

> **목표:** 의심 파일을 **실행하지 않고** 읽기만 해서 ① 정체 ② 흔적(IOC) ③ 위험 기능 ④ 실제 행위 여부를 밝히고, **보고서·IOC 목록·탐지 규칙**까지 만든다.
> **분석 대상:** 직접 만든 **무해한 훈련용 샘플** (악성코드처럼 보이는 흔적만 들어 있고 아무 일도 하지 않음)

---

## 0. ⚠️ 안전 수칙 (먼저 읽기)

| 규칙 | 이유 |
| --- | --- |
| **실제 악성코드는 이 노트북(업무 PC)에 넣지 않는다** | 실수로 실행되면 기관 망 전체가 위험 |
| 실제 샘플은 **격리된 분석용 가상머신**에서만 (네트워크 차단, 스냅샷) | 감염돼도 되돌릴 수 있게 |
| 샘플은 **암호 걸린 zip**(관례상 암호 `infected`) + **확장자 변경**(`.exe` → `.exe_`)으로 보관 | 더블클릭 실행 방지 |
| 이 연습의 도구는 모두 **정적 분석**(읽기만) | REA의 이 명령들과 Ghidra는 대상을 실행하지 않음 |
| 기관 절차 준수 | 침해사고는 기관 보안관제/CERT 및 상급 기관(국가사이버안보센터 등) 보고 체계를 따름 |

---

## 1. 원리 — 실행하지 않고 어떻게 알까?

### 악성코드도 결국 "프로그램"

작업연습1에서 배운 것처럼, exe 안에는 **숫자·글자·함수 이름·명령**이 남습니다. 악성코드도 마찬가지라서, 열어 보면 **범행 흔적**이 보입니다.

| 찾는 것 | 예 | 의미 |
| --- | --- | --- |
| **지문(해시)** | SHA-256 | 파일의 주민번호. 다른 기관과 정보 공유할 때 사용 |
| **흔적(IOC, 침해 지표)** | URL, IP, 레지스트리 경로, 뮤텍스 | 어디로 연락하는지, 어떻게 숨는지 |
| **위험 기능(API)** | `VirtualAlloc`, `InternetOpenUrl` | 무엇을 **할 수 있는지** |
| **실제 호출 관계** | `Main → InternetOpenUrl` | 그 기능을 **진짜 쓰는지** |
| **엔트로피** | 0~8 | 7.2 이상이면 압축·암호화로 숨겼을(패킹) 가능성 |

> **비유:** 수상한 가방 검사. ① 가방 사진(해시) ② 안에 든 쪽지 주소(IOC) ③ 공구 목록(API) ④ 그 공구를 **실제로 쓴 흔적**이 있는지(호출 관계).
> 공구가 들어 있다고 다 범인은 아닙니다. 목수도 망치를 들고 다니니까요.

### 이 연습의 핵심 교훈: "가능성" ≠ "행위"

| | 트리아지(글자 검사)만 | + REA 호출 분석 |
| --- | --- | --- |
| 위험 API | 4개 **있음** | 4개 모두 **호출 없음** (선언만) |
| 판정 | 악성처럼 보임 | "흔적은 많지만 행위 근거 없음" |

---

## 2. 구성

```text
작업연습(악성코드분석)/
├── README.md                     ← 지금 이 안내서
├── run_all.ps1                   ← 전체 실행
├── 1_훈련용샘플/
│   ├── src/TrainingSample.cs     ← 무해한 훈련용 샘플 소스 (흔적만 있음, 위험 함수는 선언만)
│   ├── src/TrainingSample_v2.cs  ← 무해한 함수 1개(IsDebuggerPresent)를 실제로 호출하는 변형
│   ├── build.ps1
│   └── bin/*.exe
├── 2_분석/
│   ├── analyze.ps1               ← 정적 분석 전체 (트리아지 → REA → 보고서)
│   ├── triage.py                 ← 해시·PE 구조·엔트로피·글자·IOC·의심 API (표준 라이브러리만)
│   ├── report.py                 ← 보고서 + IOC CSV + YARA 규칙 생성
│   ├── result/*.json             ← 원본 결과
│   ├── 분석보고서.md              ← ★ 최신 보고서
│   └── 보고서_예시/               ← v1(선언만) / v2(호출 있음) 비교용
└── 3_탐지규칙/
    ├── ioc_list.csv              ← 공유용 IOC 목록 (엑셀로 열림)
    └── training_sample.yar       ← YARA 탐지 규칙 초안
```

| 도구 | 하는 일 |
| --- | --- |
| `triage.py` (직접 작성) | 해시, PE 머리말·구역·엔트로피, import 표, 글자 추출, IOC 패턴, 의심 API → MITRE ATT&CK 매핑 |
| REA `inspect-artifact` | 파일 신분증 |
| REA `inspect-managed-native-boundaries` | .NET이 **선언한** 외부 DLL 함수 목록 |
| REA `inspect-managed-members` | 함수끼리 **실제로 부르는** 관계 |
| REA `inspect-pe-resources` | 아이콘·버전 정보 등 리소스 (숨긴 파일이 있는지) |
| REA `analyze --provider ghidra` | 네이티브(C/C++) 파일일 때 Ghidra 분석 |

---

## 3. 프로세스

```text
 ① 접수·보관      ② 트리아지         ③ 심층 정적 분석      ④ 판정             ⑤ 산출·공유
 해시 기록    →  지문·구조·글자  →  REA: 선언 vs 호출  →  흔적 점수 +   →  보고서, IOC 목록,
 격리 보관        IOC·의심 API       (네이티브: Ghidra)     행위 근거          YARA 규칙
                                                                              │
                                     (실무) 근거 부족하면 → 격리 VM 동적 분석 ◀┘
```

| 단계 | 명령 | 결과물 |
| --- | --- | --- |
| ① 샘플 준비 | `.\1_훈련용샘플\build.ps1` | `bin\TrainingSample.exe` |
| ②~⑤ 분석 전체 | `.\2_분석\analyze.ps1` | `분석보고서.md`, `3_탐지규칙\*` |
| 다른 파일 분석 | `.\2_분석\analyze.ps1 -Target <경로>` | 같음 |

---

## 4. 작업 예시 — 실제 실행 기록 (2026-10-18)

### ② 트리아지 결과

| 종류 | 찾은 값 | 왜 수상한가 |
| --- | --- | --- |
| URL | `http://update-check.training.invalid/beacon.php` | "beacon"(신호) → C2 서버 연락 흉내 |
| IP | `203.0.113.45`, `198.51.100.7:8443` | 하드코딩된 접속 주소 |
| 레지스트리 | `Software\Microsoft\Windows\CurrentVersion\Run` | 부팅 시 자동 실행 → 지속성(T1547.001) |
| 파일 경로 | `%APPDATA%\SysUpdate\svchost_update.exe` | 정상 프로그램 이름 흉내 → 위장(T1036) |
| 뮤텍스 | `Global\TRAINING_SAMPLE_MUTEX_7F3A` | 중복 감염 방지용으로 흔히 씀 |
| Base64 | `VFJBSU5J...` → `TRAINING SAMPLE - NOT MALWARE` | 글자를 숨기는 기법 |
| 의심 API | IsDebuggerPresent, VirtualAlloc, InternetOpenUrlA, RegSetValueExA | 분석 회피, 메모리, 통신, 레지스트리 |

**오탐(잘못 잡음) 경험:** 처음엔 `1.0.0.0`, `0.0.0.0`(버전 번호)을 IP로 잡았습니다 → 거르는 규칙 추가.
**정상 비교:** `true.exe`(정상 프로그램)는 의심 API 0개, IP 0개, 레지스트리 0개. 다만 **URL은 4개** 있었습니다 (`https://www.gnu.org/...` 같은 도움말 주소).
→ URL이 있다고 다 수상한 게 아닙니다. **어떤 주소인지**(공식 사이트 vs `beacon.php`)를 봐야 합니다. 그래서 `true.exe`의 판정은 "낮음"(흔적 2점)입니다.

### ③ REA 심층 분석 — 선언 vs 호출

| 샘플 | 위험 API 선언 | 실제 호출 | 판정 |
| --- | --- | --- | --- |
| v1 `TrainingSample.exe` | 4개 | **0개** (`Main`은 `WriteLine`만 부름) | 의심 — 흔적은 많으나 행위 근거 부족 |
| v2 `TrainingSample_v2.exe` | 4개 | **1개** (`Main → IsDebuggerPresent`) | 악성 의심 높음 — 동적 분석 필요 |

→ 두 보고서를 `2_분석\보고서_예시\` 에서 나란히 비교해 보세요.

### ⑤ 산출물

`3_탐지규칙\training_sample.yar` (YARA = 악성코드 탐지 규칙 표준 언어):

```yara
rule Training_Sample_Indicators
{
    strings:
        $s0 = "http://update-check.training.invalid/beacon.php" ascii wide
        $s1 = "Global\\TRAINING_SAMPLE_MUTEX_7F3A" ascii wide
        ...
    condition:
        uint16(0) == 0x5A4D and 2 of ($s*)    // MZ(실행 파일)이고 흔적 2개 이상
}
```

---

## 5. 한계 (꼭 알아 두기)

| 한계 | 설명 |
| --- | --- |
| 정적 분석만 | 실행 중에 내려받는 코드, 암호를 푼 뒤 나오는 코드는 못 봄 → 실무는 격리 VM 동적 분석 병행 |
| 패킹(압축·암호화) | 진짜 악성코드는 대부분 숨겨져 있어 글자가 안 보임 → 엔트로피로 "숨겼다는 사실"만 알 수 있음 |
| 점수는 연습용 | `IsDebuggerPresent` 하나만으로 "높음"이 되는 등 단순함. 정상 프로그램도 쓰는 API가 많음 |
| .NET은 쉬움, 네이티브는 어려움 | 네이티브는 호출 관계를 Ghidra 의사 코드로 직접 확인해야 함 |
| REA Windows 지원 | 실험 단계. 실제 샘플 분석은 리눅스 분석 VM(REA 기능 더 많음)도 고려 |
| YARA 실행기 미설치 | 규칙 **초안**만 만듦. 실제 검사는 YARA 도구 또는 기관 EDR에 등록 |

---

## 6. 직접 해 보기

```powershell
cd "D:\SW\rsa\작업연습(악성코드분석)"
powershell -ExecutionPolicy Bypass -File .\run_all.ps1
```

### 과제

1. **흔적 추가:** `TrainingSample.cs`의 `Items`에 가짜 주소(`.invalid` 도메인, `203.0.113.x` IP만 사용)를 추가 → 빌드 → 분석 → 보고서와 YARA 규칙에 나오는지 확인
2. **v1 vs v2 비교:** `보고서_예시` 두 파일에서 무엇이 달라졌는지 찾고, 왜 판정이 바뀌었는지 설명하기
3. **오탐 찾기:** `D:\Tools\Git\usr\bin` 안의 다른 정상 프로그램을 `-Target`으로 분석해서, 정상인데 의심 API가 잡히는 경우를 찾아보고 이유 생각하기
4. **AI에게 맡기기:** Claude Code에게 "작업연습(악성코드분석) 훈련용 샘플을 REA로 정적 분석해서 IOC와 ATT&CK 매핑을 정리해 줘"라고 부탁하고, 이 보고서와 비교하기
