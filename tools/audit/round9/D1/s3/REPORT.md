# Round 9 — D1-s3 (D1)

Rendered by the box B5 thread from the JSON the seat returned (`tools/audit/round9/reports-B5.json`), because the seat's own write of this file was refused by its harness. The content is the seat's; nothing was added, verified or judged.

- baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`
- exposure: none recorded

## Method and coverage

### D1.M1 — deep

arbiter_unload.py: real asyncio loop, LoopHass subclass of FakeHass (real tasks, ThreadPoolExecutor), real HeatPumpOptimizerCoordinator with pump duty 'control', event-bus dispatch of production _changed, then the coordinator's own async_shutdown; live registrations counted by closure identity: 2 after unload (null 0, fix 0). Other listeners in scope (boost/away WeakKeyDictionary state, legionella switch release) were read and hold no registration.

### D1.M2 — deep

store_fuzz.py: 200 seeded mutants x 15 operators per store for pump_duty, boost, away, legionella, loaded through the real loaders then two consumer cycles on an aware clock; freq_map_store.py: 200 mutants of FrequencyMap.from_dict with 96 truthful folds; parsers.py: 200 DrawStats.from_dict mutants; ManualOverride checked as the guarded sibling.

### D1.M3 — spot

boost_unbounded.py: clock stepped back 0/1/6/24 h and a far-future restore; store_fuzz.py --naive-clock vs the aware clock; legionella hours_since clamps (max(0, ...)) confirmed by reading. DST days were not driven.

### D1.M4 — deep

climate_midsolve.py wraps the production coordinator._await_optimize (it does not replace it) and, from the loop at that await, runs the peak guard's _async_peak_guard_transition -> async_update_listeners; it reads HeatPumpOptimizerClimate.target_temperature. _solve_snapshot deep-copies state, params and opt_config, so the solve itself is not torn; the torn surface is the live setback that loop-side readers see.

### D1.M5 — spot

Exceptions were injected through the corrupt stores and traced to their escape: pump_arbiter.apply is unfenced in _apply_action, so it fails _async_update_data; the away TypeError is swallowed by async_run_optimization's fence into 'solve_failed'; boost.restore raises out of a spawned task. There was no per-except injection sweep of the best-effort _clear guards.

### D1.M6 — deep

away_naive_return.py drives the card's datetime-local value through coordinator.async_set_away, then _resolve_away and async_run_optimization. parsers.py sends hostile inputs to setpoint_check._setpoint_and_unit, freq_control.resolve_reading, silent_mode.compose, dhw_schedule.parse_windows/parse_weekly_windows and ManualOverride; all counts are 0, and the perturb arm moves setpoint 0->320 and freq 0->315.

## Findings

### D1-s3-01 — A tz-less return_time (card datetime-local) or a naive stored datetime wedges every cycle with TypeError

- step: D1.M6; severity: high; class: bug; class_guess: P2
- instrumented symbol: `heatpump_optimizer.away:_parse_return_time / away:expire_override (driven through coordinator.async_set_away, _resolve_away, async_run_optimization)`
- metric: Of 6 consecutive cycles after set_away(active, tz-less return_time), cycles in which _resolve_away raises; plus async_run_optimization calls returning solve_failed (of 2).

A set_away return_time without an offset (the card's <input type=datetime-local> value, and services.yaml's own example) makes away.expire_override compare naive with aware; every later solve then returns solve_failed (2 of 2), and _resolve_away raises on 6 of 6 cycles, until away is switched off.

```json
{
  "id": "D1-s3-01",
  "scope": "D1-s3",
  "step": "D1.M6",
  "title": "A tz-less return_time (card datetime-local) or a naive stored datetime wedges every cycle with TypeError",
  "severity": "high",
  "claim": "A set_away return_time without an offset (the card's <input type=datetime-local> value, and services.yaml's own example) makes away.expire_override compare naive with aware; every later solve then returns solve_failed (2 of 2), and _resolve_away raises on 6 of 6 cycles, until away is switched off.",
  "mechanism": "away._parse_return_time returns datetime.fromisoformat(value) unnormalised. async_set_away stores the naive ISO string before expire_override raises, so every coordinator._resolve_away inside async_run_optimization raises and is fenced into 'solve_failed' with an ERROR traceback. The same unnormalised parse sits in legionella async_load (dt_util.parse_datetime, consumed by async_track's now - previous), in pump_arbiter._load (datetime.fromisoformat, consumed by hold()'s now - at, which escapes _apply_action as UpdateFailed) and in boost._parse_until (restore raises once). manual_plan._coerce_awareness is the sibling seam that guards it.",
  "evidence": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/away_naive_return.py",
    "harness_path": "tools/audit/round9/D1/s3/away_naive_return.py",
    "value": 6,
    "unit": "failed cycles of 6 (plus solves_failed=2 of 2; service_raised=1)",
    "baseline_sha": "1936d5ca72a06556eeed4e8e5bf3dea520e517e1",
    "machine": "box B5, linux cloud container, python 3.14.0rc2",
    "cpu_or_wall": "count",
    "contention_note": "other finder seats sharing box B5; count metric, contention-immune",
    "tolerance": "exact",
    "load1": 1.11,
    "thread_factor": 1
  },
  "instrumented_symbol": "heatpump_optimizer.away:_parse_return_time / away:expire_override (driven through coordinator.async_set_away, _resolve_away, async_run_optimization)",
  "perturbation": {
    "change": "away._parse_return_time returns dt_util.as_local(d) when d is naive (--perturb); null control: the same instant with an explicit offset (--aware-input)",
    "expected_direction": "to_zero",
    "observed_value": "0 failed cycles, 0 solves failed, service_raised 0 in both arms"
  },
  "metric_definition": "Of 6 consecutive cycles after set_away(active, tz-less return_time), cycles in which _resolve_away raises; plus async_run_optimization calls returning solve_failed (of 2).",
  "phenomenon_property": "Every ISO datetime entering from outside the process (service input or persisted store) is normalised to an aware instant before it is compared or subtracted with dt_util.now(); no such value can make a per-cycle path raise.",
  "seam_rule": "rg -n \"fromisoformat|parse_datetime\\(\" custom_components/heatpump_optimizer/{away,boost,pump_arbiter,legionella,manual_plan}.py",
  "null_control": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/away_naive_return.py --aware-input",
    "value": 0,
    "note": "The same return instant with +02:00: 0 failed cycles, 0 failed solves. Store seams: tools/audit/round9/D1/s3/store_fuzz.py gives repeat_fail away=13, legionella=10, pump_duty=25 (17 naive_dt) of 200; --perturb gives 0; --naive-clock (the stub's default) hides the naive_dt failures."
  },
  "reproduction_steps": [
    "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/away_naive_return.py",
    "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/store_fuzz.py"
  ],
  "stop_rule_class": "bug",
  "class_guess": "P2",
  "files": [
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/pump_arbiter.py",
    "custom_components/heatpump_optimizer/boost.py"
  ],
  "proposed_fix_scope": "Normalise at each parse seam (away._parse_return_time, boost._parse_until, pump_arbiter._load, legionella.async_load) with dt_util.as_local for a naive result, or share manual_plan._coerce_awareness; one shared helper."
}
```

### D1-s3-02 — Pump-duty arbiter re-registers its timer and state listener on an unloaded coordinator and keeps writing the pump

- step: D1.M1; severity: high; class: bug; class_guess: new
- instrumented symbol: `heatpump_optimizer.pump_arbiter:apply / pump_arbiter:_listen (driven via HeatPumpOptimizerCoordinator.async_shutdown on a real asyncio loop)`
- metric: Arbiter timers plus state listeners whose callback closure holds the coordinator, counted after async_shutdown returned and all tasks drained; plus pump service calls made after the unload.

A pump state change dispatched just before unload leaves 2 live arbiter registrations on the torn-down coordinator after async_shutdown, and the leaked 1-minute tick writes the pump (2 writes) after the unload.

```json
{
  "id": "D1-s3-02",
  "scope": "D1-s3",
  "step": "D1.M1",
  "title": "Pump-duty arbiter re-registers its timer and state listener on an unloaded coordinator and keeps writing the pump",
  "severity": "high",
  "claim": "A pump state change dispatched just before unload leaves 2 live arbiter registrations on the torn-down coordinator after async_shutdown, and the leaked 1-minute tick writes the pump (2 writes) after the unload.",
  "mechanism": "pump_arbiter._changed queues hass.async_create_task(apply(coord)). async_shutdown -> pump_arbiter.release -> release_listeners empties held.unsubs. The queued apply then runs; it never checks coord._entry_released, and _listen sees empty unsubs, so it registers async_track_time_interval(_tick, 1 min) and async_track_state_change_event again. Nothing unsubscribes them, so the dead instance commands the pump every minute alongside the reloaded one, or after the integration is disabled.",
  "evidence": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/arbiter_unload.py",
    "harness_path": "tools/audit/round9/D1/s3/arbiter_unload.py",
    "value": 2,
    "unit": "live registrations after unload (writes_after_unload=2)",
    "baseline_sha": "1936d5ca72a06556eeed4e8e5bf3dea520e517e1",
    "machine": "box B5, linux cloud container, python 3.14.0rc2",
    "cpu_or_wall": "count",
    "contention_note": "other finder seats sharing box B5; count metric, contention-immune",
    "tolerance": "exact",
    "load1": 1.11,
    "thread_factor": 1
  },
  "instrumented_symbol": "heatpump_optimizer.pump_arbiter:apply / pump_arbiter:_listen (driven via HeatPumpOptimizerCoordinator.async_shutdown on a real asyncio loop)",
  "perturbation": {
    "change": "mock.patch pump_arbiter.apply to return when coord._entry_released (--perturb); null: no pump state event before the unload (--null)",
    "expected_direction": "to_zero",
    "observed_value": "0 registrations, 0 writes in both arms"
  },
  "metric_definition": "Arbiter timers plus state listeners whose callback closure holds the coordinator, counted after async_shutdown returned and all tasks drained; plus pump service calls made after the unload.",
  "phenomenon_property": "After async_shutdown returns, no arbiter registration references the coordinator and no arbiter path can write the pump; apply() declines once the entry is released.",
  "seam_rule": "rg -n \"async_track_time_interval|async_track_state_change_event|async_create_task\" custom_components/heatpump_optimizer/{pump_arbiter,legionella,disinfection,boost,away}.py",
  "null_control": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/arbiter_unload.py --null",
    "value": 0,
    "note": "The same lifecycle without an event queued before the unload: 0 live and 0 writes."
  },
  "stop_rule_class": "bug",
  "class_guess": "new",
  "files": [
    "custom_components/heatpump_optimizer/pump_arbiter.py"
  ],
  "proposed_fix_scope": "pump_arbiter.apply (and _tick/_changed) return early when coord._entry_released; release() marks held as released so _listen refuses to re-arm."
}
```

### D1-s3-03 — pump_arbiter._load installs non-numeric set-point values that raise TypeError on every apply

- step: D1.M2; severity: medium; class: bug; class_guess: P1
- instrumented symbol: `heatpump_optimizer.pump_arbiter:_load / pump_arbiter:apply`
- metric: Seeded mutants of the healthy pump_duty payload (after the real loader) whose second pump_arbiter.apply call still raises.

8 of 200 seeded pump_duty store mutants (a string, list or dict set-point) make pump_arbiter.apply raise on every cycle, on both the aware and the naive clock, because _load type-checks nothing in pair[0].

```json
{
  "id": "D1-s3-03",
  "scope": "D1-s3",
  "step": "D1.M2",
  "title": "pump_arbiter._load installs non-numeric set-point values that raise TypeError on every apply",
  "severity": "medium",
  "claim": "8 of 200 seeded pump_duty store mutants (a string, list or dict set-point) make pump_arbiter.apply raise on every cycle, on both the aware and the naive clock, because _load type-checks nothing in pair[0].",
  "mechanism": "_load accepts held.written[slot] = (pair[0], fromisoformat(pair[1])). hold() -> _differs computes abs(observed - value) with a str/list/dict value and raises TypeError before _write can overwrite the record, so the corrupt record persists. The raise escapes coordinator._apply_action, so the whole update fails. Separately, 34 of 200 mutants make the loader itself raise KeyError/AttributeError once ('written' not a dict, pair a dict).",
  "evidence": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/store_fuzz.py --naive-clock",
    "harness_path": "tools/audit/round9/D1/s3/store_fuzz.py",
    "value": 8,
    "unit": "mutants of 200 failing every cycle (pump_duty, excluding naive-datetime mutants)",
    "baseline_sha": "1936d5ca72a06556eeed4e8e5bf3dea520e517e1",
    "machine": "box B5, linux cloud container, python 3.14.0rc2",
    "cpu_or_wall": "count",
    "contention_note": "other finder seats sharing box B5; deterministic seeded count",
    "tolerance": "exact (seed 9, n 200)",
    "load1": 1.11,
    "thread_factor": 1
  },
  "instrumented_symbol": "heatpump_optimizer.pump_arbiter:_load / pump_arbiter:apply",
  "perturbation": {
    "change": "--perturb: after _load, drop any set-point slot whose value is not a real number and any mode slot that is not a str",
    "expected_direction": "to_zero",
    "observed_value": "pump_duty_repeat_fail=0"
  },
  "metric_definition": "Seeded mutants of the healthy pump_duty payload (after the real loader) whose second pump_arbiter.apply call still raises.",
  "phenomenon_property": "A persisted pump_duty record whose values are not the type the arbiter writes is dropped at load with one log line; no stored value can make apply() raise.",
  "seam_rule": "rg -n \"held.written\\[\" custom_components/heatpump_optimizer/pump_arbiter.py",
  "null_control": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/store_fuzz.py",
    "value": 0,
    "note": "The healthy payload: pump_duty_healthy_repeat=0."
  },
  "stop_rule_class": "bug",
  "class_guess": "P1",
  "files": [
    "custom_components/heatpump_optimizer/pump_arbiter.py"
  ],
  "proposed_fix_scope": "Validate each (value, at) pair in pump_arbiter._load (type per slot, aware stamp), catch KeyError/AttributeError, and log once."
}
```

### D1-s3-04 — Climate entity publishes the away setback as the user's target while the solve is in the executor

- step: D1.M4; severity: medium; class: bug; class_guess: new
- instrumented symbol: `heatpump_optimizer.climate:HeatPumpOptimizerClimate.target_temperature (window opened by away:apply_setback, write issued by coordinator._async_peak_guard_transition at coordinator._await_optimize)`
- metric: Maximum |climate.target_temperature - configured target| over the listener state writes made while the solve is awaited.

With away active, a state write during the solve's executor await (the peak guard's async_update_listeners) publishes climate target_temperature 16.0 C against the configured 21.0 C, a 5.00 C deviation; after the solve it is 0.

```json
{
  "id": "D1-s3-04",
  "scope": "D1-s3",
  "step": "D1.M4",
  "title": "Climate entity publishes the away setback as the user's target while the solve is in the executor",
  "severity": "medium",
  "claim": "With away active, a state write during the solve's executor await (the peak guard's async_update_listeners) publishes climate target_temperature 16.0 C against the configured 21.0 C, a 5.00 C deviation; after the solve it is 0.",
  "mechanism": "away.apply_setback writes the setback into the live ctx._opt_config.target_temp before _await_optimize, and restore_setback undoes it only after the await. HeatPumpOptimizerClimate.target_temperature ('the comfort target the user asked for') reads coordinator.target_temperature, which is that live field, so any loop-side state write in the window publishes the setback to the state machine and the recorder.",
  "evidence": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/climate_midsolve.py",
    "harness_path": "tools/audit/round9/D1/s3/climate_midsolve.py",
    "value": 5,
    "unit": "degC max |published - configured| mid-solve",
    "baseline_sha": "1936d5ca72a06556eeed4e8e5bf3dea520e517e1",
    "machine": "box B5, linux cloud container, python 3.14.0rc2",
    "cpu_or_wall": "n/a",
    "contention_note": "other finder seats sharing box B5; value metric, contention-immune",
    "tolerance": "exact",
    "load1": 1.18,
    "thread_factor": 1
  },
  "instrumented_symbol": "heatpump_optimizer.climate:HeatPumpOptimizerClimate.target_temperature (window opened by away:apply_setback, write issued by coordinator._async_peak_guard_transition at coordinator._await_optimize)",
  "perturbation": {
    "change": "--perturb: the property reads ctx._config[CONF_TARGET_TEMP] instead of the live solve config; --null: away override off",
    "expected_direction": "to_zero",
    "observed_value": "0.00 C in both arms"
  },
  "metric_definition": "Maximum |climate.target_temperature - configured target| over the listener state writes made while the solve is awaited.",
  "phenomenon_property": "A published entity value never reflects the solve-scoped envelope (setback, economy/open-window floor) that apply_setback/lower_floor write into the live config; readers see the configured value throughout the solve.",
  "seam_rule": "rg -n \"_opt_config\\.|target_temperature\" custom_components/heatpump_optimizer/{climate,sensor,binary_sensor,entity}.py",
  "null_control": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/climate_midsolve.py --null",
    "value": 0,
    "note": "Away off: the mid-solve write publishes 21.0."
  },
  "stop_rule_class": "bug",
  "class_guess": "new",
  "files": [
    "custom_components/heatpump_optimizer/climate.py",
    "custom_components/heatpump_optimizer/away.py"
  ],
  "proposed_fix_scope": "Apply the away envelope to the solve's deep-copied opt_config (after _solve_snapshot) instead of the live one, or have climate.target_temperature read the configured target."
}
```

### D1-s3-05 — Boost 'two-hour maximum' is an absolute instant: a clock step back or a far-future store extends it without bound

- step: D1.M3; severity: medium; class: bug; class_guess: new
- instrumented symbol: `heatpump_optimizer.boost:BoostState.expire / boost:apply / boost:restore`
- metric: Hours, sampled every 15 min to a 72 h cap, for which boost.apply still sets action['boost_space'] after the clock step or restore.

A space boost (nameplate power, comfort ceiling, full displace) stays live 2+J hours after the wall clock steps back J hours (J=24 gives 26.0 h), and a restored until in 2099 never expires (72.0 h at the harness cap).

```json
{
  "id": "D1-s3-05",
  "scope": "D1-s3",
  "step": "D1.M3",
  "title": "Boost 'two-hour maximum' is an absolute instant: a clock step back or a far-future store extends it without bound",
  "severity": "medium",
  "claim": "A space boost (nameplate power, comfort ceiling, full displace) stays live 2+J hours after the wall clock steps back J hours (J=24 gives 26.0 h), and a restored until in 2099 never expires (72.0 h at the harness cap).",
  "mechanism": "BoostState.expire/active compare the stored until with now only, and boost.restore accepts any parsed until > now; nothing bounds until - now by BOOST_HOURS.",
  "evidence": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/boost_unbounded.py",
    "harness_path": "tools/audit/round9/D1/s3/boost_unbounded.py",
    "value": 26,
    "unit": "hours live after a 24 h backward clock step (jump1=3.0, jump6=8.0, restore_2099=72.0 cap)",
    "baseline_sha": "1936d5ca72a06556eeed4e8e5bf3dea520e517e1",
    "machine": "box B5, linux cloud container, python 3.14.0rc2",
    "cpu_or_wall": "n/a",
    "contention_note": "frozen simulated clock; contention-immune",
    "tolerance": "exact (15-min sampling)",
    "load1": 1.18,
    "thread_factor": 1
  },
  "instrumented_symbol": "heatpump_optimizer.boost:BoostState.expire / boost:apply / boost:restore",
  "perturbation": {
    "change": "--perturb: BoostState.expire also drops an end more than BOOST_HOURS after now",
    "expected_direction": "down",
    "observed_value": "jump0=2.0, jump1/6/24=0.0, restore_2099=0.0"
  },
  "metric_definition": "Hours, sampled every 15 min to a 72 h cap, for which boost.apply still sets action['boost_space'] after the clock step or restore.",
  "phenomenon_property": "A boost channel is never live more than BOOST_HOURS after any instant at which it is read, whatever the clock does or the store holds.",
  "seam_rule": "rg -n \"until\" custom_components/heatpump_optimizer/boost.py",
  "null_control": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/boost_unbounded.py",
    "value": 2,
    "note": "jump0 arm, no clock step: 2.0 h as designed."
  },
  "leave_one_out": {
    "cells": 5,
    "min": 2,
    "max": 72,
    "drop_most_favourable": 26
  },
  "stop_rule_class": "bug",
  "class_guess": "new",
  "files": [
    "custom_components/heatpump_optimizer/boost.py"
  ],
  "proposed_fix_scope": "Clamp until to now + BOOST_HOURS in BoostState.expire/active and in restore."
}
```

### D1-s3-06 — FrequencyMap.from_dict admits an unbounded ratio or out-of-range decile that pins recommend() at hz_min for days

- step: D1.M2; severity: medium; class: bug; class_guess: P1
- instrumented symbol: `heatpump_optimizer.freq_control:FrequencyMap.from_dict / FrequencyMap.recommend / FrequencyMap.observe`
- metric: Mutants whose clipped recommend(3 kW) after 96 folds of truthful plant kW (0.04 kW/Hz) gives plant power below 50 % of the target.

10 of 200 seeded frequency-map store mutants (a huge ratio, or a negative decile key with a large ratio) leave the compressor recommendation for a 3 kW target at hz_min, delivering under 50 %, even after 96 truthful folds.

```json
{
  "id": "D1-s3-06",
  "scope": "D1-s3",
  "step": "D1.M2",
  "title": "FrequencyMap.from_dict admits an unbounded ratio or out-of-range decile that pins recommend() at hz_min for days",
  "severity": "medium",
  "claim": "10 of 200 seeded frequency-map store mutants (a huge ratio, or a negative decile key with a large ratio) leave the compressor recommendation for a 3 kW target at hz_min, delivering under 50 %, even after 96 truthful folds.",
  "mechanism": "from_dict refuses non-finite or non-positive ratios and negative counts, but accepts any int key and any finite ratio. recommend() walks buckets ascending; a phantom bucket predicting ratio*mid >= target at or below hz_min answers first, and _command_frequency clips it to hz_min. observe() only decays the ratio with EWMA alpha 0.1, so a 1e308 ratio needs thousands of folds.",
  "evidence": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/freq_map_store.py",
    "harness_path": "tools/audit/round9/D1/s3/freq_map_store.py",
    "value": 10,
    "unit": "mutants of 200 still under-delivering after 96 folds",
    "baseline_sha": "1936d5ca72a06556eeed4e8e5bf3dea520e517e1",
    "machine": "box B5, linux cloud container, python 3.14.0rc2",
    "cpu_or_wall": "count",
    "contention_note": "deterministic seeded count; contention-immune",
    "tolerance": "exact (seed 9, n 200)",
    "load1": 1.18,
    "thread_factor": 1
  },
  "instrumented_symbol": "heatpump_optimizer.freq_control:FrequencyMap.from_dict / FrequencyMap.recommend / FrequencyMap.observe",
  "perturbation": {
    "change": "--perturb: from_dict also drops keys outside [0, FREQ_DECILES) and ratios above 1.0 kW/Hz",
    "expected_direction": "to_zero",
    "observed_value": 0
  },
  "metric_definition": "Mutants whose clipped recommend(3 kW) after 96 folds of truthful plant kW (0.04 kW/Hz) gives plant power below 50 % of the target.",
  "phenomenon_property": "A loaded frequency map contains only deciles in [0, FREQ_DECILES) with physically plausible kW/Hz ratios; no stored bucket can pin the recommendation outside what the healthy map would answer.",
  "seam_rule": "rg -n \"def from_dict\" custom_components/heatpump_optimizer/freq_control.py",
  "null_control": {
    "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/freq_map_store.py",
    "value": 0,
    "note": "The healthy map recommends 80.0 Hz; healthy_stuck=0."
  },
  "stop_rule_class": "bug",
  "class_guess": "P1",
  "files": [
    "custom_components/heatpump_optimizer/freq_control.py"
  ],
  "proposed_fix_scope": "Bound the key to range(FREQ_DECILES) and the ratio to a plausible ceiling in FrequencyMap.from_dict."
}
```

## Non-findings

- setpoint_check._setpoint_and_unit never raises and never returns a non-finite degC for hostile pump set-point states (24 states x 5 units x 4 attribute variants); the counter moves when the finiteness guard is removed — `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/parsers.py [--perturb]` → setpoint_bad=0 (perturb 320)
- freq_control.resolve_reading returns a finite or None reading and a finite range for hostile number/sensor states and min/max attributes — `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/parsers.py [--perturb]` → freq_bad=0 (perturb 315)
- DrawStats.from_dict survives 200 hostile persisted payloads with finite reservoirs, open_kwh and quantiles — `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/parsers.py` → draws_bad=0
- silent_mode.compose with a NaN, inf, negative, huge or non-numeric fraction, or a malformed/24 kB window spec, returns None or a finite cap in (0, p_max] — `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/parsers.py` → silent_bad=0
- dhw_schedule.parse_windows/parse_weekly_windows refuse 100 kB and malformed specs only with DHWWindowError — `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/parsers.py` → windows_bad=0
- ManualOverride from_dict/is_expired/channel_pins handle naive and aware expiries against an aware now (the _coerce_awareness guard holds) — `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/parsers.py` → manual_bad=0
- Healthy payloads of pump_duty, boost, away and legionella survive load plus two cycles on an aware clock, and the boost store has no permanent failure mode under 200 mutants — `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/store_fuzz.py` → *_healthy_repeat=0 for all four; boost_repeat_fail=0/200
- The arbiter leaves no registration behind when no pump event is queued at unload (the ordinary unload path is clean) — `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/arbiter_unload.py --null` → live_registrations_after_unload=0, writes_after_unload=0

## Harnesses

- `tools/audit/round9/D1/s3/arbiter_unload.py`
- `tools/audit/round9/D1/s3/store_fuzz.py`
- `tools/audit/round9/D1/s3/away_naive_return.py`
- `tools/audit/round9/D1/s3/boost_unbounded.py`
- `tools/audit/round9/D1/s3/climate_midsolve.py`
- `tools/audit/round9/D1/s3/freq_map_store.py`
- `tools/audit/round9/D1/s3/parsers.py`

## Unfinished

- D1.M3: DST transitions were not driven for dhw_schedule, pump_schedule or dhw_draws windows. The pump_arbiter ECHO_GRACE_S and retry deadline arithmetic under a backward clock step (hold() goes blind for J hours) was not measured. Price-list-stops-updating and an empty weather forecast were not driven for the entity files in scope.
- D1.M5: There was no per-except exception-injection sweep (log-once / last_update_success / recovery) of the best-effort ir.async_delete_issue guards in legionella.py, pump_arbiter.py and setpoint_check.py, or of disinfection._write. Only the store-driven escapes were executed.
- D1.M1: Only the pump-duty arbiter's reload/unload race was driven. A full setup -> first refresh -> reload mid-solve -> unload mid-solve -> setup cycle through the entity platforms (sensor/switch/button/climate/binary_sensor) with gc.get_referrers was not run.

## Leads

- owner D1-s2: `custom_components/heatpump_optimizer/coordinator.py` `HeatPumpOptimizerCoordinator._apply_action` — pump_arbiter.apply is awaited unfenced, while _command_frequency, _async_drive_pumps and the drift watch are fenced. Any arbiter exception (see D1-s3-01/03) fails the whole _async_update_data with an ERROR traceback on every poll and skips frequency, pumps, accuracy and energy saves.
- owner D1-s2: `custom_components/heatpump_optimizer/services.py` `SERVICE_SCHEMA_SET_AWAY` — return_time is vol.Any(None, cv.string) with no datetime or awareness validation, so the card's tz-less datetime-local value reaches the coordinator unchecked (D1-s3-01).
- owner unknown: `tests/hastub/homeassistant/util/dt.py` `now` — The stub's now() is naive unless HASTUB_TZ is set, while real HA is always aware. This hides every naive-vs-aware TypeError: store_fuzz.py --naive-clock loses all the naive_dt failures, and tests/finite_boundary.py seeds a naive datetime into the pump_duty record it fuzzes. Possible instrument finding.
- owner unknown: `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js` `away-strip data-away-return change handler` — Sends the datetime-local value (tz-less) as set_away return_time; the card could send an offset-bearing ISO string (new Date(value).toISOString()).
