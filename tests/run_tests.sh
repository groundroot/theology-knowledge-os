#!/usr/bin/env bash
# 필수 테스트 시나리오 자동 검증 (임시 HOME 에서 실행, 실제 환경을 건드리지 않음)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export HOME="$(mktemp -d)"; V="$HOME/vault"; export TKOS_VAULT="$V"
pass(){ printf "  \033[32mPASS\033[0m %s\n" "$*"; }; fail(){ printf "  \033[31mFAIL\033[0m %s\n" "$*"; exit 1; }
TKOS_SRC="$ROOT" bash "$ROOT/install.sh" --vault "$V" --with-samples --no-open --no-plugins >/dev/null
T="$HOME/.local/bin/tkos"
[ -f "$V/06-LLM-Wiki/Source-Notes/SRC-000002 로마서 8장 28-30절 강해 노트 (예제).md" ] && pass "A 신규 Markdown 인제스트·출처노트" || fail A
$T search "롬 8:28" --json | python3 -c 'import json,sys;r=json.load(sys.stdin)["results"];t={x["type"] for x in r};sys.exit(0 if {"bible-commentary","sermon","bible-dictionary","bible-passage"}<=t else 1)' && pass "B 롬 8:28 → 본문·주석·사전·설교 연결" || fail B
grep -q "\[\[로마서 8장 28절\]\]" "$V/06-LLM-Wiki/Source-Notes/"SRC-000002*.md && pass "C 본문 허브 Wikilink(그래프 연결)" || fail C
grep -q "Original-Markdown/SRC-000002__romans-8-28-commentary-sample#문맥" "$V/06-LLM-Wiki/Source-Notes/"SRC-000002*.md && cmp -s "$ROOT/examples/romans-8-28-commentary-sample.md" "$V/90-Sources/Original-Markdown/SRC-000002__romans-8-28-commentary-sample.md" && pass "D 출처노트 → 원본 제목 링크 · 원본 바이트 보존" || fail D
printf -- '---\ntype: bible-commentary\n---\n# 새 주석\n롬 8:28 추가 해설.\n' > "$V/01-Inbox/New-Markdown/new.md"; $T ingest >/dev/null
grep -rq "\[\[로마서 8장 28절\]\]" "$V/06-LLM-Wiki/Source-Notes/"SRC-000004*.md && pass "G 새 주석 → 기존 본문 허브에 자동 연결" || fail G
cp "$ROOT/examples/romans-8-28-commentary-sample.md" "$V/01-Inbox/New-Markdown/"; echo x > "$V/01-Inbox/New-Markdown/a.pdf"; $T ingest >/dev/null
[ -f "$V/01-Inbox/Review-Required/romans-8-28-commentary-sample.md" ] && [ -f "$V/01-Inbox/Processing-Failed/a.pdf" ] && pass "중복 재등록 차단 · PDF 거부" || fail dup
rm -rf "$V/.tkos"; $T index --rebuild >/dev/null; [ "$($T search "롬 8:28" --json | python3 -c 'import json,sys;print(len(json.load(sys.stdin)["results"]))')" -ge 4 ] && pass "H 인덱스 삭제 → Markdown 만으로 재구축" || fail H
$T check > "$HOME/check.txt"; grep -q "해시불일치 0" "$HOME/check.txt" && pass "무결성 점검(원본 해시)" || fail check
echo "모든 테스트 통과 (E·F 설교 생성/퇴고는 LLM 이 필요해 자동 테스트 대상 아님)"
