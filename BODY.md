R10-OUTSIDE-DISINFECTION-SETPOINT, built on outside pull request #3439 (Bankaifan, fork head f9a7bcb4ee; adopted as feeb0b6b39 with the author kept and the tool trailers dropped by the ref_privacy.py guard's attribution classes). With Pump duty control writing the hot-water set-point, a disinfection cycle wrote the everyday set-point (stock pair 55/60: 55.0 on a booked and on a held step), so the pump's own thermostat ended the cycle below its target; and the set-point repair stood permanently against the arbiter's own 55, its Fix (60) rewritten to 55 at the next step.

The rule for a cycle's temperature now has one owner on `ThermalParameters`: `dhw_disinfection_temp` (the disinfection temperature where #3398's `legionella_cycle_active` holds, else `None`: the one cycle predicate) and `dhw_cycle_temp` (the higher of the everyday set-point and that). `dhw_hard_max_temp` and the repair's `_dhw_floor` read them instead of each restating the predicate and the max. The arbiter decides when (`_dhw_write`: the step's action books `dhw_reason` legionella, or `disinfecting` holds) and every row of `desired` that writes hot water takes that one answer; the cycle's target is rounded up onto the entity's step and bounded by its range (above the range is left to the guard's unreachable notice). `dhw_gated` is generalised from "the arbiter's gate, below the everyday set-point" to "the arbiter's own write, still as written": a record exists only while the arbiter controls the pump (`_forget` clears it when Control is left), so an install where the arbiter writes nothing keeps the repair unchanged.

Alternatives not taken: the contributor's private helper computing the max inside the arbiter (a third copy of the expression the ceiling and the floor already held); a special case in the repair for the cycle (the brief asks the existing exemption to generalise, and a special case would restate the arbiter's when-rule in a second module); folding the repair's floor onto `dhw_cycle_temp` (changes the repair on an install whose everyday set-point is above the disinfection temperature with the pump reading between them, which the null controls forbid).

`dhw_target_temperature` (`optimizer.py` predictive_info, copied onto every step's action) is left the everyday set-point: it is published beside `dhw_min_temperature` as the configured target, no production code reads it to act (`git grep -n dhw_target_temperature -- custom_components`: the optimizer's two writes, the sensor attribute, the payload type), and a cycle step already says so through its `dhw_reason` legionella; moving it would move every golden fixture that records it for a label change.

The space-only gate row (`DHW_GATE_C`) stays a gate on a step the plan booked for a cycle only when a block removed hot water from it; a held cycle turns a space step into Heating + DHW, whose write is the cycle's temperature (pinned).

## Head

