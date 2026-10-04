"""R9-DIAG-1 replay: two days of repeated space-boost channel use against the
real learners, the real optimizer and the real drift alarm.

Run from the repository root:

    ~/.local/state/hpo/venv-ci/bin/python tools/audit/round9/prestudy/boost_drift_replay.py

What it drives, per 30-minute cycle, in the production order
(`_async_update_data`'s order, minus the network fetches):

1. the clock is frozen at t; the fake bus carries the indoor, outdoor and
   power entities, reading what the true house did over the interval that
   just elapsed;
2. ``_update_current_state`` -- which is where every interval learner runs
   (house heat loss, COP, curve comfort, flow lift), replaying the elapsed
   interval through the coordinator's live model with ``_current_action``
   still holding the previous cycle's overlaid action;
3. a real ``HeatPumpOptimizer.optimize`` solve over the same model the
   learners update, whose result is adopted as the plan and whose
   trajectory is what ``_predicted_next_room_temp`` will read;
4. ``boost.apply`` -- the space channel overlay (nameplate power, max-temp
   setpoint) laid on a copy of the plan, exactly as the switch does;
5. the true house (a second ``ThermalModel`` with the true parameters)
   advances one step under the ACTUATED action, with a thermostat cap at
   the action's setpoint;
6. ``_record_accuracy`` -- pairing the previous interval's plan-based
   prediction with the boosted reality;
7. once per calendar day, ``_async_watch_learning_drift`` -- the #42
   heartbeat that takes weekly snapshots, counts out-of-band bias days and
   raises the "Learned model is drifting" repair issue.

The true house and the configured model share a parameter set when the arm
says so (``true=1.0``); otherwise the true heat loss is higher and the
learners have real work to do both before and after the boost days.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests/hastub")
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import asyncio
import json

import numpy as np

import homeassistant.util.dt as dt_mod
from harness import FakeEntry, FakeHass, FakeState

from heatpump_optimizer import boost as boost_mod
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

UTC = timezone.utc
DT_MIN = float(__import__("os").environ.get("DIAG_DT_MIN", 30.0))
STEP_MIN = 30.0         # solver time step, minutes
DAYS = 16
START = datetime(2026, 1, 5, 0, 0, tzinfo=UTC)

# Boost days (0-indexed from START): tvofi used boost "a few times over two
# days" after 1-2 weeks of running.  Days 8-9 of a 16-day run; the heavier
# variants (DIAG_BOOST_DAYS) stretch the same usage across more days.
BOOST_DAYS = tuple(
    int(d) for d in __import__("os").environ.get("DIAG_BOOST_DAYS", "8,9").split(",")
    if d.strip()
)
BOOST_STARTS = (7.0, 12.0, 18.0)   # local hours
BOOST_HOURS = 2.0


def day_arrays(day_index: int):
    """Prices (SEK/kWh) and weather for one day, at the solver's step."""
    n = int(24 * 60 / STEP_MIN)
    h = np.arange(n) * (STEP_MIN / 60.0)
    # Nord-pool-ish: cheap night, morning and evening peaks.
    p = np.full(n, 1.05)
    p[(h >= 0) & (h < 5)] = 0.62
    p[(h >= 7) & (h < 10)] = 2.35
    p[(h >= 16) & (h < 20)] = 2.85
    p[h >= 23] = 0.78
    # A cold but not extreme January day, repeating with a slow multi-day
    # swing so the learner never sees an identical day twice.
    base = -6.0 + 3.0 * np.sin((day_index / 4.0) * np.pi / 2.0)
    t_out = base + 4.0 * np.sin((h - 14.0) / 24.0 * 2 * np.pi)
    solar = np.clip(45.0 * np.sin((h - 8.5) / 7.0 * np.pi), 0.0, None)
    wind = np.full(n, 2.0)
    rain = np.zeros(n)
    return p, t_out, solar, wind, rain


def build_house(true_loss_scale: float) -> ThermalModel:
    cfg = {
        "target_temperature": 21.0, "min_temperature": 20.0,
        "max_temperature": 23.0, "heat_pump_max_power": 6.0,
        "heat_pump_min_power": 1.0,
    }
    params = ThermalParameters.from_config(cfg)
    params.heat_loss_coefficient = params.heat_loss_coefficient * true_loss_scale
    params.dhw_enabled = False
    return ThermalModel(params)


def weather_now(day_index: int, hour: float):
    """The TRUE outdoor temperature and solar at an instant.

    Same formulas as ``day_arrays``, evaluated continuously, so the sensor
    readings, the house's experience and the solve's perfect forecast are
    one weather."""
    base = -6.0 + 3.0 * np.sin((day_index / 4.0) * np.pi / 2.0)
    t_out = base + 4.0 * np.sin((hour - 14.0) / 24.0 * 2 * np.pi)
    solar = float(np.clip(45.0 * np.sin((hour - 8.5) / 7.0 * np.pi), 0.0, None))
    return float(t_out), solar


