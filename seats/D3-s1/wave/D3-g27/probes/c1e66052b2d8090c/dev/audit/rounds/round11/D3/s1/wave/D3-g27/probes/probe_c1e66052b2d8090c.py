#!/usr/bin/env python3
# Metric: whether optimizer._fd_steps's steps differ between baseline and mutant where the gradient reads them (the free mask, or a free variable's step), counted over a crafted boundary grid, its production-domain subset (eps=_LBFGSB_FD_EPS, 0<=lb<=x0<=ub<=100 kW) and 20000 seeded random inputs; plus, over four production solves (tests/manual_plan.py's winter house: plain, space-pinned, DHW-pinned, capped-pinned), the _fd_steps calls and batched gradients that move and the largest plan power delta (kW).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g27/probes/probe_c1e66052b2d8090c.py
#   (from the repository root; $HOME/venv-ci on this box is /opt/hpo/venv-ci)
# EXPECTED RESULT example_input=x0=0.0,eps=0.0001,lb=0.0001,ub=0.00010000000000000002
# EXPECTED RESULT h_baseline=0.0001
# EXPECTED RESULT h_mutant=-0.0001
# EXPECTED RESULT crafted_inputs_tried=38449 count
# EXPECTED RESULT crafted_inputs_moved=720 count
# EXPECTED RESULT domain_inputs_tried=1255 count
# EXPECTED RESULT domain_inputs_moved=0 count
# EXPECTED RESULT random_inputs_tried=19129 count
# EXPECTED RESULT random_inputs_moved=0 count
# EXPECTED RESULT production_fd_calls=76 count
# EXPECTED RESULT production_fd_calls_moved=0 count
# EXPECTED RESULT production_gradients=76 count
# EXPECTED RESULT production_gradients_moved=0 count
# EXPECTED RESULT production_plan_max_abs_delta_kw=0 kW
# EXPECTED RESULT null_inputs_moved=0 count
# EXPECTED RESULT null_plan_max_abs_delta_kw=0 kW
#   (counts are exact and deterministic, the random grid seeded; kW and objective deltas are solver floats, re-taken to 1e-3 relative on another BLAS build; thread_factor, load1, swapins quoted, not expected)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g27 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux, venv-ci CPython 3.14).
# Instrumented symbol: heatpump_optimizer.optimizer:_fd_steps, custom_components/heatpump_optimizer/optimizer.py:1577 `violated = (x < lb) | (x > ub)`.
# Perturbation: key c1e66052b2d8090c (CMP_BOUND), `violated = (x < lb) | (x > ub)` -> `violated = (x <= lb) | (x > ub)`, applied in memory: the function is
#   re-compiled from its own source with the one line replaced, in a copy of the module namespace; the production solves
#   see it through mock.patch.object on the module the suite imports (heatpump_optimizer.optimizer). Direction: a moved step is the mutant's; any production gradient or plan delta is the mutant's direction.
# Null control: the same function re-compiled with the line unchanged (the null_* RESULT lines), expected 0 moved.
# Count key: the step vector h (and free mask) _fd_steps returns, read only where _fd_divide reads it, never an input attribute.
# Out of the D3-g27 full-gate wave (round 11, seat D3-s1): the key's full gate is gates/<key>.json in this wave dir.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, math, sys, textwrap, time
from pathlib import Path
from unittest import mock


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents, Path.cwd()):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))
import numpy as np  # noqa: E402
import harness  # noqa: E402,F401  (the suite's stub wiring, as tests/manual_plan.py imports it)
# the package path the suite's solves import (heatpump_optimizer.*), so a patch reaches them
from heatpump_optimizer import optimizer as opt  # noqa: E402

_T0 = (time.process_time(), time.thread_time())


def mutant(fn_name, old, new):
    """``fn_name`` re-compiled from its own source with the one mutated line, in a copy of
    the module namespace (the module itself is untouched)."""
    fn = getattr(opt, fn_name)
    src = textwrap.dedent(inspect.getsource(fn))
    assert src.count(old.strip()) == 1, (fn_name, old)
    src = src.replace(old.strip(), new.strip())
    ns = dict(opt.__dict__)
    exec(compile(src, opt.__file__, "exec"), ns)
    return ns[fn_name]


def result(name, value, unit=""):
    print(f"RESULT {name}={value}{(' ' + unit) if unit else ''}")


