Fix review: merge 5c091c198bb3d4663df171b918ecc80eb415428b

bus-nonce: 211ac2c587dfe2b241422fc70d02c834

Round 1. Measured head 5c091c198bb3d4663df171b918ecc80eb415428b (authored code head 5576bcdba; the head adds only the delivery row). Merge base bfd61aaf1. The governance roles directory is unchanged between the merge base and origin/main.

## Findings

- The new pins call `headroom_verdict` directly, and `closure.py`'s selftest pins only the spelling of the variable. Nothing committed pins that `run_harness` actually routes its grade through `headroom_verdict`. A mutant hard-wiring `graded, ok = True, cpu <= bound * CPU_HEADROOM` inside `run_harness` leaves every committed pin green (I only reasoned this from the code; I did not run that mutant). The behaviour is covered end to end only by my plant below, which is not committed. The wiring is three lines, and the headroom grade is itself read by the fast lane on every PR. Carry: dismissed: three-line wiring, covered end to end by the plant in Evidence, not worth a pin of its own

## Evidence

- RESULT mutation: dropping the flag check in `headroom_verdict` (ev/mutant_diff.txt) turns "a recorded run does not grade the CPU headroom (closure.py's flag)" red (`[(True, False)]`) in ev/hh_mutant.txt, and nothing else new. Red-first commit 50423394a is the author's; I did not re-run it separately.
- RESULT plant (frontier bound lowered to 160 s, its cost about 150 s, so past the 80 s headroom), driver `plant.py` kept beside this verdict:
  - without the flag: `FAIL ... costs at most 50% of its CPU bound [cpu=149.4s against 80s]`, rc 1 (ev/plant_noflag.txt).
  - with `HPO_CLOSURE_RECORDING=1`: `headroom not graded under HPO_CLOSURE_RECORDING=1`, and `exits 0` plus every RESULT line still checked and ok (ev/plant_flag.txt). The flagged run's total drops from 112 to 103 checks, which is exactly the nine headroom checks. Both runs end rc 1 only because of my environment's failures below.
- RESULT null control: with the flag unset, the headroom is graded on all nine harnesses (ev/hh_head_unflagged.txt), and the pins "unrecorded run past half its bound still fails" and "within it passes" are ok.
- RESULT environment: this container runs python 3.11, not CI's 3.14, so `dev/audit/rounds/round4/D6/claims.py` and one inlined-walk check fail to compile (14 of 112 in ev/hh_head_unflagged.txt). That is my environment, not the PR. Every headroom line and every other harness line is ok.
- Flag cannot leak: `git grep HPO_CLOSURE_RECORDING` at the head names only `closure.py` (`env[RECORDING_ENV] = "1"` in `record()`), `stress.py`, `harness_headers.py` (read), the closure selftest pin and RCA/bugclass prose. No workflow file or shell script under `.github`, `tools` or `tests/*.sh` sets or mentions it. The fast lane's "Run the suite" step sets `HPO_CI_METRICS`, `GOLDEN_MODE`, `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS` and `MKL_NUM_THREADS`, none of them the flag. `headroom_verdict` matches the exact string "1" only. A stray env var in CI could disable the grade, but only by someone adding it to the workflow, which a diff would show.
- Fast lane grades it: `tests/run.sh` line 666 calls `run_always "$PYTHON" tests/harness_headers.py`, so the scoped gate always runs it, without the flag. A push to main forces a full gate. No grade is lost.
- The skip skips only the headroom: the `exits 0` check and the RESULT comparisons come before it in `run_harness` and are unchanged. The diff contains no change to `CPU_HEADROOM = 0.5` or to any bound or `WALL_LIMIT_S`; the 240 s figure is 0.5 of the 480 s bound.
- Closure selftest: ALL 113 pins PASSED (ev/closure_selftest.txt). The body's 112 harness-header checks matches the unflagged run's total.
- Scoped gate: `closure.py select --diff <merge base>` prints `MODE: FULL -- every test script runs, nothing is scoped out. reason: tests/closure.py changes the gate itself` (ev/select.txt). The full gate is CI's to run.
- Merge: `git merge-tree --write-tree origin/main 5c091c198` exits 0, no conflicts, at origin/main a6620c3 (ev/merge_tree.txt held the earlier main). No main commit after the merge base touches `harness_headers.py`, `closure.py` or `run.sh`.
- Version: `VERSION`, the manifest and the release notes are untouched in the diff. Commit messages hold no Claude, Co-Authored-By or session lines.
- Body checks: head sha in the body matches the measured head; Red checks `none`; Forward-carry `none` (no later stage changes because of this fix).
- CI (one bulk check-runs read, ev/checkruns.txt): 35 runs; 31 concluded success, skipped or neutral. At read time `closures`, `fast (3.14)`, `coverage` and `Analyze (python)` were still in progress, none red. I cite CI's heavy runs and did not re-run them.
