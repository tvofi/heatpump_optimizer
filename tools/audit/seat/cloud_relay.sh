#!/bin/bash
# cloud_relay.sh [--confirm] [--log FILE] <pr> <nonce> <head40>    relay one cloud reviewer's verdict
# cloud_relay.sh --watch [--interval N] [--once] [--confirm] [--log FILE]
# cloud_relay.sh pass [--confirm] [--log FILE] [--loop [--interval N]]
# cloud_relay.sh dispose <ref> <sha40>                                record an OWED ref handled
# cloud_relay.sh held <pr>                                           rc 0 held, 1 not held, 2 malformed hold file
# cloud_relay.sh --self-test
#
# WHY. A cloud reviewer cannot run `bus.sh push-verdict`: the dispatch record
# `push-verdict` checks lives on the orchestrator's machine, so it refuses
# "unknown nonce" there. The cloud reviewer instead commits verdict.md (first
# line in fix-review.md's grammar, then a blank line and `bus-nonce: <nonce>`)
# plus ev/ to a fresh repository and pushes it to
# refs/heads/probe/rev-<pr>-<nonce first 8>; this script, run by the
# orchestrator where the record is, fetches that ref, grades it, and runs
# `bus.sh push-verdict` locally. `bus.sh confirm` follows, as for any verdict.
#
# REFUSES (exit 2, push-verdict not run):
#   * a head that is not 40 lowercase hex, or a nonce that is not 32 hex;
#   * no probe ref for <pr> and <nonce>;
#   * a verdict whose `bus-nonce:` line is not exactly <nonce>;
#   * a verdict whose first line names a head other than <head40>;
#   * a ref whose commit subject (`verdict <pr> <head>`) names another PR or
#     head than the arguments (a verdict relayed onto the wrong PR);
#   * a ref already relayed: the ledger keys on `<ref> <sha>`, so a second
#     relay of the same push is refused and a re-pushed ref relays again.
# NORMALISES one thing, and says so. A reviewer that read the old brief wraps a
# blocked verdict's tail in brackets: `Fix review: blocked <head> [class: reason]`.
# bus.sh's grammar is `blocked <head> <class>: <reason>` (class `[a-z-]+`), and
# dropping exactly the one outer bracket pair loses nothing, so the relay rewrites
# the first line in its temp copy and prints `normalised first line: A -> B`.
# Anything else (a bracketed merge suffix, unbalanced brackets, a bracketed
# tail whose class is not `[a-z-]+: <reason>`) is refused unchanged: dropping a
# suffix from a merge would be lossy, and push-verdict's own refusal names the rest.
#
# --watch is the orchestrator's poll loop: every N seconds (default 120) it runs
# the probe arm, `git ls-remote origin 'refs/heads/probe/*'`. A ref that is not
# probe/rev-* appends `OWED <utc> probe-ref <ref> <sha>` on EVERY pass until
# `dispose <ref> <sha>` writes `<ref> <sha>` to <state>/cloud-disposed: a level,
# not a diff, so a missed line is repeated rather than lost, and a disposed ref
# that moves is owed again. It relays each probe/rev-* ref+sha once.
# The dispatch record ($HPO_BUS_STATE or ~/.zcode/bus, field order `pr head
# thread nonce`) supplies the head and full nonce for a ref's pr and nonce8; a ref
# with no record is logged and left for a later pass. A refused ref+sha is noted
# in `<ledger>.refused` and not retried, so a loop does not repeat one refusal
# every interval; a re-pushed ref has a new sha and is tried again. --once makes
# one pass (the self-test's and cron's shape). Run it detached via daemonize.py.
#
# --confirm does not stop at push-verdict (two verdicts once sat relayed and
# unposted for 20 minutes): after a push-verdict that PASSED it runs
# `bus.sh confirm <pr> <review-sha>`, the sha being the one push-verdict printed
# (`review/<pr> <sha>`), and appends one line to the log (--log FILE, default
# <state>/cloud-relay.log, which the orchestrator reads):
#   POSTED <utc> <pr> <review-sha>          confirm succeeded
#   OWED   <utc> <pr> <review-sha|-> <why>  push-verdict passed, the verdict is not posted
# confirm never runs after a refused relay or a failed push-verdict, and writes
# nothing for them (a refusal prints its reason, and --watch's .refused file
# holds it). HPO_RELAY_CONFIRM replaces the confirm command (the self-test's stub).
#
# `pass` is the orchestrator's whole beat, ONE entry point a driver calls once
# (and takes over relay_watch.sh, which was session-local). A pass runs two arms.
#   handoff arm: for every OPEN pull request, topic = headRefName less a leading
#     `fix/` and a trailing `-pr`. If handoff-body/<topic> and handoff/<topic>
#     exist and handoff/<topic> is NOT an ancestor of the PR head, it runs
#     update_pr.sh <branch> <code-sha> <body> <issues> (issues = the body's
#     closing keywords), then approve_held_runs.sh on the branch, then
#     `bus.sh dispatch <pr> <new head> cloud`, and appends
#       OWED reviewer-fire <pr> <head40> <nonce> <utc>
#     to the log: firing the cloud reviewer stays with the orchestrator. It only
#     UPDATES an existing PR (the soft cap counts roster groups in progress at
#     dispatch; an update neither opens a PR nor enters WIP).
#     A handoff already contained in its PR, or with no body ref, does nothing;
#     a topic whose update failed is noted in `<ledger>.handoff-failed` by
#     `<topic> <code-sha>` and retried only when handoff/<topic> moves, with an
#     `OWED handoff-update` line. Every handoff/* or handoff-body/* ref whose
#     topic has no open PR appends `OWED <utc> handoff-no-pr <ref> <sha>` on
#     every pass until disposed; a failed PR listing reports none.
#     HOLD. `<state>/cloud-handoff-hold` lists PR numbers, one per line (blank
#     lines and `#` lines allowed); only the orchestrator writes or edits it.
#     A listed PR whose handoff is ahead is NOT updated and prints
#       cloud_relay: HELD #<pr> <handoff tip>
#     once per pass; removing the number resumes it. A missing or empty file
#     holds nothing. A line that is not a plain PR number (or a file that is
#     not readable) refuses the whole handoff arm that pass (rc 2, an OWED
#     `handoff-hold-malformed` line): never hold-all, never hold-none.
#     `held <pr>` answers from the same file, for a driver that updates PRs
#     itself (the beat's handoff job reads it unchanged).
#   probe arm: the --watch pass above (probe/rev-* -> relay -> confirm; other
#     probe refs OWED until disposed).
# `--loop` repeats a pass every --interval seconds (default 120); without it a
# pass runs once. HPO_RELAY_PRS, HPO_RELAY_UPDATE, HPO_RELAY_APPROVE and
# HPO_RELAY_DISPATCH replace the PR lister (tab lines `number branch head`),
# update_pr.sh, approve_held_runs.sh and bus.sh dispatch: the self-test's stubs.
#
# The ledger is ${HPO_STATE_DIR:-$HOME/.local/state/hpo}/cloud-relayed and is
# written only after push-verdict succeeded. HPO_RELAY_PUSH replaces the
# push-verdict command (the self-test's stub; it takes <pr> <verdict> <ev>).
set -uo pipefail
HERE=$(cd "$(dirname -- "$0")" && pwd)