def tail():
    cpu, thr = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    result("thread_factor", f"{cpu / thr:.3f}" if thr > 0 else "1.000")
    result("load1", f"{os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "na"
    result("swapins", sw)


def load_mp():
    """tests/manual_plan.py's optimizer builder (the module has a __main__ guard)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("_mp_probe", str(ROOT / "tests" / "manual_plan.py"))
    mp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mp)
    return mp


def production_solves(mp):
    """The production solves every reach count runs: HeatPumpOptimizer.optimize on
    tests/manual_plan.py's winter house (with DHW): unpinned; space-pinned (on at step 36, off
    at 40-43, on at every step whose headroom beside the unpinned plan's DHW is below the pin's
    on-power, free elsewhere); DHW-pinned (on at step 20, off at 60-63, free elsewhere); and
    space-pinned on at step 36 under a 0.05 kW total power cap there (power_caps_extra), a step
    whose upper bound is below the pin's on-power."""
    bundle = mp._build_optimizer("winter_typical", "winter_cold")
    out = {"plain": mp._solve(bundle)}
    n = mp.N
    p_max = bundle[0].model.params.max_electrical_power
    on_power = bundle[0]._pin_on_power(p_max)
    full = [i for i, v in enumerate(out["plain"].dhw_power_schedule) if p_max - v < on_power]
    sp = np.full(n, np.nan)
    sp[36] = 1.0
    sp[40:44] = 0.0
    sp[full] = 1.0
    out["space_pinned"] = mp._solve(bundle, space_pins=sp)
    dp = np.full(n, np.nan)
    dp[20] = 1.0
    dp[60:64] = 0.0
    out["dhw_pinned"] = mp._solve(bundle, dhw_pins=dp)
    cap = np.full(n, 100.0)
    cap[36] = 0.05
    sp2 = np.full(n, np.nan)
    sp2[36] = 1.0
    out["capped_pinned"] = mp._solve(bundle, space_pins=sp2, power_caps_extra=cap)
    return out, full, p_max


def run_arms(mp, patch_to=None):
    """production_solves with ``opt.<name>`` replaced by ``fn`` for ``patch_to=(name, fn)``."""
    if patch_to is None:
        return production_solves(mp)
    with mock.patch.object(opt, patch_to[0], patch_to[1]):
        return production_solves(mp)


