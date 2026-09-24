"""D7-s1 objective/terminal-cost statefulness (the former last_buffer_trajectory seam).

Metrics:
  order_mismatch: count of captured space objectives f (optimizer:_scoped_minimize's `fun`, the
    production objective closure incl. its terminal cost) whose value at plan A changes when
    another plan B, or a whole second optimize() on the SAME optimizer with a different initial
    buffer temperature, is evaluated in between. 0 = the objective is a pure function of its input.
  scratch_attrs: instance attributes of the model/optimizer that one objective evaluation writes.
  side_series: model/optimizer attributes holding a horizon-length series after optimize()
    (what last_buffer_trajectory was).
Scenario: tests/golden.py SCENARIOS["valve_storage"] (buffer is a store, so the tank enters the
  terminal cost).
Command:  PYTHONPATH=tests/hastub python3 tools/audit/round8/D7/s1_statefulness.py [--perturb]
  --perturb: re-introduce the side channel -- wrap ThermalModel.simulate_trajectory so it stores its
  buffer series on the model and wrap HeatPumpOptimizer._terminal_cost so its closure reads that
  stored series instead of its argument (the pre-R3 shape); order_mismatch must go up. Restored in finally.
Expected: order_mismatch=0, side_series=0 (exact).
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud container (counts only).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, logging
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, "tests/hastub")
logging.disable(logging.CRITICAL)
_p0, _t0 = time.process_time(), time.thread_time()
import numpy as np
from golden import make, SCENARIOS, START
from heatpump_optimizer import optimizer as O
from heatpump_optimizer.thermal_model import ThermalModel

PERTURB = "--perturb" in sys.argv
captured = []
_orig_min = O._scoped_minimize
_orig_traj = ThermalModel.simulate_trajectory
_orig_tc = O.HeatPumpOptimizer._terminal_cost


def _cap_min(*a, **k):
    fun = a[0] if a else k.get("fun")
    x0 = a[1] if len(a) > 1 else k.get("x0")
    captured.append((fun, np.array(x0, dtype=float), a[2:] if len(a) > 2 else k.get("args", ())))
    return _orig_min(*a, **k)


def _side_traj(self, *a, **k):
    out = _orig_traj(self, *a, **k)
    self.last_buffer_trajectory = np.array(out[4])
    return out


def _side_tc(self, *a, **k):
    cost, batch = _orig_tc(self, *a, **k)
    model = self.model

    def cost2(room, slab, upper, lower, buffer_temps=None):
        stored = getattr(model, "last_buffer_trajectory", None)
        return cost(room, slab, upper, lower, stored if stored is not None else buffer_temps)
    return cost2, batch


def snapshot(obj):
    out = {}
    for k, v in vars(obj).items():
        try:
            out[k] = np.array(v, copy=True) if isinstance(v, np.ndarray) else (v if isinstance(v, (int, float, str, bool, type(None))) else id(v))
        except Exception:
            out[k] = id(v)
    return out


def diff(a, b):
    ch = []
    for k in set(a) | set(b):
        va, vb = a.get(k, "<absent>"), b.get(k, "<absent>")
        if isinstance(va, np.ndarray) or isinstance(vb, np.ndarray):
            if not (isinstance(va, np.ndarray) and isinstance(vb, np.ndarray) and va.shape == vb.shape and np.array_equal(va, vb)):
                ch.append(k)
        elif va != vb:
            ch.append(k)
    return sorted(ch)


try:
    O._scoped_minimize = _cap_min
    if PERTURB:
        ThermalModel.simulate_trajectory = _side_traj
        O.HeatPumpOptimizer._terminal_cost = _side_tc
    tcs = []
    _inner_tc = O.HeatPumpOptimizer._terminal_cost

    def _cap_tc(self, *a, **k):
        cost, batch = _inner_tc(self, *a, **k)
        tcs.append(cost)
        return cost, batch
    O.HeatPumpOptimizer._terminal_cost = _cap_tc
    b = make(**SCENARIOS["valve_storage"])
    opt = b["optimizer"]
    args = (b["state"], b["prices"], b["outdoor"], b["wind"], b["rain"], b["solar"], START)
    opt.optimize(*args)
    n_steps = len(b["prices"])
    side = [k for o in (opt, opt.model) for k, v in vars(o).items()
            if isinstance(v, (np.ndarray, list)) and len(v) in (n_steps, n_steps + 1)
            and not k.startswith("_price_known") and not k.startswith("_pv_surplus")]
    print(f"side-series attributes after optimize: {side}")
    rng = np.random.default_rng(7)
    mism = 0
    scratch = set()
    funs = [c for c in captured if callable(c[0])]
    for fun, x0, fargs in funs:
        xa = np.clip(x0, 0, None)
        xb = np.clip(x0 + rng.uniform(0.2, 1.5, size=x0.shape), 0, None)
        s0m, s0o = snapshot(opt.model), snapshot(opt)
        fa1 = float(fun(xa, *fargs) if fargs else fun(xa))
        scratch |= {f"model.{k}" for k in diff(s0m, snapshot(opt.model))}
        scratch |= {f"opt.{k}" for k in diff(s0o, snapshot(opt))}
        fun(xb, *fargs) if fargs else fun(xb)
        fa2 = float(fun(xa, *fargs) if fargs else fun(xa))
        mism += int(fa1 != fa2)
    # a whole second solve on the SAME optimizer, different initial tank, between two evaluations
    fun, x0, fargs = funs[-1]
    xa = np.clip(x0, 0, None)
    fa1 = float(fun(xa, *fargs) if fargs else fun(xa))
    st2 = b["state"].__class__(**{**vars(b["state"]), "buffer_tank_temperature": 60.0})
    opt.optimize(st2, *args[1:])
    fa2 = float(fun(xa, *fargs) if fargs else fun(xa))
    second = int(fa1 != fa2)
    # the terminal cost itself, evaluated on plan A's trajectory with plan B simulated in between
    m = opt.model
    n = len(b["prices"])
    sim_args = (b["outdoor"], b["wind"], b["rain"], b["solar"])
    def traj(power):
        return m.simulate_trajectory(b["state"], power, *sim_args, dt_hours=0.25)
    tr_a = traj(np.full(n, 1.0))
    tc_mism = 0
    for tc in tcs:
        v1 = float(tc(*tr_a[:5]))
        traj(np.full(n, 4.0))
        v2 = float(tc(*tr_a[:5]))
        tc_mism += int(v1 != v2)
    print(f"RESULT tc_order_mismatch={tc_mism} count (of {len(tcs)} terminal closures)")
    print(f"objective evaluations checked: {len(funs)}; first-closure delta after second solve: {fa2 - fa1:.6g}")
    print(f"attributes written by one objective evaluation: {sorted(scratch)}")
    print(f"RESULT order_mismatch={mism + second} count (of {len(funs) + 1} checks)")
    print(f"RESULT scratch_attrs={len(scratch)} count")
    print(f"RESULT side_series={len(side)} count")
finally:
    O._scoped_minimize = _orig_min
    ThermalModel.simulate_trajectory = _orig_traj
    O.HeatPumpOptimizer._terminal_cost = _orig_tc
tf = (time.process_time() - _p0) / max(time.thread_time() - _t0, 1e-9)
print(f"RESULT thread_factor={tf:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
