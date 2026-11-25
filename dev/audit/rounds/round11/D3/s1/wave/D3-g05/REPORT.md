# D3-s1 round 11, box D3-g05: full gate for 16 D3.M3 full-net survivors (D3 u1 wave)

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Keys: dev/audit/rounds/round11/D3/s1/wave/D3-g05/keys.tsv (the box's 16 of the wave's 742; every other key belongs to boxes D3-g01..D3-g47).

## Machine and controls

```
nproc: 4
cpu:  Intel(R) Xeon(R) Processor @ 2.10GHz
load1: 0.98
date: 2026-11-22T21:38:37Z
               total        used        free      shared  buff/cache   available
Mem:           16087        1022       13560          12        1802       15065
Swap:              0           0           0
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
python3: /root/venv-ci -> /opt/hpo/venv-ci (symlink made by this box; the image ships venv-ci at /opt/hpo)
--- re-fire resume 2026-11-25T00:46:16Z (new container, same shape)
nproc: 4
cpu:  Intel(R) Xeon(R) Processor @ 2.10GHz
load1: 0.62
               total        used        free      shared  buff/cache   available
Mem:           16087         716       14094          12        1547       15370
Swap:              0           0           0
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
python3: /root/venv-ci -> /opt/hpo/venv-ci (symlink re-made by this box)
```

