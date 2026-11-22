#!/usr/bin/env python3
# Metric: count of inputs on which DhwPlanner._repair_dhw_floor's repaired DHW plan differs under the mutant, which
#   can only differ where a top-up's new level equals min_run_power - 1e-9 exactly: (a) exact ties sought by
#   bisecting the start temperature to double precision across every sign change of new_level - (min_run - 1e-9)
#   in the first repair round (700 seeded near-ceiling calls, the crossing and 8 doubles either side tested), the
#   plans compared raw and rounded to 1 W; (b) 1500 seeded calls with no tie forced.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_3c6e75178a60d75e.py
# EXPECTED RESULT crossings_bisected=135 count
# EXPECTED RESULT inputs_tried_at_crossings=2430 count
# EXPECTED RESULT exact_ties=2 count
# EXPECTED RESULT differing_at_ties=2 count
# EXPECTED RESULT max_delta_at_ties_kw=3.89e-16 kW   (the tied step is lifted by the 1e-9 epsilon, then clamped)
# EXPECTED RESULT differing_at_ties_rounded_1w=0 count
# EXPECTED RESULT differing_plain_calls=0 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g18 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: heatpump_optimizer.dhw_planner:DhwPlanner._repair_dhw_floor, line 1870
#   `if new_level < min_run_power - 1e-9:`, reached from DhwPlanner._build_dhw_requirements via place_startable.
# Perturbation: mutant 3c6e75178a60d75e, `<` -> `<=`, applied in memory (the method is recompiled from its own
#   source for the mutant arm). Direction: a level exactly 1e-9 under the minimum run is raised to a runnable block.
# Null control: arm (b), seeded calls with no tie forced.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path


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
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))
import inspect  # noqa: E402
import logging  # noqa: E402
import textwrap  # noqa: E402
from dataclasses import replace  # noqa: E402
from unittest import mock  # noqa: E402

import numpy as np  # noqa: E402

logging.disable(logging.CRITICAL)
from heatpump_optimizer import dhw_planner  # noqa: E402
from heatpump_optimizer.dhw_planner import DhwPlanner, _DhwPlanContext  # noqa: E402
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402

SRC = textwrap.dedent(inspect.getsource(DhwPlanner._repair_dhw_floor))


def mutant(old, new):
    """_repair_dhw_floor recompiled from its own source with one line edited (in memory)."""
    assert SRC.count(old) == 1, "anchor line moved"
    ns = dict(dhw_planner.__dict__)
    exec(compile(SRC.replace(old, new, 1), dhw_planner.__file__, "exec"), ns)
    return ns["_repair_dhw_floor"]


