# Probe r10-live-away-heating: result at cf4f6b7a660f5b61e0f2b933bd18647fe3ba90c7 (= origin/main)

## Classification

**(f) Not reproduced in the production solve.** Given an away state as `away.resolve` produces one, the solve plans **zero** space-heating slots at indoor 22 °C (row `away`). The live slots therefore come from something upstream of the solve or from what the plan shows. The candidates are ranked under *What would settle it*, and the owner's diagnostics are needed to choose between them.

There is also one **latent (b)** found on the way, which is real at the config level but adds no slots in the reproduced house: a configured weekend or holiday comfort schedule **replaces the away target** on Saturday and Sunday and on holiday dates (Saturday comfort target 21.0 while away, where it should be 16.0). The report's day was Friday 2026-10-30, so a 24–48 h horizon reaches Saturday.

## Measured table

Harness: `dev/audit/harnesses/r10_live_away_heating.py` (in full below). Each arm builds the solve the way `coordinator._solve_hubs` does: `OptimizationConfig.from_mapping(EntryConfig)`, then `away.solve_bands` with an `AwayState` in the shape `away.resolve` leaves it, then `replace` into copies, then `HeatPumpOptimizer.optimize`. The horizon is 48 h from Fri 2026-10-30 12:00, with the suite's `winter_typical` SE3 prices over two days, the `shoulder` weather minus 4 K (a mean of about 2 °C), a single zone, and DHW on. A space slot is a step with more than 0.1 kW.

| arm | away | set point | indoor | price | space slots | space kWh | first–last | DHW slots / kWh | Sat comfort / floor |
|---|---|---|---|---|---|---|---|---|---|
| **away** (scenario) | on | 18 | 22 | SE3 | **0** | 0.00 | – | 6 / 4.43 | 16.0 / 16.0 |
| **null 1**: away off | off | 18 | 22 | SE3 | 6 | 2.99 | Sat 00:45–02:00 | 35 / 9.98 | 21.0 / 17.0 |
| away off, set point 21 | off | 21 | 22 | SE3 | 35 | 20.41 | Sat 00:15–Sun 04:45 | 35 / 9.98 | 21.0 / 17.0 |
| **null 2**: flat price | on | 18 | 22 | flat 1.2 | **0** | 0.00 | – | 4 / 3.78 | 16.0 / 16.0 |
| indoor 18 | on | 18 | 18 | SE3 | 19 | 6.84 | Sun 00:15–04:45 | 6 / 4.43 | 16.0 / 16.0 |
| weekend comfort 21/19.5 | on | 18 | 22 | SE3 | 0 | 0.00 | – | 6 / 4.43 | **21.0** / 16.0 |
| weekend, flat price | on | 18 | 22 | flat | 0 | 0.00 | – | 4 / 3.78 | **21.0** / 16.0 |
| holiday on Sat, 21/19.5 | on | 18 | 22 | SE3 | 0 | 0.00 | – | 6 / 4.43 | **21.0** / 16.0 |
| recovery_active | on (recovering) | 18 | 22 | SE3 | 6 | 2.99 | Sat 00:45–02:00 | 35 / 9.98 | 21.0 / 17.0 |

Reading:
- **Null 1.** Away off schedules 6 slots (3.0 kWh) where away on schedules 0, so the setback does reach the solve.
- **Null 2.** A flat price also gives 0, so there is no price-driven pre-charge under away. (d) is refuted.
- **Indoor 18.** The plan holds the 16 °C floor only about 36 h out (from Sun 00:15). A stale reading of 18 would still not give "plenty" of near-term slots, so a stale *reading* does not explain the symptom on its own.
- **recovery_active.** This row is **byte-identical to away off**. While recovering, `solve_bands` drops the setback wholesale: the space floor goes back to 17, the comfort target to 21, and the DHW floor is restored. If the live state says `away_recovery_active: true`, then away is honoured in name and not in the plan.
- **DHW.** Away still plans 4–6 DHW slots (3.8–4.4 kWh). A reader of the plan could take these for heating, which is (e) in part.
- **Set point.** Moving the set point from 18 to 21 (away off) moves the plan from 6 to 35 slots, so the thermostat's set point does reach the plan through `target_temp`.

