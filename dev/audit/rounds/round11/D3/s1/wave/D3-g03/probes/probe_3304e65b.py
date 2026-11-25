#!/usr/bin/env python3
# Metric: the plan views HeatPumpOptimizerCoordinator._build_plan_views returns for an OptimizationResult with no
#   timestamps (n = 0): whether they equal {"space_plan": {}, "dhw_plan": {}}, and the space_plan key count.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g03/probes/probe_3304e65b.py
# EXPECTED RESULT empty_views_baseline=True space_plan_keys=0 ; empty_views_mutant=False space_plan_keys=5
#   (the general path publishes empty forecast/slots and zero totals instead of the empty view)
# EXPECTED RESULT null_delta=0 count (n = 4: guard false in both arms)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g03 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._build_plan_views,
#   line 4831 `if not n:`; real OptimizationResult, real plan_slots.
# Perturbation: key 3304e65ba361587f GUARD_OFF -> `if False:`, in memory. Direction: {} views -> populated-empty views.
# Null control: a 4-step result.
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

from datetime import datetime, timedelta, timezone  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import OptimizationResult  # noqa: E402

T0 = datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc)


def result(n, **kw):
    base = dict(
        power_schedule=[1.0] * n, room_temp_trajectory=[21.0] * (n + 1), slab_temp_trajectory=[22.0] * (n + 1),
        timestamps=[T0 + timedelta(minutes=15 * i) for i in range(n)], prices=[1.0 + 0.1 * i for i in range(n)],
        predicted_cost=0.0, baseline_cost=0.0, predicted_savings=0.0, savings_percentage=0.0,
        optimal_setpoints=[21.0] * n, status="optimal", outdoor_temps=[-2.0] * n,
        dhw_power_schedule=[0.0] * n, dhw_temp_trajectory=[50.0] * (n + 1),
    )
    base.update(kw)
    return OptimizationResult(**base)


def views(fn, res):
    me = SimpleNamespace(_opt_config=SimpleNamespace(dt_hours=0.25),
                         _dhw_confidence_band=lambda temps, dt: ([None] * len(temps), [None] * len(temps)))
    try:
        return fn(me, res)
    except Exception as err:  # noqa: BLE001 - a raise is an outcome too
        return f"raised {type(err).__name__}: {err}"
MUT = mutant(CLS._build_plan_views, 4831, "        if not n:", "        if False:")
for arm, fn in (("baseline", CLS._build_plan_views), ("mutant", MUT)):
    v = views(fn, result(0))
    sp = v.get("space_plan") if isinstance(v, dict) else None
    print(f"RESULT empty_views_{arm}={v == {'space_plan': {}, 'dhw_plan': {}}} space_plan_keys={len(sp) if isinstance(sp, dict) else v!r}")
print(f"RESULT null_delta={int(views(CLS._build_plan_views, result(4)) != views(MUT, result(4)))} count")
tail()
