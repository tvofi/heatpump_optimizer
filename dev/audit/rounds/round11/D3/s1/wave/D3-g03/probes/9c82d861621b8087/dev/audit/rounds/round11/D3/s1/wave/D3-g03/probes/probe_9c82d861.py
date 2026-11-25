#!/usr/bin/env python3
# Metric: the per-step electrical cap array HeatPumpOptimizerCoordinator._capacity_caps returns (None = no cap),
#   p_max 1.0 kW from ThermalParameters.from_config, COP pinned to 1, one learned envelope bucket whose heat makes
#   cap_i land exactly on the tie cap_i == p_max - 1e-9, and around it.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g03/probes/probe_9c82d861.py
# EXPECTED RESULT caps_tie_baseline=None ; caps_tie_mutant=[0.999999999, 0.999999999] ; max_cap_delta_kw=1e-09
# EXPECTED RESULT null_delta=0 count (bucket heat p_max - 2e-9, p_max - 0.5e-9 and 0.8: arms agree)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g03 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._capacity_caps,
#   line 9365 `if cap_i < p_max - 1e-9:`.
# Perturbation: key 9c82d861621b8087 CMP_BOUND -> `if cap_i <= p_max - 1e-9:`, in memory. Direction: None -> caps at the tie.
# Null control: bucket heats off the tie on both sides.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, sys, textwrap, time, types
from types import SimpleNamespace
from unittest import mock

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
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402

CLS = co.HeatPumpOptimizerCoordinator
_T0 = (time.process_time(), time.thread_time())


def mutant(fn, line, old, new):
    """`fn` recompiled from its own source with production line `line` replaced (in memory only)."""
    lines, start = inspect.getsourcelines(fn)
    i = line - start
    assert lines[i].rstrip("\n") == old, f"anchor moved: {lines[i]!r}"
    lines[i] = new + "\n"
    ns = dict(co.__dict__)
    exec(compile(textwrap.dedent("".join(lines)), co.__file__, "exec"), ns)
    f = ns[fn.__name__]
    # rebound onto the module's own globals, so a patch of a module name reaches both arms alike
    return types.FunctionType(f.__code__, co.__dict__, f.__name__, f.__defaults__, f.__closure__)


def run(coro):
    return asyncio.run(coro)


def tail():
    p, t = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
    except OSError:
        sw = -1
    print(f"RESULT swapins={sw} count")

from custom_components.heatpump_optimizer import const, thermal_model as tm  # noqa: E402


def caps(fn, p_max, heat_kw, outdoor=-3.0):
    """_capacity_caps over 2 steps at `outdoor`, one learned envelope bucket of `heat_kw` (COP pinned to 1)."""
    params = tm.ThermalParameters.from_config({const.CONF_HEAT_PUMP_MAX_POWER: p_max})
    model = SimpleNamespace(params=params, compute_cop=lambda o, humidity=None: 1.0)
    me = SimpleNamespace(_config=SimpleNamespace(capacity_curve_enabled=True), _thermal_params=params,
                         _thermal_model=model,
                         _capacity_envelope={int(co.np.floor(outdoor / 3.0)): [heat_kw, const.CAPACITY_MIN_SAMPLES]})
    out = fn(me, co.np.array([outdoor, outdoor]))
    return None if out is None else [float(x) for x in out]
MUT = mutant(CLS._capacity_caps, 9365, "            if cap_i < p_max - 1e-9:", "            if cap_i <= p_max - 1e-9:")
tie = 1.0 - 1e-9
b, m = caps(CLS._capacity_caps, 1.0, tie), caps(MUT, 1.0, tie)
print(f"RESULT caps_tie_baseline={b}")
print(f"RESULT caps_tie_mutant={m}")
print(f"RESULT max_cap_delta_kw={max(abs(1.0 - x) for x in m) if m and not b else 0.0:.3g}")
print(f"RESULT null_delta={sum(int(caps(CLS._capacity_caps, 1.0, h) != caps(MUT, 1.0, h)) for h in (1.0 - 2e-9, 1.0 - 0.5e-9, 0.8))} count")
tail()
