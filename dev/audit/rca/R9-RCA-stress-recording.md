# R9-RCA-stress-recording: a stress.py timing miss read as a truncated recording

The root-cause seat `r9c-rca-stress`. It ran beside PR **#1987** (`fix/r9-dbg-1`) and not
inside it (`dev/governance/roles/root-cause.md`, `dev/governance/rules/defect-root-cause.md`).

**Trigger.** This was the third instance on one PR, so it is a recurrence. At heads
`cf9de4e2`, `705c3be3` and `95ad5034`, `closures` printed a real UNDER-SCOPED. The cause was
that `tests/debug_collect.py` reads
`custom_components/heatpump_optimizer/quiet_windows.py`. `closures-autofix` answered
`skip-failed-recording` every time, so it never re-recorded the closure. The under-scope
waited for a human for three pushes, from 20:26Z on 2026-10-06 to 02:57Z on 2026-10-07.

**Class.** I2 (`bugclasses.json`, barriered): a closure diverges from the real dependency
graph. This instance did not escape the barrier, because `closures` caught it. What failed
was the repair path behind the barrier.

## 1. Cause (reproduced from the runs' own artifacts)

The three runs are Tests 37526452102, 37539776088 and 37564484318. In each, the
`closure-recordings` artifact (`gh run download <run> -p closure-recordings`) holds
`stress.py.json` with `"rc": 1`. It is the only recording with a nonzero rc. Each
`stress.py.out` ends `N of 104 STRESS CHECKS FAILED`. Every `FAIL` line in those files is a
CPU-ratio verdict:

| run | head | stress.py FAIL lines (all timing) | recorded seconds |
|---|---|---|---|
| 37526452102 | cf9de4e2 | own-budget: typical_slab/winter 16.2x vs 11.3x | 825.2 |
| 37539776088 | 705c3be3 | own-budget (3 scenarios); sweep 54.59x vs 52.44x | 756.4 |
| 37564484318 | 95ad5034 | per-scenario CPU: 329x vs 268x | 1082.4 |

The run reached its last line, so the recording is complete. The rc says nothing about
truncation here. It reports a timing verdict made in a different environment from the
gate:

- **The gate** runs stress.py "alone on the box". In the `fast (3.14)` job of 37564484318 it
  passed in 281 s with reference solve 28.2 ms. The worst scenario was 247.5x against the
  268x budget.
- **The recorder** runs stress.py under `tests/derive_closures.sh`'s lane 1. That lane runs
  beside lanes 2 and 3, and an audit hook fires on every open. Under those conditions the
  reference solve was 53.8 to 112.9 ms, and the worst scenario reached 178x to 329x.

`apply_under_scoped_recordings` (`tests/closure.py`) returns `skip-failed-recording` for any
`rc != 0` once UNDER-SCOPED is printed. `merge(allow_failures=False)` refuses the same
records.

**Contributing cause: the log line was wrong.** `derive_closures.sh`'s `rec()` printed
`done $script (exit $?)` in one echo with `$(date ...)`. The `$?` it printed was therefore
the date substitution's status, always 0. Every `closures` log in the table above prints
`done tests/stress.py (exit 0)`. That is the log `ci-autofix.md` sends the reader to: "On
`skip-failed-recording` the script named in the `closures` log stopped". The log named no
script. A one-line bash reproduction shows this:
`false; echo "[$(date +%H)] (exit $?)"` prints `(exit 0)`.

## 2. Process state: (c), followed and wrong

Each step worked as written. The recorder kept the rc. The autofix classified it and went
red, as `#528` meant it to. The rule told the reader to fix the named script. The defect is
in the unit the autofix uses: **`rc != 0` stands for "stopped early"**, and stress.py breaks
that equivalence. It is the one recorded script whose verdicts depend on the machine it runs
on.

This is not (b), because nothing was skipped. It is not (d) either, because the precondition
never held:

- stress.py's CPU budgets date from #77 (2026-08-28).
- Lane 1 has run stress.py beside the other lanes since #84 (2026-08-28).
- `skip-failed-recording` dates from #528 (2026-09-06).

What changed was the headroom, not the rule. The constants were re-derived against the
alone-on-box ruler in F2.5 (`0e3dc0a3`, 2026-09-28), and the budgets in F10.2 (`3d844990`,
2026-10-01). The gate's own margin is now 8% (247.5x against 268x). The recording
environment crosses that margin, and every attributable instance is dated 2026-10-05 or
later. The rule also already describes this kind of failure: `ci-autofix.md`'s truncation
bullet says a script "that fails *only* under recording" would not redden `fast`. A firmer
instruction would therefore add nothing. The countermeasure has to change the unit.

## 3. How far the class reaches

