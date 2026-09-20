#!/bin/bash
{ set +x; } 2>/dev/null # before anything: a caller's `bash -x` would trace the token
# Push one branch and open or re-body its pull request as the App `hpo-author`
# -- the author identity decision 0011 built this tool for, with the body's
# contract check FIRST so nothing reaches the remote until the body passes.
#
#   tools/audit/app_push.sh [--dry-run] <owner/repo> <worktree> <branch> <body.md> [issue-numbers...]
#   tools/audit/app_push.sh --self-test
#
# WHY THIS EXISTS. The seat account that authored pull requests is spam-flagged:
# its #1256 returned 201 then 404 within about a minute and left branch
# `fix/d11-gov` wedged, and about eleven of its merged pull requests now 404
# retroactively (docs/decisions/0011). Authorship moves to the `hpo-author`
# App and MINTING IS ORCHESTRATOR-CENTRAL: seats never hold the App's key,
# hand their branch off locally, and the orchestrator runs this script. The
# trailing issue numbers are the ones the body INTENDS to close; they go to
# `prepr.sh`, which hands them to `preflight.sh`.
#
# IT REFUSES, AND TOUCHES NOTHING REMOTE, UNLESS ALL OF THESE HOLD:
#   - the App id file holds digits only and the private key file exists
#     (fail closed, before any call);
#   - `tools/audit/prepr.sh <body.md> <issues...>` passes, run from the
#     worktree, BEFORE anything is minted (#678's ordering: nothing reaches
#     the remote until the body passes);
#   - the worktree's HEAD is exactly the branch's committed tip and the
#     worktree is clean -- only a committed tip is pushed;
#   - the open-pull-request query over the branch answers: `none` or a
#     number. Anything else -- no `gh`, a failed call, an unparseable
#     listing -- refuses before minting (push.sh's "no answer, no push").
#
# WHAT IT DOES AFTER THOSE PASS: mints a JWT and an installation token into
# mode-600 header files inside a mode-700 mktemp directory; pushes the branch
# over https as the App; POSTs /pulls as the App when no pull request is open
# for the branch (title = the tip commit's subject, base = main), else PATCHes
# the body of the open one; then reads the pull request back and REFUSES
# unless it is open, its head sha is the pushed sha, and its body is
# byte-identical to <body.md> modulo one trailing newline (GitHub appends
# one; measured 2026-09-18). Not atomic against GitHub: a push whose POST
# then fails leaves the branch pushed, and the refusal message says so.
#
# THE SECRETS. The key files are `$HPO_IDENTITY_DIR/hpo-author.appid.txt` and
# `hpo-author.pem` (default directory `~/.zcode`). The JWT and the
# installation token are written only as curl header files inside the private
# mode-700 directory, never onto a command line and never printed. An EXIT
# trap revokes the installation token (DELETE /installation/token) and removes
# that directory on every path, the refusals and a failed POST included. The
# one read that is not an App call -- the open-pull-request query -- goes
# through `gh` as whatever GH_TOKEN the caller set, exactly as `app_approve.sh`
# reads; only the App calls carry the JWT or the token.
#
# HOW THE APP AUTHENTICATES THE PUSH, and why a credential helper. An
# installation token can ride a push three ways and two of them leak it:
#   * `git -c http.<url>.extraheader="Authorization: Bearer <token>"` puts
#     the token on git's command line, readable from any process listing;
#   * the same key through GIT_CONFIG_KEY_n/VALUE_n keeps it off argv but
#     plants it in git's environment, which every child of the push
#     inherits;
#   * a credential helper is executed by git with the fixed argv `get` (plus
#     `store`/`erase`, ignored here) and answers over its stdout pipe, so the
#     token travels file -> pipe -> git and never sits on any command line.
#     Measured with GIT_TRACE=1 and `git credential fill` on this host's git:
#     the helper answered and the only run_command line was `<helper> get`.
# `credential.helper=` (the empty reset) clears the host's own helpers first
# -- osxkeychain answered before the App's helper without it, from the
# keychain, in the same measurement -- so the App's token is the only
# credential this push can use, and no other credential leaks into it. An
# askpass would also keep the token off argv, but git consults credential
# helpers BEFORE askpass, so any configured helper shadows one; the reset
# plus exactly one helper is the deterministic form. The helper is generated
# inside the private directory, reads only the token header file, and ignores
# `store`/`erase`, so the token is persisted nowhere.
#
# --dry-run runs every refusal above, then stops before signing anything.
set -uo pipefail

