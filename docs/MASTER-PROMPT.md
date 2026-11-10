# MASTER PROMPT — Theology Knowledge OS

## Markdown Native LLM Wiki × Obsidian × Hybrid RAG × AI Sermon Studio

> 프롬프트 도우미 권장: 작업 환경 Codex · 코딩·개발 · 추론 수준 매우 깊게
>
> 개선 제안: “기존 설계를 Markdown(.md) 전용 지식관리 시스템으로 재구성하고, PDF 처리 기능을 완전히 제외한 상태에서 LLM Wiki·Obsidian·하이브리드 RAG·Knowledge Graph·AI 설교 집필 기능을 통합하라.”

핵심 변경은 단순히 PDF 지원을 제거하는 것이 아니라, 모든 원본 자료·지식 문서·색인 정보·설교 원고를 `.md` 파일 중심으로 관리하도록 아키텍처를 변경하는 것입니다.

### 0. 역할과 최종 목표

당신은 LLM 지식관리 시스템, Obsidian 플러그인, 하이브리드 검색, Knowledge Graph, 성경 연구 시스템, 신학 문헌 관리 및 AI 설교 집필 시스템을 전문적으로 설계·구현하는 수석 시스템 아키텍트다.

목표는 **오직 Markdown(.md) 파일을 원본 지식 저장 형식으로 사용하는 로컬 우선 AI 신학 연구 운영체제**를 실제 구축하는 것이다.

Obsidian을 핵심 인터페이스로 사용하고 LLM Wiki를 지식 축적 및 연결 엔진으로 통합한다.

Logos Bible Software와 같은 성경 연구 경험을 지향하면서 성경 사전, 주석, 원어 연구, 신학 자료, 과거 설교 및 개인 연구를 연결한다.

최종적으로 다음 워크플로를 지원해야 한다.

**Markdown 자료 등록 → 자동 인덱싱 → 지식 구조화 → 자동 링크 생성 → 그래프 탐색 → 성경 및 신학 연구 → 설교 초안 작성 → 신학적 검증 → 원고 퇴고 → 지식 재축적**

이 프로젝트는 개념 설명이나 설정 제안으로 종료하지 않는다. 실제 설치 권한이 있는 환경에서는 구현과 검증까지 진행한다.

---

### 1. 절대적인 데이터 형식 규칙

시스템의 모든 지식 자료는 Markdown을 기준으로 한다.

#### 필수 규칙

1. 시스템에 등록되는 원본 지식 문서는 `.md` 파일이어야 한다.
2. PDF는 입력, 추출, 인덱싱, 검색, 미리보기 및 원본 연결 대상에서 완전히 제외한다.
3. PDF 파서, OCR 파이프라인, PDF 뷰어 및 PDF 변환 기능을 설치하거나 구현하지 않는다.
4. DOCX, EPUB, HWP 등 다른 파일 형식도 직접 인덱싱하지 않는다.
5. 외부 자료를 사용하려면 사용자가 별도로 Markdown으로 변환해 지정된 Inbox에 등록한 뒤 처리한다.
6. 성경 자료, 신학 문헌, 주석, 사전, 설교, 연구 노트는 모두 Markdown으로 관리한다.
7. AI가 생성하는 Wiki 문서와 설교문 역시 `.md`로 저장한다.
8. 구조화된 문서 정보는 가능한 한 YAML Frontmatter로 기록한다.
9. 문서 간 연결은 Obsidian Wikilink 및 표준 Markdown 링크를 사용한다.
10. 사용자가 작성한 Markdown 원본은 AI가 임의로 덮어쓰거나 삭제하지 않는다.

**Markdown은 지식의 원본이자 최종 저장 형식이다.**

검색 성능을 위한 벡터 인덱스, 캐시, 데이터베이스 및 관계 인덱스는 별도로 사용할 수 있다. 다만 이들은 Markdown 원본에서 재구축 가능한 파생 데이터여야 한다.

시스템의 핵심 지식이 특정 데이터베이스에만 보관되어서는 안 된다.

