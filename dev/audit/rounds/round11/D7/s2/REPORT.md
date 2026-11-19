# Round 11 — D7 seat s2 (steps D7.M2, D7.M3, D7.M4)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`, box B5, `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3`
from the export root. Cells: `check_scopes.py --seat D7-s2` printed 95 lines, `M2+M3+M4 × every
custom_components/heatpump_optimizer/*.py`. Each step's universe is its own enumerator's, written and
committed here, and each one scans the whole package or reads production. Every number below is a count
or a ratio. No timing number is a finding. Exposure: none.

## Method and coverage

| step | enumerator | universe | examined | not reached |
|---|---|---|---|---|
| D7.M2 | `enum_m2.py` (the shipped presets in `tests/stress.py` BUILDINGS) | 3 | 3 | — |
| D7.M3 | `enum_m3.py` (each persisted learner, mapped from a real coordinator's `_learner_snapshot_payloads`; an unmapped key fails the run) | 21 | 21 | — |
| D7.M4 | `enum_m4.py` (AST: optimizer per-solve state, context bindings held across an await, in-place writes into context members) | 17 | 17 | — |

**Redispatched C1 (D7.M3): examined.** All 21 learners are now driven end to end through their own
production entry on a real coordinator, under each of window, pumps, external heat, defrost and away.
Each learner also has a clean null arm, and the null arm ingests in 21 of 21 cases. The table includes
`dhw_learning`'s `_frozen`: the coordinator's `functools.partial(_learning_frozen, room_air=False)`,
driven through `async_learn_dynamics`. It also includes `comfort_learner`, driven through
`_record_quiet_comfort_period`.

## Findings

- **D7-s2-01 (M3, medium, bug).** Away does not freeze any of three occupancy-borne learners:
  - The internal-gains profile, the DHW draw statistics and the comfort quiet evidence all keep learning
    while away. The curve learner is the only one that checks away.
  - `contaminated_ingest=3`. The away freeze in `_learning_frozen` (applied as `--perturb`) brings it to 0.
  - Consequences measured by `m3_away_drift.py` after a 14-day absence:
    - The gains profile mean falls to 0.69 g0 when half the free heat comes from the occupants, and to 0.38 g0 when all of it does.
    - 14 of the 40 occurrences in each DHW window are empty-house occurrences. At 14 days the p90 has not moved.
    - At 28 days, 28 of 40 occurrences are empty-house ones and the p90 is 11–12 % lower.
    - The comfort cell ingests, but on a real away plan the plan is not flat, so it books no consequence.
- **D7-s2-02 (M2, medium, bug).** The production two-state fit admits biased fits on the configured free-heat prior:
  - When the true free heat is far above the configured prior, `adoption_decision` admits:
    - heavy_old at +0.8 kW: UA 11.5 % low;
    - typical_slab at +0.5 kW: 12.9 % low;
    - typical_slab at +0.8 kW: 21.1 % low.
  - That is 3 of 57 cells. Widening `SLAB_INTERCEPT_PRIOR_SD_KW` to 0.3 brings it to 0.
  - The design answers this with the learned night profile, and the R9-P5 sweep in `tests/features.py` only checks the `learned=True` arm.
  - But internal-gains learning is off by default (`DEFAULT_INTERNAL_GAINS_LEARNING_ENABLED=False`).
  - Effect after blending into the house heat-loss scale: up to −7.1 %.
- **D7-s2-03 (M4, low, hygiene).** `CoordinatorContext` is not write-once for `_opt_config`:
  - `async_set_target_temperature` and `_apply_comfort_weight` assign in place.
  - Every context ever published shares that one `OptimizationConfig`, so a superseded context sees 2 fields change.
  - Publishing a replaced config brings it to 0.
  - `_thermal_params`, `_current_state` and `_config` do keep the promise.

## Non-findings

These are in `REPORT.json`.
- **Statefulness and order:**
  - A second terminal-cost call gives the same value, delta 0.
  - A reused optimizer solves exactly as a fresh one: 0 of 5 pairs differ.
  - No holder that captured the context before an await writes it back after the await: 0 of 8 sites.
- **Learner freezes:**
  - Window, pumps, external heat and defrost: no contaminated ingest, apart from the passes the design intends.
  - The curve learner freezes on away.
- **Sysid:**
  - Slab-pair and noise mismatches are refused or adopted within the bar.
  - The first-order fit admits nothing.
- **Over-freezes:** the defrost derate freezes on ventilation, and the DHW learner freezes on a space boost. These pause a learner but do not contaminate it.

`last_buffer_trajectory` no longer exists. Its successor, `_initial_buffer_temp`, cannot move the
terminal cost in any of the 9 shipped buffer scenarios (`seed_binding_scenarios=0`), because the
ceiling already equals `buffer_max_temperature`. The order coupling is therefore latent: no scenario
shows it. This is recorded as a harness gap: `--perturb-stash` does not move any count.

## Harnesses (each runnable by the command in its header)

`enum_m2.py`, `enum_m3.py`, `enum_m4.py`, `m2_sysid_plant.py`, `m3_learner_freeze.py`,
`m3_away_drift.py`, `m4_order_context.py`.

## Leads

The lead is outside these cells, so it has no harness here.

- `thermal_model.py` `ThermalParameters.from_config`: `two_zone_mode` `auto`, the default, is handled in the same branch as `on`.
- So `from_config({})` returns `two_zone_enabled=True`.
- `const.py` says `auto` keeps the presence rule, but that rule is now reached only for unknown values.
- Owner: unknown.

## Unfinished

None.
