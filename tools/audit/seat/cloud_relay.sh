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
# probe/rev-* is OWED until `dispose <ref> <sha>` records it in the ledger's
# dispositions.tsv (ledger.py): a level, not a diff, so a missed line is repeated rather
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
# THE LEDGER. Every obligation the relay writes goes through ledger.py, whose
# stores live beside the log (--log FILE, default <state>/cloud-relay.log): an
# event is opened there keyed on kind, PR and sha, and `dispose` writes its
# dispositions.tsv. A push-verdict that PASSED opens `verdict-unposted <pr>
# <head> <first line>`, closed only when the tick reads that comment back.
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
# that tip carries this verdict's tree (confirm takes only a tip), and on success
# appends `POSTED <utc> <pr> <review-sha>` to the log, a journal line that closes
# nothing (a relayed claim is not a read-back). A failure prints
#   cloud_relay: UNPOSTED #<pr>: <why>   (<why> carries confirm's last output line)
# and the verdict stays owed in the ledger. confirm never runs after a refused
# relay or a failed push-verdict, and writes nothing for them (a refusal prints
# its reason, and --watch's .refused file holds it). HPO_RELAY_CONFIRM replaces
# the confirm command (the self-test's stub).
#
# `pass` is the orchestrator's whole beat, ONE entry point a driver calls once
# (and takes over relay_watch.sh, which was session-local). A pass runs two arms,
# and with --confirm a third, in the order probe, confirm, handoff (R10-RELAY-ARM-ORDER).
#   handoff arm: for every OPEN pull request, topic = headRefName less a leading
#     `fix/` and a trailing `-pr`. If handoff-body/<topic> and handoff/<topic>
#     exist and handoff/<topic> is NOT an ancestor of the PR head, it runs
#     update_pr.sh <branch> <code-sha> <body> <issues> (issues = the body's
#     closing keywords) from its own tools tree levelled to origin/main, never
#     from this checkout (tools_level below; dirty or busy is refused by name and
#     retried next pass), then approve_held_runs.sh on the branch, then
#     `bus.sh dispatch <pr> <new head> cloud`, and opens `reviewer-fire <pr>
#     <head40> nonce=<nonce>` in the ledger (a failed approve or dispatch opens
#     `approve-held-runs` or `dispatch` instead): firing the cloud reviewer stays
#     with the orchestrator. It only
#     UPDATES an existing PR (the soft cap counts roster groups in progress at
#     dispatch; an update neither opens a PR nor enters WIP).
#     A handoff already contained in its PR, or with no body ref, does nothing;
#     a topic whose update failed is noted in `<ledger>.handoff-failed` by
#     `<topic> <code-sha> <body-sha>` and retried only when handoff/<topic> or its body moves, owed
#     meanwhile as `OWED <utc> handoff-update <ref> <sha> <why>` in <log>.level, <why>
#     kept in `<ledger>.handoff-failed.why`; a body whose `Code:` trailer names
#     another head is `handoff-body-stale` (retried). A refusal of a body-content step (unpinned sites, carry,
#     figures, the body contract) stays recorded until the body ref moves; any other (ancestry reds, ci predict)
#     reruns after HPO_RELAY_RETRY_BACKOFF (default 1800 s), three runs at most (`<ledger>.handoff-failed.tries`),
#     then stays recorded and owed as above (carry 12). The
#     `handoff-no-pr` lines there are `ledger.py level`'s fold of every
#     handoff/* and handoff-body/* ref: owed unless its topic has an open PR,
#     it is disposed at its sha, or main already carries the change (`ledger.py
#     landed`, the classifier bus.sh orphans asks too), one line per topic
#     (a body ref rides its code ref's), each with its tip's commit time; rewritten every pass, and
#     a failed PR listing or ledger read leaves them as they were.
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
#     FREEZE. A PR whose live head is under review is not updated either: a
#     merge verdict at that head on verdict/<pr> (HELD-VERDICT), or a review of
#     that head in flight with no verdict at it yet (HELD-REVIEW: bus.sh's
#     dispatch record of the PR at that head, the worker registry, and only it;
#     its nonce prefix and time are the evidence). A blocked verdict, or one
#     naming an older head, freezes nothing. Each prints
#       cloud_relay: HELD-<why> #<pr> <handoff tip>[ dispatch=<nonce8> at=<utc>] (...)
#     once per pass and is `OWED <utc> handoff-held <ref> <tip> #<pr> <why>` in
#     <log>.level; `<state>/cloud-handoff-release` (the hold grammar, the
#     orchestrator's) releases a listed PR from the freeze, never from the
#     hold. review_freeze below says why each case is what it is.
#     HELD-BODY: `cloud_relay: HELD-BODY #<pr> <tip8>`: the handoff is ahead of a
#     body that does not name its first 8 chars; retried next pass. Levels
#     `handoff-body-unapplied` (BODY-ONLY line) and `handoff-hold-stale` (hold line
#     whose PR is not open) are published before the serial loops.
#   probe arm: the --watch pass above (probe/rev-* -> relay -> confirm; other
#     probe refs OWED until disposed).
#   relay() refuses (rc 2, naming both) ev/ names differing only in case, and
#     pushes nothing when review/<pr> already carries the probe's tree (delivered
#     guard: recorded). Each pass prints `state dir <dir>, ledger ..., log ...`.
#   stuck and no-return arms: level lines only (THE STUCK ANDON, THE NO-RETURN LINE below).
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
#     tips are noted in `<ledger>.confirm-done`, so a pass fetches only new ones. A tip whose PR
#     is not open (this pass's open-PR listing; a verdict posts only on an open PR) prints
#     `cloud_relay: confirm skip #<pr>: not open` once and is settled, owed nothing (P332); a failed
#     listing skips nothing.
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
unposted() { echo "cloud_relay: UNPOSTED #$1: $3 (the verdict stays owed in the ledger)" >&2; }
# Every obligation the relay writes goes through ledger.py (R10-ORCH-LEDGER): an event is
# opened there, keyed on kind, PR and sha, and the log keeps only the POSTED journal.
ledger() { python3 -I "$HERE/ledger.py" --log "$(relay_log)" "$@"; }
ledger_open() { ledger open "$@" >/dev/null || echo "cloud_relay: the ledger refused $1 for #$2" >&2; echo "cloud_relay: OWED $1 #$2 $3" >&2; }
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

ev_case_collision() { # <commit> -> "<a> and <b>" for the first two names under ev/ that fold together; reads only the commit's name list
  git -c core.quotepath=off ls-tree -r --name-only "$1" -- ev | awk '{
    n = split($0, p, "/"); q = ""
    for (i = 1; i <= n; i++) { q = (i == 1 ? p[i] : q "/" p[i]); k = tolower(q)
      if ((k in s) && s[k] != q) { print s[k] " and " q; exit } s[k] = q } }'
}

pending_red_seen() { # <state dir> <ref sha head> -> the epoch of that key's first RED read, nothing when none (R10-REVIEW-DISPATCH-RESIDUE)
  awk -v k="$2 " 'index($0, k) == 1 { print substr($0, length(k) + 1); exit }' "$1/cloud-pending-red" 2>/dev/null; }
pending_red_clear() { # <state dir> <ref sha head>: a check ran (WAIT or GREEN), so the next RED starts a new clock
  [ -f "$1/cloud-pending-red" ] && { awk -v k="$2 " 'index($0, k) != 1' "$1/cloud-pending-red" > "$1/cloud-pending-red.$$"; mv -f "$1/cloud-pending-red.$$" "$1/cloud-pending-red"; }; return 0; }

relay() { # <pr> <nonce> <head> [<topic>]: with a topic, the verdict was returned at the handoff (probe/revt-<topic>-<n8>, subject `verdict <topic> <head>`)
  local pr=$1 nonce=$2 head=$3 topic=${4:-} ref sha d subj first state led key=$1
  case $pr in ''|*[!0-9]*) die "pr '$pr' is not a number"; return;; esac
  printf '%s' "$head" | grep -Eq '^[0-9a-f]{40}$' || { die "head must be 40 lowercase hex"; return; }
  printf '%s' "$nonce" | grep -Eq '^[0-9a-f]{32}$' || { die "nonce must be 32 hex"; return; }
  ref=refs/heads/probe/rev-$pr-$(printf '%s' "$nonce" | cut -c1-8)
  [ -z "$topic" ] || { key=$topic; ref=refs/heads/probe/revt-$topic-$(printf '%s' "$nonce" | cut -c1-8); }  # mut:relaytopic
  sha=$(git ls-remote origin "$ref" | awk 'NF { print $1; exit }')
  [ -n "$sha" ] || { die "no $ref on origin"; return; }
  state=${HPO_STATE_DIR:-$HOME/.local/state/hpo}; led=$state/cloud-relayed
  if [ -f "$led" ] && grep -qxF "$ref $sha" "$led"; then die "$ref at $sha was already relayed"; return; fi
  git fetch -q origin "$ref" || { echo "cloud_relay: could not fetch $ref" >&2; return 1; }
  # Names under ev/ that differ only in case: a case-insensitive filesystem (the orchestrator's
  # macOS) unpacks one over the other, and push-verdict then refuses "no file names the head" --
  # a cause that reads as a missing file (PR 3061). Refused here by name, on the first tick line,
  # from the commit's own name list and BEFORE anything is extracted: on such a filesystem the
  # unpack itself dies (mkdir/write on the colliding path, rc 1) before any later check could refuse.
  # Every ancestor path is compared too, so a file ev/A and a directory ev/a collide as well.
  local dup; dup=$(ev_case_collision "$sha")
  [ -z "$dup" ] || { die "ev/ holds names that differ only in case ($dup); a case-insensitive checkout keeps one, so rename them apart"; return; }
  d=$(mktemp -d "${TMPDIR:-/tmp}/cloud_relay.XXXXXX") || return 1
  git archive "$sha" | tar -x -C "$d" || { die "could not read $sha"; return; }
  subj=$(git log -1 --format=%s "$sha")
  [ "$subj" = "verdict $key $head" ] || { die "the ref's commit says '$subj', not 'verdict $key $head': another PR or head"; return; }
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
  # PENDING-CI (R10-CLOUD-POOL carry 5, moved to R10-DISPATCH-AT-HANDOFF): a reviewer whose review is complete
  # while CI at the head is still pending returns the verdict with a `pending-ci: <why>` line instead of waiting
  # without bound. The relay posts it only once classify reads the head GREEN; WAIT holds it (rc 75, one line
  # each pass, retried). A PR head that moved is asked of review_carry (--verdict-only): CARRY classifies the LIVE
  # head and posts on GREEN (the verdict names the drafted head, as a handoff verdict does), anything else refuses
  # the draft, with the head it was drafted at and the head now. RED holds as WAIT does (a red the branch did not
  # cause clears when main is merged, or when a judged run ends, with no fixer work: PRs 3425 and 3430) and is
  # refused only after HPO_RELAY_PENDING_RED_SECS (default 21600) since the first RED read at that head, no
  # check having run in between (a WAIT or GREEN read clears the record). Both refusals are OWED re-dispatch.
  if grep -q '^pending-ci: ' "$d/verdict.md"; then  # mut:pendingci
    local live cls crc cl=$head carried= rkey redsecs=${HPO_RELAY_PENDING_RED_SECS:-21600} seen reds
    live=$(if [ -n "${HPO_RELAY_PRHEAD:-}" ]; then "$HPO_RELAY_PRHEAD" "$pr"; else gh pr view "$pr" -R "${HPO_RELAY_REPO:-tvofi/heatpump_optimizer}" --json headRefOid --jq .headRefOid; fi 2>/dev/null)
    if ! printf '%s' "$live" | grep -Eq '^[0-9a-f]{40}$'; then echo "cloud_relay: #$pr's head could not be read, so its pending-ci draft is held" >&2; return 75; fi
    case $redsecs in ''|*[!0-9]*) echo "cloud_relay: HPO_RELAY_PENDING_RED_SECS must be seconds; the pending-ci draft is held" >&2; return 75;; esac
    if [ "$live" != "$head" ]; then
      git fetch -q origin "$head" "$live" 2>/dev/null || :
      if ${HPO_RELAY_CARRY:-python3 -I "$HERE/review_carry.py"} "$head" "$live" --verdict-only >/dev/null 2>&1; then  # mut:pendingcarry
        cl=$live; carried=" (the verdict carried from ${head:0:12}: review_carry CARRY)"
      else
        echo "cloud_relay: OWED re-dispatch #$pr $live"
        die "the head moved under a pending-ci draft: drafted at $head, #$pr is at $live; it is not posted"; return  # mut:pendinghead
      fi
    fi
    rkey="$ref $sha $cl"
    cls=$(${HPO_RELAY_CLASSIFY:-python3 -I "$HERE/merge_train.py" classify} "$cl" --repo "${HPO_RELAY_REPO:-tvofi/heatpump_optimizer}" --pr "$pr" 2>&1); crc=$?
    case $crc in
      0|4) pending_red_clear "$state" "$rkey"; echo "cloud_relay: pending-ci draft for #$pr: CI at $cl is now GREEN (classify rc $crc)$carried; relaying" ;;
      3) pending_red_clear "$state" "$rkey"; echo "cloud_relay: HELD-PENDING-CI #$pr $cl: $(sed -n 's/^WAIT *//p' <<< "$cls" | head -n 1) (classify WAIT); the draft posts when CI is green"; return 75 ;;
      1) reds=$(sed -n 's/^RED *//p' <<< "$cls" | head -n 1); seen=$(pending_red_seen "$state" "$rkey")
        if [ -n "$seen" ] && [ $(($(date +%s) - seen)) -ge "$redsecs" ]; then  # mut:pendingredbound
          echo "cloud_relay: OWED re-dispatch #$pr $cl"
          die "CI has read RED at $cl since $(date -u -d "@$seen" +%FT%TZ) with no check running ($reds; classify RED): a pending-ci draft is not posted over a red"; return
        fi
        [ -n "$seen" ] || { mkdir -p "$state" && printf '%s %s\n' "$rkey" "$(date +%s)" >> "$state/cloud-pending-red"; }
        echo "cloud_relay: HELD-PENDING-CI-RED #$pr $cl: $reds (classify RED)"; return 75 ;;  # mut:pendingredhold
      *) echo "cloud_relay: classify could not read $cl (rc $crc): $(last_line "$cls"); the pending-ci draft is held" >&2; return 75 ;;
    esac
  fi
  local out sha2 wt tip tries=0
  wt=$(verdict_tree "$d/verdict.md" "$d/ev") || { echo "cloud_relay: could not build the verdict's tree" >&2; return 1; }
  # DELIVERED GUARD (R10-RELAY-REPLAY): a ledger that is not the one that recorded this probe (a
  # loop restarted without HPO_STATE_DIR read the stale default) made every probe look unseen, and
  # 93 were replayed as 92 commits on 56 review refs. Whether review/<pr> already carries this
  # verdict's tree is asked of the remote, so correctness does not depend on which ledger is read.
  # The tree list goes to a file: a pipe into an early-exiting reader breaks under pipefail.
  if tip=$(review_tip "$pr") && [ -n "$tip" ] && git log --format=%T "$tip" > "$d/rtrees" 2>/dev/null && grep -qxF "$wt" "$d/rtrees"; then
    mkdir -p "$state" && echo "$ref $sha" >> "$led"
    echo "cloud_relay: review/$pr already carries this verdict's tree (tip ${tip:0:12}); $ref $sha recorded as relayed, nothing pushed"
    return 0
  fi
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
  ledger_open verdict-unposted "$pr" "$head" "$first"
  # The remote's tip, not the commit push-verdict built here: confirm takes only a tip (bus.sh
  # unpack), and it is confirmed only when it carries this verdict's tree.
  sha2=-; tip=$(review_tip "$pr") && [ -n "$tip" ] && [ "$(git rev-parse "$tip^{tree}")" = "$wt" ] && sha2=$tip
  echo "cloud_relay: review/$pr remote tip ${tip:-none}"
  if [ -n "${CONFIRM:-}" ]; then
    if [ "$sha2" = - ]; then unposted "$pr" - "review/$pr's remote tip ${tip:-none} does not carry this verdict"
    else out=$(confirm_run "$pr" "$sha2" 2>&1) && posted "$pr" "$sha2" || unposted "$pr" "$sha2" "confirm failed: $(last_line "$out")"; fi
  fi
  echo "cloud_relay: relayed $ref $sha; next: bus.sh confirm $pr $sha2"
}

disposed() { ledger disposed "$1" "$2"; }  # the orchestrator ran `dispose` on this ref at this sha

dispose() { # dispose <ref> <sha>: a probe or handoff ref at that sha is handled; it is OWED again once it moves
  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo}
  [ $# = 2 ] || { echo "usage: cloud_relay.sh dispose <ref> <sha40>" >&2; return 2; }
  case $1 in refs/heads/probe/?*|refs/heads/handoff/?*|refs/heads/handoff-body/?*|refs/heads/review/?*) ;; *) die "'$1' is not a refs/heads/probe/, handoff/, handoff-body/ or review/ ref"; return;; esac
  printf '%s' "$2" | grep -Eq '^[0-9a-f]{40}$' || { die "sha must be 40 lowercase hex"; return; }
  ledger dispose "$1" "$2" relay-dispose >/dev/null || return $?
  local lv; lv=$(relay_log).level   # owed no longer: off the level now, not at the next pass
  if [ -f "$lv" ]; then awk -v r="$1" -v s="$2" '!($4 == r && $5 == s)' "$lv" > "$lv.$$" && mv -f "$lv.$$" "$lv"; fi
  echo "cloud_relay: disposed $1 $2"
}