---

### 2. 시스템 핵심 아키텍처

다음 계층을 구축한다.

**Layer 1 — Markdown Source Repository**

모든 원본 성경 자료, 신학 도서, 주석, 사전, 설교 원고의 Markdown 저장소.

**Layer 2 — Markdown Ingestion Engine**

신규 Markdown 파일 자동 감지, 파싱, 메타데이터 추출, 구조 분석, 중복 확인 및 변경 감지.

**Layer 3 — LLM Wiki Knowledge Engine**

문서 내용을 분석해 개념을 추출하고 지식 페이지를 생성·보강하며 관련 문서 간 연결을 관리한다.

**Layer 4 — Hybrid RAG Search**

BM25, 다국어 임베딩, 메타데이터 검색, 그래프 기반 검색과 재순위화를 결합한다.

**Layer 5 — Knowledge Graph**

성경 본문, 신학 주제, 인물, 사건, 원어, 주석, 사전, 설교 간의 관계를 관리한다.

**Layer 6 — Obsidian Interface**

폴더, Bases, Dataview, 그래프 뷰, 검색, 링크, 템플릿, 대시보드를 통해 전체 지식베이스를 탐색한다.

**Layer 7 — Theology AI Research Agents**

성경 해석, 원어 분석, 주석 비교, 신학 연구, 자료 검증을 담당한다.

**Layer 8 — AI Sermon Studio**

설교 연구, 대지 구성, 초안 작성, 비평, 퇴고 및 최종 원고 저장을 담당한다.

각 계층은 독립적으로 유지보수하고, 모델이나 검색 엔진을 교체하더라도 Markdown 지식베이스가 보존되도록 설계한다.

### 3. LLM Wiki 엔진 선정 및 통합

실제 설치 전에 현재 이용 가능한 LLM Wiki 프로젝트를 조사한다.

최소한 다음 기준을 비교한다.

- Obsidian 통합성
- Markdown 구조 보존
- YAML Properties 지원
- Wikilink 생성 및 수정
- 신규 문서 자동 수집
- 기존 문서와의 관계 추론
- 지식 페이지의 안전한 갱신
- 로컬 LLM 및 클라우드 LLM 지원
- 변경 이력 및 충돌 관리
- 최근 유지보수 상태
- 대량 문서 처리 성능

하나의 LLM Wiki 엔진을 주력으로 사용하며, 기능이 부족한 부분만 독립 모듈로 구현한다.

사용자 연구 노트를 자동 수정하지 않도록 권한을 분리하고 AI 생성 문서에는 별도 표시와 검토 상태를 유지한다.

### 4. Obsidian Vault 구조

다음 구조를 기본으로 구축한다.

