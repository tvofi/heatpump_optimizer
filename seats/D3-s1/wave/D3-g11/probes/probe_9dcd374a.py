#!/usr/bin/env python3
# Metric: whether the what-if payload HeatPumpOptimizerCoordinator.async_simulate returns carries the key
#   "power_cap_breach_c" (1 = present, with its value), for a what-if that does NOT cap power ({"target_temperature": 22.0}).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_9dcd374a.py
# Expected: RESULT no_cap_breach_key_baseline=0, mutant=1 (value 0.0); null_moved=0 (a power_cap_kw what-if carries the
#   key in both arms).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g11 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator.async_simulate
#   (line 11271, `                if "power_cap_kw" in overrides and simulated.predictive_info`), driven after one real
#   async_run_optimization on tests/features.py:_r9f13_make's rig (frozen clock, in-process solve), limited=False.
# Perturbation: mutant 9dcd374ac007dfc9, `and` -> `or`, in memory (the method recompiled from its own source in the module
#   namespace). Direction: key absent -> present on every uncapped what-if (predictive_info is never empty after a solve),
#   so the payload claims a power-cap comfort breach field for a what-if that set no cap (the comment at
#   coordinator.py:11265 says the key is "present only when the what-if capped power").
# Null control: {"power_cap_kw": 3.0}, where both arms carry the key with the same value.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from pathlib import Path

ROOT = Path.cwd()  # run from the repository root (harness contract)
assert (ROOT / "custom_components/heatpump_optimizer/manifest.json").is_file(), "run from the repository root"
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402


def mutate(fn, old, new, name=None):
    """Recompile fn's own source with the one-line mutant, in the module namespace (in memory)."""
    src = textwrap.dedent(inspect.getsource(fn))
    assert src.count(old) == 1, f"anchor moved: {old!r}"
    ns = dict(co.__dict__)
    exec(compile(src.replace(old, new, 1), co.__file__, "exec"), ns)
    return ns[name or fn.__name__]


def tail_results(t0_cpu, t0_thr):
    import time
    pc, tc = time.process_time() - t0_cpu, time.thread_time() - t0_thr
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        for ln in open("/proc/vmstat"):
            if ln.startswith("pswpin "):
                sw = int(ln.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw} count")

import asyncio
import time
from datetime import datetime, timedelta, timezone
from unittest import mock
from homeassistant.util import dt as ha_dt
from custom_components.heatpump_optimizer import const as hc
from custom_components.heatpump_optimizer.optimizer import optimize_in_process
from tests.harness import FakeEntry, FakeHass, FakeState

NOW = datetime(2026, 1, 15, 6, 0, tzinfo=timezone.utc)
CLS = co.HeatPumpOptimizerCoordinator


def make(entry_id, price_hours=50, price_start_h=-2):
    """tests/features.py:_r9f13_make's rig: injected hourly prices and flat weather, fetches no-ops."""
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.0"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    entry = FakeEntry(data={hc.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
                            hc.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor"}, entry_id=entry_id)
    coord = CLS(hass, entry)
    coord._prices = [{"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
                      "starts_at": (NOW + timedelta(hours=h + price_start_h)).isoformat(), "level": "NORMAL"}
                     for h in range(price_hours)]
    coord._weather_forecast = [{"datetime": (NOW + timedelta(hours=h)).isoformat(), "temperature": -5.0,
                                "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0} for h in range(48)]

    async def noop(*_a, **_k):
        return None

    coord._fetch_tibber_prices = coord._fetch_weather_forecast = coord._fetch_solar_forecast = noop
    return hass, coord


SOLVES = []


async def inline(hass, optimizer, inputs):
    """The in-process solve, counted (features.py's _r9f13_inline)."""
    SOLVES.append(len(inputs.forecast.prices))
    return optimize_in_process(optimizer, inputs)


def run(fn, coord, *args, patches=None, **kwargs):
    """Await fn(coord, *args, **kwargs) with patches on the module and on a mutant's own namespace copy."""
    patches = dict(patches or {})
    patches.setdefault("_await_optimize", inline)
    g = fn.__globals__
    own = g is not co.__dict__ and "HeatPumpOptimizerCoordinator" in g
    saved = {k: g[k] for k in patches} if own else {}
    try:
        if own:
            g.update(patches)
        with mock.patch.multiple(co, **patches):
            return asyncio.run(fn(coord, *args, **kwargs))
    finally:
        g.update(saved)


PRICE_CASES = {  # (hours of hourly prices, first start relative to NOW in hours)
    "no_prices": (0, 0), "one_hour_from_now": (1, 0), "two_hours_from_now": (2, 0), "past_only": (50, -60),
    "head_2h_past": (50, -2), "tail_23h": (2, 22), "day_and_half": (36, 0),
}

ha_dt.freeze(NOW)
t0, t1 = time.process_time(), time.thread_time()
MUT = mutate(CLS.async_simulate, 'if "power_cap_kw" in overrides and simulated.predictive_info',
             'if "power_cap_kw" in overrides or simulated.predictive_info')


def key_of(fn, overrides):
    _, c = make("sim")
    assert run(CLS.async_run_optimization, c) is None
    p = run(fn, c, dict(overrides), limited=False)
    assert "error" not in p, p
    return (1, p["power_cap_breach_c"]) if "power_cap_breach_c" in p else (0, None)


for name, ov in {"no_cap": {"target_temperature": 22.0}, "no_cap_empty": {}}.items():
    b, m = key_of(CLS.async_simulate, ov), key_of(MUT, ov)
    print(f"RESULT {name}_breach_key_baseline={b[0]} mutant={m[0]} (mutant value {m[1]})")
b, m = key_of(CLS.async_simulate, {"power_cap_kw": 3.0}), key_of(MUT, {"power_cap_kw": 3.0})
print(f"RESULT null_moved={int(b != m)} count  (capped: {b})")
ha_dt.freeze(None)
tail_results(t0, t1)
