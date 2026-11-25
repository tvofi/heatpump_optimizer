#!/usr/bin/env python3
# Metric: count of the 144 production-shaped fixtures (48 of which take the joint shortcut on the baseline) whose _apply_dhw_min_run plan differs baseline vs mutant; and simulate_dhw_step calls (cost) on 12 shortcut fixtures.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_111763243ac44278.py
# EXPECTED RESULT production_shaped_moved=0 of 144  (when every weak slot raised jointly fits, the per-slot pass raises each:
#   a subset of the raises lies below the joint trajectory, and the per-slot reference only rises)
# EXPECTED RESULT baseline_paths joint_shortcut=48 per_slot=96 count
# EXPECTED RESULT dhw_steps_baseline=4608 count  (48 joint-shortcut fixtures)
# EXPECTED RESULT dhw_steps_mutant=22560 count  (x4.9: the shortcut is a cost saving, not a behaviour)
# Count key: the plan array DhwPlanner._apply_dhw_min_run returns (np.array_equal, baseline vs mutant), fed straight
#   back into DhwPlanner.optimize's schedule (dhw_planner.py:1257); production-shaped = 0 <= plan <= p_dhw_max and
#   min_run_power <= p_dhw_max, the two invariants its only caller guarantees (dhw_planner.py:1141 and the clipped
#   returns of _plan_dhw_cheapest_first).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g13 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._apply_dhw_min_run
#   (line 2075 `        if bool(np.all(joint_temps <= joint_limit + 1e-9)):`), driven on features.py's _mr_fixture shape (weak slots spread over the horizon, a draw block)
#   over 12 seeds x 4 tank states x 3 horizon sizes = 144 fixtures.
# Perturbation: mutant 111763243ac44278, the joint-shortcut guard -> `if False:`, applied in memory (method recompiled from its own source, called unbound for
#   the mutant arm). Direction: the per-slot pass always runs; same plan, more tank steps.
# Null control: the 96 per-slot fixtures, which never reach the shortcut's return.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time
from pathlib import Path
from unittest import mock


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
_T0 = (time.process_time(), time.thread_time())


def mutated(module, func, old, new, name=None):
    """``func`` recompiled from its own source with the one mutant line swapped (anchor must occur once)."""
    src = textwrap.dedent(inspect.getsource(func))
    o, n = old.strip(), new.strip()
    assert src.count(o) == 1, f"anchor moved: {o!r}"
    ns = dict(module.__dict__)
    exec(compile(src.replace(o, n, 1), module.__file__, "exec"), ns)
    return ns[name or func.__name__]


def footer():
    pc, tc = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        swp = [l for l in open("/proc/vmstat") if l.startswith("pswpin ")]
        print(f"RESULT swapins={swp[0].split()[1] if swp else 0}")
    except OSError:
        print("RESULT swapins=n/a")
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import dhw_planner  # noqa: E402
from custom_components.heatpump_optimizer.dhw_planner import DhwPlanner  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402

params = ThermalParameters(dhw_enabled=True, dhw_tank_volume=200.0, dhw_cooling_rate=0.3)
opt = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(
    horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0))
planner = DhwPlanner(opt.model, opt.config, opt._pv_surplus, opt._price_known)
BASE_FN = DhwPlanner._apply_dhw_min_run
MIN_RUN, P_MAX = 0.6, 3.0


def run(plan, fn=None, initial=50.0, ceiling=50.0, draws=None, p_max=P_MAX, min_run=MIN_RUN, dt=0.25):
    n = len(plan)
    draws = np.zeros(n) if draws is None else draws
    return (fn or BASE_FN)(
        planner, plan=np.array(plan, dtype=float), initial_temp=initial, outdoor_temps=np.zeros(n),
        draw_rates=draws, dt=dt, p_dhw_max=p_max, min_run_power=min_run, max_temp=np.full(n, ceiling))


