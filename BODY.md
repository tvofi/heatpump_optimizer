R10-OUTSIDE-DISINFECTION-SETPOINT, built on outside pull request #3439 (Bankaifan, fork head f9a7bcb4ee; adopted as feeb0b6b39 with the author kept and the tool trailers dropped by the ref_privacy.py guard's attribution classes). With Pump duty control writing the hot-water set-point, a disinfection cycle wrote the everyday set-point (stock pair 55/60: 55.0 on a booked and on a held step), so the pump's own thermostat ended the cycle below its target; and the set-point repair stood permanently against the arbiter's own 55, its Fix (60) rewritten to 55 at the next step.

The rule for a cycle's temperature now has one owner on `ThermalParameters`: `dhw_disinfection_temp` (the disinfection temperature where a cycle runs, else `None`: the one cycle predicate) and `dhw_cycle_temp` (the higher of the everyday set-point and that). `dhw_hard_max_temp` and the repair's `_dhw_floor` read them instead of each restating the flag and the max; when #3398 replaces the enabled flag with its cycle-active property it changes one line. The arbiter decides when (`_dhw_write`: the step's action books `dhw_reason` legionella, or `disinfecting` holds) and every row of `desired` that writes hot water takes that one answer; the cycle's target is rounded up onto the entity's step and bounded by its range (above the range is left to the guard's unreachable notice). `dhw_gated` is generalised from "the arbiter's gate, below the everyday set-point" to "the arbiter's own write, still as written": a record exists only while the arbiter controls the pump (`_forget` clears it when Control is left), so an install where the arbiter writes nothing keeps the repair unchanged.

Alternatives not taken: the contributor's private helper computing the max inside the arbiter (a third copy of the expression the ceiling and the floor already held); a special case in the repair for the cycle (the brief asks the existing exemption to generalise, and a special case would restate the arbiter's when-rule in a second module); folding the repair's floor onto `dhw_cycle_temp` (changes the repair on an install whose everyday set-point is above the disinfection temperature with the pump reading between them, which the null controls forbid).

`dhw_target_temperature` (`optimizer.py` predictive_info, copied onto every step's action) is left the everyday set-point: it is published beside `dhw_min_temperature` as the configured target, no production code reads it to act (`git grep -n dhw_target_temperature -- custom_components`: the optimizer's two writes, the sensor attribute, the payload type), and a cycle step already says so through its `dhw_reason` legionella; moving it would move every golden fixture that records it for a label change.

The space-only gate row (`DHW_GATE_C`) stays a gate on a step the plan booked for a cycle only when a block removed hot water from it; a held cycle turns a space step into Heating + DHW, whose write is the cycle's temperature (pinned).

## Head

