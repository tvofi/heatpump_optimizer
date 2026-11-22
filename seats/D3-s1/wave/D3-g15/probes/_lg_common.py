#!/usr/bin/env python3
# Shared driver for box D3-g15's probes (not a harness on its own; each probe_<key>.py imports it).
# It drives the two production stages the box's 16 mutants sit in, DhwPlanner._dhw_legionella_due
# (dhw_planner.py:565-708) and DhwPlanner._dhw_legionella_ceilings (dhw_planner.py:710-815), directly
# on a minimal horizon (the same shape tests/features.py:_dhw_horizon builds), and applies a one-line
# mutant IN MEMORY: the method is recompiled from its own source with the line replaced and attached to
# DhwPlanner with mock.patch.object for the mutant arm only. No file is edited.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Run from the repository root, PYTHONPATH=tests/hastub.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import contextlib, inspect, sys, textwrap, time
from dataclasses import replace
from pathlib import Path
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
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import dhw_planner as dp  # noqa: E402
from custom_components.heatpump_optimizer import optimizer as optmod  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState)

_T0 = (time.process_time(), time.thread_time())


def mutant(method, old, new):
    """``DhwPlanner.<method>`` recompiled with the one line ``old`` -> ``new`` (stripped, must be unique)."""
    src = textwrap.dedent(inspect.getsource(getattr(dp.DhwPlanner, method)))
    o, n = old.strip(), new.strip()
    assert src.count(o) == 1, f"anchor {o!r} is not unique in {method}"
    ns = dict(dp.__dict__)
    exec(compile(src.replace(o, n, 1), dp.__file__, "exec"), ns)
    return ns[method]


@contextlib.contextmanager
def arm(method, fn):
    """The mutant arm: ``fn`` attached as ``DhwPlanner.<method>``; ``fn`` None is the baseline arm."""
    if fn is None:
        yield
    else:
        with mock.patch.object(dp.DhwPlanner, method, fn):
            yield


def params(**kw):
    base = dict(dhw_enabled=True, dhw_setpoint=55.0, dhw_legionella_enabled=True,
                dhw_legionella_temp=60.0, dhw_legionella_interval_days=7.0)
    base.update(kw)
    return ThermalParameters(**base)


def planner(p, price_known=None):
    return dp.DhwPlanner(ThermalModel(p), SimpleNamespace(pv_export_price=0.0), None, price_known)


def horizon(n=96, dt=0.25, *, dhw_temp=48.0, hours_since=20.0, prices=None, outdoor=None):
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=-5.0,
                      dhw_temperature=dhw_temp, dhw_hours_since_legionella=hours_since,
                      buffer_tank_temperature=40.0)
    k = max(n, 0)  # a negative n_steps (only ever a probe's input) gets empty arrays
    return optmod._Horizon(
        initial_state=st, prices=np.full(k, 1.0) if prices is None else prices,
        outdoor_temps=np.zeros(k) if outdoor is None else outdoor,
        wind_speeds=np.zeros(k), precipitation=np.zeros(k), solar_radiation=np.zeros(k),
        start_time=None, n_steps=n, dt=dt, comfort_targets=np.full(k, 21.0),
        temp_min_bounds=np.full(k, 17.0), temp_max_bounds=np.full(k, 23.0),
        step_hours=np.arange(k) * dt, solar_gains=np.zeros(k), heat_loss_factors=np.ones(k),
        forecast={}, t_start=0.0, step_weekdays=None, holiday_flags=None, humidity=None, dhw_pins=None)


def ceilings(p, h, *, step, draw=None, floor=None, p_run=4.0, exo=None, fn=None, planner_=None):
    """``_dhw_legionella_ceilings`` -> (max_temp, lp_max_temp, runup_temps) as lists, or the exception name."""
    n = h.n_steps
    pl = planner_ or planner(p)
    with arm("_dhw_legionella_ceilings", fn):
        try:
            r = pl._dhw_legionella_ceilings(
                h, params=p, draw_rates=np.zeros(max(n, 0)) if draw is None else draw,
                floor_temps=np.full(max(n, 0), 20.0) if floor is None else floor, p_dhw_run=p_run,
                legionella_due=step is not None, legionella_hour=None if step is None else float(step) * h.dt,
                legionella_step=step, exo_kw=exo)
        except Exception as exc:  # the mutant arm may raise where the baseline does not
            return f"raises {type(exc).__name__}"
    return (np.asarray(r.max_temp).tolist(), np.asarray(r.lp_max_temp).tolist(), np.asarray(r.runup_temps).tolist())