API=https://api.github.com
ACCEPT='Accept: application/vnd.github+json'
die() { printf 'app_push: REFUSE: %s\n' "$*" >&2; exit 1; }

cleanup() {
  if [ -s "$PRIV/token.h" ]; then
    curl -fsS -X DELETE -H @"$PRIV/token.h" -H "$ACCEPT" "$API/installation/token" >/dev/null 2>&1 \
      || printf 'app_push: warning: revoking the installation token failed; it expires within the hour\n' >&2
  fi
  rm -rf "$PRIV"
}

# push.sh's classification, over a JSON listing: `[]` POSITIVELY means no
# pull request is open, an array naming a number names one, and anything
# else -- prose, an empty string, a broken filter -- is `unknown`, which
# refuses. Reading "nothing" out of an unasked question is the defect the
# three-outcome shape exists to prevent.
pr_from_listing() { # listing text -> number, 'none' or 'unknown'
  printf '%s' "${1:-}" | python3 -c '
import sys, json
try:
    d = json.loads(sys.stdin.read() or "null")
except ValueError:
    d = None
if isinstance(d, list) and not d:
    print("none")
elif isinstance(d, list) and d and isinstance(d[0], dict) and isinstance(d[0].get("number"), int):
    print(d[0]["number"])
else:
    print("unknown")'
}

