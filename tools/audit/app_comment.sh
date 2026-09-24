#!/bin/bash
{ set +x; } 2>/dev/null # before anything: a caller's `bash -x` would trace the JWT
# Post one fix-review verdict on a pull request as the App `hpo-approver`, and
# read it back byte-identical -- the verdict identity of decision 0013, which
# amends 0011's "verdicts are `tvofi`".
#
#   tools/audit/app_comment.sh [--dry-run] <owner/repo> <pr> <verdict.md>
#   tools/audit/app_comment.sh --self-test
#
# WHY THIS EXISTS. The owner ruled on 2026-09-24 that verdicts come from the
# approver identity, not from `tvofi`. Seats hold no App credential (0011), so
# the reviewer seat hands its verdict text to the orchestrator, who runs this.
# `tools/audit/app_approve.sh` then accepts only a verdict whose author is the
# approver App, so a verdict posted any other way is not one it will act on.
# A verdict never posts as the AUTHOR App (#1233's defect): this reads only the
# approver's key files, and refuses a post that reads back as anyone else.
#
# IT REFUSES, AND POSTS NOTHING, UNLESS ALL OF THESE HOLD:
#   - the App id file holds digits only and the private key file exists
#     (fail closed, before any call);
#   - `.claude/workflows/gh_comment.py post --dry-run` accepts the body file:
#     not absent, empty, over GitHub's cap, a bare path (`-f body=@FILE`), or
#     directly in a root other seats write to (`comment-readback.md`);
#   - the body's first line is a verdict in `fix-review.md`'s grammar:
#     exactly `Fix review: merge <40-hex>`, or `Fix review: blocked <40-hex>
#     <class>: <why>`. This is a verdict poster, not a general App voice;
#   - the pull request is open, and for a `merge` verdict its live head is
#     exactly the verdict's SHA -- read before the mint and again just before
#     the POST (`fix-review.md` step 12). A `blocked` verdict may name a head
#     that moved (`head-moved: measured <sha>, head is <other>`), so it is
#     not held to the live head.
#
# AFTER THE POST it refuses (exit non-zero) unless the created comment's user
# is `hpo-approver[bot]` of type `Bot`, and unless `gh_comment.py verify`
# reads the comment back off the API byte-identical to the file. A post whose
# read-back fails is left on the record and the refusal names its id; nothing
# here deletes a comment.
#
# THE SECRETS are `app_approve.sh`'s: `$HPO_IDENTITY_DIR/identity-approver.appid`
# and `identity-approver.pem` (default directory `~/.zcode`). The JWT and the
# installation token live only as curl header files in a mode-700 mktemp
# directory, never on a command line and never printed; an EXIT trap revokes
# the token and removes the directory on every path. Reads go through `gh` as
# whatever GH_TOKEN the caller set; only the App calls carry the JWT or token.
#
# --dry-run runs every refusal, then stops before signing or minting anything.
set -uo pipefail

API=https://api.github.com
ACCEPT='Accept: application/vnd.github+json'
APP_LOGIN='hpo-approver[bot]'
GH_COMMENT="$(cd "$(dirname -- "$0")/../.." && pwd)/.claude/workflows/gh_comment.py"
die() { printf 'app_comment: REFUSE: %s\n' "$*" >&2; exit 1; }

