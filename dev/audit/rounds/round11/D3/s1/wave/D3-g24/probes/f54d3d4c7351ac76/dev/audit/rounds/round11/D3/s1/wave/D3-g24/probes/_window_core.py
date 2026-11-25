# Shared driver of box D3-g24's two _window_offset_steps probes (not a harness itself). Per case
# (window minutes, dt hours, start time) it records, per arm: the method's own return value, and what
# every production consumer of that offset produces from it -- _peak_billing's PeakBilling with
# offset_steps itself left out (window_factors, day kwargs), the capacity penalty _grid_terms prices a
# fixed plan at (scalar and batch), and _grid_report's published dict -- or the exception raised.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import dataclasses  # noqa: E402
from datetime import datetime  # noqa: E402
from unittest import mock  # noqa: E402
import _mutlib  # noqa: E402
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import optimizer  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402


def _opt(window, masked):
    kw = dict(peak_window_minutes=window, peak_threshold_kw=1.0, peak_price_per_kw=50.0, peak_count=2)
    if masked:
        kw.update(peak_hours=[(7, 10), (17, 20)], peak_offpeak_factor=0.5, peak_weekdays_only=True)
    return HeatPumpOptimizer(ThermalModel(ThermalParameters()), OptimizationConfig(**kw))


def _norm(v):
    if isinstance(v, np.ndarray):
        return ("arr", v.shape, v.tolist())
    if isinstance(v, (list, tuple)):
        return tuple(_norm(x) for x in v)
    if isinstance(v, dict):
        return tuple(sorted((k, _norm(x)) for k, x in v.items()))
    return repr(v)


def outcome(window, dt, start, masked, n=24):
    opt = _opt(window, masked)
    try:
        off = opt._window_offset_steps(start, dt)
        bill = opt._peak_billing(n, dt, start)
        bd = {f.name: getattr(bill, f.name) for f in dataclasses.fields(bill) if f.name != "offset_steps"}
        rng = np.random.default_rng(7)
        plan = rng.uniform(0.0, 4.0, n)
        cap, capb = opt._grid_terms(n, dt, start)
        rep = opt._grid_report(plan, np.zeros(n), dt, start)
        down = _norm((bd, cap(plan), capb(np.vstack([plan, plan[::-1]])), rep))
    except Exception as e:
        return ("raise", type(e).__name__), None
    return ("ok", off), down


def cases():
    out = []
    for window in (15, 60):
        for dt in (0.25, 0.5, 1.0, 0.75, 1 / 60):
            for hh, mm in ((0, 0), (12, 0), (7, 0), (12, 15), (12, 45), (23, 30)):
                for masked in (False, True):
                    out.append((window, dt, datetime(2026, 1, 15, hh, mm), masked))
    for dt in (1e-9, 0.0, -0.25):
        for hh, mm in ((12, 0), (12, 15)):
            out.append((60, dt, datetime(2026, 1, 15, hh, mm), False))
    out.append((60, 0.25, None, False))
    return out


def run(old, new, label):
    mut = _mutlib.mutated(HeatPumpOptimizer, "_window_offset_steps", old, new, optimizer)
    ret_moved = down_moved = n = 0
    for window, dt, start, masked in cases():
        b_ret, b_down = outcome(window, dt, start, masked)
        with mock.patch.object(HeatPumpOptimizer, "_window_offset_steps", mut):
            m_ret, m_down = outcome(window, dt, start, masked)
        r, d = int(b_ret != m_ret), int(b_down != m_down)
        ret_moved += r
        down_moved += d
        n += 1
        if r or d:
            print(f"CASE window={window} dt={dt} start={start} masked={masked}: offset {b_ret} -> {m_ret}; downstream moved={d}")
    print(f"RESULT {label}_return_moved={ret_moved} count")
    print(f"RESULT {label}_downstream_moved={down_moved} count")
    print(f"RESULT {label}_cases_tried={n} count")
