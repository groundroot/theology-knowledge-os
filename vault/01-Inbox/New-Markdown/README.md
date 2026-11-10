---
type: system
---
# 📥 Inbox — 여기에 .md 파일을 넣으세요

- `.md` 파일만 처리합니다. PDF·DOCX·EPUB·HWP 는 처리하지 않으며 `Processing-Failed` 로 옮겨집니다.
- 넣은 뒤 터미널에서 `tkos ingest` (또는 `tkos watch` 상시 실행).
- 원본은 내용 변경 없이 `90-Sources/Original-Markdown/` 으로 옮겨지고, 출처 노트가 `06-LLM-Wiki/Source-Notes/` 에 생성됩니다.
- YAML 이 있으면 사용자 입력값(검증값)으로, 없으면 추정값으로 기록·구분됩니다.
