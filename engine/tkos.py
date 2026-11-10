#!/usr/bin/env python3
"""Theology Knowledge OS — Markdown Native 엔진 (표준 라이브러리만 사용)

원칙
- Markdown 파일이 유일한 원본(SSOT). .tkos/index.sqlite 는 언제든 지우고 재생성 가능한 파생 데이터.
- 사용자가 등록한 원본은 바이트 단위로 보존(이동만 하고 내용은 바꾸지 않음).
- AI/시스템이 만든 노트에는 generated_by, review_status 를 기록.
- PDF·DOCX·EPUB·HWP 등 .md 이외 형식은 처리하지 않음.

명령
  ingest      01-Inbox/New-Markdown 의 .md 를 등록 → 원본 보존 + 출처 노트 + 성경 본문 허브 + 인덱스
  index       변경된 Markdown 만 증분 인덱싱 (--rebuild: 인덱스 삭제 후 전체 재구축)
  search      BM25 + 성경 참조 + 메타데이터 필터 검색 (원본 구간·링크 표시)
  check       깨진 링크·고립 문서·중복·출처 없는 AI 문서 점검 → 99-System/Review-Reports 에 리포트
  status      인덱싱 현황 출력
  refs        텍스트에서 성경 참조 추출 테스트
  watch       Inbox 를 주기적으로 감시하며 자동 ingest
"""
import argparse, datetime as dt, hashlib, json, os, re, shutil, sqlite3, sys, time, urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bibleref  # noqa: E402

VERSION = "0.1.0"
SKIP_DIRS = {".obsidian", ".tkos", ".git", ".trash", "node_modules"}
NO_INDEX_PREFIX = ("10-Templates", "99-System/Templates", "01-Inbox")
NO_SEARCH_PREFIX = ("00-Dashboard", "11-Indexes", "99-System")
INBOX = "01-Inbox/New-Markdown"
REVIEW = "01-Inbox/Review-Required"
FAILED = "01-Inbox/Processing-Failed"
ORIG = "90-Sources/Original-Markdown"
SRCNOTES = "06-LLM-Wiki/Source-Notes"
PASSAGES = "02-Bible/Bible-Passages"
MANIFESTS = "90-Sources/Source-Manifests"
REPORTS = "99-System/Review-Reports"


# ---------------------------------------------------------------- utilities
def now():
    return dt.datetime.now().replace(microsecond=0).isoformat()


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def find_vault(start=None):
    p = Path(start or os.environ.get("TKOS_VAULT") or Path.cwd()).expanduser().resolve()
    for c in [p, *p.parents]:
        if (c / "99-System/Configuration/tkos.json").exists():
            return c
    sys.exit(f"[tkos] Vault 를 찾을 수 없습니다: {p}\n  --vault 경로를 지정하거나 TKOS_VAULT 환경변수를 설정하세요.")


def md_files(vault):
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".md"):
                yield Path(root) / f


def rel(vault, p):
    return Path(p).resolve().relative_to(vault).as_posix()