push_and_open() {
  local dry=0
  [ "${1:-}" = "--dry-run" ] && { dry=1; shift; }
  [ $# -ge 4 ] || die "usage: app_push.sh [--dry-run] <owner/repo> <worktree> <branch> <body.md> [issue-numbers...]"
  local repo=$1 wt=$2 br=$3 body=$4
  shift 4
  [[ $repo =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || die "repo '$repo' is not owner/repo"
  [[ $br =~ ^[A-Za-z0-9._][A-Za-z0-9._/-]*$ ]] || die "branch name '$br' is not a plain ref name"
  [ "$br" != "main" ] || die "refusing to push main: a push to main forces the full gate (CLAUDE.md rule 1); a pull request is not opened on it either"
  local issue
  for issue in "$@"; do
    [[ $issue =~ ^[0-9]+$ ]] || die "issue number '$issue' is not a number"
  done
  # The body is a path the caller typed; resolve it before any cd changes
  # what it means (push.sh's #622 rule: one expansion, no re-quoting). The
  # refusal names $body -- after `shift 4` the positional $4 is an issue
  # number or unset, and `set -u` trips on the unset one before die prints.
  local body_abs
  body_abs=$(cd "$(dirname -- "$body")" 2>/dev/null && printf '%s/%s\n' "$(pwd)" "$(basename -- "$body")") \
    || die "no body at $body"
  body=$body_abs
  [ -f "$body" ] || die "no body file at $body"
  wt=$(cd "$wt" 2>/dev/null && pwd) || die "cannot enter worktree '$wt'"

  local idir="${HPO_IDENTITY_DIR:-$HOME/.zcode}"
  local appid_f="$idir/hpo-author.appid.txt" key="$idir/hpo-author.pem"
  [ -s "$appid_f" ] || die "App id file missing or empty: $appid_f (fail closed)"
  [ -s "$key" ] || die "App private key missing or empty: $key (fail closed)"
  local appid; appid=$(cat "$appid_f")
  [[ $appid =~ ^[0-9]+$ ]] || die "App id file must hold digits only: $appid_f (fail closed)"

  # THE #678 ORDERING: the body passes BEFORE anything is minted. prepr.sh
  # derives its diff from the worktree it runs in, so it runs with the
  # worktree as cwd; a refusal here leaves nothing minted, pushed or posted.
  local prepr; prepr="$(cd "$(dirname -- "$0")" && pwd)/prepr.sh"
  [ -f "$prepr" ] || die "no prepr.sh beside this script at $prepr"
  ( cd "$wt" && bash "$prepr" "$body" "$@" ) \
    || die "the body did not pass tools/audit/prepr.sh, so NOTHING was minted, pushed or posted; repair it and run this again"

  # Only a committed tip is pushed: HEAD is the branch's tip, and the tree is
  # clean. A dirty worktree would push a sha whose tree the body never
  # measured, and a HEAD elsewhere would push a branch the seat is not on.
  local head tip
  head=$(git -C "$wt" rev-parse HEAD 2>/dev/null) || die "'$wt' is not a git worktree"
  tip=$(git -C "$wt" rev-parse --verify "refs/heads/$br" 2>/dev/null) \
    || die "no local branch '$br' in $wt"
  [ "$head" = "$tip" ] || die "worktree HEAD ($head) is not the committed tip of '$br' ($tip); commit or check out first"
  [ -z "$(git -C "$wt" status --porcelain 2>/dev/null)" ] \
    || die "worktree $wt is dirty; only a committed tip is pushed -- commit or clean it first"
  local subject; subject=$(git -C "$wt" log -1 --format=%s) || die "could not read the tip commit's subject"

  # Is a pull request open on this branch? Read through `gh` before minting,
  # so a query that cannot answer refuses while nothing is minted. The head
  # filter is percent-encoded: a slash in a branch name is legal in a query
  # string but `gh api` passes the path through unexamined, and asking for
  # `head=o:fix/x` and being handed GitHub's reading of `o:fix` is a silence,
  # not an answer.
  command -v gh >/dev/null 2>&1 || die "no gh on PATH, so the open-pull-request query cannot be asked and NOTHING was pushed (push.sh's no-answer rule)"
  local owner=${repo%/*} listing prnum
  local headq; headq=$(printf '%s:%s' "$owner" "$br" | sed 's|:|%3A|g; s|/|%2F|g')
  listing=$(gh api "repos/$repo/pulls?head=$headq&state=open" 2>/dev/null) \
    || die "could not ask whether a pull request is open on $br (gh exited $?), so NOTHING was minted or pushed"
  prnum=$(pr_from_listing "$listing")
  [ "$prnum" != "unknown" ] \
    || die "the open-pull-request query on $br answered <<$listing>>, which names no pull request and states none is open; NOTHING was minted or pushed"

  if [ "$dry" = 1 ]; then
    if [ "$prnum" = "none" ]; then
      printf 'app_push: DRY-RUN: every refusal passed; would mint a token, push %s to %s, and CREATE a pull request from %s with %s; signed, minted, pushed and posted nothing\n' "$br" "$repo" "$br" "$body"
    else
      printf 'app_push: DRY-RUN: every refusal passed; would mint a token, push %s to %s, and PATCH #%s'"'"'s body from %s; signed, minted, pushed and posted nothing\n' "$br" "$repo" "$prnum" "$body"
    fi
    exit 0
  fi

  umask 077
  PRIV=$(mktemp -d "${TMPDIR:-/tmp}/app_push.XXXXXX") || die "could not create a private directory"
  trap cleanup EXIT
  trap 'exit 130' INT TERM HUP
  # SIGKILL is the one signal no trap catches: a kill -9 mid-push can leave the token file in $PRIV, and the backstop is the one already documented -- the token expires within the hour.
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
  chmod 600 "$PRIV/token.h" "$PRIV/jwt.h"

  # The App's push credential: generated, file-fed, and the only helper. See
  # the header for why a helper rather than extraheader or askpass. `get` is
  # the argv git actually passes (measured); `store`/`erase` are no-ops.
  cat > "$PRIV/credhelper.sh" <<HELPER
#!/bin/sh
case "\$1" in
  get) printf 'username=x-access-token\npassword=%s\n' "\$(sed 's/^Authorization: Bearer //' '$PRIV/token.h')" ;;
esac
HELPER
  chmod 700 "$PRIV/credhelper.sh"

  # The URL carries no credential; the token rides the helper's stdout pipe.
  # http.postBuffer=64m (bounded): git's 1 MiB default sends a larger push
  # chunked, and the remote hung up on every screenshot branch that hit it
  # (#1267) -- 64 MiB keeps such a push in one Content-Length request.
  GIT_TERMINAL_PROMPT=0 git -C "$wt" -c credential.helper= -c "credential.helper=$PRIV/credhelper.sh" \
    -c http.postBuffer=64m push "https://github.com/$repo.git" "$br" \
    || die "the App's push of $br to $repo was refused; no pull request was opened or re-bodied"

  local num url
  if [ "$prnum" = "none" ]; then
    python3 -c 'import sys, json
d = {"title": sys.argv[1], "head": sys.argv[2], "base": "main", "body": open(sys.argv[3]).read()}
json.dump(d, open(sys.argv[4], "w"))' "$subject" "$br" "$body" "$PRIV/pr.json" || die "could not write the pull-request payload"
    num=$(curl -fsS -X POST -H @"$PRIV/token.h" -H "$ACCEPT" "$API/repos/$repo/pulls" \
      --data-binary @"$PRIV/pr.json" \
      | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["number"], d["html_url"])') \
      || die "the pull-request POST was refused; the branch IS pushed as the App -- open or re-body the pull request by hand from $body"
  else
    num=$prnum
    python3 -c 'import sys, json
json.dump({"body": open(sys.argv[1]).read()}, open(sys.argv[2], "w"))' "$body" "$PRIV/pr.json" || die "could not write the body payload"
    curl -fsS -X PATCH -H @"$PRIV/token.h" -H "$ACCEPT" "$API/repos/$repo/pulls/$num" \
      --data-binary @"$PRIV/pr.json" >/dev/null \
      || die "the body PATCH on #$num was refused; the branch IS pushed as the App -- set the body by hand from $body"
  fi
  read -r num url <<<"$num"

  # Read the pull request back: open, at the pushed sha, body byte-identical
  # modulo ONE trailing newline (GitHub appends one; measured 2026-09-18).
  curl -fsS -H @"$PRIV/token.h" -H "$ACCEPT" "$API/repos/$repo/pulls/$num" \
    | python3 -c 'import sys, json
sha, f = sys.argv[1:3]
d = json.load(sys.stdin)
want = open(f).read(); live = d.get("body") or ""
# equal, or differing by EXACTLY ONE trailing newline on either side -- the
# both-sides-strip form would refuse the measured shape (live == want + "\n")
# because stripping want too hides the difference it exists to allow.
def eq1(a, b):
    return a == b or (a.endswith("\n") and a[:-1] == b) or (b.endswith("\n") and b[:-1] == a)
line = "state=%s head=%s" % (d.get("state"), (d.get("head") or {}).get("sha"))
if d.get("state") != "open" or (d.get("head") or {}).get("sha") != sha:
    sys.exit("pull request #%s does not read back as open at %s: %s" % (d.get("number"), sha, line))
if not eq1(live, want):
    sys.exit("pull request #%s'"'"'s body is not byte-identical to %s modulo one trailing newline" % (d.get("number"), f))
print("read back: open at %s, body identical modulo one trailing newline" % sha)' "$head" "$body" \
    || die "the pull request did not read back; its state is above -- re-read it by hand before touching anything"

  printf 'app_push: PUSHED %s to %s:%s as the App; pull request #%s is open at %s with the body read back: %s\n' \
    "$head" "$repo" "$br" "$num" "$head" "$url"
}

if [ "${1:-}" != "--self-test" ]; then
  push_and_open "$@"
  exit $?
fi

# ---------------------------------------------------------------------------
# --self-test: `gh`, `git`, `curl` and `openssl` are stubs on PATH; no network,
# no key, no real git. The script under test is a byte-identical COPY in a
# scratch directory beside a stub prepr.sh -- $0 resolves prepr.sh next to
# itself, so the copy drives the real ordering with a stub rather than a seam
# in the production code. Every refusal is paired with the healthy run it must
# NOT refuse, and every run gets its own TMPDIR, so "the private directory is
# gone" is read off the tree.
SELF="$(cd "$(dirname -- "$0")" && pwd)/$(basename -- "$0")"
W=$(mktemp -d) || exit 2
trap 'rm -rf "$W"' EXIT
mkdir -p "$W/bin" "$W/id" "$W/nokey" "$W/badid" "$W/tool" "$W/tool-wt"
cp "$SELF" "$W/tool/app_push.sh"
FAILS=0; N=0
st() { N=$((N + 1)); if [ "$1" = "$2" ]; then echo "ok   $3"; else echo "FAIL $3 (got '$1', want '$2')"; FAILS=$((FAILS + 1)); fi; }
SHA=1111111111111111111111111111111111111111
OTHER=2222222222222222222222222222222222222222
TOKEN=ghs_STUBTOKEN_must_never_print
JWTHEAD=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9   # base64url of the JWT header
SIGB64=U1RVQlNJR05BVFVSRQ                      # base64url of STUBSIGNATURE
BR=fix/stub-x                                  # a slash: the head filter is encoded
printf '%s\n' "$SHA" > "$W/head.sha"
printf '424242\n' > "$W/id/hpo-author.appid.txt"; cp "$W/id/hpo-author.appid.txt" "$W/nokey/"
printf -- '-----BEGIN STUB KEY-----\nSTUBKEYMATERIAL\n-----END STUB KEY-----\n' > "$W/id/hpo-author.pem"
cp "$W/id/hpo-author.pem" "$W/badid/"; printf '4242a\n' > "$W/badid/hpo-author.appid.txt"
printf '## Head\n\n`%s`\n\n## Mutation proof\n\nm\n\n## Null control\n\nn\n\n## Figures\n\nnone\n\n## Red checks\n\nnone\n\n## Forward-carry\n\nnone\n\n## Friction\n\nnone\n' "$SHA" > "$W/body.md"

# The stub prepr.sh: logs its arguments, passes, or refuses on a marker file.
cat > "$W/tool/prepr.sh" <<'STUB'
#!/bin/bash
printf 'prepr %s\n' "$*" >> "$STUB/log"
[ -f "$STUB/prepr-fails" ] && { echo "prepr: REFUSE" >&2; exit 1; }
echo "PRE-PR: stub ok"
STUB
# The stub gh: only the open-pull-request query, answered from a fixture.
cat > "$W/bin/gh" <<'STUB'
#!/bin/bash
printf 'gh %s\n' "$*" >> "$STUB/log"
case "$*" in
  "api repos/o/r/pulls?head=o%3Afix%2Fstub-x&state=open")
    [ -f "$STUB/gh-fails" ] && exit 1
    if [ -f "$STUB/listing.json" ]; then cat "$STUB/listing.json"; else printf '[]'; fi ;;
  *) exit 9 ;;
esac
STUB
# The stub git: worktree state from markers; the push logs its argv, runs the
# real generated helper once with `get` (the argv git passes), and can fail.
cat > "$W/bin/git" <<'STUB'
#!/bin/bash
printf 'git %s\n' "$*" >> "$STUB/log"
case "$*" in
  *"rev-parse HEAD")    cat "$STUB/../head.sha" ;;
  *"rev-parse --verify"*)
    if [ -f "$STUB/tip-moved" ]; then printf '%s\n' "$OTHER_SHA_STUB"; else cat "$STUB/../head.sha"; fi ;;
  *"status --porcelain") [ -f "$STUB/dirty" ] && printf ' M tools/audit/x.sh'; true ;;
  *"log -1 --format=%s") printf 'fix: the stub subject' ;;
  *"push https://github.com/"*)
    if [ -f "$STUB/push-fails" ]; then echo "error: stub push refused" >&2; exit 1; fi
    for a in "$@"; do
      case "$a" in credential.helper=*)
        sh "${a#credential.helper=}" get > "$STUB/credout" 2>&1 ;; esac
    done ;;
  *) exit 9 ;;
esac
STUB
OTHER_SHA_STUB=$OTHER export OTHER_SHA_STUB
# The stub curl: answers the App's calls; logs METHOD and path for the pulls
# endpoints so create/patch/read-back are distinguishable in the log.
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
  */repos/o/r/installation) cp "$hdr" "$STUB/jwtcopy"; printf '{"id": 99}' ;;
  */app/installations/99/access_tokens)
    printf '{"token": "ghs_STUBTOKEN_must_never_print", "permissions": {"contents": "write", "pull_requests": "write"}}' ;;
  */installation/token) grep -q 'ghs_STUBTOKEN' "$hdr" || exit 22; : ;;
  *"repos/o/r/pulls?head="*) exit 9 ;;  # the listing query goes through gh, never curl
  */repos/o/r/pulls)
    [ -n "$data" ] || exit 9            # a bare GET here is not a call this script makes
    cp "$hdr" "$STUB/tokencopy"; ls -l "$hdr" | cut -c1-10 > "$STUB/tokenmode"
    python3 "$STUB/../prjson.py" store "$data" "$STUB/live-body" "$STUB/../head.sha" ;;
  */repos/o/r/pulls/[0-9]*)
    cp "$hdr" "$STUB/tokencopy"; ls -l "$hdr" | cut -c1-10 > "$STUB/tokenmode"
    if [ -n "$data" ]; then              # PATCH
      [ -f "$STUB/refuse-patch" ] && { echo "curl: (22) error: 422" >&2; exit 22; }
      python3 "$STUB/../prjson.py" store "$data" "$STUB/live-body" "$STUB/../head.sha"
    else                                 # GET read-back
      [ -f "$STUB/refuse-get" ] && exit 22
      [ -f "$STUB/mangle-body" ] && printf '{"number": 7, "state": "open", "head": {"sha": "%s"}, "html_url": "https://example.test/pr7", "body": "edited by someone else\\n"}' "$(cat "$STUB/../head.sha")" \
        || python3 "$STUB/../prjson.py" get "$STUB/live-body" "$STUB/../head.sha"
    fi ;;
  *) exit 9 ;;
