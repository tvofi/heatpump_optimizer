#!/usr/bin/env python3
# Metric: the live DHW inlet temperature coordinator._dhw_inlet_c returns (degC, or None = falls back to the seasonal model)
#   for a 12.0 degC probe whose state is exactly DHW_INLET_MAX_AGE_MINUTES (24 h) old under a frozen clock.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_4fd094e9.py
# Expected: RESULT age_at_limit_baseline=12.0, age_at_limit_mutant=None; null_moved=0.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g11 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:_dhw_inlet_c (line 2907,
#   `    if state is None or age is None or age > timedelta(minutes=DHW_INLET_MAX_AGE_MINUTES):`).
# Perturbation: mutant 4fd094e9727818b3, `age > timedelta(...)` -> `age >= timedelta(...)`, in memory (recompiled from
#   its own source in the module namespace); dt_util.utcnow patched to a fixed instant. Direction: 12.0 -> None at age == 24 h.
# Null control: ages 23 h 59 min, 24 h 1 min and 1 h, where both arms agree.
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

import time
from datetime import datetime, timedelta, timezone
from unittest import mock
from tests.harness import FakeState, FakeStates

NOW = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
MUT = mutate(co._dhw_inlet_c, "age > timedelta(", "age >= timedelta(")


def read(fn, age):
    hass = type("H", (), {})()
    hass.states = FakeStates({"sensor.inlet": FakeState("12.0", last_updated=NOW - age, unit="°C")})
    with mock.patch.object(co.dt_util, "utcnow", lambda: NOW):
        return fn(hass, "sensor.inlet")


t0, t1 = time.process_time(), time.thread_time()
lim = timedelta(minutes=co.DHW_INLET_MAX_AGE_MINUTES)
print(f"RESULT age_at_limit_baseline={read(co._dhw_inlet_c, lim)}")
print(f"RESULT age_at_limit_mutant={read(MUT, lim)}")
nulls = [lim - timedelta(minutes=1), lim + timedelta(minutes=1), timedelta(hours=1)]
print(f"RESULT null_moved={sum(read(co._dhw_inlet_c, a) != read(MUT, a) for a in nulls)} count")
tail_results(t0, t1)