check_pr() { # repo pr [sha] -> refuses unless open (and, given a sha, at exactly it)
  local js info state head
  js=$(gh api "repos/$1/pulls/$2") || die "could not read pull request #$2 on $1"
  info=$(printf '%s' "$js" | python3 -c 'import sys,json
d=json.load(sys.stdin); print(d["state"], d["head"]["sha"])') \
    || die "pull request #$2's JSON has no state or head"
  read -r state head <<<"$info"
  [ "$state" = "open" ] || die "pull request #$2 is $state; a verdict posts only on an open one"
  [ -z "${3:-}" ] || [ "$head" = "$3" ] \
    || die "head moved: the merge verdict names $3, the live head of #$2 is $head"
}

cleanup() {
  if [ -s "$PRIV/token.h" ]; then
    curl -fsS -X DELETE -H @"$PRIV/token.h" -H "$ACCEPT" "$API/installation/token" >/dev/null 2>&1 \
      || printf 'app_comment: warning: revoking the installation token failed; it expires within the hour\n' >&2
  fi
  rm -rf "$PRIV"
}

post() {
  local dry=0
  [ "${1:-}" = "--dry-run" ] && { dry=1; shift; }
  [ $# -eq 3 ] || die "usage: app_comment.sh [--dry-run] <owner/repo> <pr> <verdict.md>"
  local repo=$1 pr=$2 body=$3
  [[ $repo =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || die "repo '$repo' is not owner/repo"
  [[ $pr =~ ^[0-9]+$ ]] || die "pull request '$pr' is not a number"
  local idir="${HPO_IDENTITY_DIR:-$HOME/.zcode}"
  local appid_f="$idir/identity-approver.appid" key="$idir/identity-approver.pem"
  [ -s "$appid_f" ] || die "App id file missing or empty: $appid_f (fail closed)"
  [ -s "$key" ] || die "App private key missing or empty: $key (fail closed)"
  local appid; appid=$(cat "$appid_f")
  [[ $appid =~ ^[0-9]+$ ]] || die "App id file must hold digits only: $appid_f (fail closed)"

  python3 "$GH_COMMENT" post --dry-run --repo "$repo" --issue "$pr" --body-file "$body" >/dev/null \
    || die "gh_comment.py refused the body file $body (its REFUSED line above says why)"
  local first sha kind
  first=$(head -n 1 -- "$body")
  if [[ $first =~ ^Fix\ review:\ merge\ ([0-9a-f]{40})$ ]]; then kind=merge; sha=${BASH_REMATCH[1]}
  elif [[ $first =~ ^Fix\ review:\ blocked\ ([0-9a-f]{40})\ [a-z-]+:\ .+$ ]]; then kind=blocked; sha=${BASH_REMATCH[1]}
  else die "the first line is not a verdict ('Fix review: merge <40-hex>' or 'Fix review: blocked <40-hex> <class>: <why>'): '$first'"
  fi
  local want=""; [ "$kind" = merge ] && want=$sha
  check_pr "$repo" "$pr" "$want"

  if [ "$dry" = 1 ]; then
    printf 'app_comment: DRY-RUN: every refusal passed; would post the %s verdict for %s on #%s as %s; signed, minted and posted nothing\n' "$kind" "$sha" "$pr" "$APP_LOGIN"
    exit 0
  fi

  umask 077
  PRIV=$(mktemp -d "${TMPDIR:-/tmp}/app_comment.XXXXXX") || die "could not create a private directory"
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

  check_pr "$repo" "$pr" "$want"
  python3 -c 'import sys,json
json.dump({"body": open(sys.argv[1], encoding="utf-8").read()}, open(sys.argv[2], "w"))' "$body" "$PRIV/comment.json" \
    || die "could not write the comment payload"
  local resp cid
  resp=$(curl -fsS -X POST -H @"$PRIV/token.h" -H "$ACCEPT" "$API/repos/$repo/issues/$pr/comments" \
    --data-binary @"$PRIV/comment.json") || die "the comment POST was refused; nothing posted"
  cid=$(printf '%s' "$resp" | python3 -c 'import sys,json
d = json.load(sys.stdin); u = d.get("user") or {}
if u.get("login") != sys.argv[1] or u.get("type") != "Bot":
    sys.exit("app_comment: REFUSE: comment %s posted as %s (%s), not %s" % (d.get("id"), u.get("login"), u.get("type"), sys.argv[1]))
print(int(d["id"]))' "$APP_LOGIN") || exit 1
  printf 'app_comment: POSTED id=%s as %s on #%s\n' "$cid" "$APP_LOGIN" "$pr"
  python3 "$GH_COMMENT" verify --repo "$repo" --comment "$cid" --body-file "$body" \
    || die "comment $cid is on the record but did not read back byte-identical; it was not deleted"
}

if [ "${1:-}" != "--self-test" ]; then
  post "$@"
  exit $?
fi

# ---------------------------------------------------------------------------
# --self-test: `gh`, `curl` and `openssl` are stubs on PATH; no network, no key.
# `gh_comment.py` is the real one, so its refusals and its read-back run here.
SELF="$(cd "$(dirname -- "$0")" && pwd)/$(basename -- "$0")"
W=$(mktemp -d) || exit 2
trap 'rm -rf "$W"' EXIT
FAILS=0; N=0
st() { N=$((N + 1)); if [ "$1" = "$2" ]; then echo "ok   $3"; else echo "FAIL $3 (got '$1', want '$2')"; FAILS=$((FAILS + 1)); fi; }
SHA=1111111111111111111111111111111111111111
OTHER=2222222222222222222222222222222222222222
TOKEN=ghs_STUBTOKEN_must_never_print
JWTHEAD=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9
mkdir -p "$W/bin" "$W/id" "$W/authoronly"
printf '424242\n' > "$W/id/identity-approver.appid"
printf -- '-----BEGIN STUB KEY-----\nSTUBKEYMATERIAL\n-----END STUB KEY-----\n' > "$W/id/identity-approver.pem"
printf '424242\n' > "$W/authoronly/hpo-author.appid.txt"; cp "$W/id/identity-approver.pem" "$W/authoronly/hpo-author.pem"

cat > "$W/bin/gh" <<'STUB'
#!/bin/bash
printf 'gh %s\n' "$*" >> "$STUB/log"
case "$*" in
  "api repos/o/r/pulls/7")
    n=$(grep -c '^gh api repos/o/r/pulls/7$' "$STUB/log")
    if [ "$n" -gt 1 ] && [ -f "$STUB/pr2.json" ]; then cat "$STUB/pr2.json"; else cat "$STUB/pr.json"; fi ;;
  "api /repos/o/r/issues/comments/55")
    [ -f "$STUB/readback-off" ] && { python3 -c 'import sys,json; print(json.dumps({"id": 55, "body": open(sys.argv[1]).read() + "x"}))' "$STUB/posted.body"; exit 0; }
    python3 -c 'import sys,json; print(json.dumps({"id": 55, "body": open(sys.argv[1]).read()}))' "$STUB/posted.body" ;;
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
  */app/installations/99/access_tokens) printf '{"token": "ghs_STUBTOKEN_must_never_print"}' ;;
  */installation/token) grep -q 'ghs_STUBTOKEN' "$hdr" || exit 22 ;;
  */repos/o/r/issues/7/comments)
    ls -l "$hdr" | cut -c1-10 > "$STUB/tokenmode"; cp "$hdr" "$STUB/tokencopy"
    python3 -c 'import sys,json; open(sys.argv[2], "w").write(json.load(open(sys.argv[1]))["body"])' "$data" "$STUB/posted.body"
    if [ -f "$STUB/refuse-post" ]; then echo "curl: (22) The requested URL returned error: 403" >&2; exit 22; fi
    login='hpo-approver[bot]'; [ -f "$STUB/as-author" ] && login='hpo-author[bot]'
    printf '{"id": 55, "user": {"login": "%s", "type": "Bot"}}' "$login" ;;
  *) exit 9 ;;
