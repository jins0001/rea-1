# Q6. Ghidra·JADX 설치, 그리고 Ghidra는 뭔가요?

(2026-10-17 설치 및 시험 완료)

## 1. Ghidra(기드라)는 뭔가요?

**미국 국가안보국(NSA)이 만든 "프로그램 해부 현미경"** 입니다.

| 항목 | 내용 |
| --- | --- |
| 만든 곳 | 미국 NSA (National Security Agency, 국가안보국) |
| 공개 | 2019년 무료 공개, GitHub에 소스 코드도 공개 |
| GitHub | <https://github.com/NationalSecurityAgency/ghidra> |
| 만든 언어 | Java (그래서 JDK가 필요) |
| 하는 일 | `.exe` 같은 완성 프로그램(0과 1)을 → 사람이 읽을 수 있는 **어셈블리**와 **C 언어 비슷한 코드(의사 코드)** 로 바꿔 보여 줌 |
| 라이선스 | Apache 2.0 (자유롭게 사용 가능) |

### REA와 비슷한 건가요? → **아니요, 역할이 다릅니다**

| | Ghidra | REA |
| --- | --- | --- |
| 정체 | 분석 도구 **그 자체** | 분석 도구를 **AI에 연결하는 어댑터** |
| 비유 | 🔬 현미경 | 🤖 AI가 현미경을 쓸 수 있게 해 주는 로봇 팔 |
| 누가 씀 | 사람이 직접 화면에서 조작 | AI(Claude Code)가 대신 조작 |
| 만든 곳 | 미국 NSA (정부기관) | 개인 개발자 morluto |
| 관계 | REA가 **안에서 Ghidra를 불러다 씀** | |

> REA 문서에도 "REA는 NSA와 관계없고, NSA가 보증한 것도 아니다"라고 적혀 있습니다.

## 2. 유튜버가 Ghidra 이야기하며 "다른 REA"를 소개한 건가요?

**아니요, 같은 REA입니다.**

- 영상 설명란의 목차: "파트 1 · REA가 어떤 도구이고, **Ghidra·Hopper·IDA 같은 기존 도구와 무엇이 다른지**"
  → Ghidra는 **비교 대상**으로 나온 것이지, 다른 REA가 아닙니다.
- 영상의 실험 자료 페이지가 링크한 저장소: `github.com/morluto/rea` (버전 6.4.0)
  → 내 `jins0001/rea`의 원본과 **같은 저장소**입니다.
- (참고: 영상 화면 자체는 볼 수 없어서, 설명란과 실험 자료 페이지로 확인했습니다.)

## 3. 내 GitHub에 Ghidra 포크

- ✅ 완료: <https://github.com/jins0001/ghidra>
- 원본: `NationalSecurityAgency/ghidra`
- 노트북에는 내려받지 않았습니다(GitHub 계정에 복사만 함).
- ⚠️ 포크는 **소스 코드 복사본**입니다. 실제로 쓰는 Ghidra는 아래처럼 **공식 완성본(zip)** 을 설치했습니다.

## 4. 설치한 것

| 도구 | 위치 | 버전 | 검증 |
| --- | --- | --- | --- |
| Ghidra | `D:\Tools\ghidra_12.1.4_PUBLIC` | 12.1.4 | SHA-256 공식값 일치 ✅ |
| jadx-headless-mcp | `D:\Tools\jadx\jadx-headless-mcp-0.7.1-all.jar` | 0.7.1 | SHA-256 공식값 일치 ✅ |
| REA | `npm install -g rea-agents@6.4.0` | 6.4.0 | `rea --version` ✅ |
| JDK (원래 있던 것) | `C:\Program Files\Eclipse Adoptium\jdk-21...` | 21 | ✅ |

### 바꾼 설정

| 무엇 | 내용 |
| --- | --- |
| Windows 사용자 환경 변수 | `GHIDRA_INSTALL_DIR`, `REA_JADX_MCP_JAR` 추가 |
| Claude Code 설정 | `C:\Users\a\.claude.json`에 `rea` MCP 서버 등록 (백업: `.claude.json.rea.backup`) |
| Claude Code 스킬 | `C:\Users\a\.claude\skills\reverse-engineer-anything` 설치 |

## 5. 시험 결과

| 시험 | 대상 | 결과 |
| --- | --- | --- |
| `rea doctor` | Ghidra·Java·Claude Code 등록·스킬 | ✅ 모두 healthy |
| C/C++ `.exe` 분석 (Ghidra) | `D:\Tools\Git\usr\bin\true.exe` (GPL 공개 소스) | ✅ 26초, x86-64 PE로 인식, 구역(.text, .data 등) 분석 |
| 안드로이드 APK 분석 (JADX) | `samples\ApiDemos-debug.apk` (Appium 공개 테스트 앱, Apache 2.0) | ✅ 9초, 클래스 2,876개, 권한 14개 확인 |

## 6. 사용하려면

1. **VS Code를 완전히 껐다가 다시 켜기** (그래야 새 환경 변수와 REA 등록이 적용됨)
2. Claude Code에게 부탁하기. 예:
   > "D:\SW\rsa\samples\ApiDemos-debug.apk 를 REA로 분석해서 어떤 화면들이 있는지 알려 줘"

## 7. 되돌리고 싶다면

```powershell
npm uninstall --global rea-agents
Copy-Item "$env:USERPROFILE\.claude.json.rea.backup" "$env:USERPROFILE\.claude.json"
Remove-Item -Recurse "$env:USERPROFILE\.claude\skills\reverse-engineer-anything"
[Environment]::SetEnvironmentVariable('GHIDRA_INSTALL_DIR', $null, 'User')
[Environment]::SetEnvironmentVariable('REA_JADX_MCP_JAR', $null, 'User')
Remove-Item -Recurse 'D:\Tools\ghidra_12.1.4_PUBLIC', 'D:\Tools\jadx'
```

> 주의: 백업 파일로 되돌리면 설치 이후에 바뀐 다른 Claude Code 설정도 함께 되돌아갑니다.