die() { echo "cloud_relay: refused: $*" >&2; return 2; }

logline() { mkdir -p "$(dirname -- "${LOG:-${HPO_STATE_DIR:-$HOME/.local/state/hpo}/cloud-relay.log}")" && printf '%s %s\n' "$1" "$(date -u +%FT%TZ) $2" >> "${LOG:-${HPO_STATE_DIR:-$HOME/.local/state/hpo}/cloud-relay.log}"; }
posted() { logline POSTED "$1 $2"; echo "cloud_relay: POSTED #$1 $2"; }
owed() { logline OWED "$1 $2 $3"; echo "cloud_relay: OWED #$1: $3" >&2; }

relay() {
  local pr=$1 nonce=$2 head=$3 ref sha d subj first state led
  case $pr in ''|*[!0-9]*) die "pr '$pr' is not a number"; return;; esac
  printf '%s' "$head" | grep -Eq '^[0-9a-f]{40}$' || { die "head must be 40 lowercase hex"; return; }
  printf '%s' "$nonce" | grep -Eq '^[0-9a-f]{32}$' || { die "nonce must be 32 hex"; return; }
  ref=refs/heads/probe/rev-$pr-$(printf '%s' "$nonce" | cut -c1-8)
  sha=$(git ls-remote origin "$ref" | awk 'NF { print $1; exit }')
  [ -n "$sha" ] || { die "no $ref on origin"; return; }
  state=${HPO_STATE_DIR:-$HOME/.local/state/hpo}; led=$state/cloud-relayed
  if [ -f "$led" ] && grep -qxF "$ref $sha" "$led"; then die "$ref at $sha was already relayed"; return; fi
  git fetch -q origin "$ref" || { die "could not fetch $ref"; return; }
  d=$(mktemp -d "${TMPDIR:-/tmp}/cloud_relay.XXXXXX") || return 1
  git archive "$sha" | tar -x -C "$d" || { die "could not read $sha"; return; }
  subj=$(git log -1 --format=%s "$sha")
  [ "$subj" = "verdict $pr $head" ] || { die "the ref's commit says '$subj', not 'verdict $pr $head': another PR or head"; return; }
  [ -f "$d/verdict.md" ] || { die "no verdict.md in the ref"; return; }
  first=$(head -n 1 "$d/verdict.md")
  if [[ $first =~ ^(Fix\ review:\ blocked\ [0-9a-f]{40})\ \[([a-z-]+:\ [^][]+)\]$ ]]; then
    local fixed="${BASH_REMATCH[1]} ${BASH_REMATCH[2]}"
    { printf '%s\n' "$fixed"; tail -n +2 "$d/verdict.md"; } > "$d/verdict.new" && mv "$d/verdict.new" "$d/verdict.md"
    echo "cloud_relay: normalised first line: $first -> $fixed"
    first=$fixed
  fi
  # bus.sh's grammar (verdict_sha): merge has no tail; blocked has `<class>: <reason>`.
  if [ "$first" = "Fix review: merge $head" ]; then :
  elif [[ $first == "Fix review: blocked $head "* ]] && [[ ${first#"Fix review: blocked $head "} =~ ^[a-z-]+:\ .+$ ]]; then :
  else die "the first line is not 'Fix review: merge $head' or 'Fix review: blocked $head <class>: <reason>': '$first'"; return; fi
  grep -qx "bus-nonce: $nonce" "$d/verdict.md" || { die "nonce mismatch: no 'bus-nonce: $nonce' line"; return; }
  [ -d "$d/ev" ] || { die "no ev/ directory in the ref"; return; }
  local out sha2
  if [ -n "${HPO_RELAY_PUSH:-}" ]; then out=$("$HPO_RELAY_PUSH" "$pr" "$d/verdict.md" "$d/ev") || { printf '%s\n' "$out"; return 1; }
  else out=$(bash "$HERE/bus.sh" push-verdict "$pr" "$d/verdict.md" "$d/ev") || { printf '%s\n' "$out"; return 1; }; fi
  printf '%s\n' "$out"
  mkdir -p "$state" && echo "$ref $sha" >> "$led"
  if [ -n "${CONFIRM:-}" ]; then
    sha2=$(printf '%s\n' "$out" | tail -n 1 | awk '{ print $NF }')
    if ! printf '%s' "$sha2" | grep -Eq '^[0-9a-f]{40}$'; then owed "$pr" - "push-verdict printed no 40-hex review commit"
    elif [ -n "${HPO_RELAY_CONFIRM:-}" ]; then
      "$HPO_RELAY_CONFIRM" "$pr" "$sha2" >/dev/null 2>&1 && posted "$pr" "$sha2" || owed "$pr" "$sha2" "confirm failed"
    else bash "$HERE/bus.sh" confirm "$pr" "$sha2" >/dev/null 2>&1 && posted "$pr" "$sha2" || owed "$pr" "$sha2" "bus.sh confirm failed; run it by hand"; fi
  fi
  echo "cloud_relay: relayed $ref $sha; next: bus.sh confirm $pr <review commit>"
}

disposed() { # disposed <ref> <sha>: the orchestrator ran `dispose` on this ref at this sha
  local f=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/cloud-disposed; [ -f "$f" ] && grep -qxF "$1 $2" "$f"; }

dispose() { # dispose <ref> <sha>: a probe or handoff ref at that sha is handled; it is OWED again once it moves
  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo}
  [ $# = 2 ] || { echo "usage: cloud_relay.sh dispose <ref> <sha40>" >&2; return 2; }
  case $1 in refs/heads/probe/?*|refs/heads/handoff/?*|refs/heads/handoff-body/?*) ;; *) die "'$1' is not a refs/heads/probe/, handoff/ or handoff-body/ ref"; return;; esac
  printf '%s' "$2" | grep -Eq '^[0-9a-f]{40}$' || { die "sha must be 40 lowercase hex"; return; }
  mkdir -p "$state" && echo "$1 $2" >> "$state/cloud-disposed" && echo "cloud_relay: disposed $1 $2"
}

