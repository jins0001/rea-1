# Q4. 요즘 유튜버들이 말하는 REA는 뭔가요? 이걸로 개발이 가능한가요?

## 1. 같은 것인가요?

**네.** 유튜버·기사들이 말하는 REA는 모두 `github.com/morluto/rea` 하나입니다.
가지고 계신 `jins0001/rea`는 이것을 복사(포크)한 것입니다.

## 2. 왜 갑자기 유명해졌나요?

- 2026년 10월 초, **약 1주일 만에 GitHub 별 11만~14만 개**를 받았습니다 (기사마다 숫자가 다름).
- "소스 코드 없이 앱을 AI가 20분 만에 복사!" 같은 **자극적인 제목**이 많이 퍼졌습니다.
- Claude Code, Codex, Cursor 같은 **AI 코딩 도우미 붐**과 맞물렸습니다.

> 주의: 일부 기사는 REA를 **ArtCraft**(별개 프로젝트, "어도비 대체"로 소개됨)와 헷갈려서 같이 묶어 소개합니다. 둘은 다른 것입니다.
> 또 일부 블로그 글(Apidog 등)은 **광고성(스폰서) 글**입니다.

## 3. REA의 진짜 정체

| 흔한 오해 | 실제 |
| --- | --- |
| "새로운 해킹 기술" | ❌ Ghidra(NSA, 2019), Hopper, IDA 같은 **원래 있던 분석 도구를 AI에 연결**해 주는 "어댑터" |
| "원본 소스 코드를 복원해 줌" | ❌ 원래 변수 이름, 주석, 설계 의도는 **복원 못 함**. 대략적인 모양만 추측 |
| "앱을 그대로 복사" | ❌ AI가 **비슷하게 다시 만드는 것**. 유튜브 실험에서도 100점 중 74점 |
| "REA가 코드를 짜 줌" | ❌ 코드를 짜는 건 **AI 에이전트(Claude Code 등)**. REA는 "조사 보고서"만 넘겨줌 |

## 4. 그럼 개발이 가능한가요?

**네, 가능합니다. 단, REA는 "개발 도구"가 아니라 "개발 전 조사 도구"입니다.**

```
[1단계: 조사]  REA  ──▶ "이 기능은 이렇게 동작한다 + 근거"
[2단계: 개발]  AI 에이전트(Claude Code 등) ──▶ 그 이해를 바탕으로 내 코드 작성
[3단계: 검사]  테스트로 잘 되는지 확인
```

> **비유:** REA는 **"탐정"**, AI 에이전트는 **"요리사"** 입니다.
> 탐정이 "이 요리에는 이런 재료가 이런 순서로 들어간 것 같다"고 알려 주면,
> 요리사가 그걸 보고 **자기 방식으로** 요리를 만듭니다.

### 개발에 쓸 수 있는 경우 ✅
- **내가 만든 옛날 프로그램**인데 소스 코드를 잃어버렸을 때 → 다시 만들기
- **오픈소스 앱**(MIT 등)의 기능이 어떻게 동작하는지 배워서 내 앱에 적용
- 내 프로그램이 **다른 프로그램과 연결**(호환)되도록 필요한 정보 확인
- 보안 공부, CTF, 악성코드 분석

### 쓰면 안 되는 경우 ❌
- 엑셀, 포토샵 같은 **상용 프로그램을 따라 만들기**
- 게임 핵, 정품 인증 뚫기

## 5. 꼭 REA가 필요할까요?

**꼭 그렇지는 않습니다.** MindStudio라는 곳의 실험 결과:
- REA를 써서 맥의 "미리보기" 앱을 다시 만들었더니 꽤 비슷하게 나왔습니다.
- 그런데 **REA 없이** AI가 화면 캡처만 보고 만든 것도 비슷한 수준이었고, **오히려 더 빨랐습니다.**

→ **겉모습(화면, 버튼)** 을 따라 만드는 건 REA 없이도 됩니다.
→ REA는 **겉으로 안 보이는 속 계산**(예: 게임 속 소리·총알 각도 계산)을 알아낼 때 진짜 쓸모가 있습니다.

## 6. 한 줄 정리

> **REA = AI에게 "돋보기"를 쥐여 주는 도구.**
> 개발은 AI 에이전트가 하고, REA는 "어떻게 동작하는지" 알아내는 걸 돕습니다.
> 허락된 대상에만 쓰면 개발에 도움이 되지만, 유튜브 제목처럼 "아무 앱이나 복사"하는 마법 도구는 아닙니다.

## 출처

- [MindStudio – reverse engineer anything mcp](https://www.mindstudio.ai/blog/reverse-engineer-anything-mcp/)
- [Developers Digest – What the MCP Server Does and Where the Line Is](https://www.developersdigest.tech/blog/reverse-engineer-anything-rea-mcp-agents-guide-2026)
- [Kunal Ganglani – REA: Reverse Engineer Anything With AI Agents](https://www.kunalganglani.com/blog/rea-reverse-engineer-anything-agents)
- [Apidog – What Is REA? (스폰서 글)](https://apidog.com/blog/what-is-rea-reverse-engineer-anything/)
- [INSIDE (대만) – REA 기사](https://www.inside.com.tw/article/42615-rea-reverse-engineer-anything-open-source-mcp-ai-agent-github)
- [단테랩스 실험 자료](https://dante-labs.com/blog/rea-clean-room-experiment)