49a45dd8a8aad27f63b797bc747e79d9246e439a, origin/main cbd23f1c8b merged in (origin/main's tip at 2026-11-11T09:18:35Z, `date -u`); the branch was cut from a7628041dc.

## Merge resolution (delta from 1713468b)

`git merge origin/main` at 1713468b conflicted in three files against #3398 (R10-COMBI-TANK-PR-B), which replaced the readers' `dhw_legionella_enabled` with `ThermalParameters.legionella_cycle_active` (enabled, and not an active combi store at or under `COMBI_LEGIONELLA_POTABLE_LIMIT_L` unless forced). Each hunk keeps both behaviours:

- `thermal_model.py` `dhw_hard_max_temp`: this group's form (`min(70.0, dhw_setpoint if dhw_cycle_temp is None else dhw_cycle_temp)`), and `dhw_disinfection_temp` now reads `legionella_cycle_active` where it read `dhw_legionella_enabled`. Main's `if self.legionella_cycle_active: top = max(top, dhw_legionella_temp)` is that expression through the owner, so main's ceiling is unchanged and #3398's gating now reaches the arbiter's write and the repair too.
- `setpoint_check.py` `_dhw_floor`: this group's form (`max(floor, dhw_disinfection_temp)` where not `None`), equal to main's `legionella_cycle_active` branch through the same owner.
- `tests/features.py`, three fakes (`_p8_setpoint`, `_pa_mbs._thermal_params`, the `_df_sc.evaluate` space-slot check): this group's real `ThermalParameters` (`_r9f12_tp`), from which `legionella_cycle_active` derives (combi off by default, so equal to the flag); main's namespace fakes carried `legionella_cycle_active` by hand and no `dhw_disinfection_temp`.

Commits after the merge: `b8736ad3` adds a `tests/block_duty.py` check on an active combi store holding 2 L (forced and unforced, over the three cycle bookings), retargets M7's anchor to the merged line and adds M10; `1aa850c2` records `class_excess_loc` down (main's own reduction under this branch's recorded budget); `49a45dd8` deletes #3398's two `killed_by` pins on the rewritten lines (`_dhw_floor` GUARD_OFF ea9e613f, `dhw_hard_max_temp` GUARD_OFF f3c560aa), which `ci_predict.py` named STALE PIN.

## Mutation proof

`python3 tools/audit/seat/r10_disinfection_setpoint_mutants.py` (this PR): each mutant applied to a detached worktree of HEAD, `tests/block_duty.py` run there, worktree removed; exit 0 only when NULL survives and every other mutant is killed. Exit 0 at 49a45dd8; killed:

- `NULL` (no change): survives, 62 of 62 checks pass.
- `M1-no-cycle-write` (`_dhw_write`: `cycle = None`): killed by "a commanded or held disinfection cycle writes its temperature, not the configured set-point" and five more.
- `M2-round-nearest` (`_dhw_write`: drop `rounding="up"`): killed by "an off-step disinfection temperature is written on the step above it, never below".
- `M3-booking-ignored` (`_dhw_write`: `if inp.disinfecting`): killed by "a commanded or held disinfection cycle writes its temperature, not the configured set-point", "every row a cycle step can take writes the cycle's temperature, the idle and baseline rows too".
- `M4-hold-ignored` (`_dhw_write`: `if booked`): killed by "a commanded or held disinfection cycle writes its temperature, not the configured set-point" and four more.
- `M5-gate-only-excuse` (`dhw_gated`: restore `and written[0] < configured - SETPOINT_TOLERANCE`): killed by "the arbiter's own everyday write raises no disinfection-floor repair: it writes the cycle itself".
- `M6-excuse-any-reading` (`dhw_gated`: drop the `_differs` term): killed by "a person's value beside the arbiter's write still raises the repair, its Fix on the floor".
- `M7-flag-ignored` (`dhw_disinfection_temp`: ignore `legionella_cycle_active`): killed by "null control: a disabled cycle writes the everyday set-point on every row and booking".
- `M10-enabled-not-active` (`dhw_disinfection_temp`: the merge's resolution reverted to `dhw_legionella_enabled`): killed by "a combi store at or under the potable limit runs no cycle: a booked or held step writes the everyday set-point, unless the cycle is forced (#3398's predicate, read through the cycle's owner)".
- `M8-cycle-not-max` (`dhw_cycle_temp`: `return target`): killed by "a cycle never lowers the tank: an everyday set-point above the disinfection temperature is the cycle's and the ceiling's" (it survived the first cut: the arbiter's own everyday branch masked it; that check was added for it).
- `M9-floor-no-disinfection` (`_dhw_floor`: `return floor`): killed by "a person's value beside the arbiter's write still raises the repair, its Fix on the floor", "null control: with no arbiter write the pump's own set-point must still permit the cycle".

Failing first at main: `tests/block_duty.py` at the head copied over an origin/main cbd23f1c worktree fails 9 of 62 checks, both faces among them: "a commanded or held disinfection cycle writes its temperature, not the configured set-point" (the write) and "the arbiter's own everyday write raises no disinfection-floor repair: it writes the cycle itself" (the standing repair); every null-control check passes there.

## Null control

`dev/audit/harnesses/r10_disinfection_setpoint.py` (this PR) drives the production `desired` and `setpoint_check._dhw` over 5 rows x 4 bookings for six installs and prints one line each; run at origin/main cbd23f1c (the file copied over a main worktree; sha1 276cb8cf1d68e145cb169db474825d317319d5e0) and at 49a45dd8, then `diff <(grep '^null_' base) <(grep '^null_' head) && echo IDENTICAL` printed IDENTICAL over the 80 `null_*` lines: the cycle disabled, an everyday set-point at (60) and above (62) the disinfection temperature, and no hot-water set-point entity. Had the fix leaked into them the diff would print those lines. The 40 `stock`/`offstep` lines differ (36 lines changed): the defect's install, which is the fix. Each null control is also a check in `tests/block_duty.py` (four `null control:` checks), passing at main and at the head.

The `repair_none` column is the repair on an install whose arbiter has written nothing: unchanged on every non-cycle line (`stock none * repair_none=60` at both ends).

Precondition of the generalised exemption, stated rather than assumed: an arbiter writing an everyday set-point below `dhw_min_temp` would now be excused where main raised the repair; the options form refuses that pair (`config_flow.py` `_dhw_min_too_close`, minimum within 5 °C of the set-point), and the null-control installs carry `dhw_min_temp` 40.

## Figures

Taken at 49a45dd8 (production code as at the merge commit 340c426e; the later commits touch `tests/` and the seat instrument only), against origin/main cbd23f1c.

- Scoped gate: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED`; `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` ran every script `scope.run` names: all green except `tests/features.py` and `tests/structure.py`. `structure.py` was the unrecorded `class_excess_loc` gain, recorded in `1aa850c2` (`python3 tests/structure.py` then exit 0). `features.py` (`PYTHONPATH=tests/hastub python3 tests/features.py`): 1 of 5237 checks fails, "combi_type_branch census: ... no product or vendor name in the package's Python", which is origin/main's own red (see `## Red checks`). `tests/block_duty.py` 62 of 62 at the head. `tests/golden.py` green with no drift; no fixture claimed.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0023 IMPROVES`.
- Predicted reds: `python3 tools/pr/ci_predict.py` named two STALE PINs (deleted in `49a45dd8`); a re-run predicts no closures, fast, governance or instrument red and the 11 unpinned sites below.
- Harness: `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_disinfection_setpoint.py` at base and head, as under `## Null control`: 80 `null_*` lines IDENTICAL; 36 of the 40 `stock`/`offstep` lines changed (`diff ... | grep -c '^>'`).
- Class seams (`fixer.md` step 8). Rule: `git grep -nE "\.dhw_legionella_enabled|\.legionella_cycle_active|\.dhw_legionella_temp\b" -- custom_components` (every reader of the cycle's predicate or temperature) and `git grep -n '"dhw_setpoint"' -- custom_components/heatpump_optimizer/pump_arbiter.py` (every hot-water write of the arbiter). Dispositions:
  - `thermal_model.py` `legionella_cycle_active` (#3398's predicate) and `dhw_disinfection_temp`: the owner; this diff routes the predicate through it.
  - `pump_arbiter.py` `_dhw_write` (two `_bounded` calls): this diff; the gate row `DHW_GATE_C`: a gate by design, pinned on a cycle step; `dhw_gated`: this diff.
  - `dhw_planner.py` (legionella step placement on `legionella_cycle_active`, `ready_temps` max with the disinfection temperature): the plan's per-step requirement the cycle must meet, a floor below `dhw_cycle_temp` by construction; not the hold temperature. Already consistent.
  - `legionella.py` (the guard's credit target and watch flags, on `legionella_cycle_active`): the threshold a cycle must reach, at or below `dhw_cycle_temp` by construction; the arbiter rounds up so its write passes that test. Already consistent.
  - `coordinator.py` elastic-legionella deadline and the diagnostics echo (`dhw_legionella_cycle_active`): when a cycle is due and what is configured, not its temperature. Already consistent.

## Unpinned sites

Every site `python3 tools/pr/ci_predict.py` lists is under `custom_components/`, so each is pinned by `mutation-autofix`; the named mutants that already kill the same predicate are in brackets.

- custom_components/heatpump_optimizer/pump_arbiter.py:1105 CMP_BOUND: pinned by mutation-autofix (M1, M2)
- custom_components/heatpump_optimizer/pump_arbiter.py:1105 GUARD_OFF: pinned by mutation-autofix (M1, M2)
- custom_components/heatpump_optimizer/pump_arbiter.py:1107 RETURN_DEL: pinned by mutation-autofix (M1, M2)
- custom_components/heatpump_optimizer/pump_arbiter.py:1156 RETURN_DEL: pinned by mutation-autofix (M5, M6)
- custom_components/heatpump_optimizer/setpoint_check.py:120 CLAMP_DROP: pinned by mutation-autofix (M9)
- custom_components/heatpump_optimizer/setpoint_check.py:120 RETURN_DEL: pinned by mutation-autofix (M9)
- custom_components/heatpump_optimizer/thermal_model.py:893 CLAMP_DROP: pinned by mutation-autofix (M8)
- custom_components/heatpump_optimizer/thermal_model.py:893 RETURN_DEL: pinned by mutation-autofix (M8)
- custom_components/heatpump_optimizer/thermal_model.py:898 RETURN_DEL: pinned by mutation-autofix (M7, M10)
- custom_components/heatpump_optimizer/thermal_model.py:905 CLAMP_DROP: pinned by mutation-autofix (M8)
- custom_components/heatpump_optimizer/thermal_model.py:905 RETURN_DEL: pinned by mutation-autofix (M8)

## Red checks

- `mutation`: predicted, not yet run: the 11 sites under `## Unpinned sites` are added with no pin, which is the input `mutation-autofix` repairs by design (`ci-autofix.md`). The cheaper detector exists and ran: `tools/pr/ci_predict.py` (prepr.sh step 6d), locally, at no standing cost beyond the prepr run every seat already makes; no further countermeasure.
- `tests` (`tests/features.py`): predicted red, inherited from origin/main cbd23f1c: the "combi_type_branch census" vendor clause, `_CB_VENDOR` (`alpha.?innotec|mfs ?[0-9]|luxtronik`), matches six package lines (`const.py` two, `heat_curve.py` one, `pump_arbiter.py` two, `thermal_model.py` one, each a `Luxtronik` comment present at main, none in this diff's hunks) against `_CB_VENDOR_BASE = 4`; measured by the census in `PYTHONPATH=tests/hastub python3 tests/features.py` at this head and by the same regex over origin/main's package (6 at both). No commit of this branch turned it red, so no root-cause answer is this branch's; left untouched rather than loosen the base or edit other groups' comments.

## Forward-carry

none

## Friction

none
