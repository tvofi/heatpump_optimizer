#!/bin/bash
# bus.sh -- git refs as the programme's message bus (round-9 process review
# item 9, adopted by tvofi 2026-10-01). Seats publish on refs; the orchestrator
# watches them; the coordinator is left to start seats and handle blocks.
#
#   bus.sh push-verdict <pr> <VERDICT.md> <evidence dir>       (reviewer)
#   bus.sh watch [--once] [--post] [--every <seconds>]          (orchestrator)
#   bus.sh dispatch <pr> <head> <reviewer>                      (orchestrator)
#   bus.sh confirm <pr> <review commit>                         (orchestrator)
#   bus.sh post <pr>                                            (orchestrator)
#   bus.sh --self-test
#
# THE REFS. `handoff/<topic>` is a fixer's code head; `handoff-body/<topic>` its
# body (`body_push.sh`); `review/<pr>` a reviewer's proposed verdicts;
# `verdict/<pr>` the verdicts the orchestrator confirmed and signed. Both
# verdict families are append-only like a body ref: each push adds one commit
# whose tree is VERDICT.md plus the evidence directory under `evidence/`, its
# parent the previous tip, so a later round never needs a force-push. A
# crossed-out verdict stays in the ref's history; only the tip is posted.
#
# push-verdict REFUSES, AND PUSHES NOTHING, unless the first line is in
# `fix-review.md`'s grammar (the regex is `app_comment.sh`'s), the verdict
# carries its dispatch's `bus-nonce:` line, and a file under the evidence
# directory names the verdict's 40-hex head. VERDICT.md alone does not count:
# it names the sha by construction, and `app_approve.sh`'s evidence gate
# exists to make a forged verdict forge artifacts too.
#
# watch lists the four ref families on the remote and prints one line per
# ref that appeared, moved or went since the last pass:
#   BUS handoff|body|review|verdict <name> <sha>|gone
# It records the pass in $HPO_BUS_STATE/refs (default ~/.zcode/bus), so each
# change is reported once. A first pass with no state records a baseline and
# reports nothing. Without --once it polls every --every seconds (default 60)
# and EXITS on the first pass that reports anything: run it as a background
# task and its exit wakes you (process review item 4), never a timer.
#
# THE REF IS NOT THE REVIEWER. Every cloud seat pushes with one credential, so
# a hand-made ref with a well-formed line and evidence is as easy for a fixer
# as for its reviewer (PROC-4's round-1 review drove exactly that to a post).
# So a reviewer's push proposes and only the orchestrator's signature posts:
#   - `dispatch` when the reviewer starts records PR, head and reviewer (its
#     thread or session id) and prints a fresh nonce for the reviewer's brief;
#     a nonce binds only the PR and head it was minted for.
#   - watch reports a new `review/<pr>` tip as `BUS undispatched` (no record
#     for its PR, head and nonce) or `BUS unconfirmed`, naming the reviewer.
#   - `confirm`, after the orchestrator has read that reviewer's OWN thread or
#     session output and found this commit there, re-publishes the commit's
#     tree on `verdict/<pr>`, signed with the `hpo-approver` App's private key
#     ($HPO_IDENTITY_DIR, default ~/.zcode, `identity-approver.pem`, the file
#     `app_comment.sh` signs with): "hpo-bus verdict <pr> <tree>" in a
#     `bus-signature:` line, binding the PR and the whole tree. The key stays on
#     the orchestrator's machine (tvofi, 2026-10-01: no App key in the cloud).
#   - --post, and `post <pr>`, post a `verdict/<pr>` tip only when that
#     signature verifies against the same key; anything else is `BUS unsigned`.
# WHAT THIS PROVES: a posted verdict was confirmed on the machine holding the
# key. The nonce ties a proposal to a dispatch, not to a seat (a brief is
# readable project-wide); authorship rests on the confirmation, as it did on
# the relay before the bus. It works with or without a coordinator.
#
# Posting goes through `app_comment.sh` (decision 0013), which keeps every
# refusal it has: the grammar, an open pull request, a `merge` verdict at
# exactly the live head, and the byte-identical read-back. The tip's tree is
# unpacked to $HPO_BUS_STATE/verdicts/<pr>/<commit>/, and the posted body is
# VERDICT.md and one line naming the ref, the commit, the reviewer and that
# directory's `evidence/` -- a directory on THIS machine holding a file that
# names the head, which is what `app_approve.sh`'s evidence gate reads. A
# commit is posted at most once ($HPO_BUS_STATE/posted); a refused one is
# reported `BUS refused` and not retried by watch -- `post <pr>` retries it.
#
# A VERDICT IS A COMMENT, NEVER A REVIEW. The bus posts only through
# `app_comment.sh` and approves nothing: a pull request touching code-owned
# paths still needs tvofi's own approving review (`main-protect-checks`'s
# code-owner rule), given by the orchestrator under the mandate, separately.
#
# Environment: HPO_BUS_REMOTE (origin), HPO_BUS_REPO (tvofi/heatpump_optimizer),
# HPO_BUS_POSTER (this checkout's app_comment.sh: tools/audit/ if a copy is
# restored there, else tools/pr/, where R9-RO-6 moved it), HPO_IDENTITY_DIR.
# Plain variables, no arrays: macOS /bin/bash 3.2 rejects an empty array under -u.
set -uo pipefail

ROOT=$(cd "$(dirname -- "$0")/../../.." && pwd)
REMOTE=${HPO_BUS_REMOTE:-origin}
REPO=${HPO_BUS_REPO:-tvofi/heatpump_optimizer}
POSTER=${HPO_BUS_POSTER:-}
if [ -z "$POSTER" ]; then
  if [ -f "$ROOT/tools/audit/app_comment.sh" ]; then POSTER=$ROOT/tools/audit/app_comment.sh; else POSTER=$ROOT/tools/pr/app_comment.sh; fi
fi
S=${HPO_BUS_STATE:-$HOME/.zcode/bus}
die() { printf 'bus: REFUSE: %s\n' "$*" >&2; exit 1; }

