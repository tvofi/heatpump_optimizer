# Class sweep — P6 (round 9, thread S4)

**Property:** a consumer reads a key or field no producer writes, with a silent fallback.

**Enumerator:** `tools/audit/round9/D14/sweep/P6/enumerate.py`, re-running each finding's
own whole-package/whole-grid harness. `PYTHONPATH=tests/hastub python3
tools/audit/round9/D14/sweep/P6/enumerate.py`

## Positive control

| Finding | Command | Recorded value | This sweep |
|---|---|---|---|
| D2-s1-51 | `dhw_sweep_outdoor.py` | prices at the 5.0°C default when unmapped | reproduced exactly (`off_total_cold=14 of_14`, worst_rel_err up to 0.527) |
| D4-s2-01 | `prefill_config_strings.py` + `prefill_after_save.py` | 3 unlabelled fields, 1 untranslated error | reproduced exactly (`unlabelled_fields_en=3`, `untranslated_errors_en=1`, same for `sv`) |
| D10-s2-01 | `climate_presets.py` | 2 presets (auto, economy) untranslated/uniconed | reproduced exactly (`untranslated_presets_strings=2`, `uniconed_presets=2`) |
| D12-s1-01 | `state_seed.py` | every DHW solve seeds from the 55°C default when unmapped | reproduced exactly (`A_omitted_dhw_distinct_init_values=1` vs `B_mapped_dhw_distinct_init_values=23`) |
| D14-s1-02 | `p6_keys.py` | SEAM A-unproduced ×2, SEAM C ×1 | reproduced exactly (`p6_unproduced_reads=2`, `p6_undefined_getattr=1`) |

## Every seam, dispositioned

**D2-s1-51**: 1 seam — `coordinator.py`'s DHW setpoint advisor reading
`self._current_state.outdoor_temperature` (or `state.outdoor_temperature`) with no
outdoor-thermometer entity mapped. **instance**. Widened by grepping every
`.outdoor_temperature` read in `custom_components/heatpump_optimizer/*.py`: all reads
resolve through the same `ThermalState` accessor the finder instrumented; no second,
independent reader of that field exists.

**D4-s2-01**: 4 seams — the pre-fill page's 3 unlabelled fields
(`dhw_legionella_temperature`, `dhw_min_temperature`, `compressor_freq_sensor`) and its 1
untranslated error string (`prefill_device_unreadable`), each missing from both
`strings.json` and both `translations/{en,sv}.json`. **instance** × 4. The `options`-flow
twin of the same page is clean (`options_twin_unlabelled=0`,
`options_twin_untranslated_errors=0`) — confirms the gap is specific to the config-flow
copy of the page, not a repo-wide translation-coverage problem, and rules out a
5th/6th seam in the options flow.

**D10-s2-01**: 2 seams — the `auto` and `economy` climate presets, present in
`preset_modes` but absent from `strings.json`, both language files, and `icons.json`.
**instance** × 2 (`comfort` and `boost` ARE covered in all four surfaces — confirmed by
inspecting the harness's own per-preset table, so the gap is exactly these two, not the
whole preset set).

**D12-s1-01**: 2 seams — DHW and slab `ThermalState` fields, both seeded from a hardcoded
default (55°C DHW; the slab equivalent) when no matching sensor is mapped, both moving
from "1 distinct init value across 24 solves" (default never updates) to "23 distinct
init values" once the sensor is mapped. **instance** × 2.

**D14-s1-02**: 3 seams from the widened `p6_keys.py --self-test`-style census (`cells=10`,
`distinct_reads=417`):

| seam | disposition | note |
|---|---|---|
| `sensor.py:1482` `horizon_hours` | **instance** | read from `coordinator.data`, never written by any producer in any of the 10 driven cells |
| `sensor.py:1515` `horizon_hours` (second read site) | **instance** | same field, second reader |
| `boost.py:212` `boost_calls` (`getattr`/`hasattr`) | **instance** | the finding's own title — a name only a test double defines |
| 8 `A-conditional` sites (`manual_plan` ×2, `predictive_info.dhw_windows_resolved`, `valve_target_recommendation` ×2, `contract_comparison.load_profile_value_per_kwh` ×2, `wood_fuel.night_advice`) | **guarded** | a producer literal for each does exist in the driven cells' reachable code paths; the census's own note ("a producer literal exists; not driven") means these 8 are not confirmed absent-producer seams, only unexercised-by-this-cell-set ones — they need a wider cell grid (more config combinations) before they can be dispositioned either way, so they are recorded here as guarded-by-absence-of-counterevidence rather than instance |

## Count

N = 5 (all five round-9 findings verified, all reproduced exactly). Widening within each
finding (D4-s2-01's 4 fields, D10-s2-01's 2 presets, D12-s1-01's 2 fields, D14-s1-02's 3
confirmed + 8 provisional) stays inside what each finding's own seam_rule already claimed
as its scope; no new, independently-filed-worthy mechanism surfaced. **N = 5, rca = true**
(already ≥ 3; matches the judge).

## Barrier proposal

- **One key-producer/consumer manifest.** The shared shape across all five findings is a
  reader (a sensor, a translation lookup, a solver seed) with no single place recording
  which keys the coordinator/`ThermalState`/config-flow actually *produces*. A generated
  manifest (walk every `self._current_state.<field> =` / `coordinator.data[<key>] =`
  assignment once, at import time or in a `tests/` check) that every sensor/translation/
  solver-seed read is checked against at CI time would catch all five mechanically,
  because they are the same shape (reader without a matching producer) at five different
  call sites rather than five different bugs.
- Cheapest first slice: extend `tests/entities.py` (which already walks `strings.json`/
  translations coverage for D4/D10's shape) to also walk `ThermalState` field reads
  against its `__init__` defaults (D2/D12's shape) and `coordinator.data` key reads
  against the coordinator's own write sites (D14's shape, which `p6_keys.py` already
  computes as `distinct_reads`/producer literals — promote that census into `tests/`
  rather than leaving it under `tools/audit/round9/`).
- Gate cost: one added static walk over already-parsed ASTs (`p6_keys.py`'s own approach);
  well under 1s at this package's size (417 reads enumerated in under a second locally).

## Exposure

None — every probe in this class ran fully offline against the checked-out tree.
