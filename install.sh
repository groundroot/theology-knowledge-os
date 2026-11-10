#!/usr/bin/env bash
# Theology Knowledge OS — 원라인 설치
#   curl -fsSL https://raw.githubusercontent.com/groundroot/theology-knowledge-os/main/install.sh | bash
# 옵션 (bash -s -- 뒤에):
#   --vault <경로>    Vault 위치 (기본 ~/Documents/THEOLOGY-KNOWLEDGE-OS)
#   --with-samples    예제 Markdown 3개를 넣고 인제스트까지 실행
#   --merge           기존 폴더가 있어도 진행 (없는 파일만 추가, 기존 파일은 절대 덮어쓰지 않음)
#   --no-plugins      커뮤니티 플러그인 다운로드 생략
#   --no-open         설치 후 Obsidian 실행 생략
#   --no-git          Vault 의 Git 초기화 생략
set -euo pipefail

REPO="groundroot/theology-knowledge-os"
BRANCH="${TKOS_BRANCH:-main}"
VAULT="${HOME}/Documents/THEOLOGY-KNOWLEDGE-OS"
SAMPLES=0; MERGE=0; PLUGINS=1; OPEN=1; GIT=1
while [ $# -gt 0 ]; do
  case "$1" in
    --vault) VAULT="$2"; shift 2;;
    --with-samples) SAMPLES=1; shift;;
    --merge) MERGE=1; shift;;
    --no-plugins) PLUGINS=0; shift;;
    --no-open) OPEN=0; shift;;
    --no-git) GIT=0; shift;;
    -h|--help) sed -n '2,12p' "$0" 2>/dev/null || true; exit 0;;
    *) echo "알 수 없는 옵션: $1"; exit 1;;
  esac
done
VAULT="${VAULT/#\~/$HOME}"

c(){ printf "\033[1;36m▸ %s\033[0m\n" "$*"; }
ok(){ printf "  \033[32m✔\033[0m %s\n" "$*"; }
warn(){ printf "  \033[33m!\033[0m %s\n" "$*"; }
die(){ printf "\033[31m✖ %s\033[0m\n" "$*"; exit 1; }

c "Theology Knowledge OS 설치 → $VAULT"
for b in curl python3 tar; do command -v "$b" >/dev/null || die "$b 이(가) 필요합니다."; done
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)' || die "Python 3.8 이상이 필요합니다."

# ---- 기존 Vault 보호
MARKER="$VAULT/99-System/Configuration/tkos.json"
if [ -d "$VAULT" ] && [ -n "$(ls -A "$VAULT" 2>/dev/null)" ] && [ ! -f "$MARKER" ] && [ "$MERGE" -eq 0 ]; then
  die "이미 내용이 있는 폴더입니다: $VAULT
   기존 Vault 를 보호하기 위해 중단합니다. 다른 --vault 경로를 쓰거나,
   기존 파일은 그대로 두고 빠진 것만 추가하려면 --merge 를 붙이세요."
fi

# ---- 소스 준비 (TKOS_SRC 가 있으면 로컬 소스 사용)
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
if [ -n "${TKOS_SRC:-}" ]; then
  SRC="$TKOS_SRC"
else
  curl -fsSL "https://codeload.github.com/$REPO/tar.gz/refs/heads/$BRANCH" | tar -xz -C "$TMP"
  SRC="$(find "$TMP" -maxdepth 1 -mindepth 1 -type d | head -1)"
fi
[ -f "$SRC/engine/tkos.py" ] || die "소스를 내려받지 못했습니다."
ok "소스 준비"

