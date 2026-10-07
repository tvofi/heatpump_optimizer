On PR #1987, `closures-autofix` returned `skip-failed-recording` three times, at heads `cf9de4e2`, `705c3be3` and `95ad5034`. Each time it masked a real UNDER-SCOPED, and the repair waited for a human. The UNDER-SCOPED was `tests/debug_collect.py` reading `quiet_windows.py`.

The only failing recording was `tests/stress.py`, with `rc` 1. It ran to its end, and every check it failed was a CPU-ratio verdict, for example 329x against a 268x budget. The recorder runs stress.py beside two other lanes under an audit hook, so the ratio measures the recorder rather than the solver. In the same run, the gate ran stress.py alone on the box, read 247.5x, and passed.

This is a root-cause seat's countermeasure, state (c). The analysis, the class search and the cost test are in `dev/audit/rca/R9-RCA-stress-recording.md`, indexed under I2 in `tools/audit/bugclasses.json`. The changes:

- `tests/closure.py`: `record()` sets `HPO_CLOSURE_RECORDING=1` in the environment of the script it records.
- `tests/stress.py`: the new `timing_check()` replaces `R.check` at the six CPU and wall-clock verdicts (per-scenario CPU, own budget, dramatically cheaper, kernel per call, sweep, wall ceiling). Under the recorder, a miss is printed and not counted. Everywhere else it fails exactly as before. All other checks still count under the recorder.
- `tests/derive_closures.sh`: the `done` line printed the status of the `$(date)` substitution, so every script, including the failing stress.py, read `exit 0`. It now prints the recording's real exit.

## Head

acf186b7556307964acbea3e61d555681a12aca5 holds the code. c799f329f4647437fecd092709a8988e45325dcd adds the RCA document and the bugclasses entry. Every figure below is measured at c799f329, on base `origin/main` 59b5ac6e.

## Mutation proof

- **`tests/derive_closures.sh` reverted to `origin/main`.** `python3 tests/closure.py selftest` exits 1. The failing pin is `FAIL derive_closures.sh's done line reports a recording's exit 3`: main prints `done tests/x.py (exit 0)` for a stub that exits 3.
- **`env[RECORDING_ENV] = "1"` replaced by `pass` in `record()`.** The selftest exits 1. The failing pin is `FAIL record() runs the script with HPO_CLOSURE_RECORDING=1`, because the probe script saw `''`.
- **End to end, on the defect's own recordings.** `apply_under_scoped_recordings` replayed the `closure-recordings` artifacts of Tests runs 37526452102, 37539776088 and 37564484318 at the #1987 head `95ad5034`.
  - As CI wrote them, all three return `skip-failed-recording`.
  - With stress.py's rc set to what this change yields, all three return `changed`, and `tests/debug_collect.py`'s closure then lists `quiet_windows.py`. That rc is 0, because each run had 0 FAIL lines outside the six timing verdicts.
- The stress.py arm of the pin is left to CI's stress run. `fixer.md` step 5 says not to run stress.py locally per mutant.

## Null control

- On main's derive line (the first mutation above), the `exit 0` arm passes and only the `exit 3` arm fails. So the pin reads the real exit and does not fail on every line.
- `timing_check` with `recording=False` still counts a miss: 1 failure out of 1 check. With `recording=True`, a miss counts nothing (0 of 0), and a pass is still counted (0 failures of 1). stress.py's own new check pins that tuple, `(1, 0, 1)`, so the exemption cannot make a graded run green.
- No stress.py check outside the six timing verdicts changed.

## Figures

- `python3 tests/closure.py selftest`: ALL 36 closure shrink pins PASSED.
- `python3 tools/audit/fold_ledger.py check`: 0 violations, 97 rca entries.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir D`: MODE: FULL, because `tests/closure.py` changes the gate itself. The full suite is left to CI.
- Class frequency, from `gh api repos/tvofi/heatpump_optimizer/actions/workflows/tests.yml/runs` over 700 `pull_request` runs since 2026-09-27, with 0 page failures:
  - 28 red `closures-autofix` jobs, 17 of them `skip-failed-recording`.
  - 8 of those 17 still have an artifact. In 5, stress.py's timing verdicts alone caused the status.
  - 9 cannot be attributed, because the log printed `exit 0` for every script.
- Standing cost, `python3 tests/closure.py selftest` timed 3 times at each tree with machine load around 450: median 5.44 s at main and 9.14 s at this head.

## Red checks

- `delivery-status` grades `main`, and this diff touches nothing it reads. It is red because main's `record-autofix` staged the old delivery path. #2011 fixes that.
- `nightly-status` grades `main`, and this diff touches nothing it reads either.

## Approval

This branch changes no file under `CODEOWNERS` and no policy file. `dev/governance/rules/ci-autofix.md` is unchanged: its `skip-failed-recording` remedy still holds for a real truncation, and this change makes stress.py's timing misses stop producing that status. If a reviewer reads any part of this as policy, the orchestrator holds the owner's mandate 5951564627 to approve it.

## Forward-carry

none

## Friction

- ci-autofix.md: stale: it says "On `skip-failed-recording` the script named in the `closures` log stopped", but on main that log named no script. Every `done` line printed `exit 0`, because `$?` sat inside the same echo as `$(date)`. This branch fixes the log, and the rule's sentence is now true.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
