# Shared driver of box D3-g24's five _stash_price_horizon probes (not a harness itself): calls
# HeatPumpOptimizer._stash_price_horizon on one optimizer per arm for each input case and compares
# what it hands the solve: the returned price array and the stashed _price_known / _pv_surplus
# (values, dtype, finiteness), or the exception it raises.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import _mutlib  # noqa: E402
import numpy as np  # noqa: E402
from unittest import mock  # noqa: E402
from custom_components.heatpump_optimizer import optimizer  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402

STATE = ThermalState(room_temperature=21.0, slab_temperature=25.0, outdoor_temperature=-5.0)


def _call(fn, lam, n, known, sigma, prices, pv):
    opt = HeatPumpOptimizer(ThermalModel(ThermalParameters()), OptimizationConfig(price_risk_lambda=lam))
    try:
        out = fn(opt, STATE, n, known, sigma, prices, pv)
    except Exception as e:  # the outcome IS the number for a guard probe
        return ("raise", type(e).__name__)
    arr = np.asarray(out)
    return ("ok", arr.dtype.str, arr.tolist(), opt._price_known.dtype.str, opt._price_known.tolist(),
            opt._pv_surplus.dtype.str, opt._pv_surplus.tolist())


def _same(a, b):
    if a[0] != b[0]:
        return False
    if a[0] == "raise":
        return a[1] == b[1]
    return all(np.array_equal(np.asarray(x), np.asarray(y), equal_nan=True) if isinstance(x, list) else x == y
               for x, y in zip(a[1:], b[1:]))


def run(old, new, cases, label):
    base = HeatPumpOptimizer._stash_price_horizon
    mut = _mutlib.mutated(HeatPumpOptimizer, "_stash_price_horizon", old, new, optimizer)
    moved = 0
    for name, lam, n, known, sigma, prices, pv in cases:
        b = _call(base, lam, n, known, sigma, prices, pv)
        m = _call(mut, lam, n, known, sigma, prices, pv)
        d = int(not _same(b, m))
        moved += d
        short = lambda r: r if r[0] == "raise" else ("ok", "prices", r[1], [round(x, 6) if isinstance(x, float) else x for x in r[2]][:6])
        print(f"CASE {name}: baseline={short(b)} mutant={short(m)} moved={d}")
    print(f"RESULT {label}_cases_moved={moved} count")
    print(f"RESULT {label}_cases_tried={len(cases)} count")
    return moved


def reach(old, new, lam, sigma, label, known_hours=2):
    """Drive the production HeatPumpOptimizer.optimize (6 h horizon, 15-min steps, the first
    known_hours published) in both arms; print the plan's max |power| difference, its NaN count and
    its status, or the exception optimize raises."""
    from datetime import datetime
    from custom_components.heatpump_optimizer.optimizer import ForecastSeries, SolveInputs, SolveLimits
    n = 24
    pr = np.full(n, 2.0)
    pr[:4] = 0.5
    known = np.zeros(n, dtype=bool)
    known[: known_hours * 4] = True
    mut = _mutlib.mutated(HeatPumpOptimizer, "_stash_price_horizon", old, new, optimizer)

    def solve():
        opt = HeatPumpOptimizer(ThermalModel(ThermalParameters()), OptimizationConfig(
            horizon_hours=6, time_step_minutes=15, target_temp=21.0, min_temp=19.0, max_temp=23.0,
            price_risk_lambda=lam))
        fs = ForecastSeries(prices=pr, outdoor_temps=np.full(n, -5.0), price_known=known,
                            **({} if sigma is None else {"price_sigma": np.asarray(sigma, dtype=float)}))
        try:
            r = opt.optimize(inputs=SolveInputs(state=STATE, start_time=datetime(2026, 1, 15, 12, 0),
                                                forecast=fs, limits=SolveLimits()))
        except Exception as e:
            return ("raise", f"{type(e).__name__}: {str(e)[:80]}")
        ps = np.asarray(r.power_schedule, dtype=float)
        return ("ok", ps, r.status)
    b = solve()
    with mock.patch.object(HeatPumpOptimizer, "_stash_price_horizon", mut):
        m = solve()
    if b[0] == m[0] == "ok":
        diff = float(np.nanmax(np.abs(b[1] - m[1]))) if np.isfinite(b[1] - m[1]).any() else float("nan")
        print(f"REACH {label}: baseline status={b[2]!r} nan={int(np.isnan(b[1]).sum())} | mutant status={m[2]!r} nan={int(np.isnan(m[1]).sum())}")
        print(f"RESULT {label}_plan_maxabs_diff_kw={diff:.6g} kW")
        print(f"RESULT {label}_moved={int(diff > 0 or b[2] != m[2] or np.isnan(b[1]).sum() != np.isnan(m[1]).sum())} count")
    else:
        print(f"REACH {label}: baseline={b if b[0] == 'raise' else ('ok', b[2])} mutant={m if m[0] == 'raise' else ('ok', m[2])}")
        print(f"RESULT {label}_moved={int(b[0] != m[0])} count")
