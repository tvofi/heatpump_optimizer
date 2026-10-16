"""D9-s1 sse_per_gradient: simulate-step-equivalents per gradient evaluation.

Metric: (scalar ThermalModel.simulate_step calls + rows of
ThermalModel.simulate_trajectory_batch) per gradient evaluation, split by
phase: "main" = gradients inside optimizer._multi_start_minimize served by
_batch_fd_gradient with f0=None (the fused value+gradient), "cont" = the
two-zone continuation's jac (_batch_fd_gradient called with a float f0, from
_optimize_space_only.move_starts), "scipy" = scipy approx_derivative (scalar
FD path). Key: SSE counted at the production seams simulate_step /
simulate_trajectory_batch (rows), attributed to the innermost open gradient
or, between gradients, to the enclosing phase's "fun" bucket.
Command: PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python dev/audit/rounds/round10/D9/s1/sse_grad.py [--perturb fuse|nocont]
Expected (17f1c55fad1b, Darwin arm64 M-series): main sse/grad = 97 + n/a scalar;
cont sse/grad = 96 batch + 2x96 scalar steps = 288 (+-0, counts are exact).
Grid: --scenarios tz:<price>:<weather>,... builds a two-zone no-DHW day.
Perturbation: --perturb fuse replaces the continuation's jac by the fused
value_and_gradient (jac=True), expected to drop cont sse/grad 288 -> 97.
--perturb maxiter halves maxiter via _multi_start_minimize wrapper (main
gradients count drops, ratio unchanged: the ratio is per gradient).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, argparse
sys.path.insert(0, "tests")
sys.path.insert(0, ".")
import numpy as np
import golden
from heatpump_optimizer import optimizer as O
from heatpump_optimizer import thermal_model as T
from scipy.optimize import _numdiff

ap = argparse.ArgumentParser()
ap.add_argument("--perturb", default="none")
ap.add_argument("--scenarios", default="winter_two_zone_dhw,winter_single_dhw,winter_two_zone_no_dhw,winter_single_no_dhw,fuse_guard,shoulder_two_zone")
a = ap.parse_args()

stack = []          # open gradient phases
cnt = {}
def bump(phase, key, n):
    d = cnt.setdefault(phase, {"grad": 0, "scalar": 0, "rows": 0})
    d[key] += n
cur_scen = [""]
in_msm = [0]
def phase_outside():
    return "msm_fun" if in_msm[0] else "other"

_ss = T.ThermalModel.simulate_step
def ss(self, *aa, **kk):
    bump(stack[-1] if stack else phase_outside(), "scalar", 1)
    return _ss(self, *aa, **kk)
T.ThermalModel.simulate_step = ss
_stb = T.ThermalModel.simulate_trajectory_batch
def stb(self, initial_state, power_matrix, *aa, **kk):
    bump(stack[-1] if stack else phase_outside(), "rows", int(np.asarray(power_matrix).shape[0]))
    return _stb(self, initial_state, power_matrix, *aa, **kk)
T.ThermalModel.simulate_trajectory_batch = stb

_bfd = O._batch_fd_gradient
def bfd(batch_objective, args, x0, f0, eps, bounds):
    ph = "main" if f0 is None else "cont"
    bump(ph, "grad", 1)
    return _bfd(batch_objective, args, x0, f0, eps, bounds)
O._batch_fd_gradient = bfd

# The continuation's jac lambda evaluates float(objective(x)) BEFORE calling
# _batch_fd_gradient; attribute that scalar to "cont" by wrapping the jac
# passed to _scoped_minimize when it is a plain callable.
_sm = O._scoped_minimize
def sm(fun, x0, *aa, **kk):
    jac = kk.get("jac")
    if callable(jac):
        _t = time.thread_time()
        try:
            return _sm_cont(fun, x0, jac, aa, kk)
        finally:
            cpu["cont"] += time.thread_time() - _t
    return _sm(fun, x0, *aa, **kk)
cpu = {"cont": 0.0}
def _sm_cont(fun, x0, jac, aa, kk):
    if True:
        if a.perturb == "fuse":
            bounds = kk["bounds"]
            # perturbation: fused value+gradient, as the main loop does
            inner = jac
            def fused(x, *b):
                stack.append("cont")
                try:
                    vals = []
                    g = _bfd(lambda rows, *c: _cap(rows, vals), (), x, None, 1e-4, bounds)
                    bump("cont", "grad", 1)
                    return vals[-1], g
                finally:
                    stack.pop()
            # need the batch objective: recover it from the lambda's closure
            ob = [c.cell_contents for c in (inner.__closure__ or ()) if callable(getattr(c, "cell_contents", None)) and getattr(c.cell_contents, "__name__", "") != "objective"]
            batch = [f for f in ob if "batch" in getattr(f, "__name__", "")]
            if batch:
                global _cap
                def _cap(rows, vals, _b=batch[0]):
                    out = _b(rows); vals.append(float(out[0])); return out
                kk["jac"] = True
                return _sm(fused, x0, *aa, **kk)
        def wrapped(x, *b):
            stack.append("cont")
            try:
                return jac(x, *b)
            finally:
                stack.pop()
        kk["jac"] = wrapped
        def wfun(x, *b):
            stack.append("cont_fun")
            try:
                return fun(x, *b)
            finally:
                stack.pop()
        return _sm(wfun, x0, *aa, **kk)
O._scoped_minimize = sm

_msm = O._multi_start_minimize
def msm(*aa, **kk):
    in_msm[0] += 1
    try:
        return _msm(*aa, **kk)
    finally:
        in_msm[0] -= 1
O._multi_start_minimize = msm

_ad = _numdiff.approx_derivative
def ad(*aa, **kk):
    stack.append("scipy"); bump("scipy", "grad", 1)
    try:
        return _ad(*aa, **kk)
    finally:
        stack.pop()
_numdiff.approx_derivative = ad
import scipy.optimize._differentiable_functions as _df
_df.approx_derivative = ad

# rows inside main gradients: _batch_fd_gradient runs the batch under no
# stack entry; push "main" around it.
_bfd2 = O._batch_fd_gradient
def bfd2(batch_objective, args, x0, f0, eps, bounds):
    stack.append("main" if f0 is None else "cont")
    try:
        return _bfd2(batch_objective, args, x0, f0, eps, bounds)
    finally:
        stack.pop()
O._batch_fd_gradient = bfd2

t0p, t0t = time.process_time(), time.thread_time()
for name in a.scenarios.split(","):
    cnt.clear(); cpu["cont"] = 0.0
    _t = time.thread_time()
    if name.startswith("tz:"):
        _, pp, wp = name.split(":")
        spec = dict(two_zone=True, dhw=False, price_profile=pp, weather_profile=wp)
    else:
        spec = golden.SCENARIOS[name]
    golden.capture(name, spec)
    _solve = time.thread_time() - _t
    if cpu["cont"]:
        print(f"RESULT {name}.cont_cpu_share={cpu['cont']/_solve:.4f} ratio (provisional)")
        print(f"RESULT {name}.cont_cpu_ms={cpu['cont']*1e3:.1f} ms (provisional)")
        print(f"RESULT {name}.capture_cpu_ms={_solve*1e3:.1f} ms (provisional)")
    for ph in ("main", "cont", "scipy"):
        d = cnt.get(ph)
        if d and d["grad"]:
            print(f"RESULT {name}.{ph}.grads={d['grad']} count")
            print(f"RESULT {name}.{ph}.sse_per_grad={(d['scalar']+d['rows'])/d['grad']:.2f} sse")
            print(f"RESULT {name}.{ph}.scalar_per_grad={d['scalar']/d['grad']:.2f} steps")
    for ph in ("msm_fun", "cont_fun", "other"):
        d = cnt.get(ph)
        if d:
            print(f"RESULT {name}.{ph}.sse={d['scalar']+d['rows']} sse")
    tot = sum(d["scalar"] + d["rows"] for d in cnt.values())
    c = cnt.get("cont", {"scalar": 0}); cf = cnt.get("cont_fun", {"scalar": 0, "rows": 0})
    print(f"RESULT {name}.total_sse={tot} sse")
    print(f"RESULT {name}.cont_scalar_share={(c['scalar']+cf['scalar']+cf['rows'])/max(tot,1):.4f} ratio")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc/tc:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
import resource
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
