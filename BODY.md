R10-SETPOINT-POWER: the flow set-point is a power command

Part of #201. Closes no filed issue: the group comes from the owner's live diagnostics (tvofi, 2026-10-19).

On an install whose pump power is commanded through a heating-flow set-point, the plan sat at the 1.5 kW floor all day despite a price spread. The owner's words: "a 55 degree setpoint does not necessarily mean a 55 degree outgoing temperature when done in short slots, it is just a way to apply maximum power". Two defects caused it, and this diff fixes both.

- **The mapping (thermal_model.py, pump_arbiter.py).** `flow_setpoint_for_level` set the floor level's set-point to the return temperature, or 35 °C when no return sensor was configured. With the tank at 23-34 °C, that commands about a third of the planned draw. The floor's set-point is now `modulation_floor_flow_c(inlet)`: the measured inlet water plus `FLOW_MIN_LIFT_K` (5 K, the condenser spread EN 14511 rates a pump at). Full power still writes the configured ceiling. The arbiter's `_flow_inlet_c` is the one resolver, and it reads `FLOW_INLET_KEYS` through `InputReader`, so a stale or implausible slot drops to the next rung. Precedence, owner's requirement (tvofi via the orchestrator, 2026-10-19: "works across as many combinations of setups as possible"):
  1. `heat_pump_return_temp_entity`: the condenser's own inlet, on any plant.
  2. `buffer_tank_temp_entity`: on a buffered plant, with or without a mixing valve, the pump heats the tank.
  3. `floor_return_temp_entity`: on a direct-to-radiator plant this is the pump's inlet. Behind a buffer it is the mixed circuit's return, colder than the tank, so the floor errs toward less power.
  4. `valve_outlet_temp_entity`: house-side supply. On a wood topology it is mixed with the wood tank and can stand above the pump's inlet, so it is the last rung.
  5. None of these read: the rated 35 °C (`FLOW_HOLD_C`), today's default.

  Per plant: with no buffer, the pump return anchors, else the floor return. With a buffer and no valve, the pump return, else the tank. With a buffer and a valve, the pump return, else the tank, else the floor return, else the valve outlet.

  `heat_pump_supply_temp_entity`, the pump's outgoing temperature, is deliberately not a rung. It is the set-point's own controlled variable, so a floor anchored on it would chase itself. **No config key is added.** The four slots above and the supply slot already exist, each with config-flow and options-flow fields, strings and diagnostics. With none of them set, the floor is exactly today's 35 °C. One description in `strings.json` (`pump_duty_mode`) still said the floor slides "toward the return temperature or 35 °C". It now names the precedence. `coordinator.py` is unchanged, as the architect note asks.
- **The flat band (optimizer.py).** On a clamped install the objective scores the levels projected onto `{0} ∪ [p_min, p_max]`. Its cost is therefore flat between 0 and p_min, and a start that descends into that band stalls with a zero gradient. `_relaxed_starts` runs one L-BFGS-B pass from the first structural start on the duty-cycle reading (the objective with `_levels_relaxed` set, which has no flat band). It appends the result as one more candidate. The multi-start refines and ranks that candidate on the rounded objective like every other, so what ships is still scored as it ships, and never worse than without it. Both solve paths carry it: the space-only path through its existing `move_starts` hook, ahead of the two-zone continuation, and the space solve inside the hot-water path on its initial solve only, like that path's other structural seeds. On a warm pass the hot-water path names a start index past the last, which `_relaxed_starts`' own guard returns unchanged. On an install that can duty-cycle it is the identity, so no unclamped plan moves.

