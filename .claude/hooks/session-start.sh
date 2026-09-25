#!/bin/bash
# SessionStart. Prints the facts about THIS clone that a seat otherwise assumes,
# and installs the one thing a clone needs and no clone has by default.
#
# WHY THESE. Each is a trap the handover records paying for:
#
#   is-shallow-repository   A shallow clone answers "no common ancestor" to
#                           `git merge-base origin/main HEAD`, and every scoped
#                           command then measures against nothing. The fiction
#                           is SILENT (HANDOVER trap 11), which is what makes it
#                           worth a line at session start rather than a rule.
#   merge.claimnotes.driver .gitattributes routes the two claim files to
#                           env_drift.merge_claim_file. The routing is tracked;
#                           the DRIVER is per-clone config that no clone has
#                           until someone runs the installer, and a missing
#                           driver silently degrades to the default merge that
#                           claim-files.md exists to prevent.
#   the branch              Not the directory. A checkout sitting on a stale
#                           branch reported current files as missing and cost a
#                           session a filed defect (HANDOVER, corrections).
#   being BEHIND main       The fifth and sixth lines, and the trap the other
#                           three could not see (#1148). They were all present
#                           and all green while an orchestrator checkout sat
#                           **409 commits behind origin/main for 51 hours**
#                           (reflog: cb30d98, 2026-09-16 14:06 -> 2026-09-18
#                           17:08): `git merge-base origin/main HEAD` returns an
#                           ANCESTOR checkout's OWN SHA, which reads as healthy,
#                           so the line built for exactly this trap was blind to
#                           it by construction. Distance is the trap, so
#                           distance is what is now printed.
#
# THE DISTANCE LINES CARRY NO THRESHOLD, deliberately. This hook never blocks,
# so there is nothing to refuse and no number to derive -- a threshold nobody
# derived is the same defect in a new place. `behind main: 409 commits (65
# merges)` beside `shallow clone: false` is read the way `shallow clone: true`
# is: as a measured fact about the checkout a seat is in, before its first turn.
# `origin/main at:` is not decoration and closes the obvious hole: the count is
# measured against the LOCAL remote-tracking ref, which in a checkout nobody has
# fetched in days is itself stale, so `0 commits` against a two-day-old ref is
# still an alarm. origin/main takes a median 38 first-parent commits a day, so a
# tip dated yesterday is that alarm. NO `git fetch` HERE on purpose: 489 ms of
# network in a hook whose contract is that it never blocks.
#
# It never blocks. SessionStart output is context, and a session that cannot
# start is worse than one that starts uninformed.
#
#   .claude/hooks/session-start.sh --self-test
set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0

report() {
  local shallow driver branch base behind merges tip
  shallow=$(git rev-parse --is-shallow-repository 2>/dev/null || echo unknown)
  branch=$(git branch --show-current 2>/dev/null); branch=${branch:-DETACHED}
  driver=$(git config --get merge.claimnotes.driver 2>/dev/null)
  if [ -z "$driver" ]; then
    python3 tests/env_drift.py --install-merge-driver >/dev/null 2>&1
    driver=$(git config --get merge.claimnotes.driver 2>/dev/null)
    [ -n "$driver" ] && driver="$driver (installed just now)"
  fi
  # The ledger driver is the same per-clone config, for the three measured
  # JSON ledgers (tools/merge/ledger_merge.py). Installed silently: its
  # absence only restores the plain text merge.
  if [ -z "$(git config --get merge.ledgermerge.driver 2>/dev/null)" ]; then
    python3 tools/merge/ledger_merge.py --install >/dev/null 2>&1
  fi
  base=$(git merge-base origin/main HEAD 2>/dev/null)
  behind=$(git rev-list --count HEAD..origin/main 2>/dev/null)
  merges=$(git rev-list --count --first-parent HEAD..origin/main 2>/dev/null)
  tip=$(git log -1 --format=%cr origin/main 2>/dev/null)

  printf 'shallow clone:  %s%s\n' "$shallow" \
    "$([ "$shallow" = true ] && printf '  <- every scoped command measures against nothing; git fetch --unshallow origin')"
  printf 'branch:         %s\n' "$branch"
  printf 'merge-base:     %s\n' "${base:-NONE -- git merge-base origin/main HEAD does not resolve}"
  if [ -n "$behind" ]; then
    printf 'behind main:    %s commits (%s merges)\n' "$behind" "${merges:-unknown}"
  else
    printf 'behind main:    UNKNOWN -- git rev-list --count HEAD..origin/main did not resolve; git fetch origin main\n'
  fi
  printf 'origin/main at: %s\n' \
    "${tip:-UNKNOWN -- origin/main does not resolve; git fetch origin main}"
  printf 'claim driver:   %s\n' "${driver:-MISSING -- python3 tests/env_drift.py --install-merge-driver}"
}

if [ "${1:-}" = "--self-test" ]; then
  # The report is a pure read of git state, so what a self-test can assert is
  # that it ASKS -- that every one of the six lines is present and none is
  # empty. A hook that silently prints five lines instead of six is the failure
  # mode here: nobody reads a missing line.
  out=$(report)
  pass=0; fail=0
  st() { if printf '%s' "$out" | grep -qE "$1"; then pass=$((pass+1)); printf '  ok   %s\n' "$2"
         else fail=$((fail+1)); printf '  FAIL %s\n' "$2"; fi; }
  st '^shallow clone:  (true|false|unknown)$|^shallow clone:  true  <-' "the shallow state is printed and is one of the three answers"
  st '^branch:         .+$'                                            "the branch is printed"
  st '^merge-base:     .+$'                                            "the merge base is printed, or says it does not resolve"
  st '^behind main:    [0-9]+ commits \(([0-9]+|unknown) merges\)$|^behind main:    UNKNOWN --' "the distance from origin/main is printed as a count, or says it does not resolve"
  st '^origin/main at: .+$'                                            "origin/main's committer date is printed, or says it does not resolve"
  st '^claim driver:   .+$'                                            "the claim driver is printed, or says how to install it"
  # AND THE LINE MUST CARRY THE DISTANCE, not a quantity that reads as healthy.
  # The precise defect #1148 records is that the hook printed `merge-base`, which
  # on an ancestor checkout IS that checkout's own SHA: a substitute -- or a
  # constant, or the merge base under a new label -- is exactly what the presence
  # assertion above cannot see. So the self-test recomputes the count and
  # requires the printed number to equal it. Skipped, not failed, when the ref
  # does not resolve here either: "I could not measure" and "it printed the
  # wrong number" are different answers.
  want=$(git rev-list --count HEAD..origin/main 2>/dev/null)
  if [ -n "$want" ]; then
    st "^behind main:    ${want} commits " "the printed distance is a fresh git rev-list --count HEAD..origin/main"
  fi
  # And the driver is actually installed by the time this returns, which is the
  # half that is an ACTION rather than a report.
  if [ -n "$(git config --get merge.claimnotes.driver 2>/dev/null)" ]; then
    pass=$((pass+1)); printf '  ok   %s\n' "the claimnotes merge driver is configured after a run"
  else
    fail=$((fail+1)); printf '  FAIL %s\n' "the claimnotes merge driver is configured after a run"
  fi
  printf '\n%s passed, %s failed\n' "$pass" "$fail"
  [ "$fail" -eq 0 ] || exit 2
  exit 0
fi

report
exit 0
