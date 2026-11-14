R10-SAV-VALUATION-RESIDUE part 4: Carry 9. Behind a throttling valve whose curve cannot hold the target, `_thermostat_held_state` bisected a family of states with both floors at one temperature (`_held_zones`). On a two-zone house the plant at its pump settles with the floors apart: radiators above, slab-fed floor below, and the mean is warmer than any level state the curve can feed. The reference therefore started below its own ceiling, and its 96-step day warmed to that ceiling, so every booked day bought the warming. That affects `baseline_cost` and the saving against it on every two-zone valved install whose curve is the bound.

The fix adds `thermal_model.valve_top_equilibrium`, which solves the plant's own rates (`_two_zone_rates`, affine while each zone sits below its circuit's top) with every circuit at the curve's top. `optimizer._held_at_valve_top` takes that equilibrium only where the valve's top draw is the bound and the pump can make that draw (`_pump_unreachable`, now shared with `_held_unreachable`). Anywhere else, the level bisection (`_held_bisected`, moved out unchanged) holds as before.

The three measurements the brief puts first:
- **(0) The harness.** Pull request 3481 has not merged (`git merge-base --is-ancestor 9a543f44d696 origin/main` is false at `a77d71fb755f`). Its `fields` arm was run from that head in a detached worktree. Its imports (`whatif`) and `_compute_baseline_power(start=)` do not exist on main, so it cannot run against the merge base. The install row is in this pull request's own harness, `dev/audit/harnesses/r10_sav_held_install.py`.
- **(1) The `fields` arm at 3481's head.** That head's base is main `c987209cc7`, whose production code equals `a77d71fb755f`'s (`git diff --quiet c987209cc7 a77d71fb75 -- custom_components/` exits 0); 3481's own diff adds the `start=` hook and touches neither `_thermostat_held_state`'s body nor `_held_unreachable`. Second-pass room: single-zone 21.00, valve one tank 19.88, two-zone valve two-tank 21.01 (`## Figures`).
- **(2) Install-parameter reproduction.** The 3574 body reports a scratch probe on `tests/replay/owner-2026-10-30-away.json` (two zones, valve `manual` at 21 C, a 4 kW pump). Its probe is not in the tree, so this pull request builds the reproduction as `tests/profiles.py` `replay_install()`, used by the new harness and the new checks. At the merge base, +5 C reads: held 20.527, day's end 20.719, plant's ceiling 20.719. At -15 C: held 19.532, end 19.982, plant 19.980. 3574 read 20.557 against 20.749 at its own base, the same shape.
- **(3) The cause, from the code.**
  - **The synthetic one-tank fixture is the unreachable case part 1 models.** No behaviour changes there. The plant at its pump settles where the reference holds: 19.888 at 0 C, 20.662 / 19.115 / 17.568 at +5 / -5 / -15 C (`## Figures`). The bound is the derived curve, `mixing_valve.flow_setpoint`. Its draw is `_single_valve_rates`' `ua * (min(T_buf, flow_set) - T_slab)`. The curve adds the house's loss over the emitter UA to the target, but the single-zone emitters feed the slab, so the slab-to-room resistance is not in it, and the room settles below target even with the target at `comfort_ceiling`. The plan cannot do better: `_derive_hold_schedule` only ever lowers the valve target below `mixing_valve_target or comfort_ceiling`, and `manual` mode sets none. This part's files leave that alone; the plant-curve finding is carried (`## Forward-carry`). The new check's one-tank control and the 3481 `fields` row pin that the reference equals the plant there.
  - **On the install it is the held state.** The cause is `_thermostat_held_state`'s unreachable branch: `held_at` builds every candidate through `_held_zones`, `upper_floor_temperature = lower_floor_temperature = temp`. `_held_unreachable`'s valve half (`need_kw > valve_top_draw(...)`) is right. The family it is tested on is what is wrong: the curve's top draw at level floors is less than at the plant's own split.
  - **`valve_top_draw` is right**: the plant's draw is the same `_circuit_draw` at the same tops.
  - **`_compute_baseline_power`'s use is right**: from the corrected held state its day ends where it starts (gap 0.000, `## Figures`).

