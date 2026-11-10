---
type: index
---
# 설교 색인
```dataview
TABLE passage AS 본문, stage AS 단계, target_date AS 설교일
FROM "07-Sermon-Studio"
WHERE type = "sermon"
SORT target_date DESC
```