1713468b91e6d7fb1345ad391b03213df1148ce9, cut from origin/main a7628041dc (origin/main's tip at 2026-11-11T07:53:22Z, `date -u`).

## Mutation proof

`python3 tools/audit/seat/r10_disinfection_setpoint_mutants.py` (this PR): each mutant applied to a detached worktree of HEAD, `tests/block_duty.py` run there, worktree removed; exit 0 only when NULL survives and every other mutant is killed. Exit 0 at the head; killed:

- `NULL` (no change): survives, 61 of 61 checks pass.
- `M1-no-cycle-write` (`_dhw_write`: `cycle = None`): killed by "a commanded or held disinfection cycle writes its temperature, not the configured set-point" and five more.
- `M2-round-nearest` (`_dhw_write`: drop `rounding="up"`): killed by "an off-step disinfection temperature is written on the step above it, never below".
- `M3-booking-ignored` (`_dhw_write`: `if inp.disinfecting`): killed by "a commanded or held disinfection cycle writes its temperature, not the configured set-point", "every row a cycle step can take writes the cycle's temperature, the idle and baseline rows too".
- `M4-hold-ignored` (`_dhw_write`: `if booked`): killed by "a commanded or held disinfection cycle writes its temperature, not the configured set-point" and four more.
- `M5-gate-only-excuse` (`dhw_gated`: restore `and written[0] < configured - SETPOINT_TOLERANCE`): killed by "the arbiter's own everyday write raises no disinfection-floor repair: it writes the cycle itself".
- `M6-excuse-any-reading` (`dhw_gated`: drop the `_differs` term): killed by "a person's value beside the arbiter's write still raises the repair, its Fix on the floor".
- `M7-flag-ignored` (`dhw_disinfection_temp`: ignore `dhw_legionella_enabled`): killed by "null control: a disabled cycle writes the everyday set-point on every row and booking".
- `M8-cycle-not-max` (`dhw_cycle_temp`: `return target`): killed by "a cycle never lowers the tank: an everyday set-point above the disinfection temperature is the cycle's and the ceiling's" (it survived the first cut: the arbiter's own everyday branch masked it; that check was added for it).
- `M9-floor-no-disinfection` (`_dhw_floor`: `return floor`): killed by "a person's value beside the arbiter's write still raises the repair, its Fix on the floor", "null control: with no arbiter write the pump's own set-point must still permit the cycle".

Failing first at main: `tests/block_duty.py` at the head copied over an origin/main a7628041dc worktree fails 7 checks, both faces among them: "a commanded or held disinfection cycle writes its temperature, not the configured set-point" (the write) and "the arbiter's own everyday write raises no disinfection-floor repair: it writes the cycle itself" (the standing repair); every null-control check passes there.

## Null control

`dev/audit/harnesses/r10_disinfection_setpoint.py` (this PR) drives the production `desired` and `setpoint_check._dhw` over 5 rows x 4 bookings for six installs and prints one line each; run at origin/main a7628041dc (the file copied over a main worktree) and at the head, then `diff <(grep '^null_' base) <(grep '^null_' head) && echo IDENTICAL` printed IDENTICAL over the 80 `null_*` lines: the cycle disabled, an everyday set-point at (60) and above (62) the disinfection temperature, and no hot-water set-point entity. Had the fix leaked into them the diff would print those lines. The 40 `stock`/`offstep` lines differ (36 lines changed): the defect's install, which is the fix. Each null control is also a check in `tests/block_duty.py` (four `null control:` checks), passing at main and at the head.

The `repair_none` column is the repair on an install whose arbiter has written nothing: unchanged on every non-cycle line (`stock none * repair_none=60` at both ends).

Precondition of the generalised exemption, stated rather than assumed: an arbiter writing an everyday set-point below `dhw_min_temp` would now be excused where main raised the repair; the options form refuses that pair (`config_flow.py` `_dhw_min_too_close`, minimum within 5 °C of the set-point), and the null-control installs carry `dhw_min_temp` 40.

## Figures

- Scoped gate: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED`; every script `scope.run` names except `tests/stress.py` (CI's, under the gate lease), plus `run.sh`'s `run_always` pair, ran green with `PYTHONPATH=tests/hastub GOLDEN_MODE=drift` (production code as at the head; the scripts the later test, ledger and budget commits reach, `features.py`, `entities.py`, `harness_headers.py`, `block_duty.py`, `structure.py` and `closure.py selftest`, re-run at the head). `tests/golden.py` green with no drift, so no fixture is claimed.
- Structure: `python3 tests/structure.py` green; `class_excess_loc` moved down and was re-recorded (commit message names the row): the two new properties are paid by tightening the hot-water ceilings' docstrings.
- Predicted reds: `python3 tools/pr/ci_predict.py` named six stale `killed_by` pins on lines this diff rewrote (`dhw_gated`, `_dhw_floor`, `dhw_hard_max_temp`), deleted by hand, and two INERT READS for the new instruments, written by `--apply-inert`; a re-run predicts no closures, fast, governance or instrument red.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0023 IMPROVES`.
- Harness: `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_disinfection_setpoint.py` at base and head, as under `## Null control`.
- Class seams (`fixer.md` step 8). Rule: `git grep -nE "\.dhw_legionella_enabled|\.dhw_legionella_temp\b" -- custom_components` (every reader of the cycle's flag or temperature) and `git grep -n '"dhw_setpoint"' -- custom_components/heatpump_optimizer/pump_arbiter.py` (every hot-water write of the arbiter). Dispositions:
  - `thermal_model.py` `dhw_disinfection_temp`: the owner, this diff.
  - `pump_arbiter.py` `_dhw_write` (two `_bounded` calls): this diff; the gate row `DHW_GATE_C`: a gate by design, pinned on a cycle step; `dhw_gated`: this diff.
  - `dhw_planner.py` (legionella step placement, `ready_temps` max with the disinfection temperature): the plan's per-step requirement the cycle must meet, a floor below `dhw_cycle_temp` by construction; not the hold temperature. Already consistent.
  - `legionella.py` (the guard's credit target and watch flags): the threshold a cycle must reach, at or below `dhw_cycle_temp` by construction; the arbiter rounds up so its write passes that test. Already consistent.
  - `coordinator.py` elastic-legionella deadline and the diagnostics echo: when a cycle is due and what is configured, not its temperature. The enabled-flag predicate in these readers is #3398's (R10-COMBI-TANK-PR-B) to replace.

## Unpinned sites

Every site `python3 tools/pr/ci_predict.py` lists is under `custom_components/`, so each is pinned by `mutation-autofix`; the named mutants that already kill the same predicate are in brackets.

- custom_components/heatpump_optimizer/pump_arbiter.py:1097 CMP_BOUND: pinned by mutation-autofix (M1, M2)
- custom_components/heatpump_optimizer/pump_arbiter.py:1097 GUARD_OFF: pinned by mutation-autofix (M1, M2)
- custom_components/heatpump_optimizer/pump_arbiter.py:1099 RETURN_DEL: pinned by mutation-autofix (M1, M2)
- custom_components/heatpump_optimizer/pump_arbiter.py:1148 RETURN_DEL: pinned by mutation-autofix (M5, M6)
- custom_components/heatpump_optimizer/setpoint_check.py:120 CLAMP_DROP: pinned by mutation-autofix (M9)
- custom_components/heatpump_optimizer/setpoint_check.py:120 RETURN_DEL: pinned by mutation-autofix (M9)
- custom_components/heatpump_optimizer/thermal_model.py:886 CLAMP_DROP: pinned by mutation-autofix (M8)
- custom_components/heatpump_optimizer/thermal_model.py:886 RETURN_DEL: pinned by mutation-autofix (M8)
- custom_components/heatpump_optimizer/thermal_model.py:891 RETURN_DEL: pinned by mutation-autofix (M7)
- custom_components/heatpump_optimizer/thermal_model.py:898 CLAMP_DROP: pinned by mutation-autofix (M8)
- custom_components/heatpump_optimizer/thermal_model.py:898 RETURN_DEL: pinned by mutation-autofix (M8)

## Red checks

- `mutation`: predicted, not yet run: the 11 sites under `## Unpinned sites` are added with no pin, which is the input `mutation-autofix` repairs by design (`ci-autofix.md`). The cheaper detector exists and ran: `tools/pr/ci_predict.py` (prepr.sh step 6d), locally, at no standing cost beyond the prepr run every seat already makes; no further countermeasure.

## Forward-carry

none

## Friction

none
