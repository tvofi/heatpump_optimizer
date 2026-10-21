#!/bin/bash
{ set +x; } 2>/dev/null # before anything: a caller's `bash -x` would trace the token
# body_patch.sh [--dry-run] [--repo <owner/repo>] <pr> <expected-head-sha> <body.md>
# body_patch.sh --self-test
#
# Repair an open pull request's BODY without moving its head (Lean flow study
# K14, R10-FLOW-BODY-PATCH). Ruling R4 forbids moving a clean head and
# update_pr.sh merges main on every run; app_push.sh mints, pushes, then
# PATCHes. Nothing PATCHed a body alone, so a body `pr-contract` or
# `carry_audit` refused stayed red or cost a head move.
#
# ORDER, each step refusing before the next, and NOTHING is minted or written
# until step 4 (the #678 ordering app_push.sh keeps):
#   1. the App's identity files read back (fail closed);
#   2. the live pull request is OPEN and its head IS <expected-head-sha>;
#   3. the body contract, offline, at that head: `policy_lint.mjs --pr-body`
#      with the arguments pr-contract passes (title, author, the paths the head
#      changes against the base, the paths the base already had, the red
#      checks at the head) and `carry_audit.py check --body`;
#   4. mint the `hpo-author` token (tools/pr/app_mint.sh, the mint app_push.sh
#      uses), re-read the head once more, PATCH {"body"} and nothing else;
#   5. read the pull request back: open, head still <expected-head-sha>, body
#      identical to <body.md> modulo ONE trailing newline (GitHub appends one;
#      app_push.sh's measured rule). A completed read that differs refuses at
#      once; a read that could not be performed retries (3 reads, 2 s apart).
# The PATCH sets `body` only: it cannot move the head. `pr-contract` re-runs on
# the `edited` event and reads the body from the API.
#
# --dry-run runs steps 1-3, then prints the exact PATCH request and stops
# before signing anything. Exit 0 = patched and read back; 1 = refused.
#
# AS A JOB. `body_patch <pr> <sha> <body>` is one `--once` unit: its only state
# is its arguments and the exit code, and its last line is a single
# `body_patch: OK|REFUSE ...` line, so a beat (R10-ORCH-MACHINERY) hosts it
# unchanged. It reads the repository from the worktree it runs in
# (`--repo` overrides; default tvofi/heatpump_optimizer).
#
# Lines ending `# mut:<arm>` are the arms the self-test deletes in turn; a
# mutant that still passes its arm's control fails the self-test.
set -uo pipefail

API=https://api.github.com
ACCEPT='Accept: application/vnd.github+json'
MINT_NAME=body_patch
die() { printf 'body_patch: REFUSE: %s\n' "$*" >&2; exit 1; }
HERE="$(cd "$(dirname -- "$0")" && pwd)"
# shellcheck source=../../pr/app_mint.sh
. "$HERE/../../pr/app_mint.sh"

RB_TRIES=${BODY_PATCH_READBACK_TRIES:-3}
RB_SLEEP=${BODY_PATCH_READBACK_SLEEP:-2}

# One verdict token for a pull request document and the body file:
#   ok | stale <sha> | body | bad <why>
verdict() { # head body-file < pr-json
  python3 -c '
import sys, json
head, f = sys.argv[1], sys.argv[2]
try:
    d = json.loads(sys.stdin.read())
except ValueError:
    print("bad unparseable response"); sys.exit(0)
if d.get("state") != "open":
    print("bad state=%s" % d.get("state")); sys.exit(0)
live = (d.get("head") or {}).get("sha") or ""
if live != head:
    print("stale %s" % live); sys.exit(0)
want = open(f).read(); got = d.get("body") or ""
def eq1(a, b):
    return a == b or (a.endswith("\n") and a[:-1] == b) or (b.endswith("\n") and b[:-1] == a)
print("ok" if eq1(got, want) else "body")' "$1" "$2"
}