## Head

`8fac4e7e5b18dff2973f3cf35848199b9de26fb1`, seven commits on origin/main `a77d71fb755f231934e5e59ce1c38c51f86b6439`, measured 2026-11-14 (UTC). The last commit adds only `tests/closures.json`'s INERT entry (`tools/pr/ci_predict.py --apply-inert`) and deletes the moved pin; every other figure was taken at `193b86d9d0`, whose production code and checks are the head's (`git diff --stat 193b86d9d0 8fac4e7e5b` names those two files alone). `git merge-tree --write-tree origin/main HEAD` reports no conflict. Pull request 3574 had not landed at that tip, so origin/main was not merged. VERSION, the manifest and RELEASE_NOTES are untouched.

## Mutation proof

Command: `PYTHONPATH=tests/hastub:tests:custom_components python3 tools/audit/seat/mutant_run.py --diff a77d71fb755f...HEAD --report-only --cmd "python3 tools/audit/seat/features_block.py '# --- R10-SAV-VALUATION-RESIDUE: stored heat bought back' '# --- R10-WATER-SETPOINT-FEEDBACK (outside report #3380'"`.
- 35 mutants are drawn (`--list`). 32 are killed. The 3 survivors are the three `>` to `>=` equality bounds, each triaged equivalent under `tests/mutation_ledger/survivor_triage/`:
  - `optimizer.py` `_held_at_valve_top` CMP_BOUND db7fdb5e;
  - `_pump_unreachable` CMP_BOUND 51c81f26;
  - `thermal_model.py` `valve_top_equilibrium` CMP_BOUND 43d78bdc.
- The ledger's CLAMP_DROP operator, which `mutant_run --diff` does not draw, was run by spec on both `min(top, p.buffer_max_temp)` clamps, together with the guard's GUARD_OFF: `KILLED CLAMP_DROP t_rad`, `KILLED CLAMP_DROP t_floor`, `KILLED GUARD_OFF valve_top_equilibrium none`, `SURVIVED NULL`.
- Failing first: at `6fcca20502` (the checks alone, base production code), the same block reads `FAIL R10-SAV-VALUATION-RESIDUE Carry 9: on an install whose valve curve cannot hold the setpoint, ...` with the held floors level at 20.527 against the plant's 20.719 / 21.009 / 20.428 at +5 C, `1 of 12 FEATURES BLOCK FAILED`.
- At the head: `ALL 13 FEATURES BLOCK PASSED`.
- Three first-round survivors were removed by changing the code, not by triage. The tank line re-derived the tank `held_at` had already placed at the curve's top. The steady charge's `dt` multiplied a zero; it is now `math.inf`. The solve's zero origin is now the state's own zones.
- That last edit exposed a real gap, which part 1's pump check (4 kW, valve at 40 C, -25 C) caught at 36.9 C: the valve's ceiling was taken where the pump, not the curve, was the bound. `cdbd4c6f56` gates it on the valve's own bound.
- The stale `_held_unreachable` CMP_BOUND triage and RETURN_DEL pin at ebd24b04 are deleted: their line moved unchanged into `_pump_unreachable`.

## Null control

- Bit for bit, merge base against head, `_thermostat_held_state`'s room and the day's summed `_compute_baseline_power` (float hex, a scratch probe over 4 outdoor temperatures x 6 houses). 20 of 24 rows are identical: single-zone, two-zone, the one-tank valve, the two-zone valve two-tank control, and the install with its valve off. The 4 install-valve rows move (`## Figures`).
- The install with the valve off holds 21.000 on both floors at every temperature; that is the new check's null and the harness's `valve off` rows.
- Flat price: `tests/golden/flat_prices.json` (`baseline_cost` 100.179654) and its valved twin `valve_storage_flat_prices` (two-zone, valve `manual`) are unmoved. Neither reaches the changed branch: a counting probe over `golden.capture` reads `_held_at_valve_top` called 0 times in each (2 held-state calls each), because both curves hold the target there.
- Golden drift: no scenario moves (`## Figures`).

## Figures

