Owner item: a flow set-point above the highest value the heat pump accepts. This pull request does two things.

1. **Clamp at the one write path.** Every set-point write is clamped to the range the target entity states when it is written. The clamp is in `inputs.write_setpoint`, the one service call every set-point write goes through. The range is a number's `min`/`max`, or `min_temp`/`max_temp` for a climate or water heater, read in the entity's own unit. The maximum is rounded down onto the entity's step and the minimum up. Before this, each caller bounded its own value. The arbiter's slots did (`SetpointGrid.bounded`), but the mixing-valve write (`coordinator._valve_write_problem`) and the DHW repair's write (`repairs.py`) did not.
2. **A manual high limit for the space water set-point** (owner ruling, 2026-11-22: "Flow cap: add an option to manually configure the high-limit if there is no such sensor"). A new optional option, `space_setpoint_high_limit_c`, sits on the entities page in the indoor group and is shown for a water set-point only. It takes 30–70 °C in 0.5 steps and has no default. Where an integration advertises a maximum above what the device takes, the clamp alone still writes the advertised maximum. The option lets an install without a maximum set-point sensor state the lower value.

The new pure module `flow_limit.py` is the one owner of how the sensor and the option combine (design `fa8cd134`, approved; verdict `a934ea3671`). The rules:

- Each source is judged alone first. The sensor arrives with the crossed-pair rule already applied (`_setpoint_limits_c`).
- A source below the lowest heating write is dropped and logged once (`log_held`). The lowest heating write is the gate plus its clearance, on the entity's step. A source equal to it is kept, which is `_feedback_bounds`' existing boundary (reviewer notes 7 and 8).
- Of the kept sources, the lower binds.

`pump_arbiter._space_limit_c` reads both sources, for a flow unit only, and passes the limit as `hi` to these consumers: the heating step, the fallback hold, the level map's top (`_map_inputs`, which also caps a boost), and the feedback loop's highs. These keep the advertised grid: the gate (`_gate_c`), the lowest heating write, the draw-range command (`_flow_command`, because a capped write does not command top draw), the adopted edit (`_adopt`) and `_arm_space`'s raw baseline. The device accepted the last two, because they are its own read-backs. Indoor-unit paths never read the option, because it is in water terms.

The minimum is honoured. Every arbiter space write is bounded at or above the 25 °C flow gate, which `_gate_c` raises to the entity's minimum, and the one write path now also lifts any caller's value to the entity's minimum.

Departures from the approved design, each measured:

- **I1 re-pinned for the high limit.** R10-WATER-SETPOINT-FEEDBACK's I1 held that the limit sensors act on the feedback loop alone, so an unmetered or switched-off loop wrote the same with them as without. The approved design moves the heating step and the hold under the high limit, and so does the owner ruling: no space water set-point above it is written. The two I1 checks now read the same for the indoor unit, for a step that does not heat, and for a limit at or below the gate. An install the loop does not act on writes the same up to the limit, holds a write there instead of going above it, and does not send the held value again. The low sensor still acts on the loop alone. At `01a105fa` the two old I1 checks failed, which is the null control for the re-pin: the cap moved those writes.

- **The "entity minimum wins" raise (design rule 5) is not built: it is unreachable.** `_gate_c` is bounded up to the entity's minimum, so the lowest heating write already sits above that minimum. A limit under the minimum is therefore under the lowest heating write too, and rule 4 drops it first. The check `an option under the entity's minimum ... is dropped and a boost writes the entity's maximum, never a value under the minimum` pins that. It covers a 40 minimum, and a 41 minimum on a 5-degree step, and in both the record equals what was sent.
- **No second grid accessor (`_space_grid`).** The limit is passed as `_bounded(..., hi=)`. The entity's minimum outranks a caller's `hi` in `SetpointGrid.bounded`, and its maximum stays among the ceilings. A redundant `limited=` path would only have bred equivalent mutants. The check `a limit above the entity's own maximum never lifts a heating write past it` pins that the maximum still binds: option 65 on a 60 maximum writes and records 60.
- **`_boost_ceiling_c` no longer caps by the limit itself.** `_map_inputs` takes `min(boost, limit)` for the level map's top, which is where a boost is written. A second cap in `_boost_ceiling_c` was an equivalent mutant (M7 below), so it was removed and the base's sensor cap moved to the map with it. The harness row `boost, entity max 65, high-limit sensor 62` still reads 62.