# The contract arm: pr-contract's own policy_lint call, then the carry check.
# Runs in the current directory (a worktree holding the head's objects).
contract() { # pr-json base head body -> rc
  local doc=$1 base=$2 head=$3 body=$4 title author
  local d; d=$(mktemp -d "${TMPDIR:-/tmp}/body_patch.XXXXXX") || return 1
  title=$(printf '%s' "$doc" | python3 -c 'import sys, json; print(json.load(sys.stdin).get("title") or "")') || return 1
  author=$(printf '%s' "$doc" | python3 -c 'import sys, json; print((json.load(sys.stdin).get("user") or {}).get("login") or "")') || return 1
  git diff --no-renames --name-only "$base...$head" > "$d/files" || { rm -rf "$d"; return 1; }
  git diff --no-renames --name-only --diff-filter=a "$base...$head" > "$d/existing" || { rm -rf "$d"; return 1; }
  # One --red per name, as pr-contract passes them; a failed listing is a
  # refusal (an empty list read from a failed fetch is "no reds").
  gh api --paginate "repos/$REPO/commits/$head/check-runs" --jq '.check_runs[]
      | select(.status == "completed" and .conclusion == "failure")
      | select(.name != "pr-contract") | .name' 2>/dev/null | sort -u > "$d/reds" \
    || { echo "body_patch: the check runs at $head could not be listed" >&2; rm -rf "$d"; return 1; }
  local args=(--pr-body "$body" --head "$head" --title "$title" --author "$author"
              --paths-file "$d/files" --existing-file "$d/existing") name rc=0
  while IFS= read -r name; do args+=(--red "$name"); done < "$d/reds"
  node tools/policy/policy_lint.mjs "${args[@]}" || rc=1 # mut:contract
  python3 -I tools/audit/carry_audit.py check --body "$body" || rc=1 # mut:carry
  rm -rf "$d"
  return "$rc"
}

patch_body() {
  local dry=0 repo=tvofi/heatpump_optimizer
  [ "${1:-}" = "--dry-run" ] && { dry=1; shift; }
  if [ "${1:-}" = "--repo" ]; then repo=${2:-}; shift 2 2>/dev/null || die "--repo needs a value"; fi
  [ $# -eq 3 ] || die "usage: body_patch.sh [--dry-run] [--repo <owner/repo>] <pr> <expected-head-sha> <body.md>"
  local pr=$1 expect=$2 body=$3
  REPO=$repo
  [[ $repo =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || die "repo '$repo' is not owner/repo"
  [[ $pr =~ ^[0-9]+$ ]] || die "pull request '$pr' is not a number"
  [[ $expect =~ ^[0-9a-f]{40}$ ]] || die "expected head '$expect' is not a 40-hex sha"
  [ -s "$body" ] || die "no body at $body (missing or empty)"
  body=$(cd "$(dirname -- "$body")" && printf '%s/%s' "$(pwd)" "$(basename -- "$body")")
  command -v gh >/dev/null 2>&1 || die "no gh on PATH: the live head cannot be read, so NOTHING was minted or written"

  mint_identity # 1

  # 2. the live head, read before anything else is done.
  local doc live base v
  doc=$(gh api "repos/$repo/pulls/$pr" 2>/dev/null) \
    || die "pull request #$pr could not be read (gh exited $?); NOTHING was minted or written"
  v=$(printf '%s' "$doc" | verdict "$expect" "$body")
  case "$v" in
    ok|body|stale\ *) ;; # open; the head is judged by the equality below, the body differing is why we are here
    *) die "#$pr did not read back as an open pull request (${v#bad }); NOTHING was minted or written" ;;
  esac
  live=$(printf '%s' "$doc" | python3 -c 'import sys, json; print(json.load(sys.stdin)["head"]["sha"])')
  [ "$live" = "$expect" ] || die "#$pr's live head $live is not the expected $expect: the head moved, so the inference this body repair rests on is wrong; NOTHING was minted or written" # mut:head
  base=$(printf '%s' "$doc" | python3 -c 'import sys, json; print(json.load(sys.stdin)["base"]["sha"])') \
    || die "#$pr names no base sha"

  # 3. the contract, offline at that head. The head's objects must be here.
  git cat-file -e "$expect^{commit}" 2>/dev/null || git fetch -q origin "refs/pull/$pr/head" 2>/dev/null
  git cat-file -e "$expect^{commit}" 2>/dev/null \
    || die "the head $expect is not in this worktree and could not be fetched; the contract cannot run offline, so NOTHING was minted or written"
  git cat-file -e "$base^{commit}" 2>/dev/null || git fetch -q origin "$base" 2>/dev/null
  contract "$doc" "$base" "$expect" "$body" \
    || die "the body does not pass the contract at $expect (above): it is NEVER sent; repair it and run this again"

  local payload; payload=$(python3 -c 'import sys, json; print(json.dumps({"body": open(sys.argv[1]).read()}))' "$body") \
    || die "could not write the body payload"
  if [ "$dry" = 1 ]; then
    printf 'body_patch: DRY-RUN: the contract passed at %s; would PATCH %s/repos/%s/pulls/%s as hpo-author with %s; signed, minted and wrote nothing\n' "$expect" "$API" "$repo" "$pr" "$payload"
    return 0
  fi

  # 4. mint, re-read the head, PATCH.
  mint_token "$repo"
  local again
  again=$(curl -fsS -H @"$PRIV/token.h" -H "$ACCEPT" "$API/repos/$repo/pulls/$pr" | python3 -c 'import sys, json; print(json.load(sys.stdin)["head"]["sha"])') \
    || die "the pre-write read of #$pr failed; nothing was written"
  [ "$again" = "$expect" ] || die "#$pr's head moved to $again between the check and the write; nothing was written" # mut:prewrite
  printf '%s' "$payload" > "$PRIV/pr.json"
  curl -fsS -X PATCH -H @"$PRIV/token.h" -H "$ACCEPT" "$API/repos/$repo/pulls/$pr" \
    --data-binary @"$PRIV/pr.json" >/dev/null \
    || die "the body PATCH on #$pr was refused; set the body by hand from $body"

  # 5. read it back: body identical, head unmoved.
  local attempt=1 out
  while :; do
    if out=$(curl -fsS -H @"$PRIV/token.h" -H "$ACCEPT" "$API/repos/$repo/pulls/$pr" 2>/dev/null); then
      v=$(printf '%s' "$out" | verdict "$expect" "$body")
      case "$v" in
        ok) break ;;
        body) die "#$pr's body read back is not identical to $body modulo one trailing newline" ;; # mut:readback
        stale\ *) die "#$pr's head is now ${v#stale }, not $expect: the head moved around the write" ;; # mut:rbhead
        bad\ state=*) die "#$pr read back as ${v#bad }" ;;
      esac
    fi
    [ "$attempt" -lt "$RB_TRIES" ] || die "#$pr could not be read back within $RB_TRIES attempts; re-read it by hand"
    sleep "$RB_SLEEP"; attempt=$((attempt + 1))
  done
  printf 'body_patch: OK: #%s body patched and read back identical; head %s unmoved\n' "$pr" "$expect"
}