esac
STUB
# prjson.py: `store <json> <live> <sha>` records a posted payload's body and
# echoes a pull-request json; `get <live> <sha>` echoes one whose body is the
# stored body plus ONE trailing newline -- the form GitHub was measured to
# return.
cat > "$W/prjson.py" <<'PY'
import json, sys
v = sys.argv[1:]
if v[0] == "store":
    body = json.load(open(v[1])).get("body", "")
    open(v[2], "w").write(body)
    sha = open(v[3]).read().strip()
else:
    body = open(v[1]).read() + "\n"
    sha = open(v[2]).read().strip()
print(json.dumps({"number": 7, "state": "open", "head": {"sha": sha},
                  "html_url": "https://example.test/pr7", "body": body}))
PY
cat > "$W/bin/openssl" <<'STUB'
#!/bin/bash
printf 'openssl %s\n' "$*" >> "$STUB/log"
case "$1" in
  base64) base64 | tr -d '\n' ;;
  dgst) [ -s "$4" ] || exit 1; cat >/dev/null; printf 'STUBSIGNATURE' ;;
  *) exit 9 ;;
esac
STUB
chmod +x "$W/tool/prepr.sh" "$W/bin/gh" "$W/bin/git" "$W/bin/curl" "$W/bin/openssl"

mkcase() { # name -> a stub dir with its own log and TMPDIR
  local d="$W/$1"; mkdir -p "$d/tmp"; : > "$d/log"
}
run() { # name args... -> rc; out/err captured in the case dir
  local d="$W/$1"; shift
  ( export STUB="$d" PATH="$W/bin:$PATH" TMPDIR="$d/tmp" HPO_IDENTITY_DIR="${IDDIR:-$W/id}"
    bash "$W/tool/app_push.sh" "$@" > "$d/out" 2> "$d/err" )
}
calls() { grep -c "^$2" "$W/$1/log"; }
leftover() { find "$W/$1/tmp" -mindepth 1 | wc -l | tr -d ' '; }
leaks() { cat "$W/$1/out" "$W/$1/err" | grep -c -e "$TOKEN" -e STUBKEYMATERIAL -e STUBSIGNATURE -e "$JWTHEAD" -e "$SIGB64"; }
firstline() { grep -n "$2" "$W/$1/log" | head -1 | cut -d: -f1; }

