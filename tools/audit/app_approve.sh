#!/bin/bash
# Approve a pull request as the App `hpo-approver`, at one exact head SHA, and
# only on an adversarial `merge` verdict for that SHA.
#
#   tools/audit/app_approve.sh [--dry-run] <owner/repo> <pr> <40-hex head sha>
#   tools/audit/app_approve.sh --self-test
#
# WHY THIS EXISTS. Since decision 0009 step 6, `main-protect` merges nothing
# without one approving review, and GitHub never lets an author approve their
# own pull request. An ordinary pull request's review comes from the App after
# a `merge` verdict (`tools/audit/briefs/orchestrator.md` section 11); a policy
# pull request's comes from the owner, on GitHub, and this script is not that.
# The only copy of the token minting lived in a session scratchpad.
#
# IT REFUSES, AND POSTS NOTHING, UNLESS ALL OF THESE HOLD:
#   - the App id and private key files exist (fail closed, before any call);
#   - the pull request is open, and its live head is exactly <sha>;
#   - the NEWEST comment whose first line starts `Fix review:` is exactly
#     `Fix review: merge <sha>` -- the grammar `fix-review.md` sends reviewers
#     to and `.claude/workflows/web-fix-wave.js` parses. A newer `blocked`
#     verdict, or a `merge` for another head, refuses;
#   - the head is still <sha> when re-read after minting, just before the POST.
#
# THE SECRETS. The key files are `$HPO_IDENTITY_DIR/identity-approver.appid`
# and `identity-approver.pem` (default directory `~/.zcode`). The JWT and the
# installation token are written only as curl header files inside a private
# mode-700 directory, never onto a command line and never printed; an EXIT trap
# removes that directory on every path, the refusals and a failed POST
# included. Reads go through `gh` as whatever GH_TOKEN the seat set; only the
# review POST carries the App token.
#
# --dry-run runs every refusal and the mint, then stops before the POST.
set -uo pipefail

API=https://api.github.com
ACCEPT='Accept: application/vnd.github+json'
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
  local appid; appid=$(tr -dc '0-9' < "$appid_f")
  [ -n "$appid" ] || die "App id file holds no number: $appid_f"

  check_pr "$repo" "$pr" "$sha"
  local verdict vid vurl vline
  verdict=$(gh api --paginate "repos/$repo/issues/$pr/comments?per_page=100" | python3 -c "$PAGES_PY"'
vs = [c for c in out if (c.get("body") or "").split("\n", 1)[0].strip().lower().startswith("fix review:")]
vs.sort(key=lambda c: (c["created_at"], c["id"]))
if not vs: print("NONE")
else:
    c = vs[-1]; print(c["id"], c["html_url"], c["body"].split("\n", 1)[0].strip())') \
    || die "could not read the comments on #$pr"
  [ "$verdict" != "NONE" ] || die "no 'Fix review:' verdict on #$pr; an approval needs 'Fix review: merge $sha'"
  read -r vid vurl vline <<<"$verdict"
  [ "$vline" = "Fix review: merge $sha" ] \
    || die "the newest verdict on #$pr ($vurl) is '$vline', not 'Fix review: merge $sha'"

  umask 077
  PRIV=$(mktemp -d "${TMPDIR:-/tmp}/app_approve.XXXXXX") || die "could not create a private directory"
  trap 'rm -rf "$PRIV"' EXIT
  trap 'exit 130' INT TERM
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

  if [ "$dry" = 1 ]; then
    printf 'app_approve: DRY-RUN: would APPROVE #%s at %s on %s; posted nothing\n' "$pr" "$sha" "$vurl"
    exit 0
  fi
  check_pr "$repo" "$pr" "$sha"
  python3 -c 'import sys,json
sha, url, f = sys.argv[1:4]
json.dump({"commit_id": sha, "event": "APPROVE",
  "body": "Approved by `hpo-approver` at `%s` on the adversarial verdict %s (`Fix review: merge %s`), via `tools/audit/app_approve.sh`." % (sha, url, sha)},
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
mkdir -p "$W/bin" "$W/id" "$W/nokey"
printf '424242\n' > "$W/id/identity-approver.appid"; cp "$W/id/identity-approver.appid" "$W/nokey/"
printf -- '-----BEGIN STUB KEY-----\nSTUBKEYMATERIAL\n-----END STUB KEY-----\n' > "$W/id/identity-approver.pem"

cat > "$W/bin/gh" <<'STUB'
#!/bin/bash
printf 'gh %s\n' "$*" >> "$STUB/log"
case "$*" in
  "api repos/o/r/pulls/7")
    n=$(grep -c '^gh api repos/o/r/pulls/7$' "$STUB/log")
    if [ "$n" -gt 1 ] && [ -f "$STUB/pr2.json" ]; then cat "$STUB/pr2.json"; else cat "$STUB/pr.json"; fi ;;
  "api --paginate repos/o/r/issues/7/comments?per_page=100")
    cat "$STUB/c1.json"; [ -f "$STUB/c2.json" ] && cat "$STUB/c2.json"; true ;;
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
printf '%s\n' "$hdr" >> "$STUB/hdrfiles"
case "$url" in
  */repos/o/r/installation) printf '{"id": 99}' ;;
  */app/installations/99/access_tokens)
    printf '{"token": "ghs_STUBTOKEN_must_never_print", "permissions": {"pull_requests": "write"}}' ;;
  */repos/o/r/pulls/7/reviews)
    ls -l "$hdr" | cut -c1-10 > "$STUB/tokenmode"; cp "$hdr" "$STUB/tokencopy"; cp "$data" "$STUB/posted.json"
    if [ -f "$STUB/refuse-post" ]; then echo "curl: (22) The requested URL returned error: 422" >&2; exit 22; fi
    python3 -c 'import sys,json; d=json.load(open(sys.argv[1])); print(json.dumps({"id": 5, "state": "APPROVED", "commit_id": d["commit_id"], "user": {"login": "hpo-approver[bot]"}}))' "$data" ;;
  *) exit 9 ;;
