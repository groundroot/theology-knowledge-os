# ✝️ Theology Knowledge OS

**Markdown Native 신학 연구 · 설교 집필 운영체제 — Obsidian × LLM Wiki × Hybrid RAG × AI Sermon Studio**

Markdown(`.md`) 파일만을 유일한 지식 원본(Single Source of Truth)으로 삼는 로컬 우선 신학 연구 환경입니다. 터미널에 한 줄을 붙여 넣으면 Obsidian Vault 구조, 대시보드, 템플릿, 플러그인, 인덱싱 엔진(`tkos`)이 한 번에 설치됩니다.

## 🚀 설치 (터미널에 붙여 넣기)

```bash
curl -fsSL https://raw.githubusercontent.com/groundroot/theology-knowledge-os/main/install.sh | bash
```

예제 자료까지 넣어 바로 체험하려면:

```bash
curl -fsSL https://raw.githubusercontent.com/groundroot/theology-knowledge-os/main/install.sh | bash -s -- --with-samples
```

| 옵션 | 설명 |
|---|---|
| `--vault <경로>` | Vault 위치 (기본 `~/Documents/THEOLOGY-KNOWLEDGE-OS`) |
| `--with-samples` | 예제 Markdown 3개(주석·사전·설교)를 넣고 인제스트까지 실행 |
| `--merge` | 이미 내용이 있는 폴더에 설치 (빠진 파일만 추가, 기존 파일은 덮어쓰지 않음) |
| `--no-plugins` / `--no-open` / `--no-git` | 플러그인 다운로드 / Obsidian 실행 / Git 초기화 생략 |