def due(p, h, *, draw=None, p_run=4.0, prices=None, off=None, fn=None, planner_=None):
    """``_dhw_legionella_due`` -> (due, hour, step, ready_temps list), or the exception name."""
    n = h.n_steps
    pl = planner_ or planner(p)
    ready = np.full(max(n, 0), 40.0)
    with arm("_dhw_legionella_due", fn):
        try:
            d, hr, st = pl._dhw_legionella_due(
                h, params=p, hours_mod=np.asarray(h.step_hours) % 24.0,
                draw_rates=np.zeros(max(n, 0)) if draw is None else draw, ready_temps=ready,
                p_dhw_run=p_run, dhw_prices=np.full(max(n, 0), 1.0) if prices is None else prices,
                off_steps=off, exo_kw=None)
        except Exception as exc:
            return f"raises {type(exc).__name__}"
    return (d, hr, st, ready.tolist())


def differs(a, b):
    return int(a != b)


def solve_reach(method, record, *, hours_since=20.0, interval=7.0, n=96, extra=None):
    """Drive the production ``HeatPumpOptimizer.optimize`` (DHW + legionella on) with a spy on
    ``DhwPlanner.<method>`` that appends ``record(kwargs, h)`` per call; returns the spy's list."""
    seen = []
    real = getattr(dp.DhwPlanner, method)

    def spy(self, h, **kw):
        seen.append(record(kw, h))
        return real(self, h, **kw)

    p = params(dhw_legionella_interval_days=interval, **(extra or {}))
    opt = optmod.HeatPumpOptimizer(ThermalModel(p), optmod.OptimizationConfig(
        horizon_hours=n // 4, time_step_minutes=15, target_temp=21.0, min_temp=19.0, max_temp=23.0))
    pr = np.full(n, 2.0)
    pr[:8] = 0.5
    from datetime import datetime
    with mock.patch.object(dp.DhwPlanner, method, spy):
        try:
            opt.optimize(inputs=optmod.SolveInputs(
                state=ThermalState(room_temperature=21.0, slab_temperature=25.0, outdoor_temperature=-5.0,
                                   dhw_temperature=48.0, dhw_hours_since_legionella=hours_since),
                start_time=datetime(2026, 1, 15, 12, 0),
                forecast=optmod.ForecastSeries(prices=pr, outdoor_temps=np.full(n, -5.0)),
                limits=optmod.SolveLimits()))
        except Exception as exc:
            seen.append(f"optimize raised {type(exc).__name__}")
    return seen


def footer():
    pc, tc = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
    except OSError:
        sw = 0
    print(f"RESULT swapins={sw} count")


def requirement(res, floor):
    """The planner's folded requirement held to the ceiling (dhw_planner.py:1174 then _within_ceiling),
    with ready temps zero: min(max(floor, runup), max_temp)."""
    mx, _lp, run = res
    return np.minimum(np.maximum(np.asarray(floor, float), np.asarray(run, float)), np.asarray(mx, float)).tolist()


def ulps(x, k):
    """``x`` and the ``k`` floats either side of it, nearest first."""
    out, lo, hi = [x], x, x
    for _ in range(k):
        lo, hi = np.nextafter(lo, -np.inf), np.nextafter(hi, np.inf)
        out += [float(lo), float(hi)]
    return out


HDR_MACHINE = "box D3-g15 (4 vCPU Intel Xeon @ 2.10GHz, Linux, python 3.14)"


def walk_tie(p, h, step, target, fn, k=300, base_draw=None, floor=None, p_run=4.0):
    """Search the draw at step ``step`` (the walk's first transition, m = step-1) for values that put the
    walk's first ``need`` exactly on ``target``: bisect the draw for the crossing of ``target`` (the
    baseline's run-up at step-1, or +inf once the walk breaks), then ``k`` floats either side of it.
    Returns (tie_hits, moved, tried, moved_under_tie, sample): tie_hits counts draws whose BASELINE
    run-up at step-1 equals ``target`` exactly; moved counts draws whose two arms' outputs differ."""
    n = h.n_steps
    draw0 = np.zeros(n) if base_draw is None else np.asarray(base_draw, float).copy()
    flo = np.full(n, 20.0) if floor is None else floor

    def first_need(d):
        dr = draw0.copy()
        dr[step] = d
        r = ceilings(p, h, step=step, draw=dr, floor=flo, p_run=p_run)
        v = r[2][step - 1]
        return v if v else float("inf")  # 0.0 = the walk broke before writing step-1

    lo, hi = float(draw0[step]), float(draw0[step]) + 1.0
    while first_need(hi) <= target:
        hi *= 2.0
    if first_need(lo) > target:
        return 0, 0, 0, 0, None
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if mid in (lo, hi):
            break
        if first_need(mid) <= target:
            lo = mid
        else:
            hi = mid
    hits = moved = tried = mt = 0
    sample = None
    for d in ulps(lo, k):
        if d < 0:
            continue
        dr = draw0.copy()
        dr[step] = d
        b = ceilings(p, h, step=step, draw=dr, floor=flo, p_run=p_run)
        m = ceilings(p, h, step=step, draw=dr, floor=flo, fn=fn, p_run=p_run)
        tried += 1
        hit = isinstance(b, tuple) and b[2][step - 1] == target
        hits += hit
        mv = b != m
        moved += mv
        mt += hit and mv
        if hit and sample is None:
            sample = (d, b, m)
    return hits, moved, tried, mt, sample


def solve(*, hours_since, interval=7.0, n=96, dhw_temp=48.0, prices=None, extra=None):
    """One production ``HeatPumpOptimizer.optimize`` with DHW and the legionella cycle on; the result."""
    from datetime import datetime
    p = params(dhw_legionella_interval_days=interval, **(extra or {}))
    opt = optmod.HeatPumpOptimizer(ThermalModel(p), optmod.OptimizationConfig(
        horizon_hours=n // 4, time_step_minutes=15, target_temp=21.0, min_temp=19.0, max_temp=23.0))
    if prices is None:
        prices = np.full(n, 2.0)
        prices[:8] = 0.5
    return opt.optimize(inputs=optmod.SolveInputs(
        state=ThermalState(room_temperature=21.0, slab_temperature=25.0, outdoor_temperature=-5.0,
                           dhw_temperature=dhw_temp, dhw_hours_since_legionella=hours_since),
        start_time=datetime(2026, 1, 15, 12, 0),
        forecast=optmod.ForecastSeries(prices=prices, outdoor_temps=np.full(n, -5.0)),
        limits=optmod.SolveLimits()))


def due_grid(fn, seed):
    """Both arms of ``_dhw_legionella_due`` over a grid that covers every branch of the hard-deadline placement:
    n_steps 4/96/192, hours_since from fresh to far overdue (deadline inside, at, past and before the horizon),
    initial tank 20..65 C (reach_step from 0 to unreachable), an Off window none / at step 0 / a band, and seeded
    random prices. Returns (tried, moved, branch counts {reach<n: k, overdue: k, reach>=n: k})."""
    rng = np.random.default_rng(seed)
    p = params()
    tried = moved = 0
    br = {"hard_reachable": 0, "hard_overdue_reachable": 0, "hard_unreachable": 0}
    for n in (4, 96, 192):
        for hs in (0.0, 100.0, 150.0, 167.0, 168.0, 170.0, 400.0, 2000.0):
            for t0 in (20.0, 45.0, 55.0, 59.5, 60.0, 65.0):
                for offk in ("none", "first", "band"):
                    off = None
                    if offk != "none":
                        off = np.zeros(n, dtype=bool)
                        if offk == "first":
                            off[0] = True
                        else:
                            off[n // 4: n // 2] = True
                    h = horizon(n=n, hours_since=hs, dhw_temp=t0)
                    pr = rng.uniform(0.1, 3.0, n)
                    b = due(p, h, prices=pr, off=off)
                    m = due(p, h, prices=pr, off=off, fn=fn)
                    tried += 1
                    moved += b != m
                    dl = int(np.floor((168.0 - hs) / h.dt))
                    if dl < n:
                        pl = planner(p)
                        o = _legionella_off_mask_(off, n)
                        ramp = pl._dhw_plan_temps(dp._legionella_charge(n, 4.0, o), t0, h.outdoor_temps,
                                                  np.zeros(n), h.dt, None, None)
                        hot = np.where(ramp[1:] >= p.dhw_legionella_temp - 1e-6)[0]
                        rs = int(hot[0]) if hot.size else n
                        key = "hard_unreachable" if rs >= n else ("hard_overdue_reachable" if dl < 0 else "hard_reachable")
                        br[key] += 1
    return tried, moved, br


def _legionella_off_mask_(off, n):
    return dp._legionella_off_mask(off, n)
