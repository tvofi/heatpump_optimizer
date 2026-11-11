#!/usr/bin/env python3
"""D1-s5 (round 9, D1.M3): inputs.age_of vs InputReader's own age rule.

Metric (one line): over a grid of sensor states, the number of cells where the
value the coordinator DELIVERS through `inputs.age_of` (the DHW inlet probe
via `coordinator._dhw_inlet_c`, the indoor humidity via
`HeatPumpOptimizerCoordinator._indoor_humidity_value`) disagrees with the
freshness verdict `inputs.InputReader._age_minutes` reaches on the same state
object at the same instant with the same limit.

Count key: the delivered value (None vs a number) from the production seam,
compared against InputReader's verdict on the identical State; never an
attribute of the input records.

Two arms, one mechanism (age_of reads last_updated, never last_reported,
and has no guard against a stamp ahead of the clock):
  reported  - a live sensor re-reporting an unchanged value: last_reported =
              now - 1 min, last_updated = now - X min. Real Home Assistant
              moves last_reported on every write and last_updated only on a
              state/attribute change. Divergence = delivered None while the
              reader calls the reading fresh.
  future    - last_reported = last_updated = now + X min (a backward host
              clock step, #775). Divergence = delivered a number while the
              reader refuses the stamp (age None -> stale).

Command:
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s5/age_of_divergence.py [--perturb]
  --perturb swaps coordinator.age_of for a one-line-fixed copy (prefer
  last_reported, refuse a negative age) in memory: both counts go to 0.

Expected (baseline): RESULT reported_divergent=7 cells (of 12), future_divergent=6 cells
(of 6), control_divergent=0 cells (of 12), exact.  With --perturb: 0, 0, 0.
Null control: the same grid with last_reported == last_updated (a sensor whose
value changes on every write), where both rules must agree: 0 divergent cells.
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud container
(box B5, Linux x86_64), Python 3.14 venv. Counts are contention-immune.
Root rule: imports from the working directory (run from the export root).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys
import time
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, ".")
sys.path.insert(0, "tests")

_p0, _t0 = time.process_time(), time.thread_time()

from homeassistant.util import dt as dt_util  # noqa: E402
from harness import FakeHass, FakeState  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as coord  # noqa: E402
from custom_components.heatpump_optimizer import inputs  # noqa: E402

NOW = datetime(2026, 1, 15, 3, 0, tzinfo=timezone.utc)
PERTURB = "--perturb" in sys.argv


def _fixed_age_of(state, now):
    """inputs.age_of with the reader's rule: last_reported first, no negative."""
    stamp = (getattr(state, "last_reported", None)
             or getattr(state, "last_updated", None)
             or getattr(state, "last_changed", None))
    if not isinstance(stamp, datetime) or stamp.tzinfo is None or now.tzinfo is None:
        return None
    age = now - stamp
    return None if age < timedelta(0) else age


def _reader_fresh(state, limit_min):
    """InputReader's verdict on the same State: True fresh, False stale/refused."""
    r = inputs.InputReader(FakeHass({}), {}, now=lambda: NOW)
    age = r._age_minutes(state)
    if age is None:
        return False  # future stamp: #775 treats it as stale
    return age <= limit_min


def _deliver_inlet(state):
    hass = FakeHass({"sensor.inlet": state})
    return coord._dhw_inlet_c(hass, "sensor.inlet")


def _deliver_humidity(state):
    hass = FakeHass({"sensor.rh": state})
    ns = SimpleNamespace(
        hass=hass,
        _config={coord.CONF_INDOOR_HUMIDITY_ENTITY: "sensor.rh"},
    )
    return coord.HeatPumpOptimizerCoordinator._indoor_humidity_value(ns)


SEAMS = (
    ("dhw_inlet", _deliver_inlet, "8.0", "°C", coord.DHW_INLET_MAX_AGE_MINUTES),
    ("humidity", _deliver_humidity, "72", "%", coord.HUMIDITY_MAX_AGE_MINUTES),
)
# Per seam: minutes since the value last CHANGED, bracketing each limit.
REPORTED_X = {
    "dhw_inlet": (60, 600, 1400, 1500, 2000, 4000),
    "humidity": (30, 100, 130, 240, 480, 900),
}
FUTURE_X = (5, 60, 600)


def run():
    reported = future = cells_r = cells_f = control = cells_c = 0
    dt_util.freeze(NOW)
    try:
        for name, deliver, raw, unit, limit in SEAMS:
            for x in REPORTED_X[name]:
                st = FakeState(raw, unit=unit,
                               last_updated=NOW - timedelta(minutes=x),
                               last_reported=NOW - timedelta(minutes=1))
                got = deliver(st)
                fresh = _reader_fresh(st, limit)
                cells_r += 1
                bad = (got is None) and fresh
                reported += bad
                print(f"  reported {name:9s} changed {x:5d} min ago: delivered={got!r:6} "
                      f"reader_fresh={fresh} {'DIVERGES' if bad else ''}")
            for x in REPORTED_X[name]:
                st = FakeState(raw, unit=unit,
                               last_updated=NOW - timedelta(minutes=x),
                               last_reported=NOW - timedelta(minutes=x))
                got = deliver(st)
                fresh = _reader_fresh(st, limit)
                cells_c += 1
                control += (got is None) == fresh
            for x in FUTURE_X:
                st = FakeState(raw, unit=unit,
                               last_updated=NOW + timedelta(minutes=x),
                               last_reported=NOW + timedelta(minutes=x))
                got = deliver(st)
                fresh = _reader_fresh(st, limit)
                cells_f += 1
                bad = (got is not None) and not fresh
                future += bad
                print(f"  future   {name:9s} stamp +{x:4d} min:         delivered={got!r:6} "
                      f"reader_fresh={fresh} {'DIVERGES' if bad else ''}")
    finally:
        dt_util.freeze(None)
    return reported, cells_r, future, cells_f, control, cells_c


def _swapins():
    try:
        with open("/proc/vmstat") as f:
            for line in f:
                if line.startswith("pswpin"):
                    return int(line.split()[1])
    except OSError:
        pass
    return -1


if __name__ == "__main__":
    print(f"arm: {'PERTURBED (age_of fixed in memory)' if PERTURB else 'baseline'}")
    if PERTURB:
        with mock.patch.object(coord, "age_of", _fixed_age_of):
            r, cr, f, cf, c, cc = run()
    else:
        r, cr, f, cf, c, cc = run()
    print(f"RESULT reported_divergent={r} cells (of {cr})")
    print(f"RESULT future_divergent={f} cells (of {cf})")
    print(f"RESULT control_divergent={c} cells (of {cc})")
    p, t = time.process_time() - _p0, time.thread_time() - _t0
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={_swapins()}")
