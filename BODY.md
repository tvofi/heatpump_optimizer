Fold the 2026-11-06 out-of-tree sweep changes into the tracked sweep instruments under `tools/audit/seat/`.

Owner ruling (tvofi 2026-11-06), verbatim: "There should already be tracked sweep templates/scripts for these, update them if needed".

Tracked counterparts: only `sweep_render.py` and `sweep_template.md` existed. `sweep_render.py` takes no run-time arguments and the template had no verdict-audit, Gantt or republish text. The Gantt script, the verdict audit, the roster-drain path and the runner loop had no tracked counterpart, so they are added here beside the template rather than folded into the renderer; the beat's `roster-drain` row (`beat_jobs.py`) already covers the unattended roster path and is untouched. Host paths in the inputs were replaced by environment variables and arguments; nothing committed carries a host path or secret.

- (a) `sweep_gantt.py`: Gantt drift against a baseline. A handoff counts as work in flight only if its tip was committed within 12 h (`live_handoffs`), and only fire-ledger lines from the last 12 h count (`recent_fired`); the ledger is passed as `--fired`.
- (b) `verdict_audit.py`: maps every open PR to its latest verdict and holder, prints `UNHELD` lines; the runner runs it every second pass.
- (c) `sweep_runner.sh`: the sweep's mechanical steps as a loop, with the `PLAN MOVED` republish emit; configured by `SWEEP_*` environment variables.
- (d) `roster_drain.py`: the manual roster-queue drain, with a pure `reconcile` core.
- `sweep_template.md` gains step (4b+) and a roster-drain sentence in (1b); `INSTRUMENTS.md` and `instruments/` pages; `governance.yml` runs the five self-tests; the four new files are classified as inert reads of `tests/entities.py` by `ci_predict.py --apply-inert`.

## Head

a6259e84a09e726c6a9b41d55acf6260dab9026e (main had not moved since the prepr run, merge base 28482eceeb6b9809e44b12d80fc994282cc21645, so no second run).

## Mutation proof

Each mutation was applied to one tracked file and the matching self-test went red; the file was then restored and the self-tests went green again.
- `LIVE_H = 12.0` -> `1200.0` in `sweep_gantt.py`: `sweep_gantt` self-test AssertionError on the 13 h-old handoff row, and `sweep_runner` self-test `FAIL a 20 h-old handoff tip no longer counts: IDLE slip` (11 checks, 1 failed).
- `verdict_audit.py` drops the `and not held` guard on the merge-train line: `FAIL null control: a fire in 12 h holds it` (14 checks, 1 failed).
- `sweep_runner.sh` drops `--handoff-rows`: `sweep_runner` self-test `FAIL a 20 h-old handoff tip no longer counts: IDLE slip` (11 checks, 1 failed).
- `roster_drain.py` marks a refusal `#done`: `FAIL refused -> #refused + ROSTER-REFUSED` (9 checks, 1 failed).

## Null control

Each quantified claim has a control that changes one input. A 13 h-old handoff tip is dropped while the same row three hours earlier is kept; a 2 h-old tip and a 2 h-old fire line keep the critical-path group busy where a 20 h-old one does not; a fire naming the topic holds an otherwise unheld PR; an unchanged plan page emits no `PLAN MOVED`; a queue with no roster configured prints no `ROSTER-` line; an all-pushed drain prints no problem line.

## Figures

- `python3 -I tools/audit/seat/sweep_gantt.py --self-test` prints 16 checks, 0 failed.
- `python3 -I tools/audit/seat/verdict_audit.py --self-test` prints 14 checks, 0 failed.
- `python3 -I tools/audit/seat/roster_drain.py --self-test` prints 9 checks, 0 failed.
- `bash tools/audit/seat/sweep_runner.sh --self-test` prints 11 checks, 0 failed.
- `python3 -I tools/audit/seat/sweep_render.py --self-test` prints 34 checks, 0 failed (the new template text renders and cites only instruments in the tree).
- `python3 -I tools/audit/seat/selftest_wiring.py --check` prints 122 self-testing, 122 wired, 0 unwired.

## Red checks

none

## Forward-carry

none

## Friction

none