# ---- 폴더 구조
c "Vault 폴더 구성"
DIRS="00-Dashboard
01-Inbox/New-Markdown 01-Inbox/Review-Required 01-Inbox/Processing-Failed
02-Bible/Old-Testament 02-Bible/New-Testament 02-Bible/Bible-Books 02-Bible/Bible-Passages 02-Bible/Cross-References 02-Bible/Original-Languages
03-Biblical-Studies/Exegesis 03-Biblical-Studies/Hermeneutics 03-Biblical-Studies/Word-Studies 03-Biblical-Studies/Historical-Background 03-Biblical-Studies/Biblical-Theology
04-Theology/Systematic-Theology 04-Theology/Historical-Theology 04-Theology/Practical-Theology 04-Theology/Church-History 04-Theology/Ethics 04-Theology/Apologetics
05-Reference-Library/Bible-Commentaries 05-Reference-Library/Bible-Dictionaries 05-Reference-Library/Original-Language-Lexicons 05-Reference-Library/Theology-Books 05-Reference-Library/Articles 05-Reference-Library/Bibliographies
06-LLM-Wiki/Concepts 06-LLM-Wiki/Doctrines 06-LLM-Wiki/People 06-LLM-Wiki/Places 06-LLM-Wiki/Events 06-LLM-Wiki/Themes 06-LLM-Wiki/Source-Notes 06-LLM-Wiki/Synthesis
07-Sermon-Studio/Ideas 07-Sermon-Studio/Research 07-Sermon-Studio/Outlines 07-Sermon-Studio/Drafts 07-Sermon-Studio/Reviews 07-Sermon-Studio/Final 07-Sermon-Studio/Delivered
08-Ministry/Worship 08-Ministry/Discipleship 08-Ministry/Missions 08-Ministry/Education 08-Ministry/Pastoral-Care
09-Research-Projects 10-Templates 11-Indexes
90-Sources/Original-Markdown 90-Sources/Source-Manifests 90-Sources/Citation-Records
99-System/Documentation 99-System/Configuration 99-System/Review-Reports 99-System/Templates 99-System/Agents
.obsidian/plugins"
for d in $DIRS; do mkdir -p "$VAULT/$d"; done

# 파일 복사: 이미 있는 파일은 절대 덮어쓰지 않음
python3 - "$SRC/vault" "$VAULT" <<'PY'
import os, shutil, sys
src, dst = sys.argv[1], sys.argv[2]
added = kept = 0
for root, _, files in os.walk(src):
    for f in files:
        s = os.path.join(root, f); d = os.path.join(dst, os.path.relpath(s, src))
        os.makedirs(os.path.dirname(d), exist_ok=True)
        if os.path.exists(d): kept += 1; continue
        shutil.copy2(s, d); added += 1
print(f"  \033[32m✔\033[0m 문서 {added}개 추가, 기존 {kept}개 보존")
PY
cp -n "$SRC/docs/"*.md "$VAULT/99-System/Documentation/" 2>/dev/null || true

# ---- Obsidian 설정 (없을 때만 생성)
c "Obsidian 설정"
python3 - "$VAULT" <<'PY'
import json, os, sys
v = sys.argv[1]; o = os.path.join(v, ".obsidian")
def put(name, data):
    p = os.path.join(o, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if os.path.exists(p): print(f"  - {name} 이미 있음(보존)"); return
    json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2); print(f"  \033[32m✔\033[0m {name}")
put("app.json", {"newFileLocation": "folder", "newFileFolderPath": "01-Inbox/New-Markdown",
    "useMarkdownLinks": False, "newLinkFormat": "shortest", "alwaysUpdateLinks": True,
    "showFrontmatter": True, "propertiesInDocument": "visible", "attachmentFolderPath": "99-System/Attachments"})
put("core-plugins.json", {k: True for k in ["file-explorer","global-search","switcher","graph","backlink","canvas",
    "outgoing-link","tag-pane","properties","page-preview","templates","note-composer","command-palette",
    "editor-status","bookmarks","outline","word-count","file-recovery","workspaces","bases"]})
put("templates.json", {"folder": "10-Templates", "dateFormat": "YYYY-MM-DD"})
put("graph.json", {"colorGroups": [
    {"query": "path:02-Bible", "color": {"a": 1, "rgb": 14701138}},
    {"query": "path:06-LLM-Wiki/Source-Notes", "color": {"a": 1, "rgb": 5431378}},
    {"query": "path:90-Sources", "color": {"a": 1, "rgb": 9013641}},
    {"query": "path:06-LLM-Wiki", "color": {"a": 1, "rgb": 3381759}},
    {"query": "path:07-Sermon-Studio", "color": {"a": 1, "rgb": 16750848}}],
    "search": "-path:99-System -path:10-Templates -path:00-Dashboard -path:11-Indexes", "showOrphans": True})
