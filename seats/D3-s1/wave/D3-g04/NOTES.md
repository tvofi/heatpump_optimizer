# D3-g04 preliminary per-key notes (probe class if the gate SURVIVES; KILLED/TIMEOUT override)

- 466c95cb8978ea1d: candidate -- No check drives smart_write with no valve write entity; dropping the guard turns a DEBUG skip into a WARNING
- a7dd3153718e531b: candidate -- No check feeds _confidence_margins a damping in (0, 1e-9]; removing its early None is unseen
- b6b6e82fb4a33703: equivalent-candidate -- none reachable: the arms differ only at damp == 1e-9 exactly, which 1.0 - trust() cannot produce (granularity 2**-53 near 1).
- 10ba5036744c9a99: equivalent-candidate -- none reachable: OptimizationConfig.time_step_minutes is never assigned outside its 15.0 default (optimizer.py:2667), so max(step, 1.0) is the identity on every production input.
- 7457d714cd44306c: candidate -- No check makes a confidence margin exactly 1e-9; the `>` -> `>=` swap in its None test is unseen
- 6aeb83e5435c9cac: candidate -- No check books a grid-fee line before reading the contract comparison; dropping grid_fee_sek is unseen
- d06a2d8e53342785: candidate -- No check records a spot mean before the contract comparison; the monthly-average contract can vanish unseen
- 9789e0e7faa1b53a: equivalent-candidate -- none: at kwh == 0 both other contracts are gated on kwh > 0, so costs holds hourly_spot alone and len(costs) > 1 is false on both arms.
- 8b4f4adbf55981bc: equivalent-candidate -- none reachable: _weather_forecast is a list from __init__ (coordinator.py:3725) and only ever assigned a non-empty list (7076) or a fabricated one (7111); on [] the loop runs zero times and returns No
- c555c1a38da31dde: equivalent-candidate -- none reachable: the inlet production resolves is at most 35 C (options 25 + 8 seasonal; a live probe above 35 C is refused by _dhw_inlet_c), so 40 - inlet >= 5 and the boundary at 1.0 is never met.
- ff67ca31aba14e7f: equivalent-candidate -- none reachable: as for c555c1a38da31dde, the resolved inlet never exceeds 35 C, so the guard is never taken in production.
- 201955bf671ce8aa: equivalent-candidate -- none through the options flow: shower_flow_lpm's selector bounds it to 4..20 (config_flow.py:1811). EntryConfig itself (entry_config.py:193) parses it with finite_float alone, so a stored 0 from outsi
- faf822994582adfc: candidate -- No check sets the DHW minimum above the lowest sweep candidate; dropping the usable-energy clamp moves the advice unseen
- feed2751f4116bd1: candidate -- No check ties a sweep candidate's usable energy to the heaviest window; `>=` -> `>` moves the advice unseen
- 29bad645ca2c2438: candidate -- No check pins the sweep's tie-break; `<` -> `<=` hands a cost tie to the hotter setpoint unseen
- 640a1a68b6c1eb23: candidate -- The _entity_state 'before any lookup' check cannot see a lookup; removing the guard is unseen and raises under HA's states contract
