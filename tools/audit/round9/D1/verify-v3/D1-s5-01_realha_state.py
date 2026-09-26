#!/usr/bin/env python3
"""V3 (round 9) D1-s5-01 reach on REAL Home Assistant: State objects produced by the
genuine StateMachine (homeassistant.core), fed to the two production age_of
consumers (coordinator._dhw_inlet_c, HeatPumpOptimizerCoordinator._indoor_humidity_value)
and to InputReader._age_minutes.

Metric (one line): of the cells below, the count where the consumer DELIVERS None
while InputReader._age_minutes (same State, same instant, same limit) judges the
sensor fresh, or delivers a number while the reader returns None (future stamp).
Arms: reported - value written at now-X, the SAME value re-written at now-1 min
(real HA moves last_reported only); future - value written with a stamp now+D
(what a backward host-clock step leaves); control - value CHANGED at now-1 min.
Command:  PYTHONPATH=. /root/venvha/bin/python tools/audit/round9/D1/verify-v3/D1-s5-01_realha_state.py [--perturb]
  --perturb: coordinator.age_of replaced by the reader's rule (last_reported first,
  negative age -> None); divergent must go to 0.
Environment shim: typing.ByteString aliased to bytes before importing HA (CPython
3.14.0rc2 removed it; mashumaro in HA 2026.2.3 needs it). Not a product change.
Expected: measured, exact.  Baseline SHA 1936d5ca (evidence tree).  HA 2026.2.3.
Machine: cloud 4-core box, CPython 3.14.0rc2 (V3 sub-seat for G1).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import typing  # noqa: E402
if not hasattr(typing, "ByteString"):
    typing.ByteString = bytes

import asyncio  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from datetime import timedelta  # noqa: E402
from types import SimpleNamespace  # noqa: E402

sys.path.insert(0, ".")
t_proc0, t_thr0 = time.process_time(), time.thread_time()

from homeassistant.core import HomeAssistant  # noqa: E402
import homeassistant.const as hac  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as C  # noqa: E402
from custom_components.heatpump_optimizer import inputs as I  # noqa: E402

assert "tests/hastub" not in " ".join(sys.path)
PERTURB = "--perturb" in sys.argv
if PERTURB:
    def _fixed(state, now):
        stamp = (getattr(state, "last_reported", None) or getattr(state, "last_updated", None)
                 or getattr(state, "last_changed", None))
        if stamp is None or stamp.tzinfo is None or now.tzinfo is None:
            return None
        age = now - stamp
        return None if age.total_seconds() < 0 else age
    C.age_of = _fixed


def reader_fresh(state, limit_min):
    age = I.InputReader._age_minutes(SimpleNamespace(_utcnow=dt_util.utcnow), state)
    return age is not None and age <= limit_min


async def main():
    hass = HomeAssistant(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
    now = time.time()
    rows = []
    consumers = [
        ("humidity", "sensor.hum", "45.0", C.HUMIDITY_MAX_AGE_MINUTES,
         lambda: C.HeatPumpOptimizerCoordinator._indoor_humidity_value(
             SimpleNamespace(hass=hass, _config={C.CONF_INDOOR_HUMIDITY_ENTITY: "sensor.hum"}))),
        ("dhw_inlet", "sensor.inlet", "9.0", C.DHW_INLET_MAX_AGE_MINUTES,
         lambda: C._dhw_inlet_c(hass, "sensor.inlet")),
    ]
    for name, eid, val, limit, deliver in consumers:
        for arm, first_age_min, second in (
            ("reported", 1.5 * limit, "same"), ("reported", 3 * limit, "same"),
            ("reported", 0.5 * limit, "same"),
            ("future", -10.0, None), ("future", -120.0, None),
            ("control", 1.5 * limit, "changed"), ("control", 0.5 * limit, "changed"),
        ):
            hass.states.async_remove(eid)
            hass.states.async_set(eid, val, {"unit_of_measurement": "%" if name == "humidity" else "°C"},
                                  timestamp=now - first_age_min * 60.0)
            if second == "same":
                hass.states.async_set(eid, val, {"unit_of_measurement": "%" if name == "humidity" else "°C"},
                                      timestamp=now - 60.0)
            elif second == "changed":
                hass.states.async_set(eid, str(float(val) + 1), {"unit_of_measurement": "%" if name == "humidity" else "°C"},
                                      timestamp=now - 60.0)
            st = hass.states.get(eid)
            delivered = deliver()
            fresh = reader_fresh(st, limit)
            div = (delivered is None) == fresh
            rows.append((name, arm, first_age_min, st.last_updated, st.last_reported, delivered, fresh, div))
    await hass.async_stop(force=True)
    return rows


rows = asyncio.run(main())
print(f"HA {hac.__version__} perturb={PERTURB}")
agg = {}
for name, arm, a, lu, lr, dv, fr, div in rows:
    print(f"  {name:9s} {arm:8s} first_at=-{a:.0f}min last_updated={lu.isoformat(timespec='seconds')} "
          f"last_reported={lr.isoformat(timespec='seconds')} delivered={dv} reader_fresh={fr} divergent={div}")
    k = arm
    agg.setdefault(k, [0, 0])
    agg[k][0] += int(div)
    agg[k][1] += 1
for k, (d, n) in agg.items():
    print(f"RESULT realha_{k}_divergent={d} cells (of {n})")
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=" + next((ln.split()[1] for ln in open("/proc/vmstat") if ln.startswith("pswpin")), "unknown"))
