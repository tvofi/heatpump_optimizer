Fix review: blocked 9f4a1a41078ab70510afe7e2413ac603e0ffdd56 resolution-ungated-step: the main merge brought in selftest_scope's gating rule and the PR's new bottleneck self-test step is ungated, so selftest_scope --self-test fails at this head and passes on main

bus-nonce: 7ae982bbf4992b91836aa84c76543496

## Block

Round: second review of #3350 (resolution delta after the merge verdict at ab236e012dedd0c24039a4b530dcc83ebd20d3b3); `review_carry.py ab236e012 9f4a1a410` prints FRESH-REVIEW, because the branch's own diff differs.

The diffs `fdc8d21..ab236e0` and `f365ce7..9f4a1a4` add the same lines (1244 insertions, 34 deletions, 21 files each). They differ only in context lines, in two files (`ev/diff-of-diffs.txt`):
- `tests/closures.json`: the neighbouring harness names shifted. No line is lost or duplicated, and the lists at the head parse with no duplicates and stay sorted.
- `.github/workflows/governance.yml`: the step above the PR's new step is now `id: outside-intake` with `if: steps.scope.outputs.outside-intake == 'true'`. Main's a751546c5 ("gate main's plan-public, outside-intake and hooks-setup self-test steps") and the R10-CI-SELFTEST-SCOPE landing added it. The resolution kept the PR's step `Show the bottleneck alert tripping each rule once and silent on its null control` with no `id:` and no `if:`.

Main's `tools/ci/selftest_scope.py` makes that a defect. `wiring_gaps` at the head prints exactly one gap: `UNGATED step 'Show the bottleneck alert tripping each rule once and silent on its null control': its if: does not read steps.scope.outputs.<its own id>`. So `python3 -I tools/ci/selftest_scope.py --self-test` prints `FAIL the live job parses (115 steps) and its gating is consistent`, with 90 checks and 1 failed, rc 1. Null control: the same command at main f365ce757 prints `ok ... (114 steps)`, with 90 checks and 0 failed, rc 0.

Repair, shown in a scratch worktree and not pushed: give the step `id: bottleneck-alert` and `if: steps.scope.outputs.bottleneck-alert == 'true'`. The self-test then passes (90/0). `select` then reports `the table is stale: ... missing ['bottleneck-alert']`, so a `tools/ci/selftest_closures.json` entry also has to be recorded (`selftest_scope.py record --step bottleneck-alert`, on Linux with strace). Without it, every pull request's self-test selection drops to FULL. The fixer could instead add the step to `UNGATED`, but that would need its own justification.

## Findings

- Resolution defect: the PR's new governance.yml self-test step is ungated and has no row in `tools/ci/selftest_closures.json`. This breaks main's self-test scoping rule (R10-CI-SELFTEST-SCOPE). The fixer re-resolves it on this branch: the `id:` and `if:` above, plus a recorded table entry. Carry: R10-OUTSIDE-INTAKE

## Evidence

- Head reviewed: 9f4a1a41078ab70510afe7e2413ac603e0ffdd56 (`ev/HEAD.txt`). Merge base and base: f365ce757ded1e64a9ec40102495b7c051055f38 = origin/main, and the head contains main.
- `git merge-tree --write-tree origin/main 9f4a1a41078ab70510afe7e2413ac603e0ffdd56`: rc 0, tree d6269bff1fbad15055dc1b1ae35cb009194161ef. No conflict.
- Diffs and their comparison: `ev/old-branch-diff.patch`, `ev/new-branch-diff.patch`, `ev/diff-of-diffs.txt`.
- selftest_scope self-test at the head and at main: `ev/selftest-scope-selftest-head.txt` (rc 1) and `ev/selftest-scope-selftest-main.txt` (rc 0). Gaps at the head: `ev/wiring-gaps-head.txt`. Control after gating the step: `ev/selftest-scope-gated-control.txt` (0 failed).
- `selftest_scope.py select --base f365ce7 --head HEAD`: `MODE: FULL` (governance.yml is a gate file), in `ev/selftest-scope.txt`.
- Lines that are identical between the two diffs stand on the merge verdict at ab236e012dedd0c24039a4b530dcc83ebd20d3b3. I did not re-run its mutation proof or figures.
- CI at the head: the required lane `governance / instrument-self-tests` (job 129152227797) concluded failure on this same check: `FAIL the live job parses (115 steps) and its gating is consistent`, 90 checks and 1 failed (`ev/ci-instrument-self-tests-tail.txt`). `gate` job 129152782003 is a deferral to run 42614818040. The classify waiter log is `ev/classify-log.txt`.
- PR body `## Head` (step 7): it names 9f4a1a41078ab70510afe7e2413ac603e0ffdd56, which is the head I measured. Its sentence "an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged" is true of the text but not of the behaviour. The merge was textually clean, yet main's new rule now reads the PR's unchanged step as a defect.
- carry_audit closing self-audit: `python3 -I tools/audit/carry_audit.py check --body <stub> --comments <this verdict>` prints `CARRY-AUDIT: 0 finding item(s)`, rc 0. In a blocked verdict, the block and its items are owed rather than carried.
- `merge_train.py classify 9f4a1a41078ab70510afe7e2413ac603e0ffdd56 --pr 3350` exited 0 at 2026-11-09T13:00:31Z: `GREEN 9f4a1a41078ab70510afe7e2413ac603e0ffdd56 pending: none red: none` (`ev/classify-log.txt`). The head is GREEN only because `governance / instrument-self-tests` is not a required context: `merge_train.py owed-reds` does not list it (`ev/owed-reds.txt`).
- This block is a defect block, not a root-cause-trigger block. Every push to main runs every step, so merging this head would turn main's `instrument-self-tests` red on the selftest_scope self-test. The check fails at this head and passes at main f365ce757.
