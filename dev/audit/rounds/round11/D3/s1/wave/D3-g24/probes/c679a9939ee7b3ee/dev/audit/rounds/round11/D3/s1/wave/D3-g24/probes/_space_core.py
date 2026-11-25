# Shared driver of box D3-g24's two _solve_space probes (not a harness itself). It runs real DHW solves
# (dhw_enabled, 12 h / 15-min, a total-power cap power_caps_extra so the space headroom sits below p_max
# while a DHW block runs) and captures every HeatPumpOptimizer._solve_space call the solve makes. Then:
#   replay: each captured call re-run with the baseline and with the mutant method on the same optimizer and
#     the same arguments, with the captured warm start and with crafted ones (the warm start x1.5, + p_max,
#     with negative entries, all NaN-free) -- comparing the returned (power, status, score);
#   whole: the full optimize() in both arms (mutant patched onto the class) -- comparing the published plan.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import copy  # noqa: E402
from datetime import datetime, timezone  # noqa: E402
from unittest import mock  # noqa: E402
import _mutlib  # noqa: E402
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import optimizer  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import (  # noqa: E402
    ForecastSeries, HeatPumpOptimizer, OptimizationConfig, SolveInputs, SolveLimits)
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402

N = 48
SCEN = {
    "dhw_cap3": dict(cap=3.0, out=-5.0),
    "dhw_cap2": dict(cap=2.0, out=-12.0),
    "dhw_cap1": dict(cap=1.0, out=-12.0),
}


def _solve(name, cls_patch=None, capture=None):
    s = SCEN[name]
    opt = HeatPumpOptimizer(ThermalModel(ThermalParameters(dhw_enabled=True)), OptimizationConfig(
        horizon_hours=12, time_step_minutes=15, target_temp=21.0, min_temp=19.0, max_temp=23.0))
    pr = np.full(N, 2.0)
    pr[:8] = 0.4
    pr[20:28] = 0.6
    inputs = SolveInputs(
        state=ThermalState(room_temperature=20.5, slab_temperature=24.0, outdoor_temperature=s["out"],
                           dhw_temperature=38.0),
        start_time=datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc),
        forecast=ForecastSeries(prices=pr, outdoor_temps=np.full(N, s["out"])),
        limits=SolveLimits(power_caps_extra=np.full(N, s["cap"])))
    real = HeatPumpOptimizer._solve_space if cls_patch is None else cls_patch

    def spy(self, *a, **k):
        if capture is not None:
            capture.append((self, copy.deepcopy(a), k))
        return real(self, *a, **k)
    with mock.patch.object(HeatPumpOptimizer, "_solve_space", spy):
        r = opt.optimize(inputs=inputs)
    return r


OUT_OF_BOX = {"n": 0}
_REAL_SEED = HeatPumpOptimizer._seed_pinned_guess


def _seed_spy(self, guess, bounds):
    lo = np.array([b[0] for b in bounds], dtype=float)
    hi = np.array([b[1] for b in bounds], dtype=float)
    g = np.asarray(guess, dtype=float)
    OUT_OF_BOX["n"] += int(np.any(g < lo - 1e-12) or np.any(g > hi + 1e-12))
    return _REAL_SEED(self, guess, bounds)


def _out(fn, opt, a, k):
    saved = opt._space_avail
    try:
        with mock.patch.object(HeatPumpOptimizer, "_seed_pinned_guess", _seed_spy):
            p, st, sc = fn(opt, *a, **k)
        return ("ok", np.asarray(p, dtype=float), st, float(sc))
    except Exception as e:
        return ("raise", type(e).__name__)
    finally:
        opt._space_avail = saved


def _diff(b, m):
    if b[0] != m[0]:
        return 1, float("inf")
    if b[0] == "raise":
        return 0, 0.0
    d = float(np.max(np.abs(b[1] - m[1]))) if b[1].size else 0.0
    return int(d > 0 or b[2] != m[2] or b[3] != m[3]), d


def run(old, new, label):
    mut = _mutlib.mutated(HeatPumpOptimizer, "_solve_space", old, new, optimizer)
    base = HeatPumpOptimizer._solve_space
    replay_moved = replay_n = whole_moved = 0
    oob_base = oob_mut = 0
    warm_calls = above_headroom = negative = 0
    for name in SCEN:
        cap = []
        rb = _solve(name, capture=cap)
        for self_, a, k in cap:
            dhw_plan, warm, h, p_max = a[0], a[1], a[2], a[3]
            variants = [("captured", warm)]
            if warm is not None:
                warm_calls += 1
                w = np.asarray(warm, dtype=float)
                variants += [("x1.5", w * 1.5), ("+p_max", w + p_max), ("neg", w - 0.5 * p_max)]
            else:
                ib = np.asarray(a[7], dtype=float)
                variants += [("none_initbase_x2", None), ("warm=init_base*1.5", ib * 1.5),
                             ("warm=init_base+p_max", ib + p_max), ("warm=init_base-p_max/2", ib - 0.5 * p_max),
                             ("warm=-1", np.full_like(ib, -1.0))]
            for vname, ws in variants:
                aa = list(a)
                aa[1] = ws
                if vname == "none_initbase_x2":
                    aa[7] = np.asarray(a[7], dtype=float) * 2.0 - 0.5
                n0 = OUT_OF_BOX["n"]
                b = _out(base, self_, aa, k)
                n1 = OUT_OF_BOX["n"]
                m = _out(mut, self_, aa, k)
                oob_base += n1 - n0
                oob_mut += OUT_OF_BOX["n"] - n1
                d, mag = _diff(b, m)
                replay_moved += d
                replay_n += 1
                if d:
                    print(f"CASE {name}/{vname}: baseline={b[0]} "
                          f"{b[2] if b[0] == 'ok' else b[1]} score={b[3] if b[0] == 'ok' else '-'} | mutant={m[0]} "
                          f"{m[2] if m[0] == 'ok' else m[1]} score={m[3] if m[0] == 'ok' else '-'} maxabs={mag:.6g} kW")
        rm = _solve(name, cls_patch=mut)
        pb, pm = np.asarray(rb.power_schedule, dtype=float), np.asarray(rm.power_schedule, dtype=float)
        wd = float(np.max(np.abs(pb - pm)))
        wm = int(wd > 0 or rb.status != rm.status)
        whole_moved += wm
        print(f"WHOLE {name}: calls={len(cap)} status {rb.status!r} -> {rm.status!r} plan maxabs={wd:.6g} kW moved={wm}")
    print(f"RESULT {label}_replay_moved={replay_moved} count")
    print(f"RESULT {label}_replay_tried={replay_n} count")
    print(f"RESULT {label}_guess_outside_bounds_baseline={oob_base} count")
    print(f"RESULT {label}_guess_outside_bounds_mutant={oob_mut} count")
    print(f"RESULT {label}_whole_moved={whole_moved} count")
    print(f"RESULT {label}_whole_tried={len(SCEN)} count")
    print(f"RESULT {label}_captured_warm_calls={warm_calls} count")