def build_coord():
    cfg = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        "heat_pump_power_entity": "sensor.hp_power",
        "solar_radiation_entity": "sensor.solar",
        "optimization_interval": DT_MIN,
    }
    coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
    coord._snapshots_loaded = True
    return coord


def run(arm: str, true_loss_scale: float, boosts: bool, mode_boost: bool = False):
    coord = build_coord()
    ctx = getattr(coord, "_ctx", coord)
    house = build_house(true_loss_scale)
    # The solve uses the coordinator's own live model: the one the learners
    # keep correcting.
    opt_cfg = OptimizationConfig(
        horizon_hours=24.0,
        time_step_minutes=STEP_MIN,
        target_temp=21.0, min_temp=20.0, max_temp=23.0,
    )
    optimizer = HeatPumpOptimizer(coord._thermal_model, opt_cfg)

    house_state = ThermalState(room_temperature=20.5, outdoor_temperature=-6.0)
    draw = 0.0                      # what the pump drew over the last interval
    daily = []                      # per-day summary rows
    interval_rows = []              # per-interval sample-level rows
    day_index = -1
    boost_tag = False               # whether the interval just elapsed was boosted
    n_cycles = int(DAYS * 24 * 60 / DT_MIN)

    for i in range(n_cycles):
        t = START + timedelta(minutes=i * DT_MIN)
        if t.date() != (t - timedelta(minutes=DT_MIN)).date():
            day_index += 1
        dt_mod.freeze(t)
        h_now = t.hour + t.minute / 60.0
        outdoor_now, solar_now = weather_now(day_index, h_now)
        # -- the bus carries what the house just did ----------------------
        coord.hass.states.set(
            "sensor.indoor",
            FakeState(f"{house_state.room_temperature:.3f}", last_updated=t,
                      unit="°C"),
        )
        coord.hass.states.set(
            "sensor.outdoor",
            FakeState(f"{outdoor_now:.3f}", last_updated=t, unit="°C"),
        )
        coord.hass.states.set(
            "sensor.hp_power",
            FakeState(f"{draw:.3f}", last_updated=t, unit="kW"),
        )
        coord.hass.states.set(
            "sensor.solar",
            FakeState(f"{solar_now:.2f}", last_updated=t, unit="W/m²"),
        )
        # -- learners replay the elapsed interval --------------------------
        asyncio.run(coord._update_current_state())
        # -- the plan (a real solve on the live model) ----------------------
        # Two days of arrays, sliced from the current half-hour, so the
        # horizon starts at now the way the production forecast does.
        step_idx = int(round(h_now * 60.0 / STEP_MIN))
        p, t_out, solar, wind, rain = day_arrays(day_index)
        p2, t_out2, solar2, wind2, rain2 = day_arrays(day_index + 1)
        p = np.concatenate([p, p2])[step_idx:]
        t_out = np.concatenate([t_out, t_out2])[step_idx:]
        solar = np.concatenate([solar, solar2])[step_idx:]
        wind = np.concatenate([wind, wind2])[step_idx:]
        rain = np.concatenate([rain, rain2])[step_idx:]
        result = optimizer.optimize(
            ctx._current_state,
            prices=p, outdoor_temps=t_out,
            wind_speeds=wind, precipitation=rain, solar_radiation=solar,
            start_time=t,
        )
        coord._optimization_result = result
        power0 = float(result.power_schedule[0])
        boost_mod.adopt_plan(coord, {
            "power": power0,
            "setpoint": 23.0,
            "mode": "auto",
            "power_normalized": power0 / 6.0,
            "heat_pump_on": power0 > 0.05,
            "displace_value": 0.0,
            "space_reason": "plan",
        })
        # -- the boost channel, as the switch leaves it --------------------
        boosting = boosts and (
            day_index in BOOST_DAYS
            and any(s <= t.hour + t.minute / 60.0 < s + BOOST_HOURS
                    for s in BOOST_STARTS)
        )
        if mode_boost:
            # the global-mode arm: same windows through the mode select
            coord._mode = "boost" if boosting else "auto"
        held = boost_mod.held_for(coord)
        if boosting and "space" not in held.until:
            held.until["space"] = t + timedelta(hours=BOOST_HOURS)
        elif not boosting:
            held.until.pop("space", None)
        boost_mod.apply(coord)
        # -- actuate: the true house answers the overlaid action -----------
        act = coord._current_action
        want = float(act.get("power", 0.0))
        setpoint = float(act.get("setpoint", 23.0))
        # thermostat cap: the pump stops at its setpoint
        applied = want if house_state.room_temperature < setpoint - 0.1 else 0.0
        if boosting and house_state.room_temperature >= setpoint - 0.1:
            # modulating near the ceiling rather than fully off
            applied = want * 0.35
        prev_room = house_state.room_temperature
        house_state = house.simulate_step(
            house_state, applied, outdoor_now,
            wind_speed=2.0, precipitation=0.0,
            solar_radiation=solar_now, dt_hours=DT_MIN / 60.0,
            hour_of_day=h_now,
        )
        house_state.outdoor_temperature = outdoor_now
        draw = applied
        # -- close the loop on the prediction ------------------------------
        coord._record_accuracy()
        sample = coord._accuracy.samples[-1] if coord._accuracy.samples else None
        if sample is not None and sample.predicted_temp is not None:
            interval_rows.append({
                "t": t.isoformat(timespec="minutes"),
                "boost": boost_tag,
                "pred": sample.predicted_temp,
                "act": sample.actual_temp,
                "err": round(sample.predicted_temp - sample.actual_temp, 3)
                        if sample.actual_temp is not None else None,
                "outdoor": sample.outdoor_temp,
                "pred_kw": sample.predicted_power_kw,
                "act_kw": sample.actual_power_kw,
                "room": round(house_state.room_temperature, 3),
            })
        boost_tag = boosting
        # -- the daily heartbeat, once per calendar day --------------------
        if t.hour == 3 and t.minute == 0:
            asyncio.run(coord._async_watch_learning_drift())
            daily.append({
                "day": day_index,
                "bias": coord._accuracy.temperature_bias(),
                "mae": coord._accuracy.temperature_mae(),
                "samples": len(coord._accuracy.samples),
                "hh_scale": round(coord._house_heat_loss_scale, 4),
                "cop_scale": round(coord._cop_scale, 4),
                "alarmed": coord._snapshot_ring.alarmed,
                "bias_days": coord._snapshot_ring._bias_days,
                "vent_tripped": coord._vent_cusum.tripped,
                "vent_stat": round(coord._vent_cusum.stat, 3),
                "freeze_reason": coord._learner_freeze_reason,
                "trust": round(coord._accuracy.trust(), 3),
            })
            print(f"[{arm}] day {day_index} bias={daily[-1]['bias']} "
                  f"hh={daily[-1]['hh_scale']} alarmed={daily[-1]['alarmed']}",
                  flush=True)
    issues = [
        (i[1], i[2].get("translation_key"))
        for i in getattr(coord.hass, "issues", [])
        if i[1] == "accuracy_drift"
    ]
    return {
        "arm": arm,
        "daily": daily,
        "issues": issues,
        "alarmed": coord._snapshot_ring.alarmed,
        "rollback_done": coord._rollback_done_for_alarm,
        "hh_scale_final": coord._house_heat_loss_scale,
        "cop_scale_final": coord._cop_scale,
        "interval_rows": interval_rows,
    }