Null control (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py null`, comment-only marker in tariff.py): gate_rc 1, red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'], fail counts {'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 1, 'python3 tests/harness_headers.py': 3}, wall 3747.6 s, load1 0.76..1.02 (provisional). A mutant is KILLED only when run.sh is red and a script beyond the null fails, or a null-red script prints more FAILs; red with nothing beyond the null is RED-AS-NULL, read as survived.

Procedure: gate_wave.sh (out of tree, on the dispatch ref) drives fullgate.py once per key, one gate at a time, GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1, 4 h cap. Probes ran in a second detached worktree of the baseline (never the gate tree); each recompiles the mutated coordinator method from its own source with the one line replaced and calls it beside the baseline method on the same inputs. Walls and load are provisional; counts and probe values are exact. On the resume (a new container after the first seat stalled at 6 of 16 gates), every probe was re-run once all 16 gates had ended, in the gate tree at the baseline with no gate running: all 16 RESULT lines reproduced exactly, load1/thread_factor/swapins aside.

## Tally

- gated: 16 of 16; RED-AS-NULL 16
- KILLED by script: none
- candidates (gate survivors whose probe moves): 7
- equivalent-candidates: 9
- TIMEOUT: 0

## Gate table

| key | site | patch | verdict | killed_by | class | wall s (prov.) | load1 |
|---|---|---|---|---|---|---|---|
| 0acf3cb312a5b76e | coordinator.py:9849 GUARD_OFF | `if state is None: -> if False:` | RED-AS-NULL | - | equivalent-candidate | 3588.3 | 0.94..0.92 |
| c087dc286eeff014 | coordinator.py:5083 CLAMP_DROP | `max_sample_hours=max(1.0, 1.5 * interval_hours), -> max_sample_hours=(1.0),` | RED-AS-NULL | - | candidate | 3528.9 | 0.86..0.92 |
| 3b458790a543507e | coordinator.py:5248 GUARD_OFF | `if not self._external_heat.suppressing: -> if False:` | RED-AS-NULL | - | equivalent-candidate | 3605.6 | 0.86..0.85 |
| c39bf88e7fd0066f | coordinator.py:5259 CMP_BOUND | `return arr if bool(np.any(arr > 0.0)) else None -> return arr if bool(np.any(arr >= 0.0)) else None` | RED-AS-NULL | - | equivalent-candidate | 3490.6 | 0.88..1.0 |
| 218ac218da41d87d | coordinator.py:5156 CMP_BOUND | `return probe.value > 30.0 -> return probe.value >= 30.0` | RED-AS-NULL | - | candidate | 3532.2 | 0.93..0.92 |
| bcf290164a0edeeb | coordinator.py:5157 GUARD_OFF | `if probe.stale: -> if False:` | RED-AS-NULL | - | candidate | 3613.5 | 0.78..1.0 |
| 375376c4733a1a51 | coordinator.py:5174 RETURN_DEL | `return None -> pass` | RED-AS-NULL | - | candidate | 3356.2 | 0.61..0.94 |
| 2699efc070f5d4e3 | coordinator.py:5176 GUARD_OFF | `if probe.problem != "not_numeric": -> if False:` | RED-AS-NULL | - | candidate | 3316.8 | 0.95..1.0 |
| cc7e5a62ec1ea4d0 | coordinator.py:5182 GUARD_OFF | `if not reading.ok or reading.text is None: -> if False:` | RED-AS-NULL | - | equivalent-candidate | 3325.4 | 0.85..0.92 |
| d05457b7adf4d691 | coordinator.py:7056 GUARD_OFF | `if not weather_entity: -> if False:` | RED-AS-NULL | - | candidate | 3361.7 | 0.78..1.07 |
| d943cc9f7670a834 | coordinator.py:7069 BOOLOP | `if result and weather_entity in result: -> if result or weather_entity in result:` | RED-AS-NULL | - | candidate | 3352.8 | 0.77..0.92 |
| 894b4e70a336f8fa | coordinator.py:10188 GUARD_OFF | `if not trajectory: -> if False:` | RED-AS-NULL | - | equivalent-candidate | 3462.1 | 0.85..0.92 |
| 2d6701afc323e1e8 | coordinator.py:10192 CMP_BOUND | `if 0 < idx < len(trajectory): -> if 0 <= idx < len(trajectory):` | RED-AS-NULL | - | equivalent-candidate | 3550.9 | 0.79..0.92 |
| 8cfd8cf0d8a58c83 | coordinator.py:10192 CMP_BOUND | `if 0 < idx < len(trajectory): -> if 0 < idx <= len(trajectory):` | RED-AS-NULL | - | equivalent-candidate | 3682.7 | 0.92..0.92 |
| e02e1ac8cc0b714a | coordinator.py:10223 GUARD_OFF | `if not trajectory: -> if False:` | RED-AS-NULL | - | equivalent-candidate | 3630.4 | 0.78..0.92 |
| ba1c58ad6dabbebd | coordinator.py:10231 CMP_BOUND | `if 0 < idx < len(trajectory): -> if 0 <= idx < len(trajectory):` | RED-AS-NULL | - | equivalent-candidate | 3723.8 | 0.86..0.92 |

## Survivors: the step-4 answer per key

**0acf3cb312a5b76e** coordinator.py:9849 GUARD_OFF `if state is None: -> if False:` (RED-AS-NULL, equivalent-candidate). Equivalent: with the guard off, getattr(None, 'attributes', None) or {} and getattr(None, 'state', None) return exactly the guard's (None, {}); no input separates the arms (moved_inputs=0). Probe: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_0acf3cb312a5b76e.py`: baseline (None, {}) for an absent entity; mutant (None, {}). Inputs tried: sensor.absent; sensor.present (state 'on', attrs); attribute-less state object; ''; None. Should have failed: none: no assertion can separate the arms; traced by tests/config_flow_steps.py and tests/features.py.

**c087dc286eeff014** coordinator.py:5083 CLAMP_DROP `max_sample_hours=max(1.0, 1.5 * interval_hours), -> max_sample_hours=(1.0),` (RED-AS-NULL, candidate). Moves: at optimization_interval 61/90/120 min max_sample_hours drops 1.525/2.25/3.0 -> 1.0 and the external-heat detector, fed a DHW tank rising 4 C/h with the compressor off once per interval, never turns on (suppressing True -> False); 16 of the config flow's 23 interval settings change the window. Probe: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_c087dc286eeff014.py`: baseline max_sample_hours 2.25 h, detector suppressing True at a 90-min interval; mutant 1.0 h, suppressing False. Inputs tried: optimization_interval 10..120 step 5 (23 values); detector at 30, 60, 61, 90, 120 min. Should have failed: tests/features.py (traced at line 5083; also block_duty, boost_drift_replay, config_flow_steps, doc_claims, entities, finite_boundary, manual_plan, solar_alignment): no check builds _external_heat_config at an interval above 40 min and asserts max_sample_hours = 1.5 * interval, nor drives the detector at a >60-min sampling interval.
Candidate (id assigned at consolidation): *No check pins _external_heat_config's sample window above a 40-min interval; the 1 h clamp is unseen*; severity medium; class_guess I1; metric: ExternalHeatDetector.suppressing after 4 interval-spaced samples of a 4 C/h DHW rise, compressor off, at optimization_interval 90 min; perturbation direction down, observed suppressing False (max_sample_hours 1.0); null: interval 30 min (default) and 60 min: max_sample_hours 1.0 and suppressing True in both arms.

**3b458790a543507e** coordinator.py:5248 GUARD_OFF `if not self._external_heat.suppressing: -> if False:` (RED-AS-NULL, equivalent-candidate). Equivalent: free_heat_kw is zeroed by _update_displacement whenever the detector is neither active nor fading (external_heat.py:355-357) and by _reset, so with suppressing False forecast_free_heat returns all zeros and line 5259 returns None in both arms (moved_states=0); the positive arm (suppressing, displacement 0.5) sums 11.25 kW in both. Probe: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_3b458790a543507e.py`: baseline None in 4 non-suppressing states; mutant None in the same 4. Inputs tried: fresh detector; fire on, then off for 5 h (decay over); fire on, then detection disabled (_reset); override off. Should have failed: none: no detector state separates the arms; traced by tests/config_flow_steps.py, tests/entities.py, tests/features.py.

**c39bf88e7fd0066f** coordinator.py:5259 CMP_BOUND `return arr if bool(np.any(arr > 0.0)) else None -> return arr if bool(np.any(arr >= 0.0)) else None` (RED-AS-NULL, equivalent-candidate). Reachable but equivalent at the output: the probe executes line 5259 through production states (the user's override flag on with free heat 0), and the symbol's return moves None -> an all-zero array of 96 (moved_at_symbol=2), but its only reader, optimizer._horizon_weather (optimizer.py:3046-3050), maps an all-zero series to None, so the solve sees identical input (moved_at_solve_input=0). The line is reachable, not dead; no traced baseline executes it. Probe: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_c39bf88e7fd0066f.py`: baseline None (symbol); None (solve input); mutant zeros[96] (symbol); None (solve input). Inputs tried: override on, no wood/outlet probes (displacement 0); override on, wood tank below the pump tank + margin. Should have failed: none at the observable output; a direct unit check on _external_heat_forecast's return (None for an all-zero forecast) would separate the arms, but no consumer behaviour depends on it.

**218ac218da41d87d** coordinator.py:5156 CMP_BOUND `return probe.value > 30.0 -> return probe.value >= 30.0` (RED-AS-NULL, candidate). Moves at the boundary only: a fresh flue probe reading exactly 30.0 C gives override False on the baseline and True under the mutant (moved_inputs=1); 29.9, 30.1 and 400 C are unchanged. Probe: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_218ac218da41d87d.py`: baseline override False at 30.0 C; mutant override True at 30.0 C. Inputs tried: 29.9 C; 30.0 C; 30.1 C; 400 C. Should have failed: tests/features.py ('a flue probe still uses its own threshold, not the shared numeric rule', features.py:3366) checks 45 and 20 C only; no case at the 30.0 C boundary.
Candidate (id assigned at consolidation): *No check pins the flue-probe threshold at exactly 30.0 C; > -> >= in the override is unseen*; severity low; class_guess I1; metric: _external_heat_override's return for a fresh numeric flue probe reading 30.0 C; perturbation direction up, observed True; null: 29.9, 30.1 and 400 C: identical in both arms.

**bcf290164a0edeeb** coordinator.py:5157 GUARD_OFF `if probe.stale: -> if False:` (RED-AS-NULL, candidate). Moves in the log only: with the stale branch skipped, a stale flue probe still returns None (problem 'stale' != 'not_numeric' returns at line 5178) but the once-per-outage warning is never logged (1 -> 0 over 4 cycles). Probe: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_bcf290164a0edeeb.py`: baseline 1 warning over 4 stale cycles, value None; mutant 0 warnings, value None. Inputs tried: stale flue probe (120 min old, limit 60) over 4 cycles; untimestamped fresh probe (null). Should have failed: tests/features.py ('a flue PROBE that stopped reporting stops suppressing (v5.3.0)', features.py:3319) asserts the None value only; nothing asserts the stale warning is logged once.
Candidate (id assigned at consolidation): *No check asserts the stale flue-probe warning is logged; disabling the stale branch is unseen*; severity low; class_guess I1; metric: _LOGGER.warning calls from _external_heat_override over 4 cycles of a flue probe 120 min stale (limit 60); perturbation direction to_zero, observed 0; null: an untimestamped (fresh) probe: (True, 0 warnings) in both arms.

**375376c4733a1a51** coordinator.py:5174 RETURN_DEL `return None -> pass` (RED-AS-NULL, candidate). Moves in the log: deleting the stale branch's return lets execution reach line 5175, which re-arms the latch every cycle, so a stale probe logs its warning every cycle (1 -> 4 over 4 cycles); the value stays None (line 5178 returns). Probe: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_375376c4733a1a51.py`: baseline 1 warning over 4 stale cycles, value None; mutant 4 warnings, value None. Inputs tried: stale flue probe (120 min old, limit 60) over 4 cycles; untimestamped fresh probe (null). Should have failed: tests/features.py (features.py:3319 stale-probe check; traced at line 5174 only by features.py) asserts the None value but not the once-per-outage latch (_external_probe_stale_warned).
Candidate (id assigned at consolidation): *No check pins the stale flue-probe warning to once per outage; the return deletion floods the log*; severity low; class_guess I1; metric: _LOGGER.warning calls from _external_heat_override over 4 cycles of a flue probe 120 min stale (limit 60); perturbation direction up, observed 4; null: an untimestamped (fresh) probe: (True, 0 warnings) in both arms.

**2699efc070f5d4e3** coordinator.py:5176 GUARD_OFF `if probe.problem != "not_numeric": -> if False:` (RED-AS-NULL, candidate). Moves: a flue probe reporting a value outside FLUE_RANGE_C (-70..1000 C), e.g. a DS18B20's -127 C lost-bus code, is classed 'implausible' by read(); the baseline returns None, the mutant re-reads it as text and parse_bool's non-zero rule calls it a fire: override None -> True (moved_inputs=2). Unconfigured, missing, unavailable and unknown stay None. Probe: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_2699efc070f5d4e3.py`: baseline override None for a -127 C or 1500 C flue reading; mutant override True. Inputs tried: not configured; missing entity; unavailable; unknown; -127 C; 1500 C; word 'on'; 20 C. Should have failed: tests/features.py ('an unavailable or unconfigured override is simply absent', features.py:3390) covers unavailable and None only; no case feeds an implausible numeric flue reading.
Candidate (id assigned at consolidation): *No check feeds the override an implausible flue reading; dropping the not_numeric guard reads -127 C as a fire*; severity medium; class_guess I1; metric: _external_heat_override's return for a fresh flue probe reading -127 C; perturbation direction up, observed True; null: not_configured, missing, unavailable, unknown: None in both arms; 'on' True and 20 C False in both.

**cc7e5a62ec1ea4d0** coordinator.py:5182 GUARD_OFF `if not reading.ok or reading.text is None: -> if False:` (RED-AS-NULL, equivalent-candidate). Equivalent: line 5182 is reached only when read() classed a present, valued state 'not_numeric', and read_state with UNBOUNDED on the same state then has no age limit and no 'valid' filter, so reading.ok is True and text is set; parse_bool returns what the baseline would (moved_inputs=0 of 10). Probe: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_cc7e5a62ec1ea4d0.py`: baseline per-state override identical; mutant identical. Inputs tried: 'on'; 'off'; 'burning?'; ''; '  '; 'on' 14 days old; 'on' stamped 2 h in the future; '400' with an unknown unit; unavailable; not configured. Should have failed: none: no state reaching the line separates the arms; traced by tests/features.py only.

**d05457b7adf4d691** coordinator.py:7056 GUARD_OFF `if not weather_entity: -> if False:` (RED-AS-NULL, candidate). Moves: with no weather entity configured the mutant calls weather.get_forecasts with entity_id None (calls 0 -> 1) and logs 'No forecast data returned for None' instead of 'No weather entity configured'; the outage latch counts once in both. Probe: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_d05457b7adf4d691.py`: baseline 0 service calls; warning 'No weather entity configured'; mutant 1 weather.get_forecasts call with entity_id None; warning 'No forecast data returned for None'. Inputs tried: weather_entity ''; weather_entity None; '' with a get_forecasts handler registered; configured entity (null). Should have failed: tests/features.py / tests/entities.py / tests/manual_plan.py (traced at line 7056) always configure weather_entity; no check fetches with it unset and asserts no service call.
Candidate (id assigned at consolidation): *No check fetches the weather forecast with no weather entity; the guard's removal calls the service with None*; severity low; class_guess I1; metric: weather.get_forecasts calls made by one _fetch_weather_forecast with weather_entity unset; perturbation direction up, observed 1; null: a configured entity returning an empty forecast: identical in both arms.

**d943cc9f7670a834** coordinator.py:7069 BOOLOP `if result and weather_entity in result: -> if result or weather_entity in result:` (RED-AS-NULL, candidate). Moves: when the response lacks the configured entity (or is None) and no forecast is held, the mutant raises KeyError/TypeError inside the try, so the except branch fabricates the flat 48 h trajectory from the entity's current state (held rows 0 -> 48); the baseline takes the else branch and holds nothing (moved_held_rows=2). Probe: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_d943cc9f7670a834.py`: baseline 0 held rows, else branch ('No forecast data returned'); mutant 48 fabricated rows (except branch). Inputs tried: response holding only another entity; response None; response {}; forecast already held (null). Should have failed: tests/features.py ('a failed weather fetch latches the outage and marks the forecast stale', features.py:41558) returns None with no weather-entity state, so the except branch has nothing to fabricate from; it lacks an assertion that a no-data reply with a live entity holds no fabricated forecast.
Candidate (id assigned at consolidation): *No check sends a forecast reply lacking the entity with a live weather state; and->or fabricates a flat forecast*; severity medium; class_guess I1; metric: rows in _weather_forecast after one fetch whose reply lacks the configured entity, nothing held, weather entity state live; perturbation direction up, observed 48; null: reply {} and a held forecast: rows identical in both arms.

**894b4e70a336f8fa** coordinator.py:10188 GUARD_OFF `if not trajectory: -> if False:` (RED-AS-NULL, equivalent-candidate). Equivalent on reachable inputs: with the guard off an empty list loops with 0 < idx < 0 false and files nothing; only None separates (TypeError), and OptimizationResult's one constructor (optimizer.py:3899) always delivers a list ([] or tolist()). Probe: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_894b4e70a336f8fa.py`: baseline 0 leads for [] and [x]; 5 for the solved 97; mutant identical; None raises TypeError. Inputs tried: []; None; [50.0]; the solved 97-point list. Should have failed: none: no reachable input separates the arms; traced by config_flow_steps, entities, features.

**2d6701afc323e1e8** coordinator.py:10192 CMP_BOUND `if 0 < idx < len(trajectory): -> if 0 <= idx < len(trajectory):` (RED-AS-NULL, equivalent-candidate). Equivalent in production: dt_h = max(time_step_minutes, 1)/60 with time_step_minutes a fixed 15 (OptimizationConfig default, never assigned), so the smallest lead (1 h) rounds to idx 4 and idx 0 never occurs (moved 0 of 201 lengths); only an off-grid 3 h step separates (4 -> 5 leads). Probe: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_2d6701afc323e1e8.py`: baseline DHW leads identical over lengths 0..200 at dt_h 0.25; mutant identical; off-grid dt 3 h: 4 -> 5. Inputs tried: trajectory lengths 0..200 at the production dt_h 0.25; off-grid control dt_h 3.0. Should have failed: none reachable: the distinction needs a step over 2 h, which no configuration produces.

**8cfd8cf0d8a58c83** coordinator.py:10192 CMP_BOUND `if 0 < idx < len(trajectory): -> if 0 < idx <= len(trajectory):` (RED-AS-NULL, equivalent-candidate). Equivalent in production: the mutant only differs (IndexError) when len(trajectory) equals a lead index [4, 12, 24, 48, 96]; every solve's trajectory is n_steps + 1 = 97 because _forecast_arrays pads every series to n_steps = 96 and extend_price_series fills the price horizon, so no reachable length separates. Probe: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_8cfd8cf0d8a58c83.py`: baseline 5 leads at the solved length 97; mutant 5 leads; IndexError only at lengths 4/12/24/48/96. Inputs tried: trajectory lengths 0..200 at dt_h 0.25; the solved length 97. Should have failed: none reachable: the trajectory length is fixed at 97.

**e02e1ac8cc0b714a** coordinator.py:10223 GUARD_OFF `if not trajectory: -> if False:` (RED-AS-NULL, equivalent-candidate). Equivalent at the output: with the guard off an empty trajectory reaches note_promise (calls 0 -> 1), but plan_promise returns None for len(room)-1 < 1 (accuracy.py:554-556), so no promise is kept and no lead is filed (moved_kept_records=0); the solved trajectory keeps 1 promise and 5 leads in both arms. Probe: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_e02e1ac8cc0b714a.py`: baseline empty room trajectory: 0 leads, 0 promises kept; mutant note_promise called once, still 0 promises kept. Inputs tried: []; [21.0]; the solved 97-point list at PROMISE_HOUR. Should have failed: none at the observable output; traced by config_flow_steps, entities, features.

**ba1c58ad6dabbebd** coordinator.py:10231 CMP_BOUND `if 0 < idx < len(trajectory): -> if 0 <= idx < len(trajectory):` (RED-AS-NULL, equivalent-candidate). Equivalent in production: time_step_minutes is a fixed 15, so the 1 h lead rounds to idx 4 and idx 0 never occurs (moved 0 of 201 lengths); only an off-grid 180-min step separates (4 -> 5 leads). Probe: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes/probe_ba1c58ad6dabbebd.py`: baseline room leads identical over lengths 0..200 at dt_h 0.25; mutant identical; off-grid 180-min step: 4 -> 5. Inputs tried: trajectory lengths 0..200 at the production dt_h 0.25; off-grid time_step_minutes 180. Should have failed: none reachable: the distinction needs a step over 2 h, which no configuration produces.

## Coverage

D3.M3 (this box): enumerator `awk -F'\t' '$6=="gate"' SURVIVORS.tsv`, universe 742, examined 16, not reached 46 groups (every other key, by box; TIMEOUTs by name). D3.M1, D3.M2, D3.M4, D3.M5 and their redispatched C-items are carried verbatim from REPORT-D3-u1b.json.

## Findings

None numbered here: findings: []. The candidates above are returned under `gate_survivors` for the orchestrator's consolidation to number.

## Unfinished

- none

## Exposure

None (no docs/ or GitHub records read). Other boxes' dispatch refs were read for their keys.tsv only, to name not_reached by box.

