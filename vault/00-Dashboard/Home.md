---
type: dashboard
---
# ✝️ Theology Knowledge OS

> Markdown 이 유일한 원본입니다. 새 자료는 `.md` 로 **[[01-Inbox/New-Markdown/README|Inbox]]** 에 넣고 터미널에서 `tkos ingest` 를 실행하세요.

| 연구 | 서재 | 설교 | 시스템 |
|---|---|---|---|
| [[Bible-Research\|📖 성경 연구]] | [[Theology-Library\|📚 신학 서재]] | [[Sermon-Studio\|🎙️ 설교 스튜디오]] | [[Indexing-Status\|⚙️ 인덱싱 상태]] |
| [[Bible-Index\|성경 색인]] | [[Source-Index\|출처 색인]] | [[Sermon-Index\|설교 색인]] | [[Knowledge-Graph\|🕸️ 지식 그래프]] |

## 🆕 최근 등록 자료
```dataview
TABLE source_type AS 유형, author AS 저자, length(references) AS 참조수, review_status AS 상태
FROM "06-LLM-Wiki/Source-Notes"
SORT created DESC
LIMIT 10
```

## 🔍 검토가 필요한 자료
```dataview
LIST
FROM "06-LLM-Wiki" OR "07-Sermon-Studio"
WHERE review_status = "pending"
SORT file.mtime DESC
LIMIT 15
```

## 🎙️ 진행 중인 설교
```dataview
TABLE stage AS 단계, passage AS 본문, target_date AS 설교일
FROM "07-Sermon-Studio"
WHERE type = "sermon" AND stage != "delivered"
SORT target_date ASC
```

## ✍️ 최근 수정한 노트
```dataview
LIST
FROM "" AND -"99-System" AND -"10-Templates"
SORT file.mtime DESC
LIMIT 10
```