def summarise(out: dict) -> None:
    print(f"\n=== arm {out['arm']} ===")
    print(f"{'day':>3} {'bias':>7} {'mae':>7} {'n':>4} {'hh':>7} {'cop':>6} "
          f"{'alarmed':>7} {'days':>4}")
    for d in out["daily"]:
        print(f"{d['day']:>3} {str(d['bias']):>7} {str(d['mae']):>7} "
              f"{d['samples']:>4} {d['hh_scale']:>7} {d['cop_scale']:>6} "
              f"{str(d['alarmed']):>7} {d['bias_days']:>4}")
    boosted = [r["err"] for r in out["interval_rows"] if r["boost"] and r["err"] is not None]
    plain = [r["err"] for r in out["interval_rows"] if not r["boost"] and r["err"] is not None]
    if boosted:
        print(f"boost-interval errors: n={len(boosted)} "
              f"mean={np.mean(boosted):+.3f} min={min(boosted):+.3f} max={max(boosted):+.3f}")
    if plain:
        print(f"non-boost errors:      n={len(plain)} mean={np.mean(plain):+.3f}")
    print(f"alarmed={out['alarmed']} rolled_back={out['rollback_done']} "
          f"hh_final={out['hh_scale_final']:.4f} cop_final={out['cop_scale_final']:.4f}")
    print(f"accuracy_drift issues raised: {out['issues']}")


if __name__ == "__main__":
    arms = {
        "null-no-boost": (1.0, False, False),
        "boost-model-correct": (1.0, True, False),
        "boost-model-wrong15": (1.15, True, False),
        "global-mode-boost-null": (1.0, True, True),
    }
    import os
    outdir = os.environ.get("DIAG_OUT", "/tmp/r9-diag-1")
    os.makedirs(outdir, exist_ok=True)
    # One arm per process (argv[1]), or all four serially.
    todo = sys.argv[1:] or list(arms)
    for arm in todo:
        scale, boosts, mode_boost = arms[arm]
        out = run(arm, scale, boosts, mode_boost)
        summarise(out)
        with open(f"{outdir}/{arm}.json", "w") as f:
            json.dump(out, f, indent=1, default=str)
        print(f"written: {outdir}/{arm}.json", flush=True)
