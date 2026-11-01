Triage batch 104 rules one queue proposal from the orchestrator s10 (2026-11-01T17:49:18Z): promote the session-local Gantt-drift stand-in, which the owner ordered, to a tracked instrument. It is the rolling batch after batch 103.

- **P361: ACCEPT, as a new fly-in group R10-FLY-GANTT-DRIFT (size S, sonnet fixer, opus reviewer).**
  - **Why it is owed.** The orchestrator's sweep already runs the stand-in after each replan and plan render. `orchestrator.md` section 13 makes a session-local instrument a defect.
  - **Its first run** (the 17:48Z acks file) reported 3 IDLE slips, one acted on and two deferred on the dispatch cap.
  - **What promotion adds.** No new run, one S fixer, and a self-test that CI enforces through `selftest_wiring.py --check`. The new files sit under `tools/`, which no structure budget measures.
  - **Why not R10-PLAN-REAL-DURATIONS.** #3097 is in flight, so a carry would refuse its review packet. It owns the duration model and the render, a different seam.
  - **The stand-in's self-test** uses bare `assert`s that no mutant pins. The brief requires `check()` counting and a mutant per arm.

The roster op is queued `#held` and released when this file is on main: one `append-group R10-FLY-GANTT-DRIFT`. No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`18db0281a502ccca3ddd70cf850fab662d3a3d88`; the file is the whole diff against `ca6333333`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P361 as `ACCEPT`, and `triage_refusal` passes the group's brief and `resume.note`.
- With P361's verdict flipped to `REJECT`, they are refused: `dev/programme/triage/s6-batch104.md#P361 is not an ACCEPT ruling (REJECT)`.
- On roster branch `1bc687570`, `op_append_group` with the duration model's sizes applies: 302 groups become 303.

## Null control

- With the file absent, the brief is refused: `the triage ruling dev/programme/triage/s6-batch104.md is not on the roster branch or origin/main`.
- The stand-in run on the live inputs at 17:54Z prints no `GANTT-SLIP` line, because all three slips are acked.

## Figures

- The stand-in's self-test prints `gantt_drift self-test: 9 checks passed` in 0.04 s real time.
- The stand-in is 191 lines (`wc -l`).
- `node tools/policy/brief_lint.mjs` on the roster after the op: `TOTAL: 0 error(s)`.
- `tests/structure.py` measures only `custom_components/` (`PACKAGE_DIR`, line 241).

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