Alternatives, and why each lost:
- **Smoothing the projection inside the objective.** It scores a level the install cannot deliver.
- **Moving the start in place**, as the two-zone continuation does. It re-plans through another basin even where the relaxed candidate loses.
- **Price-ranked seeds at fixed levels** (p_min plus a quarter or a half of the band, at the first start's energy). Tried on the replica: they moved no stalled spread plan and still changed the flat plan. This was a scratch probe, so it is not cited as a figure.
- **Counting radiator water in the system capacity** (optional in the architect note). Not taken: it re-prices every buffered plan and every golden, which is outside this group.
- **Wiring `draw_range.planned_range`** into the solve. Not done; it stays diagnostics-only.

## Head

`432c425568e54768a2d9db091aab73af74f51cbd`, which merges origin/main `c3530277373ddf87652858f9ecb0ee1cf36f4347` (merge commit `97008cc4e`, no conflict). After a fetch on 2026-10-19, `origin/main` was still `c35302773` and the merge base is that commit. Between `db3293dcb`, where the branch was cut, and that main, `git diff --stat db3293dcb c35302773 -- custom_components tests/features.py` prints nothing. Figures labelled "merge base" were taken from a detached worktree at `c35302773`.

## Mutation proof

Each mutant was applied to a detached worktree, then restored, and `git status --short` was clean after. The runner is `$SCRATCH/mutants.py` (sha1 `5586d7fbcffd4df7aa5811eb6bcee154b8dcc569`).
- Under the full `PYTHONPATH=tests/hastub python3 tests/features.py`: M1, M7 and M8, at `76e54dff3`, whose mapping and new solver checks equal the head's.
- Under `$SCRATCH/mini.py` (sha1 `52594aab8ced92b75c11ce28eb43f84fbe17af07`), which holds the ten new checks verbatim from `tests/features.py`: every mutant, at the head. M0 (no mutation) prints `ALL 10 SETPOINT PASSED`, and every mutant exits 1.

| Mutant | Production edit | Checks that go red |
|---|---|---|
| M1 (architect: the bottom reverted to the return temperature) | `_flow_inlet_c` reads `state.floor_return_temperature` again | full features `3 of 4221 FEATURE CHECKS FAILED`: "every combination of inlet sensors writes the first rung's reading plus the lift ...", "a tank at 24 degC writes 29 at the floor, not the 35 ...", "a stale rung falls to the next fresh one" |
| M2 | `FLOW_MIN_LIFT_K = 0.0` | the same 3 |
| M3 | `heat_pump_return_temp_entity` dropped from `FLOW_INLET_KEYS` | "every combination ..." (cell `('heat_pump_return_temp_entity',)` writes 35.0) |
| M4 | `buffer_tank_temp_entity` dropped | the M1 three |
| M5 | `floor_return_temp_entity` dropped | "every combination ..." |
| M6 | `valve_outlet_temp_entity` dropped | "every combination ..." |
| M7 (architect: the new start dropped, space path) | the `_relaxed_starts` call in the space-only `move_starts` deleted | full features `1 of 4221`: "a buffered rounded install with price spread books above the floor in the cheapest steps ..." (2.63 vs 2.63 kWh) |
| M8 | the hot-water path's `move_starts=` argument deleted | full features `1 of 4221`: "with hot water on, the space solve around the hot-water plan carries the relaxed start too" (18.680 vs 18.680) |
| M9 (architect: the smoothing dropped) | `_scores_rounded` ignores `_levels_relaxed` | 3: the two above and "a clamped install gains one candidate, refined while the objective scores the duty-cycle reading, and rounds again after" |
| S1 (`_scores_rounded` BOOLOP) | `and` becomes `or` | 4, among them "an install that can duty-cycle gains none and never scores rounded; a start past the last (the warm pass) adds none" |
| S2 (`_scores_rounded` RETURN_DEL) | the return removed | 4 |
| S3 (`_relaxed_starts` CMP_BOUND) | `first >= len(cands)` becomes `>` | `IndexError: list index out of range` stops the run |
| S4 (`_relaxed_starts` GUARD_OFF) | the guard becomes `if False:` | "an install that can duty-cycle gains none ..." |
| S5 (`_relaxed_starts` RETURN_DEL) | the return removed | 3, then a `TypeError` stops the run |
| S7 (`modulation_floor_flow_c` RETURN_DEL) | the return removed | 4, among them "the floor helper refuses an unmeasured inlet rather than guessing one" |

## Null control

- **On the two test fixtures the flat-price plan is unchanged, but not in general. The architect note's control "flat-price run publishes the same plan" does not hold on the owner's replica.**
  - The test "flat-price null control: on both fixtures the flat-price plan is the one shipped without the relaxed start" holds on the space-only and the hot-water synthetic fixtures.
  - The flat band also traps flat-price solves. On the census (Figures), 18 of 32 synthetic cells publish a different flat-price plan; every one is scored lower by the plan's own objective, and none higher.
  - On the owner's replica the flat-price plan moves too. Its objective goes from 227.271 to 200.568 at recorded weather and from 359.288 to 359.280 at 8 K colder. Costed net of end-of-horizon stores, the moved flat plan is 4.89 SEK cheaper at recorded weather. That is a search gain, not a timing gain, so every gain figure below is quoted net of the flat-price column.
  - This deviates from the note's control as written, and the reviewer judges it. Running the relaxed pass from every start, a scratch probe, moved the flat plan further. One candidate is the narrowest form that still unstalls the spread plan.
- **On an unclamped install nothing moves.** `_relaxed_starts` returns `cands` when `clamp_planned_levels` is false. `GOLDEN_MODE=drift python3 tests/golden.py` prints `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`.
- **With no inlet sensor the mapping is today's.** The check "null control: no inlet sensor keeps today's rated hold, and the pump's outgoing temperature alone is not a rung" writes 35.0 at the floor and 48.0 (the configured ceiling) at full power.
- **`lumped_dp` reads flat at both ends, as it should.** It is the study's independent DP over a lumped system temperature. It imports only `compute_cop`, which this diff leaves alone, so its rows are identical at the merge base and the head. It is cited as the study's own physics, not as evidence for this diff.

## Figures

`$EXPORT` is the owner's private config-entry diagnostics export, passed by path, never committed; only aggregates are printed. `$STUDY` is the pre-study's script directory and `$SCRATCH` is this seat's. Each command runs from the tree being measured with `PYTHONPATH=tests/hastub:custom_components:tests`. The replica figures were taken at `76e54dff3`. The later production delta only routes the warm pass through the index guard, and `$SCRATCH/relaxexp.py` re-run at the head wrote byte-identical plans for all four (shift, price) runs (`cmp -s` against the `76e54dff3` plans), and the same objectives.

- `python3 $STUDY/econ.py $EXPORT 0` and `... $EXPORT -8` (sha1 `991201b13ef4c63d478d7ae28345993f6759235c`), row "(a) main, as shipped": kWh, SEK at spread prices, SEK at flat prices (the null), and comfort breach in Kh below 18 °C.
  - recorded weather, merge base: 18.0 kWh, 16.44 SEK at spread, 23.31 at flat, breach 0.00; 48 solver steps in (0, p_min).
  - recorded weather, head: 20.6 kWh, 18.26 at spread, 26.63 at flat, breach 0.00; 13 steps in (0, p_min).
  - 8 K colder, merge base: 43.5 kWh, 52.11 at spread, 56.32 at flat, breach 0.02, 2 starts.
  - 8 K colder, head: 45.4 kWh, 45.79 at spread, 58.76 at flat, breach 0.34, 6 starts.
- `python3 $SCRATCH/compare.py $EXPORT <shift> spread <base dir> <head dir>` (sha1 `3021080515cc58f3e4133ccdabe174153d1a8275`). It simulates each plan in the replica's model, and values the head-minus-base difference in end-of-horizon stores at the flat price through the mean COP, as `econ.py` does. Net of that credit, the spread-chosen plan:
  - recorded weather: -1.77 SEK at spread prices, -0.27 SEK costed at flat prices. The timing gain net of the flat-price null is -1.50 SEK/day.
  - 8 K colder: -7.62 SEK at spread, +1.14 SEK at flat, so -8.76 SEK/day net. The comfort cost is 0.34 Kh below 18 °C, against 0.02 at the merge base. The objective prices that trade; it is stated here so it is not read as free.
  - The study had predicted about -1.2 and -5.3 SEK/day.
- `python3 $SCRATCH/compare.py $EXPORT <shift> flat ...`, the flat-price run's own plan: -4.89 SEK net at recorded weather, -0.14 SEK net at 8 K colder.
- `python3 $SCRATCH/relaxexp.py $EXPORT <shift> none <dir>` (sha1 `86390e2c3c801b379a0b07d846097125591408e9`), the published plan's `objective_value`, merge base to head:
  - spread, recorded weather: 138.419 to 126.004.
  - flat, recorded weather: 227.271 to 200.568.
  - spread, 8 K colder: 322.738 to 286.120.
  - flat, 8 K colder: 359.288 to 359.280.
- `python3 $STUDY/lumped_dp.py $EXPORT <shift> 300 3 25` (sha1 `3910c877bada95440e1bb75962185b0e94105730`), at both shifts: identical rows at the merge base and the head, each beside its flat-price column. Sliding against low-long reads DiD -0.74 SEK at recorded weather and -5.53 SEK at 8 K colder: the study's physics, unchanged by this diff (Null control).
- `python3 dev/audit/harnesses/r10_setpoint_power.py`, the census. The rule: 32 synthetic buffered clamped installs (two-zone off/on, hot water off/on, heat-loss scale 0.6/1.0, outdoor -4/+2 °C, starting tank 25/34 °C), each solved with and without `_relaxed_starts`, counting cells by the plan's own `objective_value`.
  - head: `spread: cells 32 objective lower 27 higher 0 identical plan 5`, `flat: cells 32 objective lower 18 higher 0 identical plan 14`, `failures 0`.
  - merge base, where the function is absent and both arms are the tree, so the census reads its own null: `spread: cells 32 objective lower 0 higher 0 identical plan 32`, `flat: cells 32 objective lower 0 higher 0 identical plan 32`, `failures 0`.
- `python3 $SCRATCH/cputime.py $EXPORT <shift>` (sha1 `9e0f79c3a60c49484d47c07b767f286c455c5b86`): the minimum of three `time.process_time()` solve CPU seconds on this seat's arm64 machine, at `76e54dff3`. It is a cost, on clamped installs only, for the reviewer to weigh against the D9 Raspberry-Pi target. Merge base to head:
  - recorded weather: spread 1.43 to 3.02 s, flat 1.69 to 3.43 s.
  - 8 K colder: spread 2.56 to 4.91 s, flat 4.75 to 5.81 s.
- The census for the mapping class (step 8). The rule: the empty subset and every non-empty subset of the four inlet slots, 16 cells. "every combination of inlet sensors ..." asserts that each cell writes the first rung's reading plus `FLOW_MIN_LIFT_K` at the floor and 48.0 at full power, and it reads 16 cells, 0 wrong, at the head. The seams are the rungs of `FLOW_INLET_KEYS`, each closed in this diff (M3 to M6). The supply slot is excluded by design choice, and a check pins that.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`
- Re-run green locally at the head with `PYTHONPATH=tests/hastub`, each with its last line:
  - `tests/features.py` (`ALL 4223 FEATURE CHECKS PASSED`), `tests/structure.py` (`STRUCTURE RATCHET PASSED`) and `env -u BASH_ENV python3 tests/entities.py` (`ALL 2349 ENTITY CHECKS PASSED`).
  - `tests/harness_headers.py` (`ALL 109 HARNESS HEADER CHECKS PASSED`), `tests/closure.py selftest` (`ALL 124 closure shrink pins PASSED`) and `python3 -I tools/audit/seat/tmp_paths.py --check` (`0 refused`).
  - the rest of the scope: `tests/arch_score_head.py` (`ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`), `tests/backtest.py` (`ALL 25 BACKTEST CHECKS PASSED`), `tests/block_duty.py` (`ALL 46 BLOCK DUTY CHECKS PASSED`), `tests/boost_drift_replay.py` (`ALL 46 BOOST DRIFT CHECKS PASSED`), `tests/config_flow_steps.py` (`ALL 499 checks PASSED`), `tests/debug_collect.py` (`ALL 122 DEBUG COLLECT CHECKS PASSED`), `tests/deployment_shape.py` (`ALL DEPLOYMENT SHAPE CHECKS PASSED`), `tests/doc_claims.py` (`ALL 169 checks PASSED`), `tests/edge.py` (`ALL EDGE CASES PASS`), `tests/env_drift.py` (`NO STALE FIXTURE: 5 committed fixture(s) still match what this tree computes`), `tests/finite_boundary.py` (`ALL 106 FINITE BOUNDARY CHECKS PASSED`), `GOLDEN_MODE=drift GOLDEN_REF=c3530277373ddf87652858f9ecb0ee1cf36f4347 python3 tests/golden.py` (`NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`), `tests/guard_pins.py` (`ALL 50 GUARD PIN CHECKS PASSED`), `tests/manual_plan.py` (`ALL 129 manual plan checks PASSED`), `tests/plan_view.py` (`plan reason codes, price provenance and slot energy OK`), `tests/solar_alignment.py` (`ALL SOLAR ALIGNMENT CHECKS PASSED`), `tests/typing_ruler.py` (`ALL 12 typing-ruler source checks PASSED`), `tests/validate.py` (`NO ISSUES`), `tests/wood_advisor.py` (`ALL 7 wood-advisor checks PASSED`), `node tests/card.mjs` (`ALL CARD CHECKS PASSED`) and `node tests/card_drift.mjs` (`card_drift: identical in all 40 states`).
  - **Left to CI:** `tests/stress.py` and `tests/optimality.py`, heavy; their check-runs are owed at the PR head (Red checks for optimality's local line).
- `python3 tools/audit/archscore/score.py --diff c3530277373ddf87652858f9ecb0ee1cf36f4347`: `Architecture score: dS +0.0000 NULL`.

## Architecture score

n/a: no gate metric rises (`dS +0.0000 NULL`).

No raise. `class_excess_loc` first read `18365 > 18302 (+63)` with the relaxed start as a `HeatPumpOptimizer` method. It was paid two ways:
- `_relaxed_starts` and `_scores_rounded` are module functions taking the optimizer, as `_duty_floor` already is. They are pure apart from the one flag they set and restore.
- A 12-line comment in the objective is cut to 3. It re-stated the module docstring's weather-anticipation paragraph and the history of two removed terms, and the 3 lines keep the reason and the measured effect.

`tests/structure.py` then prints `STRUCTURE RATCHET PASSED` at the recorded value. No other budget moved.

## Red checks

No PR yet, so no CI check-run exists; CI's are owed at the PR head. One local red, inherited from main:
- **`tests/optimality.py`** reads `1 of 84 OPTIMALITY CHECKS FAILED` on this arm64 seat: "one|summer_negative|shoulder: a recorded claim still has a gap (not stale)". The detail is "claimed but gap 0.0000% is at or below the bar".
  - The merge base prints the same line and the same count, so the red is not this diff's. The cell is an unclamped install, so `_relaxed_starts` is the identity there.
  - The claim is recorded for CI's x86_64 runner, and solver floats do not reproduce across BLAS builds (`CLAUDE.md` rule 3). `prepr.sh`'s closures step refused for the same reason, because the closure recorder runs `tests/optimality.py`.
  - CI's `optimality` check-run at the PR head is the arbiter. No cheaper detector exists for a per-architecture float difference.

## Forward-carry

none. The gap between the flat-price control's letter and its purpose (Null control) is this group's review question, not a later stage's brief.

## Unpinned sites

`python3 tools/pr/ci_predict.py --base origin/main` lists 7 sites the diff adds. A value check in this diff kills each one (Mutation proof), so each is `mutation-autofix`'s to pin at the PR head:
- `custom_components/heatpump_optimizer/optimizer.py:158 BOOLOP` (`_scores_rounded`): killed, S1.
- `custom_components/heatpump_optimizer/optimizer.py:158 RETURN_DEL`: killed, S2.
- `custom_components/heatpump_optimizer/optimizer.py:188 CMP_BOUND` (`_relaxed_starts`' guard): killed, S3.
- `custom_components/heatpump_optimizer/optimizer.py:188 GUARD_OFF`: killed, S4.
- `custom_components/heatpump_optimizer/optimizer.py:202 RETURN_DEL` (`_relaxed_starts`' return): killed, S5.
- `custom_components/heatpump_optimizer/thermal_model.py:1452 CONST` (`FLOW_MIN_LIFT_K = 5.0`): killed, M2.
- `custom_components/heatpump_optimizer/thermal_model.py:1465 RETURN_DEL` (`modulation_floor_flow_c`): killed, S7.

## Friction

- `fixer.md`: `contradiction`: the architect note's flat-price control ("flat-price run publishes the same plan") cannot hold for a fix to a search defect that also traps flat-price solves; the census shows 18 of 32 flat plans moving, every one to a lower objective. Carry: the orchestrator's, whose architect notes these are (`orchestrator.md` section 5). A control could state the property it guards, "no gain without a price spread", rather than plan identity.
