#!/usr/bin/env python3
# Metric: the irradiance series HeatPumpOptimizerCoordinator._apply_open_meteo returns (or the exception it raises) for a
#   6-step horizon whose weather-entity solar list has 3 entries and whose Open-Meteo stub covers only the first 2 steps.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_37e0face2a901e71.py
# EXPECTED RESULT short_solar_baseline=[100.0, 101.0, 7.0, 0.0, 0.0, 0.0] ; short_solar_mutant=IndexError
# EXPECTED RESULT null_delta=0 count  (solar as long as the horizon, and full Open-Meteo coverage)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g01 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._apply_open_meteo
#   line 7419 (`value = solar[i] if i < len(solar) else 0.0`), live coordinator, _open_meteo replaced by a stub
#   (available=True, irradiance_for keyed on the production utc_step_starts grid). Reach: _forecast_arrays
#   (coordinator.py:7473) calls it BEFORE the hold-flat padding at 7476, so a weather forecast shorter than the horizon
#   arrives here short.
# Perturbation: key 37e0face2a901e71, `i < len(solar)` -> `i <= len(solar)`, in memory (method recompiled from source).
#   Direction: a series -> IndexError at i == len(solar) (the forecast assembly raises instead of falling back).
# Null control: a solar list as long as the horizon (i < len always), and full Open-Meteo coverage (fallback unused).
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


MUT = recompile(CLS, "_apply_open_meteo", "value = solar[i] if i < len(solar) else 0.0",
                "value = solar[i] if i <= len(solar) else 0.0")
b, m = drive(CLS._apply_open_meteo, [5.0, 6.0, 7.0], 6, 2)[0], drive(MUT, [5.0, 6.0, 7.0], 6, 2)[0]
print(f"RESULT short_solar_baseline={b}")
print(f"RESULT short_solar_mutant={m}")
for solar, n, cov in (([], 4, 0), ([5.0, 6.0, 7.0], 6, 3), ([5.0, 6.0, 7.0], 6, 4), ([5.0, 6.0, 7.0], 3, 0)):
    print(f"RESULT inputs solar={solar} n={n} covered={cov}: baseline={drive(CLS._apply_open_meteo, solar, n, cov)[0]} "
          f"mutant={drive(MUT, solar, n, cov)[0]}")
nulls = (([5.0] * 6, 6, 2), ([5.0, 6.0, 7.0], 6, 6))
print(f"RESULT null_delta={sum(int(drive(CLS._apply_open_meteo, *a)[0] != drive(MUT, *a)[0]) for a in nulls)} count")
tail()