probe_arm() { # one pass over every probe/* ref: rev-* relays each unseen ref+sha, any other is OWED until disposed
  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} led bus sha ref k pr n8 rec nonce head rc why n max=${HPO_RELAY_TRIES:-3}
  led=$state/cloud-relayed; bus=${HPO_BUS_STATE:-$HOME/.zcode/bus}
  # a failed listing leaves the level as it was: unknown is not "nothing owed"
  git ls-remote origin 'refs/heads/probe/*' > "${TMPDIR:-/tmp}/cloud_relay_ls.$$" || { echo "cloud_relay: ls-remote failed; will retry" >&2; rm -f "${TMPDIR:-/tmp}/cloud_relay_ls.$$"; return 0; }
  mkdir -p "$state"; : > "$state/cloud-level-probe.$$"; : > "$state/cloud-level-refused.$$"; : > "$state/cloud-torelay.$$"; : > "$state/cloud-level-vheld.$$"
  # The levels are published before the serial relay loop, which is slow (a fetch and a push per ref):
  # written only at its end they were missing for a whole pass (2026-10-22, R10-RELAY-SWEEP carry 2).
  while read -r sha ref; do
    [ -n "$ref" ] || continue
    case $ref in refs/heads/probe/rev-*|refs/heads/probe/revt-*) ;;
      *) disposed "$ref" "$sha" || { level_line probe-ref "$ref" "$sha" >> "$state/cloud-level-probe.$$"; echo "cloud_relay: OWED probe-ref $ref $sha"; }; continue;; esac
    if [ -f "$led" ] && grep -qxF "$ref $sha" "$led"; then continue; fi
    if disposed "$ref" "$sha"; then continue; fi  # mut:probedispose -- handled by the orchestrator at this sha; relayed again once it moves
    if [ -f "$led.refused" ] && grep -qxF "$ref $sha" "$led.refused"; then
      # a refusal is owed until disposed; one recorded before reasons were kept stays silent
      why=$(awk -v r="$ref" -v s="$sha" '$1 == r && $2 == s { $1 = $2 = ""; w = substr($0, 3) } END { print w }' "$led.refused-why" 2>/dev/null)
      [ -z "$why" ] || disposed "$ref" "$sha" || level_line probe-refused "$ref" "$sha" "$why" >> "$state/cloud-level-refused.$$"
      continue
    fi
    echo "$sha $ref" >> "$state/cloud-torelay.$$"
  done < "${TMPDIR:-/tmp}/cloud_relay_ls.$$"
  cp "$state/cloud-level-probe.$$" "$state/cloud-level-probe.$$.k"; cp "$state/cloud-level-refused.$$" "$state/cloud-level-refused.$$.k"
  level_set probe-ref "$state/cloud-level-probe.$$.k"; level_set probe-refused "$state/cloud-level-refused.$$.k"
  while read -r sha ref; do
    [ -n "$ref" ] || continue
    case $ref in refs/heads/probe/revt-*)
      topic_verdict "$sha" "$ref" "$state/cloud-level-vheld.$$" "$state/cloud-level-refused.$$"; continue ;;
    esac
    k=${ref#refs/heads/probe/rev-}; pr=${k%%-*}; n8=${k#*-}
    rec=$(awk -v p="$pr" -v n="$n8" '$1 == p && index($4, n) == 1 { print $2, $4 }' "$bus/dispatched" 2>/dev/null | tail -n 1)
    if [ -z "$rec" ]; then echo "$(date -u +%FT%TZ) cloud_relay: $ref $sha has no dispatch record in $bus; leaving it" >&2; continue; fi
    head=${rec%% *}; nonce=${rec#* }
    echo "$(date -u +%FT%TZ) cloud_relay: relaying $ref $sha"
    relay "$pr" "$nonce" "$head" 2> "$state/cloud-relay-err.$$"; rc=$?; cat "$state/cloud-relay-err.$$" >&2
    [ $rc -ne 0 ] || continue
    [ $rc -ne 75 ] || continue  # a pending-ci draft held: nothing recorded, so the next pass asks again
    # rc 2 is a refusal of the ref itself, final; any other failure (a push, a fetch) is
    # retried on later passes, at most HPO_RELAY_TRIES times in all, then refused with its reason.
    why=$(last_line "$(cat "$state/cloud-relay-err.$$")"); echo "$ref $sha" >> "$led.tries"
    n=$(grep -cxF "$ref $sha" "$led.tries")
    if [ $rc = 2 ] || [ "$n" -ge "$max" ]; then
      echo "$ref $sha" >> "$led.refused"; echo "$ref $sha $why" >> "$led.refused-why"
      level_line probe-refused "$ref" "$sha" "$why" >> "$state/cloud-level-refused.$$"; echo "cloud_relay: REFUSED $ref $sha $why"
    else echo "cloud_relay: relay of $ref $sha failed (rc=$rc, try $n of $max); the next pass retries: $why" >&2; fi
  done < "$state/cloud-torelay.$$"
  rm -f "${TMPDIR:-/tmp}/cloud_relay_ls.$$" "$state/cloud-relay-err.$$" "$state/cloud-torelay.$$"
  level_set probe-ref "$state/cloud-level-probe.$$"; level_set probe-refused "$state/cloud-level-refused.$$"
  level_set handoff-verdict-held "$state/cloud-level-vheld.$$"
}

# A verdict returned at the handoff (Carry 0; bus.sh dispatch-handoff). Three outcomes, none a post unless the
# review carries. HELD: no pull request has opened for the topic (bus.sh rekey writes `<topic> <head> <pr>` to
# <bus>/rekeyed when open_pr.sh opens one), so the verdict is reported on the level every pass and never posted:
# a topic that never opens a PR stays reported. CARRY: review_carry.py answers CARRY for handoff-head..PR-head (the
# merge of main and the delivery row), and the verdict is relayed and confirmed as any other, at the handoff head
# it names. STALE: the PR head holds a commit of the branch's own (a conflict resolution, a code edit), so the
# verdict is not posted, the ref is refused with the reason (owed until disposed), and the PR is re-dispatched at
# its head by the ordinary `bus.sh dispatch <pr> <head>`. An unreadable PR head or range retries next pass.
topic_verdict() { # <sha> <ref> <held-level-file> <refused-level-file>
  local sha=$1 ref=$2 vheld=$3 vref=$4 k topic n8 rec head nonce pr prhead rc why out
  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} led bus=${HPO_BUS_STATE:-$HOME/.zcode/bus}
  led=$state/cloud-relayed
  k=${ref#refs/heads/probe/revt-}; n8=${k##*-}; topic=${k%-*}
  rec=$(awk -v t="topic:$topic" -v n="$n8" '$1 == t && index($4, n) == 1 { print $2, $4 }' "$bus/dispatched" 2>/dev/null | tail -n 1)
  [ -n "$rec" ] || { echo "$(date -u +%FT%TZ) cloud_relay: $ref $sha has no handoff dispatch record in $bus; leaving it" >&2; return 0; }
  head=${rec%% *}; nonce=${rec#* }
  pr=$(awk -v t="$topic" -v h="$head" '$1 == t && $2 == h { p = $3 } END { print p }' "$bus/rekeyed" 2>/dev/null)
  if [ -z "$pr" ]; then  # mut:topicheld
    echo "cloud_relay: HELD-NOPR $ref $sha: no pull request has opened for $topic, so its verdict is held, never posted"
    level_line handoff-verdict-held "$ref" "$sha" "topic $topic: no pull request opened" >> "$vheld"
    return 0
  fi
  prhead=$(if [ -n "${HPO_RELAY_PRHEAD:-}" ]; then "$HPO_RELAY_PRHEAD" "$pr"; else gh pr view "$pr" -R "${HPO_RELAY_REPO:-tvofi/heatpump_optimizer}" --json headRefOid --jq .headRefOid; fi 2>/dev/null)
  printf '%s' "$prhead" | grep -Eq '^[0-9a-f]{40}$' || { echo "cloud_relay: #$pr's head could not be read; $ref $sha retries next pass" >&2; return 0; }
  git fetch -q origin "$head" "$prhead" 2>/dev/null || :
  out=$(${HPO_RELAY_CARRY:-python3 -I "$HERE/review_carry.py"} "$head" "$prhead" --verdict-only 2>&1); rc=$?
  if [ "$rc" = 2 ]; then echo "cloud_relay: $ref $sha: cannot read $head..$prhead ($(last_line "$out")); retries next pass" >&2; return 0; fi
  if [ "$rc" != 0 ]; then  # mut:topiccarry
    why="verdict at handoff head ${head:0:12} is stale against #$pr's head ${prhead:0:12} (review_carry: FRESH-REVIEW); re-dispatch: bus.sh dispatch $pr $prhead <reviewer>"
    echo "$ref $sha" >> "$led.refused"; echo "$ref $sha $why" >> "$led.refused-why"
    level_line probe-refused "$ref" "$sha" "$why" >> "$vref"; echo "cloud_relay: HELD-STALE $ref $sha $why"
    return 0
  fi
  echo "$(date -u +%FT%TZ) cloud_relay: relaying $ref $sha at #$pr (handoff head carries to ${prhead:0:12})"
  relay "$pr" "$nonce" "$head" "$topic"; rc=$?
  [ "$rc" = 0 ] || [ "$rc" = 75 ] && return 0
  echo "$ref $sha" >> "$led.tries"
  if [ "$rc" = 2 ] || [ "$(grep -cxF "$ref $sha" "$led.tries")" -ge "${HPO_RELAY_TRIES:-3}" ]; then
    why="relay of the held handoff verdict failed (rc=$rc)"
    echo "$ref $sha" >> "$led.refused"; echo "$ref $sha $why" >> "$led.refused-why"
    level_line probe-refused "$ref" "$sha" "$why" >> "$vref"; echo "cloud_relay: REFUSED $ref $sha $why"
  fi
}

confirm_arm() { # one pass over review/* tips the relay delivered: confirm each not yet posted, owed on the level until it is
  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} led bus sha ref pr tree v nonce head n why lv max=${HPO_RELAY_CONFIRM_TRIES:-3}
  led=$state/cloud-relayed; bus=${HPO_BUS_STATE:-$HOME/.zcode/bus}; lv=$(relay_log).level
  git ls-remote origin 'refs/heads/review/*' > "$state/cloud-reviews.$$" || { echo "cloud_relay: ls-remote of review/* failed; will retry" >&2; rm -f "$state/cloud-reviews.$$"; return 0; }
  : > "$state/cloud-level-confirm.$$"
  # P332: a verdict posts only on an open PR (app_comment.sh), so one on a closed or merged PR is
  # skipped, not owed. The open PRs are this pass's one listing (pass() takes it ahead of every arm), else one listing here; a
  # failed listing skips nothing (every tip stays owed as before).
  local open=""
  if [ -f "$state/cloud-prs-open.$$" ]; then open=$(cut -f1 "$state/cloud-prs-open.$$"); open=${open:-none}
  else open=$( { if [ -n "${HPO_RELAY_PRS:-}" ]; then "$HPO_RELAY_PRS"
    else gh pr list -R "${HPO_RELAY_REPO:-tvofi/heatpump_optimizer}" --state open --limit 100 --json number,headRefName,headRefOid \
      -q '.[] | [.number, .headRefName, .headRefOid] | @tsv'; fi; } | cut -f1) && open=${open:-none} || open=""; fi
  while read -r sha ref; do
    pr=${ref#refs/heads/review/}; case $pr in ''|*[!0-9]*) continue;; esac
    # only what this relay delivered: a reviewer of the orchestrator's own waits for its thread read
    grep -q "^refs/heads/probe/rev-$pr-" "$led" 2>/dev/null || continue
    grep -qxF "$pr $sha" "$led.confirm-done" 2>/dev/null && continue
    if [ -n "$open" ] && ! grep -qxF "$pr" <<< "$open"; then  # mut:closedskip
      echo "cloud_relay: confirm skip #$pr: not open"; echo "$pr $sha" >> "$led.confirm-done"; continue
    fi
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
release_file() { echo "${HPO_STATE_DIR:-$HOME/.local/state/hpo}/cloud-handoff-release"; }
hold_list() { # [file] the PR numbers a hold-grammar file lists, one per line; rc 2 when it is malformed. No file = none.
  local f=${1:-$(hold_file)} l; [ -e "$f" ] || return 0
  [ -f "$f" ] && [ -r "$f" ] || { echo "cloud_relay: refused: malformed hold file $f (not a readable file)" >&2; return 2; }
  while IFS= read -r l || [ -n "$l" ]; do
    case $l in ''|'#'*) ;; *[!0-9]*|0*) echo "cloud_relay: refused: malformed hold file $f: '$l' is not a PR number" >&2; return 2;; *) printf '%s\n' "$l";; esac
  done < "$f"
}
held() { # held <pr>: rc 0 listed in the hold file, 1 not listed, 2 malformed file or argument. The orchestrator writes the file.
  local l; case ${1:-} in ''|*[!0-9]*|0*) die "'${1:-}' is not a PR number"; return;; esac
  l=$(hold_list) || return 2; grep -qxF "$1" <<< "$l"; }
