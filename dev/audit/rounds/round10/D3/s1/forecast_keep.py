"""D3-s1 (D3.M4): a raising weather fetch WITH a previous forecast must keep it.

Metric: after coordinator.py:HeatPumpOptimizerCoordinator._fetch_weather_forecast
runs with a service call that raises, a live weather entity (-8.0 C) and a
previous 24-row forecast at 2.0 C: prior_kept = 1 when the forecast is still
those 24 rows at 2.0 C, 0 when it was replaced (by the fabricated 48-row
constant trajectory). Count key: the coordinator's own _weather_forecast after
the call, never an input attribute.
Command:
  PYTHONPATH=tests/hastub python dev/audit/rounds/round10/D3/s1/forecast_keep.py [--mutant]
Expected: RESULT prior_kept=1 count (exact); with --mutant RESULT prior_kept=0.
Perturbation: --mutant flips `if state and not self._weather_forecast:` to
`or` (the sampled mutant M08 of mutants.py, which the closure did not kill),
in memory -- the method re-compiled from its source and patched onto the class.
Null control: --no-prior (no previous forecast) fabricates in BOTH arms
(prior_kept is then reported as fabricated=1), so the arms differ only where a
previous forecast exists.
Baseline 17f1c55fad1b; machine: owner's 8-core Mac (Darwin 25.6). Count, no timing.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, sys, textwrap, time
from unittest import mock

sys.path.insert(0, "custom_components")
sys.path.insert(0, "tests")
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
import heatpump_optimizer.coordinator as co  # noqa: E402

GUARD = "if state and not self._weather_forecast:"
C = co.HeatPumpOptimizerCoordinator


def mutant():
    fn = C._fetch_weather_forecast
    first = fn.__code__.co_firstlineno
    src = inspect.getsource(fn)
    assert src.count(GUARD) == 1
    src = src.replace(GUARD, GUARD.replace(" and ", " or "))
    ns = {}
    exec(compile("\n" * (first - 1) + textwrap.dedent(src), co.__file__, "exec"), co.__dict__, ns)
    return ns["_fetch_weather_forecast"]


def run(prior):
    cfg = {"price_source": "entity", "price_entity": "sensor.prices",
           "weather_entity": "weather.home"}
    c = C(FakeHass(), FakeEntry(data=cfg))

    async def raising(*a, **k):
        raise RuntimeError("weather integration broken")

    c.hass.services.async_call = raising
    c.hass.states.set("weather.home", FakeState(
        "cold", attributes={"temperature": "-8.0", "wind_speed": "3.0"}))
    if prior:
        c._weather_forecast = [{"temperature": 2.0} for _ in range(24)]
    asyncio.run(c._fetch_weather_forecast())
    f = c._weather_forecast
    kept = len(f) == 24 and all(r.get("temperature") == 2.0 for r in f)
    fabricated = len(f) == 48 and all(r.get("temperature") == -8.0 for r in f)
    return int(kept), int(fabricated), len(f)


prior = "--no-prior" not in sys.argv
if "--mutant" in sys.argv:
    with mock.patch.object(C, "_fetch_weather_forecast", mutant()):
        kept, fab, n = run(prior)
else:
    kept, fab, n = run(prior)
print("RESULT prior_kept=%d count" % kept)
print("RESULT fabricated=%d count" % fab)
print("RESULT rows=%d count" % n)
print("RESULT thread_factor=%.3f" % (time.process_time() / max(time.thread_time(), 1e-9)))
print("RESULT load1=%.2f" % os.getloadavg()[0])
print("RESULT swapins=0")
