Adopts outside pull request 3356 (contributor Bankaifan, fork branch `feat/water-setpoint-lift-ceiling`, fork head e9dc72be09b9fc16fdde3508b1816ca5b4f5c9d5): with Pump duty control at Control and a water space set-point, the modulation floor's lift over the measured inlet (`flow_min_lift_k`, else `thermal_model.FLOW_MIN_LIFT_K`) and the full-power ceiling (`flow_heat_c`, read by the arbiter since #1955 but not offered) become options on the Sensors and entities page, shown for a water unit; `space_setpoint_unit` gains `return`, a controller taking the number as its return-water target. For a return target the hold, the weather curve and the gate move down by `pump_arbiter.RETURN_SUPPLY_OFFSET_K` (`_as_target`, `_gate_floor_c`), the valve outlet is skipped as the lift's anchor (`RETURN_SKIPPED_RUNG`), and `_full_draw_c` withholds the full-draw set-point from `draw_range` while the return-side inlet has less than `FLOW_MIN_LIFT_K` of headroom under the ceiling. The contributor's four commits are kept with their authorship, except one: the fork's c73b0e015 ("tests: review checks for the return set-point unit") was authored by the assistant identity the contributor ran, which `ref_privacy` refuses to publish, so it is re-authored to the contributor's own identity from the adjacent commit of the same fork session (Bankaifan <bankaifan@users.noreply.github.com>); their assistant-session trailers were dropped from the messages, and the contributor is credited by the Co-authored-by trailer below. The fork's `tests/golden/claimed_drift.txt` hunk, which restated the R10-MIN-POWER-FLOOR line under claims-for 7.1.7 that the 7.1.8 stamp emptied, is dropped; one added commit writes this branch's own config_flow claim, a default-options null-control grid, and makes `_or_hold`'s config argument required. No issue: the build is the outside-intake adoption, roster group R10-WATER-SETPOINT-LIFT.

Close 3356 with thanks once this merges. Plan page link for the outside-intake ruling (tvofi 2026-11-06): owed on 3356 by the orchestrator. After: R10-GENERIC-HEAT-CURVE (#3299), open at this head; if it merges first with its own config_flow claim, the combined claim line is restated on this branch (claim-files.md).

Co-authored-by: Daniel <476059+Bankaifan@users.noreply.github.com>

## Independent review of the fork (fix-review.md, detached at the fork head, rebased onto main)

Sound, adopted. Judged on the added production lines (238 added, 39 deleted under `custom_components/`, `git diff --numstat origin/main HEAD -- custom_components`):

- One owner per concept: `const.SPACE_SETPOINT_WATER_UNITS` is the one definition of "a water set-point", read by `pump_arbiter._flow_unit`, `thermal_model.flow_setpoint_driven` and `config_flow._water_space_setpoint`; the supply-to-target shift lives in `pump_arbiter._as_target` alone; the lift's read in `thermal_model.configured_flow_min_lift_k`, beside `configured_flow_heat_c`. No `homeassistant` import added below the glue; `entry.options` is read only through the config mapping the arbiter is handed.
- Missing or invalid input refuses rather than guesses: a non-positive, non-finite or non-numeric lift reads as the rated lift; a return target with no return-side reading anchors nothing and takes the no-inlet hold.
- **Full-draw withholding — kept as the fork encodes it, the finite value `ceiling + FLOW_MIN_LIFT_K` in `FlowCommand.ceiling_c`, not an explicit representation.** Every reader is in `draw_range.py` and reads the pair as `written_c >= ceiling_c - CEILING_TOLERANCE_K` (`takes_ceiling`, `_overdrawn`, `_evidence`); the stored rows persist `(written_c, ceiling_c)` and `_command_cells` re-reads them only when both are finite. The explicit alternatives each lose: `None` already means "nothing commanded the draw" and `_evidence` reads it as **full** (`cmd is None or ...`), the opposite of what is meant; `math.inf` compares right live but `_command_cells` drops a non-finite row to `None` on reload, so a restart turns every withheld sample into a full one; a separate `full_draw` field on `FlowCommand` changes all three predicates and the stored-row schema with its back-compat read, which is widening into `draw_range`'s seam. The finite value persists and reloads with the meaning it was written with, and is unreachable by any write: `_flow_target` caps every heating write at the ceiling (`hi=heat_c`) and the gap, `FLOW_MIN_LIFT_K`, exceeds `CEILING_TOLERANCE_K` plus one entity step. Cost of the choice: a return target's stored row holds `ceiling + 5` rather than the configured ceiling while withheld, which a diagnostics reader of the raw rows sees.
- **Silent behaviour change, named:** `pump_arbiter._heat_ceiling_c` reads a stored `flow_heat_c` at or below `FLOW_GATE_C` (25 °C) as `FLOW_HEAT_C` (55 °C) at all three arbiter sites. On main such a value made every heating step write the gate, i.e. off; at this head it heats to 55 °C. The options flow offers 30–70 °C, so only a hand-edited entry reaches it; `docs/configuration.md` states it.
- `configured_flow_heat_c` now reads an absent key as `const.DEFAULT_FLOW_HEAT_C` and keeps `default` only for an unreadable value; every caller passes `pump_arbiter.FLOW_HEAT_C`, the same 55.0, so no caller's result moves (the null-control grid below runs the absent case).
- Assumptions the code labels as assumptions, not measured: `RETURN_SUPPLY_OFFSET_K` (the W35 30/35 °C rating spread) and the 5 K full-draw headroom. The fork's evidence (one install's recorder, a firmware decompilation not in the tree) was read as data; no figure from it is restated here as a measurement.