put("plugins/templater-obsidian/data.json", {"templates_folder": "10-Templates", "trigger_on_file_creation": False})
put("plugins/copilot/data.json", {"customPromptsFolder": "99-System/Agents"})
put("plugins/dataview/data.json", {"enableDataviewJs": False, "enableInlineDataview": True})
PY

# ---- 커뮤니티 플러그인
# 활성화: 검증된 조합. 설치만(비활성): 원본 자동 수정 위험이 있거나 선택적인 것.
ENABLED="blacksmithgu/obsidian-dataview SilentVoid13/Templater chhoumann/quickadd scambier/obsidian-omnisearch Vinzent03/obsidian-git zsviczian/obsidian-excalidraw-plugin zsviczian/excalibrain logancyang/obsidian-copilot tim-hub/obsidian-bible-reference"
DISABLED="platers/obsidian-linter"
IDS_FILE="$TMP/enabled_ids"; : > "$IDS_FILE"
FAILS=""
install_plugin(){ # $1=repo $2=enable(1/0)
  local repo="$1" base="https://github.com/$1/releases/latest/download" t="$TMP/p"
  rm -rf "$t"; mkdir -p "$t"
  if ! curl -fsSL --retry 2 "$base/manifest.json" -o "$t/manifest.json"; then FAILS="$FAILS $repo"; warn "$repo 다운로드 실패"; return; fi
  local id; id="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["id"])' "$t/manifest.json")"
  local dir="$VAULT/.obsidian/plugins/$id"
  if [ -f "$dir/main.js" ]; then ok "$id 이미 설치됨(보존)"; else
    curl -fsSL --retry 2 "$base/main.js" -o "$t/main.js" || { FAILS="$FAILS $repo"; warn "$repo main.js 실패"; return; }
    curl -fsSL "$base/styles.css" -o "$t/styles.css" 2>/dev/null || rm -f "$t/styles.css"
    mkdir -p "$dir"; cp "$t/"* "$dir/"
    ok "$id $(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["version"])' "$t/manifest.json")$([ "$2" = 1 ] || echo ' (설치만, 비활성)')"
  fi
  [ "$2" = 1 ] && echo "$id" >> "$IDS_FILE"
  return 0
}
if [ "$PLUGINS" -eq 1 ]; then
  c "커뮤니티 플러그인 설치 (GitHub 최신 릴리스)"
  for r in $ENABLED; do install_plugin "$r" 1; done
  for r in $DISABLED; do install_plugin "$r" 0; done
  python3 - "$VAULT/.obsidian/community-plugins.json" "$IDS_FILE" <<'PY'
import json, os, sys
p, ids = sys.argv[1], [l.strip() for l in open(sys.argv[2]) if l.strip()]
cur = json.load(open(p)) if os.path.exists(p) else []
json.dump(cur + [i for i in ids if i not in cur], open(p, "w"), indent=2)
print(f"  \033[32m✔\033[0m community-plugins.json 활성 {len(ids)}개")
PY
fi

# ---- 엔진 & tkos 명령
c "tkos 엔진 설치"
mkdir -p "$HOME/.tkos/engine" "$HOME/.local/bin"
cp "$SRC/engine/"*.py "$HOME/.tkos/engine/"
cat > "$HOME/.local/bin/tkos" <<EOF
#!/bin/sh
export TKOS_VAULT="\${TKOS_VAULT:-$VAULT}"
exec python3 "\$HOME/.tkos/engine/tkos.py" "\$@"
EOF
chmod +x "$HOME/.local/bin/tkos"
[ -f "$MARKER" ] || printf '{\n  "name": "Theology Knowledge OS",\n  "version": "0.1.0",\n  "installed": "%s",\n  "source_of_truth": "markdown"\n}\n' "$(date +%Y-%m-%dT%H:%M:%S)" > "$MARKER"
ok "~/.local/bin/tkos"
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *)
  RC="$HOME/.zshrc"; [ -n "${BASH_VERSION:-}" ] && [ "$(basename "${SHELL:-}")" = bash ] && RC="$HOME/.bashrc"
  if ! grep -qs 'TKOS PATH' "$RC"; then printf '\n# TKOS PATH\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$RC"; fi
  warn "PATH 에 ~/.local/bin 추가함($RC). 새 터미널을 열거나: export PATH=\"\$HOME/.local/bin:\$PATH\"";;
