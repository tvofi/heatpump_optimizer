import json, sys
P = "dev/audit/rounds/round11/D3/s1/wave/D3-g05/probes"
M = "box D3-g05 cloud (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14)"
S = "custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator."
H = {
 "0acf3cb312a5b76e": ("the (state, attributes) pair _entity_state returns per entity id; moved_inputs = ids whose pair differs between arms",
   "moved_inputs=0 count (every input identical: getattr(None, ..., None) reproduces the guard's (None, {}))",
   "_entity_state (line 9849 `if state is None:`)", "`if state is None:` -> `if False:` (mutant 0acf3cb312a5b76e)",
   "inputs absent, present-with-attributes, attribute-less object, '' and None; '' and None return at line 9847 in both arms"),
 "c087dc286eeff014": ("ExternalHeatConfig.max_sample_hours _external_heat_config delivers per optimization_interval (10..120 min, step 5, the config flow's range) and whether ExternalHeatDetector.suppressing turns on for a DHW tank rising 4 C/h with the compressor off, sampled once per interval (4 samples)",
   "interval 61/90/120 min: max_sample_hours 1.525/2.25/3.0 -> 1.0 and detector suppressing True -> False; intervals_moved=16 of 23",
   "_external_heat_config (line 5083), consumed by external_heat.ExternalHeatDetector._rate (external_heat.py:216)",
   "`max_sample_hours=max(1.0, 1.5 * interval_hours),` -> `max_sample_hours=(1.0),` (mutant c087dc286eeff014); direction: window shrinks to 1 h, detector blind past 60 min",
   "interval 30 min (the default) and 60 min: both arms 1.0 h and suppressing True (null: max(1, 1.5*0.5)=1.0; at 60 min dt=1.0 is not > 1.0)"),
 "3b458790a543507e": ("whether _external_heat_forecast returns None or an array, over detector states reached through ExternalHeatDetector.update with suppressing False; moved_states = states whose return differs",
   "moved_states=0 count; positive arm (suppressing, displacement > 0) sum 11.25 kW in both arms",
   "_external_heat_forecast (line 5248 `if not self._external_heat.suppressing:`)", "`if not self._external_heat.suppressing:` -> `if False:` (mutant 3b458790a543507e)",
   "positive arm: a suppressing detector with free heat, where the guard is not taken in either arm"),
 "c39bf88e7fd0066f": ("_external_heat_forecast's return (None or array) for a suppressing detector whose free heat is 0, and what optimizer._horizon_weather hands the solve from it (ForecastSeries.external_heat_kw)",
   "moved_at_symbol=2 (None -> zeros[96]) and moved_at_solve_input=0 (optimizer.py:3049 maps all-zero to None in both arms)",
   "_external_heat_forecast (line 5259 return) and optimizer:_horizon_weather (optimizer.py:3046-3050)",
   "`np.any(arr > 0.0)` -> `np.any(arr >= 0.0)` (mutant c39bf88e7fd0066f)",
   "the solve-input arm: the same two states read through _horizon_weather, where the effect must vanish"),
 "218ac218da41d87d": ("_external_heat_override's value for a fresh numeric flue probe at 29.9, 30.0, 30.1 and 400 C; moved_inputs = readings whose override differs",
   "flue 30.0 C: False -> True; moved_inputs=1 count",
   "_external_heat_override (line 5156 `return probe.value > 30.0`)", "`>` -> `>=` (mutant 218ac218da41d87d); direction: a probe at exactly 30.0 C reads as a fire",
   "29.9, 30.1 and 400 C must not move"),
 "bcf290164a0edeeb": ("override value and the count of _LOGGER.warning calls over 4 update cycles (30 min apart) for a flue probe last reported 120 min before the first cycle (limit 60 min)",
   "stale probe: value None in both arms; warnings 1 -> 0",
   "_external_heat_override (line 5157 `if probe.stale:`)", "`if probe.stale:` -> `if False:` (mutant bcf290164a0edeeb); direction: the once-per-outage warning is never logged",
   "an untimestamped (fresh) probe at 400 C: (True, 0 warnings) in both arms"),
 "375376c4733a1a51": ("override value and the count of _LOGGER.warning calls over 4 update cycles (30 min apart) for a flue probe last reported 120 min before the first cycle (limit 60 min)",
   "stale probe: value None in both arms; warnings 1 -> 4 (the once-per-outage latch is reset each cycle)",
   "_external_heat_override (line 5174 `return None` in the stale branch)", "`return None` -> `pass` (mutant 375376c4733a1a51); direction: warning once per cycle",
   "an untimestamped (fresh) probe at 400 C: (True, 0 warnings) in both arms"),
 "2699efc070f5d4e3": ("_external_heat_override's value per external-heat entity state; moved_inputs = states whose override differs",
   "implausible flue readings -127 C and 1500 C (outside FLUE_RANGE_C): None -> True; moved_inputs=2 count",
   "_external_heat_override (line 5176 `if probe.problem != \"not_numeric\":`)", "`if probe.problem != \"not_numeric\":` -> `if False:` (mutant 2699efc070f5d4e3); direction: an implausible numeric probe falls to parse_bool, non-zero reads as a fire",
   "not_configured, missing_entity, unavailable, unknown: None in both arms; word 'on' True and 20 C False in both"),
 "cc7e5a62ec1ea4d0": ("_external_heat_override's value per entity state reaching line 5182 (read() classed it not_numeric); moved_inputs = states whose override differs",
   "moved_inputs=0 of 10 count",
   "_external_heat_override (line 5182 `if not reading.ok or reading.text is None:`)", "`if not reading.ok or reading.text is None:` -> `if False:` (mutant cc7e5a62ec1ea4d0)",
   "unavailable and not_configured return at line 5178 in both arms"),
 "d05457b7adf4d691": ("one _fetch_weather_forecast with no weather entity configured: (weather service calls made, held forecast rows, outage cycles, warning text)",
   "calls 0 -> 1 (weather.get_forecasts called with entity_id None) and warning 'No weather entity configured' -> 'No forecast data returned for None'",
   "_fetch_weather_forecast (line 7056 `if not weather_entity:`)", "`if not weather_entity:` -> `if False:` (mutant d05457b7adf4d691)",
   "weather entity configured, empty forecast: identical in both arms"),
 "d943cc9f7670a834": ("held forecast rows after one _fetch_weather_forecast whose response lacks the configured entity, no forecast held before, the weather entity's state live",
   "response {'weather.other': ...} or None: rows 0 -> 48 (the except branch fabricates the flat 48 h trajectory); moved_held_rows=2 count",
   "_fetch_weather_forecast (line 7069 `if result and weather_entity in result:`)", "`and` -> `or` (mutant d943cc9f7670a834); direction: a no-data reply becomes an exception and a fabricated forecast",
   "response {} (falsy: both arms take the else branch) and a held forecast (the except branch keeps it): rows identical"),
 "894b4e70a336f8fa": ("(DHW lead predictions filed, note_promise calls, kept promises) from _file_dhw_lead_predictions per dhw_temp_trajectory",
   "reachable inputs ([], [x], the solved 97-point list) identical; None raises TypeError under the mutant but OptimizationResult's one constructor (optimizer.py:3899) delivers a list",
   "_file_dhw_lead_predictions (line 10188 `if not trajectory:`)", "`if not trajectory:` -> `if False:` (mutant 894b4e70a336f8fa)",
   "the solved 97-point trajectory: 5 leads in both arms"),
 "2d6701afc323e1e8": ("DHW lead predictions filed by _file_dhw_lead_predictions at the production step dt_h = max(time_step_minutes, 1)/60, over trajectory lengths 0..200",
   "moved_lengths_at_production_dt=0 of 201 (min lead idx 4); off-grid control dt_h=3 h: 4 -> 5 leads",
   "_file_dhw_lead_predictions (line 10192 `if 0 < idx < len(trajectory):`)", "`0 < idx` -> `0 <= idx` (mutant 2d6701afc323e1e8)",
   "the off-grid arm (dt 3 h) is the positive control that the probe can see idx 0"),
 "8cfd8cf0d8a58c83": ("DHW lead predictions filed by _file_dhw_lead_predictions at the production dt_h, over trajectory lengths 0..200, and the length a real solve delivers",
   "lengths that move = the lead indices [4,12,24,48,96] (mutant IndexError); a solve delivers 97 (n_steps 96 + 1; _forecast_arrays pads every series to n_steps): 5 leads in both arms",
   "_file_dhw_lead_predictions (line 10192 `if 0 < idx < len(trajectory):`)", "`idx < len` -> `idx <= len` (mutant 8cfd8cf0d8a58c83)",
   "the solved length 97: identical"),
 "e02e1ac8cc0b714a": ("(room lead predictions filed, note_promise calls, day promises kept) from _file_lead_predictions per room trajectory, solve at PROMISE_HOUR",
   "empty trajectory: note_promise calls 0 -> 1 but kept promises 0 and leads 0 in both arms (plan_promise returns None for len(room)-1 < 1); moved_kept_records=0",
   "_file_lead_predictions (line 10223 `if not trajectory:`)", "`if not trajectory:` -> `if False:` (mutant e02e1ac8cc0b714a)",
   "solved 97-point trajectory: 5 leads and 1 kept promise in both arms (positive control that the promise path is live)"),
 "ba1c58ad6dabbebd": ("room lead predictions filed by _file_lead_predictions at the production dt_h, over trajectory lengths 0..200",
   "moved_lengths_at_production_dt=0 of 201 (min lead idx 4); off-grid control time_step_minutes=180: 4 -> 5 leads",
   "_file_lead_predictions (line 10231 `if 0 < idx < len(trajectory):`)", "`0 < idx` -> `0 <= idx` (mutant ba1c58ad6dabbebd)",
   "the off-grid arm is the positive control that the probe can see idx 0"),
}
out = {}
for k, (metric, exp, sym, pert, null) in H.items():
    out[k] = (f"# Metric: {metric}.\n"
              f"# Command: PYTHONPATH=tests/hastub python3 {P}/probe_{k}.py\n"
              f"# Expected: {exp}; tolerance exact (counts and values, no timing).\n"
              f"# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: {M}.\n"
              f"# Instrumented symbol: {S}{sym}.\n"
              f"# Perturbation: {pert}, applied in memory: the method is recompiled from its own source with the one\n"
              f"#   line replaced, in the coordinator module's namespace, and called on the same coordinator as the baseline arm.\n"
              f"# Null control: {null}.\n"
              f"# Count key: the value the production method returns or files (never an input attribute). Writes nothing.\n")
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(len(out))
