Fix review: merge c48d7a36c5bfb5bce5f417497eb43be15ea11d38

bus-nonce: 4876ca099ecd2b7c7ddac973791edac2
pending-ci: gate

## Summary

This is round 5 of #3825, a later round over the reviewed head `db727d36e0`. The delta to `c48d7a36c5` is one commit: the orchestrator's automatic merge of main `eaaaf24`. The PR's own diff is unchanged. Comparing it before and after (`db727d36e0`'s three-dot diff against `c48d7a36c5^2..c48d7a36c5`) differs only in two hunk offsets in `tests/closures.json` (`ev/own_diff_interdiff.txt`). `review_carry.py` prints `CARRY` (`ev/review_carry.txt`). The previous verdict blocked only on stale `gate` suites at the old head. The fix is new CI at this head, which classify reads below.

No code, test or harness finding blocks. The head merges cleanly with origin/main, and mutant A1 still fails its check at this head.

## Findings

- Follow-up: the `yields` floor in `tests/cycle_budgets.json` is recorded on one platform and read on another, so how sensitive it is depends on the kernel. Round 1 showed that a planted halving of `_gil_yield` failed only one of five scenarios (`probe/rev-3825-d64c72ea`, `ev/mut_yield_half.txt`). The production code is unchanged at this head. Carry: dismissed: design-approved operator (§5) that still detects a halving; the C part's CI-platform re-record (design §7) is where re-recording the lane's budgets on CI's platform runs

## Notes

- Note: round: this is the fifth review round. The earlier four turned on CI state alone, and none turned on code, so this seat reads no re-cut as owed on the fix. If the orchestrator reads `fix-review.md`'s "from the fourth, a re-cut is owed" otherwise, the call is its own.
- Note: figure: the body's A figures are still 2 short. The head reads `flow_error_triples=56` (body: 54), and mutant A1 reads 56 unrecovered (body: 54). The extra 2 are main's silent-mode `device_prefill` triples, as rounds 3 and 4 recorded.

## Evidence

- Head `c48d7a36c5bfb5bce5f417497eb43be15ea11d38` (`ev/HEAD.txt`). The PR body's `## Head` names this head.
- Scope: delta (step 12). The main merge brings 19 `custom_components/` files from main (`ev/main_merge_prod.txt`), and none from this branch. The branch's reviewed code is tests and instruments that drive `config_flow.py` and `coordinator.py`. A behaviour change that breaks them fails `config_flow_steps.py` or `cycle_lane.py` in the required `gate`, which runs at this head. So the merged production code puts nothing at a risk CI would not detect, and the scope does not widen.
- Role contracts: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty (`ev/roles_diff.txt`).
- Merge with main: `git merge-tree --write-tree origin/main c48d7a36c5` exits 0, with `LEDGER-MERGE: resolved tests/closures.json`. origin/main was `1207ee13b0` (`ev/merge-tree.txt`).
- Step 1, re-run at this head under venv-ci with `PYTHONPATH=tests/hastub`:
  - Clean: `RESULT unrecovered_flow_error_triples=0`, `ALL 684 checks PASSED`, rc 0 (`ev/cfs_head.txt`).
  - A1: both tracker `done = True` sites set to False (`ev/mut_A1.patch`). Result: `RESULT unrecovered_flow_error_triples=56`, rc 1 (`ev/mut_A1.txt`). Restored afterwards.
  - Not re-run, because the PR's own diff is unchanged: A2, beatd `--self-test 2`, M9/M10, the gate-schema mutant, the cycle_lane arms and the finder's harness at both ends. Their evidence is at `bef3842c44` and `ce756cbe00` `ev/`.
- Step 14: the diff is unchanged, so round 3's readings stand: `script_runs_per_push: 54 -> 56` and `dS +0.0000 NULL`.
- Step 11: the owed-reds set is in `ev/owed_reds.txt`. The body's `## Raise justification` and `## Red checks` answer the budget-raise red, and its `governance / policy-docs` entry answers the version-skew red that this main merge repaired.
- CI: `merge_train.py classify c48d7a36c5 --pr 3825` was polled from 18:53 to 19:22:54 UTC, 29 readings, every one `WAIT c48d7a36c5bfb5bce5f417497eb43be15ea11d38 pending: gate red: none` (`ev/classify.log`). The poll stopped at its 30-minute limit. That is why the `pending-ci: gate` line is set.
