R10-BUFFER-OPENLOOP (R10-COMBI-TANK PR 0, S; design `a605014bff4478f470853109060f4ff7ef605d4c` §C0, approved by `design-verdict/r10-combi-tank` `56810263b`). Carry 0 (owner ruling tvofi 11-06): without a buffer probe, `_update_current_state` never advanced `buffer_tank_temperature` (class D12-s1-01). It kept the 40 °C `ThermalState` default, or its last value, and every solve started the buffer from it. Refs #3225 (PR B closes it); this PR closes no issue.

What changes (`custom_components/heatpump_optimizer/coordinator.py`):
- **`_seed_store(reading, result, trajectory_attr, now) -> float | None`** is a module-level function beside `_open_loop_plan_value`. It returns the reading if ok, otherwise the previous plan's trajectory at the covering step, otherwise `None`. On `None` the caller leaves the field as it is, so nothing is fabricated. It is one primitive, and PR B reuses it for `combi_tank_seed`.
- **`_update_current_state`**: the DHW seed is re-expressed through `_seed_store` with identical behaviour; the R9 D12-s1-01 checks are its control. The buffer is seeded the same way from `buffer_temp_trajectory`. Both writes land on the private `state` copy before `ctx.publish(self, state)`, which is R10-LIVESTATE's I1/I2. R10-LIVESTATE is on main (`f7567be02`), so this PR is not blocked on it.
- **The observation split (`_update_external_heat_detection`)**:
  - The rise inputs `dhw_temp` and `buffer_temp` take the measured value or `None`. Without this, a planned rise would be read as external-heat evidence.
  - The level input `hp_tank_temp` keeps its text and reads the best estimate, which is the seed. This keeps wood energy and displacement on for a wood install with no buffer probe.
  - Following the verdict's `observation-read-in-place` note, the rise inputs are read with the `reader` that method already builds, the way `outlet` and `wood_top` are. No coordinator attribute is carried between methods.
- **Which buffers.** The seed applies to every buffer whose last plan published a trajectory. The plan publishes one only under a throttling valve (`optimizer.py`, the `buffer_temp_trajectory=` ternary on `mixing_valve.is_throttling`). Without one the level stays where it was. The harness's `solve` arm shows this with the real solver.
- **Observable side effect, publish-only.** On an install with no DHW probe, the external-heat attribute `dhw_rise_c_per_h` (binary sensor attributes, `ExternalHeatState.as_dict`) now reads `None` instead of a rate taken from the constant or the seed. Every reader is publish-only (`grep -rn "dhw_rise_c_per_h\|buffer_rise_c_per_h" custom_components`). The goldens already read `null`.

**Note for PR B. It is not carried, because it is not a measured finding: combi is not reachable yet, so nothing can be measured.** In combi one buffer probe fills both store fields, but the DHW rise input here reads only `CONF_DHW_TEMP_ENTITY`. PR B's `combi_tank_seed` will have to decide whether the combi DHW rise input reads the buffer probe, since it is the same water.

Group carries (roster `R10-COMBI-TANK`, read at `origin/handoff/audit-r10-roster`), one disposition each:
- **Carry 1** (owner ruling 11-06, the no-probe buffer bug): **closed in this PR.** The unprobed buffer is seeded from the previous plan's `buffer_temp_trajectory` through the same seed helper the design adds, `_seed_store` over `_open_loop_plan_value`. PR B reuses that helper for `combi_tank_seed`. Its failing test and its controls are below.
- **Carry 2** (physically sound, general combi-tank types): not reached by PR 0. It adds no heat-transfer path, no tank type and no type branch. The seed is type-agnostic, because it reads whichever trajectory the plan published, so PR A and PR B build on it without a combi special case.
- **Carry 3** (judged on robustness, integration efficiency, architecture and maintainability): answered here as follows:
  - **Robustness.** No reading and no plan leaves the field as it is, never fabricated. The rise inputs are never fed a planned value.
  - **Integration efficiency.** It adds two `InputReader` reads in the same tick and no new coordinator attribute, following the verdict's `observation-read-in-place` note.
  - **Architecture.** One module-level primitive outside the coordinator class. `max_class_loc` and `class_excess_loc` each fall by 1.
  - **Maintainability.** The DHW and buffer seeds share one code path.
- **Carry 4** (web verification of the figures before PR B): binds PR B. PR 0 states no tank figure.
- **Carry 5** (the folded web-verification report): binds PR B, and PR A takes only item 1's UA. PR 0 touches no preset, UA, volume or help text.

## Head

`0ec5d1852cf679730c04e2923a8bbc3a6fafecee`. The merge base is `80016a71f567d936450d8708abcbb79d9e8071d7`, which was origin/main's tip at 2026-11-06T23:29Z. Main moved from the design base `28482ece` during the first gate run. It was merged in, never rebased; that merge brought #3234 (replay-cost tooling, no `custom_components` change). The scoped gate, `ci_predict`, structure and the harness were then re-taken on this head, and prepr.sh was run on it.

## Mutation proof