probe_arm() { # one pass over every probe/* ref: rev-* relays each unseen ref+sha, any other is OWED until disposed
  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} led bus sha ref k pr n8 rec nonce head rc
  led=$state/cloud-relayed; bus=${HPO_BUS_STATE:-$HOME/.zcode/bus}
  git ls-remote origin 'refs/heads/probe/*' > "${TMPDIR:-/tmp}/cloud_relay_ls.$$" || { echo "cloud_relay: ls-remote failed; will retry" >&2; rm -f "${TMPDIR:-/tmp}/cloud_relay_ls.$$"; return 0; }
  while read -r sha ref; do
    [ -n "$ref" ] || continue
    case $ref in refs/heads/probe/rev-*) ;;
      *) disposed "$ref" "$sha" || { logline OWED "probe-ref $ref $sha"; echo "cloud_relay: OWED probe-ref $ref $sha"; }; continue;; esac
    if { [ -f "$led" ] && grep -qxF "$ref $sha" "$led"; } || { [ -f "$led.refused" ] && grep -qxF "$ref $sha" "$led.refused"; }; then continue; fi
    k=${ref#refs/heads/probe/rev-}; pr=${k%%-*}; n8=${k#*-}
    rec=$(awk -v p="$pr" -v n="$n8" '$1 == p && index($4, n) == 1 { print $2, $4 }' "$bus/dispatched" 2>/dev/null | tail -n 1)
    if [ -z "$rec" ]; then echo "$(date -u +%FT%TZ) cloud_relay: $ref $sha has no dispatch record in $bus; leaving it" >&2; continue; fi
    head=${rec%% *}; nonce=${rec#* }
    echo "$(date -u +%FT%TZ) cloud_relay: relaying $ref $sha"
    relay "$pr" "$nonce" "$head"; rc=$?
    if [ $rc -ne 0 ]; then mkdir -p "$state" && echo "$ref $sha" >> "$led.refused"; fi
  done < "${TMPDIR:-/tmp}/cloud_relay_ls.$$"
  rm -f "${TMPDIR:-/tmp}/cloud_relay_ls.$$"
}

watch() { # [--interval N] [--once]
  local every=120 once=""
  while [ $# -gt 0 ]; do case $1 in
    --interval) every=${2:-}; shift 2;; --once) once=1; shift;; --confirm) CONFIRM=1; shift;; --log) LOG=${2:-}; shift 2;; *) echo "cloud_relay: unknown watch option '$1'" >&2; return 2;; esac; done
  case $every in ''|*[!0-9]*|0) echo "cloud_relay: --interval must be a positive number of seconds" >&2; return 2;; esac
  while :; do probe_arm; [ -n "$once" ] && return 0; sleep "$every"; done
}

hold_file() { echo "${HPO_STATE_DIR:-$HOME/.local/state/hpo}/cloud-handoff-hold"; }
hold_list() { # the held PR numbers, one per line; rc 2 when the hold file is malformed. No file = no hold.
  local f l; f=$(hold_file); [ -e "$f" ] || return 0
  [ -f "$f" ] && [ -r "$f" ] || { echo "cloud_relay: refused: malformed hold file $f (not a readable file)" >&2; return 2; }
  while IFS= read -r l || [ -n "$l" ]; do
    case $l in ''|'#'*) ;; *[!0-9]*|0*) echo "cloud_relay: refused: malformed hold file $f: '$l' is not a PR number" >&2; return 2;; *) printf '%s\n' "$l";; esac
  done < "$f"
}
held() { # held <pr>: rc 0 listed in the hold file, 1 not listed, 2 malformed file or argument. The orchestrator writes the file.
  local l; case ${1:-} in ''|*[!0-9]*|0*) die "'${1:-}' is not a PR number"; return;; esac
  l=$(hold_list) || return 2; grep -qxF "$1" <<< "$l"; }
handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of its head
  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} repo=${HPO_RELAY_REPO:-tvofi/heatpump_optimizer} f pr br head topic hs bs bd body iss nh nonce urc held_prs
  f=$state/cloud-handoff-failed; mkdir -p "$state"
  held_prs=$(hold_list) || { logline OWED "handoff-hold-malformed $(hold_file)"; return 2; }
  { if [ -n "${HPO_RELAY_PRS:-}" ]; then "$HPO_RELAY_PRS"
    else gh pr list -R "$repo" --state open --limit 100 --json number,headRefName,headRefOid \
      -q '.[] | [.number, .headRefName, .headRefOid] | @tsv'; fi; } > "$state/cloud-prs.$$" \
    || { echo "cloud_relay: could not list open PRs; will retry" >&2; rm -f "$state/cloud-prs.$$"; return 0; }
  git ls-remote origin 'refs/heads/handoff/*' 'refs/heads/handoff-body/*' > "$state/cloud-hrefs.$$" \
    || { echo "cloud_relay: could not list handoff refs; will retry" >&2; rm -f "$state/cloud-prs.$$" "$state/cloud-hrefs.$$"; return 0; }
  while IFS=$'\t' read -r pr br head; do
    [ -n "$pr" ] || continue
    topic=${br#fix/}; topic=${topic%-pr}
    hs=$(awk -v r="refs/heads/handoff/$topic" '$2 == r { print $1; exit }' "$state/cloud-hrefs.$$")
    bs=$(awk -v r="refs/heads/handoff-body/$topic" '$2 == r { print $1; exit }' "$state/cloud-hrefs.$$")
    [ -n "$hs" ] && [ -n "$bs" ] || continue
    git fetch -q origin "refs/heads/handoff/$topic" "refs/heads/$br" 2>/dev/null
    git cat-file -e "$hs^{commit}" 2>/dev/null && git cat-file -e "$head^{commit}" 2>/dev/null || continue
    git merge-base --is-ancestor "$hs" "$head" && continue
    if grep -qxF "$pr" <<< "$held_prs"; then echo "cloud_relay: HELD #$pr $hs"; continue; fi
    if [ -f "$f" ] && grep -qxF "$topic $hs" "$f"; then continue; fi
    # The body goes in a directory of this run's own, under the state dir: a file directly in a
    # shared temp root ($TMPDIR, /tmp) is refused by prepr's body-path check, so every relay
    # update failed there (#2469, #2471) -- and still raced the manual update it was meant to spare.
    bd=$(mktemp -d "$state/cloud-body.XXXXXX") || { echo "cloud_relay: no body directory under $state" >&2; continue; }
    body=$bd/BODY.md
    git fetch -q origin "refs/heads/handoff-body/$topic" 2>/dev/null \
      && git show "$bs:BODY.md" > "$body" 2>/dev/null || { echo "cloud_relay: no BODY.md at handoff-body/$topic" >&2; rm -rf "$bd"; continue; }
    iss=$(grep -oiE '\b(close[sd]?|fix(e[sd])?|resolve[sd]?)[: ]+#[0-9]+' "$body" | grep -oE '[0-9]+' | sort -un | tr '\n' ' ')
    echo "$(date -u +%FT%TZ) cloud_relay: handoff/$topic $hs is ahead of #$pr $head; updating"
    urc=0; { if [ -n "${HPO_RELAY_UPDATE:-}" ]; then "$HPO_RELAY_UPDATE" "$br" "$hs" "$body" $iss; else bash "$HERE/update_pr.sh" "$br" "$hs" "$body" $iss; fi; } >&2 || urc=$?
    # 75 is update_pr.sh's BUSY: another run (the orchestrator's) holds this branch's worktree. Not
    # a failure, so it is not recorded and the next pass retries once that run has ended.
    if [ "$urc" = 75 ]; then echo "cloud_relay: update_pr busy on $br; the next pass retries" >&2; rm -rf "$bd"; continue; fi
    if [ "$urc" != 0 ]; then
      echo "$topic $hs" >> "$f"; logline OWED "handoff-update $pr $topic $hs"; rm -rf "$bd"; continue
    fi
    rm -rf "$bd"
    if [ -n "${HPO_RELAY_APPROVE:-}" ]; then "$HPO_RELAY_APPROVE" "$br"; else bash "$HERE/../../pr/approve_held_runs.sh" "$repo" "$br"; fi >&2 \
      || logline OWED "approve-held-runs $pr $br"
    nh=$( { if [ -n "${HPO_RELAY_PRS:-}" ]; then "$HPO_RELAY_PRS"; else gh pr list -R "$repo" --state open --limit 100 --json number,headRefName,headRefOid \
      -q '.[] | [.number, .headRefName, .headRefOid] | @tsv'; fi; } | awk -F'\t' -v p="$pr" '$1 == p { print $3; exit }')
    printf '%s' "$nh" | grep -Eq '^[0-9a-f]{40}$' || { logline OWED "dispatch $pr no new head read after the update"; continue; }
    if nonce=$( { if [ -n "${HPO_RELAY_DISPATCH:-}" ]; then "$HPO_RELAY_DISPATCH" "$pr" "$nh" cloud; else bash "$HERE/bus.sh" dispatch "$pr" "$nh" cloud; fi; } | sed -n 's/^bus-nonce: //p' | head -n 1) \
       && printf '%s' "$nonce" | grep -Eq '^[0-9a-f]{32}$'; then
      mkdir -p "$(dirname -- "${LOG:-$state/cloud-relay.log}")" && printf 'OWED reviewer-fire %s %s %s %s\n' "$pr" "$nh" "$nonce" "$(date -u +%FT%TZ)" >> "${LOG:-$state/cloud-relay.log}"
      echo "cloud_relay: OWED reviewer-fire #$pr $nh"
    else logline OWED "dispatch $pr $nh bus.sh dispatch failed; run it by hand"; fi
  done < "$state/cloud-prs.$$"
  # a handoff or handoff-body ref whose topic has no open PR is OWED on every pass until disposed
  cut -f2 "$state/cloud-prs.$$" | sed -e 's,^fix/,,' -e 's,-pr$,,' > "$state/cloud-topics.$$"
  while read -r hs ref; do
    [ -n "$ref" ] || continue
    topic=${ref#refs/heads/handoff-body/}; topic=${topic#refs/heads/handoff/}
    grep -qxF "$topic" "$state/cloud-topics.$$" && continue
    disposed "$ref" "$hs" || { logline OWED "handoff-no-pr $ref $hs"; echo "cloud_relay: OWED handoff-no-pr $ref $hs"; }
  done < "$state/cloud-hrefs.$$"
  rm -f "$state/cloud-prs.$$" "$state/cloud-hrefs.$$" "$state/cloud-topics.$$"
}

pass() { # [--confirm] [--log FILE] [--loop [--interval N]]
  local every=120 loop=""
  while [ $# -gt 0 ]; do case $1 in
    --confirm) CONFIRM=1; shift;; --log) LOG=${2:-}; shift 2;; --loop) loop=1; shift;; --interval) every=${2:-}; shift 2;;
    *) echo "cloud_relay: unknown pass option '$1'" >&2; return 2;; esac; done
  case $every in ''|*[!0-9]*|0) echo "cloud_relay: --interval must be a positive number of seconds" >&2; return 2;; esac
  while :; do handoff_arm; probe_arm; [ -z "$loop" ] && return 0; sleep "$every"; done
}

