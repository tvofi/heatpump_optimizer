R10-HOTFIX-SWEEP-DEFERRAL-DISPATCH (owner order 2026-11-14, merge as soon as possible). When a review or edit event arrives at an unchanged head, its `refresh` job re-runs every green gate at that head, and each of those gates fails at once as a deferral. The sweep then read a deferral red on a stale-pinned pull-request run as a real verdict and dispatched a whole new code run. A dispatched run whose first gate was green also stopped counting as the head's fresh judge once refresh had turned its latest attempt red. This change is in `tools/ci/sweep.py`'s fresh-run decision only. `tools/ci/gate.py` is not changed, and neither is `refresh`; the sweep imports `gate.busy`.

- `Sweep.judged(r)`: a dispatch at the head is its fresh judge while it is not completed, while it is green, or when its first attempt's gate concluded `success`. It reads `actions/runs/<id>/attempts/1/jobs` with `per_page` 100, and only for a completed, non-green dispatch past attempt 1. #3544's gate was job 41 of 41, so a default page of 30 misses it. If that read is unreadable (not HTTP 200, no gate) it is no judge, so the sweep dispatches as today and is never silent. A rate limit propagates as before (`RATE-LIMITED`).
- `Sweep.covered_deferral(run, gate, runs)` is the deferral predicate, narrowed after #3584's fix review (blocked at b17c7877, cases B and C; the orchestrator ruled for the reviewer's option (b)). A red is a deferral only if `gate.busy()` was true when its gate started. The sweep imports the gate's own `busy()` and does not restate it. It calls `busy()` on the runs at the head as `listed_at(run, jobs, t0)` reconstructs them from their job stamps at the red gate's start `t0`:
  - a job that had not started by then reads queued;
  - one that had started and was unfinished reads in progress;
  - a skipped job reads skipped whatever its stamps say, because GitHub re-stamps skipped jobs at every gate re-run;
  - a run counts as completed only if it had jobs and all of them were done, and a run created after `t0` is absent;
  - the title is the run's `display_title`, which `judging()` reads.

  So a higher-id run whose gate had started, a judging run, a completed run and any job `busy()` never reads (a report-only job) make no deferral. The second condition is unchanged: some gate at the head is green and covers the newest event (`covers_newest`). When both hold, `fresh()` posts no dispatch, prints `STALE-PIN ... is a deferral ...; re-run in place` and returns False, so `judge()` re-runs the gate in place within `must_rerun`'s ATTEMPT_CAP. With nothing green (#3261's pair, reviewer case D) it still dispatches. The test runs after the existing `later` and `self.dispatches` checks.
  - Residual, in the conservative direction: `listed_at` reads the latest attempt's stamps, so a run whose own later gate re-run re-queued jobs reads unfinished at an earlier `t0`, and the red is re-run in place. #3584's reviewer measured an in-place re-run as outcome-equivalent: no false green, and a persisting real red stays red. Carry: dismissed: conservative direction, outcome-equivalent by the review's measurement
- Deferral cannot be read from the gate's text. That text is in stdout and the step summary only; check run 132385059558, run 43531915583 attempt 3, shows `output` null and only "Process completed with exit code 1." among its annotations.
- Which copy of sweep.py judges an open PR's reds after this merges:
  - `gate-sweep.yml` (`workflow_run`) checks out `${{ github.sha }}`, which is the default branch. So main's copy judges at once for every completed CI run whose actor is not the bot. That covers review and edit runs, App pushes, and every recorded dispatching sweep below.
  - `ci.yml`'s `sweep-self` restores `tools/ci/*.py` from `github.event.pull_request.base.sha` for a pull_request run. That is the PR's pinned base, an old copy, used only for a bot-actor pull_request run (a token push). For a `workflow_dispatch` run it restores from `origin/<base>` fetched at job start, which is main's copy at once.
  - So the fix reaches already-open PRs at once in every path that dispatched here. The one exception is a bot-actor pull_request run's own sweep-self, which keeps its pinned copy until the PR's base moves past this merge.
  - Recorded: the dispatch at #3544 came from gate-sweep run 43573334631, created 07:55:19Z, the settle for R1 43572050013's completion. Its log shows `STALE-PIN e23124ff...: run 43512354900's gate ... re-judged by a fresh run dispatched` and then three `left to this sweep's dispatched run` lines, and run 43574296856 was created 08:07:30Z.
- Loop bound. The 11-08 loop was a pinned `busy()` re-run forever. An in-place re-run here is still a `judge()` re-run, so the same limits apply:
  - once per sweep (`rerun_ids`), and refused at attempt 44 (`must_rerun`);
  - in settle, never again while it is the bot's attempt with no source after it (`settled`). A deferral needs a source after its start, and a gate re-run adds no source, because a gate is no source and skipped jobs are excluded.
  - The self-test shows a re-run that defers again, swept from itself, left by settle. The green decider's own sweep then re-runs it once, and attempt 44 is left at the cap.

## Head

54e622286520d349f921879be62310625555bdd0. It fast-forwards the PR head b17c78773410 (code 2fa16a7e plus the delivery row) and is on origin/main f7e7a0244a. The repair round after the fix review blocked at b17c7877 narrows the deferral predicate to `gate.busy()` at the red gate's start.

## Mutation proof