esac
STUB
chmod +x "$W/bin/gh" "$W/bin/openssl" "$W/bin/curl"

MERGE="Fix review: merge $SHA"
BLOCKED="Fix review: blocked $SHA head-moved: measured $SHA, head is $OTHER"
mkcase() { # name head first-line
  local d="$W/$1"; mkdir -p "$d/tmp" "$d/seat"; : > "$d/log"
  printf '{"state": "open", "head": {"sha": "%s"}}' "$2" > "$d/pr.json"
  printf '%s\nevidence: /private/tmp/x/review-%s\nRESULT merge clean\n' "$3" "$1" > "$d/seat/verdict.md"
}
run() { # name args... ; the last arg defaults to the case's own verdict file
  local d="$W/$1"; shift
  ( export STUB="$d" PATH="$W/bin:$PATH" TMPDIR="$d/tmp" HPO_IDENTITY_DIR="${IDDIR:-$W/id}"
    if [ "${BASHX:-}" = 1 ]; then bash -x "$SELF" "$@"; else bash "$SELF" "$@"; fi > "$d/out" 2> "$d/err" )
}
calls() { grep -c "^$2" "$W/$1/log"; }
leftover() { find "$W/$1/tmp" -mindepth 1 | wc -l | tr -d ' '; }
leaks() { cat "$W/$1/out" "$W/$1/err" | grep -c -e "$TOKEN" -e STUBKEYMATERIAL -e STUBSIGNATURE -e "$JWTHEAD"; }

