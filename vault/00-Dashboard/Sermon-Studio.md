---
type: dashboard
---
# 🎙️ AI Sermon Studio

**새 설교 시작:** `Templater: Create new note from template` → `T-Sermon-Project`.
단계별 에이전트 프롬프트는 `99-System/Agents/` 에 있으며 Copilot 플러그인의 커스텀 프롬프트 폴더로 지정돼 있습니다.

| 단계 | 폴더 | 담당 에이전트 |
|---|---|---|
| 1 본문 선택 · 2 자료 조사 | Ideas / Research | [[01-Biblical-Researcher]] |
| 3 본문 분석 · 4 해석 검증 | Research | [[02-Original-Language-Analyst]] · [[03-Commentary-Researcher]] · [[04-Theology-Reviewer]] · [[05-Source-Verification]] |
| 5 설교 구조 | Outlines | [[06-Sermon-Architect]] |
| 6 초안 | Drafts | [[07-Sermon-Writer]] |
| 7 비평 | Reviews | [[08-Critical-Reviewer]] |
| 8 퇴고 · 9 최종 | Final | [[09-Final-Editor]] |
| 10 재축적 | 06-LLM-Wiki | 사용자 검토 후 반영 |

## 단계별 설교
```dataview
TABLE rows.file.link AS 설교, rows.passage AS 본문, rows.target_date AS 설교일
FROM "07-Sermon-Studio"
WHERE type = "sermon"
GROUP BY stage
```

설교 스타일 프로필: [[Preacher-Style-Profile]]