esac
STUB
chmod +x "$W/bin/gh" "$W/bin/openssl" "$W/bin/curl"

pr_json() { printf '{"state": "%s", "merged": %s, "head": {"sha": "%s"}}' "$1" "$2" "$3"; }
comment() { # id first-line
  printf '{"id": %s, "created_at": "2026-09-17T0%s:00:00Z", "html_url": "https://example.test/c%s", "body": "%s\\nRESULT x"}' "$1" "$1" "$1" "$2"
}
mkcase() { # name state merged head comments-json
  local d="$W/$1"; mkdir -p "$d/tmp"; : > "$d/log"; : > "$d/hdrfiles"
  pr_json "$2" "$3" "$4" > "$d/pr.json"; printf '%s' "$5" > "$d/c1.json"
}
run() { # name args... -> rc; out/err captured
  local d="$W/$1"; shift
  ( export STUB="$d" PATH="$W/bin:$PATH" TMPDIR="$d/tmp" HPO_IDENTITY_DIR="${IDDIR:-$W/id}"
    bash "$SELF" "$@" > "$d/out" 2> "$d/err" )
}
calls() { grep -c "^$2" "$W/$1/log"; }
leftover() { find "$W/$1/tmp" -mindepth 1 | wc -l | tr -d ' '; }
leaks() { cat "$W/$1/out" "$W/$1/err" | grep -c -e "$TOKEN" -e STUBKEYMATERIAL -e STUBSIGNATURE; }
GOOD="[$(comment 1 'An ordinary comment'),$(comment 2 "Fix review: merge $SHA")]"

mkcase ok open false "$SHA" "$GOOD"
run ok o/r 7 "$SHA"; st $? 0 "a merge verdict at the live head of an open pull request is approved"
st "$(calls ok 'curl repos/o/r/pulls/7/reviews')" 1 "with exactly one review POST"
st "$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d["event"], d["commit_id"])' "$W/ok/posted.json")" \
   "APPROVE $SHA" "whose event is APPROVE and whose commit_id is the asked-for SHA"
