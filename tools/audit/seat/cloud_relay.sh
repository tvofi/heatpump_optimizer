#!/bin/bash
# cloud_relay.sh [--confirm] [--log FILE] <pr> <nonce> <head40>    relay one cloud reviewer's verdict
# cloud_relay.sh --watch [--interval N] [--once] [--confirm] [--log FILE]
# cloud_relay.sh pass [--confirm] [--log FILE] [--loop [--interval N]]
# cloud_relay.sh dispose [--log FILE] <ref> <sha40>                    record an OWED probe/handoff/review ref handled
# cloud_relay.sh held <pr>                                             rc 0 held, 1 not held, 2 malformed hold file
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
# probe/rev-* is OWED until `dispose <ref> <sha>` writes `<ref> <sha>` to
# <state>/cloud-disposed: a level, not a diff, so a missed line is repeated rather
# than lost, and a disposed ref that moves is owed again. The level is `<log>.level`
# (beside --log), whose `OWED <utc> probe-ref <ref> <sha>` lines EVERY pass rewrites,
# never appends; dispose drops its line at once; a failed listing leaves it as it was.
# It relays each probe/rev-* ref+sha once.
# The dispatch record ($HPO_BUS_STATE or ~/.zcode/bus, field order `pr head
# thread nonce`) supplies the head and full nonce for a ref's pr and nonce8; a ref
# with no record is logged and left for a later pass. A refused ref+sha (relay
# rc 2, a refusal of the ref itself) is noted in `<ledger>.refused` and not
# retried, so a loop does not repeat one refusal every interval; any other
# failure (a push or a fetch: an HTTP 400 once sat 3 h refused in silence) is
# retried on later passes, HPO_RELAY_TRIES times in all (default 3; tries in
# `<ledger>.tries`), and then refused. A refusal prints
#   cloud_relay: REFUSED <ref> <sha> <reason>       (the relay's last stderr line)
# and is `OWED <utc> probe-refused <ref> <sha> <reason>` in <log>.level until
# disposed; one refused before reasons were kept (`<ledger>.refused-why`) stays
# silent. A re-pushed ref has a new sha and is tried again. --once makes
# one pass (the self-test's and cron's shape). Run it detached via daemonize.py.
#
# A push-verdict refused non-fast-forward (review/<pr> moved under it) is run
# again, at most three times in all: bus.sh re-reads the fresh tip and appends the
# same verdict there; nothing is forced. A fresh tip whose tree is already this
# verdict's (VERDICT.md, evidence/: bus.sh's tree) is not re-applied. Either case
# is printed. After the push the relay prints `review/<pr> remote tip <sha>`, the
# tip `git ls-remote` answers, never the commit push-verdict built here.
#
# --confirm does not stop at push-verdict (two verdicts once sat relayed and
# unposted for 20 minutes): after a push-verdict that PASSED it runs
# `bus.sh confirm <pr> <review-sha>`, the sha being review/<pr>'s remote tip when
# that tip carries this verdict's tree (confirm takes only a tip), and appends
# one line to the log (--log FILE, default <state>/cloud-relay.log, which the
# orchestrator reads):
#   POSTED <utc> <pr> <review-sha>          confirm succeeded
#   OWED   <utc> <pr> <review-sha|-> <why>  push-verdict passed, the verdict is not posted;
#                                           <why> carries confirm's last output line
# confirm never runs after a refused relay or a failed push-verdict, and writes
# nothing for them (a refusal prints its reason, and --watch's .refused file
# holds it). HPO_RELAY_CONFIRM replaces the confirm command (the self-test's stub).
#
# `pass` is the orchestrator's whole beat, ONE entry point a driver calls once
# (and takes over relay_watch.sh, which was session-local). A pass runs two arms,
# and with --confirm a third.
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
#     topic has no open PR is `OWED <utc> handoff-no-pr <ref> <sha>` in
#     <log>.level, rewritten every pass, until disposed; a failed PR listing
#     leaves those lines as they were. The log itself holds events only.
#     HOLD. `<state>/cloud-handoff-hold` lists PR numbers, one per line (blank
#     lines and `#` lines allowed); only the orchestrator writes or edits it.
#     A listed PR whose handoff is ahead is NOT updated and prints
#       cloud_relay: HELD #<pr> <handoff tip>
#     once per pass; removing the number resumes it. A missing or empty file
#     holds nothing. A line that is not a plain PR number (or a file that is
#     not readable) refuses the whole handoff arm that pass (rc 2, and
#     `OWED <utc> handoff-hold-malformed <file> -` in <log>.level until a pass
#     reads the file well-formed): never hold-all, never hold-none.
#     `held <pr>` answers from the same file, for a driver that updates PRs
#     itself (the beat's handoff job reads it unchanged).
#   probe arm: the --watch pass above (probe/rev-* -> relay -> confirm; other
#     probe refs OWED until disposed).
#   confirm arm (--confirm): the ledger is written before confirm runs, so a
#     confirm that failed, a relay by a script without the confirm, or one by a
#     call without --confirm was never confirmed later ('already relayed';
#     #2659, #2632). For every review/<pr> tip (git ls-remote) that the relay
#     pushed -- the tip's `bus-nonce:` matches a ledgered probe/rev-<pr>-<nonce8>
#     -- and whose tree is not in bus.sh's posted record (`<pr> <tree>` in
#     $HPO_BUS_STATE/posted-signed), it runs `bus.sh confirm <pr> <tip>`: POSTED
#     on success; on failure `OWED <utc> confirm-owed refs/heads/review/<pr> <tip>
#     tries=<n>/<max>: <last output line>` in <log>.level, retried next pass up to
#     HPO_RELAY_CONFIRM_TRIES (default 3), then left owed, untried, until bus.sh's
#     record shows it posted or `dispose` takes it. A tip with no dispatch for its
#     PR, head and nonce is owed `undispatched` and never confirmed. A tip the
#     relay did not push waits for the orchestrator's own read (bus.sh). Settled
#     tips are noted in `<ledger>.confirm-done`, so a pass fetches only new ones.
#     It makes no gh call; bus.sh confirm posts.
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
# A stopped relay ends the whole tree it started (R10-PUSHER-REAP): pr_args.sh's EXIT
# trap reaps it, and the update runs asynchronously so an INT does not wait behind it.
. "$HERE/pr_args.sh"; pr_exit_trap

die() { echo "cloud_relay: refused: $*" >&2; return 2; }

