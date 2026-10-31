"""D6-s2 harness: behaviour claims of docs/ecl110.md and docs/automations.md, driven.

Metric: count of the listed behaviour claims (CLAIMS below, each with its doc line) whose
executed check against the named production symbol disagrees with the doc sentence.
Key: the value the production symbol returns for the constructed input.

Checks and symbols:
  ecl110.md:15-16  ON threshold = max(0.1, 0.5*min power)  optimizer:HeatPumpOptimizer._power_to_heat_pump_schedule
  ecl110.md:21-23  weather bias over the first eight hours  optimizer:HeatPumpOptimizer._power_to_displace_schedule
  ecl110.md:130    lag moves interval/time-constant of the gap  optimizer:HeatPumpOptimizer._power_to_displace_schedule
  ecl110.md:27-28  curve bias only cools, <= 0.5 K per week     curve_learning:CurveLearner.record_day
  automations.md:60 economy: 1.5 C below the floor, never < 15  away:lower_floor (with const.ECONOMY_MIN_TEMP_WIDENING)
  automations.md:14-25 headroom min(fuse,threshold)-draw, clamp 0; tariff-only no-peak 0.0 + source text;
                   nothing bounds -> unavailable               coordinator:HeatPumpOptimizerCoordinator._power_headroom
  automations.md:7-10 entity ids fixed regardless of entry name  sensor/binary_sensor/switch/button/climate/datetime async_setup_entry

Command (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/s2/behaviour_claims.py
Perturbation: --perturb sets curve_learning.MAX_DOWN_PER_WEEK=1.0 and STEP_K=0.5 and
  const/away ECONOMY_ABSOLUTE_FLOOR=14.0 in memory; behaviour_claims_false must go up by >= 2.
Expected: see REPORT.md (exact).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud container, 4 CPU, Linux.
Root rule: ROOT = Path.cwd().
"""

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import importlib
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tests" / "hastub"))
_t0p, _t0t = time.process_time(), time.thread_time()

import numpy as np  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import away, const, curve_learning  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402

RESULTS = []


def claim(src, what, ok, detail=""):
    RESULTS.append((src, what, bool(ok), detail))


def optimizer(min_power=1.0, tau=1.5):
    p = ThermalParameters()
    p.min_electrical_power = min_power
    p.ecl110_pid_time_constant_hours = tau
    return HeatPumpOptimizer(ThermalModel(p), OptimizationConfig(horizon_hours=24, time_step_minutes=15))


def ecl110():
    for pmin in (1.0, 0.1, 3.0):
        opt = optimizer(min_power=pmin)
        thr = max(0.1, 0.5 * pmin)
        space = np.array([thr - 1e-3, thr, 0.0, 0.0])
        dhw = np.array([0.0, 0.0, thr - 1e-3, thr])
        on = opt._power_to_heat_pump_schedule(space, dhw)
        claim("docs/ecl110.md:15", f"ON threshold max(0.1, half min power) at min power {pmin}",
              on == [False, True, False, True], str(on))
    # weather bias over the first eight hours: alpha=1 (tau <= step) makes output = raw
    opt = optimizer(tau=0.1)
    n = 96
    power = np.full(n, 2.0)
    out = np.full(n, 10.0)
    base = opt._power_to_displace_schedule(power, out, {})
    windy = opt._power_to_displace_schedule(power, out, {"wind_anticipation_factor": 1.5})
    biased = [i for i in range(n) if abs(base[i] - windy[i]) > 1e-9]
    hours = len(biased) * opt.config.dt_hours
    claim("docs/ecl110.md:21", "weather anticipation bias applies over the first eight hours",
          hours == 8.0 and biased == list(range(len(biased))), f"{len(biased)} steps = {hours} h")
    # first-order lag: fraction interval / time constant of the remaining gap
    opt = optimizer(tau=1.5)
    d_max = opt.model.params.ecl110_displace_max
    step = opt._power_to_displace_schedule(np.full(8, opt.model.params.max_electrical_power), out[:8], {})
    frac = step[0] / d_max
    want = opt.config.dt_hours / 1.5
    claim("docs/ecl110.md:130", "lag moves interval/time-constant of the remaining distance",
          abs(frac - want) < 0.01, f"first-step fraction {frac:.4f} vs dt/tau {want:.4f} (dt={opt.config.dt_hours} h)")
    # curve bias: only cools, <= 0.5 K per week, over 70 comfortable days
    cl = curve_learning.CurveLearner()
    t0 = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
    worst_week = 0.0
    hist = []
    for d in range(70):
        cl.record_day(t0 + timedelta(days=d), 1.0)
        hist.append(cl.bias)
    for d in range(7, 70):
        worst_week = max(worst_week, hist[d - 7] - hist[d])
    print(f"RESULT curve_bias_max_7day_drop_k={worst_week:.3f} K")
    claim("docs/ecl110.md:31", "curve bias moves at most 0.5 K per week",
          worst_week <= 0.5 + 1e-9, f"largest 7-day drop {worst_week:.3f} K")
    claim("docs/ecl110.md:30", "curve bias may only cool (never > 0)",
          max(hist) <= 0.0 and min(hist) < 0.0, f"range [{min(hist):.2f}, {max(hist):.2f}]")