```
THEOLOGY-KNOWLEDGE-OS/
│
├── 00-Dashboard/
│   ├── Home.md
│   ├── Bible-Research.md
│   ├── Theology-Library.md
│   ├── Sermon-Studio.md
│   ├── Knowledge-Graph.md
│   └── Indexing-Status.md
│
├── 01-Inbox/
│   ├── New-Markdown/
│   ├── Review-Required/
│   └── Processing-Failed/
│
├── 02-Bible/
│   ├── Old-Testament/
│   ├── New-Testament/
│   ├── Bible-Books/
│   ├── Bible-Passages/
│   ├── Cross-References/
│   └── Original-Languages/
│
├── 03-Biblical-Studies/
│   ├── Exegesis/
│   ├── Hermeneutics/
│   ├── Word-Studies/
│   ├── Historical-Background/
│   └── Biblical-Theology/
│
├── 04-Theology/
│   ├── Systematic-Theology/
│   ├── Historical-Theology/
│   ├── Practical-Theology/
│   ├── Church-History/
│   ├── Ethics/
│   └── Apologetics/
│
├── 05-Reference-Library/
│   ├── Bible-Commentaries/
│   ├── Bible-Dictionaries/
│   ├── Original-Language-Lexicons/
│   ├── Theology-Books/
│   ├── Articles/
│   └── Bibliographies/
│
├── 06-LLM-Wiki/
│   ├── Concepts/
│   ├── Doctrines/
│   ├── People/
│   ├── Places/
│   ├── Events/
│   ├── Themes/
│   ├── Source-Notes/
│   └── Synthesis/
│
├── 07-Sermon-Studio/
│   ├── Ideas/
│   ├── Research/
│   ├── Outlines/
│   ├── Drafts/
│   ├── Reviews/
│   ├── Final/
│   └── Delivered/
│
├── 08-Ministry/
│   ├── Worship/
│   ├── Discipleship/
│   ├── Missions/
│   ├── Education/
│   └── Pastoral-Care/
│
├── 09-Research-Projects/
│
├── 10-Templates/
│
├── 11-Indexes/
│   ├── Bible-Index.md
│   ├── Topic-Index.md
│   ├── Doctrine-Index.md
│   ├── Source-Index.md
│   └── Sermon-Index.md
│
├── 90-Sources/
│   ├── Original-Markdown/
│   ├── Source-Manifests/
│   └── Citation-Records/
│
└── 99-System/
    ├── Documentation/
    ├── Configuration/
    ├── Review-Reports/
    └── Templates/
```

Vault 내부의 지식 문서는 모두 Markdown 형식으로 관리한다.

시스템 운영에 필요한 설정·캐시·로그 파일은 적합한 형식을 사용할 수 있지만 실제 연구 자료와 Wiki 지식의 기준은 Markdown으로 유지한다.

폴더만으로 관계를 표현하지 않는다. YAML, 링크, 태그 및 자동 생성되는 인덱스 문서를 함께 활용한다.

### 5. Markdown 메타데이터 표준

모든 연구 자료에 공통으로 사용할 YAML 스키마를 설계한다.

예시:

```yaml
---
id: SRC-000001
type: bible-commentary
title: "로마서 주석"
author: "저자명"
language: ko
category:
  - 성경주석
  - 바울서신
bible:
  book: Romans
  chapters:
    - 8
references:
  - ROM.8.28
topics:
  - 하나님의 섭리
  - 고난
  - 구원
theological_tradition:
source_id: SRC-000001
source_path:
source_hash:
license:
citation_key:
review_status: pending
created:
updated:
---
```

필드의 자료형과 필수 여부를 정의하고 Obsidian Properties와 일치시킨다.

성경 참조는 고유한 표준 표현으로 정규화한다.

사용자가 별도의 메타데이터를 입력하지 않아도 AI가 초안을 자동 생성하도록 한다. 다만 추론된 값은 검증된 서지 정보와 구분한다.

### 6. Markdown 자동 인덱싱

지정된 Inbox에 `.md` 파일이 추가되면 전체 자동화가 시작되어야 한다.

#### 자동 처리

1. 새로운 Markdown 감지
2. 파일명과 고유 ID 검사
3. YAML Frontmatter 분석
4. Markdown AST 기반 문서 구조 분석
5. 제목·소제목·단락·인용·표·각주 추출
6. 문서 유형 및 신학적 카테고리 분류
7. 성경 참조·학자·주제·원어·교리 추출
8. 내용 기반 중복 및 유사 문서 검사
9. 문서 구조를 보존한 청킹
10. 키워드 및 벡터 인덱스 생성
11. 기존 Wiki와 관련 지식 탐색
12. Wikilink 및 관계 후보 생성
13. 지식 문서 생성 또는 갱신 제안
14. 출처 및 링크 무결성 검사
15. 최종 인덱싱 결과 기록

#### 증분 인덱싱

파일 변경 여부를 해시 또는 변경 이력으로 감지한다.

변경된 영역과 그 영향을 받는 검색 청크·위키·관계 인덱스를 갱신한다.

파일이 이동하거나 이름이 변경되어도 고유 ID를 통해 원본을 추적할 수 있도록 한다.