def case(rng, prod=True):
    """One seeded direct call of the floor repair: tank, horizon, prices, ceiling, requirement, draws and an
    initial plan. prod=True keeps the envelope _build_dhw_requirements guarantees (dhw_planner.py:1138-1141):
    p_dhw_max >= 0.1 and min_run_power <= p_dhw_max."""
    vol = float(rng.choice([80.0, 150.0, 200.0, 300.0]))
    params = ThermalParameters(dhw_enabled=True, dhw_tank_volume=vol, dhw_cooling_rate=float(rng.choice([0.05, 0.1, 0.3, 1.0, 3.0])))  # config range 0.05..3.0 (config_flow.py:1800)
    opt = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(
        horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pl = DhwPlanner(opt.model, opt.config, opt._pv_surplus, opt._price_known)
    n = int(rng.integers(4, 16))
    dt = float(rng.choice([0.25, 0.5, 1.0]))
    if prod:
        pmax = float(rng.choice([0.1, 0.3, 1.0, 2.0, 3.0, 4.8]))
        mrp = min(pmax, float(rng.choice([0.15, 0.3, 0.6, 1.2, 2.4])))
    else:
        pmax = float(rng.choice([0.3, 1.0, 2.0]))
        mrp = float(rng.choice([2.5, 4.0]))
    prices = rng.uniform(0, 5, n)
    ctx = _DhwPlanContext(
        prices=prices, import_prices=prices, outdoor_temps=rng.uniform(-15, 15, n), humidity=None, n_steps=n, dt=dt,
        store=replace(params.dhw_store, capacity_kwh_per_c=vol * 0.00116), p_dhw_max=pmax, min_run_power=mrp,
        max_lead_steps=24, tank_exo_kw=None)
    ceil = float(rng.choice([50.0, 55.0, 60.0, 65.0]))
    req = np.full(n, float(rng.uniform(35, ceil + 3)))
    if rng.random() < 0.5:
        req[: int(rng.integers(0, n))] = 0.0
    mt = np.full(n, ceil)
    if rng.random() < 0.3:
        mt[: n // 2] = ceil + 10
    plan = np.where(rng.random(n) < 0.4, rng.uniform(0, pmax, n), 0.0)
    draws = rng.uniform(0, 3, n) * (rng.random(n) < 0.5)
    it = float(rng.uniform(30, ceil + 2))
    fo = (rng.random(n) < 0.2) if rng.random() < 0.3 else None
    sb = np.full(n, float(it - rng.uniform(-5, 10))) if rng.random() < 0.3 else None
    kw = dict(plan=plan, initial_temp=it, draw_rates=draws, requirement=req, max_temp=mt, forced_off=fo, start_below=sb)
    return pl, ctx, kw


def golden_repair_calls(names=("winter_single_dhw", "winter_two_zone_dhw", "summer_dhw_only")):
    """The (planner, ctx, kwargs) of every _repair_dhw_floor call three golden DHW scenarios make."""
    import copy
    import golden
    calls = []
    real = DhwPlanner._repair_dhw_floor

    def spy(self, ctx, **kw):
        calls.append((self, copy.deepcopy(ctx), copy.deepcopy(kw)))
        return real(self, ctx, **kw)

    with mock.patch.object(DhwPlanner, "_repair_dhw_floor", spy):
        for name in names:
            golden.capture(name, golden.SCENARIOS[name])
    return calls


def traced(old, expr):
    """_repair_dhw_floor (baseline behaviour) that records `expr`, the compared quantity minus its threshold,
    each time the line `old` is about to run."""
    assert SRC.count(old) == 1, "anchor line moved"
    indent = SRC.split(old)[0].split("\n")[-1]
    ns = dict(dhw_planner.__dict__, TR=[])
    exec(compile(SRC.replace(old, f"TR.append(np.array({expr}, dtype=float))\n{indent}{old}", 1),
                 dhw_planner.__file__, "exec"), ns)
    return ns


def near_ceiling_case(rng):
    """A seeded production-envelope call biased toward the boundaries: a tank started just under its ceiling with a
    later draw opening a breach, half the time behind a ceiling that steps up (a disinfection raise)."""
    pl, ctx, kw = case(rng)
    n = ctx.n_steps
    ceil = float(kw["max_temp"][-1])
    if rng.random() < 0.7:
        draws = np.zeros(n)
        k0 = int(rng.integers(1, n))
        draws[k0] = float(rng.uniform(0.5, 6))
        req = np.zeros(n)
        req[k0:] = float(ceil - rng.uniform(0.05, 2))
        kw = dict(kw, initial_temp=float(ceil - rng.uniform(0, 0.6)), draw_rates=draws, requirement=req,
                  plan=np.zeros(n), forced_off=None, start_below=None)
        if rng.random() < 0.7:
            k1 = int(rng.integers(1, n))
            mt = np.full(n, ceil)
            mt[k1:] = ceil + float(rng.uniform(0.02, 1.5))
            req = np.zeros(n)
            req[k1:] = mt[k1:] - float(rng.uniform(0.0, 0.3))
            kw = dict(kw, max_temp=mt, requirement=req, initial_temp=float(ceil - rng.uniform(0, 0.3)))
    return pl, ctx, kw


def first_trace(ns, pl, ctx, kw, x):
    ns["TR"].clear()
    try:
        ns["_repair_dhw_floor"](pl, ctx, **dict(kw, initial_temp=float(x)))
    except Exception:  # an input the bisection walks into that the repair rejects is simply not a tie
        return None
    return ns["TR"][0].copy() if ns["TR"] else None


TIE_ROUNDED = [0]  # differing plans at the exact ties once rounded to 1 W (0.001 kW)


def tie_search(bisect_ns, check_ns, mut_fn, seed, n_cases, scan=0, widths=(0.02, 0.2, 1.0)):
    """Bisect the start temperature to double precision across every sign change of the quantity `bisect_ns`
    records (first repair round), then test the crossing (and `scan` doubles either side) for an exact zero of the
    quantity `check_ns` records; at each exact tie compare the baseline's repaired plan with the mutant's."""
    rng = np.random.default_rng(seed)
    cross = tried = ties = differ = 0
    max_d = 0.0
    TIE_ROUNDED[:] = [0]
    for _ in range(n_cases):
        pl, ctx, kw = near_ceiling_case(rng)
        it0 = kw["initial_temp"]
        for w in widths:
            a = first_trace(bisect_ns, pl, ctx, kw, it0 - w)
            b = first_trace(bisect_ns, pl, ctx, kw, it0 + w)
            if a is None or b is None or a.shape != b.shape:
                continue
            for e in range(a.size):
                if a[e] == 0 or b[e] == 0 or np.sign(a[e]) == np.sign(b[e]):
                    continue
                cross += 1
                x0, x1, ok = it0 - w, it0 + w, True
                for _ in range(90):
                    xm = 0.5 * (x0 + x1)
                    if xm in (x0, x1):
                        break
                    t = first_trace(bisect_ns, pl, ctx, kw, xm)
                    if t is None or t.shape != a.shape:
                        ok = False
                        break
                    if np.sign(t[e]) == np.sign(a[e]):
                        x0 = xm
                    else:
                        x1 = xm
                if not ok:
                    continue
                xs = [x0, x1]
                lo = hi = x0
                for _ in range(scan):
                    lo, hi = float(np.nextafter(lo, -np.inf)), float(np.nextafter(hi, np.inf))
                    xs += [lo, hi]
                for x in xs:
                    tried += 1
                    q = first_trace(check_ns, pl, ctx, kw, x)
                    idx = e if check_ns is bisect_ns else 0
                    if q is None or q.size <= idx or q[idx] != 0.0:
                        continue
                    ties += 1
                    kk = dict(kw, initial_temp=float(x))
                    bp, mp = DhwPlanner._repair_dhw_floor(pl, ctx, **kk), mut_fn(pl, ctx, **kk)
                    if not np.array_equal(bp, mp):
                        differ += 1
                        max_d = max(max_d, float(np.abs(bp - mp).max()))
                        TIE_ROUNDED[0] += not np.array_equal(np.round(bp, 3), np.round(mp, 3))
                break
    return cross, tried, ties, differ, max_d
OLD = "if new_level < min_run_power - 1e-9:"
MUT = mutant(OLD, "if new_level <= min_run_power - 1e-9:")
Q = traced(OLD, "[new_level - (min_run_power - 1e-9)]")
cross, tried, ties, differ, max_d = tie_search(Q, Q, MUT, seed=13, n_cases=700, scan=8)
rng = np.random.default_rng(14)
plain = 0
for _ in range(1500):
    pl, ctx, kw = case(rng)
    plain += not np.array_equal(DhwPlanner._repair_dhw_floor(pl, ctx, **kw), MUT(pl, ctx, **kw))
print(f"RESULT crossings_bisected={cross} count")
print(f"RESULT inputs_tried_at_crossings={tried} count")
print(f"RESULT exact_ties={ties} count")
print(f"RESULT differing_at_ties={differ} count")
print(f"RESULT max_delta_at_ties_kw={max_d:.3g} kW")
print(f"RESULT differing_at_ties_rounded_1w={TIE_ROUNDED[0]} count")
print(f"RESULT differing_plain_calls={plain} count")

import resource as _resource  # noqa: E402
import time as _time  # noqa: E402

print(f"RESULT thread_factor={_time.process_time() / max(_time.thread_time(), 1e-9):.3f} ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={_resource.getrusage(_resource.RUSAGE_SELF).ru_nswap} count")
