---
type: dashboard
---
# 🕸️ 지식 그래프

- 전체 그래프: 명령 팔레트 → `Graph view: Open graph view` (색상 그룹이 미리 설정돼 있습니다)
- 로컬 그래프: 노트를 연 상태에서 `Graph view: Open local graph`
- ExcaliBrain: 명령 팔레트 → `ExcaliBrain: Open ExcaliBrain`

## 관계 표기 규칙
YAML 에 관계를 적습니다. **근거로 확인된 관계**와 **AI 제안 관계**를 분리합니다.
```yaml
supports: ["[[하나님의 섭리]]"]
contrasts: []
explains: []
cites: []
applied_in: []
related_to: []
suggested_relations: []   # AI 제안(검토 전)
```

## 연결이 가장 많은 개념
```dataview
TABLE length(file.inlinks) AS 백링크
FROM "06-LLM-Wiki" AND -"06-LLM-Wiki/Source-Notes"
SORT length(file.inlinks) DESC
LIMIT 20
```
