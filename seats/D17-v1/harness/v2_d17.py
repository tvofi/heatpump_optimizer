"""D17-v1 V2 independent harness: one arm per D17 finding, my own metrics.

Run from the private export copy root:
  PYTHONPATH=tests/hastub python3 $HOME/vout/D17-v1/harness/v2_d17.py <arm> [...]
Arms: s1-03 s1-04 s1-05 s2-01 s2-04 s3-01 s3-02 s3-03 s3-51 all
Each arm prints RESULT lines with its metric definition.
"""
import asyncio
import os
import sys
import time
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myrig  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from harness import FakeState  # noqa: E402


def plan_energy(data):
    s = data["schedule"]
    return sum(float(r["power"]) for r in s) * 0.25, s


# ---------------------------------------------------------------- s1-03 / s3-02
async def plan_with(data_extra, options=None):
    myrig.freeze()
    hass, entry, c = await myrig.setup(myrig.base_data(**data_extra), options)
    d = await myrig.solve(c)
    e, _ = plan_energy(d)
    return e, d.get("two_zone_enabled")


async def arm_s1_03():
    """Metric: |plan kWh(mass=40) - plan kWh(mass=10)| per zone mode, house_thermal_mass
    stored in options; two-zone off vs on (explicit) and auto (absent)."""
    for mode in ("off", "on", None):
        ex = {} if mode is None else {const.CONF_TWO_ZONE_MODE: mode}
        a, tz = await plan_with(ex, {"house_thermal_mass": 10.0})
        b, _ = await plan_with(ex, {"house_thermal_mass": 40.0})
        print(f"RESULT s1-03 mode={mode} two_zone={tz} kwh_m10={a:.4f} kwh_m40={b:.4f} delta={b - a:+.4f} kWh")


async def arm_s3_02():
    """Metric: plan kWh delta after a set_thermal_parameters service call
    (house_heat_loss_coefficient 0.35) vs before, per zone mode."""
    for mode in ("off", "on", None):
        ex = {} if mode is None else {const.CONF_TWO_ZONE_MODE: mode}
        myrig.freeze()
        hass, entry, c = await myrig.setup(myrig.base_data(**ex))
        d0 = await myrig.solve(c)
        e0, _ = plan_energy(d0)
        for fld, val in (("house_heat_loss_coefficient", 0.35), ("house_thermal_mass", 3.0)):
            try:
                await hass.services.async_call(const.DOMAIN, "set_thermal_parameters", {fld: val})
            except Exception as err:  # noqa: BLE001
                print("call failed", fld, type(err).__name__, err)
            await myrig.settle(hass)
            d1 = await myrig.solve(c)
            e1, _ = plan_energy(d1)
            print(f"RESULT s3-02 mode={mode} two_zone={d0.get('two_zone_enabled')} field={fld} "
                  f"kwh_before={e0:.4f} kwh_after={e1:.4f} delta={e1 - e0:+.4f} kWh")
            e0 = e1


# ---------------------------------------------------------------- s1-04
async def arm_s1_04():
    """Metric: declared_modulation per mode, and planned steps with 0.01<P<min (1.5 kW)
    when compressor_modulation and heat_pump_min_power are stored in the entry data."""
    from heatpump_optimizer.thermal_model import declared_modulation
    for mode in ("on_off", "modulating", "auto"):
        print(f"RESULT s1-04 declared_modulation({mode})={declared_modulation({const.CONF_COMPRESSOR_MODULATION: mode})}")
    for mode in ("on_off", "modulating"):
        myrig.freeze()
        hass = myrig.make_hass(indoor=20.0, outdoor=2.0)
        hass, entry, c = await myrig.setup(myrig.base_data(**{const.CONF_COMPRESSOR_MODULATION: mode,
                                                               const.CONF_HEAT_PUMP_MIN_POWER: 1.5}), hass=hass)
        d = await myrig.solve(c)
        pw = [float(r["power"]) for r in d["schedule"]]
        sub = sum(1 for x in pw if 0.01 < x < 1.5 - 1e-6)
        print(f"RESULT s1-04 mode={mode} sub_min_steps={sub} of {len(pw)}")


