"""#290 judge instrument: event-loop starvation while a solve holds the GIL.

Recreated from the #290 judge comment (the file is not on main). A real
asyncio loop, a 1 ms heartbeat coroutine, ``HeatPumpOptimizer.optimize``
submitted the same way production submits it — never FakeHass, whose
executor runs inline and would measure nothing.

Prefix (required; OpenBLAS reads the pin at import):

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \\
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \\
      python3 tools/audit/round2/D9/j5_gil.py

Routes:
  J5_ROUTE=thread       ThreadPoolExecutor(1) + run_in_executor (pre-fix)
  J5_ROUTE=production   coordinator._await_optimize (the shipped path)

Arms: idle (null, no solve), two_zone_dhw, dhw_cap_zero_range (D9-01),
and the inverted switch-interval lever 5 ms -> 0.5 ms on two_zone_dhw.

Metric: starvation share = sum(gaps > 5 ms) / solve wall; longest hold =
max gap; gap_p50 = median heartbeat gap. Heartbeat period 1 ms.
"""
from __future__ import annotations

import asyncio
import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor

for _threads in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_threads, "1")

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "tests", "hastub"))
sys.path.insert(0, os.path.join(ROOT, "custom_components"))

import numpy as np  # noqa: E402

from profiles import DT, house, prices, weather  # noqa: E402
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer,
    OptimizationConfig,
)
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

START = __import__("datetime").datetime(2026, 1, 15, 0, 0)
SEASON_PRICES, SEASON_WEATHER = "winter_typical", "winter_cold"
GAP_CUTOFF = 0.005
HEARTBEAT = 0.001
IDLE_SECONDS = 2.0
ROUTE = os.environ.get("J5_ROUTE", "production")


class LoopHass:
    """The HA wait-point: a real thread pool, never FakeHass."""

    def __init__(self, loop: asyncio.AbstractEventLoop, pool: ThreadPoolExecutor) -> None:
        self.loop = loop
        self.pool = pool

    async def async_add_executor_job(self, func, *args):
        return await self.loop.run_in_executor(self.pool, func, *args)


def load1() -> float:
    try:
        return float(os.getloadavg()[0])
    except OSError:
        return float("nan")


def result(name, value, unit) -> None:
    if isinstance(value, float):
        text = f"{value:.6g}"
    else:
        text = str(value)
    print(f"RESULT {name}={text} {unit}", flush=True)


def make_solve(*, power_cap_kw: float | None = None):
    """two_zone_dhw inputs; optional flat cap is the D9-01 zero-range path."""
    cfg = house(two_zone=True, dhw=True)
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = True
    opt_cfg = OptimizationConfig(
        horizon_hours=24,
        time_step_minutes=15,
        target_temp=cfg["target_temperature"],
        min_temp=cfg["min_temperature"],
        max_temp=cfg["max_temperature"],
    )
    n = int(24 / DT)

    def fit(arr):
        arr = np.asarray(arr, dtype=float)
        if len(arr) >= n:
            return arr[:n]
        return np.tile(arr, int(np.ceil(n / len(arr))))[:n]

    price_series = fit(prices(SEASON_PRICES, START))
    outdoor, wind, rain, solar = (fit(a) for a in weather(SEASON_WEATHER, START))
    initial = ThermalState(
        room_temperature=21.0,
        slab_temperature=22.0,
        outdoor_temperature=float(outdoor[0]),
        upper_floor_temperature=21.0,
        lower_floor_temperature=21.0,
        dhw_temperature=50.0,
        dhw_hours_since_legionella=20.0,
        buffer_tank_temperature=40.0,
    )
    caps = None if power_cap_kw is None else np.full(n, float(power_cap_kw))
    optimizer = HeatPumpOptimizer(ThermalModel(params), opt_cfg)
    return optimizer, initial, price_series, outdoor, wind, rain, solar, caps


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    k = (len(ordered) - 1) * p
    lo = int(k)
    hi = min(lo + 1, len(ordered) - 1)
    frac = k - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