if [ "${1:-}" != "--self-test" ]; then
  patch_body "$@"
  exit $?
fi

# ---------------------------------------------------------------------------
# --self-test: `gh`, `curl`, `openssl` and `node` are stubs on PATH; the git
# repository is a real scratch one. The script under test is a byte-identical
# COPY beside the real app_mint.sh. Every refusal is paired with the healthy run
# it must NOT refuse, and each `# mut:` arm is deleted in turn from a copy and
# its control must then FAIL to refuse (the mutant is caught).
SELF="$HERE/$(basename -- "$0")"
W=$(mktemp -d) || exit 2
trap 'rm -rf "$W"' EXIT
FAILS=0; N=0
st() { N=$((N + 1)); if [ "$1" = "$2" ]; then echo "ok   $3"; else echo "FAIL $3 (got '$1', want '$2')"; FAILS=$((FAILS + 1)); fi; }
TOKEN=ghs_STUBTOKEN_must_never_print
mkdir -p "$W/bin" "$W/id" "$W/tool/audit/seat" "$W/tool/pr" "$W/repo/tools/policy" "$W/repo/tools/audit"
cp "$SELF" "$W/tool/audit/seat/body_patch.sh"; cp "$HERE/../../pr/app_mint.sh" "$W/tool/pr/"
printf '424242\n' > "$W/id/hpo-author.appid.txt"
printf -- '-----BEGIN STUB KEY-----\nSTUBKEYMATERIAL\n-----END STUB KEY-----\n' > "$W/id/hpo-author.pem"
# A real repository: base, then the head (adds b.txt), and a third commit the
# "moved" head points at (adds c.txt), so a moved head is a real object.
( cd "$W/repo" && git init -q . && git config user.email t@t && git config user.name t \
  && echo a > a.txt && git add . && git commit -qm base && git rev-parse HEAD > "$W/base.sha" \
  && echo b > b.txt && git add b.txt && git commit -qm head && git rev-parse HEAD > "$W/head.sha" \
  && echo c > c.txt && git add c.txt && git commit -qm moved && git rev-parse HEAD > "$W/moved.sha" ) >/dev/null 2>&1
