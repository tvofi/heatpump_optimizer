#!/usr/bin/env python3
# Metric: the learned house heat-loss scale after HeatPumpOptimizerCoordinator._reanchor_house_heat_loss_scale restores
#   a store fitted against a nameplate UA 7 % off today's (scale 1.2, 200 samples), and whether it re-anchored.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_021dc21415f3229e.py
# EXPECTED RESULT reanchor_7pct_baseline=(True, 1.279005) ; reanchor_7pct_mutant=(False, 1.2)  (kept verbatim)
# EXPECTED RESULT null_delta=0 count  (3 % and 12 % edits: on the same side of both gates)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g01 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._reanchor_house_heat_loss_scale
#   (passes step=HOUSE_LOSS_MAX_STEP to heat_loss_anchor_pair at coordinator.py:5572; the constant is coordinator.py:1651),
#   on a live coordinator; the stored anchor dict is the coordinator's own _heat_loss_anchors() with the UA scaled.
# Perturbation: key 021dc21415f3229e, `HOUSE_LOSS_MAX_STEP = 0.05` -> `= 0.1`, in memory (mock.patch.object).
#   Direction: a 5..10 % nameplate edit re-anchored -> kept verbatim (the learned scale stays fitted to the old UA).
# Null control: a 3 % edit (below both gates) and a 12 % edit (above both).
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
    from pathlib import Path
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


def drive(frac, step):
    """Restore a store whose house_heat_loss_anchor was fitted against a nameplate frac away from today's."""
    c = coord()
    c._house_heat_loss_scale, c._house_heat_loss_samples = 1.2, 200
    stored = dict(c._heat_loss_anchors())
    stored["house_heat_loss_anchor"] = float(stored["house_heat_loss_anchor"]) * (1.0 + frac)
    with mock.patch.object(co, "HOUSE_LOSS_MAX_STEP", step):
        changed = c._reanchor_house_heat_loss_scale(stored)
    return bool(changed), round(float(c._house_heat_loss_scale), 6)


b, m = drive(0.07, 0.05), drive(0.07, 0.1)
print(f"RESULT reanchor_7pct_baseline={b}")
print(f"RESULT reanchor_7pct_mutant={m}")
for f in (0.049, 0.051, 0.099, 0.101, -0.07):
    print(f"RESULT inputs frac={f}: baseline={drive(f, 0.05)} mutant={drive(f, 0.1)}")
print(f"RESULT null_delta={sum(int(drive(f, 0.05) != drive(f, 0.1)) for f in (0.03, 0.12))} count")
tail()
