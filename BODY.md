Repair round 3 of #3181 (R10-CI-RUNNER-FIXES), answering the blocked verdict on 3339aa92b: the lane report's new `>>> ENDED BEFORE ITS SUMMARY:` line was not read by `merge_train.py` FAILED_SCRIPT, so `culprit()` named no script for a proof job whose script crashed before its summary.

Reader fix, and why this one: FAILED_SCRIPT now accepts `>>> (?:FAILED|ENDED BEFORE ITS SUMMARY): `. Chosen over appending the wording after a `>>> FAILED: <label>` prefix because it is a one-token change in the one reader that needs it, leaves the plain FAILED line byte-identical for every other reader (quiet.sh strips `^>>> FAILED: ` to get a bare label and would otherwise carry the suffix into its failed-script list), and keeps the two outcomes distinguishable in the log.

## Head
Code head 4f379445e4c4a8f0ef9a001b5b96d4aa2d451644 (repair commit 3173cce2d156676ebffc2d49d752d0a107f9f630 on PR head 3339aa92b6a60e6492263da1a6b6dd5efaa39b64, plus a merge of origin/main fad43b0471b9cef3c563d2c2ae1eab3d87a34190, which had moved; the merge brought no change to tests/run.sh or tools/audit/seat/merge_train.py). `tools/pr/prepr.sh` re-ran at this head after that merge with PREPR_SKIP_CLOSURES=1: rc=0. Partial delivery stands: carry 0 (actions: write dispatch step) is NOT built and stays in the roster carry list. Carry: dismissed: statement of scope, not a finding
Roster numbering (1-based, as the review packet counts): Carry 1 = brief carry 0 (the actions: write dispatch step, NOT built, see Forward-carry); Carry 2 = brief carry 1 (run.sh ENDED BEFORE ITS SUMMARY, done in round 1, its reader and call site pinned in this round); Carry 3 = brief carry 2 (closure.py `--cached`, done in round 1, unchanged here). Carry: dismissed: numbering note, not a finding

## Mutation proof
Fixture: `_failed_marker_self_test` in tools/audit/seat/merge_train.py, run by `python3 tools/audit/seat/merge_train.py --self-test`. It lifts `SUMMARY_LINE`, `ended_before_summary` and the report if/else out of tests/run.sh, drives them on a crash log and a failed-check log (rc=1), and feeds each printed line to FAILED_SCRIPT.
- Mutant 1, reader reverted to `>>> FAILED: `: `1 failed`, check "FAILED_SCRIPT names the script from the crash line and from the failed-check line".
- Mutant 3 (the verdict's), run.sh if/else reverted to the one-line `echo ">>> FAILED: $label"`: `1 failed`, check "run.sh's lane report still has the SUMMARY_LINE / ended_before_summary / if-else this check lifts" (the lift finds no if/else).
- Mutant 4, the negation dropped from `ended_before_summary`: `2 failed`, the crash-prints-ENDED and failed-keeps-FAILED checks.
- Each mutant restored from a byte copy afterwards.

## Null control
Unmutated head: `merge_train self-test: 442 checks, 0 failed`, the four new checks ok. The failed-check log prints exactly `>>> FAILED: python3 tests/entities.py`, not the ENDED line.

## Figures
- Self-test: `python3 tools/audit/seat/merge_train.py --self-test | tail -1` prints `merge_train self-test: 442 checks, 0 failed` at the code head before the origin/main merge (the merge touches neither file; CI's governance self-test is the authority after it).
- Verdict's harness, both ends: evidence/failed_script_regex.txt applied to the new line returned `[]` at 3339aa92b; FAILED_SCRIPT.findall on the line run.sh now prints returns `['tests/entities.py']` (the fixture's third check).
- `PYTHONPATH=tests/hastub python3 tests/entities.py` at 3173cce2d: ALL 2603 ENTITY CHECKS PASSED (run before the origin/main merge; CI reruns it). `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL` (tests.yml is a gate file), left to CI.
- Toolchain: numpy 2.5.4, scipy 1.18.1 equal tests/requirements-ci.txt; no golden was run, CI is the authority.
- Class enumeration, rule: `grep -rIn ">>> FAILED\|>>> ENDED\|ENDED BEFORE" .` over the tree (null control: the same grep matches tests/run.sh:418, the known writer). Every hit:
  - tests/run.sh:418 (writer, serial `run()`, only when JOBS<=1): unchanged, serial runs never print ENDED.
  - tests/run.sh:811 and :813 (writers, lane report): pinned by the new fixture.
  - tools/audit/seat/merge_train.py FAILED_SCRIPT (the only live reader of the lane line): fixed here, pinned.
  - merge_train.py fake-gh job log `>>> FAILED: "$PYTHON" tests/ratchet.py` (self-test fixture, job 11): still a valid FAILED line, left.
  - tools/audit/seat/orchestrator_tick.py:3633 (test fixture text `>>> FAILED: tests/stress.py`): a fixture of the plain line, not a reader; left.
  - dev/audit/rounds/round10/intake/quiet.sh:61 (live reader, `grep -E '^>>> FAILED: '`): runs the gate with GATE_JOBS=1 (serial), where only run()'s FAILED line exists, so it never sees ENDED; unaffected, left.
  - dev/audit/rounds/round3/D11/conformance_raw.json, round4/quiet-window.md, round7/QUIET.md, round6/D13/fixtures/*.json, dev/archive/handoff/r9-f2-solver-4/ev/gate_round1_head.log: recorded measurements, not readers.
  - dev/programme/rosters/wave-r10-groups.json (two carry texts): prose naming the run.sh change, not a reader.
  Result: one live reader needed the change; it is closed.

## Red checks
No check is concluded red at this head (CI has not run on it). The ancestry reds the contract lists:
- `tests / fast (3.14)` at 241f47e62: 1 of 2603 entity checks failed, "every `bash -c` / `sh -c` a check runs carries errexit", naming the new site `tests/entities.py:_gl_ended_before_summary`. Repaired in round 2 (the site runs `bash -e -c`). Cause and process state: the local entities run was cut short by a pipe, so the check was never reached; the step was skipped, not unavailable. Cheaper detector: `PYTHONPATH=tests/hastub python3 tests/entities.py` run to completion (about 7 minutes), which this round ran: ALL 2603 ENTITY CHECKS PASSED. Countermeasure: none built; the detector exists and the gap was skipping it.
- `tests / nightly-status`: inherited from main, grades main (`NIGHTLY FAILED: slow failed 1 night ago`, scheduled run 41555367389, predating this branch); the diff touches no nightly lane and it is not required by main-protect. Nothing to repair here.
- Verdict on 3339aa92b was a block with CI green: a reader no check exercised. The cheaper detector now exists: the fixture in `merge_train.py --self-test` drives the writer's output through the reader.

## Forward-carry
Carry 0 (edit run exits without holding a runner; code run's gate re-dispatches body units) is not built: it needs an `actions: write` dispatch step in the read-only `gate` job on a code-owned path. It stays verbatim in the roster carry list for this group (dev/programme/rosters/wave-r10-groups.json, group R10-CI-RUNNER-FIXES, carry[0]). Carry: dismissed: carry 0 stays in the owner's plan-regain card 9 brief for r10-ci-runner-fixes, unchanged

## Friction
none