# The verdict's head sha, or a non-zero exit when the line is outside the
# grammar. The two patterns are `app_comment.sh`'s, character for character.
verdict_sha() { # first line
  if [[ $1 =~ ^Fix\ review:\ merge\ ([0-9a-f]{40})$ ]]; then printf '%s\n' "${BASH_REMATCH[1]}"; return 0; fi
  if [[ $1 =~ ^Fix\ review:\ blocked\ ([0-9a-f]{40})\ [a-z-]+:\ .+$ ]]; then printf '%s\n' "${BASH_REMATCH[1]}"; return 0; fi
  return 1
}
verdict_nonce() { # verdict file -> the first bus-nonce, or nothing
  sed -n 's/^bus-nonce: \([0-9a-f]\{32\}\)$/\1/p' "$1" | head -n 1
}
numeric() { case $1 in ''|*[!0-9]*) return 1 ;; esac; return 0; }
approver_key() { # -> the hpo-approver App's private key on this machine, or a non-zero exit
  local k=${HPO_IDENTITY_DIR:-$HOME/.zcode}/identity-approver.pem
  [ -f "$k" ] && printf '%s\n' "$k"
}
signed_by_approver() { # pr commit -> rc 0 when the commit's bus-signature is the approver key's over pr and tree
  local pr=$1 c=$2 key t rc line
  key=$(approver_key) || return 1
  t=$(mktemp -d) || return 1
  # Canonical base64 only: the decoded signature must re-encode to the line.
  line=$(git log -1 --format=%B "$c" | sed -n 's/^bus-signature: //p' | head -n 1)
  printf '%s' "$line" | openssl base64 -d -A > "$t/sig" 2>/dev/null \
    && [ -s "$t/sig" ] && [ "$(openssl base64 -A < "$t/sig")" = "$line" ] && openssl rsa -in "$key" -pubout -out "$t/pub" 2>/dev/null \
    && printf 'hpo-bus verdict %s %s\n' "$pr" "$(git rev-parse "$c^{tree}")" \
       | openssl dgst -sha256 -verify "$t/pub" -signature "$t/sig" >/dev/null 2>&1
  rc=$?; rm -rf "$t"; return $rc
}

push_verdict() { # pr verdict-file evidence-dir -> proposes the verdict on review/<pr>
  local pr=${1:-} v=${2:-} ev=${3:-} first hsha t gd tree
  numeric "$pr" || die "push-verdict: the pull request '$pr' is not a number"
  [ -f "$v" ] || die "push-verdict: no verdict file at '$v'"
  first=$(head -n 1 "$v")
  hsha=$(verdict_sha "$first") \
    || die "push-verdict: the first line is outside fix-review.md's grammar: '$first'"
  [ -n "$(verdict_nonce "$v")" ] \
    || die "push-verdict: no 'bus-nonce: <32 hex>' line; the dispatcher's brief gives it (bus.sh dispatch)"
  [ -n "$ev" ] && [ -d "$ev" ] || die "push-verdict: no evidence directory (a verdict cites one; fix-review.md)"
  grep -rqF -- "$hsha" "$ev" \
    || die "push-verdict: no file under $ev names the head $hsha"
  [ -z "$(find "$ev" -type f -size +50M 2>/dev/null)" ] \
    || die "push-verdict: a file under $ev is over 50 MB; cite it by path instead"
  t=$(mktemp -d) || die "push-verdict: no temporary directory"
  mkdir -p "$t/w/evidence" && cp "$v" "$t/w/VERDICT.md" && cp -R "$ev"/. "$t/w/evidence/" \
    || { rm -rf "$t"; die "push-verdict: could not stage the verdict and its evidence"; }
  # A private index over a scratch work tree: nothing touches the caller's
  # index or checkout, and -f keeps a global excludes file from dropping logs.
  gd=$(git rev-parse --absolute-git-dir) || { rm -rf "$t"; die "push-verdict: not inside a git checkout"; }
  tree=$(cd "$t/w" && export GIT_DIR="$gd" GIT_INDEX_FILE="$t/index" GIT_WORK_TREE="$t/w" \
         && git add -A -f . && git write-tree) \
    || { rm -rf "$t"; die "push-verdict: could not build the verdict's tree"; }
  rm -rf "$t"
  append_commit review "$pr" "$tree" "verdict: #$pr $first" || exit 1
}

append_commit() { # family pr tree message -> pushes one commit on <family>/<pr> after its tip, prints it
  local fam=$1 pr=$2 tree=$3 msg=$4 parent="" c
  if git ls-remote --exit-code -q "$REMOTE" "refs/heads/$fam/$pr" >/dev/null 2>&1; then
    git fetch -q "$REMOTE" "refs/heads/$fam/$pr" || { printf 'bus: REFUSE: could not fetch %s/%s\n' "$fam" "$pr" >&2; return 1; }
    parent="-p $(git rev-parse FETCH_HEAD)"
  fi
  # shellcheck disable=SC2086 # $parent is empty or exactly "-p <sha>"
  c=$(git commit-tree "$tree" $parent -m "$msg") || { printf 'bus: REFUSE: commit-tree failed\n' >&2; return 1; }
  git push -q "$REMOTE" "$c:refs/heads/$fam/$pr" || { printf 'bus: REFUSE: the push of %s/%s was refused\n' "$fam" "$pr" >&2; return 1; }
  printf '%s/%s %s\n' "$fam" "$pr" "$c"
}