동일한 자료를 다시 등록하더라도 중복 지식 페이지가 무한히 생성되지 않아야 한다.

### 7. Markdown 원본 추적 시스템

AI가 생성한 모든 지식에는 원본 근거를 기록한다.

추적 단계는 다음과 같다.

**AI 답변 → Wiki 문서 → 출처 노트 → 원본 Markdown → 해당 제목·문단·블록**

Markdown의 다음 요소를 활용한다.

- 문서의 고유 ID
- 파일 경로
- 제목 및 소제목
- Obsidian Block ID
- 문단 위치 및 라인 범위
- 콘텐츠 해시
- 원본 텍스트의 제한된 직접 인용
- Obsidian 링크

예를 들어 AI가 특정 신학자의 견해를 설명하면 사용자가 클릭 한 번으로 실제 Markdown 자료의 해당 단락을 확인할 수 있어야 한다.

Markdown 문서의 행 번호가 수정될 수 있으므로 제목·Block ID·문단 해시를 함께 활용한다.

근거를 확인하지 못한 인용과 AI의 추론은 명시적으로 구분한다.

### 8. Hybrid RAG 검색 엔진

다음 검색 방식을 조합한다.

- **BM25:** 정확한 단어와 문구 검색
- **Vector Search:** 문서의 의미 검색
- **Metadata Filtering:** 성경, 주제, 저자, 자료 유형, 출판연도 필터
- **Graph Search:** 관련 개념과 관계를 따라 탐색
- **Reranking:** 질문과 검색 결과의 관련성을 재평가

한국어, 영어, 히브리어 및 헬라어를 고려한 다국어 검색을 설계한다.

검색 결과는 단순 문서 목록이 아니라 관련 원본의 실제 구간과 출처 링크를 보여줘야 한다.

LLM Wiki가 만든 문서와 원본 Markdown을 모두 검색 대상으로 포함하되, 출처가 반복되어 검색 품질이 저하되지 않도록 중복 결과를 통합한다.

### 9. Knowledge Graph 및 자동 Wikilink

다음 개체를 인식한다.

- 성경 권·장·절
- 인물과 장소
- 사건 및 연대
- 신학적 개념
- 교리
- 성경 원어 단어
- 주석과 사전
- 저자와 신학자
- 설교 원고
- 연구 프로젝트

관계 유형은 `references`, `supports`, `contrasts`, `explains`, `cites`, `related_to`, `applied_in` 등을 사용한다.

연결 예시:

`[[로마서 8장 28절]]` → `[[하나님의 섭리]]` → `[[고난의 신학]]` → `[[로마서 주석 연구]]` → `[[설교 - 모든 것이 합력하여 선을 이룬다]]`

근거에 의해 확인된 관계와 AI가 제안한 관계는 구분한다.

Obsidian Graph View에서 연결 문서를 클릭해 실제 노트로 이동할 수 있어야 한다.

### 10. Obsidian 플러그인 설치

현재 호환성과 유지보수 상태를 조사한 후 기능별로 설치한다.

#### Core 기능

- Graph View
- Backlinks
- Outgoing Links
- Bases
- Canvas
- Properties View
- Search
- Templates
- Bookmarks
- Workspaces
- File Recovery

#### 지식관리 및 자동화

- Dataview
- Templater
- QuickAdd
- Omnisearch
- Obsidian Linter
- Obsidian Git
- 선택한 LLM Wiki 엔진

#### 고급 지식 그래프

- Juggl
- ExcaliBrain
- K-Plex

비교 후 주요 그래프 환경을 선정하고 필요한 기능을 설치한다.

#### 성경 연구

- Bible Reference
- Bible Verse
- Bible Linker
- Scripture Linker
- YouVersion Linker

각 플러그인의 한국어 성경 참조 지원, 로컬 Markdown 연결, 번역본 및 라이선스 제한을 확인한다.

#### 연구 보조

- Copilot
- Excalidraw
- 기타 검증된 Obsidian 연구용 플러그인