self_test() {
  local t ok=0 bad=0 c=0 h n stub
  t=$(mktemp -d "${TMPDIR:-/tmp}/cloud_relay_st.XXXXXX") || exit 1
  # Every scratch repository comes from the shared helper (tests/throwaway_git.sh, #2051).
  . "$HERE/../../../tests/throwaway_git.sh" && throwaway_git_env || exit 1
  throwaway_git_init "$t/o.git" -q --bare; throwaway_git_init "$t/w" -q; cd "$t/w" || exit 1
  git remote add origin "$t/o.git"
  h=0123456789abcdef0123456789abcdef01234567; n=0123456789abcdef0123456789abcdef
  export HPO_STATE_DIR=$t/state
  stub=$t/stub.sh; printf '#!/bin/sh\necho "$1" >> "%s/pushed"\necho "review/$1 aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\n' "$t" > "$stub"; chmod +x "$stub"; export HPO_RELAY_PUSH=$stub
  mk() { # mk <pr> <subject-head> <verdict-head> <nonce-in-verdict> : push a probe ref for nonce n
    rm -rf "$t/pr"; throwaway_git_init "$t/pr" -q; mkdir "$t/pr/ev"; echo "$((c=c+1))" > "$t/pr/ev/e"
    printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$3" "$4" > "$t/pr/verdict.md"
    git -C "$t/pr" add -A; git -C "$t/pr" commit -qm "verdict $1 $2"
    git -C "$t/o.git" fetch -qf "$t/pr" "HEAD:refs/heads/probe/rev-$1-${n:0:8}"; }
  chk() { # chk <name> <want-rc> <cmd...>
    local name=$1 want=$2; shift 2; "$@" >/dev/null 2>&1; local rc=$?
    if [ "$rc" = "$want" ]; then ok=$((ok+1)); echo "  ok   $name"; else bad=$((bad+1)); echo "  FAIL $name (rc=$rc, want $want)"; fi; }
  chk "no ref is refused" 2 relay 7 $n $h
  mk 7 $h $h $n;           chk "a clean ref relays (null control)" 0 relay 7 $n $h
  chk "the stub saw the push" 0 test "$(cat "$t/pushed")" = 7
  chk "the same push relayed twice is refused" 2 relay 7 $n $h
  mk 7 $h $h $n;           chk "a re-pushed ref relays again" 0 relay 7 $n $h
  mk 7 $h $h ffffffffffffffffffffffffffffffff; chk "a nonce mismatch is refused" 2 relay 7 $n $h
  mk 7 $h ${h%?}0 $n;     chk "a verdict naming another head is refused" 2 relay 7 $n $h
  mk 8 $h $h $n;           chk "a ref pushed for PR 8 leaves PR 7 with no ref" 2 relay 7 $n $h
  git -C "$t/o.git" update-ref refs/heads/probe/rev-7-${n:0:8} "$(git -C "$t/o.git" rev-parse refs/heads/probe/rev-8-${n:0:8})"
  chk "a commit subject naming PR 8 under PR 7's ref is refused" 2 relay 7 $n $h
  chk "a short head is refused" 2 relay 7 $n ${h%?}
  chk "a short nonce is refused" 2 relay 7 abc $h
  chk "a non-numeric PR is refused" 2 relay x $n $h
  # normalisation of a bracketed blocked tail
  bl() { # bl <first line>: push a probe ref for PR 9 with that first line
    rm -rf "$t/pr"; throwaway_git_init "$t/pr" -q; mkdir "$t/pr/ev"; echo "$((c=c+1))" > "$t/pr/ev/e"
    printf '%s\n\nbus-nonce: %s\n' "$1" "$n" > "$t/pr/verdict.md"
    git -C "$t/pr" add -A; git -C "$t/pr" commit -qm "verdict 9 $h"
    git -C "$t/o.git" fetch -qf "$t/pr" "HEAD:refs/heads/probe/rev-9-${n:0:8}"; }
  : > "$t/seen"; vstub=$t/vstub.sh
  printf '#!/bin/sh\nhead -n 1 "$2" > "%s/seen"\n' "$t" > "$vstub"; chmod +x "$vstub"; HPO_RELAY_PUSH=$vstub
  bl "Fix review: blocked $h [mutation: a fix line deleted]"
  chk "a bracketed blocked tail relays" 0 relay 9 $n $h
  chk "it was rewritten losslessly" 0 test "$(cat "$t/seen")" = "Fix review: blocked $h mutation: a fix line deleted"
  bl "Fix review: blocked $h [mutation: a fix line deleted]"
  out=$(relay 9 $n $h 2>&1); chk "the log line names the rewrite" 0 test "${out#*normalised first line}" != "$out"
  bl "Fix review: blocked $h mutation: a fix line deleted"
  chk "an unbracketed blocked line relays unchanged (null control)" 0 relay 9 $n $h
  chk "and is seen unchanged" 0 test "$(cat "$t/seen")" = "Fix review: blocked $h mutation: a fix line deleted"
  bl "Fix review: merge $h [class: none]"
  chk "a bracketed merge suffix is refused, not stripped" 2 relay 9 $n $h
  bl "Fix review: blocked $h [mutation: [nested] reason]"
  chk "a nested bracket is refused" 2 relay 9 $n $h
  bl "Fix review: blocked $h [Mutation: x]"
  chk "a bracketed class outside [a-z-]+ is refused" 2 relay 9 $n $h
  # --confirm: confirm runs only after a passed push-verdict, and logs POSTED or OWED
  cstub=$t/cstub.sh; printf '#!/bin/sh\necho "$1 $2" >> "%s/confirmed"\n' "$t" > "$cstub"; chmod +x "$cstub"
  fstub=$t/fstub.sh; printf '#!/bin/sh\nexit 1\n' > "$fstub"; chmod +x "$fstub"
  HPO_RELAY_PUSH=$stub; HPO_RELAY_CONFIRM=$cstub; LOG=$t/relay.log; rm -f "$t/confirmed" "$LOG"
  mk 7 $h $h $n; CONFIRM=1
  chk "relay --confirm succeeds" 0 relay 7 $n $h
  chk "confirm ran with the review sha push-verdict printed" 0 test "$(cat "$t/confirmed")" = "7 aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  chk "the log has a POSTED line" 0 grep -q "^POSTED .* 7 aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa$" "$LOG"
  mk 7 $h $h ffffffffffffffffffffffffffffffff; rm -f "$t/confirmed"
  chk "a refused relay does not confirm" 2 relay 7 $n $h
  chk "and logs nothing new" 0 test "$(wc -l < "$LOG" | tr -d ' ')" = 1
  failpush=$t/failpush.sh; printf '#!/bin/sh\necho nope >&2\nexit 1\n' > "$failpush"; chmod +x "$failpush"
  mk 7 $h $h $n; HPO_RELAY_PUSH=$failpush
  chk "a failed push-verdict does not confirm" 1 relay 7 $n $h
  chk "confirm did not run after it" 0 test ! -f "$t/confirmed"
  HPO_RELAY_PUSH=$stub; HPO_RELAY_CONFIRM=$fstub
  chk "a failing confirm leaves the relay itself passed" 0 relay 7 $n $h
  chk "and logs OWED with the review sha" 0 grep -q "^OWED .* 7 aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa confirm failed$" "$LOG"
  nosha=$t/nosha.sh; printf '#!/bin/sh\necho done\n' > "$nosha"; chmod +x "$nosha"
  mk 7 $h $h $n; HPO_RELAY_PUSH=$nosha; HPO_RELAY_CONFIRM=$cstub
  chk "a push-verdict that printed no review sha logs OWED" 0 relay 7 $n $h
  chk "and the OWED line carries a dash" 0 grep -q "^OWED .* 7 - " "$LOG"
  CONFIRM=; HPO_RELAY_PUSH=$stub; unset HPO_RELAY_CONFIRM; : > "$LOG"; rm -f "$t/confirmed"
  mk 7 $h $h $n
  chk "without --confirm, relay logs nothing" 0 relay 7 $n $h
  chk "and the log stayed empty" 0 test ! -s "$LOG"
  # the watch pass
  HPO_RELAY_PUSH=$stub; rm -f "$t/pushed" "$t/state/cloud-relayed" "$t/state/cloud-relayed.refused"
  export HPO_BUS_STATE=$t/bus; mkdir -p "$t/bus"
  git -C "$t/o.git" for-each-ref --format='%(refname)' 'refs/heads/probe/' | while read -r r; do git -C "$t/o.git" update-ref -d "$r"; done
  mk 5 $h $h $n; mk 6 $h $h $n; git -C "$t/o.git" update-ref -d refs/heads/probe/rev-6-${n:0:8}
  probe_arm >/dev/null 2>&1
  chk "a ref with no dispatch record is left alone" 0 test ! -s "$t/pushed"
  printf '5 %s thread %s\n' "$h" "$n" > "$t/bus/dispatched"
  probe_arm >/dev/null 2>&1
  chk "a watch pass relays a dispatched ref once" 0 test "$(cat "$t/pushed")" = 5
  probe_arm >/dev/null 2>&1
  chk "a second pass relays nothing" 0 test "$(wc -l < "$t/pushed" | tr -d ' ')" = 1
  mk 5 $h $h ffffffffffffffffffffffffffffffff
  probe_arm >/dev/null 2>&1; probe_arm >/dev/null 2>&1
  chk "a refused ref is noted once and not retried" 0 test "$(wc -l < "$t/state/cloud-relayed.refused" | tr -d ' ')" = 1
  chk "--interval 0 is refused" 2 watch --interval 0
  chk "--once makes one pass and returns" 0 watch --once
  mk 5 $h $h $n; rm -f "$t/state/cloud-relayed" "$t/state/cloud-relayed.refused"; : > "$LOG"; CONFIRM=1; HPO_RELAY_CONFIRM=$cstub
  probe_arm >/dev/null 2>&1
  chk "a watch pass with --confirm confirms and logs POSTED" 0 grep -q "^POSTED .* 5 " "$LOG"
  CONFIRM=
  # the probe arm's other refs: any probe/* that is not rev-* is OWED on every pass until disposed
  LOG=$t/probe.log; : > "$LOG"; mk 5 $h $h $n
  git -C "$t/o.git" update-ref refs/heads/probe/scan-x "$(git -C "$t/o.git" rev-parse refs/heads/probe/rev-5-${n:0:8})"; PX=$(git -C "$t/o.git" rev-parse refs/heads/probe/scan-x)
  probe_arm >/dev/null 2>&1
  chk "a non-rev probe ref is logged OWED with ref and sha" 0 grep -q "^OWED .* probe-ref refs/heads/probe/scan-x $PX$" "$LOG"
  chk "a rev ref is relayed, not logged OWED (null control)" 1 grep -q "probe-ref refs/heads/probe/rev-" "$LOG"
  probe_arm >/dev/null 2>&1
  chk "it is logged again on the next pass (a level, not a diff)" 0 test "$(grep -c "probe-ref refs/heads/probe/scan-x" "$LOG")" = 2
  chk "dispose refuses a ref outside probe/ and handoff" 2 dispose refs/heads/main "$PX"
  chk "dispose refuses a short sha" 2 dispose refs/heads/probe/scan-x "${PX%?}"
  chk "dispose takes a probe ref at its sha" 0 dispose refs/heads/probe/scan-x "$PX"
  : > "$LOG"; probe_arm >/dev/null 2>&1
  chk "a disposed ref is not logged" 0 test ! -s "$LOG"
  mk 5 $h $h ffffffffffffffffffffffffffffffff
  git -C "$t/o.git" update-ref refs/heads/probe/scan-x "$(git -C "$t/o.git" rev-parse refs/heads/probe/rev-5-${n:0:8})"; PX2=$(git -C "$t/o.git" rev-parse refs/heads/probe/scan-x)
  probe_arm >/dev/null 2>&1
  chk "a disposed ref that moved is OWED again at its new sha" 0 grep -q "^OWED .* probe-ref refs/heads/probe/scan-x $PX2$" "$LOG"
  # the handoff arm (a bare origin holds PR branches, handoff/ and handoff-body/ refs)
  unset HPO_RELAY_PUSH; export HPO_RELAY_PUSH=$stub; LOG=$t/pass.log; : > "$LOG"; CONFIRM=
  prs=$t/prs.tsv; ustub=$t/ustub.sh; dstub=$t/dstub.sh; astub=$t/astub.sh; N40=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
  hc() { git -C "$t/pr" -c user.name=t -c user.email=t@t commit -q --allow-empty -m "$1"; }
  mkref() { git -C "$t/o.git" fetch -qf "$t/pr" "HEAD:refs/heads/$1"; }
  rm -rf "$t/pr"; throwaway_git_init "$t/pr" -q; hc base; mkref fix/topic-a-pr; PRH=$(git -C "$t/pr" rev-parse HEAD)
  printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"
  printf '#!/bin/sh\ncat "%s"\n' "$prs" > "$t/lister.sh"; chmod +x "$t/lister.sh"; export HPO_RELAY_PRS=$t/lister.sh
  # update stub: records args, advances the PR head to a new commit that contains the handoff
  printf '#!/bin/sh\necho "$1 $2 $(basename "$3" | cut -c1-0) $4 $5" >> "%s/updated"\ncp "$3" "%s/body.seen"\necho "$3" > "%s/body.path"\nprintf "41\\tfix/topic-a-pr\\t%s\\n" > "%s"\n' "$t" "$t" "$t" "$N40" "$prs" > "$ustub"
  printf '#!/bin/sh\necho "$1" >> "%s/approved"\n' "$t" > "$astub"
  printf '#!/bin/sh\necho "$1 $2 $3" >> "%s/dispatched.seen"\necho "bus-nonce: 0123456789abcdef0123456789abcdef"\n' "$t" > "$dstub"
  chmod +x "$ustub" "$astub" "$dstub"; export HPO_RELAY_UPDATE=$ustub HPO_RELAY_APPROVE=$astub HPO_RELAY_DISPATCH=$dstub
  # a missing body ref does nothing
  hc ahead; mkref handoff/topic-a; HS=$(git -C "$t/pr" rev-parse HEAD)
  handoff_arm >/dev/null 2>&1
  chk "a handoff with no body ref does nothing" 0 test ! -e "$t/updated"
  # a handoff ahead of its PR fires the arm
  rm -rf "$t/b"; throwaway_git_init "$t/b" -q; printf 'Part of #201\n\nCloses #77 and fixes #78.\n' > "$t/b/BODY.md"
  git -C "$t/b" add BODY.md; git -C "$t/b" -c user.name=t -c user.email=t@t commit -qm body; mkref2() { git -C "$t/o.git" fetch -qf "$t/b" "HEAD:refs/heads/handoff-body/topic-a"; }; mkref2
  handoff_arm >/dev/null 2>&1
  chk "a handoff ahead of its PR runs update_pr with branch and code sha" 0 grep -q "^fix/topic-a-pr $HS " "$t/updated"
  chk "the issues come from the body's closing keywords" 0 grep -q " 77 78 *$" "$t/updated"
  chk "the body handed to update_pr is the handoff-body BODY.md" 0 grep -q "^Part of #201" "$t/body.seen"
  # prepr's own body-path predicate, read from prepr.sh: the relay's update ran prepr on a body
  # it wrote directly in $TMPDIR, which that check refuses, so no relay update ever passed.
  eval "$(sed -n '/^shared_root() {/,/^}/p' "$HERE/../../pr/prepr.sh")"
  chk "the body update_pr gets passes prepr's body-path check (not directly in a shared root)" 1 shared_root "$(cat "$t/body.path")"
  chk "and that body's directory is removed after the update" 0 test ! -e "$(dirname -- "$(cat "$t/body.path")")"
  chk "held runs are approved on the branch" 0 test "$(cat "$t/approved")" = fix/topic-a-pr
  chk "dispatch runs at the NEW head" 0 test "$(cat "$t/dispatched.seen")" = "41 $N40 cloud"
  chk "OWED reviewer-fire is logged with pr, head and nonce" 0 grep -q "^OWED reviewer-fire 41 $N40 0123456789abcdef0123456789abcdef " "$LOG"
  # null control: the PR head now contains the handoff -> nothing more
  git -C "$t/pr" -c user.name=t -c user.email=t@t merge -q --no-edit -m m "$HS" 2>/dev/null; git -C "$t/pr" reset -q --hard "$HS"; hc "pr tip"; mkref fix/topic-a-pr; NEW=$(git -C "$t/pr" rev-parse HEAD)
  printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$NEW" > "$prs"; rm -f "$t/updated"
  handoff_arm >/dev/null 2>&1
  chk "a handoff already merged into its PR does nothing (null control)" 0 test ! -e "$t/updated"
  # the hold file: a listed PR is skipped with one HELD line per pass; a malformed file refuses the pass
  hf=$t/state/cloud-handoff-hold; hu=$t/hu.sh; printf '#!/bin/sh\necho "$1 $2" >> "%s/hupdated"\n' "$t" > "$hu"; chmod +x "$hu"; HPO_RELAY_UPDATE=$hu
  printf '41\n' > "$hf"; ho=$(handoff_arm 2>&1)
  chk "a held PR whose handoff is already in its head prints no HELD (nothing to hold)" 1 grep -q HELD <<< "$ho"
  rm -f "$t/updated" "$t/hupdated" "$t/state/cloud-handoff-failed"; : > "$LOG"
  git -C "$t/pr" reset -q --hard "$PRH"; mkref fix/topic-a-pr; printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"
  printf '99\n41\n' > "$hf"; ho=$(handoff_arm 2>&1)
  chk "a held PR whose handoff is ahead is not updated" 0 test ! -e "$t/hupdated"
  chk "and prints HELD with the handoff tip it did not apply" 0 grep -q "HELD #41 $HS\$" <<< "$ho"
  chk "the HELD line is printed once per pass" 0 test "$(grep -c '^cloud_relay: HELD ' <<< "$ho")" = 1
  chk "and the held pass dispatches no reviewer" 1 grep -q "reviewer-fire" "$LOG"
  hc held-moved; mkref handoff/topic-a; HS2=$(git -C "$t/pr" rev-parse HEAD)
  ho=$(handoff_arm 2>&1)
  chk "a held PR whose handoff tip moved is still not updated" 0 test ! -e "$t/hupdated"
  chk "and HELD names the moved tip" 0 grep -q "HELD #41 $HS2\$" <<< "$ho"
  echo "topic-a $HS2" > "$t/state/cloud-handoff-failed"; ho=$(handoff_arm 2>&1)
  chk "a hold outranks a recorded failed update: still HELD" 0 grep -q "HELD #41 $HS2\$" <<< "$ho"
  rm -f "$t/state/cloud-handoff-failed"
  printf '99\n' > "$hf"; ho=$(handoff_arm 2>&1)
  chk "an unheld PR is updated as before (null control)" 0 grep -q "^fix/topic-a-pr $HS2\$" "$t/hupdated"
  chk "and prints no HELD" 1 grep -q HELD <<< "$ho"
  printf '141\n' > "$hf"; rm -f "$t/hupdated"; ho=$(handoff_arm 2>&1)
  chk "a held #141 does not hold #41 (whole-line match)" 0 test -e "$t/hupdated"
  chk "and prints no HELD" 1 grep -q HELD <<< "$ho"
  : > "$hf"; rm -f "$t/hupdated"; handoff_arm >/dev/null 2>&1
  chk "an empty hold file holds nothing" 0 test -e "$t/hupdated"
  printf '# held: roster freeze\n\n99\n' > "$hf"; rm -f "$t/hupdated"; handoff_arm >/dev/null 2>&1
  chk "comments and blank lines are allowed and hold nothing" 0 test -e "$t/hupdated"
  rm -f "$hf" "$t/hupdated"; handoff_arm >/dev/null 2>&1
  chk "no hold file holds nothing" 0 test -e "$t/hupdated"
  printf '41\n' > "$hf"
  chk "held <pr> says held (rc 0) for a listed PR" 0 held 41
  chk "held <pr> says not held (rc 1) for an unlisted PR" 1 held 42
  chk "held <pr> matches the whole line (#4 is not #41)" 1 held 4
  chk "held refuses a non-number" 2 held 4x
  chk "the CLI 'cloud_relay.sh held' says held (rc 0)" 0 bash "$HERE/cloud_relay.sh" held 41
  chk "the CLI 'cloud_relay.sh held' says not held (rc 1)" 1 bash "$HERE/cloud_relay.sh" held 42
  chk "a well-formed hold file logs no refusal (null control)" 1 grep -q handoff-hold-malformed "$LOG"
  for hb in '41 99' 'abc' '41x' '0' '-1' '041' '41,99' ' 41' '41 # c'; do
    printf '%s\n' "$hb" > "$hf"; rm -f "$t/hupdated"; : > "$LOG"; ho=$(handoff_arm 2>&1)
    chk "a malformed hold file ('$hb') refuses the pass (rc 2)" 2 handoff_arm
    chk "and holds none: the PR is not updated" 0 test ! -e "$t/hupdated"
    chk "and holds all: no HELD line" 1 grep -q HELD <<< "$ho"
    chk "and names the refusal" 0 grep -q "refused: malformed hold file" <<< "$ho"
    chk "and logs OWED handoff-hold-malformed" 0 grep -q "^OWED .* handoff-hold-malformed $hf\$" "$LOG"
    chk "and held refuses it too" 2 held 41
    chk "and the CLI 'cloud_relay.sh held' refuses it (rc 2)" 2 bash "$HERE/cloud_relay.sh" held 41
  done
  # the held number is the unterminated last line, so the check fails when that line is dropped
  printf '99\n41' > "$hf"; ho=$(handoff_arm 2>&1)
  chk "a last line without a newline is read: it holds #41" 0 grep -q "HELD #41 " <<< "$ho"
  chk "and held says held for it" 0 held 41
  printf '41' > "$hf"
  chk "a one-line file without a newline holds #41" 0 held 41
  printf '99\n41\n' > "$hf"; ho=$(handoff_arm 2>&1)
  chk "the same file newline-terminated holds #41 (null control)" 0 grep -q "HELD #41 " <<< "$ho"
  rm -f "$hf" "$t/hupdated"; HPO_RELAY_UPDATE=$ustub
  rm -f "$t/updated"; git -C "$t/pr" reset -q --hard "$PRH"; mkref fix/topic-a-pr; printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"; : > "$LOG"
  # a failing update is noted once and not retried
  rm -f "$t/updated"; git -C "$t/pr" reset -q --hard "$PRH"; mkref fix/topic-a-pr
  printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"; : > "$LOG"
  fu=$t/fu.sh; printf '#!/bin/sh\necho x >> "%s/updated"\nexit 1\n' "$t" > "$fu"; chmod +x "$fu"; HPO_RELAY_UPDATE=$fu
  handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
  chk "a failed update is tried once" 0 test "$(wc -l < "$t/updated" | tr -d ' ')" = 1
  chk "and logs OWED handoff-update" 0 grep -q "^OWED .* handoff-update 41 topic-a $HS2" "$LOG"
  # a BUSY update (75: another update_pr.sh holds the branch's worktree) is no failure: not recorded, retried next pass
  rm -f "$t/updated" "$t/state/cloud-handoff-failed"; : > "$LOG"
  bu=$t/bu.sh; printf '#!/bin/sh\necho x >> "%s/updated"\nexit 75\n' "$t" > "$bu"; chmod +x "$bu"; HPO_RELAY_UPDATE=$bu
  handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
  chk "a busy update is tried again on the next pass" 0 test "$(wc -l < "$t/updated" | tr -d ' ')" = 2
  chk "and is not recorded failed" 0 test ! -s "$t/state/cloud-handoff-failed"
  chk "nor logged OWED" 1 grep -q "handoff-update" "$LOG"
  # handoff refs with no open PR are OWED on every pass until disposed
  : > "$LOG"; mkref handoff/topic-b; OB=$(git -C "$t/pr" rev-parse HEAD)
  handoff_arm >/dev/null 2>&1
  chk "a handoff ref with no open PR is logged OWED" 0 grep -q "^OWED .* handoff-no-pr refs/heads/handoff/topic-b $OB$" "$LOG"
  chk "a handoff ref with an open PR is not (null control)" 1 grep -q "handoff-no-pr refs/heads/handoff/topic-a " "$LOG"
  chk "nor its handoff-body ref (null control)" 1 grep -q "handoff-no-pr refs/heads/handoff-body/topic-a " "$LOG"
  handoff_arm >/dev/null 2>&1
  chk "the no-PR ref is logged again on the next pass" 0 test "$(grep -c "handoff-no-pr refs/heads/handoff/topic-b" "$LOG")" = 2
  git -C "$t/o.git" fetch -qf "$t/b" "HEAD:refs/heads/handoff-body/topic-c"; OC=$(git -C "$t/o.git" rev-parse refs/heads/handoff-body/topic-c)
  : > "$LOG"; handoff_arm >/dev/null 2>&1
  chk "a handoff-body ref with no open PR is logged OWED" 0 grep -q "^OWED .* handoff-no-pr refs/heads/handoff-body/topic-c $OC$" "$LOG"
  dispose refs/heads/handoff/topic-b "$OB" >/dev/null; dispose refs/heads/handoff-body/topic-c "$OC" >/dev/null
  : > "$LOG"; handoff_arm >/dev/null 2>&1
  chk "disposed no-PR refs are not logged" 1 grep -q "handoff-no-pr" "$LOG"
  git -C "$t/o.git" update-ref -d refs/heads/handoff-body/topic-c; git -C "$t/o.git" update-ref -d refs/heads/handoff/topic-b
  hc moved; mkref handoff/topic-b; OB2=$(git -C "$t/pr" rev-parse HEAD)
  : > "$LOG"; handoff_arm >/dev/null 2>&1
  chk "a disposed no-PR ref that moved is OWED again" 0 grep -q "^OWED .* handoff-no-pr refs/heads/handoff/topic-b $OB2$" "$LOG"
  failprs=$t/failprs.sh; printf '#!/bin/sh\nexit 1\n' > "$failprs"; chmod +x "$failprs"
  : > "$LOG"; HPO_RELAY_PRS=$failprs handoff_arm >/dev/null 2>&1
  chk "a failed PR listing reports no ref as without a PR" 0 test ! -s "$LOG"
  git -C "$t/o.git" update-ref -d refs/heads/handoff/topic-b; : > "$LOG"
  chk "pass --loop is the only loop (a bad interval is refused)" 2 pass --loop --interval 0
  HPO_RELAY_UPDATE=$ustub; rm -f "$t/updated" "$t/state/cloud-handoff-failed"; : > "$LOG"; printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"
  chk "pass runs both arms once and returns" 0 pass --log "$LOG"
  chk "the pass fired the handoff arm" 0 test -e "$t/updated"
  rm -rf "$t"
  echo "cloud_relay self-test: $((ok+bad)) checks, $bad failed"; [ "$bad" = 0 ]
}

case ${1:-} in
  --self-test) self_test; exit $?;;
  held) shift; held "$@"; exit $?;;
  --watch) shift; watch "$@"; exit $?;;
  pass) shift; pass "$@"; exit $?;;
  dispose) shift; dispose "$@"; exit $?;;
  --confirm|--log) while [ $# -gt 0 ]; do case $1 in --confirm) CONFIRM=1; shift;; --log) LOG=${2:-}; shift 2;; *) break;; esac; done
    [ $# = 3 ] || { echo "usage: cloud_relay.sh [--confirm] [--log FILE] <pr> <nonce> <head40>" >&2; exit 2; }; relay "$1" "$2" "$3"; exit $?;;
  ''|-*) echo "usage: cloud_relay.sh <pr> <nonce> <head40> | pass [--confirm] [--log FILE] [--loop [--interval N]] | dispose <ref> <sha40> | --watch [--interval N] [--once] [--confirm] [--log FILE] | --self-test" >&2; exit 2;;
  *) [ $# = 3 ] || { echo "usage: cloud_relay.sh <pr> <nonce> <head40>" >&2; exit 2; }; relay "$1" "$2" "$3"; exit $?;;
esac