snapshot() { # -> "<name> <sha>" for every bus ref on the remote, sorted
  git ls-remote --heads "$REMOTE" | awk '
    { r = $2; sub(/^refs\/heads\//, "", r) }
    r ~ /^(handoff|handoff-body|review|verdict)\// { print r, $1 }' | LC_ALL=C sort
}

kind_of() { # ref name -> "<kind> <name>"
  case $1 in
    handoff-body/*) printf 'body %s\n' "${1#handoff-body/}" ;;
    handoff/*) printf 'handoff %s\n' "${1#handoff/}" ;;
    review/*) printf 'review %s\n' "${1#review/}" ;;
    verdict/*) printf 'verdict %s\n' "${1#verdict/}" ;;
  esac
}

unpack() { # family pr [want] -> sets c d first hsha in the caller; prints BUS refused, rc 1
  local fam=$1 want=${3:-} why=""
  pr=$2
  numeric "$pr" || { printf 'BUS refused %s: %s/%s is not a pull-request number\n' "$pr" "$fam" "$pr"; return 1; }
  if ! git fetch -q "$REMOTE" "+refs/heads/$fam/$pr:refs/hpo-bus/$fam/$pr" 2>/dev/null; then
    printf 'BUS refused %s: could not fetch %s/%s\n' "$pr" "$fam" "$pr"; return 1
  fi
  c=$(git rev-parse "refs/hpo-bus/$fam/$pr")
  if [ -n "$want" ] && [ "$c" != "$want" ]; then
    printf 'BUS refused %s %s: the tip of %s/%s is %s; only a tip counts\n' "$pr" "$want" "$fam" "$pr" "$c"; return 1
  fi
  d=$S/${fam}s/$pr/$c
  rm -rf "$d" && mkdir -p "$d" && git archive "$c" | tar -x -C "$d" \
    || { printf 'BUS refused %s %s: could not unpack the verdict tree\n' "$pr" "$c"; return 1; }
  if [ ! -f "$d/VERDICT.md" ]; then why="the tree has no VERDICT.md"
  else
    first=$(head -n 1 "$d/VERDICT.md")
    if ! hsha=$(verdict_sha "$first"); then why="the first line is outside fix-review.md's grammar: '$first'"
    elif ! grep -rqF -- "$hsha" "$d/evidence" 2>/dev/null; then why="no file under evidence/ names the head $hsha"
    fi
  fi
  [ -z "$why" ] || { printf 'BUS refused %s %s: %s\n' "$pr" "$c" "$why"; return 1; }
}

dispatched_to() { # uses pr c d hsha -> sets thread; prints BUS undispatched, rc 1
  local nonce
  nonce=$(verdict_nonce "$d/VERDICT.md")
  thread=$(awk -v k="$pr $hsha " -v n="$nonce" 'index($0, k) == 1 && n != "" && $4 == n { print $3; exit }' "$S/dispatched" 2>/dev/null)
  [ -n "$thread" ] && return 0
  printf 'BUS undispatched %s %s: no dispatch record for #%s at %s with this verdict'"'"'s nonce\n' "$pr" "$c" "$pr" "$hsha"; return 1
}

review_status() { # pr [want] -> prints BUS undispatched|unconfirmed|refused; always rc 1 (nothing posts)
  local pr c d first hsha thread
  unpack review "$1" "${2:-}" || return 1
  dispatched_to || return 1
  printf 'BUS unconfirmed %s %s: read %s'"'"'s own output for this commit, then: bus.sh confirm %s %s\n' \
    "$pr" "$c" "$thread" "$pr" "$c"; return 1
}

post_verdict() { # pr [expected sha] -> prints one BUS posted|refused|unsigned line; rc 0 posted
  local pr c d first hsha body who sig
  unpack verdict "$1" "${2:-}" || return 1
  if grep -qx "$pr $c" "$S/posted" 2>/dev/null; then
    printf 'BUS refused %s %s: already posted\n' "$pr" "$c"; return 1
  fi
  if ! signed_by_approver "$pr" "$c"; then
    printf 'BUS unsigned %s %s: not signed with hpo-approver'"'"'s key; a reviewer proposes on review/%s and the orchestrator confirms it\n' "$pr" "$c" "$pr"; return 1
  fi
  # A commit is not what was signed: a keyless seat can re-commit an earlier
  # confirmed tree and message after a later round and supersede it (round-2
  # review of PROC-4), or re-encode its signature line (round 3). What is
  # signed is "<pr> <tree>", so each tree posts once per pull request whatever
  # commit or encoding carries it; each round's nonce makes its tree distinct.
  sig=$(git rev-parse "$c^{tree}")
  if grep -qxF -- "$pr $sig" "$S/posted-signed" 2>/dev/null; then
    printf 'BUS refused %s %s: this signed verdict was already posted on #%s (a replay)\n' "$pr" "$c" "$pr"; return 1
  fi
  who=$(git log -1 --format=%B "$c" | sed -n 's/^bus-confirmed: //p' | head -n 1)
  body=$S/verdicts/$pr/$c.md
  { cat "$d/VERDICT.md"
    printf '\nbus: verdict/%s at %s, confirmed from %s; evidence: %s/evidence\n' "$pr" "$c" "$who" "$d"
  } > "$body"
  # Recorded BEFORE the post and withdrawn on a refusal: a kill between a
  # landed post and the record would otherwise post twice. A kill now leaves
  # "already posted" on a verdict that may not have landed; read the PR.
  printf '%s %s\n' "$pr" "$c" >> "$S/posted"
  printf '%s %s\n' "$pr" "$sig" >> "$S/posted-signed"
  if ! "$POSTER" "$REPO" "$pr" "$body" >"$body.log" 2>&1; then
    grep -vx "$pr $c" "$S/posted" > "$S/posted.new"; mv "$S/posted.new" "$S/posted"
    grep -vxF -- "$pr $sig" "$S/posted-signed" > "$S/posted-signed.new"; mv "$S/posted-signed.new" "$S/posted-signed"
    printf 'BUS refused %s %s: the poster refused (%s): %s\n' "$pr" "$c" "$POSTER" "$(tail -n 1 "$body.log")"; return 1
  fi
  printf 'BUS posted %s %s %s\n' "$pr" "$c" "$first"
}

dispatch() { # pr head reviewer -> records the dispatch, prints the nonce line for the brief
  local pr=${1:-} h=${2:-} r=${3:-} n
  numeric "$pr" || die "dispatch: the pull request '$pr' is not a number"
  [[ $h =~ ^[0-9a-f]{40}$ ]] || die "dispatch: '$h' is not a 40-hex head"
  [[ $r =~ ^[A-Za-z0-9_-]+$ ]] || die "dispatch: name the reviewer's thread or session as one token"
  n=$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n')
  [[ $n =~ ^[0-9a-f]{32}$ ]] || die "dispatch: could not mint a nonce"
  mkdir -p "$S" && printf '%s %s %s %s\n' "$pr" "$h" "$r" "$n" >> "$S/dispatched" || die "dispatch: cannot record in $S"
  printf 'bus-nonce: %s\n' "$n"
}

confirm() { # pr review-commit -> signs the reviewer's proposal onto verdict/<pr>, then posts it
  local pr c d first hsha thread key tree sig msg line v
  numeric "${1:-}" || die "confirm: the pull request '${1:-}' is not a number"
  [[ ${2:-} =~ ^[0-9a-f]{40}$ ]] || die "confirm: '${2:-}' is not a 40-hex review commit"
  key=$(approver_key) || die "confirm: no hpo-approver key on this machine; confirm where it is kept"
  mkdir -p "$S" || die "confirm: cannot create $S"
  unpack review "$1" "$2" || return 1
  dispatched_to || return 1
  tree=$(git rev-parse "$c^{tree}")
  sig=$(printf 'hpo-bus verdict %s %s\n' "$pr" "$tree" | openssl dgst -sha256 -sign "$key" | openssl base64 -A) \
    && [ -n "$sig" ] || die "confirm: signing with $key failed"
  msg=$(printf 'verdict: #%s %s\n\nbus-confirmed: %s (review/%s at %s)\nbus-signature: %s' "$pr" "$first" "$thread" "$pr" "$c" "$sig")
  line=$(append_commit verdict "$pr" "$tree" "$msg") || return 1
  v=${line#* }
  post_verdict "$pr" "$v"
}

watch_once() { # post? -> prints events; rc 0 when any, 3 when quiet, 1 on error
  local post=$1 cur events line kind name sha
  mkdir -p "$S" || die "watch: cannot create $S"
  cur=$(snapshot) || die "watch: could not list the refs of $REMOTE"
  if [ ! -f "$S/refs" ]; then
    printf '%s\n' "$cur" | grep -v '^$' > "$S/refs"
    printf 'bus: baseline of %s ref(s) recorded in %s/refs; changes from here on are reported\n' \
      "$(grep -c . "$S/refs")" "$S"
    return 3
  fi
  events=$(printf '%s\n' "$cur" | grep -v '^$' | awk '
    FILENAME == ARGV[1] { old[$1] = $2; next }
    { seen[$1] = 1; if (old[$1] != $2) print $1, $2 }
    END { for (r in old) if (!(r in seen)) print r, "gone" }' "$S/refs" - | LC_ALL=C sort)
  [ -n "$events" ] || return 3
  while read -r name sha; do
    line=$(kind_of "$name"); kind=${line%% *}
    printf 'BUS %s %s %s\n' "$kind" "${line#* }" "$sha"
    if [ "$post" = 1 ] && [ "$sha" != gone ]; then
      case $kind in
        review) review_status "${line#* }" "$sha" </dev/null ;;
        verdict) grep -qx "${line#* } $sha" "$S/posted" 2>/dev/null || post_verdict "${line#* }" "$sha" </dev/null ;;
      esac
    fi
  done <<EOF
$events
EOF
  printf '%s\n' "$cur" | grep -v '^$' > "$S/refs.new" && mv "$S/refs.new" "$S/refs"
  return 0
}

watch() {
  local once=0 post=0 every=60 rc
  while [ $# -gt 0 ]; do
    case $1 in
      --once) once=1 ;;
      --post) post=1 ;;
      --every) shift; numeric "${1:-}" || die "watch: --every takes seconds"; every=$1 ;;
      *) die "watch: unknown argument '$1'" ;;
    esac
    shift
  done
  while :; do
    watch_once "$post"; rc=$?
    [ $rc = 3 ] || return $rc
    [ $once = 1 ] && return 0
    sleep "$every"
  done
}

self_test() {
  local W pass=0 fail=0 out rc h1 h2 r1 r2 r9 v1 v2 ra rs rf t tt ev n N0 N1 N1b N2 N9
  local N3 N4 DT fa g1 ro n0 realgit want wanttree
  W=$(mktemp -d) || { echo "self-test: no temporary directory"; return 1; }
  ok() { pass=$((pass + 1)); printf '  ok   %s\n' "$1"; }
  bad() { fail=$((fail + 1)); printf '  FAIL %s\n' "$1"; }
  expect() { # name condition-rc
    if [ "$2" = 0 ]; then ok "$1"; else bad "$1"; fi
  }
  # Hermetic: no global or system git config (identity, hooks, push
  # negotiation) and no auto-maintenance, through the shared helper.
  . "$ROOT/tests/throwaway_git.sh" && throwaway_git_env
  throwaway_git_init "$W/origin.git" -q --bare
  throwaway_git_init "$W/seat" -q && git -C "$W/seat" remote add origin "$W/origin.git"
  git -C "$W/seat" -c user.name=t -c user.email=t@t commit -q --allow-empty -m base
  git -C "$W/seat" push -q origin HEAD:refs/heads/main
  h1=1111111111111111111111111111111111111111
  h2=2222222222222222222222222222222222222222
  mkdir -p "$W/ev1" "$W/ev2" "$W/evnone"
  printf 'measured at %s\n' "$h1" > "$W/ev1/run.log"
  printf 'measured at %s\n' "$h2" > "$W/ev2/run.log"
  printf 'nothing here\n' > "$W/evnone/run.log"
  N0=00000000000000000000000000000000
  printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$h1" "$N0" > "$W/merge0.md"
  printf 'Fix review: approve %s\n\nbus-nonce: %s\n' "$h1" "$N0" > "$W/badgrammar.md"
  printf 'Fix review: merge %s\n\nRESULT ok\n' "$h1" > "$W/nononce.md"
  # The poster stub records its arguments and the body it was handed.
  cat > "$W/poster" <<'P'
#!/bin/bash
printf '%s %s %s\n' "$1" "$2" "$3" >> "$BUS_TEST_CALLS"
cp "$3" "$BUS_TEST_LAST"
[ -z "${BUS_TEST_POSTER_FAIL:-}" ] || { echo "stub refusal"; exit 1; }
P
  chmod +x "$W/poster"
  export BUS_TEST_CALLS=$W/calls BUS_TEST_LAST=$W/last
  : > "$W/calls"
  # BUS_ID picks the identity directory: $W/ap holds the approver's key (the
  # orchestrator's machine), $W/fx a key a fixer made itself under the same
  # name, $W/noid none (every seat).
  mkdir -p "$W/ap" "$W/fx" "$W/noid"
  openssl genrsa -out "$W/ap/identity-approver.pem" 2048 2>/dev/null
  openssl genrsa -out "$W/fx/identity-approver.pem" 2048 2>/dev/null
  run() { (cd "$W/seat" && HPO_BUS_STATE=$W/state HPO_BUS_POSTER=$W/poster HPO_BUS_REPO=o/r \
           HPO_IDENTITY_DIR=${BUS_ID:-$W/ap} bash "$ROOT/tools/audit/seat/bus.sh" "$@") 2>&1; }
  seat() { BUS_ID=$W/noid run "$@"; }
  calls() { grep -c . "$W/calls"; }
  tip() { git -C "$W/origin.git" rev-parse "$1"; }
  # A raw commit on origin: VERDICT.md from stdin, evidence/run.log naming $1
  # when $1 is given, the message from $2.
  raw() {
    local b e tr
    b=$(git -C "$W/seat" hash-object -w --stdin)
    if [ -n "$1" ]; then
      e=$(printf 'measured at %s\n' "$1" | git -C "$W/seat" hash-object -w --stdin)
      e=$(printf '100644 blob %s\trun.log\n' "$e" | git -C "$W/seat" mktree)
      tr=$(printf '100644 blob %s\tVERDICT.md\n040000 tree %s\tevidence\n' "$b" "$e" | git -C "$W/seat" mktree)
    else tr=$(printf '100644 blob %s\tVERDICT.md\n' "$b" | git -C "$W/seat" mktree)
    fi
    printf '%s' "$2" | git -C "$W/seat" commit-tree "$tr"
  }

  # -x: the whole default line, so this pin cannot match itself.
  grep -qxF '  if [ -f "$ROOT/tools/audit/app_comment.sh" ]; then POSTER=$ROOT/tools/audit/app_comment.sh; else POSTER=$ROOT/tools/pr/app_comment.sh; fi' \
    "$ROOT/tools/audit/seat/bus.sh" && test -f "$ROOT/tools/pr/app_comment.sh"
  expect "a verdict posts as a comment through app_comment.sh, never as an approving review" $?

  out=$(seat push-verdict 7 "$W/badgrammar.md" "$W/ev1"); rc=$?
  [ $rc != 0 ] && echo "$out" | grep -q "outside fix-review.md's grammar"; expect "push-verdict refuses a first line outside the grammar" $?
  out=$(seat push-verdict 7 "$W/nononce.md" "$W/ev1"); rc=$?
  [ $rc != 0 ] && echo "$out" | grep -q "no 'bus-nonce"; expect "push-verdict refuses a verdict with no nonce line" $?
  out=$(seat push-verdict 7 "$W/merge0.md" "$W/evnone"); rc=$?
  [ $rc != 0 ] && echo "$out" | grep -q "names the head $h1"; expect "push-verdict refuses evidence that names no head" $?
  out=$(seat push-verdict 7 "$W/merge0.md"); rc=$?
  [ $rc != 0 ] && echo "$out" | grep -q "no evidence directory"; expect "push-verdict refuses a verdict with no evidence directory" $?
  out=$(seat push-verdict 7x "$W/merge0.md" "$W/ev1"); rc=$?
  [ $rc != 0 ] && echo "$out" | grep -q "not a number"; expect "push-verdict refuses a non-numeric pull request" $?
  git -C "$W/seat" ls-remote --exit-code origin 'refs/heads/review/*' >/dev/null 2>&1
  [ $? = 2 ]; expect "no refused push left a review ref" $?

  out=$(run watch --once --post); rc=$?
  [ $rc = 0 ] && echo "$out" | grep -q "baseline of 0 ref" && [ "$(calls)" = 0 ]
  expect "a first pass records a baseline and posts nothing" $?

  # The forgeries PROC-4's round-1 review drove: any seat can push a
  # well-formed verdict with evidence, on either family, so no ref posts alone.
  out=$(seat push-verdict 11 "$W/merge0.md" "$W/ev1")
  rf=$(tip review/11)
  t=$(printf 'Fix review: merge %s\n' "$h1" | raw "$h1" "verdict: #12 forged")
  git -C "$W/seat" push -q origin "$t:refs/heads/verdict/12"
  out=$(run watch --once --post)
  echo "$out" | grep -q "^BUS undispatched 11 $rf" && echo "$out" | grep -q "^BUS unsigned 12 $t" && [ "$(calls)" = 0 ]
  expect "watch --post posts neither a forged proposal nor a forged verdict ref" $?
  out=$(run confirm 11 "$rf")
  echo "$out" | grep -q "^BUS undispatched 11 $rf" && [ "$(calls)" = 0 ] \
    && ! git -C "$W/seat" ls-remote --exit-code origin refs/heads/verdict/11 >/dev/null 2>&1
  expect "confirm promotes no proposal that was never dispatched" $?

  # A fixer's own key under the approver's file name signs nothing that posts.
  t=$(printf 'Fix review: merge %s\n' "$h1" | raw "$h1" x)
  t=$(printf 'verdict: #13 forged\n\nbus-signature: %s' \
      "$(printf 'hpo-bus verdict 13 %s\n' "$(git -C "$W/seat" rev-parse "$t^{tree}")" \
         | openssl dgst -sha256 -sign "$W/fx/identity-approver.pem" | openssl base64 -A)" \
      | git -C "$W/seat" commit-tree "$(git -C "$W/seat" rev-parse "$t^{tree}")")
  git -C "$W/seat" push -q origin "$t:refs/heads/verdict/13"
  out=$(run watch --once --post)
  echo "$out" | grep -q "^BUS unsigned 13 $t" && [ "$(calls)" = 0 ]
  expect "a verdict signed with a key that is not the approver's does not post" $?

  N1=$(run dispatch 7 "$h1" cmsg_R | sed -n 's/^bus-nonce: //p')
  [[ $N1 =~ ^[0-9a-f]{32}$ ]] && grep -qx "7 $h1 cmsg_R $N1" "$W/state/dispatched"
  expect "dispatch records pr, head and reviewer and prints a fresh nonce" $?
  N1b=$(run dispatch 12 "$h1" cmsg_Q | sed -n 's/^bus-nonce: //p')
  [ "$N1" != "$N1b" ]; expect "two dispatches mint two nonces" $?
  printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$h1" "$N1" > "$W/merge.md"
  printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$h1" "$N1b" > "$W/othernonce.md"
  out=$(seat push-verdict 7 "$W/othernonce.md" "$W/ev1")
  ra=$(tip review/7)
  out=$(run watch --once --post)
  echo "$out" | grep -q "^BUS undispatched 7 $ra" && [ "$(calls)" = 0 ]
  expect "another dispatch's nonce does not count" $?

  git -C "$W/seat" push -q origin HEAD:refs/heads/handoff/t1
  out=$(seat push-verdict 7 "$W/merge.md" "$W/ev1"); rc=$?
  r1=$(tip review/7)
  [ $rc = 0 ] && [ "$(tip review/7^)" = "$ra" ]; expect "push-verdict proposes on review/<pr>, fast-forwarding it" $?
  out=$(run watch --once --post)
  echo "$out" | grep -qx "BUS handoff t1 $(git -C "$W/seat" rev-parse HEAD)"; expect "watch reports a new handoff ref" $?
  echo "$out" | grep -qx "BUS review 7 $r1"; expect "watch reports a new review ref" $?
  echo "$out" | grep -q "^BUS unconfirmed 7 $r1: read cmsg_R's own output .*bus.sh confirm 7 $r1" && [ "$(calls)" = 0 ]
  expect "a dispatched proposal waits for the orchestrator's confirmation, naming the reviewer" $?
  out=$(run confirm 7 "$ra")
  echo "$out" | grep -q "^BUS refused 7 $ra: the tip of review/7 is $r1" && [ "$(calls)" = 0 ]
  expect "a confirmation for a commit that is not the tip posts nothing" $?
  out=$(seat confirm 7 "$r1"); rc=$?
  [ $rc != 0 ] && echo "$out" | grep -q "no hpo-approver key" && [ "$(calls)" = 0 ]
  expect "confirm refuses on a machine without the approver key" $?
  out=$(run confirm 7 "$r1")
  v1=$(tip verdict/7)
  echo "$out" | grep -q "^BUS posted 7 $v1 Fix review: merge $h1" && [ "$(calls)" = 1 ]; expect "confirm signs the proposal onto verdict/<pr> and posts it once" $?
  [ "$(tip "verdict/7^{tree}")" = "$(tip "review/7^{tree}")" ]; expect "the signed verdict carries the reviewer's tree unchanged" $?
  grep -q "^bus: verdict/7 at $v1, confirmed from cmsg_R (review/7 at $r1);" "$W/last"; expect "the posted body names the reviewer and the proposal" $?
  [ "$(head -n 1 "$W/last")" = "Fix review: merge $h1" ]; expect "the posted body keeps the reviewer's first line" $?
  ev=$(sed -n 's/^bus: .*; evidence: //p' "$W/last")
  case $ev in /*) [ -d "$ev" ] && grep -rqF "$h1" "$ev" ;; *) false ;; esac
  expect "the posted body cites an absolute evidence directory that names the head" $?
  grep -q "^o/r 7 " "$W/calls"; expect "the poster is called with the repository and pull request" $?
  out=$(run watch --once --post); rc=$?
  [ $rc = 0 ] && ! echo "$out" | grep -q "^BUS refused" && [ "$(calls)" = 1 ]; expect "watch passes over a verdict it already posted" $?
  out=$(run watch --once --post); rc=$?
  [ $rc = 0 ] && [ -z "$out" ]; expect "an unchanged pass reports and posts nothing" $?
  out=$(run post 7); rc=$?
  [ $rc != 0 ] && echo "$out" | grep -q "already posted" && [ "$(calls)" = 1 ]; expect "post refuses a commit already posted" $?

  # A signed verdict copied to another pull request, or re-used over another tree.
  git -C "$W/seat" fetch -q origin verdict/7
  git -C "$W/seat" push -q origin "$v1:refs/heads/verdict/15"
  t=$(printf 'Fix review: merge %s\n' "$h1" | raw "$h1" "$(git -C "$W/seat" log -1 --format=%B "$v1")")
  t=$(git -C "$W/seat" log -1 --format=%B "$v1" | git -C "$W/seat" commit-tree "$(git -C "$W/seat" rev-parse "$t^{tree}")" -p "$v1")
  git -C "$W/seat" push -q origin "$t:refs/heads/verdict/7"
  out=$(run watch --once --post)
  echo "$out" | grep -q "^BUS unsigned 15 $v1" && [ "$(calls)" = 1 ]
  expect "a signed verdict moved to another pull request does not post" $?
  echo "$out" | grep -q "^BUS unsigned 7 $t"; expect "a signature over another tree does not post" $?
  tt=$t

  # Round 2 at a new head: a fresh dispatch; round 1's nonce no longer binds.
  printf 'Fix review: blocked %s harness: class-open x\n\nbus-nonce: %s\n' "$h2" "$N1" > "$W/stale.md"
  out=$(seat push-verdict 7 "$W/stale.md" "$W/ev2")
  rs=$(tip review/7)
  out=$(run watch --once --post)
  echo "$out" | grep -q "^BUS undispatched 7 $rs" && [ "$(calls)" = 1 ]; expect "round 1's nonce does not count at another head" $?
  N2=$(run dispatch 7 "$h2" cmsg_R | sed -n 's/^bus-nonce: //p')
  printf 'Fix review: blocked %s harness: class-open x\n\nbus-nonce: %s\n' "$h2" "$N2" > "$W/blocked.md"
  out=$(seat push-verdict 7 "$W/blocked.md" "$W/ev2")
  r2=$(tip review/7)
  out=$(run confirm 7 "$r2")
  v2=$(tip verdict/7)
  echo "$out" | grep -q "^BUS posted 7 $v2 Fix review: blocked $h2" && [ "$(calls)" = 2 ] \
    && [ "$(tip verdict/7^)" = "$tt" ]
  expect "a later round fast-forwards the verdict ref and is posted" $?
  # The replay the round-2 review drove: round 1's signed merge re-committed
  # by a keyless seat after round 2's block, to supersede it.
  t=$(git -C "$W/seat" log -1 --format=%B "$v1" | git -C "$W/seat" commit-tree "$(tip "$v1^{tree}")" -p "$v2")
  git -C "$W/seat" fetch -q origin verdict/7
  git -C "$W/seat" push -q origin "$t:refs/heads/verdict/7"
  out=$(run watch --once --post)
  echo "$out" | grep -q "^BUS refused 7 $t: this signed verdict was already posted on #7 (a replay)" && [ "$(calls)" = 2 ]
  expect "a confirmed verdict replayed after a later round does not post again" $?
  # Round 3's review: the same signature re-encoded (padding, a trailing space).
  for t in "$(git -C "$W/seat" log -1 --format=%B "$v1" | sed 's/^\(bus-signature: .*\)$/\1=/')" \
           "$(git -C "$W/seat" log -1 --format=%B "$v1" | sed 's/^\(bus-signature: .*\)$/\1 /')"; do
    t=$(printf '%s' "$t" | git -C "$W/seat" commit-tree "$(tip "$v1^{tree}")" -p "$(tip verdict/7)")
    git -C "$W/seat" push -q origin "$t:refs/heads/verdict/7"
    out=$(run watch --once --post)
    echo "$out" | grep -q "^BUS \(refused\|unsigned\) 7 $t" && [ "$(calls)" = 2 ]
    expect "a replay with its signature line re-encoded does not post again" $?
  done
  out=$(cd "$W/seat" && HPO_IDENTITY_DIR=$W/ap bash -c '. /dev/stdin; signed_by_approver 7 "$1" && echo verified' _ "$t" <<B 2>&1
$(sed -n '/^approver_key() {/,/^}/p;/^signed_by_approver() {/,/^}/p' "$ROOT/tools/audit/seat/bus.sh")
B
)
  [ -z "$out" ]; expect "a signature line that is not canonical base64 does not verify" $?

  # Raw refs are still checked before anything else.
  t=$(printf 'Fix review: approve %s\n' "$h1" | raw "" raw)
  git -C "$W/seat" push -q origin "$t:refs/heads/verdict/8"
  out=$(run watch --once --post)
  echo "$out" | grep -q "^BUS refused 8 $t: the first line is outside" && [ "$(calls)" = 2 ]
  expect "watch refuses a raw ref outside the grammar and posts nothing" $?
  out=$(run watch --once --post)
  [ -z "$out" ]; expect "a refused verdict is not retried on the next pass" $?
  t=$(printf 'Fix review: merge %s\n' "$h1" | raw "" raw)
  git -C "$W/seat" push -q origin "$t:refs/heads/review/10"
  out=$(run watch --once --post)
  echo "$out" | grep -q "^BUS refused 10 $t: no file under evidence/ names the head" && [ "$(calls)" = 2 ]
  expect "watch refuses a raw proposal whose only naming file is VERDICT.md" $?

  N9=$(run dispatch 9 "$h1" cmsg_S | sed -n 's/^bus-nonce: //p')
  printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$h1" "$N9" > "$W/merge9.md"
  out=$(seat push-verdict 9 "$W/merge9.md" "$W/ev1")
  r9=$(tip review/9)
  out=$(BUS_TEST_POSTER_FAIL=1 run confirm 9 "$r9")
  echo "$out" | grep -q "^BUS refused 9 .*the poster refused" && ! grep -q "^9 " "$W/state/posted"
  expect "a poster refusal is reported and not recorded as posted" $?
  out=$(run post 9)
  echo "$out" | grep -q "^BUS posted 9 "; expect "post retries a refused verdict by hand" $?

  git -C "$W/seat" push -q origin :refs/heads/handoff/t1
  out=$(run watch --once)
  echo "$out" | grep -qx "BUS handoff t1 gone"; expect "watch reports a deleted ref" $?

  git -C "$W/seat" push -q origin HEAD:refs/heads/handoff-body/t1
  out=$(run watch --every 1); rc=$?
  [ $rc = 0 ] && echo "$out" | grep -q "^BUS body t1 "; expect "watch without --once exits on its first event" $?
  # No `timeout`: it is GNU coreutils, absent from stock macOS (exit 127 there).
  (cd "$W/seat" && HPO_BUS_STATE=$W/state exec bash "$ROOT/tools/audit/seat/bus.sh" watch --every 1) > "$W/wait.out" 2>&1 &
  t=$!
  sleep 3
  kill -0 "$t" 2>/dev/null; rc=$?
  kill "$t" 2>/dev/null; wait "$t" 2>/dev/null
  [ $rc = 0 ] && [ ! -s "$W/wait.out" ]; expect "watch without --once keeps waiting while nothing changes" $?

  # ---- THE TIP IS WHAT THE REMOTE ANSWERED, NOT WHAT FETCH_HEAD HOLDS ----
  # R9-RC-BUS-FETCHHEAD. Both halves were measured on 2026-10-09: #2071's
  # round-4 reviewer's verdict commit was built parented on main's tip, and the
  # orchestrator's `git fetch -q origin <ref>` then `git -C <other worktree>
  # reset --hard FETCH_HEAD` answered `fatal: ambiguous argument 'FETCH_HEAD'`.
  # The perturbation is a fetch of an UNRELATED ref landing between
  # append_commit's fetch of the bus ref and its read of the tip -- the window a
  # sibling seat, the orchestrator or a watcher walks into. It is planted inside
  # that window, not before it: measured first, because it decides whether this
  # case can be green on the bug (probe 2026-10-09, and `git fetch`'s own
  # behaviour) -- a `git fetch` rewrites FETCH_HEAD even when the ref is
  # unchanged, so the script's own fetch would overwrite any plant placed ahead
  # of it and the case would pass with the defect in place. So a git wrapper on
  # PATH performs the unrelated fetch after the first fetch it sees, in this
  # checkout, once per run: the exact state another writer leaves behind.
  # The assertion is the PARENT SHA of the built commit, read off the ref, never
  # whether the push was accepted: a refused push IS today's behaviour on the
  # bug, and a case that passes on refusal proves nothing.
  mkdir -p "$W/shim"
  printf '%s\n' '#!/bin/bash' \
    'if [ "${1:-}" = fetch ] && [ ! -e "$BUS_ST_WINDOW" ]; then' \
    '  : > "$BUS_ST_WINDOW"' \
    '  "$BUS_ST_REAL" "$@"' \
    '  rc=$?' \
    '  "$BUS_ST_REAL" -C "$PWD" fetch -q origin refs/heads/main >/dev/null 2>&1' \
    '  exit $rc' \
    'fi' \
    'exec "$BUS_ST_REAL" "$@"' > "$W/shim/git"
  chmod +x "$W/shim/git"
  realgit=$(command -v git)
  N3=$(run dispatch 21 "$h1" cmsg_F | sed -n 's/^bus-nonce: //p')
  printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$h1" "$N3" > "$W/ff1.md"
  printf 'Fix review: blocked %s harness: class-open x\n\nbus-nonce: %s\n' "$h2" "$N3" > "$W/ff2.md"
  seat push-verdict 21 "$W/ff1.md" "$W/ev1" >/dev/null
  fa=$(tip review/21)
  rm -f "$W/window"
  out=$(BUS_ST_WINDOW=$W/window BUS_ST_REAL=$realgit PATH="$W/shim:$PATH" \
        seat push-verdict 21 "$W/ff2.md" "$W/ev2"); rc=$?
  [ $rc = 0 ] && [ "$(tip review/21)" != "$fa" ] && [ "$(tip review/21^)" = "$fa" ] \
    && [ "$(git -C "$W/seat" rev-parse FETCH_HEAD)" != "$fa" ]
  expect "an intervening fetch of an unrelated ref does not reparent the appended commit" $?

  # NULL CONTROL for the same fix: the ordinary append with no plant, which
  # already worked, is byte-for-byte the commit it always was. The expected
  # commit is re-derived here from the same staged content, the same parent and
  # the same message with both timestamps pinned to the same literals on each
  # side, so ONE sha carries tree, parent, message and identity at once -- a
  # moved parent, a changed tree or a reworded message all fail it. The tree is
  # named too, because the claim the brief owes is a byte-identical ref tree.
  DT=2026-10-09T12:00:00+02:00
  seat push-verdict 22 "$W/ff1.md" "$W/ev1" >/dev/null
  g1=$(tip review/22)
  t=$(raw "$h2" x < "$W/ff2.md")
  wanttree=$(git -C "$W/seat" rev-parse "$t^{tree}")
  want=$(GIT_AUTHOR_DATE=$DT GIT_COMMITTER_DATE=$DT git -C "$W/seat" commit-tree "$wanttree" \
         -p "$g1" -m "verdict: #22 $(head -n 1 "$W/ff2.md")")
  out=$(GIT_AUTHOR_DATE=$DT GIT_COMMITTER_DATE=$DT seat push-verdict 22 "$W/ff2.md" "$W/ev2")
  [ "$(tip review/22)" = "$want" ] && [ "$(tip 'review/22^{tree}')" = "$wanttree" ] \
    && [ "$(tip review/22^)" = "$g1" ]
  expect "an ordinary append with no intervening fetch is the same commit object as before" $?

  # A COPY OF THE SCRIPT OUTSIDE A CHECKOUT REFUSES BEFORE ANY PUSH (#2074).
  # ROOT is three levels above the file, so a copy parked in a throwaway
  # directory derives its poster from a path that cannot exist -- and `confirm`
  # used to find that out only after signing and pushing verdict/<pr>: the
  # verdict ref moved to 7c64dd213, the comment never posted, and the record was
  # left saying "already posted" for the older tip. The guard is at load, so the
  # case asserts the ref never moved AND the poster was never called. HPO_BUS_POSTER
  # is deliberately not set on this one call: the derived default is the thing
  # under test, and every other call in this self-test sets it, which is this
  # case's own null control (a script run from the checkout is not refused).
  # The proposal is for a PR whose dispatch matches, or the unfixed script would
  # stop at dispatched_to and the case would be green on the defect (#2074's
  # confirm got past every check because it WAS dispatched at the tip).
  mkdir -p "$W/o/b/c" && cp "$ROOT/tools/audit/seat/bus.sh" "$W/o/b/c/bus.sh"
  N4=$(run dispatch 24 "$h1" cmsg_O | sed -n 's/^bus-nonce: //p')
  printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$h1" "$N4" > "$W/oo.md"
  seat push-verdict 24 "$W/oo.md" "$W/ev1" >/dev/null
  ro=$(tip review/24)
  n0=$(calls)
  out=$( (cd "$W/seat" && HPO_BUS_STATE=$W/state HPO_IDENTITY_DIR=$W/ap \
          bash "$W/o/b/c/bus.sh" confirm 24 "$ro") 2>&1 ); rc=$?
  [ $rc != 0 ] && echo "$out" | grep -q "no executable poster" \
    && ! git -C "$W/seat" ls-remote --exit-code origin refs/heads/verdict/24 >/dev/null 2>&1 \
    && [ "$(calls)" = "$n0" ]
  expect "a copy outside a checkout refuses before it pushes the verdict ref" $?

  [ -n "${BUS_KEEP:-}" ] && echo "kept $W" || rm -rf "$W"
  printf 'bus self-test: %s checks, %s failed\n' "$((pass + fail))" "$fail"
  [ "$fail" = 0 ]
}

case ${1:-} in
  push-verdict) shift; push_verdict "$@" ;;
  watch) shift; watch "$@" ;;
  dispatch) shift; dispatch "$@" ;;
  confirm) shift; confirm "$@" ;;
  post) shift; numeric "${1:-}" || die "post: give a pull-request number"; mkdir -p "$S"; post_verdict "$1" ;;
  --self-test) self_test ;;
  *) sed -n '2,8p' "$0" >&2; exit 2 ;;
esac