async def arm_s2_02():
    """Metric: schedule[0..3] outdoor input (result.outdoor_temps / published
    outdoor_forecast_temperature) and plan kWh with the outdoor sensor at -20/0/+8 C,
    a flat forecast of -5 C injected; null: no forecast."""
    for fc in (True, False):
        vals = []
        for reading in (-20.0, 0.0, 8.0):
            myrig.freeze()
            hass = myrig.make_hass(outdoor=reading)
            hass, entry, c = await myrig.setup(myrig.base_data(**{const.CONF_WEATHER_ENTITY: "weather.home"}), hass=hass)

            async def _noop(*a, **k):
                return None
            c._fetch_weather_forecast = _noop
            now = dt_util.now().replace(minute=0, second=0, microsecond=0)
            c._weather_forecast = ([{"datetime": (now + timedelta(hours=h)).isoformat(), "temperature": -5.0,
                                     "wind_speed": 2.0, "precipitation": 0.0, "humidity": 80.0} for h in range(48)]
                                   if fc else [])
            d = await myrig.solve(c)
            e, s = plan_energy(d)
            res = c._optimization_result
            o0 = float(res.outdoor_temps[0]) if res is not None and getattr(res, "outdoor_temps", None) is not None else None
            vals.append((reading, o0, e))
        sp = max(v[1] for v in vals) - min(v[1] for v in vals)
        ek = max(v[2] for v in vals) - min(v[2] for v in vals)
        print(f"RESULT s2-02 forecast={fc} step0_outdoor={[v[1] for v in vals]} spread={sp:.3f} K plan_kwh_spread={ek:.4f}")


# ---------------------------------------------------------------- s1-05
def arm_s1_05():
    """Metric: projection error of power_guard.project_window_mean for a steady draw P
    over a 60-min window (mean_so_far=P, current=P; the true billed mean is P).
    Count (P, minute) cells with |proj-P|/P > 5 %, minutes 1..59, P in {0.5,1,2,4,8}."""
    from heatpump_optimizer.power_guard import project_window_mean
    bad = tot = 0
    worst = 0.0
    for P in (0.5, 1.0, 2.0, 4.0, 8.0):
        for m in range(1, 60):
            pr = project_window_mean(P, m, P, 60)
            err = abs(pr - P) / P
            worst = max(worst, err)
            tot += 1
            bad += err > 0.05
    print(f"RESULT s1-05 cells_err_gt5pct={bad} of {tot}; worst_rel_err={worst:.3f}")
    print(f"RESULT s1-05 proj(P=3,m=1)={project_window_mean(3, 1, 3, 60):.3f} "
          f"proj(P=3,m=30)={project_window_mean(3, 30, 3, 60):.3f} proj(P=3,m=59)={project_window_mean(3, 59, 3, 60):.3f}")
    # null control: an empty window (no mean yet) should project the current draw
    print(f"RESULT s1-05 null proj(None,0,3)={project_window_mean(None, 0, 3, 60):.3f} (documented: 3.000)")


# ---------------------------------------------------------------- s2-01
async def arm_s2_01():
    """Metric: two_zone_enabled from from_config and published by the coordinator,
    for an entry with no zone key and mode absent / auto / off / on."""
    for mode in (None, "auto", "off", "on"):
        cfg = {} if mode is None else {const.CONF_TWO_ZONE_MODE: mode}
        p = ThermalParameters.from_config(cfg)
        e, tz = await plan_with(cfg)
        print(f"RESULT s2-01 mode={mode} from_config.two_zone={p.two_zone_enabled} published={tz}")
    p = ThermalParameters.from_config({const.CONF_UPPER_FLOOR_THERMAL_MASS: 5.0})
    print(f"RESULT s2-01 mode=None with_zone_key from_config.two_zone={p.two_zone_enabled}")


