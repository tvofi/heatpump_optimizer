#!/usr/bin/env python3
# Metric: the learned COP scale after HeatPumpOptimizerCoordinator._fold_cop_evidence folds ONE outlier interval
#   (3 kW commanded at a modelled COP 3.0 drawing 0.5 kW: cop_evidence's target scale 6.0) from scale 1.0.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_1165914e57f5bd08.py
# EXPECTED RESULT cop_scale_outlier_baseline=1.05 ; cop_scale_outlier_mutant=1.1  (per-sample cap 5 % -> 10 %)
# EXPECTED RESULT null_delta=0 count  (draws of 2.0 and 5.0 kW: EWMA step under 5 %, the clip inert either way)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g01 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._fold_cop_evidence
#   (max_step = cop_scale * COP_LEARNING_MAX_STEP at coordinator.py:5399; the constant is coordinator.py:1796), live
#   coordinator, real cop_evidence; probe_install is stubbed to a sample that is an inference (cop_sample -> False),
#   because the default probe config has no heat meter and would refuse the interval before the clip.
# Perturbation: key 1165914e57f5bd08, `COP_LEARNING_MAX_STEP = 0.05` -> `= 0.1`, in memory (mock.patch.object).
#   Direction: one outlier moves the scale 5 % -> 10 %.
# Null control: in-band intervals where the EWMA step is below 5 %.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, logging, sys, textwrap, time
logging.disable(logging.CRITICAL)
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

_T0 = (time.process_time(), time.thread_time())


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
from harness import FakeEntry, FakeHass  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402

CFG = {"tibber_token": "x", "weather_entity": "weather.home",
       "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}


def coord(states=None, **extra):
    return co.HeatPumpOptimizerCoordinator(FakeHass(dict(states or {})), FakeEntry(data={**CFG, **extra}))


def recompile(cls, name, old, new):
    """The method `name` of `cls` with its single line `old` replaced by `new`, compiled in the module namespace."""
    src = textwrap.dedent(inspect.getsource(getattr(cls, name)))
    assert src.count(old) == 1, f"anchor {old!r} moved"
    ns = dict(co.__dict__)
    exec(compile(src.replace(old, new, 1), co.__file__, "exec"), ns)
    return ns[name]


def tail():
    p, t = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = next(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin "))
    except (OSError, StopIteration):
        sw = 0
    print(f"RESULT swapins={sw} count")


def drive(electrical_kw, step, commanded=3.0, modelled=3.0):
    """One COP interval: `commanded` kW of heat asked, `electrical_kw` drawn, modelled COP `modelled`, scale 1.0."""
    c = coord()
    c._apply_cop_scale(1.0)
    n0 = c._cop_samples
    with mock.patch.object(co, "COP_LEARNING_MAX_STEP", step), \
         mock.patch.object(co, "probe_install", lambda cfg: SimpleNamespace(cop_sample=lambda h, d: False)):
        refused = c._fold_cop_evidence(commanded, electrical_kw, None, (modelled, False, None))
    return refused, c._cop_samples - n0, round(float(c._cop_scale), 6)


b, m = drive(0.5, 0.05), drive(0.5, 0.1)
print(f"RESULT cop_scale_outlier_baseline={b[2]} (refused={b[0]}, samples={b[1]})")
print(f"RESULT cop_scale_outlier_mutant={m[2]} (refused={m[0]}, samples={m[1]})")
for e in (1.0, 0.3, 0.1, 60.0):
    print(f"RESULT inputs electrical_kw={e}: baseline={drive(e, 0.05)} mutant={drive(e, 0.1)}")
print(f"RESULT null_delta={sum(int(drive(e, 0.05) != drive(e, 0.1)) for e in (2.0, 5.0))} count")
tail()
