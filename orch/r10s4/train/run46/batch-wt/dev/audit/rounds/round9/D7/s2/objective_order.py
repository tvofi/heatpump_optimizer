"""D7.M4 -- does the objective's terminal cost depend on call order?

The historical ``last_buffer_trajectory`` stash is gone at this baseline:
optimizer:HeatPumpOptimizer._terminal_cost's closure takes the buffer series
as an argument. What remains on the model is per-step scratch,
thermal_model:ThermalModel._step_buffer_refused, written by simulate_step
and read by simulate_trajectory (it drives the buffer-cap repair).
Metric (key: the values the production seams return):
  objective_order_maxdiff  = max |J(x) fresh - J(x) after other schedules|
                             over 24 schedules evaluated forward, reversed and
                             with a second objective call interleaved, on the
                             real space-stage objective captured from
                             optimizer:_scoped_minimize (two-zone, throttling
                             valve, 200 L buffer store, winter case);
  terminal_order_maxdiff   = the same for the terminal-cost closure alone;
  refused_order_maxdiff    = max |refused_kw fresh - after interleaving| from
                             ThermalModel.simulate_trajectory, tank at 68 C so
                             the cap refuses.
Expected at baseline: all three 0.0 exactly.
Command (repo root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/s2/objective_order.py
Positive control (--sticky-scratch): the two-zone step keeps the previous
non-zero _step_buffer_refused instead of resetting (a missing reset);
refused_order_maxdiff must go up.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine: cloud container B7.
Root rule: sys.path from the working directory.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time
sys.path.insert(0, ".")
sys.path.insert(0, "tests")
import numpy as np

import stress  # imports the package as ``heatpump_optimizer`` (tests/ path)
from heatpump_optimizer import optimizer as O
from heatpump_optimizer import thermal_model as TM

CAPTURED = []
_orig_min = O._scoped_minimize


def _capture(fun, x0, *a, **k):
    CAPTURED.append((fun, np.array(x0, dtype=float), k.get("args", ())))
    return _orig_min(fun, x0, *a, **k)
O._scoped_minimize = _capture
stress.SolverWork._wrapped = staticmethod(_capture)  # SolverWork binds the seam at import

TERMINALS = []
_orig_term = O.HeatPumpOptimizer._terminal_cost


def _cap_term(self, *a, **k):
    pair = _orig_term(self, *a, **k)
    TERMINALS.append((self, pair[0]))
    return pair
O.HeatPumpOptimizer._terminal_cost = _cap_term

if "--sticky-scratch" in sys.argv:
    _orig_tz = TM.ThermalModel._simulate_step_two_zone
    _last = {"v": 0.0}

    def _sticky(self, *a, **k):
        out = _orig_tz(self, *a, **k)
        if self._step_buffer_refused > 0.0:
            _last["v"] = self._step_buffer_refused
        else:
            self._step_buffer_refused = _last["v"]
        return out
    TM.ThermalModel._simulate_step_two_zone = _sticky


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    case = stress.build_case(
        season="winter", two_zone=True, dhw=False,
        config={"mixing_valve_mode": "smart_read", "buffer_tank_volume": 200.0},
        state={"buffer_tank_temperature": 68.0},
    )
    res = case["result"]
    print(f"RESULT solve_ok={int(bool(res.power_schedule))} count  # buffer_traj_len={len(res.buffer_temp_trajectory)}")
    # the space-stage objective: the widest captured problem
    fun, x0, args = max(CAPTURED, key=lambda c: c[1].size)
    n = x0.size
    rng = np.random.default_rng(7)
    p_max = float(np.max(res.power_schedule)) or 6.0
    xs = [rng.uniform(0, 6.0, n) for _ in range(24)] + [np.full(n, 6.0), np.zeros(n)]
    fresh = [fun(x, *args) for x in xs]
    rev = [fun(x, *args) for x in reversed(xs)][::-1]
    inter = []
    for i, x in enumerate(xs):
        fun(xs[(i + 5) % len(xs)], *args)       # a second objective call in between
        inter.append(fun(x, *args))
    obj_diff = max(max(abs(a - b) for a, b in zip(fresh, rev)),
                   max(abs(a - b) for a, b in zip(fresh, inter)))
    print(f"RESULT objective_order_maxdiff={obj_diff:.3e} abs  # over {len(xs)} schedules, n={n}")

    # terminal cost closure in isolation, on the optimizer that solved
    opt, term = TERMINALS[-1]
    model = opt.model
    init = case.get("initial")
    from datetime import datetime  # noqa
    st = TM.ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=-5.0,
                         upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                         buffer_tank_temperature=68.0)
    outs = np.full(n, -5.0)
    trajs = [model.simulate_trajectory(st, x, outs, dt_hours=0.25) for x in xs]
    tfresh = [term(t[0], t[1], t[2], t[3], t[4]) for t in trajs]
    tinter = []
    for i, t in enumerate(trajs):
        u = trajs[(i + 3) % len(trajs)]
        term(u[0], u[1], u[2], u[3], u[4])
        tinter.append(term(t[0], t[1], t[2], t[3], t[4]))
    print(f"RESULT terminal_order_maxdiff={max(abs(a - b) for a, b in zip(tfresh, tinter)):.3e} abs")

    ref_fresh = [np.asarray(t[5]) for t in trajs]
    refused_total = float(sum(r.sum() for r in ref_fresh))
    diffs = []
    for i, x in enumerate(xs):
        model.simulate_trajectory(st, xs[(i + 7) % len(xs)], outs, dt_hours=0.25)
        again = np.asarray(model.simulate_trajectory(st, x, outs, dt_hours=0.25)[5])
        diffs.append(float(np.max(np.abs(again - ref_fresh[i]))))
    print(f"RESULT refused_order_maxdiff={max(diffs):.3e} kW  # refused_kw_sum_fresh={refused_total:.3f}")
    p, t = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={p / max(t, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
    except Exception:
        sw = "na"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
