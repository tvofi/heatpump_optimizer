"""D2-s2 / D2.M3 -- every currency term of the objective scales with price_weight.

Metric (one line): homog_err = max over scenarios and K random schedules x of
  |J_w(x) - w * J_1(x)| / |w * J_1(x)|, J_w = the solver's own objective closure built with
  OptimizationConfig.price_weight = w (w = 2.5) and comfort_weight = 0 (so the only terms left
  are currency: energy, cycling, capacity, terminal) -- must be 0 to float rounding (1e-12).
  Also comfort_invariance: with comfort_weight at default, J_w(x) - w*J_1(x) must equal
  (1 - w) * comfort terms, i.e. comfort terms must NOT scale; reported as the ratio.
  count key: the float the captured objective closure returns (production seam).
Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D2/s2/price_weight_scaling.py [--perturb]
Expect (baseline 1936d5ca, box B5): homog_err <= 1e-12.
Perturbation (--perturb): HeatPumpOptimizer._terminal_cost's refill_price loses its
  price_weight factor (in memory: config.price_weight forced to 1.0 while _terminal_cost runs)
  -> homog_err rises (direction: up).
Instrumented: optimizer:_multi_start_minimize (objective capture), optimizer:HeatPumpOptimizer._terminal_cost
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import copy
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
import golden  # noqa: E402
from heatpump_optimizer import optimizer as optmod  # noqa: E402

W = 2.5
K = 5
SCEN = ["winter_single_no_dhw", "winter_two_zone_no_dhw", "winter_single_dhw", "shoulder",
        "valve_storage", "capacity_tariff", "cycling_cost", "tariff_plus_two_zone",
        "everything_on", "negative_prices"]
_orig_msm = optmod._multi_start_minimize
cap = {}


def msm(objective, candidates, bounds, args=(), maxiter=300, batch_objective=None, fd_eps=1e-4):
    if "obj" not in cap:
        cap.update(obj=objective, bounds=list(bounds), args=args)
    raise RuntimeError("captured")  # the solve itself is not needed


optmod._multi_start_minimize = msm
if "--perturb" in sys.argv:
    _orig_tc = optmod.HeatPumpOptimizer._terminal_cost

    def tc(self, *a, **k):
        saved = self.config.price_weight
        self.config.price_weight = 1.0
        try:
            return _orig_tc(self, *a, **k)
        finally:
            self.config.price_weight = saved
    optmod.HeatPumpOptimizer._terminal_cost = tc


def objective_for(name, pw, cw):
    spec = copy.deepcopy(golden.SCENARIOS[name])
    oo = dict(spec.get("opt_overrides") or {})
    oo["price_weight"] = pw
    if cw is not None:
        oo["comfort_weight"] = cw
    spec["opt_overrides"] = oo
    cap.clear()
    try:
        golden.capture(name, spec)
    except Exception:
        pass
    return cap["obj"], cap["bounds"], cap["args"]


t0 = time.process_time(); tt0 = time.thread_time()
rng = np.random.default_rng(9)
worst = 0.0; per = []; comfort_ratio = []
for name in SCEN:
    o1, bounds, args = objective_for(name, 1.0, 0.0)
    ow, _, _ = objective_for(name, W, 0.0)
    lb = np.array([b[0] for b in bounds]); ub = np.array([b[1] for b in bounds])
    e_cell = 0.0
    xs = [lb + (ub - lb) * rng.uniform(0, 1, lb.size) for _ in range(K)]
    for x in xs:
        j1 = float(o1(x, *args)); jw = float(ow(x, *args))
        e_cell = max(e_cell, abs(jw - W * j1) / max(abs(W * j1), 1e-12))
    per.append((name, e_cell)); worst = max(worst, e_cell)
    print(f"# {name:24s} homog_err={e_cell:.3e}")
cpu = time.process_time() - t0; tcpu = time.thread_time() - tt0
vals = sorted(e for _, e in per)
print(f"RESULT cells={len(per)} count")
print(f"RESULT homog_err={worst:.3e} ratio")
print(f"RESULT homog_err_drop_worst={vals[-2]:.3e} ratio")
print(f"RESULT homog_err_min_cell={vals[0]:.3e} ratio")
print(f"RESULT thread_factor={cpu / max(tcpu, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
