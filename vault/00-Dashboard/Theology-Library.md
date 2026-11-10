---
type: dashboard
---
# 📚 신학 서재

![[Library.base]]

## 자료 유형별
```dataview
TABLE rows.file.link AS 자료
FROM "06-LLM-Wiki/Source-Notes"
GROUP BY source_type
```

## 저자별
```dataview
TABLE rows.file.link AS 자료
FROM "06-LLM-Wiki/Source-Notes"
WHERE author
GROUP BY author
```

## 주제별
```dataview
TABLE rows.file.link AS 자료
FROM "06-LLM-Wiki" OR "05-Reference-Library" OR "04-Theology"
FLATTEN topics AS topic
WHERE topic
GROUP BY topic
```
