"""Shared plumbing for box D3-g17's probes (round 11, D3-s1). Not a harness on its own.

Each probe_<key>.py imports this after its own thread pin. It builds the production
DhwPlanner the way tests/features.py and probe_0911281e.py do, a _DhwPlanContext on a
small fixed horizon, compiles a one-line mutant of a DhwPlanner method IN MEMORY from
the method's own source (never on disk), and prints the harness contract's footer.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time
from dataclasses import replace
from pathlib import Path

_T0 = (time.process_time(), time.thread_time())


def repo_root(start):
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
from custom_components.heatpump_optimizer import dhw_planner  # noqa: E402
from custom_components.heatpump_optimizer.dhw_planner import DhwPlanner, _DhwPlanContext  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402


def mutant(method_name, old, new, line=None):
    """The DhwPlanner method with one line edited, compiled in memory from the method's own source.

    With ``line`` (the absolute dhw_planner.py line the gate's mutant names) exactly that line is
    edited and must equal ``old`` verbatim (indentation included), as fullgate.py applies it on disk;
    without it ``old`` must occur exactly once in the dedented source."""
    fn = getattr(DhwPlanner, method_name)
    lines, start = inspect.getsourcelines(fn)
    if line is not None:
        i = line - start
        assert lines[i].rstrip("\n") == old, f"line {line} is {lines[i]!r}, not {old!r}"
        lines = list(lines)
        lines[i] = new + "\n"
        src = textwrap.dedent("".join(lines))
    else:
        src = textwrap.dedent("".join(lines))
        assert src.count(old) == 1, f"anchor ambiguous: {old!r} x{src.count(old)}"
        src = src.replace(old, new, 1)
    # Compiled in the live module namespace (not a copy), so a mock.patch.object on a dhw_planner
    # global (linprog) reaches both arms; the function's name is popped straight back out.
    ns = dhw_planner.__dict__
    code = compile("\n" * (start - 1) + src, dhw_planner.__file__, "exec")
    had = method_name in ns
    exec(code, ns)
    fn = ns[method_name] if had else ns.pop(method_name)
    return fn


def planner(**pkw):
    kw = dict(dhw_enabled=True, dhw_tank_volume=200.0, dhw_cooling_rate=0.3)
    kw.update(pkw)
    params = ThermalParameters(**kw)
    opt = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(
        horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0))
    return DhwPlanner(opt.model, opt.config, opt._pv_surplus, opt._price_known), params


def ctx(pl, params, prices, *, dt=1.0, outdoor=-5.0, p_dhw_max=3.0, min_run_power=0.1,
        max_lead_steps=24, cap=0.232):
    prices = np.asarray(prices, dtype=float)
    n = len(prices)
    return _DhwPlanContext(
        prices=prices, import_prices=prices, outdoor_temps=np.full(n, float(outdoor)), humidity=None,
        n_steps=n, dt=dt, store=replace(params.dhw_store, capacity_kwh_per_c=cap), p_dhw_max=p_dhw_max,
        min_run_power=min_run_power, max_lead_steps=max_lead_steps, tank_exo_kw=None)


def fmt(plan):
    if plan is None:
        return "None"
    if isinstance(plan, BaseException):
        return type(plan).__name__
    return "[" + ",".join(f"{x:.9g}" for x in np.asarray(plan, dtype=float)) + "]"


def call(fn, *a, **kw):
    """fn(*a, **kw), or the exception it raised (an exception is a value the metric reads)."""
    try:
        return fn(*a, **kw)
    except Exception as err:  # noqa: BLE001 - the probe records it
        return err


def differ(a, b, tol=1e-12):
    if isinstance(a, BaseException) or isinstance(b, BaseException) or a is None or b is None:
        return type(a) is not type(b) or (isinstance(a, BaseException) and type(a) is not type(b))
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if a.shape != b.shape:
        return True
    return not np.allclose(a, b, rtol=0.0, atol=tol, equal_nan=True)


def max_abs(a, b):
    if isinstance(a, BaseException) or isinstance(b, BaseException) or a is None or b is None:
        return float("nan") if (type(a) is type(b)) is False else 0.0
    return float(np.max(np.abs(np.asarray(a, float) - np.asarray(b, float)))) if len(a) else 0.0


def footer():
    p, t = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    swap = 0
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin "):
                swap = int(line.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={swap}")


def sweep_min_cost(fn, trials=120, seed=11, pmax_choices=(2.0, 3.0, 4.0), demand_lo=-1.0, demand_hi=4.0, N=16,
                   dts=(1.0, 0.25)):
    """Random min-cost scenarios (prices, space demand, floors, draws): baseline vs ``fn``.

    Returns (scenarios, differing, max_abs_delta_kw)."""
    rng = np.random.default_rng(seed)
    pl, params = planner()
    diff, worst = 0, 0.0
    for t in range(trials):
        dt = dts[t % len(dts)]
        prices = rng.uniform(0.0, 5.0, N)
        if t % 7 == 0:
            prices = np.round(prices)  # ties
        sd = rng.uniform(demand_lo, demand_hi, N)
        pmax = float(rng.choice(pmax_choices))
        req = np.full(N, 40.0); req[rng.integers(4, N, 3)] = 55.0
        draws = np.zeros(N); draws[rng.integers(0, N, 3)] = 2.0
        c = ctx(pl, params, prices, dt=dt)
        a = (pl, c, 45.0, req, draws, np.full(N, 65.0), sd, pmax)
        b, m = call(DhwPlanner._plan_dhw_min_cost, *a), call(fn, *a)
        if differ(b, m, 1e-9):
            diff += 1
            d = max_abs(b, m)
            worst = max(worst, d if d == d else float("inf"))
    return trials, diff, worst


def sweep_cheapest_first(fn, trials=120, seed=13, N=12, derate_choices=(0.0, 0.2), mrp_choices=(0.1, 0.5, 1.5)):
    """Random cheapest-first scenarios, with and without an initial plan: baseline vs ``fn``."""
    rng = np.random.default_rng(seed)
    diff, worst = 0, 0.0
    cache = {d: planner(cop_partload_derate=d) for d in derate_choices}
    for t in range(trials):
        pl, params = cache[derate_choices[t % len(derate_choices)]]
        prices = rng.uniform(0.0, 5.0, N)
        if t % 5 == 0:
            prices = np.round(prices)
        req = np.full(N, 40.0); req[rng.integers(3, N, 2)] = float(rng.choice([50.0, 55.0, 60.0]))
        draws = np.zeros(N); draws[rng.integers(0, N, 2)] = float(rng.choice([0.0, 2.0, 6.0]))
        c = ctx(pl, params, prices, min_run_power=float(rng.choice(mrp_choices)))
        ip = None if t % 2 else rng.choice([0.0, 0.5, 3.0], N) * (rng.uniform(0, 1, N) < 0.3)
        a = (pl, c, float(rng.choice([35.0, 45.0, 58.0])), req, draws, np.full(N, 65.0))
        b, m = call(DhwPlanner._plan_dhw_cheapest_first, *a, initial_plan=ip), call(fn, *a, initial_plan=ip)
        if differ(b, m, 1e-12):
            diff += 1
            d = max_abs(b, m)
            worst = max(worst, d if d == d else float("inf"))
    return trials, diff, worst