BASE=$(cat "$W/base.sha"); HEAD=$(cat "$W/head.sha"); MOVED=$(cat "$W/moved.sha")
printf '## Head\n\n`%s`\n\nthe corrected body, 113\n' "$HEAD" > "$W/body.md"

cat > "$W/prjson.py" <<'PY'
import json, sys
# new <file> <head> <base> | get <file> | store <file> <payload>
v = sys.argv[1:]
if v[0] == "new":
    json.dump({"number": 7, "state": "open", "title": "fix: the title", "user": {"login": "hpo-author"},
               "head": {"sha": v[2]}, "base": {"sha": v[3]}, "body": "the old body, 111"}, open(v[1], "w"))
elif v[0] == "get":
    d = json.load(open(v[1])); d["body"] += "\n"; print(json.dumps(d))   # GitHub appends one newline
elif v[0] == "store":
    d = json.load(open(v[1])); d["body"] = json.load(open(v[2]))["body"]; json.dump(d, open(v[1], "w"))
PY
cat > "$W/bin/gh" <<'STUB'
#!/bin/bash
printf 'gh %s\n' "$*" >> "$STUB/log"
case "$*" in
  "api repos/o/r/pulls/7") [ -f "$STUB/gh-fails" ] && exit 1; python3 "$STUB/../prjson.py" get "$STUB/live.json" ;;
  "api --paginate repos/o/r/commits/"*"/check-runs "*) [ -f "$STUB/checks-fail" ] && exit 1; cat "$STUB/reds" 2>/dev/null; true ;;
  *) exit 9 ;;
esac
STUB
cat > "$W/bin/node" <<'STUB'
#!/bin/bash
printf 'node %s\n' "$*" >> "$STUB/log"
prev=""; for a in "$@"; do [ "$prev" = "--paths-file" ] && cp "$a" "$STUB/paths"; [ "$prev" = "--existing-file" ] && cp "$a" "$STUB/existing"; prev="$a"; done
[ -f "$STUB/lint-fails" ] && { echo "policy_lint: REFUSE stub" >&2; exit 1; }
exit 0
STUB
cat > "$W/repo/tools/audit/carry_audit.py" <<'PY'
import os, sys
open(os.path.join(os.environ["STUB"], "log"), "a").write("carry_audit %s\n" % " ".join(sys.argv[1:]))
if os.path.exists(os.path.join(os.environ["STUB"], "carry-fails")):
    print("carry_audit: REFUSED stub"); sys.exit(1)
PY
cat > "$W/bin/curl" <<'STUB'
#!/bin/bash
url=""; data=""; hdr=""; method="GET"; prev=""
for a in "$@"; do
  [ "$prev" = "-X" ] && method="$a"
  case "$a" in https://*) url="$a" ;; @*.json) data="${a#@}" ;; @*.h) hdr="${a#@}" ;; esac
  prev="$a"
done
printf 'curl %s %s\n' "$method" "${url#https://api.github.com/}" >> "$STUB/log"
case "$url" in
  */repos/o/r/installation) printf '{"id": 99}' ;;
  */app/installations/99/access_tokens) printf '{"token": "ghs_STUBTOKEN_must_never_print"}' ;;
  */installation/token) grep -q 'ghs_STUBTOKEN' "$hdr" || exit 22 ;;
  */repos/o/r/pulls/7)
    if [ "$method" = PATCH ]; then
      [ -f "$STUB/refuse-patch" ] && exit 22
      python3 "$STUB/../prjson.py" store "$STUB/live.json" "$data"
    else
      n=$(cat "$STUB/get-n" 2>/dev/null || echo 0); n=$((n + 1)); printf '%s' "$n" > "$STUB/get-n"
      # move-at-<n>: the n-th token read finds the head moved (1 = before the write, 2 = after it)
      if [ -f "$STUB/move-at-$n" ]; then
        python3 "$STUB/../prjson.py" get "$STUB/live.json" | python3 -c 'import sys, json; d = json.load(sys.stdin); d["head"]["sha"] = sys.argv[1]; print(json.dumps(d))' "$(cat "$STUB/../moved.sha")"
      elif [ -f "$STUB/mangle" ] && [ "$n" -ge 2 ]; then
        python3 "$STUB/../prjson.py" get "$STUB/live.json" | python3 -c 'import sys, json; d = json.load(sys.stdin); d["body"] = "edited by someone else\n"; print(json.dumps(d))'
      else
        python3 "$STUB/../prjson.py" get "$STUB/live.json"
      fi
    fi ;;
  *) exit 9 ;;
