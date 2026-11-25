#!/usr/bin/env python3
# Metric: count of no-weak plans whose _apply_dhw_min_run result differs baseline vs mutant: production-shaped sweep vs direct inputs outside [0, p_dhw_max].
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_72240d3f22ceb752.py
# EXPECTED RESULT production_shaped_moved=0 of 144
# EXPECTED RESULT direct_no_weak_moved=2 of 4 (above_pmax,negative)  (3.5 -> 3.0 vs 3.5; -0.5 -> 0.0 vs -0.5)
# EXPECTED RESULT reach_cheapest_first_returns=['np.clip(plan, 0.0, p_dhw_max)', 'plan']  (plan is already clipped at
#   dhw_planner.py:2191 before that early return)
# Count key: the plan array DhwPlanner._apply_dhw_min_run returns (np.array_equal, baseline vs mutant), fed straight
#   back into DhwPlanner.optimize's schedule (dhw_planner.py:1257); production-shaped = 0 <= plan <= p_dhw_max and
#   min_run_power <= p_dhw_max, the two invariants its only caller guarantees (dhw_planner.py:1141 and the clipped
#   returns of _plan_dhw_cheapest_first).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g13 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._apply_dhw_min_run
#   (line 2057 `            unchanged: np.ndarray = np.clip(plan, 0.0, p_dhw_max)`), driven on features.py's _mr_fixture shape (weak slots spread over the horizon, a draw block)
#   over 12 seeds x 4 tank states x 3 horizon sizes = 144 fixtures.
# Perturbation: mutant 72240d3f22ceb752, the no-weak clip dropped (CLAMP_DROP), applied in memory (method recompiled from its own source, called unbound for
#   the mutant arm). Direction: an out-of-range no-weak plan is returned unclipped; production never feeds one.
# Null control: the in-range and nan no-weak plans, unchanged both arms.
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
OLD = "unchanged: np.ndarray = np.clip(plan, 0.0, p_dhw_max)"
NEW = "unchanged: np.ndarray = (plan)"
MUT = mutated(dhw_planner, BASE_FN, OLD, NEW)
moved, total = sweep(MUT)
joint, per_slot = joint_cases()
print(f"RESULT production_shaped_moved={len(moved)} of {total} {moved[:3]}")
print(f"RESULT baseline_paths joint_shortcut={joint} per_slot={per_slot} count")
# no-weak plans (the branch the line sits in): in range, above p_max, negative, nan
cases = {"in_range": {3: 2.0, 7: 0.0}, "above_pmax": {3: 3.5}, "negative": {6: -0.5}, "nan": {4: float("nan")}}
mv = []
for nm, slots in cases.items():
    p = np.zeros(24)
    for i, v in slots.items():
        p[i] = v
    b, m = run(p), run(p, MUT)
    print(f"RESULT no_weak_{nm} baseline={b[list(slots)].tolist()} mutant={m[list(slots)].tolist()}")
    if not np.array_equal(b, m, equal_nan=True):
        mv.append(nm)
print(f"RESULT direct_no_weak_moved={len(mv)} of {len(cases)} ({','.join(mv)})")
# Reach: the only caller (dhw_planner.py:1257) feeds _plan_dhw_cheapest_first's result, and every return of that
# method is np.clip(plan, 0.0, p_dhw_max) with the same p_dhw_run (dhw_planner.py:2191-2195, 2307).
import ast  # noqa: E402
_tree = ast.parse(SRC)
_fn = next(n for n in ast.walk(_tree) if isinstance(n, ast.FunctionDef) and n.name == "_plan_dhw_cheapest_first")
rets = [ast.get_source_segment(SRC, r.value) for r in ast.walk(_fn) if isinstance(r, ast.Return)
        and not any(isinstance(p, (ast.FunctionDef, ast.Lambda)) and p is not _fn and r in ast.walk(p)
                    for p in ast.walk(_fn))]
print(f"RESULT reach_cheapest_first_returns={rets}")
footer()
