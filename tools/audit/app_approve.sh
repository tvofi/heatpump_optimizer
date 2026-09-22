#!/bin/bash
{ set +x; } 2>/dev/null # before anything: a caller's `bash -x` would trace the JWT
# Approve a pull request as the App `hpo-approver`, at one exact head SHA, and
# only on a `merge` verdict for that SHA from an allowlisted account.
#
#   tools/audit/app_approve.sh [--dry-run] <owner/repo> <pr> <40-hex head sha>
#   tools/audit/app_approve.sh --self-test
#
# WHY THIS EXISTS. Since decision 0009 step 6, the `main-protect-checks`
# ruleset requires one approving review, and GitHub never lets an author
# approve their own pull request. An ordinary pull request's review comes from
# the App after a `merge` verdict (`tools/audit/briefs/orchestrator.md`
# section 11); a policy pull request's comes from the owner, on GitHub, and
# this script refuses one.
#
# IT REFUSES, AND POSTS NOTHING, UNLESS ALL OF THESE HOLD:
#   - the App id file holds digits only and the private key file exists
#     (fail closed, before any call);
#   - the pull request is open, and its live head is exactly <sha>;
#   - among comments whose author is in VERDICT_AUTHORS AND whose
#     author_association is OWNER, MEMBER or COLLABORATOR, the NEWEST whose
#     first line starts `Fix review:` is exactly `Fix review: merge <sha>` --
#     the grammar `fix-review.md` sends reviewers to. Every other comment is
#     ignored, so an outsider's later line neither approves nor displaces one.
#     Verdicts post only as `tvofi` (decision 0011: the reviewer seat hands
#     the verdict text to the orchestrator, who posts it as `tvofi`; pull
#     requests author as the `hpo-author` App, never as a verdict author).
#     WHAT THIS CANNOT TELL: the allowlist still cannot prove WHICH seat's
#     word a `tvofi` verdict carries. It keeps out every other account,
#     nothing more;
#   - that verdict CITES ITS EVIDENCE: at least one absolute path in the
#     verdict comment's body is a directory that exists ON THIS MACHINE (the
#     box is shared, `COMMON.md`), is non-empty, and has at least one file
#     naming the exact 40-hex head <sha>. A fabricated `merge` line must now
#     fabricate artifacts too. WHAT THIS IS NOT: proof of reviewer
#     independence -- this script runs on the orchestrator's machine over
#     text a seat wrote, and `judge.md`'s void rule names that shape: a
#     check run by the same party on that party's text proves nothing. The
#     independent reviewer under `fix-review.md` stays the load-bearing
#     control; this gate raises the cost of a forged verdict, it does not
#     replace the seat;
#   - no changed file (or a rename's old path) matches an owned pattern of
#     `.github/CODEOWNERS` read at ref=main, never at the head; an unreadable
#     or empty CODEOWNERS refuses. Matching errs toward owning, which refuses;
#   - the head is still <sha> when re-read after minting, just before the POST.
#
# THE SECRETS. The key files are `$HPO_IDENTITY_DIR/identity-approver.appid`
# and `identity-approver.pem` (default directory `~/.zcode`). The JWT and the
# installation token are written only as curl header files inside a private
# mode-700 directory, never onto a command line and never printed. An EXIT trap
# revokes the installation token (DELETE /installation/token) and removes that
# directory on every path, the refusals and a failed POST included. Reads go
# through `gh` as whatever GH_TOKEN the seat set; only the App calls carry the
# JWT or the token.
#
# --dry-run runs every refusal, then stops before signing or minting anything.
set -uo pipefail

API=https://api.github.com
ACCEPT='Accept: application/vnd.github+json'
VERDICT_AUTHORS="tvofi"
die() { printf 'app_approve: REFUSE: %s\n' "$*" >&2; exit 1; }

# A JSON document per page from `gh api --paginate`, flattened to one list.
PAGES_PY='import sys,json
raw=sys.stdin.read(); dec=json.JSONDecoder(); i=0; out=[]
while True:
    while i < len(raw) and raw[i].isspace(): i += 1
    if i >= len(raw): break
    v, i = dec.raw_decode(raw, i); out.extend(v)'

