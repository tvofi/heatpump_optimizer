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
- **`_boost_ceiling_c` no longer caps by the limit itself.** `_map_inputs` is its only caller, and it takes `min(boost, limit)` for the level map's top, which is where a boost is written. A second cap in `_boost_ceiling_c` was an equivalent mutant (M7 below), so it is deleted at `6d54e9bd1d`, with the docstring clause that named it. The base's sensor cap moved to the map with it. A correction to the record: earlier bodies said the cap was removed in `ea4b6dd401`, but that commit changed only `tests/features.py`, and the two lines stayed in the tree until `6d54e9bd1d`. The fix review at `19eafc0fb1` found it (verdict `e18f2b1cf2`). The base's sensor cap is still pinned: the R10-HOTFIX-BOOST-FLOW-CEILING row `max 60, limit 52` writes 52 at the head, and M8 kills it.

## Head

`a6dd172693260908df97777553b7e6001c828f95` merges the PR head `7fb673f398` (`ci: pin killed mutants`, mutation-autofix's 14 pins at `19eafc0fb1`) into `b4a84ed9f1`. Three of those pins were add/add conflicts with the same anchors that #3812 put on main: `_silent_target` GUARD_OFF 32150d03, `_silent_target` RETURN_DEL 1d15c126 and `inside_silent` RETURN_DEL 21e6a29d. `killed_by` holds one driver, so the two sides cannot be unioned in one file. Main's file is kept for each, byte-identical to `origin/main`'s, so this diff carries none of the three. Each of the other 11 pins anchors a line that `grep -cxF` finds exactly once at this head. `python3 tests/mutation_table.py --normalize` leaves `git diff` empty, and `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. The merge changes no production line, so the block and mutant figures below, taken at `b4a84ed9f1`, hold here.

`b4a84ed9f1feb804cf85190bab2fc00add9f4f2d` adds one commit to the merge `010e0088d5`, the structure payment that #3812's merge left owed (Figures). The commit does two things:

- It deletes the narration of replaced implementations from five `pump_arbiter.py` docstrings: `step_duty`, `_arm_space`, `_lead_mode`, `on_off_service` and `_level_kw`. Each keeps its rule and its finding ID. This is 16 lines.
- It corrects `docs/architecture.md`'s count of modules free of Home Assistant to 65, and restores `tests/structure_budgets.json` to `origin/main`'s.

`010e0088d559513329ec14c3901ab9463ab1e9ca` merges `origin/main` `af4d89f763` (2026-11-23) into `8c2c57a37f`. Before it, `git merge-tree --write-tree origin/main HEAD` reported conflicts, and so did the PR head `566727d1db`, because #3812 had merged and made this PR's own `_silent_rows`/`_inside_silent` move. The resolution:

- `quiet_windows.py` and its three mutation-ledger pins (`_silent_target` GUARD_OFF/RETURN_DEL, `inside_silent` RETURN_DEL) are taken from main.
- `pump_arbiter.py` imports both `duty_ledger` and `flow_limit`.
- The module census is 102, main's 101 plus `flow_limit.py`, in `docs/architecture.md` and the D6 claims header. `claims.json`/`claims.md` were regenerated by `python3 dev/audit/rounds/round4/D6/claims.py`, which prints `arch_modules_on_disk=102` and `arch_map_listed=102`.
- `tests/deployment_shape.py`'s package count is 121, and `git ls-files custom_components/heatpump_optimizer/ | wc -l` prints 121.

`8c2c57a37f6611382057f234a98b2b8f5e973e8f` records `module_excess_loc` 21766 -> 21764 in `tests/structure_budgets.json`, on `6d54e9bd1dfe86891ede65fa4812bee974038eda`. That record is superseded by the merge (Figures). `6d54e9bd1d` adds one commit to `566727d1db`. That commit deletes the two-line `_space_limit_c` cap from `pump_arbiter._boost_ceiling_c`, along with its docstring clause, and changes no other line. The fix review at `19eafc0fb1`, whose tree equals `566727d1db`'s, blocked on that cap. The mutation proof below was taken at `6d54e9bd1d` and taken again at the merge `010e0088d5`, with identical figures.

`566727d1db0f460811b6f729f3473e56773bf2b9` adds one commit to `f36611dd23`, repairing its two `tests / fast (3.14)` reds: it splits one comment sentence in `tests/features.py` and re-records `dev/audit/rounds/round4/D6/claims.py`'s module census header with its regenerated `claims.json`/`claims.md`. It changes no production line. Measured against `origin/main` `e3cb5c019b` at 2026-11-22T21:01Z: `git merge-tree --write-tree origin/main HEAD` merges cleanly.

`f36611dd23542a73d141963c1eb7860f8a219edb` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/3866.md`. The authored code head is `0d1cae21a695abbc4c951143b854d2a2a45e16b6`.

`c6d5d822e3067cc7df2345d7ddffc4cf593f3cd0` merges origin/main `8cc3fb3e35` into the authored code head `0d1cae21a695abbc4c951143b854d2a2a45e16b6` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

`0d1cae21a695abbc4c951143b854d2a2a45e16b6` (the fixer's `4411000a37`, then `facaa581e4` which deletes the nine mutation-ledger pins whose lines this change replaced, then `0d1cae21a6` which counts flow_limit.py in the deployment-shape lane's note) measured against `origin/main` at `3a98735a7e` (merge base), 2026-11-22. Against `origin/main` `8ef450936a` at 2026-11-22T16:00Z, `git merge-tree --write-tree origin/main HEAD` merges cleanly; the `tests/closures.json` ledger merge driver resolves that file.

Overlap with #3812 (R11-SEAM-actuation-release): it merged first, with the same `_silent_rows`/`_inside_silent` move, so the move is main's and no longer this PR's payment. The merge `010e0088d5` takes main's side of the move. `b4a84ed9f1` pays the lines instead, as committed here before the merge, with no budget raise (Figures).

The PR was opened by an opener seat from the fixer's branch tip. The fixer's local prepr was not run on this head; CI is the authority on the steps it would have run.

## Mutation proof

Clamp mutants, in `inputs.write_setpoint` / `inputs._own_range`. Each was run as `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py "# (C) Set-points are written on the entity's own step" "def _bst_q(value_c"` and restored with `git checkout`:

- M1, the maximum clamp off (`if False and high is not None:`). 4 of 7 checks failed, including `a set-point above the entity's maximum is sent as the maximum, below its minimum as the minimum` and `a production caller that bounds nothing itself, the mixing-valve write, ...`.
- M2, the minimum clamp off. 2 of 7 failed.
- M3, the maximum rounds `"nearest"`. 1 of 7 failed: `the range ends land on the step the entity accepts` sent 65 for a 63 maximum on a 5-degree step. The check first used a 62 maximum, where nearest and down agree, and M3 survived it. The case was changed to 63.
- M4, the minimum rounds `"nearest"`. 1 of 7 failed.
- M5, `_own_range` reads the number keys for every domain. 1 of 7 failed, because the climate's `max_temp` went unread.

Option mutants, in `flow_limit.py` / `pump_arbiter.py`, re-taken at `6d54e9bd1d`. Each was run on the R11-OWNER-FLOWCAP block of `tests/features.py`, 12 checks from `# R11-OWNER-FLOWCAP (tvofi, 2026-11-22` to `_pa_bl_fb, _ = _pa_boost_level`. The runner was `features_block.py --prelude`, with the prelude from `--emit-prelude`, and each mutant was applied textually and restored after the run. At the head the block passes 12 of 12. The clamp mutants were re-run the same way at this head, and their figures above are unchanged:

- M1, the lower of the two becomes `max`. 3 failed: the pure precedence check, `a space boost writes the high limit ...` and `the feedback loop's ceiling is the high limit ...`.
- M2, the gate boundary becomes strict (a limit equal to lowest is dropped). 1 failed: the pure check's `sensor at lowest`.
- M3, a dropped source voids the other. 1 failed: the pure check.
- M4, the option's 30 °C floor is off. 1 failed: `the option reads only inside the 30-70 degC the options flow offers`.
- M5, the option's 70 °C ceiling is off. 1 failed: the same check.
- M6, an indoor unit reads the limit. 1 failed: `an indoor unit reads no high limit ...`.
- M7, the boost ignores the limit inside `_boost_ceiling_c` (GUARD_OFF). At `19eafc0fb1` it **survived**, 12 of 12 passing. It is equivalent by construction: the only caller, `_map_inputs`, takes `min(boost_c, _space_limit_c(inp) or inf)`, and `min(min(caps + [L]), L) == min(min(caps), L)`. At `6d54e9bd1d` the cap is deleted, and the mutant's anchor occurs 0 times in `pump_arbiter.py`. M8 is the live site.
- M8, the level map's top ignores the limit. At `6d54e9bd1d` it fails 6 of 12, including `a band-top heating step is held at an option under the 55 degC heating ceiling` and `a band-top write capped at the option is not read as commanding the pump's top draw`. At `19eafc0fb1`, where the M7 cap still stood, it failed 4 of 12 (the fix review's measurement), and the earlier body's "6 at the head" was measured against the wrong tree. M8 also fails 1 of the 3 R10-HOTFIX-BOOST-FLOW-CEILING checks (the `max 60, limit 52` sensor row), and 2 of the 54 R10-WATER-SETPOINT-FEEDBACK checks, both part 3 I1. That block runs from `# --- R10-WATER-SETPOINT-FEEDBACK (outside report #3380` to `# R10-OUTSIDE-LEARNER-ROBUSTNESS-P3`, and both blocks pass in full at the head.
- M9, the fallback hold ignores the limit. 1 failed: `the fallback's hold stays under the limit`.
- M10, the feedback ceiling ignores the limit. 1 failed: `the feedback loop's ceiling is the high limit ...`.
- M11, the sensor read bypasses the crossed-pair rule. **Survived** at `01a105fa`: the crossed case had option 46 under the 52 sensor, where both answers are 46. The case was changed to option 58 with a crossed 52/60 pair (the answer is 58; the mutant writes 52), and M11 now fails 1 of 12.
- M12, the option is never read. 10 of 12 failed at `6d54e9bd1d`. The fix review measured the same 10 at `19eafc0fb1`; the earlier body's 9 was wrong.
- M1-M6 and M9-M11 were re-run at `6d54e9bd1d`, and each figure above is unchanged.

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

  The head commits after `ea4b6dd401` and before `6d54e9bd1d` change no code path the harness drives: tests, docs, a docstring, and `config_flow.py`'s shared selector. `6d54e9bd1d` deletes the boost cap. The harness was not re-run there, because it is not on the repair seat's host: `find` under `$HOME` and `/private/tmp` for `owner_flowcap_harness*` printed nothing. The in-tree checks carry its boost rows at `6d54e9bd1d` instead. The FLOWCAP block's `a space boost writes the high limit ...` covers the manual option and the sensor-plus-option rows, and R10-HOTFIX-BOOST-FLOW-CEILING's `max 60, limit 52` covers the sensor-only row. Both pass, and M8 (the map's cap removed) fails both, which is the null control.

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
- Structure payment. `pump_arbiter.py` goes from 2360 to 2346 lines (2344 at `6d54e9bd1d`, `wc -l`, after the M7 cap's deletion), paid by moving `_silent_rows`/`_inside_silent` into `quiet_windows.py` as `silent_rows`/`inside_silent`, the module that owns the quiet-window grammar, plus dropping three unused imports. `config_flow.py` goes from 4200 to 4201 lines. The new row and its imports were paid by deleting a spent paragraph in `_number`'s docstring, which brought the file to 4198. The flow ceiling and the high limit then share one selector, `_WATER_LIMIT_C` (3 lines), because `archscore` read the two identical `_number(...)` specs as a literal clone (`literal_clone_copies` 114 -> 116, WORSENS). With the shared selector the score is NULL. That last line is paid inside `module_excess_loc` by `pump_arbiter.py`'s move. The `_valid_months_spec` move, which R11-OWNER-MODE-LEGS uses, is not used here. `flow_limit.py` (56 lines) is new and imports only `const`. It is classified into the 22 closures in `tests/closures.json` that hold `pump_arbiter.py`. The two mutation-ledger pins for `_silent_rows` moved with their code. The two `_inside_silent` pins lost their anchor line and are left to mutation-autofix.
- Structure ratchet: `python3 tests/structure.py` reported `module_excess_loc` 21779 -> 21766, which is recorded with `--record` in its own commit, naming the rows that moved. Every other metric is flat. At `6d54e9bd1d`, after the M7 cap left `pump_arbiter.py`, `python3 tests/structure.py` printed `gain module_excess_loc 21764 (budget 21766, -2; not yet recorded)`. That was recorded with `--record` in its own commit (`recorded_at` to the merge base `8cc3fb3e35`), and every other metric stayed flat.
- Structure after #3812 (supersedes the two bullets above for the final state). #3812 merged the same `_silent_rows`/`_inside_silent` move, so that move pays nothing here. At the merge `010e0088d5`, `python3 tests/structure.py` printed `FAIL module_excess_loc 21791 > 21760 (+31)`:
  - The 21760 is the `tests/structure_budgets.json` ledger merge driver summing both branches' copies of the one move (`21779 + both deltas`).
  - `origin/main` records 21775.
  - The PR's own growth against main is +16 lines past the module limit: `pump_arbiter.py` 2367 -> 2382 and `config_flow.py` 4200 -> 4201 (`wc -l`, main against the merge).
  - `b4a84ed9f1` pays those 16 lines, so `pump_arbiter.py` is 2366, and it restores `tests/structure_budgets.json` byte-identical to `origin/main`'s (`git diff --quiet origin/main -- tests/structure_budgets.json`). `python3 tests/structure.py` then prints `ok   module_excess_loc 21775 <= 21775` and `STRUCTURE RATCHET PASSED`.
  - No budget row moves against main.
  - archscore was not re-run for `b4a84ed9f1`, because the commit changes docstrings and one number in a doc, and no code.
- Architecture score: `python3 tools/audit/archscore/score.py --diff 3a98735a7e` gives `Architecture score: dS +0.0000 NULL`.
- Scoped gate: `python3 tests/closure.py select --base $(git merge-base origin/main HEAD)`; its mode line is in the registered block below. Run locally:
  - `tests/features.py` at `01a105fa`: 2 of 6045 failed, both R10-WATER-SETPOINT-FEEDBACK part 3 I1 checks, which are re-pinned below. At the head, the R10-WATER-SETPOINT-FEEDBACK block passes 25 of 25, the FLOWCAP block 12 of 12 and the clamp block 7 of 7.
  - `tests/doc_claims.py`: `docs/architecture.md`'s module census was raised to 99 and 64, and `flow_limit.py` added to its tree. `write_setpoint`'s docstring was split under the comment ratchet's 40 words.
  - The FLOWCAP block and the clamp block at the head: all pass.
  - `tests/config_flow_steps.py` at the head: 612 checks passed.
  - `tests/entities.py`: not finished on this host after two hours under `nice`; left to CI.
  - The rest of `scope.run` is left to CI, because the host is heavily loaded.


- Repair of `tests / fast (3.14)` at `566727d1db`:
  - `python3 tests/doc_claims.py`: at `f36611dd23` 1 of 441 failed (`REFUSE tests/features.py: long units 465 -> 466`); at the head `ALL 441 checks PASSED`. The sentence is split, the ratchet is not raised.
  - `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: at `f36611dd23` 3 of 115 failed (`arch_modules_on_disk` and `arch_map_listed` header 98, printed 99; `claims.json`, `claims.md` left modified). At the head: `ALL 115 HARNESS HEADER CHECKS PASSED`, and `git status --short` after the run printed nothing.
  - `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - `PREPR_SKIP_CLOSURES=1 PREPR_SKIP_CODE=1 bash tools/pr/prepr.sh` at `566727d1db`. Code steps are skipped because the delta since `f36611dd23` is one comment and the D6 harness outputs, with no production line. CI ran the scoped scripts at `f36611dd23` (run 45055462774), and `tests / fast (3.14)` failed only on the two checks repaired here. A first run without `PREPR_SKIP_CODE` was stopped at the 30-minute background limit inside the code steps, so it gave no verdict on them.
- Repair of the fix review's block at `6d54e9bd1d` / `8c2c57a37f`:
  - Scope: `python3 tests/closure.py select --diff 566727d1db` prints `MODE: SCOPED -- 22 script(s) run, 11 scoped out` for the one changed file, `pump_arbiter.py`.
  - Run locally (`PYTHONPATH=tests/hastub`):
    - `tests/doc_claims.py`: `ALL 441 checks PASSED`. The docstring edit passes the comment ratchet.
    - `tests/guard_pins.py`: `ALL 91 GUARD PIN CHECKS PASSED`.
    - `tests/finite_boundary.py`: `ALL 119 FINITE BOUNDARY CHECKS PASSED`.
    - The `tests/features.py` blocks the deleted cap reaches: FLOWCAP 12/12, clamp 7/7, R10-HOTFIX-BOOST-FLOW-CEILING 3/3, R10-WATER-SETPOINT-FEEDBACK 54/54. The full `features.py` was left to CI.
  - Red on this host, from the host and not the delta:
    - `tests/typing_ruler.py` fails `mypy is pinned at 2.4.1  [found 2.3.1]`. That is the host venv's mypy version, and the delta changes no annotation.
    - `tests/harness_headers.py` fails 12 of 115, all on `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py`: `rc=124 cpu=116.9s stderr=wall limit 900s exceeded`. The harness never reads `_boost_ceiling_c`. It used 117 s of CPU in 900 s of wall clock on the loaded host. The same script passed 115 of 115 at `566727d1db` (above).
  - Both scripts are left to CI.
  - The rest of `scope.run` is also left to CI.
- Re-executed after the merge (`fixer.md` step 6):
  - Scope: `python3 tests/closure.py select --diff af4d89f763` prints `MODE: SCOPED -- 30 script(s) run, 3 scoped out`.
  - At `010e0088d5`:
    - FLOWCAP 12/12, clamp 7/7, R10-HOTFIX-BOOST-FLOW-CEILING 3/3, R10-WATER-SETPOINT-FEEDBACK 54/54.
    - Every option and clamp mutant fails the same checks as at `6d54e9bd1d`. M7's anchor occurs 0 times.
    - `tests/guard_pins.py` 91/91, `tests/finite_boundary.py` 119/119, `tests/deployment_shape.py` `ALL DEPLOYMENT SHAPE CHECKS PASSED`.
    - `tests/doc_claims.py` failed 1 of 441: `architecture.md:306 modules_free_of_homeassistant: documented=64 measured=65`.
  - At `b4a84ed9f1`:
    - `tests/doc_claims.py` `ALL 441 checks PASSED`, `tests/guard_pins.py` 91/91 and `tests/structure.py` `STRUCTURE RATCHET PASSED`.
    - The FLOWCAP, boost and feedback blocks pass in full.
    - M6-M11, the mutants on `pump_arbiter.py`, give the figures above.

## Unpinned sites

- custom_components/heatpump_optimizer/flow_limit.py:32 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/flow_limit.py:32 CMP_BOUND*2: pinned by mutation-autofix
- custom_components/heatpump_optimizer/flow_limit.py:52 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/flow_limit.py:54 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/inputs.py:744 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/inputs.py:745 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:623 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:978 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1103 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1111 RETURN_DEL: pinned by mutation-autofix

## Red checks

- `tests / fast (3.14)` at f36611dd2354: red on this PR's own two checks, `tests/doc_claims.py`'s comment ratchet (one new sentence over 40 words in `tests/features.py`) and `tests/harness_headers.py` (the D6 claims harness header at 98 modules after `flow_limit.py` made 99). Both are repaired at `566727d1db`, figures above. Cheaper detector: both scripts are in this diff's `scope.run` and run locally (`doc_claims.py` in seconds, `harness_headers.py` in minutes), and `prepr.sh` runs the scoped set; the previous head was handed off without a local prepr run (state b, the process existed and was not followed). Standing cost of the detector: zero new, it exists; no countermeasure is built.
- `tests / mutation` at f36611dd2354: red by construction on the site(s) under `## Unpinned sites`, all logged ADDED UNPINNED; mutation-autofix pins killed sites after the push. At `19eafc0fb1` that list also carried `pump_arbiter.py:936 GUARD_OFF`, described as "pinned by mutation-autofix". That claim was false: the site was a survivor, and autofix pins only killed mutants. The site is deleted at `6d54e9bd1d`, and the `pump_arbiter.py` sites after it moved up two lines; each moved line was compared with its old content. At `b4a84ed9f1`, each site was mapped to its line by content, comparing `git show 8c2c57a37f:<file>` with the head. The `_silent_target` and `quiet_windows.inside_silent` lines are main's since #3812, pinned by main's ledger entries, and are no longer this diff's: each has one exact match in `git show origin/main:<file>`. At `a6dd172693`, mutation-autofix's pins from the PR head (`7fb673f398`) cover 11 more sites, which are no longer listed: `flow_limit.py` 32 RETURN_DEL, 52 CMP_BOUND, 52 GUARD_OFF and 56 RETURN_DEL; `inputs.py` 576 RETURN_DEL, 584 RETURN_DEL, 742 GUARD_OFF and 743 CLAMP_DROP; `pump_arbiter.py` 614 GUARD_OFF, 999 CLAMP_DROP and 1103 BOOLOP. Prepr step 6d at that head lists 10 sites, and this section lists those 10.

## Forward-carry

- The entity-range clamp in `inputs.write_setpoint` is owned here, and R11-SEAM-actuation-writes (design `28bedac8`, section "Grid and range") consumes it instead of adding its own. That note's amendment is the orchestrator's, by its own ruling. Carry: #3744 (owned by R11-SEAM-actuation-writes)
- A root cause is owed under `defect-root-cause.md`, because the defect reached a released version (v10.1.2). The named cause is an integration-advertised maximum above the device's accepted one, written by a boost that drives the entity to its maximum. Carry: dismissed: the orchestrator dispatches the root-cause seat, and a fixer may not run it (`root-cause.md`).
- The two `_inside_silent` killed-by pins were deleted with their anchor. Carry: dismissed: CI mutation-autofix re-pins killed mutants (`ci-autofix.md`).

## Friction

none