def same(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return a.shape == b.shape and bool(np.all((a == b) | (np.isnan(a) & np.isnan(b))))

OLD = '    violated = (x < lb) | (x > ub)'
NEW = '    violated = (x <= lb) | (x > ub)'

# ---- _fd_steps: an exhaustive boundary search plus a production reach count ----
F = "_fd_steps"
base = opt._fd_steps
mut = mutant(F, OLD, NEW)


def steps_differ(r1, r2):
    """Two _fd_steps results differ where the gradient reads them: the free mask, or a
    step of a free variable (a fixed variable's step is never read, D9-01)."""
    (h1, f1), (h2, f2) = r1, r2
    if not same(f1, f2):
        return True
    return not same(np.asarray(h1)[f1], np.asarray(h2)[f2])


def _near(v, k=2):
    """v and its k float neighbours on each side."""
    out = [v]
    a = b = v
    for _ in range(k):
        a, b = np.nextafter(a, -np.inf), np.nextafter(b, np.inf)
        out += [float(a), float(b)]
    return out


def candidates():
    xs = [0.0, -0.0, 0.5, -0.5, 1.0, -1.0, 3.7, 1e-12, -1e-12, 1e8, -1e8, 1e9, -1e9, 1e17, -1e17]
    es = [opt._LBFGSB_FD_EPS, 1e-8, 0.0, 1.4901161193847656e-08, 1e-3]
    s = np.finfo(np.float64).eps ** 0.5
    for x0 in xs:
        for eps in es:
            steps = {eps, -eps, s, -s, s * max(1.0, abs(x0)), -s * max(1.0, abs(x0)), 2 * eps, eps / 2}
            pts = set()
            for st in steps:
                for v in _near(x0 + st, 2):
                    pts.add(v)
                # bound distances exactly equal to the step, where float arithmetic allows it
                for v in _near(x0 + st, 6):
                    if v - x0 == abs(st) or x0 - v == abs(st):
                        pts.add(v)
            for v in _near(x0, 1):
                pts.add(v)
            pts |= {-np.inf, np.inf, 0.0, x0 - 1.0, x0 + 1.0}
            # boxes centred on x0, narrower than the step
            for w in (abs(eps) / 4 or 1e-12, 1e-9, 1e-12):
                yield x0, eps, x0 - w, x0 + w
            pts = sorted(pts)
            for lb in pts:
                for ub in pts:
                    if lb <= ub:
                        yield x0, eps, lb, ub


tried = moved = dom_tried = dom_moved = 0
example = dom_example = None
PEPS = opt._LBFGSB_FD_EPS
for x0, eps, lb, ub in candidates():
    tried += 1
    a = np.array([x0])
    hb, fb = base(a, eps, [(lb, ub)])
    hm, fm = mut(a, eps, [(lb, ub)])
    differ = steps_differ((hb, fb), (hm, fm))
    # the production domain: L-BFGS-B's own eps, x0 inside its bounds, all of them a
    # power in kW (0 <= lb <= x0 <= ub <= 100; L-BFGS-B projects every iterate into the box)
    dom = eps == PEPS and 0.0 <= lb <= x0 <= ub <= 100.0
    dom_tried += dom
    if differ:
        moved += 1
        if example is None:
            example = (x0, eps, lb, ub, float(hb[0]), float(hm[0]))
        if dom:
            dom_moved += 1
            if dom_example is None:
                dom_example = (x0, eps, lb, ub, float(hb[0]), float(hm[0]))
rng = np.random.default_rng(11)
rtried = rmoved = 0
for _ in range(20000):
    x0 = float(rng.uniform(-5, 5))
    w = float(10 ** rng.uniform(-12, 1))
    lb = x0 - w * float(rng.uniform(-0.2, 1.2))
    ub = x0 + w * float(rng.uniform(-0.2, 1.2))
    if lb > ub:
        continue
    eps = float(rng.choice([PEPS, 1e-8, 0.0]))
    rtried += 1
    a = np.array([x0])
    if steps_differ(base(a, eps, [(lb, ub)]), mut(a, eps, [(lb, ub)])):
        rmoved += 1

# production reach: every _fd_steps call of the production solves, both arms on the same input,
# then the gradient each arm's steps produce, then the whole plan under the mutant
calls = diff_calls = 0


def _rec(x0, eps, bounds):
    global calls, diff_calls
    calls += 1
    rb = base(x0, eps, bounds)
    if steps_differ(rb, mut(x0, eps, bounds)):
        diff_calls += 1
    return rb


grad_calls = grad_moved = 0
_bfd = opt._batch_fd_gradient


def _grad(*a, **k):
    global grad_calls, grad_moved
    grad_calls += 1
    g0 = _bfd(*a, **k)
    with mock.patch.object(opt, F, mut):
        g1 = _bfd(*a, **k)
    if not same(g0, g1):
        grad_moved += 1
    return g0


mp = load_mp()
run_arms(mp, (F, _rec))
with mock.patch.object(opt, "_batch_fd_gradient", _grad):
    production_solves(mp)
plans_b = production_solves(mp)[0]
plans_m = run_arms(mp, (F, mut))[0]
plan_delta = max(float(np.max(np.abs(np.asarray(plans_b[k].power_schedule) - np.asarray(plans_m[k].power_schedule))))
                 for k in plans_b)

if dom_example is not None:
    example = dom_example
if example is not None:
    x0, eps, lb, ub, hb0, hm0 = example
    result("example_input", f"x0={float(x0)!r},eps={float(eps)!r},lb={float(lb)!r},ub={float(ub)!r}")
    result("h_baseline", repr(hb0))
    result("h_mutant", repr(hm0))
result("crafted_inputs_tried", tried, "count")
result("crafted_inputs_moved", moved, "count")
result("domain_inputs_tried", dom_tried, "count")
result("domain_inputs_moved", dom_moved, "count")
result("random_inputs_tried", rtried, "count")
result("random_inputs_moved", rmoved, "count")
result("production_fd_calls", calls, "count")
result("production_fd_calls_moved", diff_calls, "count")
result("production_gradients", grad_calls, "count")
result("production_gradients_moved", grad_moved, "count")
result("production_plan_max_abs_delta_kw", f"{plan_delta:.6g}", "kW")

# null arm: the same function re-compiled with the line unchanged moves nothing, on the grid or the plans
nul = mutant(F, OLD, OLD)
null_moved = 0
for i, (x0, eps, lb, ub) in enumerate(candidates()):
    a = np.array([x0])
    null_moved += steps_differ(base(a, eps, [(lb, ub)]), nul(a, eps, [(lb, ub)]))
plans_n = run_arms(mp, (F, nul))[0]
null_plan = max(float(np.max(np.abs(np.asarray(plans_b[k].power_schedule) - np.asarray(plans_n[k].power_schedule))))
                for k in plans_b)
result("null_inputs_moved", null_moved, "count")
result("null_plan_max_abs_delta_kw", f"{null_plan:.6g}", "kW")

tail()