Each mutant was applied to the head's `coordinator.py`, the new `tests/features.py` block was run (`R10-BUFFER-OPENLOOP` section), and the file was restored:
- **Delete the fix line** (buffer call → `buffer_reading.value if buffer_reading.ok else None`). FAIL: `with no buffer probe the buffer level follows the previous plan's trajectory`; `(wood_seed): with no buffer probe the wood reference hp_tank_temp is the plan's seed`. I also ran this mutant through the whole closure script: `PYTHONPATH=tests/hastub python3 tests/features.py` printed `2 of 4885 FEATURE CHECKS FAILED`. The two failures are exactly those checks.
- **Seed fed to the buffer rise input** (`buffer_temp=ctx._current_state.buffer_tank_temperature`). FAIL: `the observation's rise inputs carry no seed`.
- **DHW seed fed to the DHW rise input.** FAIL: `the observation's rise inputs carry no seed`; `the open-loop DHW seed reaches the state but not the detector's rise input`.
- **`None` to `hp_tank_temp`.** FAIL: all three `wood_seed` checks.
- **Predicate mutated** (`reading.ok` → `False` in `_seed_store`). FAIL: `a buffer probe reading ok wins over the plan (null control)`; `(wood_seed): a buffer probe wins`.

Failing first, at the design base `28482ece`: with the production diff reverted and the tests kept, 4 checks FAIL: the buffer level, the rise inputs, the DHW rise input, and `wood_seed` seed. The 5 controls are ok at both ends.

## Unpinned sites

`tools/pr/ci_predict.py` lists three sites the diff adds. Each one's lane mutant was run against the new `R10-BUFFER-OPENLOOP` block and is killed. Each is pinned by `mutation-autofix` (`ci: pin killed mutants`):
- `custom_components/heatpump_optimizer/coordinator.py:2358 RETURN_DEL` (`_seed_store` returns `None`): 5 FAIL. Among them are the buffer level, the probe null control and the DHW seed.
- `custom_components/heatpump_optimizer/coordinator.py:6581 GUARD_OFF` (the DHW `_seed_store` guard): 1 FAIL, `the open-loop DHW seed reaches the state but not the detector's rise input`.
- `custom_components/heatpump_optimizer/coordinator.py:6583 GUARD_OFF` (the buffer `_seed_store` guard): 4 FAIL. Among them are the buffer level, the probe null control and `wood_seed`.

The stale pin `tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._update_current_state.GUARD_OFF.12569471.json` is deleted by hand, per `ci_predict`'s STALE PIN repair. Its line `if buffer_reading.ok:` no longer exists.

## Null control

- **Probe present.** A buffer probe reading 36.5 °C gives levels 36.5, 36.5 and a buffer rise input of 36.5 at both ends. The install has no DHW probe, so its DHW rise input moves from 55.0, the never-advanced default, to None. That move is the fix, not a drift. With the wood furnace and a 38 °C probe, `hp_tank_temp` reads 38.0 and wood energy is 29.0000 kWh, displacement 0.5312, identical at base and head.
- **Empty trajectory**, which is the no-valve plan. At both ends the level stays 40.0, 40.0. Wood energy is 26.6800 kWh, displacement 0.5000, identical at base and head. `None` is never invented.
- **`solve` with valve `none`.** The solver's buffer seeds read 40.0 ×4 at both ends, because the previous plan published no buffer trajectory.

## Figures

Harness `dev/audit/harnesses/r10_combi_tank.py`, sha1 `7eb9b4b12c2fa83171e8d71fedf0d73b59f2b6eb`, run at base (`80016a71`, the file copied in, `cmp`-identical; the first pass at `28482ece` printed the same lines) and at the head:
`PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_combi_tank.py all`
- `no_probe seed`: base 40.0, 40.0 → head 41.0, 43.0, which is the plan at covering steps 1 and 3. Rise inputs: base (40.0, 55.0) → head (None, None).
- `wood_seed seed`: `hp_tank_temp` base 40.0, 40.0 → head 41.0, 43.0. Wood energy 26.6800 → 23.2000 kWh, displacement 0.5000 → 0.4444. These equal the hand formula against 43 °C, and the test computes and compares them.
- `solve valve=manual`: solver buffer seeds base 40.0, 40.0, 40.0, 40.0 → head 40.0, 42.5, 40.9, 40.3. The first solve has no prior plan.
- Controls, as under Null control: `no_probe probe`, `no_probe empty`, `wood_seed probe`, `wood_seed empty`, `solve valve=none`. Each is identical at both ends.

Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 22 script(s) run, 11 scoped out.` `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh`: `24 TEST SCRIPT(S) PASSED; 10 SCOPED OUT AND NOT RUN`, golden lane `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main`.

Structure: `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED. `max_class_loc` and `class_excess_loc` each moved down by 1 and were re-recorded, with the reason in the commit message: the two seeds collapse into a function outside the coordinator class. Seam map: no coordinator method was added or renamed.

The census rule for the class (step 8): `git grep -n "_open_loop_plan_value(\|_seed_store(" -- custom_components` enumerates every open-loop seed site. Each returned seed site is dispositioned:
- `_seed_store`'s own body: the primitive;
- the DHW and buffer `_seed_store` calls in `_update_current_state`: closed here;
- the slab `_open_loop_plan_value` in the slab-estimate helper (R9, already guarded by the R9 D12-s1-01 slab checks).

The one other plant-state level that has a trajectory is the wood tank (`wood_temp_trajectory`). It is already guarded and is not a never-advanced constant: without a wood probe, `_update_current_state` sets `wood_tank_temperature = None` and falls back to the single-tank abstraction (issue #40).

For the rise-input class, `git grep -n "ExternalHeatObservation(" -- custom_components` names one construction. Its rise inputs are closed here.

## Red checks

- `mutation`: red only on the three unpinned sites the diff adds, listed under `## Unpinned sites`. Each is killed, and `mutation-autofix` pins them by a `ci: pin killed mutants` commit (`ci-autofix.md`). The cheaper detector already exists and ran here: `prepr.sh` step 6d / `tools/pr/ci_predict.py` predicted all three before the handoff, at no standing cost beyond that step. No new detector is owed.

## Forward-carry

none

## Friction

none
