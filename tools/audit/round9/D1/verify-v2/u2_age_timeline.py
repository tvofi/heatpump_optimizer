#!/usr/bin/env python3
"""V2 (D1-2) own harness for D1-s5-01: age_of's freshness rule on a simulated timeline.

Metric A (last_reported arm): a live sensor holds one value for H hours while re-reporting
  every 5 min (last_reported moves each write, last_updated stays at the hold start, as real
  HA writes it). Sampled every 15 min across the hold, count samples where the coordinator seam
  (coordinator:_dhw_inlet_c / HeatPumpOptimizerCoordinator._indoor_humidity_value, both over
  inputs:age_of) delivers None although the sensor reported <= 5 min ago. Denominator printed.
Metric B (future arm): the host clock steps back S=60 min just after a sensor dies (its last
  stamp = pre-step wall time). Count 15-min samples, from the step on, in which the seam still
  delivers the dead sensor's value, vs the samples InputReader._age_minutes' rule would allow.
Null: a sensor whose value changes on every report (last_updated == last_reported): 0 None.
Count key: the delivered value (None vs number) from the production seam.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/u2_age_timeline.py
Expected (exact): see RESULT lines.
Baseline SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
sys.path[:0] = [".", "tests", "tests/hastub"]
p0, t0 = time.process_time(), time.thread_time()
from homeassistant.util import dt as dt_util  # noqa: E402
from harness import FakeHass, FakeState  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as C  # noqa: E402
from custom_components.heatpump_optimizer import inputs as I  # noqa: E402

T0 = datetime(2026, 1, 15, 0, 0, tzinfo=timezone.utc)


def inlet(st):
    return C._dhw_inlet_c(FakeHass({"sensor.inlet": st}), "sensor.inlet")


def rh(st):
    ns = SimpleNamespace(hass=FakeHass({"sensor.rh": st}), _config={C.CONF_INDOOR_HUMIDITY_ENTITY: "sensor.rh"})
    return C.HeatPumpOptimizerCoordinator._indoor_humidity_value(ns)


SEAMS = (("humidity", rh, "55", "%", C.HUMIDITY_MAX_AGE_MINUTES, (1, 2, 3, 4, 8, 12)),
         ("dhw_inlet", inlet, "9.0", "°C", C.DHW_INLET_MAX_AGE_MINUTES, (12, 24, 30, 48)))


def reader_allows(st, now, limit):
    r = I.InputReader(FakeHass({}), {}, now=lambda: now)
    a = r._age_minutes(st)
    return a is not None and a <= limit


try:
    for name, fn, raw, unit, limit, holds in SEAMS:
        for H in holds:
            none = n = 0
            for k in range(1, int(H * 4) + 1):
                now = T0 + timedelta(minutes=15 * k)
                dt_util.freeze(now)
                rep = T0 + timedelta(minutes=5 * ((15 * k) // 5))  # last 5-min write <= now
                st = FakeState(raw, unit=unit, last_updated=T0, last_reported=rep)
                n += 1
                none += fn(st) is None
            print(f"RESULT {name}.hold_{H}h.live_delivered_none={none} samples (of {n})")
        # null: value changes on every write
        none = n = 0
        for k in range(1, 4 * max(holds) + 1):
            now = T0 + timedelta(minutes=15 * k)
            dt_util.freeze(now)
            rep = now - timedelta(minutes=2)
            none += fn(FakeState(raw, unit=unit, last_updated=rep, last_reported=rep)) is None
            n += 1
        print(f"RESULT {name}.null_changing.delivered_none={none} samples (of {n})")
        # future arm: sensor dies at T0 with stamp T0; clock steps back 60 min right after.
        served = allowed = 0
        st = FakeState(raw, unit=unit, last_updated=T0, last_reported=T0)
        steps = int((60 + limit) / 15) + 8
        for k in range(steps):
            now = T0 - timedelta(minutes=60) + timedelta(minutes=15 * k)
            dt_util.freeze(now)
            served += fn(st) is not None
            allowed += reader_allows(st, now, limit)
        print(f"RESULT {name}.clockstep60.dead_served={served} samples; reader_rule_allows={allowed} samples")
finally:
    dt_util.freeze(None)
p1, t1 = time.process_time(), time.thread_time()
print(f"RESULT thread_factor={(p1 - p0) / max(t1 - t0, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
except Exception:  # noqa: BLE001
    sw = "na"
print(f"RESULT swapins={sw}")
