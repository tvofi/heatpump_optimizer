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

`53fc30d6c91d76ea04c6f8fc7259c1d6809b1b9c`, which merges origin/main `d4fb5351beee7d74ab1525cc96adef563612532c` (no conflict; the ledger merge driver resolved `tests/closures.json` as a set). That is the merge base. Between the previous merge base `fb9b3fc1f` and it, main's production delta is #2448, the heat-loss learners' rate limit (`coordinator.py`, `thermal_model.py`'s learner), which no solve in this diff's figures reads. Figures labelled "merge base" were taken from a detached worktree at `d4fb5351b` unless a line says `fb9b3fc1f`.

## Mutation proof

The ledger is the proof of record. `python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/features.py` was run at `91e94bcab` and again at `f037c1e8e`. Every site `ci_predict.py` lists is now pinned by `tests/features.py`, and each run's null control (a comment-only edit) survived:
- `PIN KILLED: 6 pinned, 1 left unpinned`. The survivor was `thermal_model.py:1452 CONST` (`FLOW_MIN_LIFT_K`). The tank check compared against the imported lift, so a changed constant moved both sides. "a tank at 24 degC writes 29 at the floor, not the 35 the return-or-hold anchor wrote" now asserts `29.0` outright.
- `PIN KILLED: 1 pinned, 0 left unpinned`: `thermal_model.py:1452 CONST -- killed by tests/features.py`.

The architect note's mutants and the precedence rungs were applied by hand, with `$SCRATCH/mutants.py` (sha1 `5586d7fbcffd4df7aa5811eb6bcee154b8dcc569`), to a detached worktree and restored, with `git status --short` clean after. They were run under `$SCRATCH/mini.py`, which holds the new checks verbatim from `tests/features.py`, at `91e94bcab`. M0 (no mutation) passes and every mutant exits 1.

| Mutant | Production edit | Goes red |
|---|---|---|
| M1 (architect: the bottom reverted to the return temperature) | `_flow_inlet_c` reads `state.floor_return_temperature` again | "every combination of inlet sensors ...", "a tank at 24 degC writes 29 ...", "a stale rung falls to the next fresh one" |
| M2 | `FLOW_MIN_LIFT_K = 0.0` | the same 3 |
| M3 to M6 (one per rung) | each of the four `FLOW_INLET_KEYS` rungs dropped in turn | "every combination ..." (and for the tank rung, the M1 three) |
| M7 (architect: the new start dropped, space path) | the space-only `_relaxed_starts` call deleted | "a buffered rounded install with price spread books above the floor in the cheapest steps, and its own objective scores the plan lower than the solve without the relaxed start" |
| M8 (the new start dropped, hot-water path) | the hot-water `move_starts=` argument deleted | "with hot water on, the space solve around the hot-water plan carries the relaxed start: it lowers the objective in at least one of four cells and raises it in none" |
| M9 (architect: the smoothing dropped) | `_scores_rounded` ignores `_levels_relaxed` | the two above and "a clamped install gains one candidate, refined while the objective scores the duty-cycle reading, and rounds again after" |

## Null control

- **The architect note's control "flat-price run publishes the same plan" does not hold, and this diff does not claim it.** The flat band traps flat-price solves too. The check is "flat-price null control: at flat prices the relaxed start never ships a plan its own objective scores worse, on either path".
  - Census (Figures): 20 of 32 flat-price plans move, every one to a lower objective, and none to a higher one.
  - Owner's replica: the flat objective goes from 227.271 to 200.568 at recorded weather and from 359.288 to 359.280 at 8 K colder. The moved flat plan is 4.89 SEK net cheaper at recorded weather. That is a search gain, not a timing gain, so every gain below is quoted net of the flat-price column.
  - This weakens the control from plan identity to "never worse". Forward-carry carries it.
- **Full power still writes the ceiling** on every cell of the 16-cell matrix.
- **On an unclamped install nothing moves.** `_relaxed_starts` returns `cands` when `clamp_planned_levels` is false ("an install that can duty-cycle gains none and never scores rounded ...").
- **With no inlet sensor the mapping is today's.** "null control: no inlet sensor keeps today's rated hold, and the pump's outgoing temperature alone is not a rung" writes 35.0 at the floor and the configured ceiling at full power.
- **`lumped_dp` reads identically at both ends.** It imports only `compute_cop`, which this diff leaves alone.

## Why the round-1 checks failed on CI's Linux runner

`fast (3.14)` job 118039116220 failed the three round-1 solver checks. The cause was solver basins, not tolerance or start ordering. The rounded objective is non-convex, and which basin L-BFGS-B reaches depends on BLAS floats (`CLAUDE.md` rule 3).
- On x86_64 the control arm (no relaxed start) also left the band: 18.73 kWh above the floor against the fix's 14.79. It scored worse, 25.299 against 18.037, so the "books more above the floor" comparison was the wrong property.
- The single hot-water fixture tied at 19.475 on both arms after main's #2368, on arm64 as well.
- Flat-price plan identity is false (Null control).

The checks were re-cut to what the code guarantees on every architecture. The relaxed candidate is ranked on the shipped objective, so the plan is never worse. It is strictly better on the spread fixture and on at least one of four hot-water cells. None of them was loosened to pass: each still fails under M7, M8 or M9. Full `tests/features.py` at the head reads `ALL 4230 FEATURE CHECKS PASSED` here. CI's `fast (3.14)` at this head is the Linux arbiter.

## Figures

`$EXPORT` is the owner's private config-entry diagnostics export, passed by path and never committed; only aggregates are printed. `$STUDY` is the pre-study's script directory and `$SCRATCH` is this seat's. Commands run with `PYTHONPATH=tests/hastub:custom_components:tests`.

- Replica, taken at merge base `fb9b3fc1f` and head `0581da2ef`. The production delta since then is main's learner change and this round's tests, so they were not re-taken.
  - `python3 $SCRATCH/relaxexp.py $EXPORT <shift> none <dir>` (sha1 `86390e2c3c801b379a0b07d846097125591408e9`), the published `objective_value`, merge base to head:
    - spread, recorded weather: 138.419 to 126.004.
    - spread, 8 K colder: 322.738 to 286.120.
    - flat, recorded weather: 227.271 to 200.568.
    - flat, 8 K colder: 359.288 to 359.280.
  - `python3 $SCRATCH/compare.py ...` (sha1 `3021080515cc58f3e4133ccdabe174153d1a8275`), net of the flat-price null:
    - recorded weather: the timing gain is -1.50 SEK/day.
    - 8 K colder: -8.76 SEK/day, with a comfort breach of 0.34 Kh below 18 °C against 0.02.
    - The flat-run plan alone: -4.89 SEK at recorded weather.
  - `python3 $STUDY/econ.py $EXPORT 0|-8` (sha1 `991201b13ef4c63d478d7ae28345993f6759235c`) and `python3 $STUDY/lumped_dp.py $EXPORT <shift> 300 3 25` (sha1 `3910c877bada95440e1bb75962185b0e94105730`), each beside its flat-price run. `lumped_dp` is identical at both ends.
- `python3 dev/audit/harnesses/r10_setpoint_power.py`, the census of 32 synthetic buffered clamped installs, at the head:
  - `spread: cells 32 objective lower 24 higher 0 identical plan 8`
  - `flat: cells 32 objective lower 20 higher 0 identical plan 12`
  - `failures 0`
  - At the merge base the function is absent and both arms are the same tree: 0/0/32 on both.
- **CPU.** `python3 $SCRATCH/cputime.py $EXPORT <shift>` (sha1 `9e0f79c3a60c49484d47c07b767f286c455c5b86`) takes the minimum of three `process_time()` solves on this seat's arm64 machine, at merge base `d4fb5351b` and head `53fc30d6c`. Merge base to head:
  - recorded weather: spread 1.06 to 3.11 s, flat 1.40 to 3.60 s.
  - 8 K colder: spread 2.10 to 4.77 s, flat 3.50 to 5.61 s.
  - That is +2.0 to +2.7 s per clamped solve.
  - **Raspberry Pi estimate, not measured:** a Pi 4 runs single-core Python about 4 to 6 times slower than this machine. That puts the extra cost at roughly +8 to +16 s per clamped solve, and a whole clamped solve at roughly 13 to 34 s. Installs that can duty-cycle pay nothing. Forward-carry carries the measurement on a Pi.
- Local green at the head: `tests/features.py` (`ALL 4230 FEATURE CHECKS PASSED`), `tests/structure.py` (`STRUCTURE RATCHET PASSED`), `python3 tools/pr/ci_predict.py --base origin/main` (`CI PREDICT: no closures or fast red predicted against d4fb5351beee`). `tests/entities.py`, `tests/stress.py` and `tests/optimality.py` are CI's at this head.

## Architecture score

n/a: no gate metric rises (`dS +0.0000 NULL`).

No raise. The binding constraint is `class_excess_loc`, which has zero headroom. It was paid by keeping `_relaxed_starts` and `_scores_rounded` as module functions and by cutting a 12-line objective comment to 3. `tests/structure.py` passes at the recorded value.

## Red checks

On #2445 at `0581da2ef`:
- **`mutation`**, job 118038943653: 7 ADDED UNPINNED sites. The autofix, job 118055076573, printed `skip-measure-failed` because `fast` was red, so no pin was recorded.
  - This diff's. Fixed: all 7 are pinned in `tests/mutation_ledger/killed_by/` (Mutation proof), and the CONST survivor gained a killing check.
  - The cheaper detector is `ci_predict.py` plus a local `--pin-killed` before push.
- **`fast (3.14)`**, job 118039116220: the three round-1 solver checks failed on Linux. This diff's. Fixed by re-cutting them to cross-architecture guarantees ("Why the round-1 checks failed").
- **`pr-contract`**, job 118039151183: "check `mutation` is red and `## Red checks` does not name it". This diff's body. Fixed by this section.
- **`nightly-status`**: **main's, not this diff's.** Main's scheduled run 39218718759 failed in its record-autofix job 117948682913, where `tools/audit/seat/record_row.py`'s `enumerate_merges` raised `HTTPError 403 Forbidden`. This diff touches neither that file nor that workflow.
- **`tests/optimality.py` locally** reads `1 of 84 OPTIMALITY CHECKS FAILED` on arm64 ("one|summer_negative|shoulder: a recorded claim still has a gap (not stale)"). The merge base `c35302773` prints the same line, so the red is inherited and per-architecture. CI's `optimality` is the arbiter.

## Forward-carry

- Flat-price control weakened from plan identity to "never worse". The relaxed start also unsticks flat-price solves (20 of 32 census cells; -4.89 SEK net on the replica), so plan identity cannot hold for this fix. Owed: an owner or architect ruling on whether "no gain without a price spread" is the control. Carry: R10-SETPOINT-POWER
- Raspberry Pi CPU of the relaxed start, estimated here only at +8 to +16 s per clamped solve. Owed: a measured `process_time` on a Pi 4 or 5 at this head and its merge base, plus a decision on whether to cap `maxiter` for the relaxed pass. Carry: R10-SETPOINT-POWER

## Unpinned sites

none: `python3 tools/pr/ci_predict.py --base origin/main` lists 7 added sites, and every one has a `killed_by` record at the head:
- `custom_components/heatpump_optimizer/optimizer.py:158 BOOLOP` (`_scores_rounded`): pinned.
- `custom_components/heatpump_optimizer/optimizer.py:158 RETURN_DEL`: pinned.
- `custom_components/heatpump_optimizer/optimizer.py:188 CMP_BOUND` (`_relaxed_starts`' guard): pinned.
- `custom_components/heatpump_optimizer/optimizer.py:188 GUARD_OFF`: pinned.
- `custom_components/heatpump_optimizer/optimizer.py:202 RETURN_DEL`: pinned.
- `custom_components/heatpump_optimizer/thermal_model.py:1452 CONST` (`FLOW_MIN_LIFT_K`): pinned.
- `custom_components/heatpump_optimizer/thermal_model.py:1465 RETURN_DEL` (`modulation_floor_flow_c`): pinned.

## Friction

- `fixer.md`: `missing-instrument`: a features check that compares a mapping against an imported constant pins nothing about the constant's value. Only `--pin-killed` showed it; the hand-run mutant had been edited differently. Carry: the fixer's, practised here: run the ledger's own mutant before claiming a kill.