def economy():
    cfg = type("C", (), {})()
    for floor in (19.0, 16.0):
        cfg.min_temp = floor
        rec = type("R", (), {"written": {}})()
        away.lower_floor(rec, cfg, const.ECONOMY_MIN_TEMP_WIDENING)
        want = max(15.0, floor - 1.5)
        claim("docs/automations.md:60", f"economy: 1.5 C below floor {floor}, never below 15",
              abs(cfg.min_temp - want) < 1e-9, f"got {cfg.min_temp}")


def coord(extra):
    hass = FakeHass()
    hass.states.set("sensor.house", FakeState("3.0", unit="kW"))
    cfg = {"house_power_entity": "sensor.house", **extra}
    c = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))
    asyncio.run(c._update_current_state())
    return c


def headroom():
    c = coord({const.CONF_MAIN_FUSE_A: 16})
    h = c._power_headroom()
    claim("docs/automations.md:14", "fuse only: headroom = fuse - house draw",
          h.get("available") and abs(h["headroom_kw"] - round(max(0.0, c._fuse_kw() - 3.0), 3)) < 1e-6
          and h["limit_source"] == "main fuse", str(h)[:160])
    c = coord({const.CONF_PEAK_TARIFF_ENABLED: True})
    h = c._power_headroom()
    claim("docs/automations.md:19", "tariff only, no peak yet: 0.0 kW and the named limit_source",
          h.get("available") and h.get("headroom_kw") == 0.0
          and h.get("limit_source") == "capacity tariff with no peak reference yet", str(h)[:160])
    c = coord({})
    h = c._power_headroom()
    claim("docs/automations.md:23", "no fuse, no tariff: unavailable", h == {"available": False}, str(h))
    c = coord({const.CONF_MAIN_FUSE_A: 1})
    h = c._power_headroom()
    claim("docs/automations.md:15", "clamped at zero when the draw exceeds the limit",
          h.get("headroom_kw") == 0.0, str(h)[:120])


def entity_ids_ignore_name():
    def ids(name):
        hass = FakeHass()
        entry = FakeEntry(data={"name": name, "dhw_tank_volume": 180.0})
        entry.title = name
        c = HeatPumpOptimizerCoordinator(hass, entry)
        asyncio.run(c._update_current_state())
        entry.runtime_data = c
        added = []
        for plat in const.PLATFORMS:
            mod = importlib.import_module("heatpump_optimizer." + getattr(plat, "value", str(plat)).split(".")[-1].lower())
            asyncio.run(mod.async_setup_entry(hass, entry, lambda e, *a, **k: added.extend(e)))
        return {str(getattr(e, "entity_id", None)) for e in added}, len(added)
    a, n = ids("Heat Pump Optimizer")
    b, _ = ids("Villa Solbacken")
    off_prefix = sorted(x for x in b if not x.split(".", 1)[-1].startswith("heat_pump_optimizer"))
    claim("docs/automations.md:7", "entity ids fixed regardless of entry name",
          a == b and not off_prefix, f"{n} entities; differ {len(a ^ b)}; off-prefix {off_prefix[:5]}")


def main():
    patches = []
    if "--perturb" in sys.argv:
        # generic: must raise the false count
        patches += [mock.patch.object(curve_learning, "MAX_DOWN_PER_WEEK", 1.0),
                    mock.patch.object(curve_learning, "STEP_K", 0.5),
                    mock.patch.object(away, "ECONOMY_ABSOLUTE_FLOOR", 14.0)]
    if "--perturb-curve" in sys.argv:
        # the weekly cap measured over a sliding 7-day window: a cap of 0.3 K/week
        # in the per-step formula leaves every 7-day drop under 0.5 K
        patches += [mock.patch.object(curve_learning, "MAX_DOWN_PER_WEEK", 0.3)]
    for p in patches:
        p.start()
    try:
        ecl110()
        economy()
        headroom()
        entity_ids_ignore_name()
    finally:
        for p in patches:
            p.stop()
    for src, what, ok, det in RESULTS:
        print(f"{'true ' if ok else 'FALSE'} {src:24s} {what} -- {det}")
    print(f"RESULT behaviour_claims={len(RESULTS)} count")
    print(f"RESULT behaviour_claims_false={sum(not r[2] for r in RESULTS)} count")
    tp, tt = time.process_time() - _t0p, time.thread_time() - _t0t
    print(f"RESULT thread_factor={tp / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "na"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
