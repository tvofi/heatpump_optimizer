R10-HOTFIX-SWEEP-DEFERRAL-DISPATCH (owner order 2026-11-14, merge as soon as possible). When a review or edit event arrives at an unchanged head, its `refresh` job re-runs every green gate at that head, and each of those gates fails at once as a deferral. The sweep then read a deferral red on a stale-pinned pull-request run as a real verdict and dispatched a whole new code run. A dispatched run whose first gate was green also stopped counting as the head's fresh judge once refresh had turned its latest attempt red. This change is in `tools/ci/sweep.py`'s fresh-run decision only. `tools/ci/gate.py` is not changed, and neither is `refresh`.

- `Sweep.judged(r)`: a dispatch at the head is its fresh judge while it is not completed, while it is green, or when its first attempt's gate concluded `success`. It reads `actions/runs/<id>/attempts/1/jobs` with `per_page` 100, and only for a completed, non-green dispatch past attempt 1. #3544's gate was job 41 of 41, so a default page of 30 misses it. If that read is unreadable (not HTTP 200, no gate) it is no judge, so the sweep dispatches as today and is never silent. A rate limit propagates as before (`RATE-LIMITED`).
- `Sweep.covered_deferral(run, gate, runs)` is the deferral predicate, read structurally (ruled by the orchestrator, option B). The deferral text is in the gate's stdout and step summary only, and the API the sweep uses does not expose either. Check run 132385059558, run 43531915583 attempt 3, shows `output` null and its two annotations are "Process completed with exit code 1." and a runner notice. The predicate has two parts:
  - a source of another run finished after this red gate started, or has not finished (`source_after`, settle's own reading; `gate()` reads `busy()` before any source);
  - some gate at the head is green and covers the newest event (`covers_newest`).
  When both hold, `fresh()` posts no dispatch. It prints `STALE-PIN ... is a deferral ...; re-run in place` and returns False, so `judge()` re-runs the gate in place within `must_rerun`'s ATTEMPT_CAP. With nothing green, #3261's pair keeps its dispatch, and that self-test check is unchanged. The test runs after the existing `later` and `self.dispatches` checks, so a head that already has a fresh judge still leaves its reds to it, as before.
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

2fa16a7eac0b32a25a4c20205286579257d77d55, on origin/main f7e7a0244a.

## Mutation proof

Harness: `python3 tools/ci/sweep.py --self-test`, 98 checks, 0 failed at the head.
- Failing test first, a68d95d4e4 (test alone): `sweep self-test: 94 checks, 3 failed` at origin/main's sweep.py. The final self-test against origin/main's sweep.py gives `98 checks, 7 failed`, and those are the seven new `#3544` checks that need the fix. The recorded replay at origin/main reproduces gate-sweep run 43573334631's log line for line: one dispatch, three `left to this sweep's dispatched run`, D re-run in place, `dispatches=1`.
- `tools/audit/seat/mutant_run.py --diff origin/main...HEAD --path tools/ci/sweep.py --cmd 'python3 tools/ci/sweep.py --self-test'` drew 19 mutants and killed 18. One survivor: `sweep.py:234 CONST_SWAP {"per_page": 101}`. It is equivalent, because GitHub caps `per_page` at 100. A deleted `per_page` is killed by the fake's 30-job default page. Carry: dismissed: equivalent at GitHub's page cap
- Spec pass, `mutant_run.py --spec` with the same command: 13 of 13 hand mutants on the two predicates killed, NULL survived. They are: the deferral test dropped or negated; the cover test dropped, `all` for `any`, and `or` for `and`; the deferral read from `completed_at`; the run's own jobs read as others'; `judged` reverted to today's predicate; any first-attempt conclusion accepted; attempt 2 read instead of 1; `per_page` dropped; the deferral checked before the fresh judge; and the deferral returning True (no re-run).

## Null control

Each passes at origin/main and at the head:
- A real red on a stale pin with no dispatch at the head takes one dispatch. The red gate here judged after every other run's source finished, even with its own run's job finishing later.
- A real red beside a dispatch whose first attempt was red dispatches once, and so does one beside a dispatch whose first attempt cannot be read (404).
- A red dispatch at attempt 1 makes 0 attempt reads.
- #3261's settle pair, two deferrals with nothing green, takes one dispatch.
- Every earlier stale-pin check is unchanged: fork head, non-tools/ci base move, 300-file cap, two reds one dispatch, the dispatched judge's in-place re-runs (#3400), and the #3446 one-judge-per-head checks.
- `python3 -I tools/ci/gate.py --self-test`: 106 checks, 0 failed.

## Figures

- `python3 tools/ci/sweep.py --self-test`: 98 checks, 0 failed.
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
