Fix review: merge 0281438a528b71722a32ae98610c7f3b7b344f4a

bus-nonce: b823eb2bb01de2fa425c2393fd19aff4

## Summary

Round 2 (first-round review of the round-1 repair f-3315-r1) of R10-CI-SELFTEST-SCOPE, PR #3315, measured at head 0281438a528b71722a32ae98610c7f3b7b344f4a, merge base 2a3c05644d85b7ee5c2c314fde5aca950e4aba91, from detached worktrees. The round-1 self-test red is gone at this head. Nothing else changed since the round-1 head 38908e4eb: the delta is the one `id:` and `if:` on main's gantt-drift step plus its table entry (ev/round-delta.diff, 2 files, +15 -1). The finding names no committed harness ("Finder's harness: none named" in the packet). The failing test is the existing live-job self-test arm, and I graded with that.

## Evidence

- RESULT selftest-head: `python3 -I tools/ci/selftest_scope.py --self-test` at the head prints `ok the live job parses (111 steps) and its gating is consistent` and `selftest_scope self-test: 90 checks, 0 failed`. `static` prints `103 gated step(s), 0 problem(s)` (ev/selftest-head.txt). These match the body's figures for 0281438a.
- RESULT mutants: M1 to M4 (the body's four) and M5 (my own: table entry deleted) all KILLED. M1 to M4 each give `FAIL the live job parses (111 steps)...`, 1 failed. M5 gives static STALE and `select` falls back to FULL (ev/mutants.txt).
- RESULT re-record: I traced gantt-drift independently with `record --step gantt-drift` under strace in this container. The table came out byte-identical to the committed entry (files `tools/audit/seat/gantt_drift.py`, probes `.`). `git diff d9990a12f 0281438a -- .github tools/ci` is empty, as the body says.
- Merge with current main: `git merge-tree --write-tree origin/main 0281438a` (origin/main bb7dfb9bd) gives rc=0 and tree 0cb72b100. The only stderr line is `LEDGER-MERGE: resolved tests/closures.json` (ev/merge-tree.txt). No conflict.
- Merged tree, self-test: at that merge the same self-test FAILS (`the live job parses (113 steps)`, 1 failed), and `static` reports 2 UNGATED steps. Both steps were added by main after the base, through 36313431c (R10 outside intake): 'Show the plan page stager refusing a page it may not publish' and 'Show the outside intake owing, answering once and refusing its fixtures' (ev/selftest-merged.txt). This is round 1's red, reproduced by main's own advance, not by this head. Under the owner's 2026-11-07 ruling the head is reviewable as-is, so it is a finding below and not a block. The recarry's own CI (instrument-self-tests runs FULL on a governance.yml change) reddens before the train can merge it.
- Structure: `python3 tests/structure.py` at the head prints STRUCTURE RATCHET PASSED. No `*_budgets.json`, VERSION, manifest, RELEASE_NOTES or claim file is in the three-dot diff.
- CI at this head (check-runs API, all runs at the head read job by job, at about 13:35Z): every unit of the code run 42470397322 is success or skipped except `gate`. That includes `governance / instrument-self-tests` and `tests / mutation`.
  - The code run's `gate` (job 128721504132, attempt 3, 11:49Z) is a deferral, not a verdict. Its log reads `FAIL run(s) [42477289290] at this head are still being judged; their gate decides`.
  - Edit run 42477289290 went red only because `pr-contract` died on `gh: API rate limit exceeded for installation` (HTTP 403; infrastructure) and its body file was then missing.
  - Edit run 42477390600 (attempt 3) then concluded success: `gate` 128744284611 success at 13:25Z, `pr-contract / pr-contract` 128744006675 success at 13:24Z. That green pr-contract run started after the last red, so it is the step-11 evidence.
  - The body's Red checks section answers the round-1 instrument-self-tests red (cheaper detector `selftest_scope.py static`, countermeasure recorded for the root-cause seat).
  - `merge_train.py classify 0281438a528b71722a32ae98610c7f3b7b344f4a --pr 3315` exited 1 at 13:35Z and 13:39Z: `RED 0281438a528b71722a32ae98610c7f3b7b344f4a pending: none red: gate` (ev/classify.log). Its `latest_runs` keeps the worst gate suite, so the code run's deferral red stands beside the green suite. gate-sweep has not re-run it: the last sweep was at 12:22Z, and the green suite completed at 13:25Z. Under the brief's GATE DEFERRAL ruling this is judged not a verdict on the code, and the head is judged GREEN on every unit. The train must re-run that deferred gate (the sweep) before merging.
- Approval: tvofi's approving review is still owed for the policy edit to gate-scoping.md, as the body states. That is the owner's gate, not this review's.
- Round: this is the second review round of the PR, so no re-cut is owed (fixer.md applies one from the fourth).

## Findings

- Follow-up: the train's recarry of this head onto current main (bb7dfb9bd) owes an `id:` and `if: ... && steps.scope.outputs.<id> == 'true'` on main's two new self-test steps ('Show the plan page stager refusing a page it may not publish' and 'Show the outside intake owing, answering once and refusing its fixtures'), plus `python3 tools/ci/selftest_scope.py record --step <id>` for each. Without those the merged tree's `selftest_scope.py --self-test` fails 1 of 90 and `static` reports 2 UNGATED, the same class as round 1. Every concurrent PR that adds a self-test step re-opens this until this PR lands.
  Carry: R10-CI-SELFTEST-SCOPE
- Follow-up: the countermeasure the body leaves to the root-cause seat now has a second instance: a step main adds while this PR is open is ungated at every remerge. The cheaper detector is `python3 -I tools/ci/selftest_scope.py static` (about a second), run after any merge of main into this branch (prepr's ci-predict step or the remerge script). Two instances in two rounds sit at the threshold of `defect-root-cause.md`. The root-cause seat owes a decision on building it.
  Carry: R10-CI-SELFTEST-SCOPE
