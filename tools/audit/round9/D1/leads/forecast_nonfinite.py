"""D1-s2 lead probe: one non-finite value in one stored weather-forecast row reaches the solve.

Metric: of 7 non-finite arms (temperature nan/+inf/-inf, wind_speed nan/+inf, precipitation nan,
humidity nan), count cycles whose async_run_optimization
publishes a plan with status starting 'failed' or returns 'solve_failed'/raises. Count key: the
coordinator's own published OptimizationResult.status / return value.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/leads/forecast_nonfinite.py [--scrub]
Positive control: temperature -1e308 (D1-s2-02's finite row) -> failed, so the injected row reaches
the solve. Null control: a -4.0 row -> optimal. Expected: failed_arms=0 of 7 (non-finding).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine B10 cloud container.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _rig  # noqa: E402
import asyncio, math

SCRUB = "--scrub" in sys.argv
ARMS = [("temperature", float("nan")), ("temperature", float("inf")), ("temperature", float("-inf")),
        ("wind_speed", float("nan")), ("wind_speed", float("inf")), ("precipitation", float("nan")),
        ("humidity", float("nan")), ("temperature", -1e308), ("temperature", -4.0)]


def run():
    bad = []
    for key, val in ARMS:
        _rig.freeze()
        hass, entry, coord = _rig.make_coord()
        coord._weather_forecast[5][key] = val
        if SCRUB:
            for row in coord._weather_forecast:
                for k in list(row):
                    if isinstance(row[k], float) and not math.isfinite(row[k]):
                        del row[k]
        status = "?"

        async def go():
            await coord._update_current_state()
            return await coord.async_run_optimization()
        try:
            ret = asyncio.run(go())
            res = coord._optimization_result
            status = ret or (res.status if res is not None else "none")
        except Exception as err:  # noqa: BLE001
            status = f"raised {type(err).__name__}"
        failed = status.startswith("failed") or status in ("solve_failed", "none") or status.startswith("raised")
        bad.append(failed)
        print(f"RESULT arm_{key}_{val}={status}")
    print(f"RESULT failed_arms={sum(bad[:-2])} of_{len(ARMS) - 2}")
    print(f"RESULT positive_control_failed={int(bad[-2])} of_1  (finite -1e308, D1-s2-02's row: the rig reaches the solve)")
    print(f"RESULT control_failed={int(bad[-1])} of_1")


run()
_rig.tail()
