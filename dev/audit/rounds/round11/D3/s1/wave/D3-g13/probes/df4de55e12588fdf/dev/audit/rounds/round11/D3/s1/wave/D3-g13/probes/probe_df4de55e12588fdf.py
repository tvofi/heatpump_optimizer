#!/usr/bin/env python3
# Metric: the power (kW) _apply_dhw_min_run returns for a slot planned at exactly 1e-6 kW (the weak-slot floor), tank with room and tank full, plus the 144-fixture production-shaped sweep.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_df4de55e12588fdf.py
# EXPECTED RESULT slot_kw_at_1e-6_baseline=1e-06   (left as a 1 W trickle, not a weak slot)
# EXPECTED RESULT slot_kw_at_1e-6_mutant=0.6       (raised to min_run_power; 0.0 when the tank is full)
# EXPECTED RESULT boundary_inputs_moved=2 of 6     (only the exact 1e-6; its float neighbours agree)
# EXPECTED RESULT production_shaped_moved=0 of 144
# Count key: the plan array DhwPlanner._apply_dhw_min_run returns (np.array_equal, baseline vs mutant), fed straight
#   back into DhwPlanner.optimize's schedule (dhw_planner.py:1257); production-shaped = 0 <= plan <= p_dhw_max and
#   min_run_power <= p_dhw_max, the two invariants its only caller guarantees (dhw_planner.py:1141 and the clipped
#   returns of _plan_dhw_cheapest_first).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g13 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._apply_dhw_min_run
#   (line 2055 `        weak = np.where((plan > 1e-6) & (plan < min_run_power))[0]`), driven on features.py's _mr_fixture shape (weak slots spread over the horizon, a draw block)
#   over 12 seeds x 4 tank states x 3 horizon sizes = 144 fixtures.
# Perturbation: mutant df4de55e12588fdf, `plan > 1e-6` -> `plan >= 1e-6`, applied in memory (method recompiled from its own source, called unbound for
#   the mutant arm). Direction: a slot of exactly 1e-6 kW is repaired (raised or zeroed) instead of left in the plan.
# Null control: the float neighbours of 1e-6 (nextafter either side): the same answer both arms.
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
OLD = "weak = np.where((plan > 1e-6) & (plan < min_run_power))[0]"
NEW = "weak = np.where((plan >= 1e-6) & (plan < min_run_power))[0]"
MUT = mutated(dhw_planner, BASE_FN, OLD, NEW)
moved, total = sweep(MUT)
joint, per_slot = joint_cases()
print(f"RESULT production_shaped_moved={len(moved)} of {total} {moved[:3]}")
print(f"RESULT baseline_paths joint_shortcut={joint} per_slot={per_slot} count")
res = {}
for nm, kw in (("tank_room", dict(initial=35.0, ceiling=55.0)), ("tank_full", dict(initial=50.0, ceiling=50.0))):
    for v in (1e-6, np.nextafter(1e-6, 0.0), np.nextafter(1e-6, 1.0)):
        p = np.zeros(24); p[5] = v
        res[(nm, float(v))] = (float(run(p, **kw)[5]), float(run(p, MUT, **kw)[5]))
for (nm, v), (b, m) in res.items():
    print(f"RESULT slot_at_{v!r}_{nm} baseline={b!r} mutant={m!r}")
b, m = res[("tank_room", 1e-6)]
print(f"RESULT slot_kw_at_1e-6_baseline={b!r}")
print(f"RESULT slot_kw_at_1e-6_mutant={m!r}")
print(f"RESULT boundary_inputs_moved={sum(b != m for b, m in res.values())} of {len(res)}")
footer()