The seat searched `pull_request` Tests runs since 2026-09-27: 700 runs, 0 API page
failures. It used `gh api .../actions/workflows/tests.yml/runs` and `.../runs/<id>/jobs`.
Results:

- **28** red `closures-autofix` jobs, and **17** of them were `skip-failed-recording`.
- **8** of those 17 still have a `closure-recordings` artifact.
- **5** were stress.py alone with every FAIL a timing verdict:
  - fix/r9-dbg-1 ×3: the three runs in section 1.
  - fix/r9-sw-5: 37525837411. Per-scenario CPU 306x.
  - fix/r9-sw-model-pr: 37360319023. Own-budget winter/1z/dhw.
- **1** was stress.py's timing failures together with four scripts that genuinely failed:
  fix/r9-sw-model-pr, 37251378678 (config_flow_steps, doc_claims, entities,
  harness_headers).
- **1** was a genuine failure in harness_headers.py: 37453972072, with header figures off by
  one.
- **9** could not be attributed. No artifact remains, and the log printed `exit 0` for every
  script.

So of the 8 that can be attributed, 5 were false positives, and all 5 were caused by
stress.py's timing verdicts. Other scripts that read a clock: `replay.py` and
`nightly_ha.py` are not recorded, and `structure.py` reads only a thread factor. stress.py is
the whole known reach.

## 4. Cost test

Each side is measured in wall-clock time per release cycle.

- **cost(defect)** is at least one extra full CI cycle per occurrence. On #1987 that was
  three pushes over 6.5 h, and each `closures` job took about 45 min. A seat must also
  diagnose the cause by hand. With the log reporting `exit 0`, that meant downloading
  artifacts. Taking 70 min per occurrence as a floor, and the measured frequency of 5
  occurrences in 2.1 days since 2026-10-05, gives about **2.4 occurrences a day, or about
  165 min a day**.
- **cost(countermeasure, recurring)**:
  - One `os.environ.get` per timing verdict, which is negligible.
  - stress.py's own pin, which takes milliseconds.
  - Four `closure.py selftest` pins. The selftest runs on every gate (`run_always` in
    `run.sh`). Three runs each at `origin/main` and at the head, with machine load around
    450, gave medians of 5.44 s and 9.14 s. That is **+3.7 s per gate run** at that load.
    At about 70 PR runs a day, that is about **4.3 min a day**.

4.3 min a day is less than 165 min a day, so the countermeasure is built. The bound holds:
no budget changes, and no check is weakened where the suite grades.

## 5. Countermeasure (this branch)

It addresses state (c). The rc returns to meaning only "the run reached its end".

1. `tests/closure.py` `record()` sets `HPO_CLOSURE_RECORDING=1` (`RECORDING_ENV`) in the
   environment of the script it records.
2. `tests/stress.py` adds `timing_check()`, which replaces `R.check` at its six CPU and
   wall-clock verdicts:
   - per-scenario CPU
   - own-budget
   - dramatically-cheaper
   - kernel per-call
   - sweep
   - pathological wall ceiling

   Under the recorder a miss prints `note ... not graded under the closure recorder` and
   is not counted. Everywhere else it fails as before. Every other check still counts under
   the recorder, so a genuine stress.py failure still reddens the recording.
3. `tests/derive_closures.sh` captures `rc` on its own line, so the `done` line reports the
   recording's real exit.

**Demonstrated, failing on the defect and passing once fixed** (evidence in the seat's
`evidence/`):

- *End-to-end on the real recordings.* The base `apply_under_scoped_recordings` ran at the
  #1987 head `95ad5034`, replaying each run's artifact. The artifact as CI wrote it gives
  **`skip-failed-recording`** for all three runs. With stress.py's rc set to what the
  countermeasure yields, the result is **`changed`**. The rc becomes 0 because every FAIL
  line is one of the six timing checks, and the non-timing count was 0 in all three. The
  re-recorded closure of `tests/debug_collect.py` then lists `quiet_windows.py`.
- *Selftest pins, mutation-proven.*
  - Reverting `derive_closures.sh` to main fails `done line reports a recording's exit 3`,
    because main prints `(exit 0)` for a stub that exits 3.
  - Dropping the env assignment fails `record() runs the script with
    HPO_CLOSURE_RECORDING=1`, because the probe saw `''`.
  - The head passes 36 of 36.
- *Null controls.*
  - The `exit 0` arm of the derive pin still passes at main, so the pin is not
    reading the stub's absence.
  - stress.py's pin checks that a graded miss still fails (`(1, 0, 1)`), so the recorder's
    exemption cannot make the gate green by skipping.

**Residual, left open.** The 9 unattributable runs remain unexplained. From now on, the
corrected `done` line names the failing script in the `closures` log itself.