mkcase ok "$SHA" "$MERGE"
run ok o/r 7 "$W/ok/seat/verdict.md"; st $? 0 "a merge verdict at the live head of an open pull request is posted"
st "$(calls ok 'curl repos/o/r/issues/7/comments')" 1 "with exactly one comment POST"
st "$(cmp -s "$W/ok/posted.body" "$W/ok/seat/verdict.md" && echo same)" same "whose body is the file, byte for byte"
st "$(grep -c "Bearer $TOKEN" "$W/ok/tokencopy")" 1 "the POST carried the installation token, from a header file"
st "$(cat "$W/ok/tokenmode")" "-rw-------" "and that header file was mode 600 while it existed"
st "$(calls ok 'gh api repos/o/r/pulls/7$')" 2 "the head was read twice: before the mint and again before the POST"
st "$(calls ok 'gh api /repos/o/r/issues/comments/55')" 1 "the comment was read back off the API"
st "$(grep -c '^READBACK id=55 .* identical=True' "$W/ok/out")" 1 "and gh_comment.py printed an identical read-back"
st "$(grep -c '^app_comment: POSTED id=55 as hpo-approver\[bot\]' "$W/ok/out")" 1 "naming the App it posted as"
st "$(calls ok 'curl installation/token')" 1 "the installation token is revoked on exit"
st "$(leftover ok)" 0 "the private directory is gone after a success"
st "$(leaks ok)" 0 "no token, JWT, key or signature text in stdout or stderr"
st "$(grep -c "$TOKEN" "$W/ok/tokencopy")" 1 "(null control: the leak grep does find the token where it really is)"

mkcase xtrace "$SHA" "$MERGE"
BASHX=1 run xtrace o/r 7 "$W/xtrace/seat/verdict.md"; st $? 0 "under bash -x the post still runs"
st "$(leaks xtrace)" 0 "and no token, JWT, key or signature text reaches the trace"
st "$(grep -c "$JWTHEAD" "$W/xtrace/jwtcopy")" 1 "(null control: a JWT was signed on that run)"

mkcase blocked "$OTHER" "$BLOCKED"
run blocked o/r 7 "$W/blocked/seat/verdict.md"; st $? 0 "a blocked head-moved verdict posts although its SHA is not the live head"
mkcase moved "$OTHER" "$MERGE"
run moved o/r 7 "$W/moved/seat/verdict.md"; st $? 1 "REFUSE: a merge verdict for a head that is not the live one"
st "$(grep -c 'head moved' "$W/moved/err")" 1 "naming the moved head"
st "$(calls moved curl)" 0 "and nothing was minted or posted"
mkcase late "$SHA" "$MERGE"; printf '{"state": "open", "head": {"sha": "%s"}}' "$OTHER" > "$W/late/pr2.json"
run late o/r 7 "$W/late/seat/verdict.md"; st $? 1 "REFUSE: the head moved between the mint and the POST"
st "$(calls late 'curl repos/o/r/issues/7/comments')" 0 "and no comment was posted"
st "$(calls late 'curl installation/token')" 1 "the minted token is revoked after that refusal"
st "$(leftover late)" 0 "and the private directory is gone, token and all"
mkcase closed "$SHA" "$MERGE"; printf '{"state": "closed", "head": {"sha": "%s"}}' "$SHA" > "$W/closed/pr.json"
run closed o/r 7 "$W/closed/seat/verdict.md"; st $? 1 "REFUSE: a closed pull request"