relay_log() { printf '%s' "${LOG:-${HPO_STATE_DIR:-$HOME/.local/state/hpo}/cloud-relay.log}"; }
logline() { mkdir -p "$(dirname -- "$(relay_log)")" && printf '%s %s\n' "$1" "$(date -u +%FT%TZ) $2" >> "$(relay_log)"; }
# The level is state, not an event: an arm writes `OWED <utc> <kind> <ref> <sha>` lines to a
# file of its own, then level_set makes them the whole of <kind> in <log>.level, which the
# tick prints as is. Appended to the log on every pass they were replayed whole (2026-10-21).
level_line() { printf 'OWED %s %s %s %s%s\n' "$(date -u +%FT%TZ)" "$1" "$2" "$3" "${4:+ $4}"; }  # [why]
level_set() { # level_set <kind> <lines-file>: <kind>'s lines in <log>.level become that file's
  local lv; lv=$(relay_log).level
  mkdir -p "$(dirname -- "$lv")" || return 1
  { [ -f "$lv" ] && awk -v k="$1" '$3 != k' "$lv"; cat "$2"; } > "$lv.$$" && mv -f "$lv.$$" "$lv"
  rm -f "$2"
}
posted() { logline POSTED "$1 $2"; echo "cloud_relay: POSTED #$1 $2"; }
owed() { logline OWED "$1 $2 $3"; echo "cloud_relay: OWED #$1: $3" >&2; }
last_line() { printf '%s\n' "$1" | awk 'NF { l = $0 } END { print (l == "" ? "(no output)" : l) }'; }
push_run() { if [ -n "${HPO_RELAY_PUSH:-}" ]; then "$HPO_RELAY_PUSH" "$@"; else bash "$HERE/bus.sh" push-verdict "$@"; fi; }
confirm_run() { if [ -n "${HPO_RELAY_CONFIRM:-}" ]; then "$HPO_RELAY_CONFIRM" "$@"; else bash "$HERE/bus.sh" confirm "$@"; fi; }
verdict_tree() { # <verdict.md> <ev dir> -> the tree bus.sh push-verdict builds from them (VERDICT.md, evidence/)
  local s gd tree; s=$(mktemp -d "${TMPDIR:-/tmp}/cloud_relay_tree.XXXXXX") || return 1
  gd=$(git rev-parse --absolute-git-dir) && mkdir -p "$s/w/evidence" && cp "$1" "$s/w/VERDICT.md" && cp -R "$2"/. "$s/w/evidence/" \
    && tree=$(cd "$s/w" && export GIT_DIR="$gd" GIT_INDEX_FILE="$s/index" GIT_WORK_TREE="$s/w" && git add -A -f . && git write-tree)
  local rc=$?; rm -rf "$s"; [ $rc = 0 ] && echo "$tree"
}
review_tip() { # <pr> -> review/<pr>'s tip as ls-remote answers it, its objects fetched; nothing when absent, rc 1 when unknown
  local tip; tip=$(git ls-remote origin "refs/heads/review/$1") || return 1; tip=$(awk 'NF { print $1; exit }' <<< "$tip")
  [ -n "$tip" ] || return 0
  git cat-file -e "$tip^{commit}" 2>/dev/null || git fetch -q origin "+refs/heads/review/$1:refs/hpo-relay/review/$1" 2>/dev/null
  git cat-file -e "$tip^{commit}" 2>/dev/null && echo "$tip"
}

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
  git fetch -q origin "$ref" || { echo "cloud_relay: could not fetch $ref" >&2; return 1; }
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
  local out sha2 wt tip tries=0
  wt=$(verdict_tree "$d/verdict.md" "$d/ev") || { echo "cloud_relay: could not build the verdict's tree" >&2; return 1; }
  # A push refused non-fast-forward (review/<pr> moved since push-verdict read its tip) is
  # re-applied: push-verdict reads the fresh tip again and appends the same verdict there,
  # never forcing. A fresh tip that already carries this verdict's tree is not re-applied.
  while :; do
    tries=$((tries + 1))
    out=$(push_run "$pr" "$d/verdict.md" "$d/ev" 2> "$d/push.err") && { cat "$d/push.err" >&2; break; }
    cat "$d/push.err" >&2; printf '%s\n' "$out"
    grep -Eq 'non-fast-forward|fetch first' "$d/push.err" || return 1
    if tip=$(review_tip "$pr") && [ -n "$tip" ] && [ "$(git rev-parse "$tip^{tree}")" = "$wt" ]; then
      echo "cloud_relay: review/$pr refused non-fast-forward; its fresh tip $tip already carries this verdict: not re-applied"; out=; break
    fi
    [ "$tries" -lt 3 ] || { echo "cloud_relay: review/$pr refused non-fast-forward $tries times; giving up this pass" >&2; return 1; }
    echo "cloud_relay: review/$pr refused non-fast-forward; re-applying the verdict on its fresh tip"
  done
  [ -z "$out" ] || printf '%s\n' "$out"
  mkdir -p "$state" && echo "$ref $sha" >> "$led"
  # The remote's tip, not the commit push-verdict built here: confirm takes only a tip (bus.sh
  # unpack), and it is confirmed only when it carries this verdict's tree.
  sha2=-; tip=$(review_tip "$pr") && [ -n "$tip" ] && [ "$(git rev-parse "$tip^{tree}")" = "$wt" ] && sha2=$tip
  echo "cloud_relay: review/$pr remote tip ${tip:-none}"
  if [ -n "${CONFIRM:-}" ]; then
    if [ "$sha2" = - ]; then owed "$pr" - "review/$pr's remote tip ${tip:-none} does not carry this verdict"
    else out=$(confirm_run "$pr" "$sha2" 2>&1) && posted "$pr" "$sha2" || owed "$pr" "$sha2" "confirm failed: $(last_line "$out")"; fi
  fi
  echo "cloud_relay: relayed $ref $sha; next: bus.sh confirm $pr $sha2"
}

disposed() { # disposed <ref> <sha>: the orchestrator ran `dispose` on this ref at this sha
  local f=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/cloud-disposed; [ -f "$f" ] && grep -qxF "$1 $2" "$f"; }

dispose() { # dispose <ref> <sha>: a probe or handoff ref at that sha is handled; it is OWED again once it moves
  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo}
  [ $# = 2 ] || { echo "usage: cloud_relay.sh dispose <ref> <sha40>" >&2; return 2; }
  case $1 in refs/heads/probe/?*|refs/heads/handoff/?*|refs/heads/handoff-body/?*|refs/heads/review/?*) ;; *) die "'$1' is not a refs/heads/probe/, handoff/, handoff-body/ or review/ ref"; return;; esac
  printf '%s' "$2" | grep -Eq '^[0-9a-f]{40}$' || { die "sha must be 40 lowercase hex"; return; }
  mkdir -p "$state" && echo "$1 $2" >> "$state/cloud-disposed" || return 1
  local lv; lv=$(relay_log).level   # owed no longer: off the level now, not at the next pass
  if [ -f "$lv" ]; then awk -v r="$1" -v s="$2" '!($4 == r && $5 == s)' "$lv" > "$lv.$$" && mv -f "$lv.$$" "$lv"; fi
  echo "cloud_relay: disposed $1 $2"
}

