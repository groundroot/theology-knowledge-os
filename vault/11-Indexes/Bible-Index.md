---
type: index
---
# 성경 색인
```dataview
TABLE rows.file.link AS 본문
FROM "02-Bible/Bible-Passages"
GROUP BY testament + " · " + book
```
