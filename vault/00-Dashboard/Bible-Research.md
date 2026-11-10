---
type: dashboard
---
# 📖 성경 연구

**본문 연구 시작:** 명령 팔레트 → `Templater: Create new note from template` → `T-Bible-Passage`.
터미널 검색: `tkos search "롬 8:28"` — 원본 구간·제목·행 범위·링크까지 표시됩니다.

## 본문 허브 (자료가 많이 연결된 순)
```dataview
TABLE book AS 권, reference AS 참조, length(file.inlinks) AS 연결자료
FROM "02-Bible/Bible-Passages"
SORT length(file.inlinks) DESC
LIMIT 30
```

## 원어 연구 노트
```dataview
TABLE lemma, strongs, language
FROM "02-Bible/Original-Languages" OR "03-Biblical-Studies/Word-Studies"
SORT file.mtime DESC
```

## 주석 비교 노트
```dataview
LIST FROM "03-Biblical-Studies/Exegesis" SORT file.mtime DESC
```