Raw output:
```
RESULT arm=away space_slots=0 space_kwh=0.0 first=- last=- weekend_slots=0 peak_kw=0.0 dhw_slots=6 dhw_kwh=4.43 room_min=17.37 room_max=22.13 comfort_fri=16.0 comfort_sat=16.0 floor_sat=16.0 status=optimal
RESULT arm=null_away_off space_slots=6 space_kwh=2.99 first=Sat 00:45 last=Sat 02:00 weekend_slots=6 peak_kw=2.61 dhw_slots=35 dhw_kwh=9.98 room_min=17.84 room_max=22.13 comfort_fri=21.0 comfort_sat=21.0 floor_sat=17.0 status=optimal
RESULT arm=away_off_setpoint21 space_slots=35 space_kwh=20.41 first=Sat 00:15 last=Sun 04:45 weekend_slots=35 peak_kw=4.43 dhw_slots=35 dhw_kwh=9.98 room_min=19.12 room_max=22.13 comfort_fri=21.0 comfort_sat=21.0 floor_sat=17.0 status=optimal
RESULT arm=null_flat space_slots=0 space_kwh=0.0 first=- last=- weekend_slots=0 peak_kw=0.0 dhw_slots=4 dhw_kwh=3.78 room_min=17.37 room_max=22.13 comfort_fri=16.0 comfort_sat=16.0 floor_sat=16.0 status=optimal
RESULT arm=indoor18 space_slots=19 space_kwh=6.84 first=Sun 00:15 last=Sun 04:45 weekend_slots=19 peak_kw=2.04 dhw_slots=6 dhw_kwh=4.43 room_min=16.0 room_max=18.36 comfort_fri=16.0 comfort_sat=16.0 floor_sat=16.0 status=optimal
RESULT arm=weekend space_slots=0 space_kwh=0.0 first=- last=- weekend_slots=0 peak_kw=0.0 dhw_slots=6 dhw_kwh=4.43 room_min=17.37 room_max=22.13 comfort_fri=16.0 comfort_sat=21.0 floor_sat=16.0 status=optimal
RESULT arm=weekend_flat space_slots=0 space_kwh=0.0 first=- last=- weekend_slots=0 peak_kw=0.0 dhw_slots=4 dhw_kwh=3.78 room_min=17.37 room_max=22.13 comfort_fri=16.0 comfort_sat=21.0 floor_sat=16.0 status=optimal
RESULT arm=weekend_away_off space_slots=6 space_kwh=2.99 first=Sat 00:45 last=Sat 02:00 weekend_slots=6 peak_kw=2.61 dhw_slots=35 dhw_kwh=9.98 room_min=17.84 room_max=22.13 comfort_fri=21.0 comfort_sat=21.0 floor_sat=17.0 status=optimal
RESULT arm=holiday space_slots=0 space_kwh=0.0 first=- last=- weekend_slots=0 peak_kw=0.0 dhw_slots=6 dhw_kwh=4.43 room_min=17.37 room_max=22.13 comfort_fri=16.0 comfort_sat=21.0 floor_sat=16.0 status=optimal
RESULT arm=recovery space_slots=6 space_kwh=2.99 first=Sat 00:45 last=Sat 02:00 weekend_slots=6 peak_kw=2.61 dhw_slots=35 dhw_kwh=9.98 room_min=17.84 room_max=22.13 comfort_fri=21.0 comfort_sat=21.0 floor_sat=17.0 status=optimal
VERDICT setpoint moves the space plan
VERDICT away removes all space heating
VERDICT weekend/holiday comfort REPLACES the away target (Sat 21.0 / 21.0 vs 16.0); extra space slots in this house: none
```

## Code chain (path:line at cf4f6b7)

