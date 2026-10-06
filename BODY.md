The group halts. No seam is extracted.

#1744 asked for a remeasure of `cut_dhw`, `cut_views`, `cross_seam_edges` and the hub-read counts after the solves stopped writing the hubs, and for an extraction only where a seam's cut falls. The comparison is `tests/structure.py`'s `seam_metrics` (the function text is the same at `31567b71`, the first parent of the #1887 merge, and at this head) over `tests/seam_map.json`. The attributes each of the five seams owns are the same set at both trees, so the state did not move. A class that took the methods and left those attributes on the coordinator would be the move the brief refuses. `cross_seam_edges` is the retired budget key; the live count is the seam table's crossing-a-seam line.

Dispositions, one per label the seam table returns: dhw, halt; views, halt; learning, halt; fetch, halt; grid, halt. dhw and views are the seams #1744 names. The other three are not those seams, and their owned attributes did not leave either.

The architecture score on this diff is NULL. The brief's planned gain was for two extracted seams; this diff extracts none, and a shortfall is not a failure. The diff adds no red-team shape. Goldens and both claim files are untouched. No budget is raised.

## Head

`301abb21c2fce2e45419e6a67d4d59828c1d1e8d`

The only file this commit adds is `tools/audit/harnesses/eg_b7_seam_hubs.py`. Nothing under `custom_components/` or `tests/golden/` changes against `96683e6e7eecc2d35b5fa4cb632bfc0b2894e2ff` (`origin/main` at the measurement, 2026-10-06T13:04Z). #1887 and #1966 (`0aa61e7b72bc6f39fc43a1e74eed5e038d78d9f8`) are ancestors.

## Mutation proof

n/a: no production line was added or changed, so there is no line whose deletion a closure can go red on.

## Null control

The pre-hub-write tree is `31567b71820fe8e3380be30a19b7342360c3b6b8`. `seam_metrics` there and at this head are the same function. Had stopping the per-solve hub writes detached a seam, that seam's owned attributes would differ and its cut would be the cost of a boundary that no longer runs through the coordinator. The owned sets compare equal. `hub_solve_writes` is the write count the issue waited on; it is not the read count, and the named seams' hub loads do not follow it down.

## Figures

`git diff --name-only 96683e6e7eecc2d35b5fa4cb632bfc0b2894e2ff HEAD`:

```
tools/audit/harnesses/eg_b7_seam_hubs.py
```

`git diff --exit-code 96683e6e7eecc2d35b5fa4cb632bfc0b2894e2ff HEAD -- custom_components tests/golden` exited 0.

`python3 tests/structure.py` at this head, seam table:

```
########## coordinator seam table (helpers charged: 14) ##########
  internal call occurrences: 348, crossing a seam: 149 (ratio 0.4282, evidence only)
  seam        units  attrs  xattr  xmeth    cut
  dhw            16      3     62      8     70
  learning       31     40    234     62    296
  fetch          27     13     82     33    115
  grid           22     31    146     39    185
  views          18      3     78     28    106
  seam_cut_total = 772
```

and `ok   seam_cut_total 772 <= 772`. The script exited 0.

Pre-#1887 seam table, `D=$(mktemp -d) && git archive 31567b71820fe8e3380be30a19b7342360c3b6b8 custom_components tests | tar -x -C "$D" && python3 "$D/tests/structure.py"`:

```
########## coordinator seam table (helpers charged: 13) ##########
  internal call occurrences: 337, crossing a seam: 144 (ratio 0.4273, evidence only)
  seam        units  attrs  xattr  xmeth    cut
  dhw            16      3     64      8     72
  learning       28     40    234     60    294
  fetch          27     13     84     33    117
  grid           22     31    146     39    185
  views          16      3     68     25     93
  seam_cut_total = 761
```

That script exited 0.

`seam_metrics` text equality:

```
python3 - <<'PY'
import subprocess
def fn(rev):
    src = subprocess.check_output(["git","show",f"{rev}:tests/structure.py"], text=True)
    i = src.index("def seam_metrics(")
    rest = src[i+1:]
    cut = min(x for x in (rest.find("\ndef "), rest.find("\nclass ")) if x!=-1)
    return src[i:i+1+cut]
a=fn("31567b71820fe8e3380be30a19b7342360c3b6b8")
b=fn("HEAD")
print("seam_metrics_equal", a==b, "bytes", len(a))
PY
```

```
seam_metrics_equal True bytes 6108
```

Hub loads are loads of `_opt_config`, `_thermal_params` and `_current_state` through a state root, the same attribute walk as `seam_metrics`. `tests/structure.py` does not print that row. `python3 tools/audit/harnesses/eg_b7_seam_hubs.py`:

```
tree HEAD
hub_loads dhw 11 _opt_config=0 _thermal_params=8 _current_state=3
hub_loads learning 29 _opt_config=5 _thermal_params=13 _current_state=11
hub_loads fetch 4 _opt_config=0 _thermal_params=3 _current_state=1
hub_loads grid 1 _opt_config=0 _thermal_params=0 _current_state=1
hub_loads views 5 _opt_config=1 _thermal_params=4 _current_state=0
hub_loads core 124 _opt_config=25 _thermal_params=47 _current_state=52
owned dhw 3 _dhw_learner _dhw_temperature _legionella
owned learning 40 _band_issue_problem _buffer_cooling_rate _buffer_cooling_samples _buffer_heating_since_sample _capacity_envelope _comfort_learner _cop_baseline _cop_health_cusum _cop_ratio_ewma _cop_samples _cop_scale _curve_day _curve_day_worst _curve_learner _day_inputs_healthy _defrost _flow_bias _freq_fallback _freq_map _house_heat_loss_samples _house_heat_loss_scale _immersion_events _internal_gains_profile _last_buffer_sample_time _last_buffer_temp_sample _last_cop_curve_dhw _last_cop_dhw_temp _last_heavy_snow _last_house_sample _last_house_sample_time _last_measured_cop _learner_freeze_reason _lower_floor_loss_ratio _lower_floor_loss_samples _price_model _rollback_done_for_alarm _snow_accum_cm _snow_accum_last _solar_aperture _thermal_learning_store
owned fetch 13 _open_meteo _price_days_seen _price_known_steps _price_model _price_qdays_seen _price_tile_cursor _prices _solar_radiation_forecast _tibber_outage_cycles _tibber_reauth_started _weather_forecast _weather_outage_cycles _weather_stale_since
owned grid 31 _band_issue_problem _fuse_advisor _fuse_advisor_at _grid_fee_cache _grid_fee_issue_value _grid_fee_sign_issue_value _guard_last_fold _last_diagnosis _last_interval_record _ledger _ledger_store _lower_floor_issue_raised _month_reports _operation_score _outage_dhw_until _outage_recovery_until _peak_guard _peak_tracker _price_days_seen _price_known_steps _price_model _price_model_store _price_qdays_seen _price_tile_cursor _price_tiles _pv_production _pv_summary _pv_surplus _score_day _start_counter _unsub_peak_guard
owned views 3 _ecl110_current_displace _ecl110_last_payload _energy_totals_since
tree 31567b71820fe8e3380be30a19b7342360c3b6b8
hub_loads dhw 12 _opt_config=0 _thermal_params=8 _current_state=4
hub_loads learning 28 _opt_config=6 _thermal_params=11 _current_state=11
hub_loads fetch 6 _opt_config=1 _thermal_params=4 _current_state=1
hub_loads grid 1 _opt_config=0 _thermal_params=0 _current_state=1
hub_loads views 5 _opt_config=1 _thermal_params=4 _current_state=0
hub_loads core 152 _opt_config=45 _thermal_params=52 _current_state=55
owned dhw 3 _dhw_learner _dhw_temperature _legionella
owned learning 40 _band_issue_problem _buffer_cooling_rate _buffer_cooling_samples _buffer_heating_since_sample _capacity_envelope _comfort_learner _cop_baseline _cop_health_cusum _cop_ratio_ewma _cop_samples _cop_scale _curve_day _curve_day_worst _curve_learner _day_inputs_healthy _defrost _flow_bias _freq_fallback _freq_map _house_heat_loss_samples _house_heat_loss_scale _immersion_events _internal_gains_profile _last_buffer_sample_time _last_buffer_temp_sample _last_cop_curve_dhw _last_cop_dhw_temp _last_heavy_snow _last_house_sample _last_house_sample_time _last_measured_cop _learner_freeze_reason _lower_floor_loss_ratio _lower_floor_loss_samples _price_model _rollback_done_for_alarm _snow_accum_cm _snow_accum_last _solar_aperture _thermal_learning_store
owned fetch 13 _open_meteo _price_days_seen _price_known_steps _price_model _price_qdays_seen _price_tile_cursor _prices _solar_radiation_forecast _tibber_outage_cycles _tibber_reauth_started _weather_forecast _weather_outage_cycles _weather_stale_since
owned grid 31 _band_issue_problem _fuse_advisor _fuse_advisor_at _grid_fee_cache _grid_fee_issue_value _grid_fee_sign_issue_value _guard_last_fold _last_diagnosis _last_interval_record _ledger _ledger_store _lower_floor_issue_raised _month_reports _operation_score _outage_dhw_until _outage_recovery_until _peak_guard _peak_tracker _price_days_seen _price_known_steps _price_model _price_model_store _price_qdays_seen _price_tile_cursor _price_tiles _pv_production _pv_summary _pv_surplus _score_day _start_counter _unsub_peak_guard
owned views 3 _ecl110_current_displace _ecl110_last_payload _energy_totals_since
owned_equal dhw True
owned_equal learning True
owned_equal fetch True
owned_equal grid True
owned_equal views True
```

`hub_solve_writes` at this head, `python3 -c 'import sys; from pathlib import Path; sys.path.insert(0,"tools/audit"); from archscore.metrics.hub_solve_writes import measure; m=measure(Path(".")); print(m["value"]); print("\n".join(m["details"]["sites"]))'`:

```
2
coordinator.py:4747 _thermal_params.house_heat_loss_scale
coordinator.py:11078 _opt_config.comfort_weight
```

`hub_solve_writes` at `31567b71`:

```
python3 - <<'PY'
import subprocess, tempfile
from pathlib import Path
import sys
sys.path.insert(0, "tools/audit")
from archscore.metrics.hub_solve_writes import measure
BASE = "31567b71820fe8e3380be30a19b7342360c3b6b8"
with tempfile.TemporaryDirectory() as td:
    raw = subprocess.check_output(["git", "archive", BASE, "custom_components"])
    subprocess.run(["tar", "-x", "-C", td], input=raw, check=True)
    m = measure(Path(td))
    print("pre_b1", m["value"])
PY
```

```
pre_b1 40
```

The retired keys at the issue's commit, `git show 31394964:tests/structure_budgets.json | python3 -c 'import json,sys; d=json.load(sys.stdin); print({k:d[k] for k in ("cut_dhw","cut_views","cross_seam_edges")})'`:

```
{'cut_dhw': 73, 'cut_views': 109, 'cross_seam_edges': 134}
```

Those keys are not rows of the current ratchet. The live comparison is the two seam tables above.

`python3 tools/audit/archscore/score.py --diff 96683e6e7eecc2d35b5fa4cb632bfc0b2894e2ff`:

```
Architecture score: dS +0.0000 NULL
```

## Red checks

none

## Forward-carry

none

## Friction

none

Closes #1744
