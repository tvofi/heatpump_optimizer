#!/usr/bin/env python3
# Metric: HeatPumpOptimizerCoordinator._outage_dhw_hold(now) (bool: whether post-outage recovery still queues hot
#   water behind space heating; read at coordinator.py:6263) at instants around _outage_dhw_until; key = the bool.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g08/probes/probe_aaa2a3d6bb2ba515.py
# Expected: now == _outage_dhw_until exactly: baseline False, mutant True; 1 us before / 1 s after (null): moved 0.
#   Exact (deterministic).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g08 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._outage_dhw_hold
#   (coordinator.py:9051).
# Perturbation: mutant aaa2a3d6bb2ba515 (CMP_BOUND) `utc_elapsed_seconds(...) <= 0` -> `< 0`, compiled in memory;
#   direction: at the window's last instant the hold stays on (True) instead of ending (False).
# Inputs: SimpleNamespace coordinator (no _ctx); real ThermalParameters (dhw enabled and dhw_min_temp default) with the
#   tank at 55 degC (above the floor, so the low-tank exit does not decide); and a 30 degC tank (below: exit decides);
#   offsets of now from _outage_dhw_until in OFFSETS; aware UTC and Europe/Stockholm stamps.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo
sys.path.insert(0, str(Path.cwd()))
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

CLS = co.HeatPumpOptimizerCoordinator
OLD = "if self._outage_dhw_until is None or utc_elapsed_seconds(self._outage_dhw_until, now) <= 0:"
NEW = "if self._outage_dhw_until is None or utc_elapsed_seconds(self._outage_dhw_until, now) < 0:"


def mutant(fn):
    src = textwrap.dedent(inspect.getsource(fn))
    assert src.count(OLD) == 1, "anchor line moved"
    ns = dict(co.__dict__)
    exec(compile(src.replace(OLD, NEW, 1), co.__file__, "exec"), ns)
    return ns[fn.__name__]


MUT = mutant(CLS._outage_dhw_hold)
PARAMS = ThermalParameters(dhw_enabled=True)
UNTIL = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)
OFFSETS = {"exact": timedelta(0), "minus_1us": timedelta(microseconds=-1), "plus_1s": timedelta(seconds=1),
           "minus_1h": timedelta(hours=-1)}


def hold(fn, until, now, tank):
    me = SimpleNamespace(_outage_dhw_until=until, _thermal_params=PARAMS,
                         _current_state=SimpleNamespace(dhw_temperature=tank))
    return fn(me, now)


moved = 0
nulls = 0
for zname, tz in (("utc", timezone.utc), ("stockholm", ZoneInfo("Europe/Stockholm"))):
    until = UNTIL.astimezone(tz)
    for tank in (55.0, 30.0):
        for oname, off in OFFSETS.items():
            b, m = hold(CLS._outage_dhw_hold, until, until + off, tank), hold(MUT, until, until + off, tank)
            if oname == "exact" and tank == 55.0:
                moved += int(b != m)
            else:
                nulls += int(b != m)
            print(f"RESULT {zname}_tank{tank:g}_{oname}_baseline={b} mutant={m}")
print(f"RESULT exact_moved={moved} count of 2")
print(f"RESULT null_moved={nulls} count of 14")
print(f"RESULT dhw_min_temp={PARAMS.dhw_min_temp} degC")