async def heartbeat(stop: asyncio.Event, stamps: list[float]) -> None:
    while not stop.is_set():
        stamps.append(time.perf_counter())
        try:
            await asyncio.wait_for(stop.wait(), timeout=HEARTBEAT)
        except asyncio.TimeoutError:
            continue


async def submit_optimize(hass: LoopHass, packed) -> None:
    optimizer, state, price_series, outdoor, wind, rain, solar, caps = packed
    if ROUTE == "thread":
        await hass.loop.run_in_executor(
            hass.pool,
            lambda: optimizer.optimize(
                state, price_series, outdoor, wind, rain, solar, START,
                None, None, None, None, None, None, caps,
            ),
        )
        return
    from heatpump_optimizer.coordinator import _await_optimize

    await _await_optimize(
        hass,
        optimizer,
        state,
        price_series,
        outdoor,
        wind,
        rain,
        solar,
        START,
        None,
        None,
        None,
        None,
        None,
        None,
        caps,
    )


async def measure_arm(name: str, packed, *, duration: float | None = None) -> dict:
    loop = asyncio.get_running_loop()
    pool = ThreadPoolExecutor(max_workers=1)
    hass = LoopHass(loop, pool)
    stop = asyncio.Event()
    stamps: list[float] = []
    hb = asyncio.create_task(heartbeat(stop, stamps))
    await asyncio.sleep(0.05)
    t0 = time.perf_counter()
    if packed is None:
        await asyncio.sleep(duration or IDLE_SECONDS)
    else:
        await submit_optimize(hass, packed)
    wall = time.perf_counter() - t0
    t1 = t0 + wall
    stop.set()
    await hb
    pool.shutdown(wait=False)
    in_window = [s for s in stamps if t0 <= s <= t1]
    gaps = [b - a for a, b in zip(in_window, in_window[1:])]
    over = [g for g in gaps if g > GAP_CUTOFF]
    share = (sum(over) / wall) if wall > 0 else 0.0
    longest = max(gaps) if gaps else 0.0
    p50 = statistics.median(gaps) if gaps else float("nan")
    p99 = _percentile(gaps, 0.99)
    ticks = (len(in_window) / wall) if wall > 0 else 0.0
    out = {
        "share": share,
        "longest_ms": longest * 1000.0,
        "p50_ms": p50 * 1000.0,
        "p99_ms": p99 * 1000.0,
        "wall_s": wall,
        "ticks": ticks,
        "n_gaps": len(gaps),
    }
    result(f"{name}.starvation_share", share, "1")
    result(f"{name}.longest_gil_hold_ms", out["longest_ms"], "ms")
    result(f"{name}.gap_p50_ms", out["p50_ms"], "ms")
    result(f"{name}.gap_p99_ms", out["p99_ms"], "ms")
    result(f"{name}.wall_s", wall, "s")
    result(f"{name}.ticks_per_second", ticks, "1/s")
    return out


async def main() -> None:
    import sys as _sys

    result("route", ROUTE, "enum")
    result("load1", load1(), "1")
    result("py", _sys.version.split()[0], "semver")

    print("-- idle (null, no solve)", flush=True)
    await measure_arm("idle", None)

    print("-- two_zone_dhw", flush=True)
    packed = make_solve()
    await measure_arm("two_zone_dhw", packed)

    print("-- dhw_cap_zero_range (D9-01, 0.8*p_max)", flush=True)
    p_max = packed[0].model.params.max_electrical_power
    await measure_arm("dhw_cap_zero_range", make_solve(power_cap_kw=0.8 * p_max))

    if ROUTE == "thread":
        print("-- perturbation switchinterval 5ms -> 0.5ms on two_zone_dhw", flush=True)
        prev = _sys.getswitchinterval()
        try:
            _sys.setswitchinterval(0.0005)
            await measure_arm("switchinterval_0.5ms", make_solve())
        finally:
            _sys.setswitchinterval(prev)


if __name__ == "__main__":
    asyncio.run(main())