# ---------------------------------------------------------------- s2-04
async def arm_s2_04():
    """Metric: max planned kW inside a silent window 06-10 UTC with silent_mode_windows
    stored and the fraction absent (default) vs 0.5, vs no window."""
    out = {}
    for name, ex in (("none", {}), ("win", {"silent_mode_windows": "06:00-10:00"}),
                     ("win_f05", {"silent_mode_windows": "06:00-10:00", "silent_mode_power_fraction": 0.5})):
        myrig.freeze()
        # cold house so the plan wants full power early
        hass = myrig.make_hass(indoor=18.0, outdoor=-15.0)
        hass, entry, c = await myrig.setup(myrig.base_data(**ex), hass=hass)
        d = await myrig.solve(c)
        _, s = plan_energy(d)
        inside = [float(r["power"]) for r in s if 6 <= int(r["time"][11:13]) < 10 and r["time"][:10] == "2026-02-03"]
        out[name] = max(inside)
        print(f"RESULT s2-04 arm={name} max_kw_06_10={max(inside):.3f}")
    print(f"RESULT s2-04 cap_delta_default_fraction={out['win'] - out['none']:+.3f} kW; "
          f"with_fraction_0.5={out['win_f05'] - out['none']:+.3f} kW")


# ---------------------------------------------------------------- s3-01
async def arm_s3_01():
    """Metric: the published current_price and last_optimization after the price entity
    moves 1.0 -> 3.0 and (a) the run_optimization action, (b) the optimize-now button."""
    for arm in ("action", "button", "nothing"):
        myrig.freeze()
        hass, entry, c = await myrig.setup(myrig.base_data())
        d0 = await myrig.solve(c)
        p0, s0 = d0.get("current_price"), d0.get("last_optimization")
        myrig.freeze(myrig.T0 + timedelta(minutes=3))
        hass.states.set("sensor.spot", FakeState("3.0", attributes={"raw_today": myrig.prices(3.0)}))
        if arm == "action":
            await hass.services.async_call(const.DOMAIN, "run_optimization", {})
        elif arm == "button":
            from heatpump_optimizer import button
            ents = []
            await button.async_setup_entry(hass, entry, lambda es, *a, **k: ents.extend(es))
            b = [e for e in ents if "optimi" in (getattr(e, "entity_id", "") or getattr(e, "unique_id", "") or "").lower()
                 or "optimi" in type(e).__name__.lower()]
            for e in ents:
                e.hass = hass
            await b[0].async_press()
        await myrig.settle(hass)
        d1 = c.data
        print(f"RESULT s3-01 arm={arm} price {p0}->{d1.get('current_price')} "
              f"first_step_price={d1['schedule'][0]['price']} stamp_moved={d1.get('last_optimization') != s0}")


# ---------------------------------------------------------------- s3-03
def arm_s3_03():
    """Metric: best_restore() on rings holding one healthy snapshot whose accuracy
    temperature_bias is None / 0.1 / 5.0 / accuracy missing."""
    from heatpump_optimizer import snapshots
    for label, acc in (("bias_None", {"temperature_bias": None}), ("bias_0.1", {"temperature_bias": 0.1}),
                       ("bias_5", {"temperature_bias": 5.0}), ("no_accuracy", None), ("empty_accuracy", {})):
        ring = snapshots.SnapshotRing.__new__(snapshots.SnapshotRing)
        try:
            ring.__init__()
        except TypeError:
            pass
        ring.snapshots = [dict(taken_at="2026-02-01T00:00:00+00:00", healthy=True, **({"accuracy": acc} if acc is not None else {}))]
        ring.alarmed = False
        ring._streak_started = None
        r = ring.best_restore()
        print(f"RESULT s3-03 {label} best_restore_returns={'snapshot' if r else None}")


