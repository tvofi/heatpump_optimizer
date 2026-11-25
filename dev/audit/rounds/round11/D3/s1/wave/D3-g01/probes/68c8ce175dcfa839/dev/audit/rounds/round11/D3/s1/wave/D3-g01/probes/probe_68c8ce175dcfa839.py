#!/usr/bin/env python3
# Metric: DEBUG records "Open-Meteo irradiance covered %d/%d steps" HeatPumpOptimizerCoordinator._apply_open_meteo emits
#   on the coordinator logger when Open-Meteo covers 2 of 6 horizon steps.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_68c8ce175dcfa839.py
# EXPECTED RESULT partial_cover_log_baseline=1 count ; partial_cover_log_mutant=0 count
# EXPECTED RESULT series_delta=0 count  (the returned series is identical: the guard gates only the log)
# EXPECTED RESULT null_delta=0 count  (full coverage: no record either way)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g01 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._apply_open_meteo
#   line 7422 (`if missing:`), live coordinator, Open-Meteo stub; a handler on the coordinator module's logger counts records.
# Perturbation: key 68c8ce175dcfa839, `if missing:` -> `if False:` (GUARD_OFF), in memory (method recompiled from source).
#   Direction: 1 -> 0 debug records; the plan input is unchanged.
# Null control: full Open-Meteo coverage (missing == 0).
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


CLS = co.HeatPumpOptimizerCoordinator
MID = co.dt_util.now().replace(hour=0, minute=0, second=0, microsecond=0)


def drive(fn, solar, n_steps, covered):
    """_apply_open_meteo with an Open-Meteo stub that publishes irradiance for the first `covered` steps only."""
    c = coord()
    starts = list(co.utc_step_starts(MID, n_steps, co.FORECAST_STEP, 0))
    known = {s: 100.0 + i for i, s in enumerate(starts[:covered])}
    c._open_meteo = SimpleNamespace(available=True, irradiance_for=lambda start, step: known.get(start))
    records = []
    h = logging.Handler(logging.DEBUG)
    h.emit = records.append
    lg = logging.getLogger(co.__name__)
    old = lg.level
    logging.disable(logging.NOTSET)
    lg.addHandler(h)
    lg.setLevel(logging.DEBUG)
    try:
        out = fn(c, list(solar), n_steps, MID, 0)
    except Exception as err:  # the mutant's out-of-range read
        out = type(err).__name__
    finally:
        lg.removeHandler(h)
        lg.setLevel(old)
        logging.disable(logging.CRITICAL)
    n_log = sum(1 for r in records if "Open-Meteo irradiance covered" in r.getMessage())
    return out, n_log


MUT = recompile(CLS, "_apply_open_meteo", "if missing:", "if False:")
args = ([5.0] * 6, 6, 2)
(bs, bl), (ms, ml) = drive(CLS._apply_open_meteo, *args), drive(MUT, *args)
print(f"RESULT partial_cover_log_baseline={bl} count")
print(f"RESULT partial_cover_log_mutant={ml} count")
print(f"RESULT series_delta={int(bs != ms)} count")
for a in (([], 4, 0), ([5.0] * 6, 6, 5)):
    print(f"RESULT inputs {a}: baseline={drive(CLS._apply_open_meteo, *a)} mutant={drive(MUT, *a)}")
nb, nm = drive(CLS._apply_open_meteo, [5.0] * 6, 6, 6), drive(MUT, [5.0] * 6, 6, 6)
print(f"RESULT null_delta={int(nb != nm)} count")
tail()
