On PR #1987, `closures-autofix` returned `skip-failed-recording` three times, at heads `cf9de4e2`, `705c3be3` and `95ad5034`. Each time it masked a real UNDER-SCOPED, and the repair waited for a human. The UNDER-SCOPED was `tests/debug_collect.py` reading `quiet_windows.py`.

The only failing recording was `tests/stress.py`, with `rc` 1. It ran to its end, and every check it failed was a CPU-ratio verdict, for example 329x against a 268x budget. The recorder runs stress.py beside two other lanes under an audit hook, so the ratio measures the recorder rather than the solver. In the same run, the gate ran stress.py alone on the box, read 247.5x, and passed.

This is a root-cause seat's countermeasure, state (c). The analysis, the class search and the cost test are in `dev/audit/rca/R9-RCA-stress-recording.md`, indexed under I2 in `tools/audit/bugclasses.json`. The changes:

- `tests/closure.py`: `record()` sets `HPO_CLOSURE_RECORDING=1` in the environment of the script it records.
- `tests/stress.py`: the new `timing_check()` replaces `R.check` at the six CPU and wall-clock verdicts (per-scenario CPU, own budget, dramatically cheaper, kernel per call, sweep, wall ceiling). Under the recorder, a miss is printed and not counted. Everywhere else it fails exactly as before. All other checks still count under the recorder.
- `tests/derive_closures.sh`: the `done` line printed the status of the `$(date)` substitution, so every script, including the failing stress.py, read `exit 0`. It now prints the recording's real exit.

## Head

`b956925c59005584c8543db2bee5974e5b385c59` merges origin/main `17f30f9c` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

223f88c24cb52a33ff7a04799d60e5e3ee8e004f is the pull request's head: the orchestrator's merge of e62b8b63 onto 7e197a6f. Its tree, d5f40a12, is identical to the tree of e62b8b63c2d6545ce598d78ff3d1672772ef945f. e62b8b63 merges `origin/main` 38c03d94 into 00834c66, and 00834c66 is a fast-forward of 7e197a6f, the round-1 review head, which added the delivery row. The commits are:

- acf186b7 holds the code.
- c799f329 adds the RCA document and the bugclasses entry.
- 00834c66 pins `timing_check`'s default environment read, the review's finding 1.
- e62b8b63 is the merge.
  - In `tools/audit/bugclasses.json` it keeps every `_rca` entry from main, including R9-RCA-1985 from #2013. On top of those it re-applies only this branch's R9-RCA-stress-recording entry and that entry's citation in `I2.rca`.
  - `tests/derive_closures.sh` auto-merged main's `rec tests/block_duty.py` line.

Merge base `origin/main` 38c03d94. Re-run at e62b8b63, one after another:

- `python3 tests/closure.py selftest`: 36 of 36.
- `pin_mutants.py`: the head passes 2 of 2, and T2, T3 and T4 are killed.
- `python3 tests/structure.py`: passed.
- `python3 tests/closure.py no-copies`: clean.
- `python3 tools/audit/fold_ledger.py check`: 0 violations.
- `python3 tools/audit/fold_ledger.py --self-test`: exit 0.

## Mutation proof

- **`tests/derive_closures.sh` reverted to `origin/main`.** `python3 tests/closure.py selftest` exits 1. The failing pin is `FAIL derive_closures.sh's done line reports a recording's exit 3`: main prints `done tests/x.py (exit 0)` for a stub that exits 3.
- **`env[RECORDING_ENV] = "1"` replaced by `pass` in `record()`.** The selftest exits 1. The failing pin is `FAIL record() runs the script with HPO_CLOSURE_RECORDING=1`, because the probe script saw `''`.
- **End to end, on the defect's own recordings.** `apply_under_scoped_recordings` replayed the `closure-recordings` artifacts of Tests runs 37526452102, 37539776088 and 37564484318 at the #1987 head `95ad5034`.
  - As CI wrote them, all three return `skip-failed-recording`.
  - With stress.py's rc set to what this change yields, all three return `changed`, and `tests/debug_collect.py`'s closure then lists `quiet_windows.py`. That rc is 0, because each run had 0 FAIL lines outside the six timing verdicts.
