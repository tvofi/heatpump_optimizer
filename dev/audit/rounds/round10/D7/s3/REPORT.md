# D7-s3 — round 10, D7.M6 (dead code), baseline 17f1c55fad1b, box B5

Cells: D7.M6 over `**` (deep). Box load1 was 37–140 throughout (shared fan-out);
every number below is a count, contention-immune.

## Method
1. Re-read the ratchet's own dead-code screens (`tests/structure.py:dead_members`,
   dead_symbols) rather than re-deriving: dead_methods=0, dead_top_level_symbols=1
   (`const.py:ENTITY_FAMILY_OVERRIDES`, consumed only by `tests/entities.py`, budgeted).
   The screen prints a **name-kept** set it cannot measure: 152 members.
2. Runtime sentinel over all 152 name-kept members (`namekept_sentinel.py`): every member
   wrapped, calls counted by whether the immediate caller frame is production code; driven by
   the five golden coordinator captures and the whole of `tests/features.py` (4107 checks).
   56 members got 0 production-frame calls; 10 of those got test calls.
3. Of the 10, four are HA hooks or live by inspection (`climate.target_temperature`,
   `DebugFinalizeButton.available`, `DefrostDerate.observe` at coordinator.py:9711,
   `LegionellaGuard.async_load` passed as a callable at coordinator.py:2635). Six have no
   production load of their name on an instance of their class: `namekept_receivers.py`
   lists every production load site and its receiver.
4. Card JS (not covered by any ratchet): `card_dead_fn.mjs` counts top-level function
   declarations with no bare reference and confirms at runtime with a vm-global sentinel.

## Findings
- **D7-s3-01** six dead production members hidden by the name-kept rule:
  `Cusum.reset` (only `.reset()` loads are on `_comfort_learner`/`_freq_watchdog`),
  `InputReader.value/text/flag` (every load is on a `Reading`), `BoostState.as_dict`
  (state is in-memory only; every `.as_dict` load is on another learner),
  `HeatPumpOptimizerCoordinator.dhw_temperature` (every load is on a `ThermalState`).
  Each is exercised by tests only, so it passes tests and the ratchet reports dead_methods=0.
- **D7-s3-02** card `textWidth` (heatpump-optimizer-card.js:3031) is dead: 0 bare
  references, 0 runtime calls while a full plan view renders (control fmtTick: 39 calls), and
  the `setupTextW` doc comment (:2156) says the chart still uses it. No dead-code instrument
  covers the card.

## Non-findings
- No production def/class is unreferenced by name outside HA hooks (`scan.py`).
- No production module is unimported (process_worker.py runs as a script path, coordinator.py:1317).
- The four `CONF_*` constants unreferenced by name are `DYNAMIC_REFERENCES`, re-checked each run.
- Card class methods: none is unreferenced apart from the custom-element lifecycle hooks.

## Harnesses
`scan.py`, `namekept_sentinel.py`, `namekept_receivers.py`, `card_dead_fn.mjs` + `card_dead_fn.sh`.

## Unfinished
None for M6. The 46 name-kept members with neither production nor test calls were not typed
one by one (most are HA `available` hooks and Protocol stubs); they are the next round's residue.

## Exposure
None. Side note: `tests/features.py` fails one check in the export (`recorded_at = 'unknown'`)
because the export has no `.git`. That comes from the environment, not from a defect.
