---
type: dashboard
---
# ⚙️ 인덱싱 · 시스템 상태

| 명령 | 하는 일 |
|---|---|
| `tkos ingest` | Inbox 의 .md 등록 → 원본 보존 · 출처 노트 · 본문 허브 · 인덱스 |
| `tkos watch` | Inbox 를 감시하며 자동 등록 |
| `tkos search "질문" [--ref 롬8:28] [--type sermon]` | BM25 + 성경참조 + 메타데이터 검색 |
| `tkos check` | 깨진 링크 · 고립 · 중복 · 출처 없는 AI 문서 · 원본 해시 점검 |
| `tkos index --rebuild` | 인덱스 삭제 후 Markdown 만으로 재구축 |
| `tkos status` | 현황 |

## Inbox 대기
```dataview
LIST FROM "01-Inbox/New-Markdown" WHERE file.name != "README"
```
## 검토 필요 / 처리 실패
```dataview
LIST FROM "01-Inbox/Review-Required" OR "01-Inbox/Processing-Failed"
```
## 인제스트 기록
```dataview
LIST FROM "90-Sources/Source-Manifests" SORT file.name DESC LIMIT 10
```
## 점검 리포트
```dataview
LIST FROM "99-System/Review-Reports" SORT file.name DESC LIMIT 10
```
