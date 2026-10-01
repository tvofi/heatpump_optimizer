#!/bin/bash
# bus.sh -- git refs as the programme's message bus (round-9 process review
# item 9, adopted by tvofi 2026-10-01). Seats publish on refs; the orchestrator
# watches them; the coordinator is left to start seats and handle blocks.
#
#   bus.sh push-verdict <pr> <VERDICT.md> [<evidence dir>]     (reviewer)
#   bus.sh watch [--once] [--post] [--every <seconds>]          (orchestrator)
#   bus.sh dispatch <pr> <head> <reviewer>                      (dispatching role)
#   bus.sh confirm <pr> <verdict commit>                        (dispatching role)
#   bus.sh post <pr>                                            (orchestrator)
#   bus.sh --self-test
#
# THE REFS. `handoff/<topic>` is a fixer's code head; `handoff-body/<topic>` its
# body (`body_push.sh`); `verdict/<pr>` a reviewer's verdicts. A verdict ref is
# append-only like a body ref: each push adds one commit whose tree is
# VERDICT.md plus the evidence directory under `evidence/`, its parent the
# previous tip, so a later round never needs a force-push. A crossed-out
# verdict stays in the ref's history; only the tip is posted.
#
# push-verdict REFUSES, AND PUSHES NOTHING, unless the first line is in
# `fix-review.md`'s grammar (the regex is `app_comment.sh`'s) and a file under
# the evidence directory names the verdict's 40-hex head. VERDICT.md alone
# does not count: it names the sha by construction, and `app_approve.sh`'s
# evidence gate exists to make a forged verdict forge artifacts too.
#
# watch lists the three ref families on the remote and prints one line per
# ref that appeared, moved or went since the last pass:
#   BUS handoff|body|verdict <name> <sha>|gone
# It records the pass in $HPO_BUS_STATE/refs (default ~/.zcode/bus), so each
# change is reported once. A first pass with no state records a baseline and
# reports nothing. Without --once it polls every --every seconds (default 60)
# and EXITS on the first pass that reports anything: run it as a background
# task and its exit wakes you (process review item 4), never a timer.
#
# --post, and `post <pr>`, post a verdict ref's tip as `hpo-approver` through
# `app_comment.sh` (decision 0013), which keeps every refusal it has: the
# grammar, an open pull request, a `merge` verdict at exactly the live head,
# and the byte-identical read-back. Before that, the tip's tree is unpacked to
# $HPO_BUS_STATE/verdicts/<pr>/<commit>/, and the posted body is VERDICT.md
# followed by one line naming the ref, the commit and that directory's
# `evidence/` -- a directory on THIS machine holding a file that names the
# head, which is what `app_approve.sh`'s evidence gate reads. A commit is
# posted at most once ($HPO_BUS_STATE/posted); a refused one is reported
# `BUS refused` and not retried by watch, so it cannot wake you every pass --
# `post <pr>` retries it by hand.
#
# THE REF IS NOT THE REVIEWER. Every cloud seat pushes with one credential, so
# a hand-made `verdict/<pr>` with a well-formed line and evidence is as easy
# for a fixer as for its reviewer (PROC-4's round-1 review drove exactly that
# to a post). Two records gate a post, both kept by whichever role dispatched
# the reviewer -- the coordinator where there is one, else the orchestrator --
# in $HPO_BUS_STATE on the machine that posts:
#   - `dispatch` when the reviewer starts: PR, head and reviewer (its thread or
#     session id), and a fresh nonce it prints for the reviewer's brief. The
#     verdict must carry `bus-nonce: <nonce>`, and a nonce binds only the PR
#     and head it was minted for.
#   - `confirm`, after the dispatcher has read that reviewer's OWN thread or
#     session output and found this verdict commit there.
# Without both it fails closed: `BUS undispatched` or `BUS unconfirmed`. WHAT
# THIS PROVES: the nonce ties a verdict to a dispatch, not to a seat -- a
# brief is readable project-wide, so any seat that reads the reviewer's
# thread can copy it; it stops a verdict for an undispatched PR, a stale head
# or a guessed nonce. Authorship rests on `confirm`, the dispatcher reading
# the reviewer's own output, as the relay did before the bus. No design
# without a confirming role is sound here: with one push credential and
# project-readable briefs, every secret a reviewer could sign with is
# readable by the seat it reviews.
#
# Environment: HPO_BUS_REMOTE (origin), HPO_BUS_REPO (tvofi/heatpump_optimizer),
# HPO_BUS_POSTER (this checkout's tools/audit/app_comment.sh).
# Plain variables, no arrays: macOS /bin/bash 3.2 rejects an empty array under -u.
set -uo pipefail