probe_arm() { # one pass over every probe/* ref: rev-* relays each unseen ref+sha, any other is OWED until disposed
  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} led bus sha ref k pr n8 rec nonce head rc why n max=${HPO_RELAY_TRIES:-3}
  led=$state/cloud-relayed; bus=${HPO_BUS_STATE:-$HOME/.zcode/bus}
  # a failed listing leaves the level as it was: unknown is not "nothing owed"
  git ls-remote origin 'refs/heads/probe/*' > "${TMPDIR:-/tmp}/cloud_relay_ls.$$" || { echo "cloud_relay: ls-remote failed; will retry" >&2; rm -f "${TMPDIR:-/tmp}/cloud_relay_ls.$$"; return 0; }
  mkdir -p "$state"; : > "$state/cloud-level-probe.$$"; : > "$state/cloud-level-refused.$$"
  while read -r sha ref; do
    [ -n "$ref" ] || continue
    case $ref in refs/heads/probe/rev-*) ;;
      *) disposed "$ref" "$sha" || { level_line probe-ref "$ref" "$sha" >> "$state/cloud-level-probe.$$"; echo "cloud_relay: OWED probe-ref $ref $sha"; }; continue;; esac
    if [ -f "$led" ] && grep -qxF "$ref $sha" "$led"; then continue; fi
    if [ -f "$led.refused" ] && grep -qxF "$ref $sha" "$led.refused"; then
      # a refusal is owed until disposed; one recorded before reasons were kept stays silent
      why=$(awk -v r="$ref" -v s="$sha" '$1 == r && $2 == s { $1 = $2 = ""; w = substr($0, 3) } END { print w }' "$led.refused-why" 2>/dev/null)
      [ -z "$why" ] || disposed "$ref" "$sha" || level_line probe-refused "$ref" "$sha" "$why" >> "$state/cloud-level-refused.$$"
      continue
    fi
    k=${ref#refs/heads/probe/rev-}; pr=${k%%-*}; n8=${k#*-}
    rec=$(awk -v p="$pr" -v n="$n8" '$1 == p && index($4, n) == 1 { print $2, $4 }' "$bus/dispatched" 2>/dev/null | tail -n 1)
    if [ -z "$rec" ]; then echo "$(date -u +%FT%TZ) cloud_relay: $ref $sha has no dispatch record in $bus; leaving it" >&2; continue; fi
    head=${rec%% *}; nonce=${rec#* }
    echo "$(date -u +%FT%TZ) cloud_relay: relaying $ref $sha"
    relay "$pr" "$nonce" "$head" 2> "$state/cloud-relay-err.$$"; rc=$?; cat "$state/cloud-relay-err.$$" >&2
    [ $rc -ne 0 ] || continue
    # rc 2 is a refusal of the ref itself, final; any other failure (a push, a fetch) is
    # retried on later passes, at most HPO_RELAY_TRIES times in all, then refused with its reason.
    why=$(last_line "$(cat "$state/cloud-relay-err.$$")"); echo "$ref $sha" >> "$led.tries"
    n=$(grep -cxF "$ref $sha" "$led.tries")
    if [ $rc = 2 ] || [ "$n" -ge "$max" ]; then
      echo "$ref $sha" >> "$led.refused"; echo "$ref $sha $why" >> "$led.refused-why"
      level_line probe-refused "$ref" "$sha" "$why" >> "$state/cloud-level-refused.$$"; echo "cloud_relay: REFUSED $ref $sha $why"
    else echo "cloud_relay: relay of $ref $sha failed (rc=$rc, try $n of $max); the next pass retries: $why" >&2; fi
  done < "${TMPDIR:-/tmp}/cloud_relay_ls.$$"
  rm -f "${TMPDIR:-/tmp}/cloud_relay_ls.$$" "$state/cloud-relay-err.$$"
  level_set probe-ref "$state/cloud-level-probe.$$"; level_set probe-refused "$state/cloud-level-refused.$$"
}

confirm_arm() { # one pass over review/* tips the relay delivered: confirm each not yet posted, owed on the level until it is
  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} led bus sha ref pr tree v nonce head n why lv max=${HPO_RELAY_CONFIRM_TRIES:-3}
  led=$state/cloud-relayed; bus=${HPO_BUS_STATE:-$HOME/.zcode/bus}; lv=$(relay_log).level
  git ls-remote origin 'refs/heads/review/*' > "$state/cloud-reviews.$$" || { echo "cloud_relay: ls-remote of review/* failed; will retry" >&2; rm -f "$state/cloud-reviews.$$"; return 0; }
  : > "$state/cloud-level-confirm.$$"
  while read -r sha ref; do
    pr=${ref#refs/heads/review/}; case $pr in ''|*[!0-9]*) continue;; esac
    # only what this relay delivered: a reviewer of the orchestrator's own waits for its thread read
    grep -q "^refs/heads/probe/rev-$pr-" "$led" 2>/dev/null || continue
    grep -qxF "$pr $sha" "$led.confirm-done" 2>/dev/null && continue
    git cat-file -e "$sha^{commit}" 2>/dev/null || git fetch -q origin "+$ref:refs/hpo-relay/review/$pr" 2>/dev/null
    if ! git cat-file -e "$sha^{commit}" 2>/dev/null; then  # unknown is not "nothing owed": keep its line
      [ -f "$lv" ] && awk -v r="$ref" -v s="$sha" '$3 == "confirm-owed" && $4 == r && $5 == s' "$lv" >> "$state/cloud-level-confirm.$$"; continue
    fi
    tree=$(git rev-parse "$sha^{tree}"); v=$(git show "$sha:VERDICT.md" 2>/dev/null)
    nonce=$(sed -n 's/^bus-nonce: \([0-9a-f]\{32\}\)$/\1/p' <<< "$v" | head -n 1)
    # posted (bus.sh's record of each tree it posted for a PR), or a tip the relay did not push: settled for this sha
    if grep -qxF "$pr $tree" "$bus/posted-signed" 2>/dev/null || ! grep -q "^refs/heads/probe/rev-$pr-${nonce:0:8} " "$led"; then
      echo "$pr $sha" >> "$led.confirm-done"; continue; fi
    disposed "$ref" "$sha" && continue
    head=$(head -n 1 <<< "$v" | grep -oE '[0-9a-f]{40}' | head -n 1)
    if ! awk -v p="$pr" -v h="$head" -v n="$nonce" '$1 == p && $2 == h && $4 == n { f = 1 } END { exit !f }' "$bus/dispatched" 2>/dev/null; then
      level_line confirm-owed "$ref" "$sha" "undispatched: no dispatch of #$pr at $head with this verdict's nonce; confirm refuses it" >> "$state/cloud-level-confirm.$$"; continue
    fi
    n=$(awk -v p="$pr" -v s="$sha" '$1 == p && $2 == s { k++ } END { print k + 0 }' "$led.confirm-tries" 2>/dev/null)
    if [ "${n:-0}" -ge "$max" ]; then
      why=$(awk -v p="$pr" -v s="$sha" '$1 == p && $2 == s { $1 = $2 = ""; w = substr($0, 3) } END { print w }' "$led.confirm-tries")
      level_line confirm-owed "$ref" "$sha" "tries=$n/$max, not retried; bus.sh confirm $pr $sha by hand, or dispose: $why" >> "$state/cloud-level-confirm.$$"; continue
    fi
    if why=$(confirm_run "$pr" "$sha" 2>&1); then posted "$pr" "$sha"; echo "$pr $sha" >> "$led.confirm-done"; continue; fi
    why=$(last_line "$why"); n=$((n + 1)); echo "$pr $sha $why" >> "$led.confirm-tries"
    level_line confirm-owed "$ref" "$sha" "tries=$n/$max: $why" >> "$state/cloud-level-confirm.$$"; echo "cloud_relay: OWED confirm #$pr $sha: $why" >&2
  done < "$state/cloud-reviews.$$"
  rm -f "$state/cloud-reviews.$$"
  level_set confirm-owed "$state/cloud-level-confirm.$$"
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
  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} repo=${HPO_RELAY_REPO:-tvofi/heatpump_optimizer} f pr br head topic hs bs bd body iss nh nonce urc held_prs upd
  f=$state/cloud-handoff-failed; mkdir -p "$state"
  : > "$state/cloud-level-hold.$$"   # the refusal is a level: owed while the file is malformed, gone once it is not
  held_prs=$(hold_list) || { level_line handoff-hold-malformed "$(hold_file)" - >> "$state/cloud-level-hold.$$"; level_set handoff-hold-malformed "$state/cloud-level-hold.$$"; return 2; }
  level_set handoff-hold-malformed "$state/cloud-level-hold.$$"
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
    # The update is the reap's lead (pr_args.sh's PR_REAP_LEAD): a stopped relay TERMs it alone,
    # so update_pr.sh ends its push before it frees the branch lock, and reaps what is left after.
    # One launch for both routes, so the self-test's stub runs the production launch line.
    urc=0; upd=(bash "$HERE/update_pr.sh"); [ -z "${HPO_RELAY_UPDATE:-}" ] || upd=("$HPO_RELAY_UPDATE")
    "${upd[@]}" "$br" "$hs" "$body" $iss >&2 &
    PR_REAP_LEAD=$!; wait "$PR_REAP_LEAD" || urc=$?
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
      mkdir -p "$(dirname -- "$(relay_log)")" && printf 'OWED reviewer-fire %s %s %s %s\n' "$pr" "$nh" "$nonce" "$(date -u +%FT%TZ)" >> "$(relay_log)"
      echo "cloud_relay: OWED reviewer-fire #$pr $nh"
    else logline OWED "dispatch $pr $nh bus.sh dispatch failed; run it by hand"; fi
  done < "$state/cloud-prs.$$"
  # a handoff or handoff-body ref whose topic has no open PR is OWED on every pass until disposed
  cut -f2 "$state/cloud-prs.$$" | sed -e 's,^fix/,,' -e 's,-pr$,,' > "$state/cloud-topics.$$"
  : > "$state/cloud-level-handoff.$$"
  while read -r hs ref; do
    [ -n "$ref" ] || continue
    topic=${ref#refs/heads/handoff-body/}; topic=${topic#refs/heads/handoff/}
    grep -qxF "$topic" "$state/cloud-topics.$$" && continue
    disposed "$ref" "$hs" || { level_line handoff-no-pr "$ref" "$hs" >> "$state/cloud-level-handoff.$$"; echo "cloud_relay: OWED handoff-no-pr $ref $hs"; }
  done < "$state/cloud-hrefs.$$"
  level_set handoff-no-pr "$state/cloud-level-handoff.$$"
  rm -f "$state/cloud-prs.$$" "$state/cloud-hrefs.$$" "$state/cloud-topics.$$"
}

pass() { # [--confirm] [--log FILE] [--loop [--interval N]]
  local every=120 loop=""
  while [ $# -gt 0 ]; do case $1 in
    --confirm) CONFIRM=1; shift;; --log) LOG=${2:-}; shift 2;; --loop) loop=1; shift;; --interval) every=${2:-}; shift 2;;
    *) echo "cloud_relay: unknown pass option '$1'" >&2; return 2;; esac; done
  case $every in ''|*[!0-9]*|0) echo "cloud_relay: --interval must be a positive number of seconds" >&2; return 2;; esac
  while :; do handoff_arm; probe_arm; [ -z "${CONFIRM:-}" ] || confirm_arm; [ -z "$loop" ] && return 0; sleep "$every"; done
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
  # push-verdict's stand-in pushes review/<pr> after its tip with bus.sh's tree (VERDICT.md,
  # evidence/), and prints `review/<pr> <commit>`, or $STUB_SAYS in place of the commit.
  export RELAY_T=$t; stub=$t/stub.sh; cat > "$stub" <<'EOF'