check_pr() { # repo pr sha -> refuses unless open at exactly sha
  local js info state merged head
  js=$(gh api "repos/$1/pulls/$2") || die "could not read pull request #$2 on $1"
  info=$(printf '%s' "$js" | python3 -c 'import sys,json
d=json.load(sys.stdin); print(d["state"], str(d.get("merged")).lower(), d["head"]["sha"])') \
    || die "pull request #$2's JSON has no state or head"
  read -r state merged head <<<"$info"
  [ "$state" = "open" ] || die "pull request #$2 is $state (merged=$merged); only an open one is approved"
  [ "$head" = "$3" ] || die "head moved: asked to approve $3, the live head of #$2 is $head"
}

cleanup() {
  if [ -s "$PRIV/token.h" ]; then
    curl -fsS -X DELETE -H @"$PRIV/token.h" -H "$ACCEPT" "$API/installation/token" >/dev/null 2>&1 \
      || printf 'app_approve: warning: revoking the installation token failed; it expires within the hour\n' >&2
  fi
  rm -rf "$PRIV"
}

approve() {
  local dry=0
  [ "${1:-}" = "--dry-run" ] && { dry=1; shift; }
  [ $# -eq 3 ] || die "usage: app_approve.sh [--dry-run] <owner/repo> <pr> <40-hex head sha>"
  local repo=$1 pr=$2 sha=$3
  [[ $repo =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || die "repo '$repo' is not owner/repo"
  [[ $pr =~ ^[0-9]+$ ]] || die "pull request '$pr' is not a number"
  [[ $sha =~ ^[0-9a-f]{40}$ ]] || die "the head must be the full 40-hex SHA, got '$sha'"
  local idir="${HPO_IDENTITY_DIR:-$HOME/.zcode}"
  local appid_f="$idir/identity-approver.appid" key="$idir/identity-approver.pem"
  [ -s "$appid_f" ] || die "App id file missing or empty: $appid_f (fail closed)"
  [ -s "$key" ] || die "App private key missing or empty: $key (fail closed)"
  local appid; appid=$(cat "$appid_f")
  [[ $appid =~ ^[0-9]+$ ]] || die "App id file must hold digits only: $appid_f (fail closed)"

  check_pr "$repo" "$pr" "$sha"
  local verdict vid vurl vline vbody
  # The body rides as a fourth line with newlines folded to \x01, so a body
  # with spaces survives the shell round trip whole -- the evidence gate
  # below reads it, not only the first line.
  verdict=$(gh api --paginate "repos/$repo/issues/$pr/comments?per_page=100" | python3 -c "$PAGES_PY"'
authors = set(sys.argv[1].split()); assoc = {"OWNER", "MEMBER", "COLLABORATOR"}
vs = [c for c in out
      if (c.get("user") or {}).get("login") in authors and c.get("author_association") in assoc
      and (c.get("body") or "").split("\n", 1)[0].strip().lower().startswith("fix review:")]
vs.sort(key=lambda c: (c["created_at"], c["id"]))
if not vs: print("NONE")
else:
    c = vs[-1]
    print(c["id"]); print(c["html_url"])
    print(c["body"].split("\n", 1)[0].strip())
    print((c.get("body") or "").replace("\n", "\x01"))' "$VERDICT_AUTHORS") \
    || die "could not read the comments on #$pr"
  [ "$verdict" != "NONE" ] \
    || die "no 'Fix review:' verdict on #$pr from an allowlisted collaborator ($VERDICT_AUTHORS); an approval needs 'Fix review: merge $sha'"
  vid=$(printf '%s\n'   "$verdict" | sed -n 1p)
  vurl=$(printf '%s\n'  "$verdict" | sed -n 2p)
  vline=$(printf '%s\n' "$verdict" | sed -n 3p)
  vbody=$(printf '%s\n' "$verdict" | sed -n 4p)
  vbody=${vbody//$'\x01'/$'\n'}
  [ "$vline" = "Fix review: merge $sha" ] \
    || die "the newest allowlisted verdict on #$pr ($vurl) is '$vline', not 'Fix review: merge $sha'"

  # The verdict's evidence gate, before minting. At least one absolute path
  # the body names must be a directory that exists here, is non-empty, and
  # holds a file naming the exact head sha. Fail closed on every miss; the
  # header says what this is not.
  local evdir="" evwhy="the verdict names no absolute path at all" tok
  while read -r tok; do
    tok=$(printf '%s' "$tok" | sed -e "s/^[(\`\"']*//" -e "s/[.,;:)\`\"']*$//")
    [ -n "$tok" ] || continue
    case "$tok" in /*) ;; *) continue ;; esac
    if [ ! -d "$tok" ]; then evwhy="$tok is not a directory that exists"; continue; fi
    if [ -z "$(ls -A "$tok" 2>/dev/null)" ]; then evwhy="$tok is empty"; continue; fi
    if grep -rqF -- "$sha" "$tok" 2>/dev/null; then evdir=$tok; break; fi
    evwhy="no file under $tok names the head $sha"
  done < <(printf '%s\n' "$vbody" | grep -oE "/[^[:space:]\`\"]+")
  [ -n "$evdir" ] \
    || die "the verdict ($vurl) cites no qualifying evidence: $evwhy. An approval needs a directory the verdict names that exists on this machine, is non-empty, and holds a file naming the exact head $sha"

  local owners files owned
  owners=$(gh api "repos/$repo/contents/.github/CODEOWNERS?ref=main") \
    || die "could not read .github/CODEOWNERS at ref=main (fail closed)"
  files=$(gh api --paginate "repos/$repo/pulls/$pr/files?per_page=100") \
    || die "could not list the files of #$pr (fail closed)"
  owned=$(printf '%s' "$files" | python3 -c "$PAGES_PY"'
import base64, fnmatch
text = base64.b64decode(json.loads(sys.argv[1])["content"]).decode()
rules = []
for line in text.splitlines():
    line = line.split("#", 1)[0].split()
    if line: rules.append((line[0], line[1:]))
if not rules: sys.exit("CODEOWNERS at ref=main holds no rules")
def hit(pat, path):
    anchored = pat.startswith("/"); p = pat.strip("/")
    if p in ("", "*", "**"): return True
    if pat.endswith("/") or not any(ch in p for ch in "*?["):
        if anchored or "/" in p: return path == p or path.startswith(p + "/")
        return p in path.split("/")
    if anchored or "/" in p: return fnmatch.fnmatch(path, p) or fnmatch.fnmatch(path, p + "/*")
    return any(fnmatch.fnmatch(seg, p) for seg in path.split("/")) or fnmatch.fnmatch(path, p)
paths = set()
for f in out:
    paths.add(f["filename"])
    if f.get("previous_filename"): paths.add(f["previous_filename"])
for path in sorted(paths):
    last = None
    for pat, who in rules:
        if hit(pat, path): last = who
    if last: print(path)' "$owners") || die "could not match #$pr's files against CODEOWNERS (fail closed)"
  [ -z "$owned" ] || die "#$pr touches code-owned paths ($(printf '%s' "$owned" | tr '\n' ' ')); the owner's GitHub review approves it, not the App"

  if [ "$dry" = 1 ]; then
    printf 'app_approve: DRY-RUN: every refusal passed; would mint a token and APPROVE #%s at %s on %s; signed, minted and posted nothing\n' "$pr" "$sha" "$vurl"
    exit 0
  fi

  umask 077
  PRIV=$(mktemp -d "${TMPDIR:-/tmp}/app_approve.XXXXXX") || die "could not create a private directory"
  trap cleanup EXIT
  trap 'exit 130' INT TERM HUP
  chmod 700 "$PRIV"
  b64() { openssl base64 -A | tr '+/' '-_' | tr -d '='; }
  local now h p s inst
  now=$(date +%s)
  h=$(printf '{"alg":"RS256","typ":"JWT"}' | b64)
  p=$(printf '{"iat":%d,"exp":%d,"iss":"%s"}' $((now - 60)) $((now + 540)) "$appid" | b64)
  s=$(printf '%s.%s' "$h" "$p" | openssl dgst -sha256 -sign "$key" -binary | b64) && [ -n "$s" ] \
    || die "signing the App JWT with $key failed"
  printf 'Authorization: Bearer %s.%s.%s\n' "$h" "$p" "$s" > "$PRIV/jwt.h"
  inst=$(curl -fsS -H @"$PRIV/jwt.h" -H "$ACCEPT" "$API/repos/$repo/installation" \
    | python3 -c 'import sys,json; print(int(json.load(sys.stdin)["id"]))') \
    || die "the App has no installation on $repo, or its JWT was refused"
  curl -fsS -X POST -H @"$PRIV/jwt.h" -H "$ACCEPT" "$API/app/installations/$inst/access_tokens" \
    | python3 -c 'import sys,json
t = json.load(sys.stdin)["token"]
open(sys.argv[1], "w").write("Authorization: Bearer %s\n" % t)' "$PRIV/token.h" && [ -s "$PRIV/token.h" ] \
    || die "minting the installation token failed"
  chmod 600 "$PRIV/token.h"

  check_pr "$repo" "$pr" "$sha"
  python3 -c 'import sys,json
sha, url, f = sys.argv[1:4]
json.dump({"commit_id": sha, "event": "APPROVE",
  "body": "Approved by `hpo-approver` at `%s` on the verdict %s (`Fix review: merge %s`), via `tools/audit/app_approve.sh`." % (sha, url, sha)},
  open(f, "w"))' "$sha" "$vurl" "$PRIV/review.json" || die "could not write the review payload"
  local resp
  resp=$(curl -fsS -X POST -H @"$PRIV/token.h" -H "$ACCEPT" "$API/repos/$repo/pulls/$pr/reviews" \
    --data-binary @"$PRIV/review.json") || die "the review POST was refused; nothing approved"
  printf '%s' "$resp" | python3 -c 'import sys,json
d = json.load(sys.stdin); sha = sys.argv[1]
line = "review id=%s state=%s commit_id=%s user=%s" % (d.get("id"), d.get("state"), d.get("commit_id"), (d.get("user") or {}).get("login"))
if d.get("state") != "APPROVED" or d.get("commit_id") != sha:
    sys.exit("app_approve: REFUSE: the posted review does not read back as APPROVED at %s: %s" % (sha, line))
print("app_approve: APPROVED " + line)' "$sha"
}

if [ "${1:-}" != "--self-test" ]; then
  approve "$@"
  exit $?
fi

# ---------------------------------------------------------------------------
# --self-test: `gh`, `curl` and `openssl` are stubs on PATH; no network, no key.
# Every refusal is paired with the healthy run it must NOT refuse, and every run
# gets its own TMPDIR, so "the private directory is gone" is read off the tree.
SELF="$(cd "$(dirname -- "$0")" && pwd)/$(basename -- "$0")"
W=$(mktemp -d) || exit 2
trap 'rm -rf "$W"' EXIT
FAILS=0; N=0
st() { N=$((N + 1)); if [ "$1" = "$2" ]; then echo "ok   $3"; else echo "FAIL $3 (got '$1', want '$2')"; FAILS=$((FAILS + 1)); fi; }
SHA=1111111111111111111111111111111111111111
OTHER=2222222222222222222222222222222222222222
TOKEN=ghs_STUBTOKEN_must_never_print
JWTHEAD=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9   # base64url of the JWT header
SIGB64=U1RVQlNJR05BVFVSRQ                      # base64url of STUBSIGNATURE
mkdir -p "$W/bin" "$W/id" "$W/nokey" "$W/badid"
printf '424242\n' > "$W/id/identity-approver.appid"; cp "$W/id/identity-approver.appid" "$W/nokey/"
printf -- '-----BEGIN STUB KEY-----\nSTUBKEYMATERIAL\n-----END STUB KEY-----\n' > "$W/id/identity-approver.pem"
cp "$W/id/identity-approver.pem" "$W/badid/"; printf '4242a\n' > "$W/badid/identity-approver.appid"
# The evidence directory a healthy verdict cites: real files, real grep, so
# the gate's own commands run in the self-test rather than only its inputs.
EV="$W/evidence"; mkdir -p "$EV"
printf 'fix review at head %s\nRESULT: merge clean\n' "$SHA" > "$EV/verdict.md"
CODEOWNERS_TEXT='# owned
/CLAUDE.md @tvofi
/tools/audit/briefs/ @tvofi
/tools/audit/briefs/COMMON.md
'
python3 -c 'import sys,json,base64; print(json.dumps({"encoding": "base64", "content": base64.b64encode(sys.argv[1].encode()).decode()}))' \
  "$CODEOWNERS_TEXT" > "$W/codeowners.json"

cat > "$W/bin/gh" <<'STUB'
#!/bin/bash
printf 'gh %s\n' "$*" >> "$STUB/log"
case "$*" in
  "api repos/o/r/pulls/7")
    n=$(grep -c '^gh api repos/o/r/pulls/7$' "$STUB/log")
    if [ "$n" -gt 1 ] && [ -f "$STUB/pr2.json" ]; then cat "$STUB/pr2.json"; else cat "$STUB/pr.json"; fi ;;
  "api --paginate repos/o/r/issues/7/comments?per_page=100")
    cat "$STUB/c1.json"; [ -f "$STUB/c2.json" ] && cat "$STUB/c2.json"; true ;;
  "api repos/o/r/contents/.github/CODEOWNERS?ref=main")
    [ -f "$STUB/no-codeowners" ] && { echo "HTTP 404" >&2; exit 1; }
    if [ -f "$STUB/codeowners.json" ]; then cat "$STUB/codeowners.json"; else cat "$STUB/../codeowners.json"; fi ;;
  "api --paginate repos/o/r/pulls/7/files?per_page=100")
    cat "$STUB/files.json" ;;
  *) exit 9 ;;
esac
STUB
cat > "$W/bin/openssl" <<'STUB'
#!/bin/bash
printf 'openssl %s\n' "$*" >> "$STUB/log"
case "$1" in
  base64) base64 | tr -d '\n' ;;
  dgst) [ -s "$4" ] || exit 1; cat >/dev/null; printf 'STUBSIGNATURE' ;;
  *) exit 9 ;;
esac
STUB
cat > "$W/bin/curl" <<'STUB'
#!/bin/bash
url=""; data=""; hdr=""
for a in "$@"; do
  case "$a" in https://*) url="$a" ;; @*.json) data="${a#@}" ;; @*.h) hdr="${a#@}" ;; esac
done
printf 'curl %s\n' "${url#https://api.github.com/}" >> "$STUB/log"
case "$url" in
  */repos/o/r/installation) cp "$hdr" "$STUB/jwtcopy"; printf '{"id": 99}' ;;
  */app/installations/99/access_tokens)
    printf '{"token": "ghs_STUBTOKEN_must_never_print", "permissions": {"pull_requests": "write"}}' ;;
  */installation/token) grep -q 'ghs_STUBTOKEN' "$hdr" || exit 22 ;;
  */repos/o/r/pulls/7/reviews)
    ls -l "$hdr" | cut -c1-10 > "$STUB/tokenmode"; cp "$hdr" "$STUB/tokencopy"; cp "$data" "$STUB/posted.json"
    if [ -f "$STUB/refuse-post" ]; then echo "curl: (22) The requested URL returned error: 422" >&2; exit 22; fi
    python3 -c 'import sys,json; d=json.load(open(sys.argv[1])); print(json.dumps({"id": 5, "state": "APPROVED", "commit_id": d["commit_id"], "user": {"login": "hpo-approver[bot]"}}))' "$data" ;;
  *) exit 9 ;;
esac
STUB
chmod +x "$W/bin/gh" "$W/bin/openssl" "$W/bin/curl"

pr_json() { printf '{"state": "%s", "merged": %s, "head": {"sha": "%s"}}' "$1" "$2" "$3"; }
comment() { # id first-line [login [association [extra-body-line]]]
  printf '{"id": %s, "created_at": "2026-09-17T0%s:00:00Z", "html_url": "https://example.test/c%s", "user": {"login": "%s"}, "author_association": "%s", "body": "%s\\nRESULT x%s"}' \
    "$1" "$1" "$1" "${3:-seat-retired-login}" "${4:-COLLABORATOR}" "$2" "${5:+\\n$5}"
}
files_json() { # path... -> a pulls/N/files page
  python3 -c 'import sys,json; print(json.dumps([{"filename": p, "status": "modified"} for p in sys.argv[1:]]))' "$@"
}
mkcase() { # name state merged head comments-json
  local d="$W/$1"; mkdir -p "$d/tmp"; : > "$d/log"
  pr_json "$2" "$3" "$4" > "$d/pr.json"; printf '%s' "$5" > "$d/c1.json"
  files_json tools/audit/app_approve.sh docs/delivery/7.md > "$d/files.json"
}
run() { # name args... -> rc; out/err captured. BASHX=1 runs the tool under bash -x
  local d="$W/$1"; shift
  ( export STUB="$d" PATH="$W/bin:$PATH" TMPDIR="$d/tmp" HPO_IDENTITY_DIR="${IDDIR:-$W/id}"
    if [ "${BASHX:-}" = 1 ]; then bash -x "$SELF" "$@"; else bash "$SELF" "$@"; fi > "$d/out" 2> "$d/err" )
}
calls() { grep -c "^$2" "$W/$1/log"; }
leftover() { find "$W/$1/tmp" -mindepth 1 | wc -l | tr -d ' '; }
leaks() { cat "$W/$1/out" "$W/$1/err" | grep -c -e "$TOKEN" -e STUBKEYMATERIAL -e STUBSIGNATURE -e "$JWTHEAD" -e "$SIGB64"; }
GOOD="[$(comment 1 'An ordinary comment'),$(comment 2 "Fix review: merge $SHA" tvofi COLLABORATOR "evidence: $EV")]"

mkcase ok open false "$SHA" "$GOOD"
run ok o/r 7 "$SHA"; st $? 0 "a merge verdict at the live head of an open, unowned pull request is approved"
st "$(calls ok 'curl repos/o/r/pulls/7/reviews')" 1 "with exactly one review POST"
st "$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d["event"], d["commit_id"])' "$W/ok/posted.json")" \
   "APPROVE $SHA" "whose event is APPROVE and whose commit_id is the asked-for SHA"
st "$(grep -c 'https://example.test/c2' "$W/ok/posted.json")" 1 "and whose body cites the verdict comment"
st "$(grep -c "Bearer $TOKEN" "$W/ok/tokencopy")" 1 "the POST carried the installation token, from a header file"
st "$(cat "$W/ok/tokenmode")" "-rw-------" "and that header file was mode 600 while it existed"
st "$(calls ok 'gh api repos/o/r/pulls/7$')" 2 "the head was read twice: before the mint and again before the POST"
st "$(calls ok 'curl installation/token')" 1 "the installation token is revoked on exit"
st "$(leftover ok)" 0 "the private directory is gone after a success"
st "$(leaks ok)" 0 "no token, JWT, key or signature text in stdout or stderr after a success"
st "$(grep -c "$TOKEN" "$W/ok/tokencopy")" 1 "(null control: the leak grep does find the token where it really is)"
st "$(grep -c -e "$JWTHEAD" "$W/ok/jwtcopy")" 1 "(null control: and the JWT header, where it really is)"
st "$(grep -c '^app_approve: APPROVED review id=5 state=APPROVED' "$W/ok/out")" 1 "and the read-back line is printed"
st "$(grep -c "$SHA" "$EV/verdict.md")" 1 "(fixture: the evidence dir names the head, so the approval above passed the gate honestly)"

mkcase xtrace open false "$SHA" "$GOOD"
BASHX=1 run xtrace o/r 7 "$SHA"; st $? 0 "under bash -x the approval still runs"
st "$(leaks xtrace)" 0 "and no token, JWT, key or signature text reaches the trace"
st "$(grep -c "$JWTHEAD" "$W/xtrace/jwtcopy")" 1 "(null control: a JWT was signed on that run)"

mkcase moved open false "$OTHER" "$GOOD"
run moved o/r 7 "$SHA"; st $? 1 "REFUSE: the live head moved off the asked-for SHA"
st "$(grep -c 'head moved' "$W/moved/err")" 1 "naming the moved head"
st "$(calls moved curl)" 0 "and nothing was minted or posted"

mkcase late open false "$SHA" "$GOOD"; pr_json open false "$OTHER" > "$W/late/pr2.json"
run late o/r 7 "$SHA"; st $? 1 "REFUSE: the head moved between the mint and the POST"
st "$(calls late 'curl repos/o/r/pulls/7/reviews')" 0 "and no review was posted"
st "$(calls late 'curl installation/token')" 1 "the minted token is revoked after that refusal"
st "$(leftover late)" 0 "and the private directory is gone, token and all"

mkcase merged closed true "$SHA" "$GOOD"
run merged o/r 7 "$SHA"; st $? 1 "REFUSE: a merged pull request, even at its own head with a merge verdict"
st "$(calls merged curl)" 0 "and nothing was minted or posted"

mkcase none open false "$SHA" "[$(comment 1 'An ordinary comment')]"
run none o/r 7 "$SHA"; st $? 1 "REFUSE: no Fix review verdict at all"
st "$(grep -c "no 'Fix review:' verdict" "$W/none/err")" 1 "saying so, not falling through to the SHA comparison"
st "$(calls none curl)" 0 "and nothing was minted or posted"

mkcase stale open false "$SHA" "[$(comment 1 "Fix review: merge $OTHER" tvofi)]"
run stale o/r 7 "$SHA"; st $? 1 "REFUSE: the merge verdict is for another SHA"
st "$(grep -c "is 'Fix review: merge $OTHER'" "$W/stale/err")" 1 "naming the SHA the verdict is for"

mkcase blocked open false "$SHA" "$GOOD"
printf '[%s]' "$(comment 3 "Fix review: blocked $SHA claims: moved" tvofi)" > "$W/blocked/c2.json"
run blocked o/r 7 "$SHA"; st $? 1 "REFUSE: a newer blocked verdict, on a later page, overrides an older merge"

mkcase outsider open false "$SHA" "[$(comment 1 "Fix review: merge $SHA" mallory NONE)]"
run outsider o/r 7 "$SHA"; st $? 1 "REFUSE: a merge verdict from an outsider (association NONE)"
st "$(calls outsider curl)" 0 "and nothing was minted or posted"
mkcase contrib open false "$SHA" "[$(comment 1 "Fix review: merge $SHA" mallory CONTRIBUTOR)]"
run contrib o/r 7 "$SHA"; st $? 1 "REFUSE: a merge verdict from a CONTRIBUTOR outside the allowlist"
mkcase badassoc open false "$SHA" "[$(comment 1 "Fix review: merge $SHA" tvofi NONE)]"
run badassoc o/r 7 "$SHA"; st $? 1 "REFUSE: an allowlisted login without a collaborator association"
mkcase retired open false "$SHA" "[$(comment 1 "Fix review: merge $SHA" seat-retired-login COLLABORATOR "evidence: $EV")]"
run retired o/r 7 "$SHA"; st $? 1 "REFUSE: a verdict from the retired seat account is outside the allowlist"
st "$(grep -c "no 'Fix review:' verdict" "$W/retired/err")" 1 "read as no allowlisted verdict, its evidence dir notwithstanding"
st "$(calls retired curl)" 0 "and nothing was minted or posted"
mkcase evmissing open false "$SHA" "[$(comment 1 "Fix review: merge $SHA" tvofi COLLABORATOR "evidence: /tmp/hpo-orch/fixer-identity/no-such-review-dir")]"
run evmissing o/r 7 "$SHA"; st $? 1 "REFUSE: the verdict cites an evidence directory that does not exist"
st "$(grep -c 'is not a directory that exists' "$W/evmissing/err")" 1 "naming the missing directory"
st "$(calls evmissing curl)" 0 "and nothing was minted or posted"
mkdir -p "$W/evnosha-dir"; printf 'a review that names no head at all\n' > "$W/evnosha-dir/notes.md"
mkcase evnosha open false "$SHA" "[$(comment 1 "Fix review: merge $SHA" tvofi COLLABORATOR "evidence: $W/evnosha-dir")]"
run evnosha o/r 7 "$SHA"; st $? 1 "REFUSE: the evidence directory holds no file naming the head"
st "$(grep -c 'names the head' "$W/evnosha/err")" 1 "naming the exact-sha rule it failed"
st "$(calls evnosha curl)" 0 "and nothing was minted or posted"
mkcase displace open false "$SHA" \
  "[$(comment 1 "Fix review: blocked $SHA other: bad" tvofi),$(comment 2 "Fix review: merge $SHA" mallory NONE)]"
run displace o/r 7 "$SHA"; st $? 1 "REFUSE: an outsider's later merge does not displace an allowlisted blocked"
st "$(grep -c "is 'Fix review: blocked $SHA" "$W/displace/err")" 1 "the allowlisted blocked verdict is the one read"
mkcase notdisplace open false "$SHA" \
  "[$(comment 1 "Fix review: merge $SHA" tvofi OWNER "evidence: $EV"),$(comment 2 "Fix review: blocked $SHA other: x" mallory NONE)]"
run notdisplace o/r 7 "$SHA"; st $? 0 "an outsider's later blocked does not displace an allowlisted merge either"

mkcase policy open false "$SHA" "$GOOD"; files_json docs/x.md tools/audit/briefs/fixer.md > "$W/policy/files.json"
run policy o/r 7 "$SHA"; st $? 1 "REFUSE: a pull request touching a CODEOWNERS path"
st "$(grep -c 'code-owned paths (tools/audit/briefs/fixer.md)' "$W/policy/err")" 1 "naming the owned path"
st "$(calls policy curl)" 0 "and nothing was minted or posted"
mkcase rootpolicy open false "$SHA" "$GOOD"; files_json CLAUDE.md > "$W/rootpolicy/files.json"
run rootpolicy o/r 7 "$SHA"; st $? 1 "REFUSE: an exact owned file at the root"
mkcase renamed open false "$SHA" "$GOOD"
printf '[{"filename": "docs/moved.md", "status": "renamed", "previous_filename": "CLAUDE.md"}]' > "$W/renamed/files.json"
run renamed o/r 7 "$SHA"; st $? 1 "REFUSE: a rename whose OLD path is owned"
mkcase unowned open false "$SHA" "$GOOD"; files_json tools/audit/briefs/COMMON.md tools/audit/push.sh > "$W/unowned/files.json"
run unowned o/r 7 "$SHA"; st $? 0 "a later owner-less line un-owns: COMMON.md is approvable (last match wins)"
mkcase nocodeowners open false "$SHA" "$GOOD"; : > "$W/nocodeowners/no-codeowners"
run nocodeowners o/r 7 "$SHA"; st $? 1 "REFUSE: CODEOWNERS unreadable at ref=main, failing closed"
st "$(grep -c 'ref=main' "$W/nocodeowners/log")" 1 "and it was asked for at ref=main"
mkcase emptycodeowners open false "$SHA" "$GOOD"
printf '{"encoding": "base64", "content": "%s"}' "$(printf '# comments only\n' | base64 | tr -d '\n')" > "$W/emptycodeowners/codeowners.json"
run emptycodeowners o/r 7 "$SHA"; st $? 1 "REFUSE: a CODEOWNERS holding no rules, failing closed"

mkcase nokey open false "$SHA" "$GOOD"
IDDIR="$W/nokey" run nokey o/r 7 "$SHA"; st $? 1 "REFUSE: the App private key is missing"
st "$(grep -c 'private key missing' "$W/nokey/err")" 1 "failing closed with a clear message"
st "$(wc -l < "$W/nokey/log" | tr -d ' ')" 0 "before any gh, openssl or curl call"

mkcase badid open false "$SHA" "$GOOD"
IDDIR="$W/badid" run badid o/r 7 "$SHA"; st $? 1 "REFUSE: an App id with a non-digit in it"
st "$(grep -c 'digits only' "$W/badid/err")" 1 "refused as malformed, not stripped to digits"
st "$(wc -l < "$W/badid/log" | tr -d ' ')" 0 "before any gh, openssl or curl call"

mkcase shortsha open false "$SHA" "$GOOD"
run shortsha o/r 7 "${SHA:0:7}"; st $? 1 "REFUSE: an abbreviated SHA is not an exact head"
st "$(grep -c 'full 40-hex SHA' "$W/shortsha/err")" 1 "refused as a malformed argument, before any call"

mkcase postfail open false "$SHA" "$GOOD"; : > "$W/postfail/refuse-post"
run postfail o/r 7 "$SHA"; st $? 1 "a refused POST exits non-zero"
st "$(calls postfail 'curl installation/token')" 1 "the token is revoked after the failed POST"
st "$(leftover postfail)" 0 "the private directory is gone after the failed POST"
st "$(grep -c "$TOKEN" "$W/postfail/tokencopy")" 1 "(the token header file did exist during that POST)"
st "$(leaks postfail)" 0 "and no token, JWT, key or signature text reached stdout or stderr"

mkcase dry open false "$SHA" "$GOOD"
run dry --dry-run o/r 7 "$SHA"; st $? 0 "--dry-run passes every refusal"
st "$(calls dry curl)" 0 "and makes no curl call: nothing minted, nothing posted"
st "$(calls dry openssl)" 0 "and signs nothing"
st "$(grep -c '^app_approve: DRY-RUN' "$W/dry/out")" 1 "reporting what it would do"
mkcase drypolicy open false "$SHA" "$GOOD"; files_json CLAUDE.md > "$W/drypolicy/files.json"
run drypolicy --dry-run o/r 7 "$SHA"; st $? 1 "--dry-run still refuses what a real run would"

echo "app_approve self-test: $N checks, $FAILS failed"
[ "$FAILS" -eq 0 ]