# ---------------------------------------------------------------- frontmatter
_FM = re.compile(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", re.S)


def split_fm(text):
    m = _FM.match(text)
    if not m:
        return {}, text, 0
    return parse_yaml(m.group(1)), text[m.end():], m.group(0).count("\n")


def parse_yaml(src):
    try:
        import yaml  # type: ignore
        d = yaml.safe_load(src)
        return d if isinstance(d, dict) else {}
    except ImportError:
        pass
    except Exception:
        return {}
    data, key, sub = {}, None, None
    for line in src.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        ind = len(line) - len(line.lstrip())
        s = line.strip()
        if s.startswith("- ") and key:
            tgt = data[key] if sub is None else data[key].setdefault(sub, [])
            if not isinstance(tgt, list):
                tgt = []
                if sub is None:
                    data[key] = tgt
                else:
                    data[key][sub] = tgt
            tgt.append(_scalar(s[2:]))
            continue
        if ":" in s:
            k, v = s.split(":", 1)
            k, v = k.strip(), v.strip()
            if ind == 0:
                key, sub = k, None
                data[k] = _scalar(v) if v else None
            elif key:
                if not isinstance(data.get(key), dict):
                    data[key] = {}
                sub = k
                data[key][k] = _scalar(v) if v else None
    for k, v in list(data.items()):
        if v is None:
            data[k] = None
    return data


def _scalar(v):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        return [_scalar(x) for x in v[1:-1].split(",") if x.strip()]
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    return v


def dump_yaml(d):
    lines = []
    for k, v in d.items():
        if isinstance(v, list):
            if not v:
                lines.append(f"{k}: []")
            else:
                lines.append(f"{k}:")
                lines += [f"  - {_q(x)}" for x in v]
        elif isinstance(v, dict):
            lines.append(f"{k}:")
            for k2, v2 in v.items():
                if isinstance(v2, list):
                    lines.append(f"  {k2}:" + ("" if v2 else " []"))
                    lines += [f"    - {_q(x)}" for x in v2]
                else:
                    lines.append(f"  {k2}: {_q(v2)}")
        else:
            lines.append(f"{k}: {_q(v)}")
    return "---\n" + "\n".join(lines) + "\n---\n"


def _q(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    s = str(v)
    if re.fullmatch(r"[A-Za-z0-9가-힣_./-]+", s) and s.lower() not in {"true", "false", "null", "yes", "no"}:
        return s
    return json.dumps(s, ensure_ascii=False)


# ---------------------------------------------------------------- markdown structure
_HEAD = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_WIKI = re.compile(r"(?<!!)\[\[([^\]|#^\\]+)(?:[#^][^\]|]*)?(?:\\?\|[^\]]*)?\]\]")
_CODE = re.compile(r"```.*?```|`[^`\n]*`", re.S)


def wikilinks(text):
    """코드 블록·인라인 코드 안의 예시는 제외하고 실제 링크만 추출."""
    return sorted({m.group(1).strip() for m in _WIKI.finditer(_CODE.sub(" ", text)) if m.group(1).strip() not in ("...", "")})


def sections(body, offset=0):
    """제목 단위로 구조를 보존해 청크를 만든다. (heading, line_start, line_end, text)"""
    out, cur_h, cur, start, fence = [], "", [], 1, False
    lines = body.split("\n")
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            fence = not fence
        m = None if fence else _HEAD.match(line)
        if m:
            if "".join(cur).strip():
                out.append((cur_h, start + offset, i - 1 + offset, "\n".join(cur).strip()))
            cur_h, cur, start = m.group(2), [line], i
        else:
            cur.append(line)
    if "".join(cur).strip():
        out.append((cur_h, start + offset, len(lines) + offset, "\n".join(cur).strip()))
    chunks = []
    for h, a, b, t in out:  # 긴 구간은 문단 단위로 다시 분할
        if len(t) <= 1800:
            chunks.append((h, a, b, t))
            continue
        buf, bstart, ln = [], a, a
        for para in t.split("\n\n"):
            if buf and sum(len(x) for x in buf) + len(para) > 1500:
                chunks.append((h, bstart, ln - 1, "\n\n".join(buf)))
                buf, bstart = [], ln
            buf.append(para)
            ln += para.count("\n") + 2
        if buf:
            chunks.append((h, bstart, b, "\n\n".join(buf)))
    return chunks


def first_title(fm, body, path):
    if fm.get("title"):
        return str(fm["title"])
    for line in body.splitlines():
        m = _HEAD.match(line)
        if m and len(m.group(1)) == 1:
            return m.group(2)
    return Path(path).stem


def anchor(s):
    return re.sub(r"[\[\]|#^]", " ", s).strip()


def safe_name(s, n=80):
    s = re.sub(r'[\\/:*?"<>|#^\[\]]', " ", s)
    return re.sub(r"\s+", " ", s).strip()[:n] or "untitled"


def obsidian_url(vault, relpath):
    return "obsidian://open?vault=" + urllib.parse.quote(vault.name) + "&file=" + urllib.parse.quote(relpath[:-3] if relpath.endswith(".md") else relpath)


# ---------------------------------------------------------------- index (derived data)
def db(vault):
    (vault / ".tkos").mkdir(exist_ok=True)
    con = sqlite3.connect(vault / ".tkos/index.sqlite")
    con.executescript("""
    CREATE TABLE IF NOT EXISTS files(path TEXT PRIMARY KEY, hash TEXT, mtime REAL, id TEXT, type TEXT,
        title TEXT, author TEXT, review_status TEXT, generated INTEGER, refs TEXT, topics TEXT, links TEXT);
    CREATE TABLE IF NOT EXISTS chunks(cid INTEGER PRIMARY KEY, path TEXT, heading TEXT, line_start INT,
        line_end INT, chash TEXT, refs TEXT);
    CREATE TABLE IF NOT EXISTS refs(ref TEXT, path TEXT, cid INT);
    CREATE INDEX IF NOT EXISTS refs_ref ON refs(ref);
    """)
    try:
        con.execute("CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(text, title, heading, tokenize='trigram')")
    except sqlite3.OperationalError:  # 구형 SQLite
        con.execute("CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(text, title, heading, tokenize='unicode61')")
    return con


def index_file(con, vault, p):
    rp = rel(vault, p)
    raw = p.read_bytes()
    h = sha256(raw)
    row = con.execute("SELECT hash FROM files WHERE path=?", (rp,)).fetchone()
    if row and row[0] == h:
        return False
    drop_file(con, rp)
    text = raw.decode("utf-8", "replace")
    fm, body, fm_lines = split_fm(text)
    refs_fm = [str(r) for r in (fm.get("references") or []) if r] if isinstance(fm.get("references"), list) else []
    if fm.get("reference"):
        refs_fm.append(str(fm["reference"]))
    refs_all = list(dict.fromkeys(refs_fm + bibleref.extract(text)))
    topics = fm.get("topics") if isinstance(fm.get("topics"), list) else []
    links = wikilinks(text)
    title = first_title(fm, body, p)
    con.execute("INSERT INTO files VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (
        rp, h, p.stat().st_mtime, str(fm.get("id") or ""), str(fm.get("type") or ""), title,
        str(fm.get("author") or ""), str(fm.get("review_status") or ""), 1 if fm.get("generated_by") else 0,
        json.dumps(refs_all, ensure_ascii=False), json.dumps(topics, ensure_ascii=False),
        json.dumps(links, ensure_ascii=False)))
    for r in refs_fm:
        for pr in bibleref.parent_refs(r):
            con.execute("INSERT INTO refs VALUES(?,?,NULL)", (pr, rp))
    for heading, a, b, t in sections(body, fm_lines):
        crefs = bibleref.extract(t)
        cur = con.execute("INSERT INTO chunks(path,heading,line_start,line_end,chash,refs) VALUES(?,?,?,?,?,?)",
                          (rp, heading, a, b, sha256(t.encode())[:16], json.dumps(crefs)))
        cid = cur.lastrowid
        con.execute("INSERT INTO fts(rowid,text,title,heading) VALUES(?,?,?,?)", (cid, t, title, heading))
        for r in crefs:
            for pr in bibleref.parent_refs(r):
                con.execute("INSERT INTO refs VALUES(?,?,?)", (pr, rp, cid))
    return True


def drop_file(con, rp):
    for (cid,) in con.execute("SELECT cid FROM chunks WHERE path=?", (rp,)).fetchall():
        con.execute("DELETE FROM fts WHERE rowid=?", (cid,))
    for t in ("chunks", "refs", "files"):
        con.execute(f"DELETE FROM {t} WHERE path=?", (rp,))


def indexable(rp):
    return not rp.startswith(NO_INDEX_PREFIX)


def cmd_index(vault, rebuild=False, quiet=False):
    if rebuild:
        shutil.rmtree(vault / ".tkos", ignore_errors=True)
    con = db(vault)
    seen, changed = set(), 0
    for p in md_files(vault):
        rp = rel(vault, p)
        if not indexable(rp):
            continue
        seen.add(rp)
        try:
            changed += index_file(con, vault, p)
        except Exception as e:  # 한 파일의 오류가 전체를 멈추지 않게
            print(f"[warn] {rp}: {e}")
    removed = 0
    for (rp,) in con.execute("SELECT path FROM files").fetchall():
        if rp not in seen:
            drop_file(con, rp)
            removed += 1
    con.commit()
    n = con.execute("SELECT count(*) FROM files").fetchone()[0]
    c = con.execute("SELECT count(*) FROM chunks").fetchone()[0]
    if not quiet:
        print(f"[index] 문서 {n} · 청크 {c} · 갱신 {changed} · 제거 {removed}" + (" (전체 재구축)" if rebuild else ""))
    return changed


# ---------------------------------------------------------------- ingest
def next_id(vault):
    mx = 0
    for p in (vault / SRCNOTES).glob("*.md"):
        m = re.search(r"SRC-(\d{6})", p.name)
        if m:
            mx = max(mx, int(m.group(1)))
    return f"SRC-{mx + 1:06d}"


def known_hashes(vault):
    out = {}
    for p in (vault / SRCNOTES).glob("*.md"):
        fm, _, _ = split_fm(p.read_text("utf-8", "replace"))
        if fm.get("source_hash"):
            out[str(fm["source_hash"])] = p
    return out


def ensure_passage(vault, ref, source_link):
    """성경 본문 허브 노트(시스템 생성). 없을 때만 만들고, 있으면 건드리지 않는다."""
    label = bibleref.korean_label(ref)
    code = ref.split(".")[0]
    book = bibleref.BY_CODE.get(code)
    p = vault / PASSAGES / f"{safe_name(label)}.md"
    if p.exists():
        return label
    fm = {"id": f"BIB-{ref}", "type": "bible-passage", "title": label, "reference": ref,
          "book": book[1] if book else code, "testament": book[5] if book else "",
          "aliases": [ref, f"{book[4]} {ref.split('.', 1)[1].replace('.', ':')}" if book else ref],
          "generated_by": "tkos", "review_status": "auto", "created": now()}
    body = (f"# {label}\n\n> 시스템이 만든 본문 허브 노트입니다. 이 본문을 언급한 자료는 **백링크** 패널과 아래 쿼리에 모입니다.\n\n"
            f"## 이 본문을 다루는 자료\n\n```dataview\nTABLE type, author, review_status\nFROM \"\"\nWHERE contains(references, \"{ref}\") AND file.name != this.file.name\n```\n\n"
            f"## 원어·주석 메모\n\n- \n\n## 교차참조\n\n- \n")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(dump_yaml(fm) + "\n" + body, "utf-8")
    return label


def cmd_ingest(vault, dry=False):
    inbox = vault / INBOX
    files = sorted(x for x in inbox.rglob("*") if x.is_file() and not x.name.startswith(".") and x.name != "README.md")
    if not files:
        print("[ingest] Inbox 가 비어 있습니다:", INBOX)
        return 0
    hashes = known_hashes(vault)
    log, done = [], 0
    for f in files:
        rp_in = rel(vault, f)
        if f.suffix.lower() != ".md":
            log.append(f"- ⛔ `{rp_in}` — .md 가 아닌 파일은 처리하지 않습니다 (Processing-Failed 로 이동)")
            if not dry:
                _move(f, vault / FAILED / f.name)
            continue
        raw = f.read_bytes()
        h = sha256(raw)
        if h in hashes:
            log.append(f"- ♻️ `{rp_in}` — 이미 등록된 자료와 동일(해시 일치): [[{hashes[h].stem}]] → Review-Required 로 이동")
            if not dry:
                _move(f, vault / REVIEW / f.name)
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            log.append(f"- ⛔ `{rp_in}` — UTF-8 이 아닙니다 → Processing-Failed")
            if not dry:
                _move(f, vault / FAILED / f.name)
            continue
        fm, body, fm_lines = split_fm(text)
        sid = str(fm.get("id")) if re.fullmatch(r"SRC-\d{6}", str(fm.get("id") or "")) else next_id(vault)
        title = first_title(fm, body, f)
        orig_rel = f"{ORIG}/{sid}__{safe_name(f.stem, 60)}.md"
        refs = list(dict.fromkeys([str(r) for r in (fm.get("references") or []) if isinstance(fm.get("references"), list)] + bibleref.extract(text)))
        heads = [(m.group(1), m.group(2)) for m in (_HEAD.match(x) for x in body.splitlines()) if m]
        links = wikilinks(text)
        words = len(re.findall(r"\S+", body))
        verified = {k: fm[k] for k in ("author", "type", "language", "license", "citation_key", "theological_tradition", "topics", "category") if fm.get(k)}
        inferred = {}
        if "type" not in verified:
            inferred["type"] = _guess_type(title + " " + rp_in)
        if "language" not in verified:
            inferred["language"] = "ko" if len(re.findall(r"[가-힣]", body)) > len(re.findall(r"[A-Za-z]", body)) / 3 else "en"
        note_name = f"{sid} {safe_name(title, 60)}"
        note = {"id": sid, "type": "source-note", "title": title, "source_id": sid,
                "source_type": verified.get("type") or inferred.get("type"),
                "author": verified.get("author") or "", "language": verified.get("language") or inferred.get("language"),
                "references": refs, "topics": verified.get("topics") or [],
                "source_path": orig_rel, "source_hash": h, "source_words": words,
                "inferred_fields": sorted(inferred.keys()),
                "generated_by": "tkos-ingest", "review_status": "pending", "created": now(), "updated": now()}
        passage_links = []
        if not dry:
            passage_links = [ensure_passage(vault, r, note_name) for r in refs[:60]]
        else:
            passage_links = [bibleref.korean_label(r) for r in refs[:60]]
        out = [f"# {title}", "",
               f"> [!info] 출처 노트 (자동 생성 · 검토 대기)\n> 원본: [[{orig_rel[:-3]}|{sid} 원본 Markdown]] · 해시 `{h[:12]}` · {words} 단어\n"
               f"> 사용자가 확인한 서지 정보는 YAML 에, AI/시스템이 추정한 값은 `inferred_fields` 에 표시됩니다.", "",
               "## 문서 구조 (원본 바로가기)", ""]
        out += [f"{'  ' * (len(lv) - 1)}- [[{orig_rel[:-3]}#{anchor(hd)}|{hd.replace('|', ' ')}]]" for lv, hd in heads] or ["- (제목 없음)"]
        out += ["", "## 성경 참조", ""] + ([f"- [[{lb}]] (`{r}`)" for lb, r in zip(passage_links, refs)] or ["- 없음"])
        out += ["", "## 원본에 있던 링크", ""] + ([f"- [[{l}]]" for l in links] or ["- 없음"])
        out += ["", "## 추정값 (검증 필요)", ""] + ([f"- {k}: {v}" for k, v in inferred.items()] or ["- 없음"])
        out += ["", "## 요약 · 핵심 주장 (LLM Wiki 단계에서 채움)", "", "- ", "",
                "## 검토 기록", "", "- [ ] 서지 정보 확인", "- [ ] 성경 참조 확인", "- [ ] review_status 를 `verified` 로 변경", ""]
        if dry:
            log.append(f"- 🔍 (dry-run) `{rp_in}` → {sid}, 참조 {len(refs)}개")
            continue
        _move(f, vault / orig_rel)  # 원본은 내용 변경 없이 이동만
        np = vault / SRCNOTES / f"{note_name}.md"
        np.parent.mkdir(parents=True, exist_ok=True)
        np.write_text(dump_yaml(note) + "\n" + "\n".join(out), "utf-8")
        hashes[h] = np
        log.append(f"- ✅ `{rp_in}` → [[{note_name}]] · 원본 `{orig_rel}` · 성경 참조 {len(refs)}개")
        done += 1
    if not dry:
        mp = vault / MANIFESTS / f"ingest-{dt.date.today().isoformat()}.md"
        mp.parent.mkdir(parents=True, exist_ok=True)
        head = "" if mp.exists() else dump_yaml({"type": "ingest-log", "generated_by": "tkos", "date": dt.date.today().isoformat()}) + "\n# 인제스트 기록\n"
        with mp.open("a", encoding="utf-8") as fh:
            fh.write(head + f"\n## {now()}\n\n" + "\n".join(log) + "\n")
        cmd_index(vault)
    print("\n".join(log))
    print(f"[ingest] 등록 {done}건")
    return done


def _guess_type(s):
    s = s.lower()
    for k, v in [("설교", "sermon"), ("sermon", "sermon"), ("주석", "bible-commentary"), ("commentary", "bible-commentary"),
                 ("사전", "bible-dictionary"), ("dictionary", "bible-dictionary"), ("lexicon", "lexicon"), ("원어", "word-study"),
                 ("조직신학", "theology-book"), ("theology", "theology-book"), ("논문", "article"), ("article", "article")]:
        if k in s:
            return v
    return "research-note"


def _move(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        dst = dst.with_name(f"{dst.stem}-{int(time.time())}{dst.suffix}")
    shutil.move(str(src), str(dst))


# ---------------------------------------------------------------- search
def cmd_search(vault, q, n=10, ref=None, ftype=None, author=None, as_json=False):
    cmd_index(vault, quiet=True)
    con = db(vault)
    refs = bibleref.normalize_query(ref or "") or bibleref.normalize_query(q)
    scores = {}
    terms = [t for t in re.findall(r"[\w가-힣]+", q) if len(t) >= 3 or re.search(r"[가-힣]{2,}", t)]
    if terms:
        fq = " OR ".join('"' + t.replace('"', "") + '"' for t in terms)
        try:
            for cid, s in con.execute("SELECT rowid, bm25(fts) FROM fts WHERE fts MATCH ? ORDER BY bm25(fts) LIMIT 200", (fq,)):
                scores[cid] = scores.get(cid, 0) + (-s)
        except sqlite3.OperationalError:
            pass
    # 2글자 한국어 등 trigram 미만 질의는 LIKE 로 보완
    for t in re.findall(r"[가-힣]{2}", q):
        if not any(len(x) >= 3 and t in x for x in terms):
            for (cid,) in con.execute("SELECT rowid FROM fts WHERE text LIKE ? LIMIT 200", (f"%{t}%",)):
                scores[cid] = scores.get(cid, 0) + 1.0
    for r in refs:
        for path, cid in con.execute("SELECT path, cid FROM refs WHERE ref=? OR ref LIKE ?", (r, r + "-%")):
            if cid:
                scores[cid] = scores.get(cid, 0) + 10.0
            else:
                for (c2,) in con.execute("SELECT cid FROM chunks WHERE path=? ORDER BY line_start LIMIT 1", (path,)):
                    scores[c2] = scores.get(c2, 0) + 6.0
    best = {}
    for cid, s in sorted(scores.items(), key=lambda x: -x[1]):
        row = con.execute("SELECT c.path, c.heading, c.line_start, c.line_end, c.chash, f.type, f.title, f.author, f.review_status, f.generated "
                          "FROM chunks c JOIN files f USING(path) WHERE c.cid=?", (cid,)).fetchone()
        if not row:
            continue
        path, heading, a, b, chash, typ, title, au, rs, gen = row
        if path.startswith(NO_SEARCH_PREFIX):
            continue
        if ftype and ftype not in (typ or ""):
            continue
        if author and author not in (au or ""):
            continue
        if gen:
            s *= 0.7  # 원본 자료를 AI/시스템 생성 문서보다 우대
        if path in best:  # 같은 문서는 한 번만 (중복 결과 통합)
            best[path]["hits"] += 1
            continue
        text = con.execute("SELECT text FROM fts WHERE rowid=?", (cid,)).fetchone()[0]
        best[path] = dict(score=round(s, 3), path=path, title=title, heading=heading, lines=f"{a}-{b}", chash=chash,
                          type=typ, review_status=rs, generated=bool(gen), hits=1, snippet=_snippet(text, terms, refs),
                          wikilink=f"[[{path[:-3]}#{anchor(heading)}]]" if heading else f"[[{path[:-3]}]]",
                          url=obsidian_url(vault, path))
    # 출처 노트와 그 원본이 함께 잡히면 원본 하나로 통합
    for path in [p for p, r in best.items() if r["type"] == "source-note"]:
        sp = con.execute("SELECT refs FROM files WHERE path=?", (path,)).fetchone()
        fm = split_fm((vault / path).read_text("utf-8", "replace"))[0]
        if str(fm.get("source_path") or "") in best:
            best[str(fm["source_path"])]["source_note"] = f"[[{path[:-3]}]]"
            del best[path]
    res = sorted(best.values(), key=lambda x: -x["score"])[:n]
    if as_json:
        print(json.dumps({"query": q, "refs": refs, "results": res}, ensure_ascii=False, indent=2))
        return res
    print(f"🔎 '{q}'" + (f"  성경참조={', '.join(refs)}" if refs else "") + f"  → {len(res)}건\n")
    for i, r in enumerate(res, 1):
        tag = "AI/시스템" if r["generated"] else "원본"
        print(f"{i}. {r['title']}  [{r['type'] or '-'} · {tag} · {r['review_status'] or '-'}]  score {r['score']}")
        print(f"   {r['path']}  §{r['heading'] or '(머리)'}  L{r['lines']}  #{r['chash']}")
        print(f"   {r['snippet']}")
        print(f"   {r['wikilink']}" + (f"   출처노트 {r['source_note']}" if r.get("source_note") else "") + "\n")
    return res


def _snippet(text, terms, refs, width=160):
    flat = re.sub(r"\s+", " ", text)
    pos = -1
    for t in terms + [bibleref.korean_label(r).split(" ")[0] for r in refs]:
        pos = flat.find(t)
        if pos >= 0:
            break
    pos = max(0, pos - 40)
    return ("…" if pos else "") + flat[pos:pos + width] + ("…" if len(flat) > pos + width else "")


# ---------------------------------------------------------------- integrity check
def cmd_check(vault):
    cmd_index(vault, quiet=True)
    names = {}
    for p in md_files(vault):
        rp = rel(vault, p)
        names.setdefault(p.stem.lower(), rp)
        names.setdefault(rp[:-3].lower(), rp)
        fm, _, _ = split_fm(p.read_text("utf-8", "replace"))
        for a in (fm.get("aliases") or []) if isinstance(fm.get("aliases"), list) else []:
            names.setdefault(str(a).lower(), rp)
    con = db(vault)
    broken, inbound, outbound = [], {}, {}
    for path, links in con.execute("SELECT path, links FROM files"):
        for l in json.loads(links or "[]"):
            key = l.strip().lower()
            key = key[:-3] if key.endswith(".md") else key
            tgt = names.get(key) or names.get(key.split("/")[-1])
            if tgt:
                inbound.setdefault(tgt, set()).add(path)
                outbound.setdefault(path, set()).add(tgt)
            else:
                broken.append((path, l))
    orphans = [p for (p,) in con.execute("SELECT path FROM files") if not p.startswith(("00-", "11-", "99-", "90-Sources/Source-Manifests"))
               and p not in inbound and p not in outbound]
    dups = {}
    for path, h in con.execute("SELECT path, hash FROM files"):
        dups.setdefault(h, []).append(path)
    dups = [v for v in dups.values() if len(v) > 1]
    nosrc = [p for (p,) in con.execute("SELECT path FROM files WHERE generated=1") if p.startswith("06-LLM-Wiki")]
    nosrc = [p for p in nosrc if not split_fm((vault / p).read_text("utf-8", "replace"))[0].get("source_id")
             and not split_fm((vault / p).read_text("utf-8", "replace"))[0].get("sources")]
    hash_bad = []
    for p in (vault / SRCNOTES).glob("*.md"):
        fm, _, _ = split_fm(p.read_text("utf-8", "replace"))
        sp = vault / str(fm.get("source_path") or "")
        if fm.get("source_path") and (not sp.exists() or sha256(sp.read_bytes()) != fm.get("source_hash")):
            hash_bad.append((p.name, str(fm.get("source_path")), "없음" if not sp.exists() else "해시 불일치(원본 변경됨)"))
    rp = vault / REPORTS / f"check-{dt.date.today().isoformat()}.md"
    rp.parent.mkdir(parents=True, exist_ok=True)
    L = [dump_yaml({"type": "review-report", "generated_by": "tkos-check", "created": now()}), f"# 무결성 점검 {now()}", "",
         f"| 항목 | 건수 |\n|---|---|\n| 미생성 링크(생성 후보) | {len(broken)} |\n| 고립 문서 | {len(orphans)} |\n| 중복 문서(동일 해시) | {len(dups)} |\n"
         f"| 출처 없는 AI 문서 | {len(nosrc)} |\n| 원본 해시 불일치 | {len(hash_bad)} |", ""]
    L += ["## 미생성 링크 (개념 노트 생성 후보 · 오타 확인)", ""] + [f"- `{a}` → `[[{b}]]`" for a, b in broken[:300]] + [""]
    L += ["## 고립 문서", ""] + [f"- [[{p[:-3]}]]" for p in orphans[:300]] + [""]
    L += ["## 중복 문서", ""] + [f"- " + " = ".join(f"`{x}`" for x in d) for d in dups] + [""]
    L += ["## 출처 없는 AI 생성 문서", ""] + [f"- [[{p[:-3]}]]" for p in nosrc] + [""]
    L += ["## 원본 해시 불일치", ""] + [f"- {a}: `{b}` ({c})" for a, b, c in hash_bad] + [""]
    rp.write_text("\n".join(L), "utf-8")
    print(f"[check] 미생성링크 {len(broken)} · 고립 {len(orphans)} · 중복 {len(dups)} · 출처없는AI {len(nosrc)} · 해시불일치 {len(hash_bad)}")
    print(f"[check] 리포트: {rel(vault, rp)}")
    return dict(broken=broken, orphans=orphans, dups=dups, nosrc=nosrc, hash_bad=hash_bad)


def cmd_status(vault):
    cmd_index(vault, quiet=True)
    con = db(vault)
    q = lambda s: con.execute(s).fetchone()[0]
    inbox = len([x for x in (vault / INBOX).rglob("*") if x.is_file() and not x.name.startswith(".") and x.name != "README.md"])
    print(f"Theology Knowledge OS v{VERSION}  ·  {vault}")
    print(f"  문서 {q('SELECT count(*) FROM files')} · 청크 {q('SELECT count(*) FROM chunks')} · 성경참조 {q('SELECT count(DISTINCT ref) FROM refs')}종")
    src = q("SELECT count(*) FROM files WHERE type='source-note'")
    pend = q("SELECT count(*) FROM files WHERE review_status='pending'")
    print(f"  출처노트 {src} · 검토대기 {pend} · Inbox 대기 {inbox}")


def cmd_watch(vault, interval):
    print(f"[watch] {INBOX} 감시 중 ({interval}s 간격, Ctrl+C 종료)")
    while True:
        if any(x.is_file() and not x.name.startswith(".") and x.name != "README.md" for x in (vault / INBOX).rglob("*")):
            time.sleep(2)  # 파일 쓰기 완료 대기
            cmd_ingest(vault)
        time.sleep(interval)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="tkos", description="Theology Knowledge OS — Markdown Native 엔진")
    ap.add_argument("--vault", help="Vault 경로 (기본: 현재 폴더 또는 TKOS_VAULT)")
    ap.add_argument("--version", action="version", version=VERSION)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("ingest"); p.add_argument("--dry-run", action="store_true")
    p = sp.add_parser("index"); p.add_argument("--rebuild", action="store_true")
    p = sp.add_parser("search"); p.add_argument("query"); p.add_argument("-n", type=int, default=10)
    p.add_argument("--ref"); p.add_argument("--type"); p.add_argument("--author"); p.add_argument("--json", action="store_true")
    sp.add_parser("check"); sp.add_parser("status")
    p = sp.add_parser("refs"); p.add_argument("text")
    p = sp.add_parser("watch"); p.add_argument("--interval", type=int, default=10)
    a = ap.parse_args(argv)
    if a.cmd == "refs":
        for r in bibleref.extract(a.text):
            print(r, "\t", bibleref.korean_label(r))
        return
    v = find_vault(a.vault)
    if a.cmd == "ingest":
        cmd_ingest(v, a.dry_run)
    elif a.cmd == "index":
        cmd_index(v, a.rebuild)
    elif a.cmd == "search":
        cmd_search(v, a.query, a.n, a.ref, a.type, a.author, a.json)
    elif a.cmd == "check":
        cmd_check(v)
    elif a.cmd == "status":
        cmd_status(v)
    elif a.cmd == "watch":
        cmd_watch(v, a.interval)


if __name__ == "__main__":
    main()
