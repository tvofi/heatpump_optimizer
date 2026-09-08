#!/bin/bash
# SessionStart. Prints the three facts about THIS clone that a seat otherwise
# assumes, and installs the one thing a clone needs and no clone has by default.
#
# WHY THESE THREE. Each is a trap the handover records paying for:
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
#
# It never blocks. SessionStart output is context, and a session that cannot
# start is worse than one that starts uninformed.
#
#   .claude/hooks/session-start.sh --self-test
set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0

report() {
  local shallow driver branch base
  shallow=$(git rev-parse --is-shallow-repository 2>/dev/null || echo unknown)
  branch=$(git branch --show-current 2>/dev/null); branch=${branch:-DETACHED}
  driver=$(git config --get merge.claimnotes.driver 2>/dev/null)
  if [ -z "$driver" ]; then
    python3 tests/env_drift.py --install-merge-driver >/dev/null 2>&1
    driver=$(git config --get merge.claimnotes.driver 2>/dev/null)
    [ -n "$driver" ] && driver="$driver (installed just now)"
  fi
  base=$(git merge-base origin/main HEAD 2>/dev/null)

  printf 'shallow clone:  %s%s\n' "$shallow" \
    "$([ "$shallow" = true ] && printf '  <- every scoped command measures against nothing; git fetch --unshallow origin')"
  printf 'branch:         %s\n' "$branch"
  printf 'merge-base:     %s\n' "${base:-NONE -- git merge-base origin/main HEAD does not resolve}"
  printf 'claim driver:   %s\n' "${driver:-MISSING -- python3 tests/env_drift.py --install-merge-driver}"
}

if [ "${1:-}" = "--self-test" ]; then
  # The report is a pure read of git state, so what a self-test can assert is
  # that it ASKS -- that every one of the four lines is present and none is
  # empty. A hook that silently prints three lines instead of four is the
  # failure mode here: nobody reads a missing line.
  out=$(report)
  pass=0; fail=0
  st() { if printf '%s' "$out" | grep -qE "$1"; then pass=$((pass+1)); printf '  ok   %s\n' "$2"
         else fail=$((fail+1)); printf '  FAIL %s\n' "$2"; fi; }
  st '^shallow clone:  (true|false|unknown)$|^shallow clone:  true  <-' "the shallow state is printed and is one of the three answers"
  st '^branch:         .+$'                                            "the branch is printed"
  st '^merge-base:     .+$'                                            "the merge base is printed, or says it does not resolve"
  st '^claim driver:   .+$'                                            "the claim driver is printed, or says how to install it"
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