esac
STUB
cat > "$W/bin/openssl" <<'STUB'
#!/bin/bash
case "$1" in
  base64) base64 | tr -d '\n' ;;
  dgst) [ -s "$4" ] || exit 1; cat >/dev/null; printf 'STUBSIGNATURE' ;;
  *) exit 9 ;;
esac
STUB
chmod +x "$W/bin/"*

mkcase() { # name [live-head] -> a stub dir with its own log, TMPDIR and live pull request
  local d="$W/$1"; mkdir -p "$d/tmp"; : > "$d/log"
  python3 "$W/prjson.py" new "$d/live.json" "${2:-$HEAD}" "$BASE"
}
run() { # name script args... -> rc; out/err captured in the case dir
  local d="$W/$1" sc=$2; shift 2
  ( cd "$W/repo" && export STUB="$d" PATH="$W/bin:$PATH" TMPDIR="$d/tmp" HPO_IDENTITY_DIR="${IDDIR:-$W/id}" \
      BODY_PATCH_READBACK_SLEEP=0 && bash "$sc" "$@" > "$d/out" 2> "$d/err" )
}
BP=$W/tool/audit/seat/body_patch.sh
calls() { grep -c "^$2" "$W/$1/log"; }
leftover() { find "$W/$1/tmp" -mindepth 1 | wc -l | tr -d ' '; }
leaks() { cat "$W/$1/out" "$W/$1/err" | grep -c -e "$TOKEN" -e STUBKEYMATERIAL -e STUBSIGNATURE; }
livebody() { python3 -c 'import json, sys; sys.stdout.write(json.load(open(sys.argv[1]))["body"])' "$W/$1/live.json"; }

# The healthy run: the arm every refusal below is paired with.
mkcase ok; printf 'fast (3.14)\nlint\n' > "$W/ok/reds"
run ok "$BP" --repo o/r 7 "$HEAD" "$W/body.md"; st $? 0 "the head is as expected and the contract passes: the body is patched"
st "$(livebody ok)" "$(cat "$W/body.md")" "the live body is the body file's exact bytes"
st "$(calls ok 'curl PATCH repos/o/r/pulls/7')" 1 "one PATCH, no other write (POST $(calls ok 'curl POST repos/o/r/pulls$'))"
st "$(calls ok 'curl POST repos/o/r/pulls$')" 0 "and no pull request created"
st "$(grep -c '^body_patch: OK: #7 .* head '"$HEAD"' unmoved$' "$W/ok/out")" 1 "the last line is one OK line naming the unmoved head"
st "$(calls ok 'curl GET repos/o/r/pulls/7')" 2 "the head is re-read before the write and the body read back after it"
l1=$(grep -n '^gh api repos/o/r/pulls/7$' "$W/ok/log" | head -1 | cut -d: -f1); l2=$(grep -n '^node ' "$W/ok/log" | head -1 | cut -d: -f1)
l3=$(grep -n '^curl GET repos/o/r/installation$' "$W/ok/log" | head -1 | cut -d: -f1); l4=$(grep -n '^curl PATCH ' "$W/ok/log" | head -1 | cut -d: -f1)
if [ "$l1" -lt "$l2" ] && [ "$l2" -lt "$l3" ] && [ "$l3" -lt "$l4" ]; then ORD=ordered; else ORD="head=$l1 lint=$l2 mint=$l3 patch=$l4"; fi
st "$ORD" ordered "live head read, then the contract, then the mint, then the PATCH (#678's ordering)"
st "$(grep -c -- "--pr-body $W/body.md --head $HEAD --title fix: the title --author hpo-author --paths-file .* --existing-file .* --red fast (3.14) --red lint$" "$W/ok/log")" 1 "policy_lint gets pr-contract's arguments: body, head, title, author, paths, existing, one --red per check"
st "$(cat "$W/ok/paths")" "b.txt" "its paths are what the head changes against the base (three-dot): b.txt, not the later c.txt"
st "$(grep -c "^carry_audit check --body $W/body.md$" "$W/ok/log")" 1 "carry_audit check --body runs on the same body"
st "$(calls ok 'curl DELETE installation/token')" 1 "the installation token is revoked on exit"
st "$(leftover ok)" 0 "the private directory is gone"
st "$(leaks ok)" 0 "no token, key or signature text in stdout or stderr"
st "$(grep -c "$TOKEN\|Authorization:" "$W/ok/log")" 0 "and none on any stubbed command line"

