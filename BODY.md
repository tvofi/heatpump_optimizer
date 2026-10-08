R9-CI-2b, PR 1 of 2 (tvofi's decision on the pre-study, 2026-10-08: build the layout first, it unblocks PRs). GitHub computes `mergeStateStatus` with no merge driver, so every open pull request that re-recorded `tests/closures.json` went DIRTY after a merge to `main`, and a DIRTY pull request runs no CI. On 2026-10-08, 4 of the 6 open PRs (#2054, #2053, #2025, #2010) were DIRTY on that file alone, and the ledger driver resolved all four locally.

The pre-study found two causes, and this removes both in the writer:

- **Timings.** `recorded.<script>.seconds` was rewritten on every recording. Run-to-run noise is 0.3x-3.4x, and 61 of 72 rewrites over 21 PR merges fell inside 2x. A re-timing inside 2x of the committed value now keeps it (`closure.stable_seconds`, `SECONDS_BAND = 2.0`, accepted by tvofi). The ledger driver applies the same band instead of always taking the larger value. The only reader, `mutation_table.recorded_seconds()`, orders a sweep.
- **Order.** Lists and keys were kept in append order, so two branches appending at a list's tail edited the same lines (#2010's `inert_reads`). Every writer now goes through `closure.write_closures` (sorted keys, sorted de-duplicated lists), and the driver writes the same layout from either side's layout. `closure.py check` refuses a table that is out of that layout and names `python3 tests/closure.py canonical`, which re-sorted main's table once with no entry changed.

**Transition, once.** A branch's own driver copy is the one its `git merge` runs, so a branch cut before this change has its pre-change driver refuse main's re-sorted table one time. After that merge the work tree holds main's driver, so `python3 tools/merge/ledger_merge.py --resolve tests/closures.json` finishes it, then commit. I measured this on #2010's head: `--resolve` returned 0, and the result is in the layout. The merge-main bot in PR 2 does the same from main's checkout.

## Head

`17f7e0296db73936a1eb960a6a95218271adb767`, which contains origin/main `9cac1947`. Measured 2026-10-08.

## Mutation proof

The ledger is `/Users/timmalmstrom/hpo-seats/r9-ci-2b/mutation.txt`. Each mutant was applied in a separate worktree, then restored.

- M1, `stable_seconds` band test deleted: `closure.py selftest` FAIL "a timing re-recorded within 2x keeps the committed seconds" and "two branches re-timing one script merge with no driver".
- M2, `write_closures` sorts nothing: FAIL "a merge writes sorted keys and sorted lists", "two branches re-timing one script merge with no driver", and the #1310 phantom null control (now out of layout).
- M3, `check`'s layout refusal deleted: FAIL "check refuses an unsorted table".
- M4, driver band deleted: `ledger_merge.py --self-test` FAIL "closures: two re-timings inside 2x of the base keep the base".
- M5, driver layout sort deleted: FAIL "closures: the driver writes the layout from two tail-appended legacy sides".
- M6, driver either-layout acceptance deleted: the same check FAILs.
- M7, `--resolve` write-back deleted: FAIL "closures: --resolve finishes a merge an older driver left conflicted".
- M0, unmutated: `ALL 52 closure shrink pins PASSED`, `all passed`.

Failing first: before the production code, the new pin "a timing re-recorded within 2x keeps the committed seconds" read FAIL `[seconds=180.0]`, then NameError on `write_closures` (`/Users/timmalmstrom/hpo-seats/r9-ci-2b/failing-first.txt`).

## Null control

The harness `dev/audit/harnesses/r9_ci2b_closures_merge.py` merges with `git merge-file`, so no driver config can take part. Its `as_written` arm is the unmodified writer's output, and it conflicts where the layout arm does not:

- `pairs 120`: real closures.json edits from the last 120 first-parent PR merges, replayed pairwise. Result: `RESULT pairs=462 semantic=0 conflicts_as_written=74 conflicts_layout=17`. The 17 that remain are large deletions (#2015's path moves, #1851) meeting an insertion in the same range. Those are real text collisions; one-file-per-entry would clear them, which the pre-study priced and rejected.
- `heads`: `RESULT head=refs/r9ci2b/pr2053 as_written=conflict layout=clean` and `RESULT head=refs/r9ci2b/pr2010 as_written=conflict layout=clean`. #2054 and #2025 read clean at both ends against the main of the run, because main moved after the pre-study.
- `closure.py selftest` drives a real `git merge-file` on two `--single` merges: before the band it conflicts (M1), after it it is clean.

## Figures

- `python3 dev/audit/harnesses/r9_ci2b_closures_merge.py pairs 120` printed the `RESULT pairs=` line above. The rule is in the harness docstring: a pair is two real edits on one base; a semantic pair, where one non-timing key is set two ways, is counted apart.
- `python3 dev/audit/harnesses/r9_ci2b_closures_merge.py heads <ref>...` printed the per-head lines above. The refs are `refs/pull/<n>/head`, fetched 2026-10-08.
- 61 of 72 seconds rewrites inside 2x: the pre-study's `synth.py` over the same 21 edits, at `/Users/timmalmstrom/hpo-seats/r9-ci-2b/PRESTUDY.md` section 1. It is an instrument outside the tree; the harness's `pairs` arm is its in-tree successor.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: FULL` (tests/closure.py changes the gate). These ran locally green, on venv-ci 3.14, `PYTHONPATH=tests/hastub:custom_components:tests`:
  - `tests/harness_headers.py` (ALL 109 PASSED)
  - `tests/layout.py`
  - `tests/env_drift.py --claims-only origin/main`
  - `tests/closure.py selftest` (ALL 52)
  - `tools/merge/ledger_merge.py --self-test`
  - `tests/entities.py` (ALL 2210)
  - `tests/structure.py` (STRUCTURE RATCHET PASSED, no budget touched)
  
  The rest of the FULL gate is CI's.
- Open PRs against this head as a merged main, measured with `git merge-tree` and no driver: #2054, #2053, #2025, #2024 and #2010 conflict once on `tests/closures.json`, which is the transition above. With this head's driver, all five are clean. #2056 is clean.

## Red checks

none at the time of writing. CI has not run at this head yet.

## Forward-carry

none. The transition note lands in this seat's own PR 2 (the merge-main bot), which merges from main's checkout and so runs this driver.

## Friction

none