# The happy path: no pull request open, so push, then create, then read back.
mkcase ok
run ok o/r "$W/tool-wt" "$BR" "$W/body.md" 1234; st $? 0 "a passing body, a clean tip and no open pull request: pushed and created"
lp=$(firstline ok '^prepr ');      lm=$(firstline ok '^curl GET repos/o/r/installation$')
lu=$(firstline ok '^git -C .* -c credential.helper= .*push '); lpr=$(firstline ok '^curl POST repos/o/r/pulls$')
if [ -n "$lp" ] && [ -n "$lm" ] && [ -n "$lu" ] && [ -n "$lpr" ] \
   && [ "$lp" -lt "$lm" ] && [ "$lm" -lt "$lu" ] && [ "$lu" -lt "$lpr" ]; then ORD=ordered; else ORD="prepr=$lp mint=$lm push=$lu pr=$lpr"; fi
st "$ORD" ordered "prepr ran before the mint, the mint before the push, the push before the pull request (#678's ordering)"
st "$(grep -c 'credential.helper= -c credential.helper=' "$W/ok/log")" 1 "the push resets the host's credential helpers before adding the App's"
st "$(grep -c -- '-c http.postBuffer=64m push ' "$W/ok/log")" 1 "the push argv carries -c http.postBuffer=64m, so an over-1-MiB branch does not go chunked (#1267)"
st "$(grep -c " push https://github.com/o/r.git $BR" "$W/ok/log")" 1 "and pushes over a token-free https URL to the branch"
st "$(grep -c "$TOKEN\|Authorization:" "$W/ok/log")" 0 "the token and header text appear on NO stubbed command line, push included"
st "$(python3 -c 'import sys; sys.stdout.write(open(sys.argv[1]).read())' "$W/ok/live-body")" "$(cat "$W/body.md")" "the created pull request carries the body file's exact bytes"
st "$(grep -c '^curl GET repos/o/r/pulls/7$' "$W/ok/log")" 1 "the pull request is read back once, through the App token"
st "$(grep -c "Bearer $TOKEN" "$W/ok/tokencopy")" 1 "(null control: the token did reach GitHub, from a mode-600 header file)"
st "$(cat "$W/ok/tokenmode")" "-rw-------" "and that header file was mode 600 while it existed"
st "$(grep -c "password=$TOKEN" "$W/ok/credout")" 1 "(null control: the credential helper delivered the token from the file, over its stdout)"
st "$(calls ok 'curl DELETE installation/token')" 1 "the installation token is revoked on exit"
st "$(leftover ok)" 0 "the private directory is gone after a success"
st "$(leaks ok)" 0 "no token, JWT, key or signature text in stdout or stderr after a success"
st "$(grep -c '^app_push: PUSHED ' "$W/ok/out")" 1 "and the read-back success line is printed"