# THE FREEZE (R10-FLOW-ROSTER-FREEZE arm (a), triage P-H): a head under review is the reviewer's
# measuring surface (fixer.md step 6), so the arm does not move it while
#   VERDICT  verdict/<pr>'s tip is `verdict: #<pr> Fix review: merge <head>` at the PR's live head:
#            moving it voids the merge it is waiting on. A `blocked` verdict at the head does not
#            freeze (a fixer handoff is what it asks for), nor one naming an older head;
#   REVIEW   no verdict at the head yet, and a review of that head is in flight: a dispatch of
#            <pr> at <head> in bus.sh's record ($HPO_BUS_STATE/dispatched), or a detached
#            worktree of this checkout at <head> (fix-review.md's review worktree). A verdict at
#            the head, either way, disposes it, so the roster edits held meanwhile land next pass.
# A frozen PR prints `cloud_relay: HELD-<why> #<pr> <handoff tip>` once per pass and is owed
# `handoff-held <ref> <tip> #<pr> <why>` in <log>.level: a decision for main, never a failure.
# RELEASE: `<state>/cloud-handoff-release` (the hold file's grammar, the orchestrator's) lists PRs
# the freeze passes over: genuine new work on a merge-verdicted fix head, which voids the verdict;
# re-dispatch with `bus.sh dispatch` after the update. The hold file outranks a release.
# bus.sh's dispatch record is the worker registry (R10-ORCH-DISPATCH-REG), so the REVIEW read
# above is the registry's live-reviewer read.
review_freeze() { # <pr> <head> <verdict refs file>: prints VERDICT, REVIEW or UNREAD and rc 0 when frozen; rc 1 when not
  local vs v bus=${HPO_BUS_STATE:-$HOME/.zcode/bus}
  vs=$(awk -v r="refs/heads/verdict/$1" '$2 == r { print $1; exit }' "$3")
  if [ -n "$vs" ]; then
    git fetch -q origin "refs/heads/verdict/$1" 2>/dev/null && git cat-file -e "$vs^{commit}" 2>/dev/null || { echo UNREAD; return 0; }
    v=$(git log -1 --format=%s "$vs" | sed -nE "s/^verdict: #$1 Fix review: (merge|blocked) ([0-9a-f]{40})( .*)?\$/\1 \2/p")
    case $v in "merge $2") echo VERDICT; return 0;; "blocked $2") return 1;; esac
  fi
  # Only the worker registry holds a review (P288): a detached worktree at the head is the
  # opener's or updater's own as often as a reviewer's (#2953 held 44 passes on one).
  v=$(awk -v p="$1" -v h="$2" '$1 == p && $2 == h { n = $4; at = $5 } END { if (n != "") print substr(n, 1, 8), (at == "" ? "-" : at) }' \
    "$bus/dispatched" 2>/dev/null)
  [ -n "$v" ] || return 1
  echo "REVIEW dispatch=${v% *} at=${v#* }"
}
# THE TOOLS TREE (P283). update_pr.sh refuses a checkout behind origin/main under the tools
# (pr_args.sh's pr_tools_fresh), and the relay's own checkout is stale whenever main moves them;
# the relay never moves that checkout, because bash reads a running script from its file as it
# goes. So it runs update_pr.sh from a worktree it owns, <state>/relay-tools, added once detached
# and checked out at origin/main before each update when clean. One that is dirty, or held by
# another relay (the mkdir lock <state>/relay-tools.lock naming a live pid; a dead pid's is taken
# over), is refused by name and left untouched; the update waits for the next pass.
tools_level() { # <state>: prints the levelled tree's seat directory, or why not: rc 75 busy, 2 refused
  local tw=$1/relay-tools o
  if ! mkdir "$tw.lock" 2>/dev/null; then
    o=$(cat "$tw.lock/pid" 2>/dev/null)
    if [ -n "$o" ] && kill -0 "$o" 2>/dev/null; then echo "the relay's tools tree $tw is busy (pid $o)"; return 75; fi  # mut:toolsbusy
  fi
  echo "$$" > "$tw.lock/pid"
  git fetch -q origin main 2>/dev/null || { rm -rf "$tw.lock"; echo "origin/main could not be fetched for the relay's tools tree"; return 2; }
  [ -e "$tw/.git" ] || git worktree add -q --detach "$tw" origin/main 2>/dev/null \
    || { rm -rf "$tw.lock"; echo "the relay's tools tree $tw could not be added"; return 2; }
  if [ -n "$(git -C "$tw" status --porcelain --untracked-files=no 2>/dev/null)" ]; then  # mut:toolsdirty
    rm -rf "$tw.lock"; echo "the relay's tools tree $tw is dirty; it is left as it is"; return 2
  fi
  git -C "$tw" checkout -q --detach origin/main 2>/dev/null \
    || { rm -rf "$tw.lock"; echo "the relay's tools tree $tw could not check out origin/main"; return 2; }  # mut:toolslevel
  echo "$tw/tools/audit/seat"
}
body_only_owed() { # <pr> <topic> <body sha> <head> <why>: a body-only handoff left unapplied is owed while its body tip is newer than the head's commit
  local bt ht; git fetch -q origin "refs/heads/handoff-body/$2" 2>/dev/null
  bt=$(git log -1 --format=%ct "$3" 2>/dev/null) && ht=$(git log -1 --format=%ct "$4" 2>/dev/null) && [ "$bt" -gt "$ht" ] || return 1
  echo "cloud_relay: BODY-ONLY #$1 handoff-body/$2 ${3:0:12} is newer than head ${4:0:12} and not applied: $5"
  level_line handoff-body-unapplied "refs/heads/handoff-body/$2" "$3" "#$1 $5" >> "$state/cloud-level-bodyonly.$$"
}
open_prs() { # the open PRs, `<number> <head ref> <head sha>` tab-separated: HPO_RELAY_PRS or gh
  if [ -n "${HPO_RELAY_PRS:-}" ]; then "$HPO_RELAY_PRS"
  else gh pr list -R "${HPO_RELAY_REPO:-tvofi/heatpump_optimizer}" --state open --limit 100 --json number,headRefName,headRefOid \
    -q '.[] | [.number, .headRefName, .headRefOid] | @tsv'; fi
}
handoff_level() { # the handoff-no-pr and hold-stale levels, derived from this pass's listings (called before the serial update loop)
  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} repo=${HPO_RELAY_REPO:-tvofi/heatpump_optimizer} l
  # a hold-file line whose PR is no longer open (merged or closed) is stale: it holds nothing and is never expired
  : > "$state/cloud-level-holdstale.$$"
  for l in $held_prs; do
    grep -qxF "$l" <<< "$(cut -f1 "$state/cloud-prs.$$")" || level_line handoff-hold-stale "$(hold_file)" "#$l" "PR #$l is not open; remove the line" >> "$state/cloud-level-holdstale.$$"
  done
  level_set handoff-hold-stale "$state/cloud-level-holdstale.$$"
  cut -f2 "$state/cloud-prs.$$" | sed -e 's,^fix/,,' -e 's,-pr$,,' > "$state/cloud-topics.$$"
  { if [ -n "${HPO_RELAY_MERGED:-}" ]; then "$HPO_RELAY_MERGED"
    else gh pr list -R "$repo" --state merged --limit 200 --json headRefName,mergedAt \
      -q '.[] | [.headRefName, .mergedAt] | @tsv'; fi; } > "$state/cloud-merged.$$" \
    || { echo "cloud_relay: could not list merged PRs; the handoff level stays as it was" >&2; return 0; }
  awk -F'\t' 'NF == 2 { t = $1; sub(/^fix\//, "", t); sub(/-pr$/, "", t); print t " merged=" $2 }' "$state/cloud-merged.$$" >> "$state/cloud-topics.$$"
  ledger level "$state/cloud-hrefs.$$" "$state/cloud-topics.$$" > "$state/cloud-level-handoff.$$"
  case $? in 0|1) level_set handoff-no-pr "$state/cloud-level-handoff.$$";;
    *) echo "cloud_relay: the ledger could not derive the handoff level; it stays as it was" >&2; rm -f "$state/cloud-level-handoff.$$";; esac
}
handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of its head
  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} repo=${HPO_RELAY_REPO:-tvofi/heatpump_optimizer} f pr br head topic hs bs bd body iss nh nonce urc held_prs released upd why code
  local bf bonly key seed="" tries n cls
  f=$state/cloud-handoff-failed; mkdir -p "$state"
  # BODY-ONLY (R10-FLOW-BODY-ONLY part (c)): `<topic> <body sha>` per body this relay has applied, by an
  # update or a body-only run. With no file yet, this pass records every contained topic's body as
  # applied (the seed) and runs nothing, so the first pass does not re-body every open PR.
  bf=$state/cloud-handoff-bodied; [ -f "$bf" ] || seed=1; touch "$bf"
  : > "$state/cloud-level-hold.$$"   # the refusal is a level: owed while the file is malformed, gone once it is not
  held_prs=$(hold_list) || { level_line handoff-hold-malformed "$(hold_file)" - >> "$state/cloud-level-hold.$$"; level_set handoff-hold-malformed "$state/cloud-level-hold.$$"; return 2; }
  released=$(hold_list "$(release_file)") || { level_line handoff-hold-malformed "$(release_file)" - >> "$state/cloud-level-hold.$$"; level_set handoff-hold-malformed "$state/cloud-level-hold.$$"; return 2; }
  level_set handoff-hold-malformed "$state/cloud-level-hold.$$"
  # R10-RELAY-ARM-ORDER: the listing is pass()'s, taken once ahead of every arm; a lone call lists here
  if [ -f "$state/cloud-prs-open.$$" ]; then cp -f "$state/cloud-prs-open.$$" "$state/cloud-prs.$$"
  else open_prs > "$state/cloud-prs.$$" \
    || { echo "cloud_relay: could not list open PRs; will retry" >&2; rm -f "$state/cloud-prs.$$"; return 0; }; fi
  git ls-remote origin 'refs/heads/handoff/*' 'refs/heads/handoff-body/*' > "$state/cloud-hrefs.$$" \
    || { echo "cloud_relay: could not list handoff refs; will retry" >&2; rm -f "$state/cloud-prs.$$" "$state/cloud-hrefs.$$"; return 0; }
  # one listing of the verdicts per pass, outside the loop: an unread listing would update a merge-verdicted head
  git ls-remote origin 'refs/heads/verdict/*' > "$state/cloud-vrefs.$$" \
    || { echo "cloud_relay: could not list verdict refs; will retry" >&2; rm -f "$state/cloud-prs.$$" "$state/cloud-hrefs.$$" "$state/cloud-vrefs.$$"; return 0; }
  : > "$state/cloud-level-update.$$"; : > "$state/cloud-level-held.$$"; : > "$state/cloud-level-stale.$$"; : > "$state/cloud-level-bodyonly.$$"
  handoff_level
  while IFS=$'\t' read -r pr br head; do
    [ -n "$pr" ] || continue
    topic=$(python3 -I "$HERE/topic_grammar.py" pr-topic "$br")
    hs=$(awk -v r="refs/heads/handoff/$topic" '$2 == r { print $1; exit }' "$state/cloud-hrefs.$$")
    bs=$(awk -v r="refs/heads/handoff-body/$topic" '$2 == r { print $1; exit }' "$state/cloud-hrefs.$$")
    [ -n "$hs" ] && [ -n "$bs" ] || continue
    git fetch -q origin "refs/heads/handoff/$topic" "refs/heads/$br" 2>/dev/null
    git cat-file -e "$hs^{commit}" 2>/dev/null && git cat-file -e "$head^{commit}" 2>/dev/null || continue
    # A head holding the handoff tip has its code; only a body this relay has not applied moves it,
    # and that move is body-only: update_pr.sh with code `-`, which PATCHes the body and pushes nothing.
    bonly=""; if git merge-base --is-ancestor "$hs" "$head"; then
      grep -qxF "$topic $bs" "$bf" && continue
      [ -z "$seed" ] || { echo "$topic $bs" >> "$bf"; continue; }
      bonly=1; fi
    if grep -qxF "$pr" <<< "$held_prs"; then echo "cloud_relay: HELD #$pr $hs"; [ -z "$bonly" ] || body_only_owed "$pr" "$topic" "$bs" "$head" "held by the hold file" || :; continue; fi
    # a body-only move leaves the head under review where it is, so no review freezes it
    if [ -z "$bonly" ] && ! grep -qxF "$pr" <<< "$released" && why=$(review_freeze "$pr" "$head" "$state/cloud-vrefs.$$"); then
      echo "cloud_relay: HELD-${why%% *} #$pr $hs${why#"${why%% *}"} (head $head under review; merge it, or list #$pr in $(release_file) and re-dispatch)"
      level_line handoff-held "refs/heads/handoff/$topic" "$hs" "#$pr $why" >> "$state/cloud-level-held.$$"; continue
    fi
    # A failed run is keyed on the body sha too (P22, carry 8): a new body re-triggers it, and the reason stays.
    key="$topic $hs $bs"
    if [ -f "$f" ] && grep -qxF "$key" "$f"; then
      why=$(awk -F'\t' -v k="$key" '$1 == k { w = $2 } END { print w }' "$f.why" 2>/dev/null)
      level_line handoff-update "refs/heads/handoff/$topic" "$hs" "$why" >> "$state/cloud-level-update.$$"; continue
    fi
    # A retryable refusal (carry 12) waits out its backoff, owed meanwhile with its reason; $f.tries is `<key>\t<n>\t<epoch>`.
    tries=$(awk -F'\t' -v k="$key" '$1 == k { n = $2; t = $3 } END { print (n == "" ? "0 0" : n " " t) }' "$f.tries" 2>/dev/null)
    if [ "${tries% *}" != 0 ] && [ "$(date +%s)" -lt $(( ${tries#* } + ${HPO_RELAY_RETRY_BACKOFF:-1800} )) ]; then why=$(awk -F'\t' -v k="$key" '$1 == k { w = $2 } END { print w }' "$f.why" 2>/dev/null); level_line handoff-update "refs/heads/handoff/$topic" "$hs" "$why" >> "$state/cloud-level-update.$$"; continue; fi  # mut:backoff
    # The body goes in a directory of this run's own, under the state dir: a file directly in a
    # shared temp root ($TMPDIR, /tmp) is refused by prepr's body-path check, so every relay
    # update failed there (#2469, #2471) -- and still raced the manual update it was meant to spare.
    bd=$(mktemp -d "$state/cloud-body.XXXXXX") || { echo "cloud_relay: no body directory under $state" >&2; continue; }
    body=$bd/BODY.md
    git fetch -q origin "refs/heads/handoff-body/$topic" 2>/dev/null \
      && git show "$bs:BODY.md" > "$body" 2>/dev/null || { echo "cloud_relay: no BODY.md at handoff-body/$topic" >&2; rm -rf "$bd"; continue; }
    # A body names the code head it was pushed for (body_push.sh's `Code:` trailer, V147). One
    # naming another head describes a tree the PR would not carry, so it waits, owed and unrecorded,
    # until the body for this head lands. A body with no `Code:` line predates the trailer: as before.
    code=$(git log -1 --format=%B "$bs" 2>/dev/null | sed -n 's/^Code: \([0-9a-f]\{40\}\)$/\1/p' | tail -n 1)
    if [ -n "$code" ] && [ "$code" != "$hs" ]; then
      echo "cloud_relay: STALE handoff-body/$topic names ${code:0:12}, handoff/$topic is at ${hs:0:12}; the next pass retries" >&2
      level_line handoff-body-stale "refs/heads/handoff/$topic" "$hs" "body names ${code:0:12}" >> "$state/cloud-level-stale.$$"; rm -rf "$bd"; continue
    fi
    # A body-only move is made with the body pushed for this head: one with no `Code:` line, which
    # predates the trailer, is recorded as applied and left alone, as before this arm existed.
    if [ -n "$bonly" ] && [ -z "$code" ]; then
      # owed (and not recorded) while the body is newer than the head: its return must not be skipped in silence (P288)
      body_only_owed "$pr" "$topic" "$bs" "$head" "its body carries no Code: trailer" || echo "$topic $bs" >> "$bf"
      rm -rf "$bd"; continue; fi
    # HELD-BODY: a code push precedes its body push, so a handoff ahead of its own body is partial work.
    # The body must name the tip (its first 8 characters), else the update waits for the next pass.
    if [ -z "$bonly" ] && ! grep -qF "${hs:0:8}" "$body"; then
      echo "cloud_relay: HELD-BODY #$pr ${hs:0:8}"
      level_line handoff-held "refs/heads/handoff/$topic" "$hs" "#$pr BODY" >> "$state/cloud-level-held.$$"; rm -rf "$bd"; continue
    fi
    iss=$(grep -oiE '\b(close[sd]?|fix(e[sd])?|resolve[sd]?)[: ]+#[0-9]+' "$body" | grep -oE '[0-9]+' | sort -un | tr '\n' ' ')
    if [ -n "$bonly" ]; then echo "$(date -u +%FT%TZ) cloud_relay: handoff-body/$topic $bs is new for #$pr $head; body-only"
    else echo "$(date -u +%FT%TZ) cloud_relay: handoff/$topic $hs is ahead of #$pr $head; updating"; fi
    # The update is the reap's lead (pr_args.sh's PR_REAP_LEAD): a stopped relay TERMs it alone,
    # so update_pr.sh ends its push before it frees the branch lock, and reaps what is left after.
    # It runs in a process group of its own (pr_own_group), so a signal to the loop's whole group
    # (`timeout`, a daemonizer ending the pgid, a closed terminal's HUP) reaches it only through
    # that reap, and a KILL to the group leaves it to finish under its own lock (#2549).
    # One launch for both routes, so the self-test's stub runs the production launch line. The
    # script is the levelled tools tree's (tools_level), never this checkout's; a stub skips the tree.
    urc=0; upd=("${HPO_RELAY_UPDATE:-}")
    if [ -z "${HPO_RELAY_UPDATE:-}" ]; then
      why=$(tools_level "$state"); urc=$?
      if [ "$urc" != 0 ]; then
        echo "cloud_relay: REFUSED the update of #$pr: $why; the next pass retries" >&2
        [ "$urc" = 75 ] || level_line handoff-update "refs/heads/handoff/$topic" "$hs" "$why" >> "$state/cloud-level-update.$$"
        rm -rf "$bd"; continue
      fi
      upd=(bash "$why/update_pr.sh")  # mut:toolsseat
    fi
    # Its output is kept until it ends, so a failure records its reason: the last REFUSE line, else the last line.
    # A body-only move skipped the review freeze, so update_pr.sh refuses one that would move the head.
    HPO_UPDATE_BODY_ONLY=$bonly pr_own_group "${upd[@]}" "$br" "$([ -n "$bonly" ] && echo - || echo "$hs")" "$body" $iss > "$bd/update.out" 2>&1 &  # never-empty: upd is assigned the bash update_pr.sh command on the line above
    PR_REAP_LEAD=$!; wait "$PR_REAP_LEAD" || urc=$?
    [ -n "${HPO_RELAY_UPDATE:-}" ] || rm -rf "$state/relay-tools.lock"
    cat "$bd/update.out" >&2
    # 75 is update_pr.sh's BUSY: another run (the orchestrator's) holds this branch's worktree. Not
    # a failure, so it is not recorded and the next pass retries once that run has ended.
    if [ "$urc" = 75 ]; then echo "cloud_relay: update_pr busy on $br; the next pass retries" >&2; rm -rf "$bd"; continue; fi
    if [ "$urc" != 0 ]; then
      why=$(grep REFUSE "$bd/update.out" | tail -n 1); [ -n "$why" ] || why=$(last_line "$(cat "$bd/update.out")")
      # A refusal of a body-content step (unpinned sites, carry, figures, the body contract) clears only when the body
      # ref moves, which is a new key: recorded at once. Any other (ancestry reds, ci predict) can clear with no ref
      # moving: it reruns after HPO_RELAY_RETRY_BACKOFF (30 min), three runs at most, then it is recorded and owed.
      n=${tries% *}; n=$((n + 1)); cls=retry
      ! grep -qiE '^[[:space:]]*(update_pr: )?REFUSE[: ]+(unpinned sites?|carry|pr-body|figures|brief)' "$bd/update.out" || cls=content  # mut:retryall
      [ "$n" -lt 3 ] || cls=content  # mut:trylimit
      if [ "$cls" = content ]; then
        echo "$key" >> "$f"
      else printf '%s\t%s\t%s\n' "$key" "$n" "$(date +%s)" >> "$f.tries"; fi
      printf '%s\t%s\n' "$key" "$why" >> "$f.why"
      level_line handoff-update "refs/heads/handoff/$topic" "$hs" "$why" >> "$state/cloud-level-update.$$"; rm -rf "$bd"; continue
    fi
    rm -rf "$bd"; echo "$topic $bs" >> "$bf"  # this body is applied: a later pass leaves it alone
    [ ! -f "$f.tries" ] || { grep -vF "$key	" "$f.tries" > "$f.tries.$$" || :; mv -f "$f.tries.$$" "$f.tries"; }
    if [ -n "$bonly" ]; then echo "cloud_relay: BODIED #$pr $head with handoff-body/$topic $bs" >&2; continue; fi
    nh=$( { if [ -n "${HPO_RELAY_PRS:-}" ]; then "$HPO_RELAY_PRS"; else gh pr list -R "$repo" --state open --limit 100 --json number,headRefName,headRefOid \
      -q '.[] | [.number, .headRefName, .headRefOid] | @tsv'; fi; } | awk -F'\t' -v p="$pr" '$1 == p { print $3; exit }')
    if [ -n "${HPO_RELAY_APPROVE:-}" ]; then "$HPO_RELAY_APPROVE" "$br"; else bash "$HERE/../../pr/approve_held_runs.sh" "$repo" "$br"; fi >&2 \
      || ledger_open approve-held-runs "$pr" "$(printf '%s' "$nh" | grep -E '^[0-9a-f]{40}$' || echo -)" "$br"
    printf '%s' "$nh" | grep -Eq '^[0-9a-f]{40}$' || { ledger_open dispatch "$pr" - "no new head read after the update"; continue; }
    if nonce=$( { if [ -n "${HPO_RELAY_DISPATCH:-}" ]; then "$HPO_RELAY_DISPATCH" "$pr" "$nh" cloud; else bash "$HERE/bus.sh" dispatch "$pr" "$nh" cloud; fi; } | sed -n 's/^bus-nonce: //p' | head -n 1) \
       && printf '%s' "$nonce" | grep -Eq '^[0-9a-f]{32}$'; then
      ledger_open reviewer-fire "$pr" "$nh" "nonce=$nonce"
    else ledger_open dispatch "$pr" "$nh" "bus.sh dispatch failed; run it by hand"; fi
  done < "$state/cloud-prs.$$"
  level_set handoff-update "$state/cloud-level-update.$$"
  level_set handoff-held "$state/cloud-level-held.$$"
  level_set handoff-body-stale "$state/cloud-level-stale.$$"
  level_set handoff-body-unapplied "$state/cloud-level-bodyonly.$$"
  rm -f "$state/cloud-prs.$$" "$state/cloud-hrefs.$$" "$state/cloud-topics.$$" "$state/cloud-vrefs.$$" "$state/cloud-merged.$$"
}

# THE STUCK ANDON (triage P163; a trial, report-only, removed if it reports no STUCK line in its first
# 48 h). A branch lock (pr_args.sh's pr_branch_lock) held longer than HPO_PUSH_STUCK_SECS (default
# 900) is a run or its push that has not ended: `push-stuck <branch> <pid>` on the level, its why
# `STUCK <branch> <pid> <age>s`, where <branch> is the lock's name (update_pr.sh's worktree name, `/`
# as `-`), <pid> the run's and <age> from the start epoch its holder recorded -- never the file's
# mtime, which the drain mark rewrites. A released lock keeps its text, so only a lock held now is
# read, by trying it (LOCK_NB) once its age is past the bound: a run that starts in that moment
# reads BUSY, exit 75, and is retried as any BUSY is. A lock with no start recorded has no age and
# is not reported. Reaping is update_pr.sh's; this reports only. Unreadable: the level stays.
STUCK_PY='import fcntl, os, sys, time
lim, d = int(sys.argv[1]), sys.argv[2]; now = int(time.time())
def held(f):
  try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
  except BlockingIOError: return True
  fcntl.flock(f, fcntl.LOCK_UN); return False
for n in sorted(os.listdir(d)) if os.path.isdir(d) else []:
  if not (n.startswith("upd-") and n.endswith(".lock")): continue
  try:
    f = open(os.path.join(d, n)); w = f.read().split()
    run, start = int(w[0]), int(w[2])
  except (OSError, IndexError, ValueError): continue
  if now - start <= lim: continue
  if not held(f): continue
  print(n[4:-5], run, now - start)'
stuck_arm() { # one pass over the branch locks: each held past HPO_PUSH_STUCK_SECS is push-stuck on the level
  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} b p a
  mkdir -p "$state" || return 0
  python3 -I -c "$STUCK_PY" "${HPO_PUSH_STUCK_SECS:-900}" "$state/pr" > "$state/cloud-stuck.$$" \
    || { echo "cloud_relay: the branch locks could not be read (HPO_PUSH_STUCK_SECS='${HPO_PUSH_STUCK_SECS:-900}'); the level stays" >&2; rm -f "$state/cloud-stuck.$$"; return 0; }
  : > "$state/cloud-level-stuck.$$"
  while read -r b p a; do
    level_line push-stuck "$b" "$p" "STUCK $b $p ${a}s" >> "$state/cloud-level-stuck.$$"; echo "cloud_relay: STUCK $b $p ${a}s"
  done < "$state/cloud-stuck.$$"
  rm -f "$state/cloud-stuck.$$"; level_set push-stuck "$state/cloud-level-stuck.$$"
}

# THE NO-RETURN LINE (triage P-E, narrowed to git). A cloud fixer dispatched on
# dispatch/fixer-<topic> returns on handoff-wip/, handoff/ or handoff-body/<topic>, or moves its
# pull request's fix/<topic>-pr or fix/<topic> head. One whose dispatch tip is older than
# HPO_RELAY_NORETURN_SECS (default 7200) with none of those moved since is
#   OWED <utc> seat-no-return refs/heads/dispatch/fixer-<topic> <sha> SEAT ENDED NO RETURN <topic> <age>h
# on the level (the #2620 seat sat 6 h silent). The record is the dispatch ref itself: no
# cloud-sessions file is written anywhere in the tree, so the session id is not named; the
# dispatch tip and its age are. Past HPO_RELAY_NORETURN_WINDOW_SECS (default 172800) a dispatch
# falls off: its refs may be gone with a merged branch. Deleting the dispatch ref disposes it.
# A listing or fetch that fails leaves the level as it was. Designer seats are out of scope.
# A reviewer on dispatch/reviewer-* is covered by the same arm with its own bound,
# HPO_RELAY_NORETURN_REVIEWER_SECS (default 5400, above the 66 min longest returner measured in the
# s13/rca-noreturn RCA; the fixer's bound stays HPO_RELAY_NORETURN_SECS): one whose dispatch tip is older than
# that, whose PROMPT.md nonce (first 8) names no probe/rev-<pr>-<n8> or probe/revt-<topic>-<n8>, and whose PR
# head (read by HPO_RELAY_PRHEAD, else gh) is still the dispatched head, is owed on the same level. A moved
# head means the dispatch was superseded, and an unreadable head is silent (unknown is not owed). The
# ledger's reviewer-fire entry closes at the fire, so nothing else owes a reviewer that never returned.
noreturn_arm() {
  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} lim=${HPO_RELAY_NORETURN_SECS:-7200} win=${HPO_RELAY_NORETURN_WINDOW_SECS:-172800} rlim=${HPO_RELAY_NORETURN_REVIEWER_SECS:-5400}
  local now sha ref topic t age r rs moved first rpr rhead rn8 rlive
  case $lim$win$rlim in *[!0-9]*) echo "cloud_relay: HPO_RELAY_NORETURN_SECS/WINDOW/REVIEWER_SECS must be seconds; the level stays" >&2; return 0;; esac
  mkdir -p "$state" || return 0
  # Only the dispatch refs are listed by glob; each candidate's return refs are asked by name, so no
  # glob here lists a handoff-wip step ref (cloud_dispatch.py pins that no handoff arm sees one).
  git ls-remote origin 'refs/heads/dispatch/fixer-*' 'refs/heads/dispatch/reviewer-*' > "$state/cloud-nr.$$" \
    && git fetch -q origin '+refs/heads/dispatch/fixer-*:refs/hpo-relay/dispatch/fixer-*' '+refs/heads/dispatch/reviewer-*:refs/hpo-relay/dispatch/reviewer-*' 2>/dev/null \
    || { echo "cloud_relay: the dispatch refs could not be read; the no-return level stays" >&2; rm -f "$state/cloud-nr.$$"; return 0; }
  now=$(date +%s); : > "$state/cloud-level-nr.$$"
  while read -r sha ref; do
    case $ref in
      refs/heads/dispatch/reviewer-?*)
        t=$(git log -1 --format=%ct "$sha" 2>/dev/null) || continue; age=$((now - t))
        [ "$age" -gt "$rlim" ] && [ "$age" -le "$win" ] || continue  # mut:noreturnrevage
        first=$(git show "$sha:PROMPT.md" 2>/dev/null | head -n 1)
        rn8=$(sed -n 's/^CLOUD REVIEWER seat for .*, at head [0-9a-f]\{40\}\. Bus nonce: \([0-9a-f]\{8\}\)[0-9a-f]*\..*/\1/p' <<< "$first")
        rhead=$(sed -n 's/^CLOUD REVIEWER seat for .*, at head \([0-9a-f]\{40\}\)\. Bus nonce:.*/\1/p' <<< "$first")
        rpr=$(sed -n 's/^CLOUD REVIEWER seat for PR #\([0-9][0-9]*\) of .*/\1/p' <<< "$first")
        [ -n "$rn8" ] && [ -n "$rhead" ] || continue  # not a reviewer's prompt, or no nonce to match a return by
        git ls-remote origin "refs/heads/probe/rev-*-$rn8" "refs/heads/probe/revt-*-$rn8" > "$state/cloud-nrr.$$" || continue
        [ -s "$state/cloud-nrr.$$" ] && continue  # mut:noreturnrevret -- the verdict came back
        if [ -n "$rpr" ]; then  # mut:noreturnrevmoved
          rlive=$(if [ -n "${HPO_RELAY_PRHEAD:-}" ]; then "$HPO_RELAY_PRHEAD" "$rpr"; else gh pr view "$rpr" -R "${HPO_RELAY_REPO:-tvofi/heatpump_optimizer}" --json headRefOid --jq .headRefOid; fi 2>/dev/null)
          [ "$rlive" = "$rhead" ] || continue
        fi
        echo "cloud_relay: SEAT ENDED NO RETURN reviewer ${rpr:+#$rpr }${ref#refs/heads/dispatch/reviewer-} (dispatch ${sha:0:12}, $((age / 60))min, no probe/rev ref and the PR head unmoved)"
        level_line seat-no-return "$ref" "$sha" "SEAT ENDED NO RETURN reviewer ${rpr:+#$rpr }${ref#refs/heads/dispatch/reviewer-} $((age / 60))min" >> "$state/cloud-level-nr.$$"
        continue ;;
      refs/heads/dispatch/fixer-?*) topic=${ref#refs/heads/dispatch/fixer-} ;;
      *) continue ;;
    esac
    t=$(git log -1 --format=%ct "$sha" 2>/dev/null) || continue
    age=$((now - t))
    [ "$age" -gt "$lim" ] && [ "$age" -le "$win" ] || continue  # mut:noreturnage
    moved=
    git ls-remote origin "refs/heads/handoff/$topic" "refs/heads/handoff-wip/$topic" "refs/heads/handoff-body/$topic" \
      "refs/heads/fix/$topic-pr" "refs/heads/fix/$topic" > "$state/cloud-nrr.$$" || { moved=unread; }
    for r in handoff/$topic handoff-wip/$topic handoff-body/$topic fix/$topic-pr fix/$topic; do
      rs=$(awk -v r="refs/heads/$r" '$2 == r { print $1; exit }' "$state/cloud-nrr.$$")
      [ -n "$rs" ] || continue
      git cat-file -e "$rs^{commit}" 2>/dev/null || git fetch -q origin "refs/heads/$r" 2>/dev/null
      [ "$(git log -1 --format=%ct "$rs" 2>/dev/null || echo 0)" -gt "$t" ] && { moved=1; break; }  # mut:noreturnmoved
    done
    if [ -z "$moved" ]; then  # a split seat returns under <base>-p<N>: only a full-matching family member counts
      { git ls-remote origin "refs/heads/handoff/${topic%-p[0-9]*}-p*" "refs/heads/handoff-wip/${topic%-p[0-9]*}-p*" \
          "refs/heads/handoff-body/${topic%-p[0-9]*}-p*" "refs/heads/handoff/${topic%-p[0-9]*}" "refs/heads/handoff-wip/${topic%-p[0-9]*}" \
          "refs/heads/handoff-body/${topic%-p[0-9]*}" 2>/dev/null || moved=unread; } > "$state/cloud-nrf.$$"
      while read -r rs r; do  # mut:noreturnfamily
        git cat-file -e "$rs^{commit}" 2>/dev/null || git fetch -q origin "$r" 2>/dev/null
        [ "$(git log -1 --format=%ct "$rs" 2>/dev/null || echo 0)" -gt "$t" ] && { moved=1; break; }
      done < <(python3 -I "$HERE/topic_grammar.py" family-refs "$topic" handoff,handoff-wip,handoff-body < "$state/cloud-nrf.$$")
      rm -f "$state/cloud-nrf.$$"
    fi
    [ -n "$moved" ] && continue
    echo "cloud_relay: SEAT ENDED NO RETURN $topic (dispatch ${sha:0:12}, $((age / 3600))h, no return ref or PR head moved since)"
    level_line seat-no-return "$ref" "$sha" "SEAT ENDED NO RETURN $topic $((age / 3600))h" >> "$state/cloud-level-nr.$$"
  done < "$state/cloud-nr.$$"
  level_set seat-no-return "$state/cloud-level-nr.$$"
  rm -f "$state/cloud-nr.$$" "$state/cloud-nrr.$$"
}

fold_judge() { # <memo> <level> <topic> <wip sha> <body sha> <outcome> <epoch> [<OWED level line>]: one judged topic, its level line set
  printf '%s %s %s %s %s%s\n' "$3" "$4" "${5:--}" "$6" "$7" "${8:+ $8}" >> "$1"; [ -z "${8:-}" ] || printf '%s\n' "$8" >> "$2"; }
fold_memo_stands() { # <outcome> <epoch> <now>: rc 0 while a judged outcome stands; a failure after the fold expires after 3600 s
  case $1:$2 in blocked:*|folded:*) return 0;; fold-failed:[0-9]*|push-failed:[0-9]*) [ $(($3 - $2)) -lt 3600 ];; *) return 1;; esac; }  # mut:foldttl
carry_fold_arm() { # one pass over handoff-wip/<topic> refs whose BLOCKED.md names CARRY-LANDED alone: fold the kept body's carries, re-run body_push.sh
  # A cloud fixer may not write the roster, so body_push.sh's CARRY-LANDED refusal (exit 4; each refusal prints
  # `body_push: REFUSED <KIND>` into the BLOCKED.md the fixer pushes) stranded it until a seat landed the carries
  # by hand (4 times on 2026-11-06, twice more on 11-07). The refusal is folded only when it is the ONLY kind the
  # BLOCKED.md names and the refused body is kept on handoff-wip/<topic>-body; any other BLOCKED.md prints a tick
  # line and folds nothing. carry_fold.py is the designated roster writer; HPO_RELAY_FOLD / HPO_RELAY_BODYPUSH replace the two steps.
  # Every judged (wip sha, body sha) is memoed in cloud-fold-judged, `<topic> <wip> <body|-> <outcome> <epoch> [<OWED line>]`
  # (P580); a (topic, body) cloud-folded holds is skipped unmemoed. A memoed pair is neither fetched nor shown, and its
  # stored line is set again, because level_set replaces the whole carry-fold level. A failure after the fold is judged
  # again once fold_memo_stands expires it: an ancestry red can clear with no ref moving. The body is pushed from a
  # worktree at a private ref fetched from handoff/<topic>, deleted after the push, never FETCH_HEAD, which a concurrent
  # fetch in this checkout overwrites, and only at that ref's ls-remote tip (P556).
  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} sha ref topic bw bsha kinds wt body why rc memo now mo me ml htip head
  git ls-remote origin 'refs/heads/handoff-wip/*' 'refs/heads/handoff/*' > "$state/cloud-wip.$$" \
    || { echo "cloud_relay: could not list handoff-wip refs; the carry-fold level stays as it was" >&2; rm -f "$state/cloud-wip.$$"; return 0; }
  memo=$state/cloud-fold-judged; now=$(date +%s)
  mkdir -p "$state"; : > "$state/cloud-level-fold.$$"; : > "$memo.$$"
  while read -r sha ref; do
    case $ref in refs/heads/handoff-wip/*) topic=${ref#refs/heads/handoff-wip/};; *) continue;; esac
    case $topic in ''|*/*|*-body|*-carries|*-body-*) continue;; esac
    bsha=$(awk -v r="refs/heads/handoff-wip/$topic-body" '$2 == r { print $1; exit }' "$state/cloud-wip.$$")
    mo= me= ml=; [ -f "$memo" ] && read -r _ _ _ mo me ml < <(awk -v t="$topic" -v w="$sha" -v b="${bsha:--}" '$1 == t && $2 == w && $3 == b { print; exit }' "$memo")
    if [ -n "$mo" ] && fold_memo_stands "$mo" "$me" "$now"; then
      fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" "$mo" "$me" "$ml"; continue  # mut:foldmemo
    fi
    [ -f "$state/cloud-folded" ] && grep -qxF "$topic $bsha" "$state/cloud-folded" && continue
    git fetch -q origin "$ref" 2>/dev/null && bw=$(git show "$sha:BLOCKED.md" 2>/dev/null) || continue
    kinds=$(printf '%s\n' "$bw" | sed -n 's/^body_push: REFUSED \([A-Z-]*\)[[:space:]]*$/\1/p' | sort -u | tr '\n' ' ')
    if [ "$kinds" != "CARRY-LANDED " ] || [ -z "$bsha" ]; then  # mut:foldonly
      why="BLOCKED.md names ${kinds:-no refusal line}${bsha:+; }${bsha:-and no kept body}: not CARRY-LANDED alone, nothing folded"
      echo "cloud_relay: OWED carry-fold $topic ${sha:0:12} $why"
      fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" blocked "$now" "$(level_line carry-fold "$ref" "$sha" "$why")"; continue
    fi
    body=$state/cloud-fold-$topic.md
    git fetch -q origin "refs/heads/handoff-wip/$topic-body" 2>/dev/null && git show "$bsha:BODY.md" > "$body" 2>/dev/null \
      || { echo "cloud_relay: no BODY.md at handoff-wip/$topic-body; nothing folded" >&2; continue; }
    rc=0; why=$(${HPO_RELAY_FOLD:-python3 -I "$HERE/carry_fold.py"} --body "$body" --topic "$topic" --worktree "$state/cloud-fold-wt" 2>&1) || rc=$?
    if [ $rc != 0 ]; then
      why=$(last_line "$why"); echo "cloud_relay: OWED carry-fold $topic ${sha:0:12} carry_fold rc=$rc: $why"
      fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" fold-failed "$now" "$(level_line carry-fold "$ref" "$sha" "carry_fold rc=$rc: $why")"; continue
    fi
    wt=$state/cloud-fold-code; rm -rf "$wt"; git worktree prune; rc=1
    htip=$(awk -v r="refs/heads/handoff/$topic" '$2 == r { print $1; exit }' "$state/cloud-wip.$$")
    if [ -z "$htip" ] || ! git fetch -q origin "+refs/heads/handoff/$topic:refs/hpo-relay/fold/$topic" 2>/dev/null \
      || ! git worktree add -q --detach "$wt" "refs/hpo-relay/fold/$topic" 2>/dev/null; then  # mut:foldref
      why="no handoff/$topic to push the body from"; echo "cloud_relay: OWED carry-fold $topic ${sha:0:12} $why"
    elif head=$(git -C "$wt" rev-parse HEAD) && [ "$head" != "$htip" ]; then  # mut:foldtip
      why="worktree at ${head:0:12}, handoff at ${htip:0:12}"; echo "cloud_relay: OWED carry-fold $topic $why"
    else
      if [ -n "${HPO_RELAY_BODYPUSH:-}" ]; then (cd "$wt" && "$HPO_RELAY_BODYPUSH" "$topic" "$body") > "$state/cloud-fold.out" 2>&1; rc=$?
      else (cd "$wt" && bash "$HERE/body_push.sh" "$topic" "$body") > "$state/cloud-fold.out" 2>&1; rc=$?; fi
      why="body_push rc=$rc: $(last_line "$(cat "$state/cloud-fold.out")")"
      [ $rc = 0 ] || echo "cloud_relay: OWED carry-fold $topic ${sha:0:12} body_push rc=$rc after the fold: ${why#*: }"
    fi
    git worktree remove --force "$wt" 2>/dev/null; git update-ref -d "refs/hpo-relay/fold/$topic" 2>/dev/null
    if [ $rc = 0 ]; then echo "$topic $bsha" >> "$state/cloud-folded"; echo "cloud_relay: FOLDED $topic: carries landed, body_push.sh pushed handoff-body/$topic"
      fold_judge "$memo.$$" /dev/null "$topic" "$sha" "$bsha" folded "$now"
    else fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" push-failed "$now" "$(level_line carry-fold "$ref" "$sha" "$why")"
    fi
  done < "$state/cloud-wip.$$"
  mv -f "$memo.$$" "$memo"; level_set carry-fold "$state/cloud-level-fold.$$"; rm -f "$state/cloud-wip.$$"
}