<!-- figure-block: scope-line mb=a77d71fb755f231934e5e59ce1c38c51f86b6439 head=8fac4e7e5b18dff2973f3cf35848199b9de26fb1 -->
~~~text
MODE: SCOPED -- 27 script(s) run, 6 scoped out.
~~~
<!-- /figure-block -->
- `PYTHONPATH=tests/hastub:tests:custom_components python3 $EXPORT/dev/audit/harnesses/r10_advisor_steady_seams.py fields`, `$EXPORT` a detached worktree of pull request 3481's head 9a543f44d696 and run from that tree (sha1 e6a4870c93b400cbc920245319ccf1f5a117c3cb), the `holds` lines: `single-zone ... 21.00`, `two-zone ... 21.33`, `valve, one tank ... 19.88`, `two-zone valve two-tank ... 21.01`. The carry quotes 19.93; this head of 3481 prints 19.88. Carry: dismissed: the brief's measurement (1), not a finding
- `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_held_install.py` (sha1 d8920de1a7c12fe27243e326278e4fc3459d493c). Each row is held / end / plant room, upper, lower:
  - Base (base production code, this tree's `tests/`):
    - install +5 C: `held 20.527/20.527/20.527 end 20.719/21.009/20.429 plant 20.719/21.009/20.428 gap 0.482`
    - -5 C: `held 20.029/... gap 0.806`
    - -15 C: `held 19.532/... gap 1.130`
  - Head: install +5 / -5 / -15 C `held 20.719/21.009/20.428`, `20.350/20.835/19.864`, `19.980/20.661/19.300`, each `gap 0.000`.
  - Both ends: one-tank `held` = `plant` at 20.662 / 19.115 / 17.568, `gap 0.000`; `valve off` held `21.000/21.000/21.000`.
  - Carry: dismissed: the control and install rows the brief asks for, not a finding
- Bitwise probe, the install's valve rows, held room and day kWh_e, base to head: +5 C 20.527 to 20.719, 12.7979 to 12.9413; 0 C 20.278 to 20.534, 19.9060 to 20.1266; -5 C 20.029 to 20.350, 29.5526 to 29.8781; -15 C 19.532 to 19.980, 64.9236 to 65.6335. The reference now holds its ceiling all day instead of warming to it, so its electricity rises and its stored-heat change falls to zero. Carry: dismissed: the fix's own effect
- `PYTHONPATH=tests/hastub GOLDEN_MODE=drift GOLDEN_REF=a77d71fb755f231934e5e59ce1c38c51f86b6439 python3 tests/golden.py`: `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56`. No claim file is touched. Carry: dismissed: a gate result
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, no budget re-recorded. `python3 tools/audit/archscore/score.py --diff a77d71fb755f`: `Architecture score: dS +0.0000 NULL`. Carry: dismissed: gate results
- Scoped gate, `GATE_SCOPE=auto PYTHONPATH=tests/hastub GOLDEN_MODE=drift GOLDEN_REF=a77d71fb755f231934e5e59ce1c38c51f86b6439 bash tests/run.sh` at `193b86d9d0`: `MODE: SCOPED -- 27 script(s) run, 6 scoped out`.
  - Every script up to `tests/stress.py` printed `ok`, `tests/features.py` included. The run then hit the session's 30-minute background limit inside `stress.py` and was stopped.
  - `stress.py` and `harness_headers.py` were re-run alone at the head with `PYTHONPATH=tests/hastub`: `ALL 115 HARNESS HEADER CHECKS PASSED`.
  - The first stress run read `1 of 116 STRESS CHECKS FAILED`. The failure was the CPU-timing check `the per-call-cost arm reaches the rule the sweep applies ... (round-5 D9-07)`: plain 49 ms, plain-again 37 ms (x0.75), doubled seam CPU 67 ms (x1.37) against the 1.80 factor. Counts were flat: evaluations 42 vs 42, simulate 131232 vs 131232.
  - The re-run, alone, read `ALL 116 STRESS CHECKS PASSED`. That is a timing instrument's noise, not this diff: its own null drifted by x0.75, and the changed branch adds no seam call to a reachable solve, as the flat counts show.
  - Carry: dismissed: gate results

## Red checks

`mutation` (`tests / mutation`), predicted red by `tools/pr/ci_predict.py` at this head. The cause is the eight `ADDED UNPINNED` sites under `## Unpinned sites`, each killed and unpinned until `mutation-autofix` pins it after the pull request opens (`ci-autofix.md`). The two stale pins the moved lines left (`_thermostat_held_state` CLAMP_DROP c7dd28c1 and `_held_unreachable` RETURN_DEL ebd24b04) are deleted by hand here. Cheaper detector: `ci_predict.py`, prepr's step 6d, already ran locally in seconds and caught both the stale pins and the unpinned sites before any CI run. The cheapest detector is the one that fired, so no further countermeasure is built.

## Unpinned sites

`tools/pr/ci_predict.py` lists these `ADDED UNPINNED` sites. Each is killed by the group's block named in `## Mutation proof` and pinned by `mutation-autofix` once the pull request opens (`ci-autofix.md`):
- custom_components/heatpump_optimizer/optimizer.py:860 CLAMP_DROP: `min(outdoor, target)` in the `_held_bisected` call. Part 1's pin c7dd28c1 (killed by `tests/features.py`) held this text before the move; that pin went stale on the move and is deleted here.
- custom_components/heatpump_optimizer/optimizer.py:877 RETURN_DEL: `return held_at(lo)`.
- custom_components/heatpump_optimizer/optimizer.py:897 GUARD_OFF: `if top is None:`.
- custom_components/heatpump_optimizer/optimizer.py:902 RETURN_DEL: `_held_at_valve_top`'s return.
- custom_components/heatpump_optimizer/optimizer.py:914 RETURN_DEL: `_pump_unreachable`'s return.
- custom_components/heatpump_optimizer/optimizer.py:940 RETURN_DEL: `_held_unreachable`'s return.
- custom_components/heatpump_optimizer/thermal_model.py:2392 CLAMP_DROP*2: `KILLED CLAMP_DROP t_rad` and `KILLED CLAMP_DROP t_floor` by spec.
- custom_components/heatpump_optimizer/thermal_model.py:2404 GUARD_OFF: `KILLED GUARD_OFF valve_top_equilibrium none` by spec.

The diff run reads every RETURN_DEL and GUARD_OFF above killed. The three survivors prepr's `MUTANT_CMD` run reports on the diff's added lines are CMP_BOUND equality bounds, triaged equivalent rather than pinned:
- custom_components/heatpump_optimizer/optimizer.py `_held_at_valve_top` CMP_BOUND db7fdb5e
- custom_components/heatpump_optimizer/optimizer.py `_pump_unreachable` CMP_BOUND 51c81f26
- custom_components/heatpump_optimizer/thermal_model.py `valve_top_equilibrium` CMP_BOUND 43d78bdc

Each is under `tests/mutation_ledger/survivor_triage/`.

## Forward-carry

- The derived valve curve does not hold its own target on a single-zone house. `mixing_valve.flow_setpoint` adds the house's loss over the emitter UA to the target. `_single_valve_rates` puts every emitter on the slab, so the slab-to-room conductance (`slab_heat_transfer`) is not in the curve.
  - Measured with `dev/audit/harnesses/r10_sav_held_install.py`, the `one-tank` rows: the plant at its pump with the tank at its cap settles at 20.662 / 19.115 / 17.568 at +5 / -5 / -15 C. That is with the curve at `comfort_ceiling` 23 C, which the docstring says it holds "exactly". The reference matches the plant, so savings are not wrong here.
  - Control: the install's radiator floor, which the curve feeds directly, reaches 21.009 at +5 C.
  - This changes the plant every plan runs on, `thermal_model.py`'s throttled law and `mixing_valve.py`, outside this part's files, and would move valved golden fixtures. Legitimate only if the one-tank harness row reaches the curve's target within 0.02 K, the two-zone direct circuits are bitwise unchanged, and each moved fixture is claimed.
  - Re-measure with the harness at that stage's merge base.
  - Carry: R11-INTAKE-R10-RESIDUE

## Friction

none