1. **Toggle.** `switch.py:132-133`: `AwaySwitch.async_turn_on` calls `coordinator.async_set_away(active=True, refresh=False)` and then `publish_then_refresh(self)`. `coordinator.py:9640-9658`: `async_set_away` persists the override and calls `async_request_refresh` when refresh is true. The `set_away` service (`services.py:595-603`) refreshes too. **Both replan immediately**, behind HA's debounce, so (c) is not supported for these paths.
2. **Set point.** `climate.py:317-324` leads to `coordinator.py:3857-3889` (`async_set_target_temperature`), which writes `_opt_config.target_temp` and the entry options. The options write goes to `__init__.py:373-398` (`async_update_options`), and because the effective config differs, the entry **reloads**. The reload's first refresh republishes the **pre-reload plan** (`coordinator.py:~5857-5866`, `_reload_handover`: "the real solve follows in the background"). So for the window until that background solve publishes, the card shows the old plan. This is a candidate for the "set point lowered, plan unchanged" half.
3. **Presence-entity path.** There is **no state listener** on `away_presence_entity`: `coordinator.py` subscribes `async_track_state_change_event` only at 8423 (defrost) and 8468 (peak guard). An away flag that comes from a person, a calendar or an `input_boolean` presence entity reaches the plan only at the next scheduled update (`update_interval = optimization_interval`, `coordinator.py:3168-3170`, default 30 min). **This is (c) for that path.**
4. **Resolve.** `coordinator.py:6092` calls `_resolve_away` (`coordinator.py:9612-9632`) before the record. That calls `away.resolve` (`away.py:449-502`): the override or presence sets `active` and `target_temperature = away_temperature` (default 16). `_apply_return` (`away.py:428-446`) sets `recovery_active` and resets `target_temperature = comfort_temp` once `hours_left <= recovery_hours + 1`. `comfort_temp` comes from `get_comfort_temp(now.hour)` **without `when`** (`coordinator.py:9623`), so it ignores the weekend and holiday schedule.
5. **Bands.** `coordinator.py:5891-5951` (`_solve_hubs`, `banded=True` from `_solve_record`) calls `away.solve_bands` (`away.py:306-335`). When `active and not recovery_active`, it sets `target_temp`, `min_temp` and `comfort_temp_day/night` to the away target and lowers the DHW floors. It does **not** set `comfort_temp_day_weekend`, `comfort_temp_night_weekend`, `holiday_comfort_day` or `holiday_comfort_night` (`away.py:302`, `_OPT_FIELDS`).
6. **Per-step comfort.** `optimizer.py:3743-3793` (`_build_comfort_bounds`) calls `get_comfort_temp` and `get_temp_bounds` with `when=times[i]`, which reach `_comfort_pair` (`optimizer.py:1879-1905`). The holiday branch (1886-1895) and the weekend branch (1896-1904) substitute their own day and night values, **overriding the away setback** (the latent (b)). The floor is `min_temp`, and the T5 margins and mold floors may raise it (3770-3790; the harness passes none of them).
7. **Penalty.** The penalty is two-sided: undershoot and overshoot against the bounds (`optimizer.py:2466-2494`), plus a pull toward `comfort_targets` (2497). A comfort target set back to 16 at a room of 22 therefore buys no heat. This is consistent with the 0-slot row.

## What would settle it (the owner's diagnostics)

From the diagnostics bundle taken while the symptom shows:
- the **away view**: `away_active`, `away_source`, `away_override_active`, `away_return_time`, `away_hours_until_return`, `away_recovery_active`, `away_recovery_hours` and `away_target_temperature`. `recovery_active: true` or `away_active: false` settles it at once.
- the published plan: per-step **space** `power_schedule` and **`dhw_power_schedule`** with timestamps, so the slots can be split into space and DHW;
- the plan's solve timestamp (`last_optimization` / `_next_optimization`) against the time of the toggle and of the set-point change, to separate a stale plan or a reload handover from a fresh one;
- the configured `comfort_temp_day/night`, `*_weekend`, `holiday_calendar_entity`, `holiday_comfort_temp_*`, `away_temperature`, `min_temperature`, `mode` (economy) and `optimization_interval`, and whether away comes from the switch or from a presence entity;
- the room sensor's value and age, and any active manual plan pins or boost;
- if the bundle publishes them, the per-step comfort target and floor (`min_temp_margins`, mold floor).

Ranked candidates until then:
1. `recovery_active`: a return time inside the recovery estimate plus 1 h drops the setback wholesale. This matches the measured row exactly.
2. The plan was not yet replanned: the reload handover after the set-point change, or a presence-entity toggle waiting for the next interval.
3. DHW slots read as space heating.
4. A raised floor from margins or the mold guard. This one is not modelled.

## Fix briefs

- **Latent (b), weekend and holiday overriding away.** In `away.solve_bands`, while away and not recovering, also set `comfort_temp_day_weekend`, `comfort_temp_night_weekend`, `holiday_comfort_day` and `holiday_comfort_night` to the away target, wherever they are not None. Extend `_OPT_FIELDS` and the `_SetbackConfig` protocol to match. Test: this harness's `weekend` and `holiday` arms must read Saturday comfort 16.0. Make a failing test first, through `solve_bands` and `_build_comfort_bounds`, rather than a re-implemented formula.
- **(c) for the presence path**, if the diagnostics show away from a presence entity: subscribe `async_track_state_change_event` on `away_presence_entity`, and request a refresh on a change of the interpreted state. The defrost and peak-guard listeners at `coordinator.py:8423/8468` are the pattern.
- Whether recovery should drop the space setback **all at once** is a design question, not a defect, and it is not briefed here.