#!/bin/bash
echo "$1" >> "$RELAY_T/pushed"
s=$(mktemp -d "$RELAY_T/push.XXXXXX"); mkdir -p "$s/w/evidence"; cp "$2" "$s/w/VERDICT.md"; cp -R "$3"/. "$s/w/evidence/"
gd=$(git rev-parse --absolute-git-dir)
tree=$(cd "$s/w" && export GIT_DIR="$gd" GIT_INDEX_FILE="$s/index" GIT_WORK_TREE="$s/w" && git add -A -f . && git write-tree) || exit 1
p=$(git ls-remote origin "refs/heads/review/$1" | awk 'NF { print "-p " $1; exit }')
[ -z "$p" ] || git fetch -q origin "refs/heads/review/$1" || exit 1
c=$(git commit-tree "$tree" $p -m "verdict: #$1") && git push -q origin "$c:refs/heads/review/$1" || exit 1
echo "review/$1 ${STUB_SAYS:-$c}"
EOF
  chmod +x "$stub"; export HPO_RELAY_PUSH=$stub
  rtip() { git ls-remote origin "refs/heads/review/$1" | awk 'NF { print $1; exit }'; }
  mk() { # mk <pr> <subject-head> <verdict-head> <nonce-in-verdict> : push a probe ref for nonce n
    rm -rf "$t/pr"; throwaway_git_init "$t/pr" -q; mkdir "$t/pr/ev"; echo "$((c=c+1)) $3" > "$t/pr/ev/e"
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
  fstub=$t/fstub.sh; printf '#!/bin/sh\necho "BUS refused $1 $2: the poster refused: HTTP 502" >&2\necho\nexit 1\n' > "$fstub"; chmod +x "$fstub"
  HPO_RELAY_PUSH=$stub; HPO_RELAY_CONFIRM=$cstub; LOG=$t/relay.log; rm -f "$t/confirmed" "$LOG"
  mk 7 $h $h $n; CONFIRM=1
  chk "relay --confirm succeeds" 0 relay 7 $n $h
  chk "confirm ran with review/7's remote tip" 0 test "$(cat "$t/confirmed")" = "7 $(rtip 7)"
  chk "the log has a POSTED line" 0 grep -q "^POSTED .* 7 $(rtip 7)$" "$LOG"
  mk 7 $h $h ffffffffffffffffffffffffffffffff; rm -f "$t/confirmed"
  chk "a refused relay does not confirm" 2 relay 7 $n $h
  chk "and logs nothing new" 0 test "$(wc -l < "$LOG" | tr -d ' ')" = 1
  failpush=$t/failpush.sh; printf '#!/bin/sh\necho nope >&2\nexit 1\n' > "$failpush"; chmod +x "$failpush"
  mk 7 $h $h $n; HPO_RELAY_PUSH=$failpush
  chk "a failed push-verdict does not confirm" 1 relay 7 $n $h
  chk "confirm did not run after it" 0 test ! -f "$t/confirmed"
  HPO_RELAY_PUSH=$stub; HPO_RELAY_CONFIRM=$fstub
  chk "a failing confirm leaves the relay itself passed" 0 relay 7 $n $h
  chk "and logs OWED with the review sha and confirm's last output line, not /dev/null" 0 grep -q "^OWED .* 7 $(rtip 7) confirm failed: BUS refused 7 $(rtip 7): the poster refused: HTTP 502$" "$LOG"
  nosha=$t/nosha.sh; printf '#!/bin/sh\necho done\n' > "$nosha"; chmod +x "$nosha"
  mk 7 $h $h $n; HPO_RELAY_PUSH=$nosha; HPO_RELAY_CONFIRM=$cstub
  chk "a push-verdict that left review/7 without this verdict logs OWED" 0 relay 7 $n $h
  chk "and the OWED line carries a dash" 0 grep -q "^OWED .* 7 - review/7's remote tip [0-9a-f]* does not carry this verdict$" "$LOG"
  # the remote's tip is confirmed, not the commit push-verdict says it built
  mk 7 $h $h $n; HPO_RELAY_PUSH=$stub; rm -f "$t/confirmed"; out=$(STUB_SAYS=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb relay 7 $n $h 2>&1)
  chk "confirm takes review/7's remote tip, not the sha push-verdict printed" 0 test "$(cat "$t/confirmed")" = "7 $(rtip 7)"
  chk "and the relay reports that remote tip" 0 grep -q "review/7 remote tip $(rtip 7)$" <<< "$out"
  # a push refused non-fast-forward is re-applied on the fresh tip, never forced
  printf '#!/bin/sh\necho x >> "%s/nff.calls"\n[ "$(wc -l < "%s/nff.calls")" -gt 1 ] && exec "%s" "$@"\necho " ! [rejected]        c -> review/$1 (fetch first)" >&2\necho "bus: REFUSE: the push of review/$1 was refused" >&2\nexit 1\n' "$t" "$t" "$stub" > "$t/nff.sh"; chmod +x "$t/nff.sh"
  mk 7 $h $h $n; rm -f "$t/confirmed" "$t/nff.calls"; HPO_RELAY_PUSH=$t/nff.sh; out=$(relay 7 $n $h 2>&1); rc=$?
  chk "a push refused non-fast-forward is re-applied and the relay passes" 0 test "$rc $(wc -l < "$t/nff.calls" | tr -d ' ')" = "0 2"
  chk "and says it re-applied" 0 grep -q "refused non-fast-forward; re-applying" <<< "$out"
  chk "and confirms the fresh remote tip" 0 test "$(cat "$t/confirmed")" = "7 $(rtip 7)"
  printf '#!/bin/sh\necho x >> "%s/nff.calls"\n"%s" "$@" >/dev/null\necho " ! [rejected]        c -> review/$1 (non-fast-forward)" >&2\nexit 1\n' "$t" "$stub" > "$t/nff2.sh"; chmod +x "$t/nff2.sh"
  mk 7 $h $h $n; rm -f "$t/confirmed" "$t/nff.calls"; HPO_RELAY_PUSH=$t/nff2.sh; out=$(relay 7 $n $h 2>&1); rc=$?
  chk "a fresh tip that already carries this verdict is not re-applied" 0 test "$rc $(wc -l < "$t/nff.calls" | tr -d ' ')" = "0 1"
  chk "and says so" 0 grep -q "already carries this verdict: not re-applied" <<< "$out"
  chk "and confirms that tip" 0 test "$(cat "$t/confirmed")" = "7 $(rtip 7)"
  printf '#!/bin/sh\necho x >> "%s/nff.calls"\necho " ! [rejected]        c -> review/$1 (fetch first)" >&2\nexit 1\n' "$t" > "$t/nff3.sh"; chmod +x "$t/nff3.sh"
  mk 7 $h $h $n; rm -f "$t/nff.calls"; HPO_RELAY_PUSH=$t/nff3.sh
  chk "a push refused non-fast-forward every time gives up after three tries (rc 1)" 1 relay 7 $n $h
  chk "and pushed three times, no more" 0 test "$(wc -l < "$t/nff.calls" | tr -d ' ')" = 3
  printf '#!/bin/sh\necho x >> "%s/nff.calls"\necho nope >&2\nexit 1\n' "$t" > "$t/nff4.sh"; chmod +x "$t/nff4.sh"
  mk 7 $h $h $n; rm -f "$t/nff.calls"; HPO_RELAY_PUSH=$t/nff4.sh
  chk "null control: any other push failure is not re-applied" 1 relay 7 $n $h
  chk "and pushed once" 0 test "$(wc -l < "$t/nff.calls" | tr -d ' ')" = 1
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
  # a failed relay that is not a refusal (rc 1: a push, a fetch) is retried, at most HPO_RELAY_TRIES
  # times, then refused with its reason; the refusal is owed in the level file until disposed
  printf '#!/bin/sh\necho x >> "%s/flaky.calls"\n[ "$(wc -l < "%s/flaky.calls")" -gt "${FLAKY_FAILS:-0}" ] && exec "%s" "$@"\necho "error: RPC failed; HTTP 400 curl 22" >&2\nexit 1\n' "$t" "$t" "$stub" > "$t/flaky.sh"; chmod +x "$t/flaky.sh"
  HPO_RELAY_PUSH=$t/flaky.sh; LV=$LOG.level; rm -f "$t/flaky.calls" "$LV"; mk 5 $h $h $n; P5=$(git -C "$t/o.git" rev-parse refs/heads/probe/rev-5-${n:0:8})
  : >> "$t/state/cloud-relayed.refused"; FLAKY_FAILS=1 probe_arm >/dev/null 2>&1
  chk "a transient push failure is not refused" 1 grep -qxF "refs/heads/probe/rev-5-${n:0:8} $P5" "$t/state/cloud-relayed.refused"
  FLAKY_FAILS=1 probe_arm >/dev/null 2>&1
  chk "and the next pass retries and relays it" 0 grep -qxF "refs/heads/probe/rev-5-${n:0:8} $P5" "$t/state/cloud-relayed"
  rm -f "$t/flaky.calls"; mk 5 $h $h $n; P5=$(git -C "$t/o.git" rev-parse refs/heads/probe/rev-5-${n:0:8})
  for k in 1 2; do FLAKY_FAILS=9 probe_arm >/dev/null 2>&1; done; out=$(FLAKY_FAILS=9 probe_arm 2>/dev/null)
  chk "a push failing every pass is refused on the third try" 0 grep -qxF "refs/heads/probe/rev-5-${n:0:8} $P5" "$t/state/cloud-relayed.refused"
  chk "and prints REFUSED with the ref and its reason" 0 grep -q "^cloud_relay: REFUSED refs/heads/probe/rev-5-${n:0:8} $P5 error: RPC failed; HTTP 400 curl 22$" <<< "$out"
  FLAKY_FAILS=9 probe_arm >/dev/null 2>&1
  chk "and is not tried a fourth time" 0 test "$(wc -l < "$t/flaky.calls" | tr -d ' ')" = 3
  chk "the refusal is owed in the level file, once, with its reason" 0 test "$(grep -c "^OWED .* probe-refused refs/heads/probe/rev-5-${n:0:8} $P5 error: RPC failed; HTTP 400 curl 22$" "$LV")" = 1
  HPO_RELAY_PUSH=$stub; mk 5 $h $h ffffffffffffffffffffffffffffffff; P5B=$(git -C "$t/o.git" rev-parse refs/heads/probe/rev-5-${n:0:8}); probe_arm >/dev/null 2>&1
  chk "a refusal of the ref itself (rc 2) is refused at once, with its reason" 0 grep -q "^OWED .* probe-refused refs/heads/probe/rev-5-${n:0:8} $P5B cloud_relay: refused: nonce mismatch" "$LV"
  dispose refs/heads/probe/rev-5-${n:0:8} "$P5B" >/dev/null; probe_arm >/dev/null 2>&1
  chk "a disposed refusal is not owed" 1 grep -q "probe-refused" "$LV"
  # the tree the relay expects is the one the real bus.sh push-verdict builds (no stub)
  mk 5 $h $h $n; HPO_RELAY_PUSH=; HPO_RELAY_CONFIRM=$cstub; CONFIRM=1; rm -f "$t/confirmed"
  chk "with the real bus.sh push-verdict the relay passes" 0 relay 5 $n $h
  chk "and confirms the remote tip as carrying its verdict tree" 0 test "$(cat "$t/confirmed" 2>/dev/null)" = "5 $(rtip 5)"
  HPO_RELAY_PUSH=$stub; CONFIRM=
  # the probe arm's other refs: any probe/* that is not rev-* is OWED on every pass until disposed
  # The level is <log>.level, rewritten by each pass: appended to the log, every pass's copy
  # was replayed by the tick (2026-10-21), so "once per pass" is checked on the file itself.
  LOG=$t/probe.log; LV=$LOG.level; : > "$LOG"; rm -f "$LV"; mk 5 $h $h $n
  git -C "$t/o.git" update-ref refs/heads/probe/scan-x "$(git -C "$t/o.git" rev-parse refs/heads/probe/rev-5-${n:0:8})"; PX=$(git -C "$t/o.git" rev-parse refs/heads/probe/scan-x)
  probe_arm >/dev/null 2>&1
  chk "a non-rev probe ref is OWED in the level file with ref and sha" 0 grep -q "^OWED .* probe-ref refs/heads/probe/scan-x $PX$" "$LV"
  chk "a rev ref is relayed, not OWED (null control)" 1 grep -q "probe-ref refs/heads/probe/rev-" "$LV"
  printf 'OWED 2026-01-01T00:00:00Z handoff-no-pr refs/heads/handoff/keep %s\n' "$h" >> "$LV"
  probe_arm >/dev/null 2>&1; probe_arm >/dev/null 2>&1
  chk "after three passes it is owed once (a level is rewritten, never appended)" 0 test "$(grep -c "probe-ref refs/heads/probe/scan-x" "$LV")" = 1
  chk "and the probe arm leaves the handoff arm's level lines alone" 0 grep -q "handoff-no-pr refs/heads/handoff/keep " "$LV"
  chk "the event log carries no level line" 1 grep -q "probe-ref" "$LOG"
  git remote set-url origin "$t/absent.git"; probe_arm >/dev/null 2>&1; git remote set-url origin "$t/o.git"
  chk "a failed listing leaves the level as it was (unknown is not 'nothing owed')" 0 grep -q "probe-ref refs/heads/probe/scan-x $PX$" "$LV"
  chk "dispose refuses a ref outside probe/ and handoff" 2 dispose refs/heads/main "$PX"
  chk "dispose refuses a short sha" 2 dispose refs/heads/probe/scan-x "${PX%?}"
  chk "dispose takes a probe ref at its sha" 0 dispose refs/heads/probe/scan-x "$PX"
  chk "and drops its level line at once, not at the next pass" 1 grep -q "probe-ref refs/heads/probe/scan-x" "$LV"
  probe_arm >/dev/null 2>&1
  chk "a disposed ref is not owed" 1 grep -q "probe-ref" "$LV"
  mk 5 $h $h ffffffffffffffffffffffffffffffff
  git -C "$t/o.git" update-ref refs/heads/probe/scan-x "$(git -C "$t/o.git" rev-parse refs/heads/probe/rev-5-${n:0:8})"; PX2=$(git -C "$t/o.git" rev-parse refs/heads/probe/scan-x)
  probe_arm >/dev/null 2>&1
  chk "a disposed ref that moved is OWED again at its new sha" 0 grep -q "^OWED .* probe-ref refs/heads/probe/scan-x $PX2$" "$LV"
  X=$t/other.log; printf 'OWED 2026-01-01T00:00:00Z probe-ref refs/heads/probe/scan-y %s\n' "$h" > "$X.level"
  chk "dispose --log FILE (the CLI) takes the ref" 0 bash "$HERE/cloud_relay.sh" dispose --log "$X" refs/heads/probe/scan-y "$h"
  chk "and drops its line from the level beside that log" 1 grep -q scan-y "$X.level"
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
  chk "a well-formed hold file owes no refusal (null control)" 1 grep -q handoff-hold-malformed "$LOG.level"
  for hb in '41 99' 'abc' '41x' '0' '-1' '041' '41,99' ' 41' '41 # c'; do
    printf '%s\n' "$hb" > "$hf"; rm -f "$t/hupdated"; : > "$LOG"; ho=$(handoff_arm 2>&1)
    chk "a malformed hold file ('$hb') refuses the pass (rc 2)" 2 handoff_arm
    chk "and holds none: the PR is not updated" 0 test ! -e "$t/hupdated"
    chk "and holds all: no HELD line" 1 grep -q HELD <<< "$ho"
    chk "and names the refusal" 0 grep -q "refused: malformed hold file" <<< "$ho"
    # a refusal repeats every pass while the file stays malformed: a level, as #2547 made every such line
    chk "and owes handoff-hold-malformed in the level file" 0 grep -q "^OWED .* handoff-hold-malformed $hf -\$" "$LOG.level"
    chk "once after two passes (rewritten, never appended)" 0 test "$(grep -c handoff-hold-malformed "$LOG.level")" = 1
    chk "and the event log carries no refusal line" 1 grep -q handoff-hold-malformed "$LOG"
    chk "and held refuses it too" 2 held 41
    chk "and the CLI 'cloud_relay.sh held' refuses it (rc 2)" 2 bash "$HERE/cloud_relay.sh" held 41
  done
  # the held number is the unterminated last line, so the check fails when that line is dropped
  printf '99\n41' > "$hf"; ho=$(handoff_arm 2>&1)
  chk "a pass that reads the file well-formed drops the refusal from the level" 1 grep -q handoff-hold-malformed "$LOG.level"
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
  LV=$LOG.level; : > "$LOG"; rm -f "$LV"; mkref handoff/topic-b; OB=$(git -C "$t/pr" rev-parse HEAD)
  handoff_arm >/dev/null 2>&1
  chk "a handoff ref with no open PR is OWED in the level file" 0 grep -q "^OWED .* handoff-no-pr refs/heads/handoff/topic-b $OB$" "$LV"
  chk "a handoff ref with an open PR is not (null control)" 1 grep -q "handoff-no-pr refs/heads/handoff/topic-a " "$LV"
  chk "nor its handoff-body ref (null control)" 1 grep -q "handoff-no-pr refs/heads/handoff-body/topic-a " "$LV"
  handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
  chk "after three passes the no-PR ref is owed once (rewritten, never appended)" 0 test "$(grep -c "handoff-no-pr refs/heads/handoff/topic-b" "$LV")" = 1
  chk "the event log carries no level line" 1 grep -q "handoff-no-pr" "$LOG"
  git -C "$t/o.git" fetch -qf "$t/b" "HEAD:refs/heads/handoff-body/topic-c"; OC=$(git -C "$t/o.git" rev-parse refs/heads/handoff-body/topic-c)
  handoff_arm >/dev/null 2>&1
  chk "a handoff-body ref with no open PR is OWED" 0 grep -q "^OWED .* handoff-no-pr refs/heads/handoff-body/topic-c $OC$" "$LV"
  dispose refs/heads/handoff/topic-b "$OB" >/dev/null; dispose refs/heads/handoff-body/topic-c "$OC" >/dev/null
  handoff_arm >/dev/null 2>&1
  chk "disposed no-PR refs are not owed" 1 grep -q "handoff-no-pr" "$LV"
  git -C "$t/o.git" update-ref -d refs/heads/handoff-body/topic-c; git -C "$t/o.git" update-ref -d refs/heads/handoff/topic-b
  hc moved; mkref handoff/topic-b; OB2=$(git -C "$t/pr" rev-parse HEAD)
  handoff_arm >/dev/null 2>&1
  chk "a disposed no-PR ref that moved is OWED again" 0 grep -q "^OWED .* handoff-no-pr refs/heads/handoff/topic-b $OB2$" "$LV"
  failprs=$t/failprs.sh; printf '#!/bin/sh\nexit 1\n' > "$failprs"; chmod +x "$failprs"
  HPO_RELAY_PRS=$failprs handoff_arm >/dev/null 2>&1
  chk "a failed PR listing leaves the level as it was (unknown is not 'nothing owed')" 0 grep -q "handoff-no-pr refs/heads/handoff/topic-b $OB2$" "$LV"
  git -C "$t/o.git" update-ref -d refs/heads/handoff/topic-b; : > "$LOG"
  chk "pass --loop is the only loop (a bad interval is refused)" 2 pass --loop --interval 0
  HPO_RELAY_UPDATE=$ustub; rm -f "$t/updated" "$t/state/cloud-handoff-failed"; : > "$LOG"; printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"
  chk "pass runs both arms once and returns" 0 pass --log "$LOG"
  chk "the pass fired the handoff arm" 0 test -e "$t/updated"
  # the confirm arm (P-O): the ledger is written before confirm runs, so a failed confirm was never
  # retried ('already relayed'). pass --confirm confirms each review/<pr> tip the relay pushed and
  # bus.sh has not posted; posting is what the confirm stub records, as bus.sh does in posted-signed.
  printf '#!/bin/sh\n' > "$t/none.sh"; chmod +x "$t/none.sh"; HPO_RELAY_PRS=$t/none.sh; HPO_RELAY_PUSH=$stub
  git -C "$t/o.git" for-each-ref --format='%(refname)' refs/heads/review/ | while read -r r; do git -C "$t/o.git" update-ref -d "$r"; done
  cat > "$t/cf.sh" <<'EOF'
#!/bin/sh
echo "$1 $2" >> "$RELAY_T/cf.calls"
[ "$(grep -c "^$1 " "$RELAY_T/cf.calls")" -gt "${CF_FAILS:-0}" ] || { echo "bus: REFUSE: the push of verdict/$1 was refused: HTTP 502" >&2; exit 1; }
echo "$1 $(git rev-parse "$2^{tree}")" >> "$HPO_BUS_STATE/posted-signed"; echo "BUS posted $1 $2"
EOF
  chmod +x "$t/cf.sh"; export HPO_RELAY_CONFIRM=$t/cf.sh CF_FAILS=2; LOG=$t/confirm.log; LV=$LOG.level; : > "$LOG"; rm -f "$LV" "$t/cf.calls"
  calls() { grep -c "^$1 " "$t/cf.calls" 2>/dev/null; }
  mk 61 $h $h $n; printf '61 %s cloud %s\n' "$h" "$n" >> "$t/bus/dispatched"
  pass --confirm --log "$LOG" >/dev/null 2>&1
  chk "a relayed review whose confirm failed is owed on the level, with confirm's last stderr line" 0 grep -q "^OWED .* confirm-owed refs/heads/review/61 $(rtip 61) tries=1/3: bus: REFUSE: the push of verdict/61 was refused: HTTP 502$" "$LV"
  chk "and nothing is posted yet" 1 grep -q "^POSTED .* 61 " "$LOG"
  pass --confirm --log "$LOG" >/dev/null 2>&1
  chk "the next pass confirms it and logs POSTED" 0 grep -q "^POSTED .* 61 $(rtip 61)$" "$LOG"
  chk "and its level line is gone" 1 grep -q "review/61 " "$LV"
  pass --confirm --log "$LOG" >/dev/null 2>&1
  chk "a posted review is not confirmed again" 0 test "$(calls 61)" = 3
  CONFIRM=; mk 66 $h $h $n; printf '66 %s cloud %s\n' "$h" "$n" >> "$t/bus/dispatched"; pass --log "$LOG" >/dev/null 2>&1
  chk "pass without --confirm relays and runs no confirm arm (null control)" 0 test "$(calls 66)" = 0
  echo "66 $(git rev-parse "$(rtip 66)^{tree}")" >> "$t/bus/posted-signed"; pass --confirm --log "$LOG" >/dev/null 2>&1
  chk "a review already posted by hand (bus.sh's posted record) does nothing (null control)" 0 test "$(calls 66)" = 0
  chk "and owes nothing" 1 grep -q "review/66 " "$LV"
  rm -rf "$t/v62"; mkdir -p "$t/v62/ev"; echo "$h" > "$t/v62/ev/e"; printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$h" "$n" > "$t/v62/verdict.md"
  "$stub" 62 "$t/v62/verdict.md" "$t/v62/ev" >/dev/null; echo "refs/heads/probe/rev-62-${n:0:8} $h" >> "$t/state/cloud-relayed"
  pass --confirm --log "$LOG" >/dev/null 2>&1; pass --confirm --log "$LOG" >/dev/null 2>&1
  chk "an undispatched review is owed once in the level after two passes (null control)" 0 test "$(grep -c "^OWED .* confirm-owed refs/heads/review/62 $(rtip 62) undispatched: " "$LV")" = 1
  chk "and confirm never runs on it" 0 test "$(calls 62)" = 0
  dispose refs/heads/review/62 "$(rtip 62)" >/dev/null; pass --confirm --log "$LOG" >/dev/null 2>&1
  chk "a disposed review is not owed" 1 grep -q "review/62 " "$LV"
  printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$h" ffffffffffffffffffffffffffffffff > "$t/v62/verdict.md"
  "$stub" 64 "$t/v62/verdict.md" "$t/v62/ev" >/dev/null; echo "refs/heads/probe/rev-64-${n:0:8} $h" >> "$t/state/cloud-relayed"
  pass --confirm --log "$LOG" >/dev/null 2>&1
  chk "a review/<pr> tip the relay did not push is left to the orchestrator (null control)" 0 test "$(calls 64)" = 0
  chk "and owes nothing" 1 grep -q "review/64 " "$LV"
  CONFIRM=; CF_FAILS=99; mk 63 $h $h $n; printf '63 %s cloud %s\n' "$h" "$n" >> "$t/bus/dispatched"; pass --log "$LOG" >/dev/null 2>&1
  for k in 1 2 3 4; do pass --confirm --log "$LOG" >/dev/null 2>&1; done
  chk "a confirm failing every pass is tried HPO_RELAY_CONFIRM_TRIES (3) times, no more" 0 test "$(calls 63)" = 3
  chk "then stays owed once on the level with its last reason" 0 test "$(grep -c "^OWED .* confirm-owed refs/heads/review/63 $(rtip 63) tries=3/3, not retried; .*: bus: REFUSE: the push of verdict/63 was refused: HTTP 502$" "$LV")" = 1
  echo "63 $(git rev-parse "$(rtip 63)^{tree}")" >> "$t/bus/posted-signed"; pass --confirm --log "$LOG" >/dev/null 2>&1
  chk "a review posted by hand after that leaves the level" 1 grep -q "review/63 " "$LV"
  CONFIRM=; CF_FAILS=0; unset HPO_RELAY_CONFIRM; HPO_RELAY_PRS=$t/lister.sh; LOG=$t/pass.log
  # R10-PUSHER-REAP: a relay TERMed mid-update ends the update's whole tree. The
  # update stub records itself and a two-level sleep tree by pid, then blocks.
  printf '#!/bin/bash\necho $$ >> "%s/tpids"\nbash -c '"'"'sleep 30 & echo $! >> "$0"; wait'"'"' "%s/tpids" & echo $! >> "%s/tpids"\nwait\n' "$t" "$t" "$t" > "$t/tree.sh"; chmod +x "$t/tree.sh"
  local rp k tn live p
  stoprelay() { # <relay script> <pids wanted>: one pass, TERMed once the update's tree is up; sets tn and live
    rm -f "$t/state/cloud-handoff-failed"; : > "$t/tpids"; : > "$t/marks"; : > "$LOG"; printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"
    bash "$1" pass --log "$LOG" >/dev/null 2>&1 & rp=$!
    k=0; while [ "$(wc -l < "$t/tpids")" -lt "$2" ] && [ $k -lt 300 ]; do sleep 0.05; k=$((k + 1)); done
    tn=$(wc -l < "$t/tpids" | tr -d ' '); kill -TERM "$rp"
    # bounded: a relay waiting behind a foreground update would never end on its TERM
    k=0; while case $(ps -o stat= -p "$rp" 2>/dev/null | tr -d ' ') in ''|Z*) false;; esac && [ $k -lt 100 ]; do sleep 0.1; k=$((k + 1)); done
    kill -KILL "$rp" 2>/dev/null; wait "$rp" 2>/dev/null
    k=0; while :; do live=0; for p in $(cat "$t/tpids"); do kill -0 "$p" 2>/dev/null && live=$((live + 1)); done
      { [ "$live" = 0 ] || [ $k -ge 30 ]; } && break; sleep 0.1; k=$((k + 1)); done
    for p in $(cat "$t/tpids"); do kill -KILL "$p" 2>/dev/null; done; }
  HPO_RELAY_UPDATE=$t/tree.sh stoprelay "$HERE/cloud_relay.sh" 3
  chk "a relay TERMed mid-update leaves none of the update's tree alive (R10-PUSHER-REAP)" 0 test "$tn $live" = "3 0"
  # ... and the update stops first, as the reap's lead: its child G stands for update_pr.sh's
  # lock holder and marks a TERM it gets; the update, TERMed, waits 0.5 s, writes "early" when
  # G was TERMed beside it, then ends G -- so a lock is freed only after the push it guards.
  printf '#!/bin/bash\necho $$ >> "%s/tpids"\nbash -c '"'"'trap "echo G >> \"$0\"; exit 0" TERM; while :; do sleep 0.1; done'"'"' "%s/marks" & g=$!; echo $g >> "%s/tpids"\ntrap '"'"'sleep 0.5; grep -q G "%s/marks" && echo early >> "%s/marks"; kill $g; wait $g; exit 143'"'"' TERM\nwait\n' \
    "$t" "$t" "$t" "$t" "$t" > "$t/lead.sh"; chmod +x "$t/lead.sh"
  HPO_RELAY_UPDATE=$t/lead.sh stoprelay "$HERE/cloud_relay.sh" 2
  chk "a relay TERMed mid-update TERMs the update alone first, so it ends its own child before anything else does" \
    0 test "$tn $live $(tr '\n' ' ' < "$t/marks")" = "2 0 G "
  # The production route, no HPO_RELAY_UPDATE: a copy of the relay and the real pr_args.sh beside
  # an update_pr.sh that is the lead stub, so the relay's own `bash "$HERE/update_pr.sh"` runs it.
  mkdir -p "$t/seat" && cp "$HERE/cloud_relay.sh" "$HERE/pr_args.sh" "$t/seat/" && cp "$t/lead.sh" "$t/seat/update_pr.sh"
  HPO_RELAY_UPDATE= stoprelay "$t/seat/cloud_relay.sh" 2
  chk "with no stub, the relay runs update_pr.sh beside it as the lead, asynchronously: a TERM ends it in that order" \
    0 test "$tn $live $(tr '\n' ' ' < "$t/marks")" = "2 0 G "
  rm -rf "$t"
  echo "cloud_relay self-test: $((ok+bad)) checks, $bad failed"; [ "$bad" = 0 ]
}

