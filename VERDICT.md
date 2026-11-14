Fix review: blocked b131ad0ad8c8e8e9710681160a8b539ab88137ff closures-regressed: the repair head drops the reviewed head's closures-autofix inert_reads line, so tests / closures re-reds, and the body misstates why the tick loop self-test step went red

bus-nonce: 9bde56e9028490ac66f0014a12363953

## Block

Round: a later round over reviewed head `5d647dd055d7e08e1073bedbe570257c606b98b3`. Scope is the delta and the step the previous review refused. `review_carry.py 5d647dd0 b131ad0a` prints `FRESH-REVIEW` (force-push: `b131ad0a` does not descend from `5d647dd0`). Its first parent is `6e8db8d8`, the authored code head *before* the `b7a838c1` merge and the `closures-autofix` bot commit.

1. **`tests / closures` (required, listed by `owed-reds`) will go red again at this head.** The reviewed head carried the bot's repair: `tests/closures.json` listing `dev/audit/rounds/round10/protection-census/main_reds.py` under `tests/harness_headers.py`'s `inert_reads` (count 1 at `5d647dd0`). Built from `6e8db8d8`, the head drops that line (count 0 at `b131ad0a`). Re-derived at the head with `env -u BASH_ENV ./tests/derive_closures.sh --single tests/harness_headers.py` (rc 0, `tests/harness_headers.py 408 files`): it writes back exactly that one line (`ev/derive_harness_headers_at_head.diff`). This is the same `INERT READS UNDER-APPROXIMATED` red the body's `## Red checks` reports at `b7a838c1`, now reintroduced. The body still says it was "Repaired by the closures-autofix bot commit `5d647dd0`", and that commit is not in this head. The body also says "The merge is the only change; no authored file moves" and "the diff is … a measured re-record of `tests/entities.py` in `tests/closures.json`". At this head the three-dot diff against `8c10361e` is `CENSUS.md` and `main_reds.py` only (`ev/figures_at_head.txt`). `entities.py` `rc 0` already comes from main, and the `inert_reads` line has moved out. Repair: build the head on `5d647dd0` (merge `origin/main` into it), or re-add the line. Then make the body's Head and diff sentences match.

2. **The step passes at this head, but not for the reason the body gives.** The body says the failing check "is a defect in the older `tools/audit/seat/tick_loop.sh` that main already repaired (`e899dde4ab`)". That is false: `e899dde4ab` is an ancestor of both `6e8db8d8` and `5d647dd0`, and `tick_loop.sh` is byte-identical at `5d647dd0` and `b131ad0a` (`ev/git_measurements.txt`). The measured cause is that the self-test's first three rows (`tick_loop.sh:206-215`) run `fresh_check` against the **real checkout**. `HPO_TICK_CODE_DIR=$t/nogit` is only set at line 218. With CI's branch checkout, a head more than `HPO_TICK_STALE_BOUND` (25) commits behind live `origin/main` on `CODE_PATHS` prints an extra `TICK-STALE` line. Row 3 counts exactly 2 `TICK-` lines, so it fails. `5d647dd0` was 26 behind (self 0). `6e8db8d8` was 50 behind (self 1). `b131ad0a` is 0 behind. Reproduced in `ev/tick_branch_checkout.txt`:
   - `5d647dd0`, branch checked out: `FAIL a seat bin dir with no gh shim…`, `30 checks, 1 failed`. This is the same single FAIL as CI job 131266913985 (`ev/ci_job_131266913985_tick_step.log`).
   - `b131ad0a`, branch checked out: `30 checks, 0 failed`.
   - Null control, `5d647dd0` with `HPO_TICK_STALE_BOUND=30` (26 ≤ bound): `30 checks, 0 failed`. The bound alone turns it green.

   So merging main is a valid repair, because the head is now level with main. The step is not INTRODUCED by this diff. It will go red again whenever main moves more than 25 commits on `tools/audit/seat`, `tools/pr` or `carry_audit.py` (or touches `tick_loop.sh`/`cloud_relay.sh`) before CI runs. The body's causal paragraph must say this, not cite `e899dde4ab`.

## Findings

- The tick loop self-test's first three rows are not isolated from the real checkout. They run `fresh_check`, including `git fetch origin main`, and in a detached clean checkout `git checkout --detach origin/main` plus exec, before line 218 sets `HPO_TICK_CODE_DIR`. Their verdict therefore depends on how far live `origin/main` has moved past the head. Run detached and locally, the self-test also moved the reviewer's worktrees (`wt-p`, `wt-old`) to `origin/main` and exec'd main's script, so a "pass" there measured main's code, not the head's. Control: `HPO_TICK_STALE_BOUND=30` at `5d647dd0` turns the FAIL green (`ev/tick_branch_checkout.txt`). Carry: R10-HOTFIX-TICK-SELFTEST-CHECKOUT

## Evidence

- Head measured: `b131ad0ad8c8e8e9710681160a8b539ab88137ff` (`ev/HEAD.txt`). Parents are `6e8db8d8c12e480181e730bd30e01da3c97b733f` and `8c10361eb1fea539dc5acb8f7442eac2810faa47` (= `origin/main` when measured).
- `git merge-tree --write-tree origin/main b131ad0a`: rc 0, tree `f498ee8b`. It merges cleanly.
- No review packet and no CI at this head: the PR head is still `5d647dd0` and the handoff head has not been pushed to the PR. Live CI at `5d647dd0`: run 43242542423 (`CI code`, 8104) failed only `governance / instrument-self-tests` at step "Show the tick loop refusing its own fixtures" (job 131266913985).
- `merge_train.py owed-reds` (`ev/owed_reds.txt`): `tests / closures` is in the set. `instrument-self-tests` is not.
- Tick loop self-test at the head: `30 checks, 0 failed`, with a branch checked out (CI's shape, `ev/tick_branch_checkout.txt`) and detached (`ev/tick_detached_runs.txt`). The detached runs at `8c10361e` and at `6e8db8d8` also print 0 failed. The `6e8db8d8` run restarted onto `origin/main` (see Findings), so it does not measure the old code.
- Body figures re-derived at the head (`ev/figures_at_head.txt`): 17 required contexts, 28 `main_reds.py` rows, null control 0, `ENTRIES 18 PRS 14`, 4 `harness_headers` rows. All match.
- The "33 recorded scripts, 29 reaching product files" figure was not re-derived: its enumerator is a one-liner inside CENSUS.md, which is outside this delta round's scope.
- Mutation: `mutant_run.py --diff 8c10361e...HEAD --cmd true --list` printed no mutant. The diff adds no production or tool code; Python under `dev/` only.
- `VERSION`, the manifest and the `RELEASE_NOTES.md` heading are untouched against the merge base: empty `git diff --stat 8c10361e b131ad0a` (`ev/git_measurements.txt`).
- No `custom_components/` change in the delta beyond main's own commits, so scope is not widened.