요구사항: macOS 또는 Linux, `python3`(3.8+), `curl`, [Obsidian](https://obsidian.md). 추가 패키지 설치는 없습니다(엔진은 Python 표준 라이브러리만 사용).

처음 Vault 를 열면 Obsidian 이 **“이 Vault 의 작성자를 신뢰합니까?”** 라고 묻습니다. **Trust author and enable plugins** 를 누르면 플러그인이 켜집니다.

### 안전장치
- 내용이 있는 기존 폴더에는 설치를 거부합니다(`--merge` 를 명시해야 진행, 그때도 기존 파일은 보존).
- 다시 실행해도 사용자가 수정한 문서·설정·플러그인은 덮어쓰지 않습니다.
- Obsidian 등록 시 `obsidian.json` 을 `obsidian.json.tkos-backup` 으로 백업합니다.

## 🧭 사용법

```bash
# 1) 자료 등록: .md 파일을 01-Inbox/New-Markdown 에 넣고
tkos ingest            # 또는 tkos watch (상시 감시)

# 2) 검색: BM25 + 성경 참조 + 메타데이터 필터, 원본 구간·행 범위·링크 표시
tkos search "롬 8:28"
tkos search "섭리 고난" --type bible-commentary
tkos search "예정" --ref "엡 1:4-5" --json

# 3) 점검 · 복구
tkos check             # 미생성 링크 · 고립 문서 · 중복 · 출처 없는 AI 문서 · 원본 해시
tkos index --rebuild   # 인덱스를 지우고 Markdown 만으로 재구축
tkos status
```

`tkos ingest` 가 하는 일:

1. `.md` 이외 파일(PDF·DOCX·EPUB·HWP 등)은 처리하지 않고 `Processing-Failed` 로 이동
2. 내용 해시로 중복 검사 → 이미 등록된 자료는 `Review-Required` 로 이동 (중복 페이지 무한 생성 방지)
3. 원본을 **내용 변경 없이** `90-Sources/Original-Markdown/SRC-000001__파일명.md` 로 이동
4. `06-LLM-Wiki/Source-Notes/` 에 출처 노트 생성 — YAML(ID·해시·참조·주제), 원본의 제목별 바로가기 링크, 사용자 입력값과 추정값 구분(`inferred_fields`), `review_status: pending`
5. 성경 참조를 정규화(`롬 8:28`, `로마서 8장 28절`, `Romans 8:28` → `ROM.8.28`)하고 `02-Bible/Bible-Passages/로마서 8장 28절.md` 같은 본문 허브를 만들어 Wikilink 로 연결 → 그래프·백링크에서 같은 본문을 다룬 주석·사전·설교가 모임
6. 제목 단위 청킹 후 SQLite FTS5(trigram, BM25) 증분 인덱스 갱신, 인제스트 기록을 `90-Sources/Source-Manifests/` 에 Markdown 으로 남김

## 🏛 구조

```
THEOLOGY-KNOWLEDGE-OS/
├── 00-Dashboard/        Home · Bible-Research · Theology-Library · Sermon-Studio · Knowledge-Graph · Indexing-Status
├── 01-Inbox/            New-Markdown · Review-Required · Processing-Failed
├── 02-Bible/            Bible-Passages(자동 본문 허브) · Original-Languages · Cross-References …
├── 03-Biblical-Studies/ Exegesis · Hermeneutics · Word-Studies · Historical-Background · Biblical-Theology
├── 04-Theology/         Systematic · Historical · Practical · Church-History · Ethics · Apologetics
├── 05-Reference-Library/ Commentaries · Dictionaries · Lexicons · Theology-Books · Articles · Bibliographies
├── 06-LLM-Wiki/         Concepts · Doctrines · People · Places · Events · Themes · Source-Notes · Synthesis
├── 07-Sermon-Studio/    Ideas → Research → Outlines → Drafts → Reviews → Final → Delivered
├── 08-Ministry/  09-Research-Projects/  10-Templates/  11-Indexes/
├── 90-Sources/          Original-Markdown(원본 보존) · Source-Manifests · Citation-Records
├── 99-System/           Agents(에이전트 프롬프트 9종) · Documentation · Review-Reports · Configuration
└── .tkos/index.sqlite   파생 데이터 — 삭제해도 `tkos index --rebuild` 로 복구
```

설계 원문: [`docs/MASTER-PROMPT.md`](docs/MASTER-PROMPT.md)

## 🔌 플러그인 (GitHub 최신 릴리스에서 설치)

| 플러그인 | 상태 | 역할 |
|---|---|---|
| Dataview | 활성 | 대시보드·색인 쿼리 |
| Templater | 활성 | `10-Templates` 템플릿 |
| QuickAdd | 활성 | 빠른 노트 생성 |
| Omnisearch | 활성 | Obsidian 내 전문 검색 |
| Obsidian Git | 활성 | Markdown 버전 관리 · 백업 |
| Excalidraw · ExcaliBrain | 활성 | 시각화 · 관계 그래프 탐색 |
| Copilot | 활성 | LLM 채팅, `99-System/Agents` 가 커스텀 프롬프트 폴더 |
| Bible Reference | 활성 | 성경 구절 조회 |
| Linter | **설치만(비활성)** | 저장 시 원본 자동 수정 위험이 있어 필요할 때만 켜기 |

Core 플러그인(Graph, Backlinks, Outgoing Links, Bases, Canvas, Properties, Search, Templates, Bookmarks, Workspaces, File Recovery)은 기본 활성화되며, 그래프 색상 그룹(성경·출처노트·원본·Wiki·설교)이 설정됩니다.

기본 설치에서 제외한 것: **Juggl**(오랫동안 업데이트되지 않음), **K-Plex**, **Bible Verse / Bible Linker / Scripture Linker / YouVersion Linker**(Bible Reference 와 기능 중복, 한국어 번역본 지원·라이선스는 사용자가 직접 확인 후 추가 권장).

## ✅ 구현 상태 (정직하게)

| 영역 | 상태 |
|---|---|
| Markdown 전용 Vault · YAML 표준 · 템플릿 6종 · 대시보드 6종 · 색인 5종 · Bases | ✅ 구현 |
| 자동 인제스트(중복·형식 거부·원본 보존·출처 노트) · `watch` 자동 감시 | ✅ 구현 |
| 성경 66권 한/영 참조 정규화 · 본문 허브 자동 생성 · 자동 Wikilink | ✅ 구현 |
| BM25(FTS5 trigram) + 성경 참조 + 메타데이터 필터 · 출처/원본 결과 통합 | ✅ 구현 |
| 출처 추적: ID · 경로 · 제목 링크 · 행 범위 · 청크 해시 · 원본 해시 검증 | ✅ 구현 |
| 무결성 점검 · 인덱스 재구축 · Git | ✅ 구현 |
| 에이전트 프롬프트 9종(Copilot/외부 LLM 에서 사용) | ✅ 프롬프트 제공 — 자동 실행 파이프라인은 아님 |
| 벡터 임베딩 · 재순위화 (Hybrid RAG 의 의미 검색) | 🔜 로드맵 |
| LLM Wiki 자동 개념 페이지 생성·보강 | 🔜 로드맵 (현재는 Copilot + `T-Wiki-Concept` 템플릿으로 수동) |
| 성경 본문 · 원어 사전 데이터 | ⛔ 저작권 때문에 미포함 — 적법한 자료를 Markdown 으로 넣으면 연결됨 |
| 설교 스타일 자동 학습 · 모델 비용 기록 · NAS 백업 | 🔜 로드맵 |

## 🧪 테스트

```bash
bash tests/run_tests.sh
```

마스터 프롬프트의 필수 시나리오 중 A(인제스트) · B(롬 8:28 검색) · C(그래프 연결) · D(출처 → 원본 문단) · G(새 주석 자동 연결) · H(인덱스 재구축)와 중복 차단·PDF 거부·해시 점검을 자동 검증합니다. E·F(설교 초안·퇴고)는 LLM 이 필요해 자동 테스트 대상이 아닙니다.

## 라이선스

MIT. 예제 문서는 시연용으로 새로 작성한 것입니다.
