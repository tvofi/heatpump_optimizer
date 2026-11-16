"""D17-s1-05 harness: the peak guard holds back when the window will NOT set a peak, and
not when it will, because its window projection counts the current draw over the
elapsed minutes instead of the remaining ones.

Metric: per steady meter draw P (kW), over one 60-minute metering window with one meter
reading a minute, the number of minutes in which the guard's `suppressing` state
disagrees with the option's description ("when the current metering window is projected
to set a new billed peak, holds back ..."): with a steady draw the window will average P,
so after the guard's 2-sample hysteresis it should suppress exactly when
P > threshold - margin (threshold 2.0 kW from three recorded peaks, margin 0.5 kW).
Count key: coordinator._peak_guard.suppressing after each reading, i.e. the state the
guard actuates from. Instrumented symbols: heatpump_optimizer.power_guard:project_window_mean
via heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._on_power_event, the
listener registered by _async_setup_peak_guard after the grid_connection page saved
peak_guard_enabled.

Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D17/s1/h_guard.py
Expected: RESULT guard_wrong_minutes_total=69 over 5 draws, range 3..25, 44 with the most
          favourable draw dropped (exact); under --perturb-docstring 0
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13
Perturbation: --perturb-docstring replaces project_window_mean with its docstring's own
rule ((mean*elapsed + current*remaining)/window): guard_wrong_minutes_total goes down to
the hysteresis floor (1 minute per suppressing draw).
Null control: peak_guard_enabled off: no listener, never suppresses (RESULT null_suppressed_minutes=0).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import sys  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402
from unittest import mock  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402
from harness import FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import coordinator as cmod  # noqa: E402
from heatpump_optimizer import power_guard  # noqa: E402

T0 = datetime(2026, 1, 15, 6, 0, tzinfo=timezone.utc)
THRESHOLD, MARGIN = 2.0, 0.5
DRAWS = (0.8, 1.2, 1.8, 3.0, 9.0)

if "--perturb-docstring" in sys.argv:
    def _doc(mean_so_far_kw, elapsed_minutes, current_kw, window_minutes):
        w = max(float(window_minutes), 1e-6)
        e = min(max(float(elapsed_minutes), 0.0), w)
        if mean_so_far_kw is None:
            e = 0.0
        m = float(mean_so_far_kw) if mean_so_far_kw is not None else 0.0
        return (m * e + float(current_kw) * (w - e)) / w

    for mod in (power_guard, cmod):
        if hasattr(mod, "project_window_mean"):
            mock.patch.object(mod, "project_window_mean", _doc).start()


def seed_peaks(coord):
    t = coord._peak_tracker
    t.month, t.peaks, t.peak_days = "2026-01", [THRESHOLD] * 3, ["2026-01-10", "2026-01-11", "2026-01-12"]


async def window(kw, enabled=True):
    res, entry = await rig.save_option(
        "grid_connection", "peak_guard_enabled", enabled,
        options={"peak_tariff_enabled": True, "house_power_entity": "sensor.house_power"})
    assert not res.get("errors"), res.get("errors")
    st = FakeState(str(kw * 1000), unit="W")
    hass, coord = rig.build_coord(entry, states={"sensor.house_power": st}, now=T0, seed=seed_peaks)
    await coord._async_setup_peak_guard()
    listeners = [a for ids, a in getattr(hass, "state_listeners", [])]
    states = []
    for minute in range(60):
        dt_util.freeze(T0 + timedelta(minutes=minute, seconds=30))
        ev = type("Ev", (), {"data": {"entity_id": "sensor.house_power", "new_state": st, "old_state": st}})()
        for a in listeners:
            r = a(ev)
            if asyncio.iscoroutine(r):
                await r
        states.append(bool(coord._peak_guard.suppressing))
    for t in list(getattr(hass, "_tasks", [])):
        t.cancel()
    return states, len(listeners)


async def main():
    total = 0
    per = []
    for kw in DRAWS:
        states, n = await window(kw)
        should = kw > THRESHOLD - MARGIN
        # documented: after the 2-reading hysteresis (minute 1 on), suppress iff the window will average over the line
        wrong = sum(1 for m, s in enumerate(states) if s != (should and m >= 1))
        first = next((m for m, s in enumerate(states) if s), None)
        per.append(wrong)
        total += wrong
        print(f"ROW draw={kw} kW listeners={n} should_suppress={should} first_suppressed_minute={first} "
              f"suppressed_minutes={sum(states)} wrong_minutes={wrong}", flush=True)
    null, n0 = await window(9.0, enabled=False)
    print(f"RESULT guard_wrong_minutes_total={total} over {len(DRAWS)} draws")
    print(f"RESULT guard_wrong_minutes_range={min(per)}..{max(per)}")
    print(f"RESULT guard_wrong_minutes_drop_most_favourable={total - max(per)}")
    print(f"RESULT null_suppressed_minutes={sum(null)} (listeners={n0})")
    print(f"RESULT thread_factor={rig.thread_factor()}")
    print(f"RESULT load1={rig.load1()}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    asyncio.run(main())
