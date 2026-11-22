# Shared builders for box D3-g14's probes (round 11, D3-s1). Not a harness on its own: every
# probe_<key>.py imports it and carries its own header. Builds a DhwPlanner the way
# tests/features.py:_dhw_planner does, a horizon the way tests/features.py:_dhw_horizon does,
# and compiles a one-line mutant of a DhwPlanner method IN MEMORY (the method's own source
# re-compiled with the line replaced, attached with mock.patch.object), never on disk.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from contextlib import contextmanager
from pathlib import Path
from unittest import mock


def repo_root(start):
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
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import dhw_planner  # noqa: E402
from custom_components.heatpump_optimizer.dhw_planner import DhwPlanner  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer, OptimizationConfig, _Horizon)
from custom_components.heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState)
from custom_components.heatpump_optimizer.dhw_schedule import parse_windows  # noqa: E402,F401


S1 = ROOT / "dev/audit/rounds/round11/D3/s1"


def mutant_dict(key):
    """The one-line mutant as the slice boxes recorded it (state/results/complete/<key>.json)."""
    import json
    return json.loads((S1 / "state/results/complete" / f"{key}.json").read_text())["mutant"]


def mutant_method(name, m):
    """DhwPlanner.<name> with file line m['line'] (== m['old']) replaced by m['new'], compiled in memory."""
    raw = inspect.getattr_static(DhwPlanner, name)
    fn = raw.__func__ if isinstance(raw, staticmethod) else raw
    lines, first = inspect.getsourcelines(fn)
    i = int(m["line"]) - first
    assert 0 <= i < len(lines) and lines[i].rstrip("\n") == m["old"], (
        f"anchor moved: {name} line {m['line']} is {lines[i]!r}")
    lines = list(lines)
    lines[i] = m["new"] + "\n"
    src = textwrap.dedent("".join(lines))
    if isinstance(raw, staticmethod) and not src.lstrip().startswith("@"):
        src = "@staticmethod\n" + src
    ns = dict(dhw_planner.__dict__)
    exec(compile(src, dhw_planner.__file__, "exec"), ns)
    return ns[name]


@contextmanager
def mutated(name, key):
    with mock.patch.object(DhwPlanner, name, mutant_method(name, mutant_dict(key))):
        yield


def planner(**pkw):
    kw = dict(dhw_enabled=True, dhw_tank_volume=200.0)
    kw.update(pkw)
    params = ThermalParameters(**kw)
    opt = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(
        horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0))
    return DhwPlanner(opt.model, opt.config, opt._pv_surplus, opt._price_known), params


def horizon(*, prices, outdoor=None, n=96, dt=0.25, state=None, dhw_pins=None, step_hours=None):
    outdoor = np.full(n, -5.0) if outdoor is None else outdoor
    return _Horizon(
        initial_state=state or ThermalState(
            room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=-5.0,
            dhw_temperature=48.0, dhw_hours_since_legionella=20.0, buffer_tank_temperature=40.0),
        prices=prices, outdoor_temps=outdoor,
        wind_speeds=np.zeros(n), precipitation=np.zeros(n), solar_radiation=np.zeros(n),
        start_time=None, n_steps=n, dt=dt,
        comfort_targets=np.full(n, 21.0), temp_min_bounds=np.full(n, 17.0),
        temp_max_bounds=np.full(n, 23.0),
        step_hours=(np.arange(n) * dt) % 24.0 if step_hours is None else step_hours,
        solar_gains=np.zeros(n), heat_loss_factors=np.ones(n), forecast={},
        t_start=0.0, step_weekdays=None, holiday_flags=None, humidity=None, dhw_pins=dhw_pins,
    )


def fmt(a):
    return "[" + ",".join(f"{float(x):.4g}" for x in np.asarray(a).ravel()) + "]"