# A pull request already open: PATCH its body instead of creating one.
mkcase prexist; printf '[{"number": 7}]' > "$W/prexist/listing.json"
run prexist o/r "$W/tool-wt" "$BR" "$W/body.md"; st $? 0 "an open pull request on the branch: pushed and re-bodied, not duplicated"
st "$(grep -c '^curl PATCH repos/o/r/pulls/7$' "$W/prexist/log")" 1 "its body is PATCHed with one call"
st "$(grep -c '^curl POST repos/o/r/pulls$' "$W/prexist/log")" 0 "and no create POST is made"
st "$(grep -c "$TOKEN" "$W/prexist/live-body" 2>/dev/null)" 0 "the PATCHed body carries no token"

# Refusals, each before anything is minted.
mkcase preprfail; : > "$W/preprfail/prepr-fails"
run preprfail o/r "$W/tool-wt" "$BR" "$W/body.md"; st $? 1 "REFUSE: prepr fails, so nothing is minted, pushed or posted"
st "$(calls preprfail curl)" 0 "no curl call at all: the refusal precedes the mint"
st "$(grep -c '^git .*push' "$W/preprfail/log")" 0 "and no push either (the ok case above is the healthy arm: it pushes exactly once)"

mkcase dirty; : > "$W/dirty/dirty"
run dirty o/r "$W/tool-wt" "$BR" "$W/body.md"; st $? 1 "REFUSE: a dirty worktree, prepr passed"
st "$(grep -c 'dirty; only a committed tip' "$W/dirty/err")" 1 "naming the dirty worktree"
st "$(calls dirty curl)" 0 "and nothing was minted"