## Head

ec2d173c7a4835d646eddca4367559f16f5c9dde, branch `handoff/r10-water-setpoint-lift`, cut from origin/main ba6fd7e8b0b0502dfcce26df781810e474fc1d2f (measured 2026-11-09). Re-authored again at open (orchestrator, 2026-11-09): the contributor's three commits carried the unnumbered noreply `bankaifan@users.noreply.github.com`, which `ref_privacy.py guard` refuses as `unnumbered-email`; they now carry the contributor's numbered noreply `476059+Bankaifan@users.noreply.github.com` (the address their own c3ac6099 already used), each of the five trees byte-identical to its predecessor at ee9138f1 (`git rev-parse <c>^{tree}` compared commit for commit). Every measurement below ran at 8fb1858d75fc, whose tree is this head's tree byte for byte (`git rev-parse HEAD^{tree}` equal before and after): the re-authoring above rewrote one author field and the SHAs after it, no file. origin/main has since moved to 79b7356f3 without a conflict (`git merge-tree --write-tree origin/main HEAD` exit 0); R10-GENERIC-HEAT-CURVE (#3299) is not among the new commits.

## Mutation proof

Each mutant applied alone to a worktree at 8fb1858d75fc, then `PYTHONPATH=tests/hastub python3 tests/features.py`:

- Failing test first: this head's `tests/` against origin/main's `custom_components/` (`git checkout origin/main -- custom_components`): `ImportError: cannot import name 'CONF_FLOW_MIN_LIFT_K' from 'heatpump_optimizer.const'`, rc=1 — the return-unit block imports production symbols main does not have.
- `_as_target`'s return branch deleted (`return supply_c`): `10 of 5011 FEATURE CHECKS FAILED` — with no inlet reading a return target's floor is the rated hold in return terms; the baseline hold of a return target is the curve or rated hold less the rated spread; null control: the supply-to-target conversion moves nothing but a return target; a return target with headroom publishes the held command in the entity's own terms; a return target's non-heating duties write the gate in return terms; a 1.5 K lift over a 22 degC return takes the lift from the return; a return below the return gate takes the lift from that gate; the hold moves by the rated spread, not by the configured lift; D5; D6.
- `_full_draw_c`'s withholding deleted (`return ceiling_c`): `2 of 5011 FEATURE CHECKS FAILED` — a return target's ceiling is a max-draw set-point only with the rated lift of headroom; draw_range folds a ceiling write on a return target as ceiling-probe evidence and as a full sample only with headroom.
- Null-control detector: `_return_unit` widened to every water unit (a flow target treated as a return one): `20 of 5011 FEATURE CHECKS FAILED`, among them `null control: with default options every set-point an indoor or flow unit writes, and every held FlowCommand, is main's, cell for cell` (`2688 cells, moved at [1344, 1347, ...]`, the first flow cell onward), and the pre-existing flow-path checks (on the real curve a space-heating step writes the level's flow; the baseline holds the rated 35 degC flow; a flow set-point never goes below 25 °C).

The `_as_target` mutant leaves the grid green, as it should: it changes only a return target.

## Null control

Unmutated head: `ALL 5011 FEATURE CHECKS PASSED` (`PYTHONPATH=tests/hastub python3 tests/features.py`). The default-options grid, pinned in `tests/features.py` as `_NC_AT_MAIN`: `_nc_cells()` drives the production `pump_arbiter.desired` for the baseline and each duty, and `_flow_command`, through a real coordinator, for unit indoor and flow × four inlet-rung sets (none, pump return, valve outlet, both) × inlets 18/27/52/60 °C × plan levels 0/1.5/3.5/6 kW × weather curve absent/30/42/61 °C: 2688 cells. Recorded by the same block on origin/main's production tree and on this head: byte-identical (`cmp`). Flat-price null control: not applicable (no cost figure).

## Figures

- `PYTHONPATH=tests/hastub python3 tests/features.py` at 8fb1858d75fc: `ALL 5011 FEATURE CHECKS PASSED`; mutant counts under `## Mutation proof`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, no budget re-recorded.
- `python3 tools/audit/archscore/score.py --diff origin/main HEAD`: `Architecture score: dS +0.0000 NULL`.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round3/D5/option_doc_coverage.py`: `option_fields_undocumented=0` and `option_fields_rendered=205` at both origin/main and this head; the rendered count does not move because the harness seeds no water unit, so the two new fields do not render (control: they render in `tests/features.py`'s "the entities page offers the lift and ceiling only for a water unit" check). Re-measure after R10-GENERIC-HEAT-CURVE merges.
- `git diff --numstat origin/main HEAD -- tests/golden/config_flow.json`: 2 insertions, 2 deletions, the claim's footprint.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED`; `bash tools/pr/prepr.sh` at 8fb1858d75fc: `PRE-PR ... rc=0` (closures: scoped recordings covered, `tests/harness_headers.py` and `tests/stress.py` left to CI; ci predict: no closures, fast, governance or instrument red predicted; merged structure passed).

## Architecture score

n/a: `dS +0.0000 NULL`, no gate metric rises.

## Unpinned sites

none: `tools/pr/prepr.sh`'s ci predict step lists no `ADDED UNPINNED` mutation site at this head. The fork's killed_by pins (anchored by content hash, not line) re-resolve after the rebase; the `_or_hold` signature edit moves no pinned anchor (same step).

## Red checks

none

## Forward-carry

Three proposals from the fork, routed to the orchestrator as the brief directs; none is measured here and none is implemented. Destination file: `dev/programme/carries/carry-201.json`, the orchestrator's to write or dismiss; this seat writes no programme record, so it is not written by this branch. Carry: #201

- The fork's proposal: a start-then-hold write sequence for a return target, since a controller that starts only once the target sits its hysteresis above the return is not started by a small lift. Unmeasured here; implemented nowhere. Carry: #201
- The fork's proposal: the 5 K full-draw headroom in `_full_draw_c` measured against a steady-state series rather than taken from the rated lift. Unmeasured here. Carry: #201
- The fork's proposal: the modulation floor anchored once per plan step rather than re-read every pass. Unmeasured here. Carry: #201

## Friction

none