# --dry-run prints the request and writes nothing.
mkcase dry
run dry "$BP" --dry-run --repo o/r 7 "$HEAD" "$W/body.md"; st $? 0 "--dry-run on a passing body exits 0"
st "$(calls dry curl)" 0 "--dry-run makes no curl call at all: nothing minted"
st "$(grep -c '^body_patch: DRY-RUN: .* would PATCH https://api.github.com/repos/o/r/pulls/7 as hpo-author with {"body": ".*113\\n"}; signed, minted and wrote nothing$' "$W/dry/out")" 1 "and prints the exact request: PATCH URL and the JSON payload"
st "$(livebody dry)" "the old body, 111" "(null control: the live body is untouched)"

# A moved head refuses before ANY write, and before the mint.
mkcase moved "$MOVED"
run moved "$BP" --repo o/r 7 "$HEAD" "$W/body.md"; st $? 1 "REFUSE: the live head is not the expected sha"
st "$(grep -c "the head moved" "$W/moved/err")" 1 "naming the reason"
st "$(calls moved curl)$(calls moved node)" 00 "no curl, no contract: refused before any write or mint"
st "$(livebody moved)" "the old body, 111" "and the body is untouched"
mkcase pre; : > "$W/pre/move-at-1"
run pre "$BP" --repo o/r 7 "$HEAD" "$W/body.md"; st $? 1 "REFUSE: the head moves between the check and the write"
st "$(calls pre 'curl PATCH')" 0 "no PATCH was sent"
mkcase post; : > "$W/post/move-at-2"
run post "$BP" --repo o/r 7 "$HEAD" "$W/body.md"; st $? 1 "REFUSE: the head is found moved on the read-back"
mkcase closed; python3 - "$W/closed/live.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); d["state"] = "closed"; json.dump(d, open(sys.argv[1], "w"))
PY
run closed "$BP" --repo o/r 7 "$HEAD" "$W/body.md"; st $? 1 "REFUSE: a closed pull request"
st "$(calls closed curl)" 0 "(and nothing minted)"

# A refused body is never sent.
mkcase lint; : > "$W/lint/lint-fails"
run lint "$BP" --repo o/r 7 "$HEAD" "$W/body.md"; st $? 1 "REFUSE: policy_lint refuses the body"
st "$(calls lint curl)" 0 "never sent, never minted"
mkcase carry; : > "$W/carry/carry-fails"
run carry "$BP" --repo o/r 7 "$HEAD" "$W/body.md"; st $? 1 "REFUSE: carry_audit refuses the body"
st "$(calls carry curl)" 0 "never sent, never minted"
mkcase checks; : > "$W/checks/checks-fail"
run checks "$BP" --repo o/r 7 "$HEAD" "$W/body.md"; st $? 1 "REFUSE: the check runs cannot be listed (an empty list from a failed read is not 'no reds')"
st "$(calls checks curl)" 0 "(and nothing minted)"

# The read-back: a body that does not read back identical, and a refused PATCH.
mkcase mangle; : > "$W/mangle/mangle"
run mangle "$BP" --repo o/r 7 "$HEAD" "$W/body.md"; st $? 1 "REFUSE: the body read back is not the body sent"
st "$(grep -c '^body_patch: OK' "$W/mangle/out")" 0 "and no OK line"
st "$(calls mangle 'curl GET repos/o/r/pulls/7')" 2 "a completed mismatch is not retried (pre-write read plus one read-back)"
mkcase refuse; : > "$W/refuse/refuse-patch"
run refuse "$BP" --repo o/r 7 "$HEAD" "$W/body.md"; st $? 1 "REFUSE: GitHub refuses the PATCH"
st "$(calls refuse 'curl DELETE installation/token')" 1 "(the token is revoked on a refusal too)"

