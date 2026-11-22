#!/usr/bin/env python3
# Metric: whether a fire-and-forget background task still pending at unload has finished when
#   HeatPumpOptimizerCoordinator.async_shutdown returns (task_done 1/True = shutdown awaited it), for a 0.3 s task.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_94285425.py
# Expected: RESULT task_done_baseline=True, mutant=False (the unload returns with the save still running); null_moved=0.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g11 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator.async_shutdown
#   (line 6615, `        if pending:`), on tests/features.py:_r9f13_make's coordinator rig; the task is an asyncio.sleep
#   registered in coord._background_tasks the way _spawn registers its tasks.
# Perturbation: mutant 94285425a1bc856a, `if pending:` -> `if False:`, in memory (the method recompiled from its own
#   source in the module namespace). Direction: True -> False: the docstring's "still-pending fire-and-forget tasks are
#   awaited (a capped wait)" no longer holds, so a reload can start while the old entry's save is still writing.
# Null control: a task already done before shutdown (0 s sleep, awaited once): both arms report it done.
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

OLD = "if pending:"
NEW = "if False:"
TASK_S, NULL_S, CASE, METRIC, IDX, NULL_NAME = 0.3, 0.0, "pending_task", "task_done", 0, "already-done task"

import logging

ha_dt.freeze(NOW)
t0, t1 = time.process_time(), time.thread_time()
# zero-argument super() needs a class cell a recompiled function lacks: the explicit two-argument form is identical here
MUT = mutate(CLS.async_shutdown, OLD, NEW)
_g = MUT.__globals__
exec(compile(textwrap.dedent(inspect.getsource(CLS.async_shutdown)).replace(OLD, NEW, 1).replace("super()", "super(HeatPumpOptimizerCoordinator, self)"), co.__file__, "exec"), _g)
MUT = _g["async_shutdown"]


class _Count(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING)
        self.hits = 0

    def emit(self, record):
        if "did not finish within 5 s" in record.getMessage():
            self.hits += 1


def shut(fn, task_s):
    _, c = make("sd")
    h = _Count()
    co._LOGGER.addHandler(h)

    async def main():
        task = asyncio.get_running_loop().create_task(asyncio.sleep(task_s))
        if task_s == 0:
            await task  # the null: a task already finished before the unload
        c._background_tasks.add(task) if isinstance(c._background_tasks, set) else c._background_tasks.append(task)
        await fn(c)
        done = task.done()
        task.cancel()
        return done

    try:
        return asyncio.run(main()), h.hits
    finally:
        co._LOGGER.removeHandler(h)


b, m = shut(CLS.async_shutdown, TASK_S), shut(MUT, TASK_S)
print(f"RESULT {CASE}_baseline=task_done:{b[0]} warnings:{b[1]} mutant=task_done:{m[0]} warnings:{m[1]}")
print(f"RESULT {METRIC}_baseline={b[IDX]} mutant={m[IDX]}")
b, m = shut(CLS.async_shutdown, NULL_S), shut(MUT, NULL_S)
print(f"RESULT null_moved={int(b[IDX] != m[IDX])} count  ({NULL_NAME}: baseline {b}, mutant {m})")
ha_dt.freeze(None)
tail_results(t0, t1)
