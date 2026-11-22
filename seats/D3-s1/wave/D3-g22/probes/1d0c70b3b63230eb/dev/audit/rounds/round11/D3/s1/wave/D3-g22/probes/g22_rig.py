"""Shared rig for box D3-g22's probes (not a harness on its own; each probe_<key>.py imports it).

- ROOT / sys.path: the repository root, `tests/` and `custom_components/` (the tests' own import layout,
  so `heatpump_optimizer.optimizer` is the module production code and the suite both run).
- mutant(cls, method, old, new): the method re-compiled from its own source with the one-line mutant
  applied in memory (asserts the anchor occurs exactly once); never touches the tree on disk.
- january(...): tests/features.py's v5.3.0 mode-block scenario (profiles.house(), DHW on, 12 h at
  15 min, winter_cold weather, winter_typical prices), copied as the README says to copy, not imported.
- tail(): the RESULT thread_factor / load1 / swapins lines the harness contract requires.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect
import sys
import textwrap
import time
from pathlib import Path


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
for _p in (ROOT / "tests", ROOT / "custom_components", ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import numpy as np  # noqa: E402
from heatpump_optimizer import optimizer as opt_mod  # noqa: E402
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402

_T0 = (time.process_time(), time.thread_time())


def mutant(cls, name, old, new):
    fn = getattr(cls, name)
    src = textwrap.dedent(inspect.getsource(fn))
    assert src.count(old) == 1, f"anchor {old!r} occurs {src.count(old)} times in {name}"
    ns = dict(sys.modules[cls.__module__].__dict__)
    exec(compile(src.replace(old, new, 1), inspect.getsourcefile(fn), "exec"), ns)
    return ns[name]


def bare_optimizer(**cfg):
    return HeatPumpOptimizer(ThermalModel(ThermalParameters()), OptimizationConfig(**cfg))


def january():
    """(optimizer, run(**solve_inputs_kw)) for features.py's v5.3.0 scenario."""
    from datetime import datetime
    import profiles
    from profiles import solve_inputs

    start = datetime(2026, 1, 15, 0, 0)
    params = ThermalParameters.from_config(profiles.house())
    params.dhw_enabled = True
    opt = HeatPumpOptimizer(
        ThermalModel(params),
        OptimizationConfig(horizon_hours=12, time_step_minutes=15, min_temp=19.0, max_temp=23.0),
    )
    n = opt.config.n_steps
    prices = np.asarray(profiles.prices("winter_typical", start))[:n]
    t, wind, rain, solar = profiles.weather("winter_cold", start)
    state = ThermalState(room_temperature=21.0, outdoor_temperature=-12.0, dhw_temperature=45.0)

    def run(**kw):
        return opt.optimize(inputs=solve_inputs(
            initial_state=state, prices=prices, outdoor_temps=t[:n], wind_speeds=wind[:n],
            precipitation=rain[:n], solar_radiation=solar[:n], start_time=start, **kw))

    return opt, run


def tail():
    p, t = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        for line in Path("/proc/vmstat").read_text().splitlines():
            if line.startswith("pswpin "):
                sw = int(line.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw} count")
