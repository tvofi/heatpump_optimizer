"""catchup/d9 cont_fuse: what the two-zone continuation's unfused jac costs, in horizons and CPU, with null arms.

Metric: per HeatPumpOptimizer.optimize call (entry: tests/golden.py:make, not
golden.capture), (a) horizon-equivalents = rows of
ThermalModel.simulate_trajectory_batch + scalar simulate_step calls / n_steps,
(b) thread CPU spent inside the scalar simulate_step seam, (c) solve thread
CPU. Arm "prod" = shipped code; arm "fused" = _scoped_minimize calls given a
callable jac (only _optimize_space_only.move_starts) rewritten to the
production _fused_value_and_gradient(objective_batch, bounds, 1e-4) with
jac=True. Arms interleaved per rep. Null arms: scenarios with no continuation
(winter_single_no_dhw, winter_two_zone_dhw) -- the rewrite must find nothing
to rewrite and every count must be identical. Iterate-path oracle: the
shipped schedule (result.optimal_power or equivalent) is compared bitwise
between arms.
Command (repo root): PYTHONPATH=tests/hastub python dev/audit/rounds/round10/catchup/d9/cont_fuse.py [--reps 3]
Expected: two-zone no-DHW: fused removes 2 scalar horizons per continuation
gradient (88 horizons on 44 gradients), CPU falls; nulls: delta 0, CPU ratio ~1.
Baseline: origin/main d749c986d (production byte-identical to 17f1c55fad1b).
Machine: Darwin arm64 Apple M-series 8-core, shared seat box; seat venv python 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, argparse, hashlib
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
import numpy as np
import golden
from profiles import solve_inputs
from heatpump_optimizer import optimizer as O
from heatpump_optimizer import thermal_model as T

ap = argparse.ArgumentParser()
ap.add_argument("--reps", type=int, default=3)
ap.add_argument("--scenarios", default="winter_two_zone_no_dhw,winter_single_no_dhw,winter_two_zone_dhw")
a = ap.parse_args()

st = {"rows": 0, "steps": 0, "step_cpu": 0.0, "rewrites": 0}
_ss = T.ThermalModel.simulate_step
def ss(self, *x, **k):
    st["steps"] += 1
    t = time.thread_time()
    try:
        return _ss(self, *x, **k)
    finally:
        st["step_cpu"] += time.thread_time() - t
T.ThermalModel.simulate_step = ss
_stb = T.ThermalModel.simulate_trajectory_batch
def stb(self, *x, **k):
    pm = k["power_matrix"] if "power_matrix" in k else x[1]
    st["rows"] += int(np.asarray(pm).shape[0])
    return _stb(self, *x, **k)
T.ThermalModel.simulate_trajectory_batch = stb

ARM = ["prod"]
_sm = O._scoped_minimize
def sm(fun, x0, *x, **k):
    jac = k.get("jac")
    if ARM[0] == "fused" and callable(jac) and jac is not True:
        cl = {n: c.cell_contents for n, c in zip(jac.__code__.co_freevars, jac.__closure__ or ())}
        k["jac"] = True
        st["rewrites"] += 1
        return _sm(O._fused_value_and_gradient(cl["objective_batch"], cl["bounds"], 1e-4), x0, *x, **k)
    return _sm(fun, x0, *x, **k)
O._scoped_minimize = sm

def run(name):
    b = golden.make(**golden.SCENARIOS[name])
    n = len(b["prices"])
    for kk in st: st[kk] = 0 if kk != "step_cpu" else 0.0
    t = time.thread_time()
    r = b["optimizer"].optimize(inputs=solve_inputs(
        initial_state=b["state"], prices=b["prices"], outdoor_temps=b["outdoor"],
        wind_speeds=b["wind"], precipitation=b["rain"], solar_radiation=b["solar"],
        start_time=golden.START))
    cpu = time.thread_time() - t
    plan = getattr(r, "optimal_power", None)
    if plan is None:
        plan = getattr(r, "power_schedule", None)
    h = hashlib.sha1(np.asarray(plan, dtype=float).tobytes()).hexdigest()[:12] if plan is not None else repr(r)[:40]
    return dict(hor=st["rows"] + st["steps"] / n, steps=st["steps"], rows=st["rows"],
                step_cpu=st["step_cpu"], cpu=cpu, plan=h, rew=st["rewrites"])

med = lambda xs: sorted(xs)[len(xs) // 2]
t0p, t0t = time.process_time(), time.thread_time()
for name in a.scenarios.split(","):
    res = {"prod": [], "fused": []}
    for _ in range(a.reps):
        for arm in ("prod", "fused"):
            ARM[0] = arm; res[arm].append(run(name))
    p, f = res["prod"][0], res["fused"][0]
    print(f"RESULT {name}.horizons prod={p['hor']:.1f} fused={f['hor']:.1f} delta={p['hor']-f['hor']:.1f} horizons (exact)")
    print(f"RESULT {name}.scalar_steps prod={p['steps']} fused={f['steps']} rows prod={p['rows']} fused={f['rows']} count")
    print(f"RESULT {name}.rewrites fused={f['rew']} count")
    print(f"RESULT {name}.plan_identical={p['plan']==f['plan']} ({p['plan']} vs {f['plan']})")
    pc_, fc_ = med([x['cpu'] for x in res['prod']]), med([x['cpu'] for x in res['fused']])
    print(f"RESULT {name}.solve_cpu_ms prod={pc_*1e3:.0f} fused={fc_*1e3:.0f} ratio_prod_over_fused={pc_/fc_:.3f} (provisional)")
    print(f"RESULT {name}.scalar_step_cpu_ms prod={med([x['step_cpu'] for x in res['prod']])*1e3:.0f} fused={med([x['step_cpu'] for x in res['fused']])*1e3:.0f} (provisional)")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc/tc:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
import resource
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