pass() { # [--confirm] [--log FILE] [--loop [--interval N]]
  local every=120 loop=""
  while [ $# -gt 0 ]; do case $1 in
    --confirm) CONFIRM=1; shift;; --log) LOG=${2:-}; shift 2;; --loop) loop=1; shift;; --interval) every=${2:-}; shift 2;;
    *) echo "cloud_relay: unknown pass option '$1'" >&2; return 2;; esac; done
  case $every in ''|*[!0-9]*|0) echo "cloud_relay: --interval must be a positive number of seconds" >&2; return 2;; esac
  while :; do
    echo "cloud_relay: state dir ${HPO_STATE_DIR:-$HOME/.local/state/hpo}, ledger ${HPO_STATE_DIR:-$HOME/.local/state/hpo}/cloud-relayed, log $(relay_log)"
    # R10-RELAY-ARM-ORDER: a returned verdict posts before the serial updates run (handoff_arm blocks on
    # each update_pr.sh and a full prepr). The one open-PR listing is taken first, for confirm_arm and handoff_arm;
    # a failed listing leaves no file and each arm lists for itself.
    local pst=${HPO_STATE_DIR:-$HOME/.local/state/hpo}; mkdir -p "$pst"
    open_prs > "$pst/cloud-prs-open.$$" 2>/dev/null || rm -f "$pst/cloud-prs-open.$$"
    probe_arm; [ -z "${CONFIRM:-}" ] || confirm_arm; handoff_arm; carry_fold_arm; rm -f "$pst/cloud-prs-open.$$"
    stuck_arm; noreturn_arm; [ -z "$loop" ] && return 0; sleep "$every"; done
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
  owes() { { ledger board 2>/dev/null || :; } | grep -qF -- "$1"; }  # the ledger beside the current LOG owes it
  # push-verdict's stand-in puts review/<pr> after its tip with bus.sh's tree (VERDICT.md,
  # evidence/), and prints `review/<pr> <commit>`, or $STUB_SAYS in place of the commit.
  # It fetches into the bare origin rather than pushing: a push site here would need a PUSHERS
  # entry (ref_privacy.py), keyed on the file, which would also pass an unguarded relay push.
  export RELAY_T=$t; stub=$t/stub.sh; cat > "$stub" <<'EOF'