ROOT=$(cd "$(dirname -- "$0")/../../.." && pwd)
REMOTE=${HPO_BUS_REMOTE:-origin}
REPO=${HPO_BUS_REPO:-tvofi/heatpump_optimizer}
POSTER=${HPO_BUS_POSTER:-$ROOT/tools/audit/app_comment.sh}
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

push_verdict() { # pr verdict-file [evidence-dir]
  local pr=${1:-} v=${2:-} ev=${3:-} first hsha t gd tree parent c
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
  parent=""
  if git ls-remote --exit-code -q "$REMOTE" "refs/heads/verdict/$pr" >/dev/null 2>&1; then
    git fetch -q "$REMOTE" "refs/heads/verdict/$pr" || die "push-verdict: could not fetch verdict/$pr"
    parent="-p $(git rev-parse FETCH_HEAD)"
  fi
  # shellcheck disable=SC2086 # $parent is empty or exactly "-p <sha>"
  c=$(git commit-tree "$tree" $parent -m "verdict: #$pr $first") || die "push-verdict: commit-tree failed"
  git push -q "$REMOTE" "$c:refs/heads/verdict/$pr" || die "push-verdict: the push of verdict/$pr was refused"
  printf 'verdict/%s %s\n' "$pr" "$c"
}

snapshot() { # -> "<name> <sha>" for every bus ref on the remote, sorted
  git ls-remote --heads "$REMOTE" | awk '
    { r = $2; sub(/^refs\/heads\//, "", r) }
    r ~ /^(handoff|handoff-body|verdict)\// { print r, $1 }' | LC_ALL=C sort
}

kind_of() { # ref name -> "<kind> <name>"
  case $1 in
    handoff-body/*) printf 'body %s\n' "${1#handoff-body/}" ;;
    handoff/*) printf 'handoff %s\n' "${1#handoff/}" ;;
    verdict/*) printf 'verdict %s\n' "${1#verdict/}" ;;
  esac
}

post_verdict() { # pr [expected sha] -> prints one BUS posted|refused line; rc 0 posted
  local pr=$1 want=${2:-} c d first hsha body why thread nonce
  numeric "$pr" || { printf 'BUS refused %s: verdict/%s is not a pull-request number\n' "$pr" "$pr"; return 1; }
  if ! git fetch -q "$REMOTE" "+refs/heads/verdict/$pr:refs/hpo-bus/verdict/$pr" 2>/dev/null; then
    printf 'BUS refused %s: could not fetch verdict/%s\n' "$pr" "$pr"; return 1
  fi
  c=$(git rev-parse "refs/hpo-bus/verdict/$pr")
  if [ -n "$want" ] && [ "$c" != "$want" ]; then
    printf 'BUS refused %s %s: the tip of verdict/%s is %s; only a tip posts\n' "$pr" "$want" "$pr" "$c"; return 1
  fi
  if grep -qx "$pr $c" "$S/posted" 2>/dev/null; then
    printf 'BUS refused %s %s: already posted\n' "$pr" "$c"; return 1
  fi
  d=$S/verdicts/$pr/$c
  rm -rf "$d" && mkdir -p "$d" && git archive "$c" | tar -x -C "$d" \
    || { printf 'BUS refused %s %s: could not unpack the verdict tree\n' "$pr" "$c"; return 1; }
  why=""
  if [ ! -f "$d/VERDICT.md" ]; then why="the tree has no VERDICT.md"
  else
    first=$(head -n 1 "$d/VERDICT.md")
    if ! hsha=$(verdict_sha "$first"); then why="the first line is outside fix-review.md's grammar: '$first'"
    elif ! grep -rqF -- "$hsha" "$d/evidence" 2>/dev/null; then why="no file under evidence/ names the head $hsha"
    fi
  fi
  [ -z "$why" ] || { printf 'BUS refused %s %s: %s\n' "$pr" "$c" "$why"; return 1; }
  # The ref proves no reviewer (the header): a dispatch record for this pr,
  # head and nonce, then the dispatcher's confirmation of this commit.
  nonce=$(verdict_nonce "$d/VERDICT.md")
  thread=$(awk -v k="$pr $hsha " -v n="$nonce" 'index($0, k) == 1 && n != "" && $4 == n { print $3; exit }' "$S/dispatched" 2>/dev/null)
  if [ -z "$thread" ]; then
    printf 'BUS undispatched %s %s: no dispatch record for #%s at %s with this verdict'"'"'s nonce\n' "$pr" "$c" "$pr" "$hsha"; return 1
  fi
  if ! grep -qx "$pr $c" "$S/confirmed" 2>/dev/null; then
    printf 'BUS unconfirmed %s %s: read %s'"'"'s own output for this commit, then: bus.sh confirm %s %s\n' \
      "$pr" "$c" "$thread" "$pr" "$c"; return 1
  fi
  body=$S/verdicts/$pr/$c.md
  { cat "$d/VERDICT.md"
    printf '\nbus: verdict/%s at %s, dispatched to and confirmed from %s; evidence: %s/evidence\n' "$pr" "$c" "$thread" "$d"
  } > "$body"
  # Recorded BEFORE the post and withdrawn on a refusal: a kill between a
  # landed post and the record would otherwise post twice. A kill now leaves
  # "already posted" on a verdict that may not have landed; read the PR.
  printf '%s %s\n' "$pr" "$c" >> "$S/posted"
  if ! "$POSTER" "$REPO" "$pr" "$body" >"$body.log" 2>&1; then
    grep -vx "$pr $c" "$S/posted" > "$S/posted.new"; mv "$S/posted.new" "$S/posted"
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

confirm() { # pr verdict-commit -> records the dispatcher's read of the reviewer's output, then posts
  local pr=${1:-} c=${2:-}
  numeric "$pr" || die "confirm: the pull request '$pr' is not a number"
  [[ $c =~ ^[0-9a-f]{40}$ ]] || die "confirm: '$c' is not a 40-hex verdict commit"
  mkdir -p "$S" && printf '%s %s\n' "$pr" "$c" >> "$S/confirmed" || die "confirm: cannot record in $S"
  post_verdict "$pr" "$c"
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
    if [ "$post" = 1 ] && [ "$kind" = verdict ] && [ "$sha" != gone ]; then
      post_verdict "${line#* }" "$sha" </dev/null
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
  local W pass=0 fail=0 out rc h1 h2 c1 c2 c9 ca cs t ev forged N0 N1 N1b N2 N9
  W=$(mktemp -d) || { echo "self-test: no temporary directory"; return 1; }
  ok() { pass=$((pass + 1)); printf '  ok   %s\n' "$1"; }
  bad() { fail=$((fail + 1)); printf '  FAIL %s\n' "$1"; }
  expect() { # name condition-rc
    if [ "$2" = 0 ]; then ok "$1"; else bad "$1"; fi
  }
  # Hermetic: no global or system git config (identity, hooks, push negotiation).
  export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=$W/gitconfig
  git config --file "$W/gitconfig" user.name t && git config --file "$W/gitconfig" user.email t@t
  git init -q --bare "$W/origin.git"
  git init -q "$W/seat" && git -C "$W/seat" remote add origin "$W/origin.git"
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
  run() { (cd "$W/seat" && HPO_BUS_STATE=$W/state HPO_BUS_POSTER=$W/poster HPO_BUS_REPO=o/r \
           bash "$ROOT/tools/audit/seat/bus.sh" "$@") 2>&1; }
  calls() { grep -c . "$W/calls"; }

  out=$(run push-verdict 7 "$W/badgrammar.md" "$W/ev1"); rc=$?
  [ $rc != 0 ] && echo "$out" | grep -q "outside fix-review.md's grammar"; expect "push-verdict refuses a first line outside the grammar" $?
  out=$(run push-verdict 7 "$W/nononce.md" "$W/ev1"); rc=$?
  [ $rc != 0 ] && echo "$out" | grep -q "no 'bus-nonce"; expect "push-verdict refuses a verdict with no nonce line" $?
  out=$(run push-verdict 7 "$W/merge0.md" "$W/evnone"); rc=$?
  [ $rc != 0 ] && echo "$out" | grep -q "names the head $h1"; expect "push-verdict refuses evidence that names no head" $?
  out=$(run push-verdict 7 "$W/merge0.md"); rc=$?
  [ $rc != 0 ] && echo "$out" | grep -q "no evidence directory"; expect "push-verdict refuses a verdict with no evidence directory" $?
  out=$(run push-verdict 7x "$W/merge0.md" "$W/ev1"); rc=$?
  [ $rc != 0 ] && echo "$out" | grep -q "not a number"; expect "push-verdict refuses a non-numeric pull request" $?
  git -C "$W/seat" ls-remote --exit-code origin refs/heads/verdict/7 >/dev/null 2>&1
  [ $? = 2 ]; expect "no refused push left a verdict ref" $?

  out=$(run watch --once --post); rc=$?
  [ $rc = 0 ] && echo "$out" | grep -q "baseline of 0 ref" && [ "$(calls)" = 0 ]
  expect "a first pass records a baseline and posts nothing" $?

  # The forgery PROC-4's round-1 review drove: any seat can push a well-formed
  # verdict with evidence by hand, so the ref alone must never post.
  out=$(run push-verdict 11 "$W/merge0.md" "$W/ev1")
  forged=$(git -C "$W/origin.git" rev-parse verdict/11)
  out=$(run watch --once --post)
  echo "$out" | grep -q "^BUS undispatched 11 $forged" && [ "$(calls)" = 0 ]
  expect "watch --post does not post a forged verdict ref no one dispatched" $?
  out=$(run confirm 11 "$forged")
  echo "$out" | grep -q "^BUS undispatched 11 $forged" && [ "$(calls)" = 0 ]
  expect "a confirmation cannot stand in for a dispatch record" $?

  N1=$(run dispatch 7 "$h1" cmsg_R | sed -n 's/^bus-nonce: //p')
  [[ $N1 =~ ^[0-9a-f]{32}$ ]] && grep -qx "7 $h1 cmsg_R $N1" "$W/state/dispatched"
  expect "dispatch records pr, head and reviewer and prints a fresh nonce" $?
  N1b=$(run dispatch 12 "$h1" cmsg_Q | sed -n 's/^bus-nonce: //p')
  [ "$N1" != "$N1b" ]; expect "two dispatches mint two nonces" $?
  printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$h1" "$N1" > "$W/merge.md"
  printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$h1" "$N1b" > "$W/othernonce.md"
  out=$(run push-verdict 7 "$W/othernonce.md" "$W/ev1")
  ca=$(git -C "$W/origin.git" rev-parse verdict/7)
  out=$(run watch --once --post)
  echo "$out" | grep -q "^BUS undispatched 7 $ca" && [ "$(calls)" = 0 ]
  expect "another dispatch's nonce does not post" $?

  git -C "$W/seat" push -q origin HEAD:refs/heads/handoff/t1
  out=$(run push-verdict 7 "$W/merge.md" "$W/ev1"); rc=$?
  [ $rc = 0 ]; expect "push-verdict publishes a verdict with nonce and evidence" $?
  c1=$(git -C "$W/seat" ls-remote origin refs/heads/verdict/7 | cut -f1)
  out=$(run watch --once --post); rc=$?
  echo "$out" | grep -qx "BUS handoff t1 $(git -C "$W/seat" rev-parse HEAD)"; expect "watch reports a new handoff ref" $?
  echo "$out" | grep -qx "BUS verdict 7 $c1"; expect "watch reports a new verdict ref" $?
  echo "$out" | grep -q "^BUS unconfirmed 7 $c1: read cmsg_R's own output .*bus.sh confirm 7 $c1" && [ "$(calls)" = 0 ]
  expect "a dispatched verdict waits for the dispatcher's confirmation, naming the reviewer" $?
  out=$(run confirm 7 "$ca")
  echo "$out" | grep -q "^BUS refused 7 $ca: the tip of verdict/7 is $c1" && [ "$(calls)" = 0 ]
  expect "a confirmation for a commit that is not the tip posts nothing" $?
  out=$(run confirm 7 "$c1")
  echo "$out" | grep -q "^BUS posted 7 $c1 Fix review: merge $h1" && [ "$(calls)" = 1 ]; expect "confirm posts the verdict once" $?
  grep -q "^bus: verdict/7 at $c1, dispatched to and confirmed from cmsg_R;" "$W/last"; expect "the posted body names the reviewer" $?
  [ "$(head -n 1 "$W/last")" = "Fix review: merge $h1" ]; expect "the posted body keeps the reviewer's first line" $?
  ev=$(sed -n 's/^bus: .*; evidence: //p' "$W/last")
  case $ev in /*) [ -d "$ev" ] && grep -rqF "$h1" "$ev" ;; *) false ;; esac
  expect "the posted body cites an absolute evidence directory that names the head" $?
  grep -q "^o/r 7 " "$W/calls"; expect "the poster is called with the repository and pull request" $?
  out=$(run watch --once --post); rc=$?
  [ $rc = 0 ] && [ -z "$out" ] && [ "$(calls)" = 1 ]; expect "an unchanged pass reports and posts nothing" $?
  out=$(run post 7); rc=$?
  [ $rc != 0 ] && echo "$out" | grep -q "already posted" && [ "$(calls)" = 1 ]; expect "post refuses a commit already posted" $?

  # Round 2 at a new head: a fresh dispatch; round 1's nonce no longer binds.
  printf 'Fix review: blocked %s harness: class-open x\n\nbus-nonce: %s\n' "$h2" "$N1" > "$W/stale.md"
  out=$(run push-verdict 7 "$W/stale.md" "$W/ev2")
  cs=$(git -C "$W/origin.git" rev-parse verdict/7)
  out=$(run watch --once --post)
  echo "$out" | grep -q "^BUS undispatched 7 $cs" && [ "$(calls)" = 1 ]; expect "round 1's nonce does not post a verdict at another head" $?
  N2=$(run dispatch 7 "$h2" cmsg_R | sed -n 's/^bus-nonce: //p')
  printf 'Fix review: blocked %s harness: class-open x\n\nbus-nonce: %s\n' "$h2" "$N2" > "$W/blocked.md"
  out=$(run push-verdict 7 "$W/blocked.md" "$W/ev2"); rc=$?
  c2=$(git -C "$W/origin.git" rev-parse verdict/7)
  [ $rc = 0 ] && [ "$(git -C "$W/origin.git" rev-parse verdict/7^)" = "$cs" ]
  expect "a later round fast-forwards the verdict ref" $?
  out=$(run watch --once --post)
  echo "$out" | grep -q "^BUS unconfirmed 7 $c2" && [ "$(calls)" = 1 ]; expect "the second round waits for its own confirmation" $?
  out=$(run confirm 7 "$c2")
  echo "$out" | grep -q "^BUS posted 7 $c2 Fix review: blocked $h2" && [ "$(calls)" = 2 ]; expect "the second round is posted" $?

  # A ref written without push-verdict is still checked before it is posted.
  t=$(printf 'Fix review: approve %s\n' "$h1" | git -C "$W/seat" hash-object -w --stdin)
  t=$(printf '100644 blob %s\tVERDICT.md\n' "$t" | git -C "$W/seat" mktree)
  t=$(git -C "$W/seat" commit-tree "$t" -m raw)
  git -C "$W/seat" push -q origin "$t:refs/heads/verdict/8"
  out=$(run watch --once --post)
  echo "$out" | grep -q "^BUS refused 8 $t: the first line is outside" && [ "$(calls)" = 2 ]
  expect "watch refuses a raw ref outside the grammar and posts nothing" $?
  out=$(run watch --once --post)
  [ -z "$out" ]; expect "a refused verdict is not retried on the next pass" $?
  t=$(printf 'Fix review: merge %s\n' "$h1" | git -C "$W/seat" hash-object -w --stdin)
  t=$(printf '100644 blob %s\tVERDICT.md\n' "$t" | git -C "$W/seat" mktree)
  t=$(git -C "$W/seat" commit-tree "$t" -m raw)
  git -C "$W/seat" push -q origin "$t:refs/heads/verdict/10"
  out=$(run watch --once --post)
  echo "$out" | grep -q "^BUS refused 10 $t: no file under evidence/ names the head" && [ "$(calls)" = 2 ]
  expect "watch refuses a raw ref whose only naming file is VERDICT.md" $?

  N9=$(run dispatch 9 "$h1" cmsg_S | sed -n 's/^bus-nonce: //p')
  printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$h1" "$N9" > "$W/merge9.md"
  out=$(run push-verdict 9 "$W/merge9.md" "$W/ev1")
  c9=$(git -C "$W/origin.git" rev-parse verdict/9)
  out=$(BUS_TEST_POSTER_FAIL=1 run confirm 9 "$c9")
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
  out=$(timeout 3 bash -c "cd '$W/seat' && HPO_BUS_STATE='$W/state' bash '$ROOT/tools/audit/seat/bus.sh' watch --every 1" 2>&1); rc=$?
  [ $rc = 124 ] && [ -z "$out" ]; expect "watch without --once keeps waiting while nothing changes" $?

  rm -rf "$W"
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