## Head

`facaa581e4bd8c3cac4d70fc27dc7f54ada6e828` (the fixer's `4411000a37` plus one commit that deletes the nine mutation-ledger pins whose lines this change replaced) measured against `origin/main` at `3a98735a7e` (merge base), 2026-11-22. Against `origin/main` `8ef450936a` at 2026-11-22T16:00Z, `git merge-tree --write-tree origin/main HEAD` merges cleanly; the `tests/closures.json` ledger merge driver resolves that file.

Overlap with #3812 (R11-SEAM-actuation-release, open at `3af986dd`): that pull request also moves `_silent_rows`/`_inside_silent` from `pump_arbiter.py` into `quiet_windows.py`, the move this pull request names as its structure payment below. Whichever merges second meets the other's move. If this one's structure check then fails on the main it lands on, it pays with another real move, never a budget raise.

The PR was opened by an opener seat from the fixer's branch tip. The fixer's local prepr was not run on this head; CI is the authority on the steps it would have run.

## Mutation proof

Clamp mutants, in `inputs.write_setpoint` / `inputs._own_range`. Each was run as `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py "# (C) Set-points are written on the entity's own step" "def _bst_q(value_c"` and restored with `git checkout`:

- M1, the maximum clamp off (`if False and high is not None:`). 4 of 7 checks failed, including `a set-point above the entity's maximum is sent as the maximum, below its minimum as the minimum` and `a production caller that bounds nothing itself, the mixing-valve write, ...`.
- M2, the minimum clamp off. 2 of 7 failed.
- M3, the maximum rounds `"nearest"`. 1 of 7 failed: `the range ends land on the step the entity accepts` sent 65 for a 63 maximum on a 5-degree step. The check first used a 62 maximum, where nearest and down agree, and M3 survived it. The case was changed to 63.
- M4, the minimum rounds `"nearest"`. 1 of 7 failed.
- M5, `_own_range` reads the number keys for every domain. 1 of 7 failed, because the climate's `max_temp` went unread.

Option mutants, in `flow_limit.py` / `pump_arbiter.py`. Each was run on the R11-OWNER-FLOWCAP block of `tests/features.py` (12 checks) through `features_block.py --prelude` and restored with `git checkout`:

- M1, the lower of the two becomes `max`. 3 failed: the pure precedence check, `a space boost writes the high limit ...` and `the feedback loop's ceiling is the high limit ...`.
- M2, the gate boundary becomes strict (a limit equal to lowest is dropped). 1 failed: the pure check's `sensor at lowest`.
- M3, a dropped source voids the other. 1 failed: the pure check.
- M4, the option's 30 °C floor is off. 1 failed: `the option reads only inside the 30-70 degC the options flow offers`.
- M5, the option's 70 °C ceiling is off. 1 failed: the same check.
- M6, an indoor unit reads the limit. 1 failed: `an indoor unit reads no high limit ...`.
- M7, the boost ignores the limit inside `_boost_ceiling_c`. **Survived**: an equivalent mutant, because `_map_inputs` already capped the boost. The cap was deleted from `_boost_ceiling_c`, so the mutant site no longer exists. M8 is the live site.
- M8, the level map's top ignores the limit. 4 failed at `01a105fa`, and 6 at the head after the M7 removal, including `a band-top heating step is held at an option under the 55 degC heating ceiling` and `a band-top write capped at the option is not read as commanding the pump's top draw`.
- M9, the fallback hold ignores the limit. 1 failed: `the fallback's hold stays under the limit`.
- M10, the feedback ceiling ignores the limit. 1 failed: `the feedback loop's ceiling is the high limit ...`.
- M11, the sensor read bypasses the crossed-pair rule. **Survived** at `01a105fa`: the crossed case had option 46 under the 52 sensor, where both answers are 46. The case was changed to option 58 with a crossed 52/60 pair (the answer is 58; the mutant writes 52), and M11 now fails 1 of 12.
- M12, the option is never read. 9 failed.

## Null control

- Clamp: the clamp block run with `inputs.py` at the merge base and `tests/features.py` at the head. The four range checks failed, and both null-control checks passed (an in-range value, and no range, a non-numeric bound or no state, each sent unchanged).
- Option: each option check carries its own control. With neither source, a boost writes the entity's maximum (70), the band top writes the 55 heating ceiling, the loop ceiling is 55, and the hold sits above 30. An option above the ceiling writes the ceiling. The same option on an indoor unit writes the same room value.
- Harness: the base column below.

## Figures

- Owner-case harness, `owner_flowcap_harness.py` sha1 `970cb958382fcbdb5b1b5a246ecf37e6257b85fc`. It is out of tree, in the seat's scratch directory, and goes to the reviewer with the handoff note. It drives the arbiter's real boost path through `tests/features.py`'s fixtures, plus `inputs.write_setpoint` and the valve write, on synthetic entities. Run from each worktree root as `PYTHONPATH=tests/hastub python3 owner_flowcap_harness.py .`.

  | case | base `3a98735a7e` | head `ea4b6dd401` |
  |---|---|---|
  | boost, entity max 65 | 65 | 65 |
  | boost, entity max 62 | 62 | 62 |
  | boost, entity max 65, high-limit sensor 62 | 62 | 62 |
  | boost, entity max 65, manual option 62 | 65 | 62 |
  | boost, entity max 65, no option (control) | 65 | 65 |
  | no boost, entity max 65 (control) | 42 | 42 |
  | `write_setpoint` 65 to max 62 | 65 | 62 |
  | `write_setpoint` 3 to min 5 | 3 | 5 |
  | valve write 65 to max 62 | 65 | 62 |
  | `write_setpoint` 45 to 5..62 (control) | 45 | 45 |

  The head commits after `ea4b6dd401` change no code path the harness drives: tests, docs, a docstring, and `config_flow.py`'s shared selector.

- Seam enumeration, the class "a temperature set-point service call". Rule: `git grep -n 'write_setpoint\b\|write_setpoint(\|write_setpoint_c(\|"set_value"\|"set_temperature"\|SETPOINT_SERVICES\[' -- custom_components/`.
  - `pump_arbiter._write`: bounded per slot, and now also clamped at the call.
  - The `pump_arbiter` off-restore `Restorer`: bounded at adoption, and now clamped.
  - `coordinator._valve_write_problem`: was unbounded; closed here and pinned by the valve check.
  - `heat_curve.write_displace` and its `Restorer`: `offset_target` saturates the value, and the call now clamps too.
  - `repairs.py`'s DHW fix: was unbounded; closed by the same call, with no dedicated repair-flow check.
  - `coordinator._command_frequency` `"set_value"`: a frequency, already `np.clip`ped to `hz_min`/`hz_max`.
  - The GCHV night-slot `"set_value"`: hour and minute integers, outside the class.
  - `services.py`'s `write_setpoint` flag and `boost.py`'s `action["setpoint"]`: they write nothing.
- Seam enumeration, the class "a space water set-point value the arbiter computes" (the option's consumers): `git grep -n '"space_setpoint"' -- custom_components/heatpump_optimizer/pump_arbiter.py`. The behaviour section above names each consumer with the grid it reads.
- Structure payment. `pump_arbiter.py` goes from 2360 to 2346 lines, paid by moving `_silent_rows`/`_inside_silent` into `quiet_windows.py` as `silent_rows`/`inside_silent`, the module that owns the quiet-window grammar, plus dropping three unused imports. `config_flow.py` goes from 4200 to 4201 lines. The new row and its imports were paid by deleting a spent paragraph in `_number`'s docstring, which brought the file to 4198. The flow ceiling and the high limit then share one selector, `_WATER_LIMIT_C` (3 lines), because `archscore` read the two identical `_number(...)` specs as a literal clone (`literal_clone_copies` 114 -> 116, WORSENS). With the shared selector the score is NULL. That last line is paid inside `module_excess_loc` by `pump_arbiter.py`'s move. The `_valid_months_spec` move, which R11-OWNER-MODE-LEGS uses, is not used here. `flow_limit.py` (56 lines) is new and imports only `const`. It is classified into the 22 closures in `tests/closures.json` that hold `pump_arbiter.py`. The two mutation-ledger pins for `_silent_rows` moved with their code. The two `_inside_silent` pins lost their anchor line and are left to mutation-autofix.
- Structure ratchet: `python3 tests/structure.py` reported `module_excess_loc` 21779 -> 21766, which is recorded with `--record` in its own commit, naming the rows that moved. Every other metric is flat.
- Architecture score: `python3 tools/audit/archscore/score.py --diff 3a98735a7e` gives `Architecture score: dS +0.0000 NULL`.
- Scoped gate: `python3 tests/closure.py select --base $(git merge-base origin/main HEAD)`; its mode line is in the registered block below. Run locally:
  - `tests/features.py` at `01a105fa`: 2 of 6045 failed, both R10-WATER-SETPOINT-FEEDBACK part 3 I1 checks, which are re-pinned below. At the head, the R10-WATER-SETPOINT-FEEDBACK block passes 25 of 25, the FLOWCAP block 12 of 12 and the clamp block 7 of 7.
  - `tests/doc_claims.py`: `docs/architecture.md`'s module census was raised to 99 and 64, and `flow_limit.py` added to its tree. `write_setpoint`'s docstring was split under the comment ratchet's 40 words.
  - The FLOWCAP block and the clamp block at the head: all pass.
  - `tests/config_flow_steps.py` at the head: 612 checks passed.
  - `tests/entities.py`: not finished on this host after two hours under `nice`; left to CI.
  - The rest of `scope.run` is left to CI, because the host is heavily loaded.

<!-- figure-block: scope-line mb=3a98735a7ecc59e7ecc095a0429cdf6251d956ec head=facaa581e4bd8c3cac4d70fc27dc7f54ada6e828 -->
~~~text
MODE: SCOPED -- 30 script(s) run, 3 scoped out.
~~~
<!-- /figure-block -->

## Unpinned sites

- custom_components/heatpump_optimizer/flow_limit.py:32 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/flow_limit.py:32 CMP_BOUND*2: pinned by mutation-autofix
- custom_components/heatpump_optimizer/flow_limit.py:32 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/flow_limit.py:52 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/flow_limit.py:52 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/flow_limit.py:52 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/flow_limit.py:54 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/flow_limit.py:56 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/inputs.py:576 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/inputs.py:584 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/inputs.py:742 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/inputs.py:743 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/inputs.py:744 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/inputs.py:745 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:623 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:632 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:936 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:990 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1011 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1115 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1115 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1123 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1237 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1244 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/quiet_windows.py:183 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/quiet_windows.py:183 RETURN_DEL: pinned by mutation-autofix

## Red checks

- `mutation` at facaa581e4bd: red by construction on the 26 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push.

## Forward-carry

- The entity-range clamp in `inputs.write_setpoint` is owned here, and R11-SEAM-actuation-writes (design `28bedac8`, section "Grid and range") consumes it instead of adding its own. That note's amendment is the orchestrator's, by its own ruling. Carry: R11-SEAM-actuation-writes.
- A root cause is owed under `defect-root-cause.md`, because the defect reached a released version (v10.1.2). The named cause is an integration-advertised maximum above the device's accepted one, written by a boost that drives the entity to its maximum. Carry: dismissed: the orchestrator dispatches the root-cause seat, and a fixer may not run it (`root-cause.md`).
- The two `_inside_silent` killed-by pins were deleted with their anchor. Carry: dismissed: CI mutation-autofix re-pins killed mutants (`ci-autofix.md`).

## Friction

none