#!/bin/bash
echo "$1" >> "$RELAY_T/pushed"
s=$(mktemp -d "$RELAY_T/push.XXXXXX"); mkdir -p "$s/w/evidence"; cp "$2" "$s/w/VERDICT.md"; cp -R "$3"/. "$s/w/evidence/"
gd=$(git rev-parse --absolute-git-dir)
tree=$(cd "$s/w" && export GIT_DIR="$gd" GIT_INDEX_FILE="$s/index" GIT_WORK_TREE="$s/w" && git add -A -f . && git write-tree) || exit 1
p=$(git ls-remote origin "refs/heads/review/$1" | awk 'NF { print "-p " $1; exit }')
[ -z "$p" ] || git fetch -q origin "refs/heads/review/$1" || exit 1
o=$(git remote get-url origin) && c=$(git commit-tree "$tree" $p -m "verdict: #$1") \
  && git -C "$o" fetch -q "$gd" "$c:refs/heads/review/$1" || exit 1
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
  # THE STATED LAYOUT RELAYS (P200, R10-REVIEW-CARRY). A cloud reviewer reads fix-review.md,
  # never this script, so the probe is built from the templates that file states -- the ref,
  # the subject, the first line, the nonce line and ev/ -- and must relay (the verdict file's
  # name is this header's alone: policy_lint refuses a path not in the tree). A
  # template the file drops, or one this relay would refuse, fails here instead of on a verdict.
  doc() { # doc <template regex> : the first backticked span in fix-review.md matching it, placeholders filled
    grep -o "\`$1[^\`]*\`" "$HERE/../../../dev/governance/roles/fix-review.md" | head -n 1 | tr -d '\`' \
      | sed -e "s/<pr>/9/g" -e "s/<head40>/$h/g" -e "s/<nonce first 8>/${n:0:8}/g" -e "s/<nonce>/$n/g"; }
  stated() { local ref subj first nl
    ref=$(doc 'probe/rev-'); subj=$(doc 'verdict <pr> '); first=$(doc 'Fix review: merge '); nl=$(doc 'bus-nonce: ')
    grep -q '`ev/`' "$HERE/../../../dev/governance/roles/fix-review.md" || return 3
    [ -n "$ref" ] && [ -n "$subj" ] && [ -n "$first" ] && [ -n "$nl" ] || return 3
    case "$ref$subj$first$nl" in *'<'*) return 3;; esac
    rm -rf "$t/pr"; throwaway_git_init "$t/pr" -q; mkdir "$t/pr/ev"; echo "$h" > "$t/pr/ev/head"
    printf '%s\n\n%s\n' "$first" "$nl" > "$t/pr/verdict.md"
    git -C "$t/pr" add -A; git -C "$t/pr" commit -qm "$subj"
    git -C "$t/o.git" fetch -qf "$t/pr" "HEAD:refs/heads/$ref" || return 3
    relay 9 $n $h; }
  chk "the probe layout fix-review.md states relays" 0 stated
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
  chk "and the log carries no OWED: the verdict stays owed in the ledger" 1 grep -q "^OWED " "$LOG"
  chk "the ledger owes the relayed verdict's posting until a read-back (K17 4b)" 0 owes "verdict-unposted 7 $h Fix review: merge $h"
  mk 7 $h $h $n; out=$(relay 7 $n $h 2>&1)
  chk "UNPOSTED carries the review sha and confirm's last output line, not /dev/null" 0 grep -q "^cloud_relay: UNPOSTED #7: confirm failed: BUS refused 7 $(rtip 7): the poster refused: HTTP 502 " <<< "$out"
  nosha=$t/nosha.sh; printf '#!/bin/sh\necho done\n' > "$nosha"; chmod +x "$nosha"
  mk 7 $h $h $n; HPO_RELAY_PUSH=$nosha; HPO_RELAY_CONFIRM=$cstub; out=$(relay 7 $n $h 2>&1); rc=$?
  chk "a push-verdict that left review/7 without this verdict passes, unposted" 0 test "$rc" = 0
  chk "and UNPOSTED says the remote tip does not carry it" 0 grep -q "^cloud_relay: UNPOSTED #7: review/7's remote tip [0-9a-f]* does not carry this verdict " <<< "$out"
  chk "and the verdict is owed in the ledger, not the log" 0 owes "verdict-unposted 7 $h "
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
  chk "but the ledger owes its posting: a relayed verdict is owed until it is read back" 0 owes "verdict-unposted 7 $h "
  # DELIVERED GUARD (carry 6) and case-colliding ev/ names (carry 8)
  mkf() { # mkf <pr> <content> <ev file>...: a probe ref whose ev/ holds those files, all with that content
    local f p=$1 body=$2; shift 2
    rm -rf "$t/pr"; throwaway_git_init "$t/pr" -q
    for f in "$@"; do mkdir -p "$t/pr/$(dirname "$f")"; echo "$body" > "$t/pr/$f"; done
    printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$h" "$n" > "$t/pr/verdict.md"
    git -C "$t/pr" add -A; git -C "$t/pr" commit -qm "verdict $p $h"
    git -C "$t/o.git" fetch -qf "$t/pr" "HEAD:refs/heads/probe/rev-$p-${n:0:8}"; }
  pushes() { [ -f "$t/pushed" ] && wc -l < "$t/pushed" | tr -d ' ' || echo 0; }
  rm -f "$t/pushed" "$t/state/cloud-relayed"; HPO_RELAY_PUSH=$stub
  mkf 31 first ev/e; out=$(relay 31 $n $h 2>&1); chk "a new tree is pushed (stub called)" 0 test "$(pushes)" = 1
  : > "$t/state/cloud-relayed"; mkf 31 first ev/e; P31=$(git -C "$t/o.git" rev-parse refs/heads/probe/rev-31-${n:0:8})
  out=$(relay 31 $n $h 2>&1); rc=$?
  chk "a tree review/31 already carries relays rc 0 with an emptied ledger" 0 test "$rc" = 0
  chk "and does not call the push stub again" 0 test "$(pushes)" = 1
  chk "and records ref sha in the ledger" 0 grep -qxF "refs/heads/probe/rev-31-${n:0:8} $P31" "$t/state/cloud-relayed"
  chk "and says 'already carries'" 0 grep -q "already carries" <<< "$out"
  mkf 31 second ev/e; out=$(relay 31 $n $h 2>&1); rc=$?
  chk "a different tree (different ev content) is pushed (null control)" 0 test "$rc $(pushes)" = "0 2"
  chk "and does not say 'already carries'" 1 grep -q "already carries" <<< "$out"
  for v in one two three four five; do mkf 32 $v ev/e; relay 32 $n $h >/dev/null 2>&1; done
  : > "$t/state/cloud-relayed"; before=$(pushes); mkf 32 one ev/e; out=$(relay 32 $n $h 2>&1); rc=$?
  chk "the oldest of many review commits is still found (pipefail-safe): skipped" 0 test "$rc $(pushes)" = "0 $before"
  chk "and says so" 0 grep -q "already carries" <<< "$out"
  : > "$t/state/cloud-relayed"; before=$(pushes); GIT_COMMITTER_DATE="@4000000000 +0000" mkf 32 three ev/e; out=$(relay 32 $n $h 2>&1)
  chk "the guard does not depend on the review commit being newer than the probe" 0 test "$(pushes)" = "$before"
  PS=$t/state/pass.log; out=$( (handoff_arm() { :; }; probe_arm() { :; }; stuck_arm() { :; }; noreturn_arm() { :; }; CONFIRM= LOG=$PS; pass) 2>&1 )
  chk "a pass prints its state dir, ledger and log once" 0 test "$(grep -cxF "cloud_relay: state dir $t/state, ledger $t/state/cloud-relayed, log $PS" <<< "$out")" = 1
  out=$( (handoff_arm() { :; }; probe_arm() { :; }; stuck_arm() { :; }; noreturn_arm() { :; }; CONFIRM= LOG=$PS; pass; pass) 2>&1 )
  chk "and once per pass (two passes, two lines)" 0 test "$(grep -c '^cloud_relay: state dir ' <<< "$out")" = 2
  # ev/ names differing only in case (carry 8): refused by name, nothing pushed
  rm -f "$t/pushed"
  # The colliding trees are built in the object database only (hash-object, mktree, commit-tree): no
  # working-tree file with either name is ever created, so this runs the same on APFS and on ext4.
  dbtree() { # <blob> <relative paths, one per line> -> a tree sha; names hold no space
    local blob=$1 list=$2 ents="" top sub
    for top in $(printf '%s\n' "$list" | sed 's|/.*||' | LC_ALL=C sort -u); do
      if printf '%s\n' "$list" | grep -qxF "$top"; then ents="$ents$(printf '100644 blob %s\t%s' "$blob" "$top")"$'\n'
      else sub=$(printf '%s\n' "$list" | grep -F "$top/" | sed "s|^$top/||"); ents="$ents$(printf '040000 tree %s\t%s' "$(dbtree "$blob" "$sub")" "$top")"$'\n'; fi
    done
    printf '%s' "$ents" | git mktree
  }
  mkdb() { # mkdb <pr> <ev path>...: a probe ref whose ev/ holds those paths, built without a working tree
    local p=$1 bl vb et rt c; shift
    rm -rf "$t/pr"; throwaway_git_init "$t/pr" -q
    bl=$(echo x | git -C "$t/pr" hash-object -w --stdin)
    vb=$(printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$h" "$n" | git -C "$t/pr" hash-object -w --stdin)
    et=$(cd "$t/pr" && dbtree "$bl" "$(printf '%s\n' "$@" | sed 's|^ev/||')")
    rt=$(printf '040000 tree %s\tev\n100644 blob %s\tverdict.md\n' "$et" "$vb" | git -C "$t/pr" mktree)
    c=$(git -C "$t/pr" commit-tree "$rt" -m "verdict $p $h")
    git -C "$t/pr" update-ref refs/heads/mkdb "$c"
    git -C "$t/o.git" fetch -qf "$t/pr" "refs/heads/mkdb:refs/heads/probe/rev-$p-${n:0:8}"
    [ -z "$(ls -A "$t/pr" | grep -v '^\.git$')" ]; }  # rc 0: the work tree holds nothing but .git
  tar() { echo x >> "$t/tar.calls"; command tar "$@"; }
  mkdb 41 ev/HEAD.txt ev/head.txt; chk "the fixture never materialises a name (work tree empty)" 0 test "$?" = 0
  mkdb 41 ev/HEAD.txt ev/head.txt; rm -f "$t/tar.calls"; TD=$(mktemp -d "$t/tmpdir.XXXXXX"); out=$(TMPDIR=$TD relay 41 $n $h 2>&1); rc=$?
  chk "refused before any write: nothing was extracted (tar never ran)" 0 test ! -e "$t/tar.calls"
  chk "and no scratch directory was created (TMPDIR still empty)" 0 test -z "$(ls -A "$TD")"
  mkdb 42 ev/head.txt ev/other.txt; rm -f "$t/tar.calls"; out=$(TMPDIR=$TD relay 42 $n $h 2>&1)
  chk "null control: distinct names do run the extract" 0 test -e "$t/tar.calls"
  unset -f tar
  rm -f "$t/pushed"
  mkdb 41 ev/HEAD.txt ev/head.txt; out=$(relay 41 $n $h 2>&1); rc=$?
  chk "ev_case_collision names both, from the commit alone" 0 grep -Eq "^ev/HEAD.txt and ev/head.txt$|^ev/head.txt and ev/HEAD.txt$" <<< "$(ev_case_collision "$(git -C "$t/o.git" rev-parse refs/heads/probe/rev-41-${n:0:8})")"
  chk "ev/HEAD.txt and ev/head.txt are refused rc 2" 0 test "$rc" = 2
  chk "naming both files" 0 grep -Eq "HEAD.txt and ev/head.txt|head.txt and ev/HEAD.txt" <<< "$out"
  chk "with nothing pushed" 0 test ! -s "$t/pushed"
  mkdb 41 ev/A ev/a/x; out=$(relay 41 $n $h 2>&1); rc=$?
  chk "a file ev/A and a directory ev/a/x are refused rc 2" 0 test "$rc $(pushes)" = "2 0"
  mkf 41 x ev/head.txt ev/other.txt; chk "distinct names relay (null control)" 0 relay 41 $n $h
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
  # Carry 30: a rev-/revt- ref the orchestrator disposed at its sha is not relayed; once it moves it is relayed at the new sha.
  rm -f "$t/state/cloud-relayed" "$t/state/cloud-relayed.refused" "$t/state/cloud-relayed.refused-why" "$t/state/cloud-relayed.tries" "$t/pushed"
  R30=refs/heads/probe/rev-5-${n:0:8}; mk 5 $h $h $n; probe_arm >/dev/null 2>&1
  chk "null control: an undisposed rev- ref is relayed (pushed for #5)" 0 test "$(cat "$t/pushed" 2>/dev/null)" = 5
  mk 5 $h $h $n; P30=$(git -C "$t/o.git" rev-parse "$R30"); dispose "$R30" "$P30" >/dev/null; rm -f "$t/pushed"; T30=$(rtip 5); probe_arm >/dev/null 2>&1
  chk "a rev- ref disposed at its sha is not relayed: nothing pushed, review/5 unmoved" 0 test ! -s "$t/pushed" -a "$(rtip 5)" = "$T30" -a -z "$(grep -x "$R30 $P30" "$t/state/cloud-relayed")"
  mk 5 $h $h $n; P30B=$(git -C "$t/o.git" rev-parse "$R30"); probe_arm >/dev/null 2>&1
  chk "null control: a disposed ref whose tip moved is relayed at the new sha" 0 test "$P30B" != "$P30" -a "$(cat "$t/pushed" 2>/dev/null)" = 5 -a -n "$(grep -x "$R30 $P30B" "$t/state/cloud-relayed")"
  # A verdict returned at the handoff (Carry 0): probe/revt-<topic>-<n8>, held until the topic's PR opens (bus.sh rekey),
  # relayed when review_carry answers CARRY for handoff-head..PR-head, refused as stale when it does not.
  LOG=$t/topicv.log; LV=$LOG.level; : > "$LOG"; rm -f "$LV" "$t/state/cloud-relayed" "$t/state/cloud-relayed.refused" "$t/state/cloud-relayed.refused-why" "$t/state/cloud-relayed.tries"
  th=1111111111111111111111111111111111111111; tn=fedcba9876543210fedcba9876543210; PH=2222222222222222222222222222222222222222
  rm -f "$t/bus/dispatched" "$t/bus/rekeyed"; printf 'topic:tp-1 %s cthread %s 2026-11-08T00:00:00Z sonnet\n' "$th" "$tn" > "$t/bus/dispatched"
  mkt() { # mkt <topic> <head>: the reviewer's probe/revt-<topic>-<n8> ref
    rm -rf "$t/pr"; throwaway_git_init "$t/pr" -q; mkdir "$t/pr/ev"; echo "$((c=c+1)) $2" > "$t/pr/ev/e"
    printf 'Fix review: merge %s\n\nbus-nonce: %s\n' "$2" "$tn" > "$t/pr/verdict.md"
    git -C "$t/pr" add -A; git -C "$t/pr" commit -qm "verdict $1 $2"
    git -C "$t/o.git" fetch -qf "$t/pr" "HEAD:refs/heads/probe/revt-$1-${tn:0:8}"; }
  mkt tp-1 $th; : > "$t/pushed"
  cstubok=$t/carry-ok.sh; printf '#!/bin/sh\necho "$@" > "%s/carry.args"\necho "review_carry: CARRY"; exit 0\n' "$t" > "$cstubok"
  cstubno=$t/carry-no.sh; printf '#!/bin/sh\necho "review_carry: FRESH-REVIEW"; exit 1\n' > "$cstubno"
  cstubun=$t/carry-un.sh; printf '#!/bin/sh\necho "review_carry: CANNOT DECIDE"; exit 2\n' > "$cstubun"
  chmod +x "$cstubok" "$cstubno" "$cstubun"; phstub=$t/ph.sh; printf '#!/bin/sh\necho %s\n' "$PH" > "$phstub"; chmod +x "$phstub"
  export HPO_RELAY_PRHEAD=$phstub HPO_RELAY_CARRY=$cstubok
  out=$(probe_arm 2>&1)
  chk "a handoff verdict whose topic has no pull request is reported HELD-NOPR" 0 grep -q "^cloud_relay: HELD-NOPR refs/heads/probe/revt-tp-1-${tn:0:8} " <<< "$out"
  chk "and is owed on the level as handoff-verdict-held, every pass" 0 grep -q "^OWED .* handoff-verdict-held refs/heads/probe/revt-tp-1-${tn:0:8} " "$LV"
  chk "and is never posted: nothing pushed, nothing relayed" 0 test ! -s "$t/pushed" -a ! -s "$t/state/cloud-relayed"
  printf 'tp-1 %s 71\n' "$th" > "$t/bus/rekeyed"; printf '71 %s cthread %s 2026-11-08T00:00:00Z sonnet\n' "$th" "$tn" >> "$t/bus/dispatched"
  export HPO_RELAY_CARRY=$cstubno; out=$(probe_arm 2>&1)
  chk "a PR head that does not carry (a conflict resolution) is HELD-STALE, naming the re-dispatch" 0 grep -q "HELD-STALE refs/heads/probe/revt-tp-1-${tn:0:8} .*re-dispatch: bus.sh dispatch 71 $PH" <<< "$out"
  chk "the stale verdict is posted nowhere: nothing pushed" 0 test ! -s "$t/pushed"
  chk "and is refused with its reason in the level until disposed" 0 grep -q "^OWED .* probe-refused refs/heads/probe/revt-tp-1-${tn:0:8} .*FRESH-REVIEW" "$LV"
  chk "the held level line is gone once the PR opened (a level is rewritten)" 1 grep -q "handoff-verdict-held" "$LV"
  rm -f "$t/state/cloud-relayed.refused" "$t/state/cloud-relayed.refused-why" "$LV"; export HPO_RELAY_CARRY=$cstubun; out=$(probe_arm 2>&1)
  chk "an undecidable range retries next pass: not relayed, not refused" 0 test ! -s "$t/pushed" -a ! -e "$t/state/cloud-relayed.refused"
  export HPO_RELAY_CARRY=$cstubok; out=$(probe_arm 2>&1)
  chk "null control: the same verdict over a head that carries is relayed at the handoff head, on #71" 0 test "$(cat "$t/pushed")" = 71
  chk "and the carry predicate was asked handoff-head then PR-head" 0 grep -qx "$th $PH --verdict-only" "$t/carry.args"
  chk "and its ref and sha are recorded as relayed" 0 grep -q "^refs/heads/probe/revt-tp-1-${tn:0:8} " "$t/state/cloud-relayed"
  mkt tp-1 $th; RT30=refs/heads/probe/revt-tp-1-${tn:0:8}; PT30=$(git -C "$t/o.git" rev-parse "$RT30"); dispose "$RT30" "$PT30" >/dev/null; : > "$t/pushed"; out=$(probe_arm 2>&1)
  chk "Carry 30: a revt- ref disposed at its sha is not relayed either" 0 test ! -s "$t/pushed" -a -z "$(grep -x "$RT30 $PT30" "$t/state/cloud-relayed")"
  mkt tp-1 $th; probe_arm >/dev/null 2>&1
  chk "and a disposed revt- ref that moved is relayed at its new sha (null control)" 0 test "$(cat "$t/pushed")" = 71
  unset HPO_RELAY_PRHEAD HPO_RELAY_CARRY
  # PENDING-CI drafts (R10-CLOUD-POOL carry 5): a verdict carrying `pending-ci:` posts only when classify reads its head GREEN.
  rm -f "$t/state/cloud-relayed" "$t/pushed"; HPO_RELAY_PUSH=$stub; CONFIRM=
  clstub=$t/classify.sh; printf '#!/bin/sh\necho "$@" > "%s/classify.args"\ncase "$(cat "%s/cls")" in 0) echo GREEN;; 3) echo "WAIT tests / fast gate";; 1) echo "RED tests / fast gate red: x";; *) echo boom;; esac\nexit "$(cat "%s/cls")"\n' "$t" "$t" "$t" > "$clstub"; chmod +x "$clstub"
  phh=$t/ph-h.sh; printf '#!/bin/sh\necho %s\n' "$h" > "$phh"; chmod +x "$phh"; phm=$t/ph-m.sh; printf '#!/bin/sh\necho %s\n' "$PH" > "$phm"; chmod +x "$phm"
  mkp() { mk 72 $h $h $n; rm -rf "$t/pr"; throwaway_git_init "$t/pr" -q; mkdir "$t/pr/ev"; echo "pc $h $((c=c+1))" > "$t/pr/ev/e"
    printf 'Fix review: merge %s\n\nbus-nonce: %s\npending-ci: tests / fast gate\n' "$h" "$n" > "$t/pr/verdict.md"
    git -C "$t/pr" add -A; git -C "$t/pr" commit -qm "verdict 72 $h"; git -C "$t/o.git" fetch -qf "$t/pr" "HEAD:refs/heads/probe/rev-72-${n:0:8}"; }
  export HPO_RELAY_CLASSIFY=$clstub HPO_RELAY_PRHEAD=$phh; mkp
  echo 3 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
  chk "a pending-ci draft over a WAIT head is held (rc 75), one HELD-PENDING-CI line naming the context" 0 test "$rc" = 75 -a -n "$(grep -m1 'HELD-PENDING-CI #72 .*tests / fast gate' <<< "$out")"
  chk "and nothing is pushed or recorded while it is held" 0 test ! -s "$t/pushed" -a ! -s "$t/state/cloud-relayed"
  chk "classify was asked the head and the PR" 0 grep -qx "$h --repo tvofi/heatpump_optimizer --pr 72" "$t/classify.args"
  echo 1 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
  chk "a pending-ci draft over a RED head is held (rc 75), naming the red, not refused (R10-REVIEW-DISPATCH-RESIDUE carry 23)" 0 test "$rc" = 75 -a -n "$(grep -m1 "HELD-PENDING-CI-RED #72 $h: tests / fast gate red: x (classify RED)" <<< "$out")"
  export HPO_RELAY_PRHEAD=$phm HPO_RELAY_CARRY=$cstubno; echo 0 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
  chk "a pending-ci draft whose PR head moved is refused (rc 2), naming both heads, though CI is green" 0 test "$rc" = 2 -a -n "$(grep -m1 "drafted at $h, #72 is at $PH" <<< "$out")"
  export HPO_RELAY_PRHEAD=$phh; echo 9 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
  chk "an unreadable classify holds the draft (rc 75), never reads it as green" 0 test "$rc" = 75 -a ! -s "$t/pushed"
  echo 0 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
  chk "null control: the same draft over a GREEN head at the same head relays on #72" 0 test "$rc" = 0 -a "$(cat "$t/pushed")" = 72
  rm -f "$t/state/cloud-relayed" "$t/pushed"; mk 72 $h $h $n; echo 3 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
  chk "null control: a verdict with no pending-ci line never asks classify (a WAIT head still relays)" 0 test "$rc" = 0 -a "$(cat "$t/pushed")" = 72
  # Carry 21: a moved head is asked of review_carry; CARRY classifies the LIVE head and posts on GREEN.
  rm -f "$t/state/cloud-relayed" "$t/pushed" "$t/carry.args" "$t/classify.args"; mkp
  export HPO_RELAY_PRHEAD=$phm HPO_RELAY_CARRY=$cstubok; echo 0 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
  chk "moved head + review_carry CARRY + GREEN at the live head posts on #72, saying the verdict was carried" 0 test "$rc" = 0 -a "$(cat "$t/pushed")" = 72 -a -n "$(grep -m1 'GREEN.*verdict carried from' <<< "$out")"
  chk "and review_carry was asked drafted head then live head, and classify the live head" 0 grep -qx "$h $PH --verdict-only" "$t/carry.args" -a "$(cut -d' ' -f1 "$t/classify.args")" = "$PH"
  rm -f "$t/state/cloud-relayed" "$t/pushed"; mkp; export HPO_RELAY_CARRY=$cstubno; out=$(relay 72 $n $h 2>&1); rc=$?
  chk "moved head + review_carry FRESH-REVIEW + GREEN refuses (rc 2), posts nothing, owes the re-dispatch" 0 test "$rc" = 2 -a ! -s "$t/pushed" -a -n "$(grep -m1 "^cloud_relay: OWED re-dispatch #72 $PH" <<< "$out")"
  export HPO_RELAY_CARRY=$cstubun; out=$(relay 72 $n $h 2>&1); rc=$?
  chk "moved head + review_carry CANNOT DECIDE refuses as today (rc 2)" 0 test "$rc" = 2 -a ! -s "$t/pushed"
  export HPO_RELAY_CARRY=$cstubok; echo 3 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
  chk "moved head + CARRY + WAIT at the live head holds (rc 75), naming the live head" 0 test "$rc" = 75 -a ! -s "$t/pushed" -a -n "$(grep -m1 "HELD-PENDING-CI #72 $PH" <<< "$out")"
  echo 1 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
  chk "moved head + CARRY + RED at the live head posts nothing (held rc 75, the red is not the carry's to post over)" 0 test "$rc" = 75 -a ! -s "$t/pushed"
  rm -f "$t/state/cloud-pending-red"
  export HPO_RELAY_PRHEAD=$phh; rm -f "$t/carry.args"; echo 0 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
  chk "null control: the same head + GREEN posts as today and never asks review_carry" 0 test "$rc" = 0 -a "$(cat "$t/pushed")" = 72 -a ! -e "$t/carry.args"
  # Carry 23: RED holds (rc 75) and is refused only past the bound since its first read at that head.
  rm -f "$t/state/cloud-relayed" "$t/pushed" "$t/state/cloud-pending-red"; mkp; echo 1 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
  chk "RED records its first read in the state dir, keyed ref sha head" 0 grep -qE "^refs/heads/probe/rev-72-${n:0:8} [0-9a-f]{40} $h [0-9]+$" "$t/state/cloud-pending-red"
  echo 1 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
  chk "a second RED pass holds again and keeps the first read (one record)" 0 test "$rc" = 75 -a "$(grep -c . "$t/state/cloud-pending-red")" = 1
  echo 0 > "$t/cls"; out=$(relay 72 $n $h 2>&1); rc=$?
  chk "RED, then GREEN at the same head, posts on #72 and clears the record" 0 test "$rc" = 0 -a "$(cat "$t/pushed")" = 72 -a ! -s "$t/state/cloud-pending-red"
  rm -f "$t/state/cloud-relayed" "$t/pushed"; mkp; echo 1 > "$t/cls"; relay 72 $n $h >/dev/null 2>&1; echo 3 > "$t/cls"; relay 72 $n $h >/dev/null 2>&1
  chk "a WAIT read between two REDs clears the record (a check ran, so the clock restarts)" 0 test ! -s "$t/state/cloud-pending-red"
  echo 1 > "$t/cls"; relay 72 $n $h >/dev/null 2>&1; export HPO_RELAY_PENDING_RED_SECS=0; out=$(relay 72 $n $h 2>&1); rc=$?
  chk "RED past the bound refuses (rc 2), prints the OWED re-dispatch line, posts nothing" 0 test "$rc" = 2 -a ! -s "$t/pushed" -a -n "$(grep -m1 "^cloud_relay: OWED re-dispatch #72 $h$" <<< "$out")"
  chk "and the first RED read never refuses, whatever the bound (null control: nothing to age yet)" 0 test "$(rm -f "$t/state/cloud-pending-red"; relay 72 $n $h >/dev/null 2>&1; echo $?)" = 75
  # a non-numeric bound is refused before classify is read: GREEN would otherwise post
  rm -f "$t/state/cloud-relayed" "$t/pushed" "$t/state/cloud-pending-red"; mkp; echo 0 > "$t/cls"; export HPO_RELAY_PENDING_RED_SECS=abc; out=$(relay 72 $n $h 2>&1); rc=$?
  chk "a non-numeric HPO_RELAY_PENDING_RED_SECS holds the pending-ci draft (rc 75), says why, and posts nothing even at GREEN" 0 test "$rc" = 75 -a ! -s "$t/pushed" -a -n "$(grep -m1 'HPO_RELAY_PENDING_RED_SECS must be seconds' <<< "$out")"
  export HPO_RELAY_PENDING_RED_SECS=60; out=$(relay 72 $n $h 2>&1); rc=$?
  chk "null control: a numeric bound at the same GREEN head posts" 0 test "$rc" = 0 -a "$(cat "$t/pushed")" = 72
  unset HPO_RELAY_PENDING_RED_SECS HPO_RELAY_CARRY; rm -f "$t/state/cloud-pending-red"
  unset HPO_RELAY_CLASSIFY HPO_RELAY_PRHEAD
  # the handoff arm (a bare origin holds PR branches, handoff/ and handoff-body/ refs)
  unset HPO_RELAY_PUSH; export HPO_RELAY_PUSH=$stub; LOG=$t/pass.log; : > "$LOG"; CONFIRM=
  prs=$t/prs.tsv; ustub=$t/ustub.sh; dstub=$t/dstub.sh; astub=$t/astub.sh; N40=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
  hc() { git -C "$t/pr" -c user.name=t -c user.email=t@t commit -q --allow-empty -m "$1"; }
  mkref() { git -C "$t/o.git" fetch -qf "$t/pr" "HEAD:refs/heads/$1"; [ "$1" = handoff/topic-a ] && [ -f "$t/b/BODY.md" ] && mkref2; return 0; }
  rm -rf "$t/m"; throwaway_git_init "$t/m" -q; git -C "$t/m" -c user.name=t -c user.email=t@t commit -q --allow-empty -m main
  git -C "$t/o.git" fetch -qf "$t/m" "HEAD:refs/heads/main"
  rm -rf "$t/pr"; throwaway_git_init "$t/pr" -q; hc base; mkref fix/topic-a-pr; PRH=$(git -C "$t/pr" rev-parse HEAD)
  printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"
  printf '#!/bin/sh\ncat "%s"\n' "$prs" > "$t/lister.sh"; chmod +x "$t/lister.sh"; export HPO_RELAY_PRS=$t/lister.sh
  : > "$t/merged.tsv"; printf '#!/bin/sh\ncat "%s"\n' "$t/merged.tsv" > "$t/mlister.sh"; chmod +x "$t/mlister.sh"; export HPO_RELAY_MERGED=$t/mlister.sh
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
  git -C "$t/b" add BODY.md; git -C "$t/b" -c user.name=t -c user.email=t@t commit -qm body; mkref2() { # the body names the handoff tip it is pushed against (HELD-BODY otherwise)
    { grep -v '^Code head: ' "$t/b/BODY.md"; echo "Code head: $(git -C "$t/o.git" rev-parse refs/heads/handoff/topic-a)"; } > "$t/b/BODY.new"; mv "$t/b/BODY.new" "$t/b/BODY.md"
    git -C "$t/b" diff --quiet || git -C "$t/b" -c user.name=t -c user.email=t@t commit -qa --amend --no-edit
    git -C "$t/o.git" fetch -qf "$t/b" "HEAD:refs/heads/handoff-body/topic-a"; }; mkref2
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
  chk "reviewer-fire is opened in the ledger with pr, head and nonce" 0 owes "reviewer-fire 41 $N40 nonce=0123456789abcdef0123456789abcdef"
  chk "and the log carries no OWED line" 1 grep -q "OWED" "$LOG"
  # null control: the PR head now contains the handoff -> nothing more
  git -C "$t/pr" -c user.name=t -c user.email=t@t merge -q --no-edit -m m "$HS" 2>/dev/null; git -C "$t/pr" reset -q --hard "$HS"; hc "pr tip"; mkref fix/topic-a-pr; NEW=$(git -C "$t/pr" rev-parse HEAD)
  printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$NEW" > "$prs"; rm -f "$t/updated"
  handoff_arm >/dev/null 2>&1
  chk "a handoff already merged into its PR does nothing (null control)" 0 test ! -e "$t/updated"
  # the hold file: a listed PR is skipped with one HELD line per pass; a malformed file refuses the pass
  hf=$t/state/cloud-handoff-hold; hu=$t/hu.sh; printf '#!/bin/sh\necho "$1 $2${HPO_UPDATE_BODY_ONLY:+ body-only}" >> "%s/hupdated"\n' "$t" > "$hu"; chmod +x "$hu"; HPO_RELAY_UPDATE=$hu
  printf '41\n' > "$hf"; ho=$(handoff_arm 2>&1)
  chk "a held PR whose handoff is already in its head prints no HELD (nothing to hold)" 1 grep -q HELD <<< "$ho"
  rm -f "$t/updated" "$t/hupdated" "$t/state/cloud-handoff-failed" "$t/events.tsv"; : > "$LOG"; rm -f "$t/state/cloud-handoff-failed.tries"
  git -C "$t/pr" reset -q --hard "$PRH"; mkref fix/topic-a-pr; printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"
  printf '99\n41\n' > "$hf"; ho=$(handoff_arm 2>&1)
  chk "a held PR whose handoff is ahead is not updated" 0 test ! -e "$t/hupdated"
  chk "and prints HELD with the handoff tip it did not apply" 0 grep -q "HELD #41 $HS\$" <<< "$ho"
  chk "the HELD line is printed once per pass" 0 test "$(grep -c '^cloud_relay: HELD ' <<< "$ho")" = 1
  chk "and the held pass dispatches no reviewer" 1 owes "reviewer-fire"
  hc held-moved; mkref handoff/topic-a; HS2=$(git -C "$t/pr" rev-parse HEAD)
  ho=$(handoff_arm 2>&1)
  chk "a held PR whose handoff tip moved is still not updated" 0 test ! -e "$t/hupdated"
  chk "and HELD names the moved tip" 0 grep -q "HELD #41 $HS2\$" <<< "$ho"
  echo "topic-a $HS2" > "$t/state/cloud-handoff-failed"; ho=$(handoff_arm 2>&1)
  chk "a hold outranks a recorded failed update: still HELD" 0 grep -q "HELD #41 $HS2\$" <<< "$ho"
  rm -f "$t/state/cloud-handoff-failed"; rm -f "$t/state/cloud-handoff-failed.tries"
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
  # the freeze (R10-FLOW-ROSTER-FREEZE (a), P-H): handoff/topic-a ($HS2) is ahead of #41's head $PRH
  HPO_RELAY_UPDATE=$hu; rf=$t/state/cloud-handoff-release; cp "$t/bus/dispatched" "$t/bus/dispatched.keep"
  mkv() { rm -rf "$t/v"; throwaway_git_init "$t/v" -q; git -C "$t/v" -c user.name=t -c user.email=t@t commit -q --allow-empty -m "$1"
    git -C "$t/o.git" fetch -qf "$t/v" "HEAD:refs/heads/verdict/41"; }
  frz() { rm -f "$t/hupdated"; ho=$(handoff_arm 2>&1); }
  mkv "verdict: #41 Fix review: merge $PRH"; frz
  chk "a merge verdict at the head holds the handoff ahead: no update_pr call" 0 test ! -e "$t/hupdated"
  chk "and prints HELD-VERDICT with the handoff tip" 0 grep -q "^cloud_relay: HELD-VERDICT #41 $HS2 " <<< "$ho"
  chk "and names the release" 0 grep -qF "list #41 in $rf" <<< "$ho"
  frz
  chk "the HELD-VERDICT line is printed once per pass" 0 test "$(grep -c '^cloud_relay: HELD-VERDICT ' <<< "$ho")" = 1
  chk "and owes handoff-held in the level once after two passes" 0 test "$(grep -c "^OWED .* handoff-held refs/heads/handoff/topic-a $HS2 #41 VERDICT\$" "$LOG.level")" = 1
  chk "and the event log carries no level line" 1 grep -q handoff-held "$LOG"
  mkv "verdict: #41 Fix review: merge $h"; frz
  chk "a merge verdict naming an older head still updates (null control)" 0 grep -q "^fix/topic-a-pr $HS2\$" "$t/hupdated"
  chk "and prints no HELD" 1 grep -q HELD <<< "$ho"
  chk "and a pass that holds nothing drops handoff-held from the level" 1 grep -q handoff-held "$LOG.level"
  mkv "verdict: #41 Fix review: blocked $PRH carry-missing: x"; frz
  chk "a blocked verdict at the head still updates (null control)" 0 test -e "$t/hupdated"
  mkv "verdict: #41 Fix review: merge ${PRH}x"; frz
  chk "a merge verdict whose head is not exactly the live head still updates" 0 test -e "$t/hupdated"
  git -C "$t/o.git" update-ref -d refs/heads/verdict/41; frz
  chk "no verdict ref and no review updates (null control)" 0 test -e "$t/hupdated"
  # a verdict ref the listing names but the fetch cannot read is UNREAD, and frozen: an unread
  # verdict may be a merge at the head (#2792 review: mutant R1 dropped this arm unseen)
  printf '%s\trefs/heads/verdict/41\n' ffffffffffffffffffffffffffffffffffffffff > "$t/vl"
  chk "a listed verdict ref the fetch cannot find freezes the head (rc 0)" 0 review_freeze 41 "$PRH" "$t/vl"
  chk "and says UNREAD" 0 test "$(review_freeze 41 "$PRH" "$t/vl")" = UNREAD
  mkv "verdict: #41 Fix review: merge $h"
  chk "a listed sha the fetched ref does not carry (it moved since the listing) is UNREAD too" 0 test "$(review_freeze 41 "$PRH" "$t/vl")" = UNREAD
  printf '%s\trefs/heads/verdict/41\n' "$(git -C "$t/o.git" rev-parse refs/heads/verdict/41)" > "$t/vl"
  chk "the same ref listed at its own sha, a verdict at an older head, freezes nothing (null control)" 1 review_freeze 41 "$PRH" "$t/vl"
  git -C "$t/o.git" update-ref -d refs/heads/verdict/41
  # a review in flight: a dispatch of #41 at its head, until a verdict at that head posts
  printf '41 %s cloud %s 2026-10-29T17:07:00Z -\n' "$PRH" "$n" >> "$t/bus/dispatched"; frz
  chk "a dispatch at the head with no verdict holds the handoff: no update_pr call" 0 test ! -e "$t/hupdated"
  chk "and prints HELD-REVIEW naming the dispatch's nonce prefix and time (P288)" 0 \
    grep -q "^cloud_relay: HELD-REVIEW #41 $HS2 dispatch=${n:0:8} at=2026-10-29T17:07:00Z (" <<< "$ho"
  chk "and owes handoff-held REVIEW with that evidence in the level" 0 \
    grep -q "^OWED .* handoff-held refs/heads/handoff/topic-a $HS2 #41 REVIEW dispatch=${n:0:8} at=2026-10-29T17:07:00Z\$" "$LOG.level"
  mkv "verdict: #41 Fix review: merge $h"; frz
  chk "a verdict at an older head does not dispose the review: still HELD-REVIEW" 0 grep -q "HELD-REVIEW #41 " <<< "$ho"
  mkv "verdict: #41 Fix review: blocked $PRH carry-missing: x"; frz
  chk "once a verdict at the head posts, the held edits land: update_pr runs" 0 grep -q "^fix/topic-a-pr $HS2\$" "$t/hupdated"
  mkv "verdict: #41 Fix review: merge $PRH"; frz
  chk "a posted merge verdict at the head turns the review hold into HELD-VERDICT" 0 grep -q "HELD-VERDICT #41 " <<< "$ho"
  git -C "$t/o.git" update-ref -d refs/heads/verdict/41; cp "$t/bus/dispatched.keep" "$t/bus/dispatched"
  printf '41 %s cloud %s\n' "$h" "$n" >> "$t/bus/dispatched"; frz
  chk "a dispatch at an older head holds nothing (null control)" 0 test -e "$t/hupdated"
  cp "$t/bus/dispatched.keep" "$t/bus/dispatched"
  printf '42 %s cloud %s\n' "$PRH" "$n" >> "$t/bus/dispatched"; frz
  chk "a dispatch of another PR at the same head holds nothing (null control)" 0 test -e "$t/hupdated"
  cp "$t/bus/dispatched.keep" "$t/bus/dispatched"
  # P288: a detached worktree at the head is no review (the opener's and updater's sit there);
  # only the dispatch record holds. The #2953 shape: handoff ahead, no verdict, no dispatch record.
  git worktree add -q --detach "$t/rw" "$PRH" 2>/dev/null; frz
  chk "a detached worktree at the head with no dispatch record updates (the #2953 shape)" 0 test -e "$t/hupdated"
  chk "and prints no HELD-REVIEW" 1 grep -q "HELD-REVIEW #41 " <<< "$ho"
  printf '41 %s cloud %s\n' "$PRH" "$n" >> "$t/bus/dispatched"; frz
  chk "the same with a dispatch record at the head holds (a record without a time says at=-)" 0 \
    grep -q "HELD-REVIEW #41 $HS2 dispatch=${n:0:8} at=- (" <<< "$ho"
  cp "$t/bus/dispatched.keep" "$t/bus/dispatched"
  git worktree remove --force "$t/rw"
  # the release: the orchestrator passes the freeze over a listed PR; the hold file outranks it
  mkv "verdict: #41 Fix review: merge $PRH"; printf '41\n' > "$rf"; frz
  chk "a released PR with a merge verdict at its head is updated" 0 test -e "$t/hupdated"
  printf '141\n' > "$rf"; frz
  chk "a released #141 does not release #41 (whole-line match)" 0 grep -q "HELD-VERDICT #41 " <<< "$ho"
  printf '41\n' > "$rf"; printf '41\n' > "$hf"; frz
  chk "a held and released PR is HELD: the hold outranks the release" 0 grep -q "^cloud_relay: HELD #41 " <<< "$ho"
  chk "and not updated" 0 test ! -e "$t/hupdated"
  rm -f "$hf"; printf '4x\n' > "$rf"; frz
  chk "a malformed release file refuses the pass (rc 2)" 2 handoff_arm
  chk "and updates nothing" 0 test ! -e "$t/hupdated"
  chk "and owes handoff-hold-malformed naming the release file" 0 grep -q "^OWED .* handoff-hold-malformed $rf -\$" "$LOG.level"
  rm -f "$rf"; git -C "$t/o.git" update-ref -d refs/heads/verdict/41; rm -f "$t/hupdated" "$t/bus/dispatched.keep"; HPO_RELAY_UPDATE=$ustub; : > "$LOG"
  # P283: the update runs from the relay's own tools tree, levelled to origin/main, never from
  # this checkout. The scratch main carries a stand-in update_pr.sh holding pr_tools_fresh's test.
  rm -rf "$t/tm"; throwaway_git_init "$t/tm" -q; mkdir -p "$t/tm/tools/audit/seat"
  printf '#!/bin/bash\nd=$(cd "$(dirname "$0")" && pwd)\nn=$(git -C "$d" rev-list --count HEAD..origin/main -- :/tools)\n[ "$n" = 0 ] || { echo "REFUSE STALE CHECKOUT behind by $n"; exit 1; }\necho "$(git -C "$d" rev-parse HEAD) $1 $2" >> "%s/tupdated"\n' "$t" > "$t/tm/tools/audit/seat/update_pr.sh"
  tmc() { git -C "$t/tm" add -A && git -C "$t/tm" -c user.name=t -c user.email=t@t commit -qm "$1"; }
  tmc tools-a; TA=$(git -C "$t/tm" rev-parse HEAD); echo b > "$t/tm/tools/audit/seat/x"; tmc tools-b; TB=$(git -C "$t/tm" rev-parse HEAD)
  git -C "$t/o.git" fetch -qf "$t/tm" "HEAD:refs/heads/main"; git fetch -q origin main
  TW=$t/state/relay-tools; git worktree add -q --detach "$TW" "$TA"
  # The relay's own checkout, stale: a copy of the seat whose update_pr.sh refuses as the guard would.
  rm -rf "$t/seat"; cp -R "$HERE" "$t/seat"; printf '#!/bin/bash\necho "REFUSE STALE CHECKOUT (the relay checkout)"; exit 1\n' > "$t/seat/update_pr.sh"
  keep_here=$HERE; HERE=$t/seat; rm -f "$t/tupdated"
  ho=$(HPO_RELAY_UPDATE= handoff_arm 2>&1)
  chk "a relayed update runs from the levelled tools tree, at origin/main, and passes the guard (P283)" 0 \
    test "$(cat "$t/tupdated" 2>/dev/null)" = "$TB fix/topic-a-pr $HS2"
  chk "the tools tree was moved from the commit behind to origin/main" 0 test "$(git -C "$TW" rev-parse HEAD)" = "$TB"
  chk "and its lock is released after the update" 0 test ! -e "$TW.lock"
  chk "the relay's own checkout is never moved or run" 1 grep -q "the relay checkout" <<< "$ho"
  git -C "$TW" checkout -q --detach "$TA"; echo dirty >> "$TW/tools/audit/seat/update_pr.sh"; rm -f "$t/tupdated" "$t/state/cloud-handoff-failed"
  ho=$(HPO_RELAY_UPDATE= handoff_arm 2>&1)
  chk "null control: a dirty tools tree is refused by name, no update runs" 0 \
    grep -q "REFUSED the update of #41: the relay's tools tree $TW is dirty" <<< "$ho"
  chk "and the tree is left untouched (its commit and its edit)" 0 \
    test "$(git -C "$TW" rev-parse HEAD) $(tail -n 1 "$TW/tools/audit/seat/update_pr.sh")" = "$TA dirty"
  chk "and the refusal is owed on the level, unrecorded, so the next pass retries" 0 \
    test "$(grep -c "handoff-update refs/heads/handoff/topic-a $HS2 the relay's tools tree .* is dirty" "$LOG.level")" = 1 -a ! -e "$t/tupdated"
  chk "and not noted as a failed update" 0 test -z "$(grep -s "topic-a $HS2" "$t/state/cloud-handoff-failed")"
  git -C "$TW" checkout -q -- .; sleep 30 & lp=$!; mkdir "$TW.lock"; echo "$lp" > "$TW.lock/pid"
  ho=$(HPO_RELAY_UPDATE= handoff_arm 2>&1)
  chk "a tools tree held by a live relay is busy: no update, no level line" 0 \
    test -n "$(grep "is busy (pid $lp)" <<< "$ho")" -a ! -e "$t/tupdated"
  kill "$lp"; wait "$lp" 2>/dev/null
  ho=$(HPO_RELAY_UPDATE= handoff_arm 2>&1)
  chk "a lock whose pid is dead is taken over and the update runs" 0 test "$(cat "$t/tupdated" 2>/dev/null)" = "$TB fix/topic-a-pr $HS2"
  HERE=$keep_here; git worktree remove --force "$TW"; rm -rf "$TW.lock" "$t/tupdated" "$t/seat"
  git -C "$t/o.git" fetch -qf "$t/m" "HEAD:refs/heads/main"; git fetch -q origin main 2>/dev/null; : > "$LOG"; rm -f "$LOG.level" "$t/state/cloud-handoff-failed"
  # a failing update is noted once and not retried
  rm -f "$t/updated"; git -C "$t/pr" reset -q --hard "$PRH"; mkref fix/topic-a-pr
  printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"; : > "$LOG"
  fu=$t/fu.sh; printf '#!/bin/sh\necho x >> "%s/updated"\nexit 1\n' "$t" > "$fu"; chmod +x "$fu"; HPO_RELAY_UPDATE=$fu
  handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
  chk "a failed update is tried once" 0 test "$(wc -l < "$t/updated" | tr -d ' ')" = 1
  chk "and owes handoff-update in the level file, at the topic's tip, with the update's last line" 0 grep -q "^OWED .* handoff-update refs/heads/handoff/topic-a $HS2 (no output)$" "$LOG.level"
  chk "once after two passes (a level, rewritten)" 0 test "$(grep -c handoff-update "$LOG.level")" = 1
  # a BUSY update (75: another update_pr.sh holds the branch's worktree) is no failure: not recorded, retried next pass
  rm -f "$t/updated" "$t/state/cloud-handoff-failed"; : > "$LOG"; rm -f "$t/state/cloud-handoff-failed.tries"
  bu=$t/bu.sh; printf '#!/bin/sh\necho x >> "%s/updated"\nexit 75\n' "$t" > "$bu"; chmod +x "$bu"; HPO_RELAY_UPDATE=$bu
  handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
  chk "a busy update is tried again on the next pass" 0 test "$(wc -l < "$t/updated" | tr -d ' ')" = 2
  chk "and is not recorded failed" 0 test ! -s "$t/state/cloud-handoff-failed"
  chk "nor owed" 1 grep -q "handoff-update" "$LOG.level"
  bodyc() { git -C "$t/b" -c user.name=t -c user.email=t@t commit -q --allow-empty -m body ${1:+-m "Code: $1"}; mkref2; }
  # Carry 12: a refusal that clears with no ref moving is rerun after a backoff, three runs at most; a body-content refusal waits for the body.
  rt=$t/rt.sh; printf '#!/bin/sh\nn=$(cat "%s/rtn" 2>/dev/null || echo 0); echo $((n + 1)) > "%s/rtn"\ncase "$RT_MODE" in\n prepr) echo "  REFUSE   ci predict            r"; echo "  skip     unpinned sites        the diff adds no unpinned mutation site"; exit 1;;\n ok1) [ "$n" = 0 ] && { echo "update_pr: REFUSE: ancestry reds: r"; exit 1; }; exit 0;;\n *) echo "update_pr: REFUSE: $RT_MODE: r"; exit 1;;\nesac\n' "$t" "$t" > "$rt"; chmod +x "$rt"; HPO_RELAY_UPDATE=$rt
  rtreset() { rm -f "$t/rtn" "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why" "$t/state/cloud-handoff-failed.tries"; : > "$LOG"; rm -f "$LOG.level"; }
  rtcalls() { cat "$t/rtn" 2>/dev/null || echo 0; }
  export HPO_RELAY_RETRY_BACKOFF=0
  rtreset; RT_MODE=ok1; export RT_MODE; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
  chk "(a) an ancestry-reds refusal that then clears updates on the retry, with no ref moved" 0 test "$(rtcalls)" = 2 -a ! -s "$t/state/cloud-handoff-failed"
  rtreset; RT_MODE="ancestry reds"; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
  chk "(c) three refusals of a retryable class stop: three runs over five passes" 0 test "$(rtcalls)" = 3
  chk "(c) and the third is recorded and owed with its reason" 0 grep -q "^OWED .* handoff-update refs/heads/handoff/topic-a $HS2 update_pr: REFUSE: ancestry reds: r\$" "$LOG.level"
  # A prepr-shaped run: its late steps print `skip unpinned sites` after the `REFUSE ci predict` line; only REFUSE step lines classify.
  rtreset; RT_MODE=prepr; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
  chk "(d) a ci-predict refusal whose output also holds the unpinned-sites skip line is rerun" 0 test "$(rtcalls)" = 2
  rtreset; RT_MODE="unpinned sites"; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
  chk "(b) an unpinned-sites refusal with the same body is not rerun" 0 test "$(rtcalls)" = 1
  chk "(b) and it is recorded at once, owed with its reason" 0 grep -q "^OWED .* handoff-update refs/heads/handoff/topic-a $HS2 update_pr: REFUSE: unpinned sites: r\$" "$LOG.level"
  bodyc "$HS2"; handoff_arm >/dev/null 2>&1
  chk "(b) a new body reruns it" 0 test "$(rtcalls)" = 2
  rtreset; HPO_RELAY_RETRY_BACKOFF=3600; RT_MODE="ancestry reds"; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
  chk "the backoff holds a retryable refusal back: one run in two passes" 0 test "$(rtcalls)" = 1
  chk "  and owes it meanwhile with its reason" 0 grep -q "handoff-update refs/heads/handoff/topic-a $HS2 update_pr: REFUSE: ancestry reds: r\$" "$LOG.level"
  export HPO_RELAY_RETRY_BACKOFF=0; rtreset; RT_MODE="ancestry reds"; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
  unset HPO_RELAY_RETRY_BACKOFF; rtreset; HPO_RELAY_UPDATE=$hu; unset RT_MODE
  # V147: a failed update records why; a body updates only the code head its Code: trailer names
  rm -f "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why"; : > "$LOG"; rm -f "$t/state/cloud-handoff-failed.tries"
  ru=$t/ru.sh; printf '#!/bin/sh\necho "update_pr: REFUSE: carry X"\necho "update_pr: cleaned up"\nexit 1\n' > "$ru"; chmod +x "$ru"; HPO_RELAY_UPDATE=$ru
  handoff_arm >/dev/null 2>&1
  chk "a failed update's handoff-update line ends in its last REFUSE line" 0 grep -q "^OWED .* handoff-update refs/heads/handoff/topic-a $HS2 update_pr: REFUSE: carry X\$" "$LOG.level"
  handoff_arm >/dev/null 2>&1
  chk "and keeps it on the next pass, which does not retry" 0 grep -q "^OWED .* handoff-update refs/heads/handoff/topic-a $HS2 update_pr: REFUSE: carry X\$" "$LOG.level"
  chk "while cloud-handoff-failed keeps its <topic> <code sha> <body sha> line" 0 test "$(cat "$t/state/cloud-handoff-failed")" = "topic-a $HS2 $(git -C "$t/o.git" rev-parse refs/heads/handoff-body/topic-a)"
  rm -f "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why"; rm -f "$t/state/cloud-handoff-failed.tries"
  printf '#!/bin/sh\necho "update_pr: merging"\necho "update_pr: STALE CHECKOUT"\nexit 1\n' > "$ru"; handoff_arm >/dev/null 2>&1
  chk "an update failing with no REFUSE line records its last line" 0 grep -q "^OWED .* handoff-update refs/heads/handoff/topic-a $HS2 update_pr: STALE CHECKOUT\$" "$LOG.level"
  rm -f "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why" "$t/hupdated"; : > "$LOG"; HPO_RELAY_UPDATE=$hu; rm -f "$t/state/cloud-handoff-failed.tries"
  bodyc "$HS"; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
  chk "a body whose Code: names the previous handoff head runs no update_pr" 0 test ! -e "$t/hupdated"
  chk "and owes one handoff-body-stale line at the handoff tip, naming the body's head" \
    0 test "$(grep -c "^OWED .* handoff-body-stale refs/heads/handoff/topic-a $HS2 body names ${HS:0:12}\$" "$LOG.level")" = 1
  chk "and records no failed update" 0 test ! -e "$t/state/cloud-handoff-failed"
  bodyc "$HS2"; handoff_arm >/dev/null 2>&1
  chk "a body whose Code: names the current handoff head updates (null control)" 0 grep -q "^fix/topic-a-pr $HS2\$" "$t/hupdated"
  chk "and the stale line is gone" 1 grep -q handoff-body-stale "$LOG.level"
  bodyc; rm -f "$t/hupdated"; handoff_arm >/dev/null 2>&1
  chk "a body with no Code: line updates as before (null control)" 0 grep -q "^fix/topic-a-pr $HS2\$" "$t/hupdated"
  rm -f "$t/hupdated"
  # R10-FLOW-BODY-ONLY part (c): a head holding its handoff tip is re-bodied once per body move, with
  # code `-` (update_pr.sh's body-only mode), and never on the pass that seeds the bodied record.
  BF=$t/state/cloud-handoff-bodied; bsha() { git -C "$t/o.git" rev-parse refs/heads/handoff-body/topic-a; }
  printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$HS2" > "$prs"; : > "$LOG"; bodyc "$HS2"; rm -f "$BF"; handoff_arm >/dev/null 2>&1
  chk "a pass with no bodied record seeds it with the contained topic's body and runs nothing" 0 test ! -e "$t/hupdated" -a "$(cat "$BF")" = "topic-a $(bsha)"
  handoff_arm >/dev/null 2>&1
  chk "a body already applied runs nothing on the next pass (null control)" 0 test ! -e "$t/hupdated"
  bodyc "$HS2"; handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
  chk "a new body for a head holding its handoff runs update_pr once, body-only (code -)" 0 test "$(cat "$t/hupdated")" = "fix/topic-a-pr - body-only"
  bodyc "$HS2"; handoff_arm >/dev/null 2>&1
  chk "the next body move runs it once more" 0 test "$(grep -cx "fix/topic-a-pr - body-only" "$t/hupdated")" = 2
  # the review freeze does not hold a body-only move (#3089 review, mutant B): a merge verdict, or a
  # dispatch, at a head holding its handoff tip still lets a new body through, once, with no held line
  rm -f "$t/hupdated"; cp "$t/bus/dispatched" "$t/bus/dispatched.bo"; mkv "verdict: #41 Fix review: merge $HS2"
  bodyc "$HS2"; ho=$(handoff_arm 2>&1); handoff_arm >/dev/null 2>&1
  chk "a new body at a contained head holding a merge verdict runs update_pr once, body-only" 0 test "$(cat "$t/hupdated")" = "fix/topic-a-pr - body-only"
  chk "and is neither printed HELD nor owed handoff-held" 0 test "$(grep -c HELD <<< "$ho")-$(grep -c handoff-held "$LOG.level")" = 0-0
  git -C "$t/o.git" update-ref -d refs/heads/verdict/41; printf '41 %s cloud %s\n' "$HS2" "$n" >> "$t/bus/dispatched"
  rm -f "$t/hupdated"; bodyc "$HS2"; ho=$(handoff_arm 2>&1)
  chk "a new body at a contained head with a reviewer dispatched runs update_pr once, body-only" 0 test "$(cat "$t/hupdated")-$(grep -c HELD <<< "$ho")" = "fix/topic-a-pr - body-only-0"
  # null control: the same head and verdict, with a handoff tip the head does not hold, is still HELD
  mkv "verdict: #41 Fix review: merge $HS2"; git -C "$t/pr" reset -q --hard "$HS2"; hc moved-past-review; mkref handoff/topic-a
  HS3=$(git -C "$t/pr" rev-parse HEAD); rm -f "$t/hupdated"; bodyc "$HS3"; ho=$(handoff_arm 2>&1)
  chk "a handoff tip the verdicted head does not hold is still HELD-VERDICT (null control)" 0 grep -q "^cloud_relay: HELD-VERDICT #41 $HS3 " <<< "$ho"
  chk "and runs no update and owes handoff-held" 0 test "$([ -e "$t/hupdated" ] && echo ran)-$(grep -c "handoff-held refs/heads/handoff/topic-a $HS3 #41 VERDICT\$" "$LOG.level")" = -1
  git -C "$t/o.git" update-ref refs/heads/handoff/topic-a "$HS2"; git -C "$t/o.git" update-ref -d refs/heads/verdict/41
  git -C "$t/pr" reset -q --hard "$PRH"; mv "$t/bus/dispatched.bo" "$t/bus/dispatched"; rm -f "$t/hupdated"
  rm -f "$t/hupdated"; GIT_COMMITTER_DATE="@1000000000 +0000" bodyc; handoff_arm >/dev/null 2>&1  # a body not newer than the head's commit
  chk "a contained body with no Code: line runs nothing, and is recorded applied" 0 test ! -e "$t/hupdated" -a "$(tail -n 1 "$BF")" = "topic-a $(bsha)"
  bodyc "$HS"; ho=$(handoff_arm 2>&1)
  chk "a contained body naming another code head runs nothing and is owed stale" 0 test ! -e "$t/hupdated" -a "$(grep -c "handoff-body-stale refs/heads/handoff/topic-a $HS2 body names ${HS:0:12}\$" "$LOG.level")" = 1
  # a failed body-only run: its reason is the LAST REFUSE line (#3037 review M2), its output is
  # replayed to the relay's stderr (M5), it is keyed on the body sha, and a new body re-triggers it
  r2=$t/r2.sh; printf '#!/bin/sh\necho "$1 $2" >> "%s/hupdated"\necho "update_pr: REFUSE: carry first"\necho "update_pr: REFUSE: carry second"\necho "update_pr: replayed tail"\nexit 1\n' "$t" > "$r2"; chmod +x "$r2"; HPO_RELAY_UPDATE=$r2
  rm -f "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why"; bodyc "$HS2"; ho=$(handoff_arm 2>&1); rm -f "$t/state/cloud-handoff-failed.tries"
  chk "a failed update's handoff-update line ends in the last of its REFUSE lines" 0 grep -q "^OWED .* handoff-update refs/heads/handoff/topic-a $HS2 update_pr: REFUSE: carry second\$" "$LOG.level"
  chk "and the update's whole output reaches the relay's stderr" 0 grep -qx "update_pr: replayed tail" <<< "$ho"
  chk "a failed body-only run is recorded on topic, code and body sha" 0 test "$(cat "$t/state/cloud-handoff-failed")" = "topic-a $HS2 $(bsha)"
  handoff_arm >/dev/null 2>&1
  chk "and not retried on the next pass, which keeps its reason" 0 test "$(grep -c . "$t/hupdated")-$(grep -c "handoff-update refs/heads/handoff/topic-a $HS2 update_pr: REFUSE: carry second\$" "$LOG.level")" = 1-1
  bodyc "$HS2"; handoff_arm >/dev/null 2>&1
  chk "a new body re-triggers it" 0 test "$(grep -c . "$t/hupdated")" = 2
  HPO_RELAY_UPDATE=$hu; rm -f "$t/hupdated" "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why"
  printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"; : > "$LOG"
  # handoff refs with no open PR are OWED on every pass until disposed
  LV=$LOG.level; : > "$LOG"; rm -f "$LV"; hc topic-b; mkref handoff/topic-b; OB=$(git -C "$t/pr" rev-parse HEAD)
  handoff_arm >/dev/null 2>&1
  chk "a handoff ref with no open PR is OWED in the level file" 0 grep -q "^OWED .* handoff-no-pr refs/heads/handoff/topic-b $OB ct=" "$LV"
  chk "a handoff ref with an open PR is not (null control)" 1 grep -q "handoff-no-pr refs/heads/handoff/topic-a " "$LV"
  chk "nor its handoff-body ref (null control)" 1 grep -q "handoff-no-pr refs/heads/handoff-body/topic-a " "$LV"
  handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
  chk "after three passes the no-PR ref is owed once (rewritten, never appended)" 0 test "$(grep -c "handoff-no-pr refs/heads/handoff/topic-b" "$LV")" = 1
  chk "the event log carries no level line" 1 grep -q "handoff-no-pr" "$LOG"
  # one obligation per topic: a no-PR topic's body ref rides its code ref's line (32 of 37 lines were noise, 20 of them body twins)
  git -C "$t/o.git" update-ref refs/heads/handoff-body/topic-b "$OB"; handoff_arm >/dev/null 2>&1
  chk "a no-PR topic with a body ref is one line, its code ref's, naming the body" 0 test "$(grep -c "handoff-no-pr refs/heads/handoff.*/topic-b " "$LV")-$(grep -c "handoff-no-pr refs/heads/handoff/topic-b $OB ct=[0-9]* body=$OB" "$LV")" = 1-1
  git -C "$t/o.git" update-ref -d refs/heads/handoff-body/topic-b
  # RCA 5.1: a merged PR of the topic closes a handoff committed by its merge; a re-handoff after it stays owed
  printf 'fix/topic-b-pr\t2099-01-01T00:00:00Z\n' > "$t/merged.tsv"; handoff_arm >/dev/null 2>&1
  chk "a handoff its topic's merged PR delivered (committed by the merge) is not owed" 1 grep -q "handoff-no-pr refs/heads/handoff/topic-b " "$LV"
  failm=$t/failm.sh; printf '#!/bin/sh\nexit 1\n' > "$failm"; chmod +x "$failm"
  HPO_RELAY_MERGED=$failm handoff_arm >/dev/null 2>&1
  chk "an unlisted merged set leaves the level as it was, never re-owing what a merge closed" 1 grep -q "handoff-no-pr refs/heads/handoff/topic-b " "$LV"
  printf 'fix/topic-b-pr\t2001-01-01T00:00:00Z\n' > "$t/merged.tsv"; handoff_arm >/dev/null 2>&1
  chk "null control: a handoff committed after its topic's merge stays owed" 0 grep -q "handoff-no-pr refs/heads/handoff/topic-b $OB " "$LV"
  : > "$t/merged.tsv"
  git -C "$t/o.git" update-ref refs/heads/handoff/topic-z "$PRH"; handoff_arm >/dev/null 2>&1
  chk "a no-PR handoff ref a live fix/ head carries is not owed (the ledger's ancestry close)" 1 grep -q "handoff/topic-z" "$LV"
  git -C "$t/o.git" update-ref -d refs/heads/handoff/topic-z
  git -C "$t/o.git" fetch -qf "$t/b" "HEAD:refs/heads/handoff-body/topic-c"; OC=$(git -C "$t/o.git" rev-parse refs/heads/handoff-body/topic-c)
  handoff_arm >/dev/null 2>&1
  chk "a handoff-body ref with no open PR is OWED" 0 grep -q "^OWED .* handoff-no-pr refs/heads/handoff-body/topic-c $OC ct=" "$LV"
  dispose refs/heads/handoff/topic-b "$OB" >/dev/null; dispose refs/heads/handoff-body/topic-c "$OC" >/dev/null
  handoff_arm >/dev/null 2>&1
  chk "disposed no-PR refs are not owed" 1 grep -q "handoff-no-pr" "$LV"
  git -C "$t/o.git" update-ref -d refs/heads/handoff-body/topic-c; git -C "$t/o.git" update-ref -d refs/heads/handoff/topic-b
  hc moved; mkref handoff/topic-b; OB2=$(git -C "$t/pr" rev-parse HEAD)
  handoff_arm >/dev/null 2>&1
  chk "a disposed no-PR ref that moved is OWED again" 0 grep -q "^OWED .* handoff-no-pr refs/heads/handoff/topic-b $OB2 ct=" "$LV"
  failprs=$t/failprs.sh; printf '#!/bin/sh\nexit 1\n' > "$failprs"; chmod +x "$failprs"
  HPO_RELAY_PRS=$failprs handoff_arm >/dev/null 2>&1
  chk "a failed PR listing leaves the level as it was (unknown is not 'nothing owed')" 0 grep -q "handoff-no-pr refs/heads/handoff/topic-b $OB2 ct=" "$LV"
  mv "$t/dispositions.tsv" "$t/disp.bak"; mkdir "$t/dispositions.tsv"; handoff_arm >/dev/null 2>&1
  chk "an unreadable ledger leaves the handoff level as it was (rc 2 is not 'nothing owed')" 0 grep -q "handoff-no-pr refs/heads/handoff/topic-b $OB2 ct=" "$LV"
  rmdir "$t/dispositions.tsv"; mv "$t/disp.bak" "$t/dispositions.tsv"
  # HELD-BODY, BODY-ONLY, a stale hold line, and the levels published before a slow update or relay.
  # topic-h: head A (PR 51); handoff tip B ahead of it, then C (the head, holding B). Dates are fixed.
  hx=$t/hx; hbd=$t/hbd; hprs=$t/hprs.sh; hslow=$t/hslow.sh; hid=(-c user.name=t -c user.email=t@t)
  hxc() { GIT_COMMITTER_DATE="@$2 +0000" git -C "$hx" "${hid[@]}" commit -q --allow-empty -m "$1"; git -C "$hx" rev-parse HEAD; }  # never-empty: hid is assigned three words on line 1315
  hbc() { GIT_COMMITTER_DATE="@$1 +0000" git -C "$hbd" "${hid[@]}" commit -q --allow-empty -m "body $1 ${2-}" ${2:+-m "Code: $2"}  # never-empty: hid is assigned three words on line 1315
    git -C "$t/o.git" fetch -qf "$hbd" HEAD:refs/heads/handoff-body/topic-h; }
  hlv() { grep -c "$1" "$LV"; }
  rm -rf "$hx" "$hbd"; throwaway_git_init "$hx" -q; throwaway_git_init "$hbd" -q
  HA=$(hxc a 1700000000); git -C "$t/o.git" fetch -qf "$hx" HEAD:refs/heads/fix/topic-h-pr
  HB=$(hxc b 1700000100); git -C "$t/o.git" fetch -qf "$hx" HEAD:refs/heads/handoff/topic-h
  printf '#!/bin/sh\nprintf "51\\tfix/topic-h-pr\\t%%s\\n" "$HX_HEAD"\n' > "$hprs"; chmod +x "$hprs"; export HX_HEAD=$HA
  printf 'Code head: %s\n' "${HA:0:8}" > "$hbd/BODY.md"; git -C "$hbd" add BODY.md; hbc 1700000150 >/dev/null
  rm -f "$t/hupdated" "$t/state/cloud-handoff-failed" "$t/state/cloud-handoff-failed.why" "$hf"; : > "$LOG"; rm -f "$LV"; HPO_RELAY_UPDATE=$hu; rm -f "$t/state/cloud-handoff-failed.tries"
  ho=$(HPO_RELAY_PRS=$hprs handoff_arm 2>&1)
  chk "a handoff ahead of its PR whose body names the old tip prints HELD-BODY once per pass" 0 test "$(grep -c "^cloud_relay: HELD-BODY #51 ${HB:0:8}\$" <<< "$ho")" = 1
  chk "and runs no update and owes one handoff-held line with why BODY" 0 test "$([ -e "$t/hupdated" ] && echo ran)-$(hlv "handoff-held refs/heads/handoff/topic-h $HB #51 BODY\$")" = -1
  printf 'Code head: %s\n' "${HB:0:8}" > "$hbd/BODY.md"; git -C "$hbd" add BODY.md; hbc 1700000160 >/dev/null
  ho=$(HPO_RELAY_PRS=$hprs handoff_arm 2>&1)
  chk "once the body names the new tip the update runs (null control)" 0 grep -q "^fix/topic-h-pr $HB\$" "$t/hupdated"
  chk "and prints no HELD-BODY and owes no handoff-held (null control)" 0 test "$(grep -c HELD-BODY <<< "$ho")-$(hlv handoff-held)" = 0-0
  # carry 3: the head holds the handoff tip (C is B's child) and a body with no Code: line is newer than it
  HC=$(hxc c 1700000200); git -C "$t/o.git" fetch -qf "$hx" HEAD:refs/heads/fix/topic-h-pr; export HX_HEAD=$HC
  rm -f "$t/hupdated"; hbc 1700000300 >/dev/null
  ho=$(HPO_RELAY_PRS=$hprs handoff_arm 2>&1); HPO_RELAY_PRS=$hprs handoff_arm >/dev/null 2>&1
  chk "a body-only handoff with a body newer than the head prints BODY-ONLY once per pass" 0 test "$(grep -c "^cloud_relay: BODY-ONLY #51 " <<< "$ho")" = 1
  chk "runs nothing and owes exactly one handoff-body-unapplied line after two passes" 0 test "$([ -e "$t/hupdated" ] && echo ran)-$(hlv "handoff-body-unapplied refs/heads/handoff-body/topic-h ")" = -1
  hbc 1700000150 >/dev/null; ho=$(HPO_RELAY_PRS=$hprs handoff_arm 2>&1)
  chk "null control: a body committed before the head's commit prints no BODY-ONLY" 1 grep -q BODY-ONLY <<< "$ho"
  chk "and owes no handoff-body-unapplied" 0 test "$(hlv handoff-body-unapplied)" = 0
  printf '51\n' > "$hf"; hbc 1700000310 >/dev/null; ho=$(HPO_RELAY_PRS=$hprs handoff_arm 2>&1)
  chk "held by the hold file, a newer body-only body prints HELD and BODY-ONLY once each" 0 test "$(grep -c "^cloud_relay: HELD #51 " <<< "$ho")-$(grep -c "^cloud_relay: BODY-ONLY #51 .*held by the hold file" <<< "$ho")" = 1-1
  chk "and owes one handoff-body-unapplied line" 0 test "$(hlv "handoff-body-unapplied .*#51 held by the hold file")" = 1
  hbc 1700000150 >/dev/null; ho=$(HPO_RELAY_PRS=$hprs handoff_arm 2>&1)
  chk "null control: held, with a body older than the head, prints no BODY-ONLY and owes nothing" 0 test "$(grep -c BODY-ONLY <<< "$ho")-$(hlv handoff-body-unapplied)" = 0-0
  # a hold-file line for a PR that is not open is stale; one for an open PR is not
  printf '51\n99\n' > "$hf"; HPO_RELAY_PRS=$hprs handoff_arm >/dev/null 2>&1
  chk "a hold line for a PR not among the open PRs owes handoff-hold-stale" 0 test "$(hlv "handoff-hold-stale [^ ]* #99 ")" = 1
  chk "a hold line for an open PR does not (null control)" 0 test "$(hlv "handoff-hold-stale [^ ]* #51 ")" = 0
  rm -f "$hf"; HPO_RELAY_PRS=$hprs handoff_arm >/dev/null 2>&1
  chk "and the stale line is gone with the hold line" 0 test "$(hlv handoff-hold-stale)" = 0
  # carry 2: the levels are published before the slow serial loop. The update stub blocks until released.
  git -C "$t/o.git" update-ref refs/heads/handoff/topic-h "$HB"; git -C "$t/o.git" update-ref refs/heads/handoff/topic-o "$HB"
  export HX_HEAD=$HA; git -C "$t/o.git" update-ref refs/heads/fix/topic-h-pr "$HA"
  printf 'Code head: %s\n' "${HB:0:8}" > "$hbd/BODY.md"; git -C "$hbd" add BODY.md; hbc 1700000320 >/dev/null
  printf '#!/bin/sh\necho "$1" > "%s/slow.started"\nwhile [ ! -e "%s/slow.go" ]; do sleep 0.1; done\n' "$t" "$t" > "$hslow"; chmod +x "$hslow"
  rm -f "$t/slow.started" "$t/slow.go" "$LV"; HPO_RELAY_UPDATE=$hslow HPO_RELAY_PRS=$hprs handoff_arm >/dev/null 2>&1 & hp=$!
  for _ in $(seq 100); do [ -e "$t/slow.started" ] && break; sleep 0.1; done
  chk "while the update runs, the handoff-no-pr line for an orphan handoff ref is already on the level" 0 grep -q "handoff-no-pr refs/heads/handoff/topic-o $HB " "$LV"
  chk "and the run is in flight (the stub has started)" 0 test -e "$t/slow.started"
  : > "$t/slow.go"; wait "$hp"; rm -f "$t/slow.go" "$t/slow.started"
  git -C "$t/o.git" update-ref -d refs/heads/handoff/topic-o
  # probe_arm: the probe-ref level (a non-rev probe ref) is published before a slow relay push
  cp "$t/bus/dispatched" "$t/bus/dispatched.h"; rm -f "$t/state/cloud-relayed" "$t/state/cloud-relayed.refused" "$t/state/cloud-relayed.tries" "$LV"
  mk 5 $h $h $n; printf '5 %s thread %s\n' "$h" "$n" >> "$t/bus/dispatched"
  git -C "$t/o.git" update-ref refs/heads/probe/odd "$(git -C "$t/o.git" rev-parse refs/heads/probe/rev-5-${n:0:8})"
  printf '#!/bin/sh\necho "$1" > "%s/slow.started"\nwhile [ ! -e "%s/slow.go" ]; do sleep 0.1; done\nexec "%s" "$@"\n' "$t" "$t" "$stub" > "$hslow"
  HPO_RELAY_PUSH=$hslow probe_arm >/dev/null 2>&1 & hp=$!
  for _ in $(seq 100); do [ -e "$t/slow.started" ] && break; sleep 0.1; done
  chk "while the relay push runs, the probe-ref line is already on the level" 0 grep -q "probe-ref refs/heads/probe/odd " "$LV"
  chk "and the push is in flight" 0 test -e "$t/slow.started"
  : > "$t/slow.go"; wait "$hp"; rm -f "$t/slow.go" "$t/slow.started"
  mv "$t/bus/dispatched.h" "$t/bus/dispatched"; rm -f "$t/state/cloud-relayed" "$t/state/cloud-relayed.refused" "$t/state/cloud-relayed.tries"
  git -C "$t/o.git" update-ref -d refs/heads/probe/odd; git -C "$t/o.git" update-ref -d refs/heads/probe/rev-5-${n:0:8}
  for r in fix/topic-h-pr handoff/topic-h handoff-body/topic-h; do git -C "$t/o.git" update-ref -d refs/heads/$r; done
  unset HX_HEAD; HPO_RELAY_UPDATE=$hu; rm -f "$t/hupdated" "$hf"
  git -C "$t/o.git" update-ref -d refs/heads/handoff/topic-b; : > "$LOG"
  chk "pass --loop is the only loop (a bad interval is refused)" 2 pass --loop --interval 0
  HPO_RELAY_UPDATE=$ustub; rm -f "$t/updated" "$t/state/cloud-handoff-failed"; : > "$LOG"; printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"
  chk "pass runs both arms once and returns" 0 pass --log "$LOG"
  chk "the pass fired the handoff arm" 0 test -e "$t/updated"
  # the confirm arm (P-O): the ledger is written before confirm runs, so a failed confirm was never
  # retried ('already relayed'). pass --confirm confirms each review/<pr> tip the relay pushed and
  # bus.sh has not posted; posting is what the confirm stub records, as bus.sh does in posted-signed.
  printf '#!/bin/sh\n' > "$t/none.sh"; chmod +x "$t/none.sh"; HPO_RELAY_PUSH=$stub
  # P332: these PRs are open (their branches carry no handoff, so the handoff arm passes them by)
  printf '#!/bin/sh\nfor p in 61 62 63 64 66; do printf "%%s\\tfix/cf-%%s\\t%s\\n" $p $p; done\n' "$N40" > "$t/open.sh"
  chmod +x "$t/open.sh"; HPO_RELAY_PRS=$t/open.sh
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
  # P332: a relayed review whose PR is not open is skipped once, owed nothing; a failed listing skips nothing.
  CF_FAILS=99; export HPO_RELAY_CONFIRM=$t/cf.sh; mk 67 $h $h $n; printf '67 %s cloud %s\n' "$h" "$n" >> "$t/bus/dispatched"
  cfo=$(pass --confirm --log "$LOG" 2>&1); cfo2=$(pass --confirm --log "$LOG" 2>&1)
  # one call is the relay's own, at the relay; the confirm arm adds none over two passes
  chk "a relayed review on a closed PR is skipped by the confirm arm with one line, confirmed no further (P332)" 0 \
    test "$(grep -c '^cloud_relay: confirm skip #67: not open$' <<< "$cfo
$cfo2") $(calls 67)" = "1 1"
  chk "and owes no confirm-owed" 1 grep -q "review/67 " "$LV"
  mk 68 $h $h $n; printf '68 %s cloud %s\n' "$h" "$n" >> "$t/bus/dispatched"
  HPO_RELAY_PRS=$failprs pass --confirm --log "$LOG" >/dev/null 2>&1
  chk "null control: with the open-PR listing failed, the same shape on #68 stays owed" 0 grep -q "confirm-owed refs/heads/review/68 " "$LV"
  # R10-RELAY-ARM-ORDER: a returned verdict posts before the serial updates start. The stub handoff_arm
  # records how many POSTED lines for #71 the log holds when it BEGINS, and how often it ran.
  printf '#!/bin/sh\nfor p in 71; do printf "%%s\\tfix/ao-%%s\\t%s\\n" $p $p; done\n' "$N40" > "$t/open71.sh"; chmod +x "$t/open71.sh"
  CF_FAILS=0; export HPO_RELAY_CONFIRM=$t/cf.sh; mk 71 $h $h $n; printf '71 %s cloud %s\n' "$h" "$n" >> "$t/bus/dispatched"
  rm -f "$t/ao.seen" "$t/ao.runs"
  aorun() { ( handoff_arm() { echo run >> "$t/ao.runs"; grep -c '^POSTED .* 71 ' "$LOG" >> "$t/ao.seen"; }
    HPO_RELAY_PRS=$t/open71.sh; pass --confirm --log "$LOG" ) >/dev/null 2>&1; }
  aorun
  chk "a verdict returned before the pass is POSTED before handoff_arm starts" 0 test "$(cat "$t/ao.seen")" = 1
  aorun
  chk "null control: with no new probe ref the second pass posts nothing more" 0 test "$(grep -c '^POSTED .* 71 ' "$LOG")" = 1
  chk "and handoff_arm still ran once per pass" 0 test "$(wc -l < "$t/ao.runs" | tr -d ' ')" = 2
  chk "the pass leaves no listing file behind" 0 test -z "$(ls "$t/state" | grep '^cloud-prs-open\.')"
  # the arm order itself: every arm stubbed to log its name; under --confirm and without it
  aoord() { ( for a in probe_arm confirm_arm handoff_arm carry_fold_arm stuck_arm noreturn_arm; do eval "$a() { echo $a >> \"\$t/ao.order\"; }"; done
    HPO_RELAY_PRS=$t/open71.sh; pass "$@" --log "$LOG" ) >/dev/null 2>&1; tr '\n' ' ' < "$t/ao.order"; }
  rm -f "$t/ao.order"; AOO=$(aoord --confirm)
  chk "pass --confirm runs the arms probe, confirm, handoff, carry_fold, stuck, noreturn in that order" 0 test "$AOO" = "probe_arm confirm_arm handoff_arm carry_fold_arm stuck_arm noreturn_arm "
  rm -f "$t/ao.order"; CONFIRM= AOO=$(aoord)
  chk "null control: without --confirm the same order holds with confirm_arm absent" 0 test "$AOO" = "probe_arm handoff_arm carry_fold_arm stuck_arm noreturn_arm "
  # the one listing is reused: a counting lister runs once per pass under --confirm, with the real handoff_arm
  printf '#!/bin/sh\necho x >> "%s/lister.calls"\nprintf "71\\tfix/ao-71\\t%s\\n"\n' "$t" "$N40" > "$t/cnt71.sh"; chmod +x "$t/cnt71.sh"
  rm -f "$t/lister.calls"; ( HPO_RELAY_PRS=$t/cnt71.sh; pass --confirm --log "$LOG" ) >/dev/null 2>&1
  chk "one pass under --confirm lists the open PRs once (handoff_arm and confirm_arm reuse the listing)" 0 test "$(wc -l < "$t/lister.calls" 2>/dev/null | tr -d ' ')" = 1
  rm -f "$t/lister.calls"; ( HPO_RELAY_PRS=$t/cnt71.sh; handoff_arm ) >/dev/null 2>&1
  chk "null control: a lone handoff_arm lists for itself, once" 0 test "$(wc -l < "$t/lister.calls" 2>/dev/null | tr -d ' ')" = 1
  CONFIRM=; CF_FAILS=0; unset HPO_RELAY_CONFIRM; HPO_RELAY_PRS=$t/lister.sh; LOG=$t/pass.log
  # R10-PUSHER-REAP: a relay TERMed mid-update ends the update's whole tree. The
  # update stub records itself and a two-level sleep tree by pid, then blocks.
  printf '#!/bin/bash\necho $$ >> "%s/tpids"\nbash -c '"'"'sleep 30 & echo $! >> "$0"; wait'"'"' "%s/tpids" & echo $! >> "%s/tpids"\nwait\n' "$t" "$t" "$t" > "$t/tree.sh"; chmod +x "$t/tree.sh"
  local rp k tn live p
  stoprelay() { # <relay script> <pids wanted>: one pass, TERMed once the update's tree is up; sets tn and live
    rm -f "$t/state/cloud-handoff-failed"; : > "$t/tpids"; : > "$t/marks"; : > "$LOG"; printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"; rm -f "$t/state/cloud-handoff-failed.tries"
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
  # The production route, no HPO_RELAY_UPDATE: the scratch main's update_pr.sh is the lead stub,
  # so the relay's own launch runs it from its levelled tools tree (tools_level, P283). The relay
  # is a copy, so no route (a mutant's included) reaches the real update_pr.sh.
  cp "$t/lead.sh" "$t/tm/tools/audit/seat/update_pr.sh"; tmc lead; git -C "$t/o.git" fetch -qf "$t/tm" "HEAD:refs/heads/main"
  mkdir -p "$t/seat" && cp "$HERE/cloud_relay.sh" "$HERE/pr_args.sh" "$HERE/topic_grammar.py" "$t/seat/" && cp "$t/lead.sh" "$t/seat/update_pr.sh"
  HPO_RELAY_UPDATE= stoprelay "$t/seat/cloud_relay.sh" 2
  git worktree remove --force "$t/state/relay-tools"; rm -rf "$t/state/relay-tools.lock"
  git -C "$t/o.git" fetch -qf "$t/m" "HEAD:refs/heads/main"; git fetch -q origin main 2>/dev/null
  chk "with no stub, the relay runs update_pr.sh beside it as the lead, asynchronously: a TERM ends it in that order" \
    0 test "$tn $live $(tr '\n' ' ' < "$t/marks")" = "2 0 G "
  # #2549: a signal to the loop's whole process group reaches the update only through the loop's
  # reap: the update runs in a group of its own (pr_own_group). grprelay <stub> <pids wanted>
  # <signal>: one pass in a group of its own, and the signal to that whole group once the update's
  # tree is up; then $t/go lets a surviving update finish, and its tree's survivors are counted.
  printf '#!/bin/bash\necho $$ >> "%s/tpids"\nk=0; while [ ! -e "%s/go" ] && [ $k -lt 400 ]; do sleep 0.05; k=$((k + 1)); done\necho done >> "%s/marks"\n' \
    "$t" "$t" "$t" > "$t/finish.sh"; chmod +x "$t/finish.sh"
  grprelay() {
    rm -f "$t/state/cloud-handoff-failed" "$t/go"; : > "$t/tpids"; : > "$t/marks"; : > "$LOG"; printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$PRH" > "$prs"; rm -f "$t/state/cloud-handoff-failed.tries"
    HPO_RELAY_UPDATE=$1 python3 -I -c 'import os, sys; os.setpgid(0, 0); os.execvp("bash", sys.argv[1:])' bash "$HERE/cloud_relay.sh" pass --log "$LOG" >/dev/null 2>&1 & rp=$!
    k=0; while [ "$(wc -l < "$t/tpids")" -lt "$2" ] && [ $k -lt 300 ]; do sleep 0.05; k=$((k + 1)); done
    tn=$(wc -l < "$t/tpids" | tr -d ' '); kill -"$3" -- "-$rp"; wait "$rp" 2>/dev/null; touch "$t/go"
    k=0; while [ "$3" = KILL ] && ! grep -q done "$t/marks" && [ $k -lt 100 ]; do sleep 0.05; k=$((k + 1)); done
    k=0; while :; do live=0; for p in $(cat "$t/tpids"); do kill -0 "$p" 2>/dev/null && live=$((live + 1)); done
      { [ "$live" = 0 ] || [ $k -ge 30 ]; } && break; sleep 0.1; k=$((k + 1)); done
    for p in $(cat "$t/tpids"); do kill -KILL "$p" 2>/dev/null; done; }
  grprelay "$t/lead.sh" 2 TERM
  chk "a TERM to the relay's whole process group reaches the update only through the relay's reap, which TERMs it alone first" \
    0 test "$tn $live $(tr '\n' ' ' < "$t/marks")" = "2 0 G "
  grprelay "$t/finish.sh" 1 KILL 2>/dev/null
  chk "a KILL to the relay's whole process group leaves the in-flight update to finish under its own lock" \
    0 test "$tn $(tr '\n' ' ' < "$t/marks")" = "1 done "
  # THE STUCK ANDON (P163): branch locks as pr_branch_lock writes them, under $HPO_STATE_DIR/pr.
  # Two held by a fixture holder, aged 901 s and 899 s by their recorded start epoch; one aged
  # 5000 s and released. All three are written now, so the file's mtime reads age 0 on each. A pass
  # whose clock moved more than one second from the write to the read could age 899 to 901, so it
  # is taken again (a condition, not a window). Each is a whole `pass`, its other arms stubbed out.
  stuckrun() { handoff_arm() { :; }; probe_arm() { :; }; CONFIRM= pass 2>&1; }
  stuckpass() {
    local k=0 t0 t1 hp; LOG=$t/stuck.log; mkdir -p "$t/state/pr"; rm -f "$t/state/pr"/upd-*.lock "$t/stuck.held"
    while :; do
      t0=$(date +%s)
      printf '111 222 %s\n' $((t0 - 901)) > "$t/state/pr/upd-fix-old.lock"
      printf '333 444 %s\n' $((t0 - 899)) > "$t/state/pr/upd-fix-young.lock"
      printf '555 666 %s drain\n' $((t0 - 5000)) > "$t/state/pr/upd-fix-gone.lock"
      python3 -I -c 'import fcntl, sys, time
fs = [open(p, "a") for p in sys.argv[2:]]
for f in fs: fcntl.flock(f, fcntl.LOCK_EX)
open(sys.argv[1], "w").close(); time.sleep(60)' "$t/stuck.held" "$t/state/pr/upd-fix-old.lock" "$t/state/pr/upd-fix-young.lock" & hp=$!
      while [ ! -e "$t/stuck.held" ] && kill -0 "$hp" 2>/dev/null; do sleep 0.05; done
      t0=$(date +%s); out=$(stuckrun); t1=$(date +%s)
      kill -KILL "$hp" 2>/dev/null; wait "$hp" 2>/dev/null; rm -f "$t/stuck.held"
      { [ $((t1 - t0)) -le 1 ] || [ $k -ge 5 ]; } && break; k=$((k + 1))
    done
    cp "$LOG.level" "$t/stuck.level"
    # one more pass with every lock released: a released lock is never reported
    stuck_free=$(stuckrun | grep -v "^cloud_relay: state dir ")
  }
  stuckpass
  chk "a held branch lock aged 901 s by its recorded start is STUCK, naming branch, run pid and age" \
    0 grep -qE '^cloud_relay: STUCK fix-old 111 90[12]s$' <<< "$out"
  chk "and it is push-stuck on the level, where the tick reads it" \
    0 grep -qE '^OWED [^ ]+ push-stuck fix-old 111 STUCK fix-old 111 90[12]s$' "$t/stuck.level"
  chk "a held lock aged 899 s is not reported" 1 grep -qF 'fix-young' <<< "$out"
  chk "a released lock aged 5000 s is not reported, whatever its text" 1 grep -qF 'fix-gone' <<< "$out"
  chk "once every lock is released nothing is reported, and the level holds no push-stuck line" \
    0 test "$(printf '%s' "$stuck_free")$(grep -c push-stuck "$LOG.level")" = 0
  # P-E: SEAT ENDED NO RETURN, keyed on the dispatch ref's own age (git only).
  LOG=$t/nr.log; : > "$LOG"; rm -f "$LOG.level"
  rm -rf "$t/nr" "$t/nrw" "$t/nro.git"; throwaway_git_init "$t/nr" -q; throwaway_git_init "$t/nrw" -q
  throwaway_git_init "$t/nro.git" -q --bare; cd "$t/nrw" && git remote add origin "$t/nro.git"
  nrc() { # <ref> <age seconds>: one commit on the scratch origin's <ref>, committed <age> ago
    GIT_COMMITTER_DATE="@$(( $(date +%s) - $2 )) +0000" git -C "$t/nr" -c user.name=t -c user.email=t@t commit -q --allow-empty -m "$1"
    git -C "$t/nro.git" fetch -qf "$t/nr" "HEAD:refs/heads/$1"; }
  nrc dispatch/fixer-nr-a 10800; nrc dispatch/fixer-nr-b 10800; nrc handoff-wip/nr-b 3600
  nrc dispatch/fixer-nr-c 10800; nrc fix/nr-c-pr 1800; nrc dispatch/fixer-nr-young 1800
  nrc dispatch/fixer-nr-old 300000; nrc handoff/nr-e 14400; nrc dispatch/fixer-nr-e 10800
  nro=$(noreturn_arm 2>&1)
  chk "a fixer dispatched 3 h ago with no return ref is SEAT ENDED NO RETURN (P-E)" 0 \
    grep -q "^cloud_relay: SEAT ENDED NO RETURN nr-a (dispatch [0-9a-f]\{12\}, 3h" <<< "$nro"
  chk "and owed seat-no-return on the level" 0 \
    grep -qE "^OWED [^ ]+ seat-no-return refs/heads/dispatch/fixer-nr-a [0-9a-f]{40} SEAT ENDED NO RETURN nr-a 3h$" "$LOG.level"
  chk "a seat whose handoff-wip moved after its dispatch is not reported (null control: it returned)" 1 grep -q " nr-b " <<< "$nro"
  chk "a seat whose pull request's head moved after its dispatch is not reported" 1 grep -q " nr-c " <<< "$nro"
  chk "a dispatch younger than the bound is not reported" 1 grep -q " nr-young " <<< "$nro"
  chk "a dispatch past the window is not reported (its refs may be gone with a merged branch)" 1 grep -q " nr-old " <<< "$nro"
  chk "a return ref older than the dispatch (an earlier round's) does not count as a return" 0 grep -q " nr-e " <<< "$nro"
  nrc dispatch/fixer-r10-agreement-bootstrap 10800; nrc handoff/r10-agreement-bootstrap-p1 3600
  nrc dispatch/fixer-r10-roster-ops 10800; nrc handoff/r10-roster-ops-2 3600
  nrc dispatch/fixer-r10-deeplink 10800; nrc handoff/r10-deeplink-census 3600
  nrc dispatch/fixer-r10-quiet 10800; nrc handoff/r10-quiet-p1 20000
  nro=$(noreturn_arm 2>&1)
  chk "a seat that returned only on handoff/<topic>-p1 after its dispatch is not reported (topic family)" 1 grep -q " r10-agreement-bootstrap " <<< "$nro"
  chk "a bare -<N> topic is no family member: handoff/r10-roster-ops-2 moving still fires r10-roster-ops" 0 grep -q " r10-roster-ops " <<< "$nro"
  chk "a sibling topic is no family member by prefix: handoff/r10-deeplink-census moving still fires r10-deeplink" 0 grep -q " r10-deeplink " <<< "$nro"
  chk "null control: a family that moved nothing since the dispatch still fires" 0 grep -q " r10-quiet " <<< "$nro"
  git -C "$t/nro.git" update-ref -d refs/heads/dispatch/fixer-nr-a; git -C "$t/nro.git" update-ref -d refs/heads/dispatch/fixer-nr-e
  noreturn_arm >/dev/null 2>&1
  chk "deleting the dispatch ref takes its line off the level (the disposal)" 1 grep -q "fixer-nr-a\|fixer-nr-e" "$LOG.level"
  LOG=$t/nr2.log; : > "$LOG"; nrc dispatch/fixer-nr-p 10800
  nro=$(handoff_arm() { :; }; probe_arm() { :; }; CONFIRM= pass 2>&1)
  chk "a pass runs the no-return arm" 0 grep -q "SEAT ENDED NO RETURN nr-p " <<< "$nro"
  # Carry 7: a reviewer dispatched (dispatch/reviewer-*) past HPO_RELAY_NORETURN_REVIEWER_SECS with no probe/rev ref and an unmoved PR head.
  LOG=$t/nr3.log; : > "$LOG"; rm -f "$LOG.level"; RH=$h; RM=2222222222222222222222222222222222222222
  printf '#!/bin/sh\ncase "$1" in 3400) echo %s;; *) echo %s;; esac\n' "$RM" "$RH" > "$t/nrph.sh"; chmod +x "$t/nrph.sh"; export HPO_RELAY_PRHEAD=$t/nrph.sh
  nrn() { printf '%08d%s' "$1" abcdef0123456789abcdef01; }  # the nonce for PR <n>: its first 8 name the return ref
  nrv() { # <pr> <age s> <returned 0|1>: dispatch/reviewer-rev-<pr> aged <age>, its PROMPT.md first line as cloud_dispatch.py renders it
    printf 'CLOUD REVIEWER seat for PR #%s of tvofi/heatpump_optimizer, at head %s. Bus nonce: %s. Never send push notifications.\n' "$1" "$RH" "$(nrn "$1")" > "$t/nr/PROMPT.md"
    git -C "$t/nr" add PROMPT.md; nrc dispatch/reviewer-rev-$1 "$2"; git -C "$t/nr" rm -q --cached PROMPT.md; rm -f "$t/nr/PROMPT.md"
    [ "$3" != 1 ] || nrc probe/rev-$1-$(nrn "$1" | cut -c1-8) 60; }
  for pr in 3339 3350 3297 3325; do nrv $pr 6000 0; done; for pr in 3352 3353 3304 3359; do nrv $pr 6000 1; done
  nrv 3400 6000 0; nrv 3401 4000 0; nrc dispatch/fixer-nr-mid 6000
  nro=$(noreturn_arm 2>&1)
  for pr in 3339 3350 3297 3325; do chk "Carry 7: reviewer #$pr dispatched 100 min ago with no probe/rev ref is SEAT ENDED NO RETURN" 0 grep -q "SEAT ENDED NO RETURN reviewer #$pr rev-$pr (dispatch [0-9a-f]\{12\}, 100min" <<< "$nro"; done
  chk "and owed seat-no-return on the level" 0 grep -qE "^OWED [^ ]+ seat-no-return refs/heads/dispatch/reviewer-rev-3339 [0-9a-f]{40} SEAT ENDED NO RETURN reviewer #3339 rev-3339 100min$" "$LOG.level"
  for pr in 3352 3353 3304 3359; do chk "Carry 7: reviewer #$pr whose probe/rev-$pr-<n8> came back is silent" 1 grep -q "reviewer #$pr " <<< "$nro"; done
  chk "a reviewer whose PR head moved since the dispatch is silent" 1 grep -q "reviewer #3400 " <<< "$nro"
  chk "a reviewer dispatched 4000 s ago (under 5400 s) is silent" 1 grep -q "reviewer #3401 " <<< "$nro"
  chk "the bounds are distinct: a fixer dispatched 6000 s ago (under 7200 s) is silent beside the reviewers" 1 grep -q " nr-mid " <<< "$nro"
  nrv 3402 200000 0; nrv 3403 6000 0; nrc probe/revt-nr-topic-$(nrn 3403 | cut -c1-8) 60
  nro=$(noreturn_arm 2>&1)
  chk "a reviewer dispatched past HPO_RELAY_NORETURN_WINDOW_SECS (172800 s) is silent (null control: #3339 at 6000 s fires)" 1 grep -q "reviewer #3402 " <<< "$nro"
  chk "a reviewer whose verdict came back as a handoff probe/revt-<topic>-<n8> is silent (null control: #3339 has no return ref)" 1 grep -q "reviewer #3403 " <<< "$nro"
  chk "null control for both: the unreturned in-window reviewer #3339 still fires in the same pass" 0 grep -q "reviewer #3339 " <<< "$nro"
  nro=$( git() { if [ "$1" = ls-remote ] && [[ "$*" == *"probe/rev-"* ]]; then return 1; fi; command git "$@"; }; noreturn_arm 2>&1)
  chk "a failed return listing owes no reviewer (unknown is not owed; null control: the same dispatches fire in the pass above)" 1 grep -q "SEAT ENDED NO RETURN reviewer" <<< "$nro"
  unset HPO_RELAY_PRHEAD
  # THE CARRY-FOLD ARM (R10-CARRY-RESIDUE-2 carry 14): a BLOCKED.md naming CARRY-LANDED alone, with its body kept on
  # handoff-wip/<topic>-body, is folded (carry_fold.py) and re-pushed (body_push.sh); any other block prints a line and folds nothing.
  throwaway_git_init "$t/cf.git" -q --bare; throwaway_git_init "$t/cfw" -q; cd "$t/cfw" || exit 1
  git remote add origin "$t/cf.git"; LOG=$t/cf.log; : > "$LOG"; rm -rf "$t/state/cloud-folded"
  cfref() { # cfref <ref> <file> <content>: a one-file orphan commit at <ref> on the origin
    rm -rf "$t/cfx"; throwaway_git_init "$t/cfx" -q; printf '%s\n' "$3" > "$t/cfx/$2"; git -C "$t/cfx" add -A; git -C "$t/cfx" commit -qm x
    git -C "$t/cf.git" fetch -qf "$t/cfx" "HEAD:refs/heads/$1"; }
  # The body_push.sh stand-in runs inside the fold's code worktree: it records that worktree's HEAD, and refuses topic cf-g.
  printf '#!/bin/bash\necho "$@" >> %s/folds\n' "$t" > "$t/foldstub"
  printf '#!/bin/bash\necho "$@" >> %s/bps\ngit rev-parse HEAD >> %s/heads\ngit for-each-ref refs/hpo-relay/fold/ >> %s/privrefs\n[ "$1" != cf-g ]\n' "$t" "$t" "$t" > "$t/bpstub"
  chmod +x "$t/foldstub" "$t/bpstub"; export HPO_RELAY_FOLD=$t/foldstub HPO_RELAY_BODYPUSH=$t/bpstub
  cftip() { git ls-remote origin "refs/heads/$1" | awk 'NF { print $1; exit }'; }
  cfref main code.txt "main's tip"; cfref handoff/cf-a code.txt "code A"
  cfref handoff-wip/cf-a BLOCKED.md "$(printf 'the carries\nbody_push: REFUSED CARRY-LANDED')"; cfref handoff-wip/cf-a-body BODY.md "the body A"
  cfo=$(carry_fold_arm 2>&1)
  chk "null control (carry 14): a sequential fold pushes the body from a worktree at handoff/cf-a's tip" 0 grep -qx "$(cftip handoff/cf-a)" "$t/heads"
  chk "a CARRY-LANDED-only block is folded by carry_fold.py on the kept body" 0 grep -q -- "--topic cf-a " "$t/folds"
  chk "... and body_push.sh re-runs on the same body" 0 grep -q "^cf-a .*cloud-fold-cf-a.md" "$t/bps"
  chk "... and the arm says FOLDED" 0 grep -q "FOLDED cf-a" <<< "$cfo"
  chk "null control: the push ran while the private fold ref refs/hpo-relay/fold/cf-a stood" 0 grep -q "refs/hpo-relay/fold/cf-a\$" "$t/privrefs"
  chk "... which the pass deleted after the push (carry 14)" 0 test -z "$(git for-each-ref refs/hpo-relay/fold/)"
  cfref handoff-wip/cf-a BLOCKED.md "$(printf 'the carries, again\nbody_push: REFUSED CARRY-LANDED')"; carry_fold_arm >/dev/null 2>&1
  chk "a folded (topic, body) whose wip ref moved is not folded again" 0 test "$(grep -c -- '--topic cf-a ' "$t/folds")" = 1
  rm -f "$t/folds" "$t/bps"; carry_fold_arm >/dev/null 2>&1
  chk "a folded body is not folded twice (same topic and body sha)" 1 test -e "$t/folds"
  cfref handoff-wip/cf-b BLOCKED.md "$(printf 'body_push: REFUSED CARRY-LANDED\nbody_push: REFUSED BODY-LINT')"; cfref handoff-wip/cf-b-body BODY.md "the body B"
  rm -f "$t/folds" "$t/bps"; cfo=$(carry_fold_arm 2>&1)
  chk "null control: CARRY-LANDED plus another refusal folds nothing" 1 test -e "$t/folds"
  chk "... runs no body_push.sh" 1 test -e "$t/bps"
  chk "... and prints its tick line naming both kinds" 0 grep -q "OWED carry-fold cf-b .*BODY-LINT CARRY-LANDED" <<< "$cfo"
  chk "... which is on the level" 0 grep -q "carry-fold .*cf-b" "$LOG.level"
  cfref handoff-wip/cf-c BLOCKED.md "the fixer is stuck on a design question"; cfref handoff-wip/cf-c-body BODY.md "the body C"
  rm -f "$t/folds"; cfo=$(carry_fold_arm 2>&1)
  chk "a block with no refusal line folds nothing and prints its line" 0 grep -q "OWED carry-fold cf-c .*no refusal line" <<< "$cfo"
  chk "... and ran no fold" 1 test -e "$t/folds"
  printf '#!/bin/bash\nexit 1\n' > "$t/foldstub"; cfref handoff-wip/cf-d BLOCKED.md "body_push: REFUSED CARRY-LANDED"; cfref handoff-wip/cf-d-body BODY.md "the body D"
  rm -f "$t/bps"; cfo=$(carry_fold_arm 2>&1)
  chk "a fold that fails (rc 1) re-runs no body_push.sh and stays owed" 0 grep -q "OWED carry-fold cf-d .*carry_fold rc=1" <<< "$cfo"
  chk "... with no body_push" 1 test -e "$t/bps"
  # Carry 14 (P556): the fold's worktree is added at a private ref, never FETCH_HEAD, and the body is pushed only from handoff/<topic>'s tip.
  printf '#!/bin/bash\necho "$@" >> %s/folds\n' "$t" > "$t/foldstub"
  cfref handoff/cf-e code.txt "code E"; cfref handoff-wip/cf-e BLOCKED.md "body_push: REFUSED CARRY-LANDED"; cfref handoff-wip/cf-e-body BODY.md "the body E"
  rm -f "$t/heads"; cfo=$(git() { [ "$1 $2" != "worktree add" ] || command git fetch -q origin main; command git "$@"; }; carry_fold_arm 2>&1)
  chk "a fold with a concurrent fetch of main before its worktree add still pushes from handoff/cf-e's tip (carry 14)" 0 grep -qx "$(cftip handoff/cf-e)" "$t/heads"
  chk "... and never from main's tip" 1 grep -qx "$(cftip main)" "$t/heads"
  cfref handoff/cf-f code.txt "code F"; cfref handoff-wip/cf-f BLOCKED.md "body_push: REFUSED CARRY-LANDED"; cfref handoff-wip/cf-f-body BODY.md "the body F"
  : > "$t/bps"; cfo=$(git() { if [ "$1 $2" = "worktree add" ]; then command git fetch -q origin main; set -- "${@:1:$#-1}" FETCH_HEAD; fi; command git "$@"; }; carry_fold_arm 2>&1)
  chk "a fold worktree that lands off the handoff tip is OWED with both heads (carry 14)" 0 \
    grep -q "OWED carry-fold cf-f worktree at $(cftip main | cut -c1-12), handoff at $(cftip handoff/cf-f | cut -c1-12)" <<< "$cfo"
  chk "... runs no body_push.sh" 1 grep -q "^cf-f " "$t/bps"
  chk "... and is on the level" 0 grep -q "carry-fold refs/heads/handoff-wip/cf-f .*worktree at" "$LOG.level"
  # Carry 22 (P580): a judged (wip sha, body sha) is neither fetched nor shown again, and its OWED level line stands.
  : > "$t/fetches"; rm -f "$t/folds"; cfo=$(git() { [ "$1" != fetch ] || echo "$*" >> "$t/fetches"; command git "$@"; }; carry_fold_arm 2>&1)
  chk "an unchanged nothing-folded ref is not fetched again (carry 22)" 1 grep -q "handoff-wip/cf-c\$" "$t/fetches"
  chk "... and its OWED level line still stands" 0 grep -q "carry-fold refs/heads/handoff-wip/cf-c .*no refusal line" "$LOG.level"
  chk "... as does a failed fold's, inside its retry bound" 0 grep -q "carry-fold refs/heads/handoff-wip/cf-d .*carry_fold rc=1" "$LOG.level"
  chk "... and a mislanded worktree's" 0 grep -q "carry-fold refs/heads/handoff-wip/cf-f .*worktree at" "$LOG.level"
  chk "... and no judged topic is folded again" 1 test -e "$t/folds"
  cfref handoff-wip/cf-c BLOCKED.md "the fixer is stuck on a second question"; cfref handoff-wip/cf-b-body BODY.md "the body B, again"
  : > "$t/fetches"; cfo=$(git() { [ "$1" != fetch ] || echo "$*" >> "$t/fetches"; command git "$@"; }; carry_fold_arm 2>&1)
  chk "null control: a moved wip ref is judged again" 0 grep -q "handoff-wip/cf-c\$" "$t/fetches"
  chk "... as is a moved body ref" 0 grep -q "OWED carry-fold cf-b " <<< "$cfo"
  cfref handoff/cf-g code.txt "code G"; cfref handoff-wip/cf-g BLOCKED.md "body_push: REFUSED CARRY-LANDED"; cfref handoff-wip/cf-g-body BODY.md "the body G"
  rm -f "$t/folds"; cfo=$(carry_fold_arm 2>&1)
  chk "a body push that fails after the fold is OWED" 0 grep -q "OWED carry-fold cf-g .*body_push rc=1" <<< "$cfo"
  : > "$t/folds"; carry_fold_arm >/dev/null 2>&1
  chk "... and not retried before its memo entry is an hour old" 1 grep -q -- "--topic cf-g " "$t/folds"
  chk "... while its OWED line stands" 0 grep -q "carry-fold refs/heads/handoff-wip/cf-g .*body_push rc=1" "$LOG.level"
  awk -v e=$(( $(date +%s) - 3601 )) '$1 == "cf-g" { $5 = e } 1' "$t/state/cloud-fold-judged" > "$t/memo" && mv "$t/memo" "$t/state/cloud-fold-judged"
  rm -f "$t/folds"; carry_fold_arm >/dev/null 2>&1
  chk "... and retried once it is" 0 grep -q -- "--topic cf-g " "$t/folds"
  # The production body_push.sh line (no HPO_RELAY_BODYPUSH): HERE points at a stand-in body_push.sh that records its working tree's HEAD.
  mkdir -p "$t/fakehere"; printf '#!/bin/bash\necho "$@" >> %s/rbps\ngit rev-parse HEAD >> %s/rheads\n' "$t" "$t" > "$t/fakehere/body_push.sh"
  cfref handoff/cf-i code.txt "code I"; cfref handoff-wip/cf-i BLOCKED.md "body_push: REFUSED CARRY-LANDED"; cfref handoff-wip/cf-i-body BODY.md "the body I"
  : > "$t/rbps"; : > "$t/rheads"; cfo=$(unset HPO_RELAY_BODYPUSH; HERE=$t/fakehere; carry_fold_arm 2>&1)
  chk "the production body_push.sh line runs the script on the kept body (carry 14)" 0 grep -q "^cf-i .*cloud-fold-cf-i.md" "$t/rbps"
  chk "... inside the worktree at handoff/cf-i's tip, not the relay's own checkout" 0 grep -qx "$(cftip handoff/cf-i)" "$t/rheads"
  chk "... and never at main's tip" 1 grep -qx "$(cftip main)" "$t/rheads"
  # A CARRY-LANDED topic with no handoff/<topic> is OWED on the level, never recorded as folded or announced.
  cfref handoff-wip/cf-h BLOCKED.md "body_push: REFUSED CARRY-LANDED"; cfref handoff-wip/cf-h-body BODY.md "the body H"
  : > "$t/bps"; cfo=$(carry_fold_arm 2>&1)
  chk "a CARRY-LANDED topic with no handoff/<topic> is OWED" 0 grep -q "OWED carry-fold cf-h .*no handoff/cf-h" <<< "$cfo"
  chk "... on the level" 0 grep -q "carry-fold refs/heads/handoff-wip/cf-h .*no handoff/cf-h" "$LOG.level"
  chk "... with no cloud-folded entry" 1 grep -q "^cf-h " "$t/state/cloud-folded"
  chk "... no FOLDED announcement" 1 grep -q "FOLDED cf-h" <<< "$cfo"
  chk "... and no body_push.sh run" 1 grep -q "^cf-h " "$t/bps"
  unset HPO_RELAY_FOLD HPO_RELAY_BODYPUSH; cd "$t/w" || exit 1
  cd / && rm -rf "$t"
  echo "cloud_relay self-test: $((ok+bad)) checks, $bad failed"; [ "$bad" = 0 ]
}

case ${1:-} in
  --self-test) [ -n "${PR_BOUND:-}" ] || pr_bounded cloud_relay bash "$0" --self-test; self_test; exit $?;;  # pr_args.sh's bound
  held) shift; held "$@"; exit $?;;
  --watch) shift; watch "$@"; exit $?;;
  pass) shift; pass "$@"; exit $?;;
  dispose) shift; [ "${1:-}" = --log ] && { LOG=${2:-}; shift 2; }; dispose "$@"; exit $?;;
  --confirm|--log) while [ $# -gt 0 ]; do case $1 in --confirm) CONFIRM=1; shift;; --log) LOG=${2:-}; shift 2;; *) break;; esac; done
    [ $# = 3 ] || { echo "usage: cloud_relay.sh [--confirm] [--log FILE] <pr> <nonce> <head40>" >&2; exit 2; }; relay "$1" "$2" "$3"; exit $?;;
  ''|-*) echo "usage: cloud_relay.sh <pr> <nonce> <head40> | pass [--confirm] [--log FILE] [--loop [--interval N]] | dispose [--log FILE] <ref> <sha40> | --watch [--interval N] [--once] [--confirm] [--log FILE] | --self-test" >&2; exit 2;;
  *) [ $# = 3 ] || { echo "usage: cloud_relay.sh <pr> <nonce> <head40>" >&2; exit 2; }; relay "$1" "$2" "$3"; exit $?;;
esac