case ${1:-} in
  --self-test) self_test; exit $?;;
  held) shift; held "$@"; exit $?;;
  --watch) shift; watch "$@"; exit $?;;
  pass) shift; pass "$@"; exit $?;;
  dispose) shift; [ "${1:-}" = --log ] && { LOG=${2:-}; shift 2; }; dispose "$@"; exit $?;;
  --confirm|--log) while [ $# -gt 0 ]; do case $1 in --confirm) CONFIRM=1; shift;; --log) LOG=${2:-}; shift 2;; *) break;; esac; done
    [ $# = 3 ] || { echo "usage: cloud_relay.sh [--confirm] [--log FILE] <pr> <nonce> <head40>" >&2; exit 2; }; relay "$1" "$2" "$3"; exit $?;;
  ''|-*) echo "usage: cloud_relay.sh <pr> <nonce> <head40> | pass [--confirm] [--log FILE] [--loop [--interval N]] | dispose [--log FILE] <ref> <sha40> | --watch [--interval N] [--once] [--confirm] [--log FILE] | --self-test" >&2; exit 2;;
  *) [ $# = 3 ] || { echo "usage: cloud_relay.sh <pr> <nonce> <head40>" >&2; exit 2; }; relay "$1" "$2" "$3"; exit $?;;
esac