설치된 플러그인은 실제 동작 검증을 수행한다.

기능 중복이나 버전 충돌이 있으면 무조건 모두 활성화하지 않고, 호환 가능한 조합을 선정해 제외한 플러그인과 이유를 기록한다.

### 11. 성경·주석·원어 연구 환경

성경 연구용 자료는 Markdown으로 구조화한다.

#### 성경 본문

- 성경 66권 분류
- 권·장·절 단위 참조
- 한국어 및 영어 성경 약칭
- 성경 교차참조
- 관련 주석 및 신학 문서 연결
- 적법하게 제공된 성경 번역본 비교

#### 원어 연구

- 히브리어와 헬라어
- Lemma
- 형태소 및 문법 정보
- Strong's 번호
- 용례 및 문맥적 의미
- 번역 비교

#### 주석 연구

선택된 성경 본문에 관련된 Markdown 주석을 자동으로 수집하고 비교한다.

주석별 해석, 공통 견해, 논쟁점, 신학적 전제, 근거 구절을 구분한다.

원어의 어원만으로 본문 해석을 단정하거나 신학적 결론을 과장하지 않는다.

Logos는 별도 외부 성경 연구 도구로 연결할 수 있지만, 시스템 내부에는 Markdown 기반 지식과 허용된 외부 링크만 보존한다.

### 12. AI Theology Research Agents

다음 전문 에이전트를 구현한다.

1. **Biblical Researcher:** 성경 본문 구조, 문맥 및 역사적 배경 연구
2. **Original Language Analyst:** 원어의 문법·의미·용례 분석
3. **Commentary Researcher:** 주석과 사전 비교
4. **Theology Reviewer:** 조직신학·성경신학적 검토
5. **Source Verification Agent:** 주장과 원본 Markdown 근거 대조
6. **Sermon Architect:** 설교 구조와 논지 설계
7. **Sermon Writer:** 한국어 설교문 초안 작성
8. **Critical Reviewer:** 해석·논리·표현 오류 검토
9. **Final Editor:** 설교자의 문체를 유지하며 최종 원고 퇴고

에이전트 간 결과는 Markdown 형식으로 기록한다.

상충하는 해석이 발견되면 자동으로 하나의 결론으로 통합하지 않고 비교 자료를 제공한다.

### 13. AI Sermon Studio

설교 작업은 다음 단계로 구성한다.

**1단계 — 본문 선택**

성경 본문과 설교 목적, 청중, 예상 시간을 지정한다.

**2단계 — 자료 조사**

관련 성경 사전, 원어 자료, 주석, 신학 문헌, 과거 설교를 검색한다.

**3단계 — 본문 분석**

핵심 주제, 문맥, 구조, 역사적 배경, 원어 및 해석상의 쟁점을 분석한다.

**4단계 — 해석 검증**

대표 해석과 그 근거를 비교하고 본문에 충실한 설명을 정리한다.

**5단계 — 설교 구조**

설교 제목, 중심 명제, 서론, 대지, 전환, 적용, 결론을 구성한다.

**6단계 — 초안 작성**

사용자가 승인한 설교 개요를 바탕으로 Markdown 설교 원고를 작성한다.

**7단계 — 비평**

신학적 정합성, 문맥 왜곡, 인용 오류, 논리 비약, 불필요한 반복을 검토한다.

**8단계 — 퇴고**

자연스러운 한국어 구어체, 문장 리듬, 청중 이해도, 설교자의 문체를 반영한다.

**9단계 — 최종 승인**

최종 원고를 `.md`로 저장하며 이전 버전은 보존한다.

**10단계 — 지식 재축적**

새롭게 생성된 연구와 통찰을 사용자 검토 후 LLM Wiki에 반영한다.

최종 설교와 연구 과정 전체가 Markdown 기반으로 추적 가능해야 한다.

### 14. 개인화된 설교 스타일 학습

사용자가 등록한 기존 Markdown 설교문을 분석해 설교 스타일 프로필을 생성한다.