# ---------------------------------------------------------------- s3-51
async def arm_s3_51():
    """Metric: half-hour cells over a Mon..Sun week where the published
    dhw_in_demand_window disagrees with windows_for_day(weekday) for the spec
    'mon-fri 05:00-06:30, sat-sun 10:00-11:00' (my own spec). Null: flat '05:00-06:30'."""
    from heatpump_optimizer.dhw_schedule import windows_for_day, hour_in_windows
    for spec in ("weekdays 05:00-06:30, weekend 10:00-11:00", "05:00-06:30"):
        myrig.freeze()
        hass, entry, c = await myrig.setup(myrig.base_data(**{const.CONF_DHW_TANK_VOLUME: 200.0,
                                                               const.CONF_DHW_WINDOWS: spec}))
        p = c._thermal_params if hasattr(c, "_thermal_params") else None
        from heatpump_optimizer.coordinator import _ctx_of
        p = _ctx_of(c)._thermal_params
        wrong = cells = 0
        monday = myrig.T0 - timedelta(days=1)  # 2026-02-02 Monday
        for day in range(7):
            for half in range(48):
                t = monday + timedelta(days=day, minutes=30 * half)
                dt_util.freeze(t)
                pub = bool(c._dhw_in_demand_window())
                wins = windows_for_day(p.dhw_weekly_windows, t.weekday(), p.dhw_windows) if p.dhw_weekly_windows else p.dhw_windows
                truth = bool(hour_in_windows(t.hour + t.minute / 60.0, wins))
                cells += 1
                wrong += pub != truth
        print(f"RESULT s3-51 spec={spec!r} cells_wrong={wrong} of {cells}")


async def arm_s3_51b():
    """As s3-51 but a solve runs at the start of each day (00:05) and every 30 min
    thereafter the cell is checked (no re-solve): post-solve published flag."""
    from heatpump_optimizer.dhw_schedule import windows_for_day, hour_in_windows
    from heatpump_optimizer.coordinator import _ctx_of
    spec = "weekdays 05:00-06:30, weekend 10:00-11:00"
    myrig.freeze()
    hass, entry, c = await myrig.setup(myrig.base_data(**{const.CONF_DHW_TANK_VOLUME: 200.0, const.CONF_DHW_WINDOWS: spec}))
    p = _ctx_of(c)._thermal_params
    monday = myrig.T0 - timedelta(days=1) - timedelta(hours=6)
    wrong = cells = 0
    resolve_each = "--hourly" in sys.argv
    for day in range(7):
        for half in range(48):
            t = monday + timedelta(days=day, minutes=30 * half)
            dt_util.freeze(t)
            if half == 0 or (resolve_each and half % 2 == 0):
                hass.states.set("sensor.spot", FakeState("1.0", attributes={"raw_today": myrig.prices(1.0)}))
                await c.async_refresh()
            pub = bool(c.data.get("dhw_in_demand_window"))
            pub2 = bool(c._dhw_in_demand_window())
            wins = windows_for_day(p.dhw_weekly_windows, t.weekday(), p.dhw_windows)
            truth = bool(hour_in_windows(t.hour + t.minute / 60.0, wins))
            cells += 1
            wrong += pub2 != truth
    print(f"RESULT s3-51b post-solve(resolve_each_hour={resolve_each}) cells_wrong={wrong} of {cells} "
          f"published_dhw_windows={c.data.get('dhw_windows')!r}")


ARMS = {"s2-02": arm_s2_02, "s3-51b": arm_s3_51b, "s1-03": arm_s1_03, "s1-04": arm_s1_04, "s1-05": arm_s1_05, "s2-01": arm_s2_01,
        "s2-04": arm_s2_04, "s3-01": arm_s3_01, "s3-02": arm_s3_02, "s3-03": arm_s3_03, "s3-51": arm_s3_51}

if __name__ == "__main__":
    t0, c0 = time.process_time(), time.thread_time()
    names = sys.argv[1:] or ["all"]
    if names == ["all"]:
        names = list(ARMS)
    for n in names:
        try:
            r = ARMS[n]()
            if asyncio.iscoroutine(r):
                asyncio.run(r)
        except Exception as err:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            print(f"RESULT {n} ERROR {type(err).__name__}: {err}")
    pc, tc = time.process_time() - t0, time.thread_time() - c0
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1:.3f} load1={os.getloadavg()[0]:.2f}")
