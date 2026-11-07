Fold the 2026-11-06 out-of-tree sweep changes into the tracked sweep instruments under `tools/audit/seat/`, and repair the one CodeQL alert the first head raised.

Owner ruling (tvofi 2026-11-06), verbatim: "There should already be tracked sweep templates/scripts for these, update them if needed".

Tracked counterparts: only `sweep_render.py` and `sweep_template.md` existed. The Gantt script, the verdict audit, the roster-drain path and the runner loop had no tracked counterpart, so they are added beside the template rather than folded into the renderer; the beat's `roster-drain` row (`beat_jobs.py`) is untouched. Host paths in the inputs were replaced by environment variables and arguments; nothing committed carries a host path or secret.

- (a) `sweep_gantt.py`: Gantt drift against a baseline. A handoff counts as work in flight only if its tip was committed within 12 h, and only fire-ledger lines from the last 12 h count.
- (b) `verdict_audit.py`: maps every open PR to its latest verdict and holder, prints `UNHELD` lines.
- (c) `sweep_runner.sh`: the sweep's mechanical steps as a loop, with the `PLAN MOVED` republish emit.
- (d) `roster_drain.py`: the manual roster-queue drain, with a pure `reconcile` core.
- `sweep_template.md` gains step (4b+) and a roster-drain sentence in (1b); `INSTRUMENTS.md` and `instruments/` pages; `governance.yml` runs the five self-tests.
- Repair: `sweep_runner_selftest.py` wrote its two fake binaries (`git`, `gh`) with mode 0o755, which CodeQL `py/overly-permissive-file` flagged (alert 51). Both callers of helper `w` that pass a mode now pass 0o700; only the owner executes them.

## Head

89f08728627d26837188df016bf0f78fc43f4596 (origin/main merged in; it moved since the first prepr run, so prepr was rerun on this head).

## Mutation proof

- `LIVE_H = 12.0` -> `1200.0` in `sweep_gantt.py`: `sweep_gantt` self-test AssertionError on the 13 h-old handoff row and `sweep_runner` self-test `FAIL a 20 h-old handoff tip no longer counts: IDLE slip`.
- `verdict_audit.py` drops the `and not held` guard: `FAIL null control: a fire in 12 h holds it`.
- `sweep_runner.sh` drops `--handoff-rows`: the same `sweep_runner` self-test FAIL.
- `roster_drain.py` marks a refusal `#done`: `FAIL refused -> #refused + ROSTER-REFUSED`.
- Alert 51: reverting the two modes to 0o755 is the mutation CodeQL `py/overly-permissive-file` reds on; no local check reads it (see Red checks).

## Null control

A 13 h-old handoff tip is dropped while the same row three hours earlier is kept; a 2 h-old tip and fire line keep the critical-path group busy where a 20 h-old one does not; a fire naming the topic holds an otherwise unheld PR; an unchanged plan page emits no `PLAN MOVED`. For the repair: `python3 -I tools/audit/seat/sweep_runner_selftest.py` prints 11 checks, 0 failed both before (0o755) and after (0o700), so the tightening changes no behaviour the self-test pins.

## Figures

- `python3 -I tools/audit/seat/sweep_gantt.py --self-test` prints 16 checks, 0 failed.
- `python3 -I tools/audit/seat/verdict_audit.py --self-test` prints 14 checks, 0 failed.
- `python3 -I tools/audit/seat/roster_drain.py --self-test` prints 9 checks, 0 failed.
- `python3 -I tools/audit/seat/sweep_runner_selftest.py` prints 11 checks, 0 failed.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` prints 0 index gaps.

## Red checks

Concluded reds at the head the PR carried (0ae78ac1), by check-run name:
- `CodeQL` and code-scanning alert 51 (py/overly-permissive-file): a real finding, fixed at the root above (0o700), not dismissed. Cheaper detector: none exists in the tree. `tools/pr/local_alerts.py` only reads alerts after a push, and no local CodeQL query run is a standing instrument; the standing cost of building one is a CodeQL CLI database build per seat, which the 23-26 minute `Analyze (python)` leg already pays on the PR, so the finding is that none cheaper exists.
- `pr-contract / pr-contract`: class stale body. The body said `none` and named neither `CodeQL` nor alert 51; this body names them. A run also reported `unreadable title`, which is the title read racing the edit, not content.
- `gate` (three runs, each ending in seconds): class dependent. It mirrors `pr-contract`, and the 23:40 and 23:45 runs were the edit-run deferral ("still being judged; their gate decides", R10-HOTFIX-GATE-BUSY-DEFER), decided by the code run, not a defect of this change.

Local gate at this head: `MODE: SCOPED -- 2 script(s) run`, 5 test scripts passed, 30 scoped out.

## Forward-carry

none

## Friction

none