# Argument and identity refusals, nothing called.
mkcase args
run args "$BP" --repo o/r 7 abc "$W/body.md"; st $? 1 "REFUSE: a short sha"
run args "$BP" --repo o/r x "$HEAD" "$W/body.md"; st $? 1 "REFUSE: a non-numeric pull request"
: > "$W/empty.md"; run args "$BP" --repo o/r 7 "$HEAD" "$W/empty.md"; st $? 1 "REFUSE: an empty body file"
mkdir -p "$W/noid"; IDDIR=$W/noid run args "$BP" --repo o/r 7 "$HEAD" "$W/body.md"; st $? 1 "REFUSE: no App identity files (fail closed)"
st "$(calls args curl)$(calls args gh)" 00 "none of those made a call"
mkcase ghfail; : > "$W/ghfail/gh-fails"
run ghfail "$BP" --repo o/r 7 "$HEAD" "$W/body.md"; st $? 1 "REFUSE: the live head cannot be read"
st "$(calls ghfail curl)" 0 "(and nothing minted)"

# Mutants: delete one arm at a time from a copy; its control must stop refusing.
mutant() { # arm sed-expression -> a copy of the tool with the arm deleted
  mkdir -p "$W/mut-$1/audit/seat" "$W/mut-$1/pr"; cp "$W/tool/pr/app_mint.sh" "$W/mut-$1/pr/"
  sed "$2" "$BP" > "$W/mut-$1/audit/seat/body_patch.sh"
  [ "$(cmp -s "$BP" "$W/mut-$1/audit/seat/body_patch.sh"; echo $?)" = 1 ] || echo "FAIL mutant $1 changed nothing" >&2
}
mutant head   '/# mut:head$/s/.*/:/'
mutant prew   '/# mut:prewrite$/s/.*/:/'
mutant lint   '/# mut:contract$/s/.*/:/'
mutant carry  '/# mut:carry$/s/.*/:/'
mutant rb     '/# mut:readback$/s/.*/        body) break ;;/'
mutant rbhead '/# mut:rbhead$/s/.*/        stale\\ *) break ;;/'
MBP() { echo "$W/mut-$1/audit/seat/body_patch.sh"; }
mkcase m1 "$MOVED"; run m1 "$(MBP head)" --repo o/r 7 "$HEAD" "$W/body.md"
st "$([ "$(calls m1 curl)" -gt 0 ] && echo minted)" minted "MUTANT head check deleted: the moved-head control now MINTS (the pre-write re-read still stops the write), so the control catches it"
mkcase m2; : > "$W/m2/move-at-1"; run m2 "$(MBP prew)" --repo o/r 7 "$HEAD" "$W/body.md"
st "$(calls m2 'curl PATCH')" 1 "MUTANT pre-write head check deleted: the control now WRITES"
mkcase m3; : > "$W/m3/lint-fails"; run m3 "$(MBP lint)" --repo o/r 7 "$HEAD" "$W/body.md"
st "$(calls m3 'curl PATCH')" 1 "MUTANT policy_lint arm deleted: the refused body is now SENT"
mkcase m4; : > "$W/m4/carry-fails"; run m4 "$(MBP carry)" --repo o/r 7 "$HEAD" "$W/body.md"
st "$(calls m4 'curl PATCH')" 1 "MUTANT carry_audit arm deleted: the refused body is now SENT"
mkcase m5; : > "$W/m5/mangle"; run m5 "$(MBP rb)" --repo o/r 7 "$HEAD" "$W/body.md"; rc=$?
st "$rc$(grep -c '^body_patch: OK' "$W/m5/out")" 01 "MUTANT body read-back deleted: a mangled body now reads OK"
mkcase m6; : > "$W/m6/move-at-2"; run m6 "$(MBP rbhead)" --repo o/r 7 "$HEAD" "$W/body.md"; rc=$?
st "$rc$(grep -c '^body_patch: OK' "$W/m6/out")" 01 "MUTANT head re-read deleted: a head moved around the write now reads OK"

echo "body_patch self-test: $N checks, $FAILS failed"
[ "$FAILS" -eq 0 ]