mkcase tipmoved; : > "$W/tipmoved/tip-moved"
run tipmoved o/r "$W/tool-wt" "$BR" "$W/body.md"; st $? 1 "REFUSE: HEAD is not the branch's committed tip"
st "$(grep -c 'is not the committed tip' "$W/tipmoved/err")" 1 "naming the mismatch"
st "$(calls tipmoved curl)" 0 "and nothing was minted"

mkcase nokey
IDDIR="$W/nokey" run nokey o/r "$W/tool-wt" "$BR" "$W/body.md"; st $? 1 "REFUSE: the App private key is missing"
st "$(wc -l < "$W/nokey/log" | tr -d ' ')" 0 "before any prepr, gh, git, openssl or curl call"

mkcase badid
IDDIR="$W/badid" run badid o/r "$W/tool-wt" "$BR" "$W/body.md"; st $? 1 "REFUSE: an App id with a non-digit in it"
st "$(grep -c 'digits only' "$W/badid/err")" 1 "refused as malformed, not stripped to digits"
st "$(wc -l < "$W/badid/log" | tr -d ' ')" 0 "before any prepr, gh, git, openssl or curl call"

mkcase ghfail; : > "$W/ghfail/gh-fails"
run ghfail o/r "$W/tool-wt" "$BR" "$W/body.md"; st $? 1 "REFUSE: the open-pull-request query did not answer"
st "$(calls ghfail curl)" 0 "no answer, no mint: nothing was minted or pushed"
mkcase ghunknown; printf 'GraphQL: Could not resolve to a Repository' > "$W/ghunknown/listing.json"
run ghunknown o/r "$W/tool-wt" "$BR" "$W/body.md"; st $? 1 "REFUSE: prose is not a listing (the fail-open shape push.sh refuses)"

