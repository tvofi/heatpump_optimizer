#!/usr/bin/env python3
# Metric: the live DHW inlet temperature coordinator._dhw_inlet_c returns (degC, or None = falls back to the seasonal model)
#   for a fresh (1 h old) probe reading at the plausibility bound 35.0 degC.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_e2b030e0.py
# Expected: RESULT inlet_35_baseline=35.0, inlet_35_mutant=None; null_moved=0.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g11 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:_dhw_inlet_c (line 2910,
#   `    return value if value is not None and -5.0 <= value <= 35.0 else None`).
# Perturbation: mutant e2b030e0716d126c, `value <= 35.0` -> `value < 35.0`, in memory (recompiled from its own source in
#   the module namespace); dt_util.utcnow patched to a fixed instant. Direction: 35.0 -> None at exactly 35.0 degC.
# Null control: 34.9, 35.1, -5.0 and 10.0 degC, where both arms agree.
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
MUT = mutate(co._dhw_inlet_c, "value <= 35.0", "value < 35.0")


def read(fn, val):
    hass = type("H", (), {})()
    hass.states = FakeStates({"sensor.inlet": FakeState(str(val), last_updated=NOW - timedelta(hours=1), unit="°C")})
    with mock.patch.object(co.dt_util, "utcnow", lambda: NOW):
        return fn(hass, "sensor.inlet")


t0, t1 = time.process_time(), time.thread_time()
print(f"RESULT inlet_35_baseline={read(co._dhw_inlet_c, 35.0)}")
print(f"RESULT inlet_35_mutant={read(MUT, 35.0)}")
nulls = [34.9, 35.1, -5.0, 10.0]
print(f"RESULT null_moved={sum(read(co._dhw_inlet_c, v) != read(MUT, v) for v in nulls)} count")
tail_results(t0, t1)