Harness: `python3 tools/ci/sweep.py --self-test`, 108 checks, 0 failed at the head.
- Failing test first, round 1, a68d95d4e4 (test alone): `sweep self-test: 94 checks, 3 failed` at origin/main's sweep.py. The #3544 replay of gate-sweep run 43573334631 reproduces its live log line for line at main (one dispatch, `dispatches=1`) and dispatches nothing at the head.
- Failing test first, round 2, bbf951963e (test alone, on b17c7877): `sweep self-test: 101 checks, 3 failed`. The failures are #3584 B and C (C at two gate starts): a real red beside a job `busy()` never reads, re-run in place at b17c7877's code. The final self-test against b17c7877's sweep.py fails the same three B/C checks.
- `tools/audit/seat/mutant_run.py --diff origin/main...HEAD --path tools/ci/sweep.py --cmd 'python3 tools/ci/sweep.py --self-test'` drew 30 mutants and killed 28. Two survivors:
  - `per_page 101` is equivalent at GitHub's cap of 100. Carry: dismissed: equivalent at GitHub's page cap
  - `created_at < t0` for `<=` changes only a run created in the very second the red gate started. Reading that run as listed is the conservative side (in-place re-run). A fixture that observes it needs a second green gate covering a run created after the first green. Carry: dismissed: a same-second boundary on the conservative side
- Spec, `mutant_run.py --spec` with the same command: 23 hand mutants, 22 killed, NULL survived.
  - One mutant per leg of the narrowed predicate: busy never, always, negated; cover dropped, `all`, and `or`; created filter dropped; `t0` from `completed_at`; skipped read by stamp; completion strict; no job ever completed; always in progress; always queued; a jobless run done; status always open or always done; title dropped.
  - Plus the earlier `judged` mutants (today's predicate, any conclusion, attempt 2, no per_page) and the deferral returning True.
  - Survivor `others-include-self` is equivalent: `busy()` drops the red's own run by `ctx["run_id"]`, and that run's red gate never covers. Carry: dismissed: equivalent by busy()'s own-run exclusion

## Null control

Over the overlap domain, where a real red's gate started while another run still had a job unfinished. Each of these dispatches at origin/main, at b17c7877 only where noted, and at the head:
- B: the covering green run's report-only job (`tests / nightly-status`) finished after the red started.
- C: a newer review run with a non-unit job (`refresh`) finishing after the red, its gate started before the red or after it.
- The reviewer's C: a newer run whose gate was running at the red's start, with `governance / delivery-status-publish` unfinished after it.
- A newer gate that started in the red's own second.
- A lower-id completed run with a skipped job re-stamped after the red, or a unit completed in the red's own second.

B and both C variants are re-run in place at b17c7877, the defect.

The deferral side, re-run in place at the head:
- the #3544 recording and its replay;
- a governance unit of a newer, gate-not-started run unfinished at the red's start;
- a run listed with no job yet;
- a source finishing in the red gate's window.

The other nulls:
- A (a real red, no dispatch at the head) dispatches once, and so do a red-first dispatch and an unreadable attempt 1 (404). A red dispatch at attempt 1 makes 0 attempt reads.
- D (#3261-shaped: a deferral with nothing green) dispatches.
- Attempt 44 is left at the cap.
- Every earlier stale-pin check is unchanged.
- `python3 -I tools/ci/gate.py --self-test`: 106 checks, 0 failed.

## Figures

- `python3 tools/ci/sweep.py --self-test`: 108 checks, 0 failed.
- `python3 -I tools/ci/gate.py --self-test`: 106 checks, 0 failed.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `python3 -I dev/audit/harnesses/r10_rca_sweep_settle_loop.py replay`: `RESULT replay reruns=1 max_attempt=2 sim_minutes=1 alarm=no`.
- `python3 -I dev/audit/harnesses/r10_gate_busy_defer_3.py replay`: `RESULT replay wait_s=0 first=FAIL swept=yes final=PASS`.
- `python3 -I dev/audit/harnesses/r10_sweep_driver_arm.py`: `SWEEP-ARM rc 0`.
- `r10_gate_defer_read_final.py selftest` fails 2 identically at origin/main's sweep.py (`predicted_listed: want 129, got 38`), so it is not this diff. Carry: dismissed: pre-existing at origin/main, the harness measures the loop R10-HOTFIX-SWEEP-SETTLE-LOOP removed

## Red checks

none.

## Root cause

- Cause: the sweep read every completed red gate on a stale-pinned pull-request run as a verdict, and keyed "a fresh judge exists" on a dispatch's latest attempt. `refresh` (ci.yml `refresh`, `gate.refresh`) re-runs every green gate at an unchanged head on each edit or review event. Each re-run defers at once to the new run (`gate.deferral`), which turns the old dispatch's latest attempt red too.
- Process state (c): the stale-pin dispatch (a5ee73e39f, 11-08) and its #3446 repair were each tested on shapes with one red kind. No fixture held a refresh-made deferral beside a covering green.
- Cost: run 43563862488 (#3570's second dispatch), created 05:55:56Z and completed 07:41:26Z, is 1h45m30s per event with the PR BLOCKED on its queued gate. Every open PR is stale-pinned since #3557 and #3573 changed tools/ci on main.
- Countermeasure: this fix, plus the recorded #3544 shape and the dispatching sweep's replay in the sweep's own self-test, which runs in governance's `gate-sweep` step.

## Forward-carry

- Whether `refresh` should re-run a green gate that already covers the newest event (each re-run is a deferral red that only the sweep can clear) is out of this group's scope by the brief. `tools/ci/gate.py` `refresh`, ci.yml's `refresh` job. Carry: R11-INTAKE-R10-RESIDUE

## Friction

none