**Owning groups** (`dev/programme/rosters/wave-r10-groups.json` at `origin/handoff/audit-r10-roster`):
- `away.py` appears in **R10-LOOP-CPU** (S, `estimate_recovery_hours` off the loop) and in **R10-LIVESTATE** (XL, the coordinator move, with D1-s1-02 the torn away-override read). Neither owns the comfort-band seam.
- The weekend and holiday fix is a small leaf change to `away.solve_bands`, so it fits a **new hotfix group** (S). It has no ordering dependency beyond landing before or rebased under R10-LIVESTATE.
- The presence listener sits inside R10-LIVESTATE's coordinator move, so it should ride that group or follow it.

## Process notes

- The brief asks for the harness to be committed on a probe branch. The payload says "never write to any branch except your return refs" and "change no tracked file". I followed the payload: **no probe branch was pushed**, and the harness is carried in full below for the next seat to commit at `dev/audit/harnesses/r10_live_away_heating.py`. It needs classifying (closure or `INERT`) when it lands.
- Run it with: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_live_away_heating.py` (about 19 s).

## Harness

```python
#!/usr/bin/env python3
"""R10-LIVE-AWAY-HEATING: does away mode plan space heating at indoor 22 C?

WHY IT EXISTS. The owner (2026-10-30, a Friday): "Turning away mode on still
leaves plenty of heating slots in the plan, even though indoor temperature is
already 22 degrees and i also lowered the set point to 18."

Every arm builds the solve the way ``coordinator._solve_hubs`` does: the
configured ``OptimizationConfig.from_mapping``, then ``away.solve_bands``
(production) over it with an ``AwayState`` as ``away.resolve`` leaves it, the
bands replaced into a copy, and ``HeatPumpOptimizer.optimize``. The thermostat
set point is ``target_temp`` (``coordinator.async_set_target_temperature``
writes only that field). A 48 h horizon from Friday 12:00 crosses into Saturday.

Arms (one RESULT line each: space slots > 0.1 kW, kWh, first/last slot, DHW
slots and kWh, room min/max):

  away           away on, set point 18, indoor 22, two winter_typical days
  null_away_off  away off, set point 18, indoor 22 (null control 1)
  away_off_setpoint21  away off at set point 21: does the set point move the plan?
  null_flat      away on, flat price (null control 2)
  indoor18       away on, indoor 18 (stale-reading vs wrong-target split)
  weekend        away on, a configured weekend comfort schedule (21/19.5)
  weekend_flat   the same at a flat price
  holiday        away on, a holiday calendar covering Saturday with 21/19.5
  recovery       away with recovery_active (return inside the estimate)

    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_live_away_heating.py
"""
from __future__ import annotations

import copy
from dataclasses import replace
from datetime import datetime, timedelta

import numpy as np

from profiles import house, prices, solve_inputs, weather
from heatpump_optimizer import away as away_mode
from heatpump_optimizer.entry_config import EntryConfig
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState

START = datetime(2026, 10, 30, 12, 0)  # Friday, the report's day
SLOT_KW = 0.1


def _two_days(fn, profile):
    a = fn(profile, START)
    b = fn(profile, START + timedelta(hours=24))
    if isinstance(a, tuple):
        return tuple(np.concatenate([x, y]) for x, y in zip(a, b))
    return np.concatenate([a, b])


def _config(setpoint: float, **over) -> tuple[OptimizationConfig, ThermalParameters]:
    cfg = house(two_zone=False, dhw=True, target_temperature=setpoint, **over)
    opt = OptimizationConfig.from_mapping(EntryConfig.from_mapping(cfg))
    opt = replace(opt, horizon_hours=48, time_step_minutes=15)
    return opt, ThermalParameters.from_config(cfg)


def _away(active: bool, recovery: bool = False) -> away_mode.AwayState:
    cfg = away_mode.config_from_mapping({})
    if not active:
        return away_mode.AwayState()
    return away_mode.AwayState(
        active=True, source="service", recovery_active=recovery,
        target_temperature=21.0 if recovery else cfg.away_temperature,
        dhw_min_temperature=cfg.away_dhw_min_temperature,
    )