for bad in "LGTM" "Fix review: merge ${SHA:0:7}" "Fix review: merge $SHA extra" "fix review: merge $SHA" \
           "Fix review: blocked $SHA" "Fix review: approve $SHA"; do
  mkcase notverdict "$SHA" "$bad"
  run notverdict o/r 7 "$W/notverdict/seat/verdict.md"; st $? 1 "REFUSE: a first line outside the verdict grammar: '$bad'"
  st "$(calls notverdict curl)" 0 "  and nothing was minted or posted"
done
mkcase shared "$SHA" "$MERGE"; mkdir -p "$W/shared/scratchpad"; cp "$W/shared/seat/verdict.md" "$W/shared/scratchpad/v.md"
run shared o/r 7 "$W/shared/scratchpad/v.md"; st $? 1 "REFUSE: a body file directly in a shared root (gh_comment.py's refusal)"
st "$(calls shared curl)" 0 "  refused before the mint: nothing minted or posted"
mkcase absent "$SHA" "$MERGE"
run absent o/r 7 "$W/absent/seat/none.md"; st $? 1 "REFUSE: an absent body file"
st "$(wc -l < "$W/absent/log" | tr -d ' ')" 0 "  before any gh, openssl or curl call"

mkcase asauthor "$SHA" "$MERGE"; : > "$W/asauthor/as-author"
run asauthor o/r 7 "$W/asauthor/seat/verdict.md"; st $? 1 "REFUSE: a post that reads back as the author App (#1233's defect)"
st "$(grep -c 'posted as hpo-author\[bot\]' "$W/asauthor/err")" 1 "naming the identity it landed as"
st "$(calls asauthor 'gh api /repos/o/r/issues/comments')" 0 "  and it is not reported as verified"
st "$(calls asauthor 'curl installation/token')" 1 "  and the token is still revoked"
mkcase authoronly "$SHA" "$MERGE"
IDDIR="$W/authoronly" run authoronly o/r 7 "$W/authoronly/seat/verdict.md"; st $? 1 "REFUSE: only the author App's key present; it is never used"
st "$(wc -l < "$W/authoronly/log" | tr -d ' ')" 0 "  before any gh, openssl or curl call"
mkcase readoff "$SHA" "$MERGE"; : > "$W/readoff/readback-off"
run readoff o/r 7 "$W/readoff/seat/verdict.md"; st $? 1 "REFUSE: a comment that does not read back byte-identical"
st "$(grep -c 'did not read back byte-identical' "$W/readoff/err")" 1 "naming the id it left on the record"
mkcase postfail "$SHA" "$MERGE"; : > "$W/postfail/refuse-post"
run postfail o/r 7 "$W/postfail/seat/verdict.md"; st $? 1 "a refused POST exits non-zero"
st "$(calls postfail 'curl installation/token')" 1 "the token is revoked after the failed POST"
st "$(leftover postfail)" 0 "the private directory is gone after the failed POST"
st "$(leaks postfail)" 0 "and no secret text reached stdout or stderr"

mkcase dry "$SHA" "$MERGE"
run dry --dry-run o/r 7 "$W/dry/seat/verdict.md"; st $? 0 "--dry-run passes every refusal"
st "$(calls dry curl)" 0 "and makes no curl call: nothing minted, nothing posted"
st "$(calls dry openssl)" 0 "and signs nothing"
mkcase drymoved "$OTHER" "$MERGE"
run drymoved --dry-run o/r 7 "$W/drymoved/seat/verdict.md"; st $? 1 "--dry-run still refuses what a real run would"

echo "app_comment self-test: $N checks, $FAILS failed"
[ "$FAILS" -eq 0 ]