st "$(grep -c 'https://example.test/c2' "$W/ok/posted.json")" 1 "and whose body cites the verdict comment"
st "$(grep -c "Bearer $TOKEN" "$W/ok/tokencopy")" 1 "the POST carried the installation token, from a header file"
st "$(cat "$W/ok/tokenmode")" "-rw-------" "and that header file was mode 600 while it existed"
st "$(calls ok 'gh api repos/o/r/pulls/7$')" 2 "the head was read twice: before the mint and again before the POST"
st "$(leftover ok)" 0 "the private directory is gone after a success"
st "$(leaks ok)" 0 "no token, key or signature text in stdout or stderr after a success"
st "$(grep -c "$TOKEN" "$W/ok/tokencopy")" 1 "(null control: the leak grep does find the token where it really is)"
st "$(grep -c '^app_approve: APPROVED review id=5 state=APPROVED' "$W/ok/out")" 1 "and the read-back line is printed"

mkcase moved open false "$OTHER" "$GOOD"
run moved o/r 7 "$SHA"; st $? 1 "REFUSE: the live head moved off the asked-for SHA"
st "$(grep -c 'head moved' "$W/moved/err")" 1 "naming the moved head"
st "$(calls moved curl)" 0 "and nothing was minted or posted"

mkcase late open false "$SHA" "$GOOD"; pr_json open false "$OTHER" > "$W/late/pr2.json"
run late o/r 7 "$SHA"; st $? 1 "REFUSE: the head moved between the mint and the POST"
st "$(calls late 'curl repos/o/r/pulls/7/reviews')" 0 "and no review was posted"
st "$(leftover late)" 0 "the private directory is gone after that refusal, token and all"

mkcase merged closed true "$SHA" "$GOOD"
run merged o/r 7 "$SHA"; st $? 1 "REFUSE: a merged pull request, even at its own head with a merge verdict"
st "$(calls merged curl)" 0 "and nothing was minted or posted"

mkcase none open false "$SHA" "[$(comment 1 'An ordinary comment')]"
run none o/r 7 "$SHA"; st $? 1 "REFUSE: no Fix review verdict at all"
st "$(grep -c "no 'Fix review:' verdict" "$W/none/err")" 1 "saying so"
st "$(calls none curl)" 0 "and nothing was minted or posted"

mkcase stale open false "$SHA" "[$(comment 1 "Fix review: merge $OTHER")]"
run stale o/r 7 "$SHA"; st $? 1 "REFUSE: the merge verdict is for another SHA"
st "$(grep -c "is 'Fix review: merge $OTHER'" "$W/stale/err")" 1 "naming the SHA the verdict is for"

mkcase blocked open false "$SHA" "$GOOD"
printf '[%s]' "$(comment 3 "Fix review: blocked $SHA claims: moved")" > "$W/blocked/c2.json"
run blocked o/r 7 "$SHA"; st $? 1 "REFUSE: a newer blocked verdict, on a later page, overrides an older merge"

mkcase nokey open false "$SHA" "$GOOD"
IDDIR="$W/nokey" run nokey o/r 7 "$SHA"; st $? 1 "REFUSE: the App private key is missing"
st "$(grep -c 'private key missing' "$W/nokey/err")" 1 "failing closed with a clear message"
st "$(wc -l < "$W/nokey/log" | tr -d ' ')" 0 "before any gh, openssl or curl call"

mkcase shortsha open false "$SHA" "$GOOD"
run shortsha o/r 7 "${SHA:0:7}"; st $? 1 "REFUSE: an abbreviated SHA is not an exact head"

mkcase postfail open false "$SHA" "$GOOD"; : > "$W/postfail/refuse-post"
run postfail o/r 7 "$SHA"; st $? 1 "a refused POST exits non-zero"
st "$(leftover postfail)" 0 "the private directory is gone after the failed POST"
st "$(grep -c "$TOKEN" "$W/postfail/tokencopy")" 1 "(the token header file did exist during that POST)"
st "$(leaks postfail)" 0 "and no token, key or signature text reached stdout or stderr"

mkcase dry open false "$SHA" "$GOOD"
run dry --dry-run o/r 7 "$SHA"; st $? 0 "--dry-run passes every refusal and the mint"
st "$(calls dry 'curl repos/o/r/pulls/7/reviews')" 0 "and posts nothing"
st "$(calls dry 'curl app/installations/99/access_tokens')" 1 "(it did mint)"
st "$(leftover dry)" 0 "and its private directory is gone"
st "$(leaks dry)" 0 "with no secret text in its output"

echo "app_approve self-test: $N checks, $FAILS failed"
[ "$FAILS" -eq 0 ]