분석 대상은 문장 구조, 설교 전개, 강조 방식, 질문, 예화, 적용, 결론 및 전체적인 전달 스타일이다.

설교자의 스타일은 별도 Markdown 프로필로 관리한다.

AI가 새로운 원고를 작성할 때 이 프로필을 활용하되, 성경 해석의 정확성과 원본 자료의 신뢰성을 우선한다.

### 15. Obsidian 대시보드

홈 화면은 실제 신학 연구용 작업 공간으로 구성한다.

다음 기능을 제공한다.

- 성경 본문 연구 시작
- 성경 주석 탐색
- 신학 주제별 문서 열람
- 원어 사전 검색
- LLM Wiki 검색
- 최근 등록한 Markdown 문서
- 새로 생성된 지식 연결
- 검증이 필요한 자료
- 진행 중인 설교 프로젝트
- 설교 원고 작성 및 퇴고
- Knowledge Graph
- 인덱싱 및 시스템 상태

Bases와 Dataview를 이용해 성경별·주제별·자료 유형별·저자별 탐색 화면을 구성한다.

### 16. 로컬·클라우드 AI 하이브리드

자료의 원본은 로컬에 유지한다.

문서 분류, 메타데이터 분석, 임베딩, 링크 추천 및 기본 검색은 가능한 한 로컬 모델로 처리한다.

복잡한 신학 연구, 장문 자료 비교 및 설교문 작성은 필요에 따라 클라우드 LLM을 이용한다.

모델별 비용과 사용량을 기록하며 개인정보 또는 비공개 목회 자료의 외부 전송을 기본 차단한다.

클라우드 서비스를 이용할 수 없어도 기존 Markdown 자료 탐색 및 기본적인 로컬 검색은 유지되어야 한다.

### 17. 백업 및 데이터 무결성

다음을 구현한다.

- Git 기반 Markdown 버전 관리
- 정기 백업
- 변경된 문서만 재인덱싱
- 원본 해시 검사
- 깨진 Wikilink 검사
- 고립된 문서 탐색
- 중복 문서 검사
- 출처 없는 AI 생성 내용 검사
- 검색 인덱스 재구축
- NAS 백업 연동
- 복원 테스트

검색 데이터베이스가 삭제되어도 모든 Markdown 원본을 기반으로 인덱스와 관계 그래프를 재생성할 수 있어야 한다.

### 18. 실제 구축 순서

**Phase 1 — 시스템 진단**

개발 환경, Obsidian, 기존 Vault, 저장 공간 및 설치 가능한 플러그인을 조사한다.

**Phase 2 — Markdown Vault 구성**

폴더, 템플릿, YAML 표준, 기본 대시보드를 구축한다.

**Phase 3 — LLM Wiki 설치**

선정된 지식관리 엔진을 설치하고 Markdown 문서 분석 및 갱신 기능을 검증한다.

**Phase 4 — 인덱싱 및 검색**

Markdown 인덱싱, BM25, 임베딩, 메타데이터 검색 및 재순위화를 구현한다.

**Phase 5 — 지식 그래프**

자동 Wikilink, 관계 추출, 그래프 뷰 및 연결 관리 기능을 구축한다.

**Phase 6 — 성경 연구**

성경 참조, 원어, 사전, 주석 및 신학 문헌 탐색 기능을 연결한다.

**Phase 7 — AI 설교 집필**

설교 연구 에이전트, 초안 작성, 비평 및 최종 원고 퇴고 기능을 구현한다.

**Phase 8 — 검증과 최적화**

실제 Markdown 자료로 검색, 인덱싱, 출처 확인, 설교 원고 생성, 백업 복원을 테스트한다.

### 19. 필수 테스트 시나리오

**Test A: 신규 Markdown 인덱싱** — 신학 자료 `.md` 파일을 Inbox에 등록하면 자동 분석·분류·인덱싱이 완료되는지 확인한다.

**Test B: 성경 본문 검색** — 로마서 8장 28절을 검색하면 관련 성경, 신학 개념, 주석 및 이전 설교가 연결되는지 확인한다.

