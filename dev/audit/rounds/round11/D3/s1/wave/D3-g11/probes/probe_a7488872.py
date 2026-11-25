#!/usr/bin/env python3
# Metric: per price input, the forecast horizon length HeatPumpOptimizerCoordinator._forecast_arrays delivers
#   (len(prices)) and the outcome of async_run_optimization on it (None = solved and published, "no_prices" = refused),
#   baseline arm against mutant arm.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_a7488872.py
# Expected: lengths_seen={0, 96} (the price series is either empty or padded to opt_config.n_steps = 24 h / 15 min);
#   moved_production=0 count; only a non-production 1 h horizon (n_steps = 4, set by replace on _opt_config; no
#   config path sets horizon_hours, optimizer.py:2666 default 24.0) moves: baseline None -> mutant "no_prices".
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g11 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator.async_run_optimization
#   (line 6379, `            if len(prices) < 4:`), driven on tests/features.py:_r9f13_make's rig (injected hourly
#   prices, flat weather, frozen clock 2026-01-15 06:00Z), solving in process (features.py's _r9f13_inline transport).
# Perturbation: mutant a7488872387d5ca7, `len(prices) < 4` -> `len(prices) <= 4`, in memory (the method recompiled from its
#   own source in the module namespace). Direction: none on production horizons (equivalent-candidate); the 1 h arm is
#   the sensitivity control showing the probe can move.
# Null control: the 5-step (1.25 h) horizon, where both arms solve.
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


def run(fn, coord, **patches):
    """Await fn(coord) with patches applied to the module and to a mutant's own namespace copy."""
    patches.setdefault("_await_optimize", inline)
    g = fn.__globals__
    saved = {k: g[k] for k in patches if g is not co.__dict__}
    try:
        if g is not co.__dict__:
            g.update(patches)
        with mock.patch.multiple(co, **patches):
            return asyncio.run(fn(coord))
    finally:
        g.update(saved)


PRICE_CASES = {  # (hours of hourly prices, first start relative to NOW in hours)
    "no_prices": (0, 0), "one_hour_from_now": (1, 0), "two_hours_from_now": (2, 0), "past_only": (50, -60),
    "head_2h_past": (50, -2), "tail_23h": (2, 22), "day_and_half": (36, 0),
}

from dataclasses import replace

ha_dt.freeze(NOW)
t0, t1 = time.process_time(), time.thread_time()
MUT = mutate(CLS.async_run_optimization, "if len(prices) < 4:", "if len(prices) <= 4:")


def outcome(fn, hours, start, horizon=None):
    _, c = make(f"p{hours}_{start}", hours, start)
    if horizon is not None:
        c._opt_config = replace(c._opt_config, horizon_hours=horizon)
    n = len(c._forecast_arrays(ha_dt.now()).prices)
    return n, run(fn, c)


seen, moved = set(), 0
for name, (h, s) in PRICE_CASES.items():
    (n, b), (_, m) = outcome(CLS.async_run_optimization, h, s), outcome(MUT, h, s)
    seen.add(n)
    moved += int(b != m)
    print(f"RESULT {name}_len={n} baseline={b!r} mutant={m!r}")
print(f"RESULT lengths_seen={sorted(seen)}")
print(f"RESULT moved_production={moved} count")
(n, b), (_, m) = outcome(CLS.async_run_optimization, 50, -2, 1.0), outcome(MUT, 50, -2, 1.0)
print(f"RESULT sensitivity_1h_horizon_len={n} baseline={b!r} mutant={m!r}  (not a production horizon)")
(n, b), (_, m) = outcome(CLS.async_run_optimization, 50, -2, 1.25), outcome(MUT, 50, -2, 1.25)
print(f"RESULT null_moved={int(b != m)} count  (len={n})")
ha_dt.freeze(None)
tail_results(t0, t1)