- **stress.py's pins, round 2.** The harness `pin_mutants.py` (seat evidence `pin_mutants_r2.txt`) imports stress.py and replays the two `timing_check` pins against mutants of the function, without running the sweep:
  - The head passes 2 of 2.
  - `!= "1"` (the review's T2) is killed: with the variable unset, 0 failures are counted.
  - `recording = True` (the review's T3) is killed for the same reason.
  - Removing the recording branch is killed by both pins.

  Before this round, the review's `timing_check_mutants.py` showed T2 and T3 surviving the `(1, 0, 1)` pin, because every call passed `recording=` explicitly.

## Null control

- On main's derive line (the first mutation above), the `exit 0` arm passes and only the `exit 3` arm fails. So the pin reads the real exit and does not fail on every line.
- `timing_check` with `recording=False` still counts a miss: 1 failure out of 1 check. With `recording=True`, a miss counts nothing (0 of 0), and a pass is still counted (0 failures of 1). stress.py pins that tuple, `(1, 0, 1)`. A second pin calls `timing_check` with `recording` omitted, which is how all six real call sites call it. With `HPO_CLOSURE_RECORDING` unset it must count 1 failure, and with it set to `"1"` it must count 0. That pin restores the environment afterwards. Together the two pins mean the exemption cannot make a graded run green.
- No stress.py check outside the six timing verdicts changed.

## Figures

- `python3 tests/closure.py selftest`: ALL 36 closure shrink pins PASSED.
- `python3 tools/audit/fold_ledger.py check`: 0 violations, 98 rca entries at e62b8b63.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir D`: MODE: FULL, because `tests/closure.py` changes the gate itself. The full suite is left to CI.
- Class frequency, from `gh api repos/tvofi/heatpump_optimizer/actions/workflows/tests.yml/runs` over 700 `pull_request` runs since 2026-09-27, with 0 page failures:
  - 28 red `closures-autofix` jobs, 17 of them `skip-failed-recording`.
  - 8 of those 17 still have an artifact. In 5, stress.py's timing verdicts alone caused the status.
  - 9 cannot be attributed, because the log printed `exit 0` for every script.
- Standing cost, `python3 tests/closure.py selftest`, depends on machine load:
  - With load around 450, timed 3 times at each tree: median 5.44 s at main and 9.14 s at the head, so +3.7 s.
  - The round-1 reviewer, with load around 216: 1.96 s at the base and 2.55 s at the head, so +0.6 s.

## Red checks

- `delivery-status` grades `main`, and this diff touches nothing it reads. It is red because main's `record-autofix` staged the old delivery path. #2011 fixes that.
- `nightly-status` grades `main`, and this diff touches nothing it reads either.
- `closures` (job 112810272267) and `closures-autofix` (job 112820973686, `skip-manual-repair-owed`) are red because of a failure inherited from main. Main's own `closures` run at 38c03d94 (job 112789710707) fails on the same line: `tests/harness_headers.py` reads `eg_b7_seam_hubs.py`, which #2017 added without a recording. A separate repair PR is in progress. Neither file is in this diff.

## Approval

**Code-owner approval is owed.** `.github/CODEOWNERS` assigns three files in this diff to @tvofi:

- `/tests/closure.py` (line 138)
- `/tests/derive_closures.sh` (line 140)
- `/tests/stress.py` (line 150)

So the PR needs @tvofi's approving review as code owner. The orchestrator holds the owner's mandate 5951564627.

No policy file is changed. `dev/governance/rules/ci-autofix.md` is unchanged, and the round-1 reviewer agrees this is not a policy change. That rule's `skip-failed-recording` remedy still holds for a real truncation. This branch stops stress.py's timing misses from producing that status, and makes the `closures` log name the failing script.

## Forward-carry

none

## Friction

- ci-autofix.md: stale: it says "On `skip-failed-recording` the script named in the `closures` log stopped", but on main that log named no script. Every `done` line printed `exit 0`, because `$?` sat inside the same echo as `$(date)`. This branch fixes the log, and the rule's sentence is now true.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