def run(name: str, *, active=True, setpoint=18.0, indoor=22.0, flat=False,
        recovery=False, holiday=False, **over) -> dict:
    opt_cfg, params = _config(setpoint, **over)
    if holiday:
        opt_cfg = replace(opt_cfg, holiday_dates=frozenset({(START + timedelta(days=1)).date()}),
                          holiday_comfort_day=21.0, holiday_comfort_night=19.5)
    bands, dhw = away_mode.solve_bands(opt_cfg, params, _away(active, recovery))
    config = replace(copy.deepcopy(opt_cfg), **bands)
    params = replace(copy.deepcopy(params), **dhw)
    model = ThermalModel(params)
    o, w, r, s = _two_days(weather, "shoulder")
    o = o - 4.0  # late-October Swedish, about 2 C mean
    pr = np.full(o.size, 1.2) if flat else _two_days(prices, "winter_typical")
    st = ThermalState(
        room_temperature=indoor, slab_temperature=indoor + 0.5, outdoor_temperature=float(o[0]),
        upper_floor_temperature=indoor, lower_floor_temperature=indoor,
        dhw_temperature=50.0, dhw_hours_since_legionella=20.0, buffer_tank_temperature=35.0,
    )
    res = HeatPumpOptimizer(model, config).optimize(inputs=solve_inputs(
        initial_state=st, prices=pr, outdoor_temps=o, wind_speeds=w, precipitation=r,
        solar_radiation=s, start_time=START))
    sp = np.asarray(res.power_schedule, float)
    dh = np.asarray(res.dhw_power_schedule or [0.0] * sp.size, float)
    on = np.flatnonzero(sp > SLOT_KW)
    ts = res.timestamps
    room = np.asarray(res.room_temp_trajectory, float)
    out = {
        "arm": name, "space_slots": int(on.size), "space_kwh": round(float(sp.sum() * 0.25), 2),
        "first": ts[on[0]].strftime("%a %H:%M") if on.size else "-",
        "last": ts[on[-1]].strftime("%a %H:%M") if on.size else "-",
        "weekend_slots": int(sum(1 for i in on if ts[i].weekday() >= 5)),
        "peak_kw": round(float(sp.max()), 2),
        "dhw_slots": int((dh > SLOT_KW).sum()), "dhw_kwh": round(float(dh.sum() * 0.25), 2),
        "room_min": round(float(room.min()), 2), "room_max": round(float(room.max()), 2),
        "comfort_fri": config.get_comfort_temp(14.0, START),
        "comfort_sat": config.get_comfort_temp(14.0, START + timedelta(days=1)),
        "floor_sat": config.get_temp_bounds(14.0, START + timedelta(days=1))[0],
        "status": res.status,
    }
    print("RESULT " + " ".join(f"{k}={v}" for k, v in out.items()), flush=True)
    return out


WEEKEND = {"comfort_temp_day_weekend": 21.0, "comfort_temp_night_weekend": 19.5}


def main() -> int:
    away = run("away")
    off18 = run("null_away_off", active=False)
    off21 = run("away_off_setpoint21", active=False, setpoint=21.0)
    run("null_flat", flat=True)
    run("indoor18", indoor=18.0)
    wk = run("weekend", **WEEKEND)
    run("weekend_flat", flat=True, **WEEKEND)
    run("weekend_away_off", active=False, **WEEKEND)
    hol = run("holiday", holiday=True)
    run("recovery", recovery=True)
    inert = (off18["space_slots"], off18["space_kwh"]) == (off21["space_slots"], off21["space_kwh"])
    print(f"VERDICT setpoint {'does NOT move the space plan (18 == 21)' if inert else 'moves the space plan'}")
    print(f"VERDICT away {'removes all space heating' if away['space_slots'] == 0 else 'leaves space heating'}")
    target_leak = wk["comfort_sat"] != away["comfort_sat"] or hol["comfort_sat"] != away["comfort_sat"]
    slot_leak = wk["weekend_slots"] > away["weekend_slots"] or hol["space_slots"] > away["space_slots"]
    print(f"VERDICT weekend/holiday comfort {'REPLACES' if target_leak else 'keeps'} the away target "
          f"(Sat {wk['comfort_sat']} / {hol['comfort_sat']} vs {away['comfort_sat']}); "
          f"extra space slots in this house: {'yes' if slot_leak else 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