def fixture(n, n_weak, seed, initial, ceiling, draw_level):
    """features.py's _mr_fixture shape: weak slots spread over the horizon, a draw block in the middle."""
    rng = np.random.default_rng(seed)
    draws = np.zeros(n)
    draws[n // 2:n // 2 + n // 6] = draw_level
    plan = np.zeros(n)
    pos = np.linspace(1, n - 2, n_weak).astype(int)
    plan[pos] = 0.05 + 0.5 * rng.random(n_weak)
    strong = rng.choice(n, size=max(1, n // 10), replace=False)
    plan[strong] = np.where(plan[strong] > 0, plan[strong], 1.0 + 2.0 * rng.random(strong.size))
    return plan, dict(initial=initial, ceiling=ceiling, draws=draws)


def sweep(fn, seeds=range(12)):
    """Production-shaped fixtures (0 <= plan <= p_max, min_run <= p_max as dhw_planner.py:1141 guarantees)."""
    moved, total = [], 0
    for seed in seeds:
        for initial, ceiling, draw in ((50.0, 50.0, 1.8), (35.0, 55.0, 0.0), (45.0, 60.0, 3.0), (55.0, 55.0, 0.5)):
            for n, nw in ((24, 3), (96, 24), (48, 10)):
                plan, kw = fixture(n, nw, seed, initial, ceiling, draw)
                total += 1
                b, m = run(plan, **kw), run(plan, fn, **kw)
                if b.shape != m.shape or not np.array_equal(b, m):
                    moved.append((seed, initial, ceiling, draw, n, float(np.max(np.abs(b - m)))))
    return moved, total


def joint_cases(seeds=range(12)):
    """How many sweep fixtures take the joint shortcut (no per-slot _dhw_raise_fits call) on the baseline."""
    calls = {"n": 0}
    orig = DhwPlanner._dhw_raise_fits

    def counted(self, *a, **k):
        calls["n"] += 1
        return orig(self, *a, **k)

    joint = per_slot = 0
    with mock.patch.object(DhwPlanner, "_dhw_raise_fits", counted):
        for seed in seeds:
            for initial, ceiling, draw in ((50.0, 50.0, 1.8), (35.0, 55.0, 0.0), (45.0, 60.0, 3.0), (55.0, 55.0, 0.5)):
                for n, nw in ((24, 3), (96, 24), (48, 10)):
                    plan, kw = fixture(n, nw, seed, initial, ceiling, draw)
                    calls["n"] = 0
                    run(plan, **kw)
                    joint += calls["n"] == 0
                    per_slot += calls["n"] > 0
    return joint, per_slot


SRC = Path(dhw_planner.__file__).read_text()
OLD = "if bool(np.all(joint_temps <= joint_limit + 1e-9)):"
NEW = "if False:"
MUT = mutated(dhw_planner, BASE_FN, OLD, NEW)
moved, total = sweep(MUT)
joint, per_slot = joint_cases()
print(f"RESULT production_shaped_moved={len(moved)} of {total} {moved[:3]}")
print(f"RESULT baseline_paths joint_shortcut={joint} per_slot={per_slot} count")
# Cost, not behaviour: simulate_dhw_step calls per repair over the joint-shortcut fixtures, baseline vs mutant.
from custom_components.heatpump_optimizer.thermal_model import ThermalModel as _TM  # noqa: E402
cnt = {"n": 0}
_orig = _TM.simulate_dhw_step


def _counted(self, *a, **k):
    cnt["n"] += 1
    return _orig(self, *a, **k)


# the fixtures that take the joint shortcut on the baseline (no per-slot _dhw_raise_fits call)
shortcut = []
_fits = DhwPlanner._dhw_raise_fits
_calls = {"n": 0}


def _cf(self, *a, **k):
    _calls["n"] += 1
    return _fits(self, *a, **k)


with mock.patch.object(DhwPlanner, "_dhw_raise_fits", _cf):
    for seed in range(12):
        for initial, ceiling, draw in ((50.0, 50.0, 1.8), (35.0, 55.0, 0.0), (45.0, 60.0, 3.0), (55.0, 55.0, 0.5)):
            for n, nw in ((24, 3), (96, 24), (48, 10)):
                plan, kw = fixture(n, nw, seed, initial, ceiling, draw)
                _calls["n"] = 0
                run(plan, **kw)
                if _calls["n"] == 0:
                    shortcut.append((plan, kw))
steps = {}
with mock.patch.object(_TM, "simulate_dhw_step", _counted):
    for arm, fn in (("baseline", None), ("mutant", MUT)):
        cnt["n"] = 0
        for plan, kw in shortcut:
            run(plan, fn, **kw)
        steps[arm] = cnt["n"]
print(f"RESULT dhw_steps_baseline={steps['baseline']} count  ({len(shortcut)} joint-shortcut fixtures)")
print(f"RESULT dhw_steps_mutant={steps['mutant']} count")
footer()