esac
TKOS="$HOME/.local/bin/tkos"

# ---- Git
if [ "$GIT" -eq 1 ] && command -v git >/dev/null; then
  c "Git 버전 관리"
  [ -f "$VAULT/.gitignore" ] || printf '.tkos/\n.obsidian/workspace*.json\n.obsidian/cache\n.trash/\n.DS_Store\n' > "$VAULT/.gitignore"
  if [ ! -d "$VAULT/.git" ]; then
    git -C "$VAULT" init -q -b main 2>/dev/null || git -C "$VAULT" init -q
    ok "git init"
  fi
fi

# ---- 예제 & 인덱스
if [ "$SAMPLES" -eq 1 ]; then
  c "예제 자료 인제스트"
  cp -n "$SRC/examples/"*.md "$VAULT/01-Inbox/New-Markdown/" 2>/dev/null || true
  TKOS_VAULT="$VAULT" "$TKOS" ingest | sed 's/^/  /'
fi
c "검색 인덱스 생성"
TKOS_VAULT="$VAULT" "$TKOS" index | sed 's/^/  /'

if [ "$GIT" -eq 1 ] && [ -d "$VAULT/.git" ]; then
  if git -C "$VAULT" config user.email >/dev/null 2>&1; then
    git -C "$VAULT" add -A && git -C "$VAULT" commit -qm "Theology Knowledge OS 설치" 2>/dev/null && ok "초기 커밋" || true
  else warn "git user.email 미설정 — 커밋은 건너뜀"; fi
fi

# ---- Obsidian 에 등록·실행 (macOS)
if [ "$OPEN" -eq 1 ] && [ "$(uname)" = "Darwin" ]; then
  c "Obsidian 열기"
  CFG="$HOME/Library/Application Support/obsidian/obsidian.json"
  if [ -d "/Applications/Obsidian.app" ]; then
    if ! pgrep -x Obsidian >/dev/null && [ -f "$CFG" ]; then
      cp "$CFG" "$CFG.tkos-backup"
      python3 - "$CFG" "$VAULT" <<'PY'
import json, sys, time, hashlib
p, v = sys.argv[1], sys.argv[2]
d = json.load(open(p)); vs = d.setdefault("vaults", {})
if not any(x.get("path") == v for x in vs.values()):
    vs[hashlib.md5(v.encode()).hexdigest()[:16]] = {"path": v, "ts": int(time.time() * 1000)}
for x in vs.values(): x.pop("open", None)
for x in vs.values():
    if x.get("path") == v: x["open"] = True
json.dump(d, open(p, "w"))
PY
      open -a Obsidian && ok "Obsidian 실행 (설정 백업: obsidian.json.tkos-backup)"
    else
      open "obsidian://open?path=$(python3 -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))' "$VAULT/00-Dashboard/Home.md")" 2>/dev/null || true
      warn "Obsidian 이 실행 중입니다. Vault 가 열리지 않으면: Obsidian → 'Open folder as vault' → $VAULT"
    fi
  else
    warn "Obsidian 이 없습니다: https://obsidian.md/download 설치 후 'Open folder as vault' → $VAULT"
  fi
fi

echo
c "완료"
echo "  Vault   : $VAULT"
echo "  처음 열 때 '이 Vault 를 신뢰합니까?' 창에서 [Trust author and enable plugins] 를 누르세요."
echo "  자료 등록: .md 를 01-Inbox/New-Markdown 에 넣고 → tkos ingest   (상시 감시: tkos watch)"
echo "  검색    : tkos search \"로마서 8:28 섭리\""
[ -n "$FAILS" ] && warn "설치 실패 플러그인:$FAILS (네트워크 확인 후 재실행하면 이어서 설치)"
exit 0