mkcase mainbr
run mainbr o/r "$W/tool-wt" main "$W/body.md"; st $? 1 "REFUSE: pushing main is not this tool's job"
mkcase usage
run usage o/r "$W/tool-wt" "$BR"; st $? 1 "REFUSE: four arguments are required"
mkcase nobody
run nobody o/r "$W/tool-wt" "$BR" "$W/nobody/missing/body.md"; st $? 1 "REFUSE: a body path that does not resolve"
st "$(grep -c '^app_push: REFUSE: no body at ' "$W/nobody/err")" 1 "naming the body path itself, not the pre-shift \$4 that set -u trips on after shift 4"

# After the mint: the push and the pull request can still fail, and the trap
# still revokes and removes.
mkcase pushfail; : > "$W/pushfail/push-fails"
run pushfail o/r "$W/tool-wt" "$BR" "$W/body.md"; st $? 1 "a refused push exits non-zero"
st "$(grep -c '^curl \(POST\|PATCH\) repos/o/r/pulls' "$W/pushfail/log")" 0 "and no pull request was created or re-bodied"
st "$(calls pushfail 'curl DELETE installation/token')" 1 "the token is revoked after the failed push"
st "$(leftover pushfail)" 0 "and the private directory is gone, token and all"

mkcase mangle; : > "$W/mangle/mangle-body"
run mangle o/r "$W/tool-wt" "$BR" "$W/body.md"; st $? 1 "a body that reads back different refuses, though the POST returned 0"
st "$(grep -c 'modulo one trailing newline' "$W/mangle/err")" 1 "naming the byte-identity rule it failed"
st "$(calls mangle 'curl DELETE installation/token')" 1 "the token is revoked after the failed read-back"
st "$(leaks mangle)" 0 "and no token, JWT, key or signature text reached stdout or stderr"

# --dry-run: every refusal, then nothing signed.
mkcase dry
run dry --dry-run o/r "$W/tool-wt" "$BR" "$W/body.md" 1234; st $? 0 "--dry-run passes every refusal"
st "$(calls dry curl)" 0 "and makes no curl call: nothing minted, pushed or posted"
st "$(calls dry openssl)" 0 "and signs nothing"
st "$(grep -c '^git .*push' "$W/dry/log")" 0 "and pushes nothing"
st "$(grep -c '^app_push: DRY-RUN' "$W/dry/out")" 1 "reporting what it would do"
mkcase dryfail; : > "$W/dryfail/prepr-fails"
run dryfail --dry-run o/r "$W/tool-wt" "$BR" "$W/body.md"; st $? 1 "--dry-run still refuses what a real run would"

echo "app_push self-test: $N checks, $FAILS failed"
[ "$FAILS" -eq 0 ]