**Test C: Knowledge Graph** — 본문과 관련 신학 문서가 연결되고 Obsidian 그래프에서 실제 탐색 가능한지 확인한다.

**Test D: 출처 검증** — AI가 생성한 신학적 주장에서 실제 Markdown 원본의 해당 문단까지 이동할 수 있는지 확인한다.

**Test E: 설교 초안** — 선택한 본문을 바탕으로 25분 분량의 설교 연구와 초안을 생성한다.

**Test F: 최종 퇴고** — 설교문 검토 및 수정 후 최종 `.md` 파일을 저장하고 이전 초안과 수정 이력을 유지한다.

**Test G: 지식 자동 축적** — 새로운 주석 Markdown이 추가되었을 때 기존 관련 Wiki가 적절하게 보강되는지 확인한다.

**Test H: 시스템 복원** — 검색 인덱스를 재생성해야 하는 상황에서 Markdown 원본만으로 전체 지식베이스를 복구할 수 있는지 확인한다.

### 20. 최종 산출물

1. Markdown Native Obsidian Vault
2. LLM Wiki 엔진 및 통합 설정
3. 자동 Markdown 인덱싱 시스템
4. 하이브리드 RAG 검색 엔진
5. 출처 추적 기능
6. Knowledge Graph 및 자동 Wikilink
7. 카테고리별 자료 탐색 대시보드
8. 성경 연구 및 주석 검색 시스템
9. 원어 연구 기능
10. AI 설교 연구 에이전트
11. 설교 초안·퇴고 시스템
12. 최종 Markdown 설교 원고 템플릿
13. 백업 및 데이터 복원 체계
14. 설치·운영 매뉴얼
15. 기능별 검증 보고서

### 21. 최종 실행 지시

이 프로젝트의 가장 중요한 설계 원칙은 **Markdown이 유일한 지식 원본(Single Source of Truth)** 이라는 것이다.

LLM Wiki, 벡터 데이터베이스, 검색 인덱스, 지식 그래프 및 AI 에이전트는 Markdown 지식베이스를 활용하고 강화하는 보조 시스템으로 구축한다.

PDF 관련 기능은 구현 대상에서 완전히 제외한다.

모든 새 자료는 Markdown으로 등록하고, 인덱싱 후 기존 자료와 연결하며, 이를 Obsidian에서 손쉽게 검색하고 탐색할 수 있도록 한다.

기존의 검증된 오픈소스 도구를 적극적으로 활용하되, 누락된 핵심 기능은 독립 모듈로 개발한다.

기존 Obsidian Vault는 삭제하거나 파괴적으로 변경하지 않는다.

모든 단계에서 실제 동작을 검증하며 성공하지 않은 기능을 완료로 표시하지 않는다.

최종적으로 사용자가 Obsidian을 실행하면 성경 연구, 주석 탐색, 신학 자료 분석, 설교 연구, 설교 원고 작성, 비평 및 최종 탈고까지 하나의 Markdown 중심 환경에서 수행할 수 있어야 한다.

## Markdown 전용 설계의 핵심

```
Markdown 원본 자료 (.md)
  성경 · 사전 · 주석 · 신학 · 설교
        ↓
자동 인덱싱 + LLM Wiki
  메타데이터 · 의미 분석 · 지식 관계 · 원본 위치
        ↓
Obsidian Graph — 지식 연결 및 탐색
        ↓
Hybrid RAG — 검색 및 출처 검증
        ↓
AI Sermon Studio
  본문 연구 → 설교 초안 → 비평 → 탈고 → .md 저장
```

이 구조에서는 Markdown 파일만 잘 보존하면 검색 데이터베이스나 LLM Wiki 엔진을 교체해도 지식 자산을 유지할 수 있습니다. 다만 재구축 시에는 Markdown에 기록된 문서 ID, 출처, 링크 및 검토 상태를 보존하는 것이 중요합니다.
