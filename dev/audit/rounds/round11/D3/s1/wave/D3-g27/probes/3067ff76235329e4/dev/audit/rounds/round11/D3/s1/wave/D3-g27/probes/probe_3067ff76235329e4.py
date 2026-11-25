#!/usr/bin/env python3
# Metric: which plan optimizer._lbfgsb_restart keeps (the start 'best' or the 'polished' one) over a (prior, score) grid built around the keep threshold and its finite subset, with only the polish run (_lbfgsb_run) faked; plus every keep decision of four production solves, recorded at the decision line.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g27/probes/probe_3067ff76235329e4.py
#   (from the repository root; $HOME/venv-ci on this box is /opt/hpo/venv-ci)
# EXPECTED RESULT example_input=prior=0.0,score=-2e-17
# EXPECTED RESULT kept_baseline=best
# EXPECTED RESULT kept_mutant=polished
# EXPECTED RESULT grid_inputs_tried=269 count
# EXPECTED RESULT grid_inputs_moved=3 count
# EXPECTED RESULT domain_inputs_tried=245 count
# EXPECTED RESULT domain_inputs_moved=3 count
# EXPECTED RESULT production_decisions=16 count
# EXPECTED RESULT production_decisions_moved=0 count
# EXPECTED RESULT production_prior_exactly_zero=0 count
# EXPECTED RESULT production_min_abs_gap_to_threshold=0.00127121
# EXPECTED RESULT null_inputs_moved=0 count
#   (counts are exact and deterministic, the random grid seeded; kW and objective deltas are solver floats, re-taken to 1e-3 relative on another BLAS build; thread_factor, load1, swapins quoted, not expected)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g27 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux, venv-ci CPython 3.14).
# Instrumented symbol: heatpump_optimizer.optimizer:_lbfgsb_restart, custom_components/heatpump_optimizer/optimizer.py:1871 `if np.isfinite(score) and (prior - score) > _LBFGSB_RESTART_KEEP_REL * scale:`.
# Perturbation: key 3067ff76235329e4 (CMP_BOUND), `if np.isfinite(score) and (prior - score) > _LBFGSB_RESTART_KEEP_REL * scale:` -> `if np.isfinite(score) and (prior - score) >= _LBFGSB_RESTART_KEEP_REL * scale:`, applied in memory: the function is
#   re-compiled from its own source with the one line replaced, in a copy of the module namespace; the production solves
#   see it through mock.patch.object on the module the suite imports (heatpump_optimizer.optimizer). Direction: moved inputs rise from 0 under the mutant.
# Null control: the same function re-compiled with the line unchanged (the null_* RESULT lines), expected 0 moved.
# Count key: the object _lbfgsb_restart returns (by identity), never an input attribute.
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

OLD = '    if np.isfinite(score) and (prior - score) > _LBFGSB_RESTART_KEEP_REL * scale:'
NEW = '    if np.isfinite(score) and (prior - score) >= _LBFGSB_RESTART_KEEP_REL * scale:'

# ---- _lbfgsb_restart: the keep decision over a (prior, score) grid, plus every production decision ----
from types import SimpleNamespace  # noqa: E402
F = "_lbfgsb_restart"
base = opt._lbfgsb_restart
mut = mutant(F, OLD, NEW)
KEEP = opt._LBFGSB_RESTART_KEEP_REL


def decide(fn, prior, score):
    """What ``fn`` returns when the polish from a start valued ``prior`` lands at ``score``:
    'polished' or 'best'. Only the polish run itself (_lbfgsb_run) is faked."""
    best = SimpleNamespace(x=np.array([0.0]))
    polished = SimpleNamespace(x=np.array([1.0]))

    def objective(x, *_a):
        return prior if float(x[0]) == 0.0 else score

    with mock.patch.dict(fn.__globals__, {"_lbfgsb_run": lambda *a, **k: polished}):
        out = fn(best, objective, [(0.0, 1.0)], (), 10, None, None)
    return "polished" if out is polished else "best"


def _near(v, k=3):
    out = [v]
    a = b = v
    for _ in range(k):
        a, b = np.nextafter(a, -np.inf), np.nextafter(b, np.inf)
        out += [float(a), float(b)]
    return out


PRIORS = [0.0, -0.0, 1e-13, 1e-12, 1.0, 69.47964532244127, -5.0, 1e5]
tried = moved = dom_tried = dom_moved = 0
example = dom_example = None
for p in PRIORS:
    t = KEEP * max(abs(p), 1e-12)
    scores = set()
    for c in (p - t, p - KEEP * abs(p), p, p - 1e-17, p - 1e-30, p - 0.5 * t, p - 2 * t):
        scores.update(_near(c))
    scores |= {float("nan"), float("inf"), float("-inf")}
    for s in sorted(scores, key=lambda v: (v != v, v)):
        tried += 1
        dom = math.isfinite(p) and math.isfinite(s)
        dom_tried += dom
        db, dm = decide(base, p, s), decide(mut, p, s)
        if db != dm:
            moved += 1
            ex = (p, s, db, dm)
            example = example or ex
            if dom:
                dom_moved += 1
                dom_example = dom_example or ex

# production reach: every keep decision of the production solves, recorded at the decision line
REC = []
probe_src = textwrap.dedent(inspect.getsource(opt._lbfgsb_restart))
anchor = "if np.isfinite(score) and (prior - score)"
assert probe_src.count(anchor) == 1
probe_src = probe_src.replace(anchor, "if _REC.append((prior, score)) is None and np.isfinite(score) and (prior - score)")
ns = dict(opt.__dict__)
ns["_REC"] = REC
exec(compile(probe_src, opt.__file__, "exec"), ns)
mp = load_mp()
run_arms(mp, (F, ns[F]))
prod_moved = sum(decide(base, p, s) != decide(mut, p, s) for p, s in REC)
min_gap = min((abs((p - s) - KEEP * max(abs(p), 1e-12)) for p, s in REC if math.isfinite(s)), default=float("nan"))
zero_priors = sum(1 for p, _s in REC if p == 0.0)

if dom_example is not None:
    example = dom_example
if example is not None:
    p, s, db, dm = example
    result("example_input", f"prior={p!r},score={s!r}")
    result("kept_baseline", db)
    result("kept_mutant", dm)
result("grid_inputs_tried", tried, "count")
result("grid_inputs_moved", moved, "count")
result("domain_inputs_tried", dom_tried, "count")
result("domain_inputs_moved", dom_moved, "count")
result("production_decisions", len(REC), "count")
result("production_decisions_moved", prod_moved, "count")
result("production_prior_exactly_zero", zero_priors, "count")
result("production_min_abs_gap_to_threshold", f"{min_gap:.6g}")

# null arm: the same function re-compiled with the line unchanged moves nothing on the grid or the records
nul = mutant(F, OLD, OLD)
null_moved = 0
for p in PRIORS:
    t = KEEP * max(abs(p), 1e-12)
    for c in (p - t, p - KEEP * abs(p), p, p - 1e-17):
        for s in _near(c):
            null_moved += decide(base, p, s) != decide(nul, p, s)
null_moved += sum(decide(base, p, s) != decide(nul, p, s) for p, s in REC)
result("null_inputs_moved", null_moved, "count")

tail()
