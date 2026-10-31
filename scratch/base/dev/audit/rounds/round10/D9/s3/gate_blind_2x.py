"""D9.M2 -- does the shipped stress gate see a synthetic 2x solve regression
that lives OUTSIDE the metered simulate seams?

Metric: for each of five sweep scenarios, inject exactly ``--factor`` times the
CPU of HeatPumpOptimizer.optimize (stress.cpu_scaler wrapped around the
production method: the solve runs once, then burns (factor-1) x its own CPU,
so no count and no seam per-call cost moves), and judge the injected solve
with the gate's OWN verdict functions -- stress.work_over_verdict (both count
channels vs the clean solve as baseline), stress.kernel_cost_over_verdict
(seam CPU vs the clean solve) and stress.scenario_verdict (solve CPU / the
reference unit vs tests/stress_budgets.json x SCENARIO_BUDGET_FACTOR).
Count key: number of scenarios for which ANY verdict fires (``flagged``).
Positive control arm (``--arm kernel``): the same factor on the simulate
seams instead (ThermalModel.simulate_step / simulate_trajectory_batch /
simulate_dhw_step) -- the kernel verdict must fire there.

Command (repo root):
  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D9/s3/gate_blind_2x.py
  [--factor 2.0] [--arm solve|kernel]
Perturbation: STRESS_SCENARIO_FACTOR=1.5 (read by tests/stress.py at import)
  -> flagged_solve_arm moves 0 -> 5 at factor 2.0; --factor 1.0 is the null
  control (0 flagged in every arm).
Expected: flagged_solve_arm=0 of 5 (exact, a count); solve_cpu_ratio ~2.0 +-0.3
  (provisional, timing). Baseline 17f1c55fad1b, machine: Apple M-series
  macOS dev box (B3), venv-ci python 3.14.
"""
import os
for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")
import argparse, resource, sys, time
sys.path.insert(0, "tests")
sys.argv_saved = list(sys.argv); sys.argv = [sys.argv[0]]
import stress  # noqa: E402  (module import runs no sweep; __main__ guarded)
sys.argv = sys.argv_saved
from heatpump_optimizer.optimizer import HeatPumpOptimizer  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--factor", type=float, default=2.0)
ap.add_argument("--arm", choices=("solve", "kernel"), default="solve")
a = ap.parse_args()

LABELS = ["flat/1z/space", "flat/2z/dhw", "winter/1z/dhw",
          "shoulder/2z/space", "winter/tariff+cycle"]
combos = {c["label"]: c for c in stress.sweep_combinations()}
table = stress.load_budget_table()
cal = stress.Calibration(5); cal.warm_up()
wrap = stress.cpu_scaler(a.factor)

def solve(label):
    spec = dict(combos[label]); spec.pop("label")
    cal.sample()
    run = stress.build_case(**spec)
    return run, run["solve_cpu_ms"] / cal.unit_ms

orig = {"opt": HeatPumpOptimizer.optimize,
        "st": ThermalModel.simulate_step,
        "bt": ThermalModel.simulate_trajectory_batch,
        "dh": ThermalModel.simulate_dhw_step}
def inject():
    if a.arm == "solve":
        HeatPumpOptimizer.optimize = wrap(orig["opt"])
    else:
        # SolverWork re-binds its own captured class attributes, so the
        # injection must go onto the attributes it captured.
        stress.SolverWork._step_wrapped = wrap(orig["st"])
        stress.SolverWork._batch_wrapped = wrap(orig["bt"])
        stress.SolverWork._dhw_step_wrapped = wrap(orig["dh"])
def restore():
    HeatPumpOptimizer.optimize = orig["opt"]
    stress.SolverWork._step_wrapped = orig["st"]
    stress.SolverWork._batch_wrapped = orig["bt"]
    stress.SolverWork._dhw_step_wrapped = orig["dh"]

flagged = 0; ratios = []
t0p, t0t = time.process_time(), time.thread_time()
for label in LABELS:
    base, base_ratio = solve(label)
    inject()
    try:
        inj, inj_ratio = solve(label)
    finally:
        restore()
    ev = stress.work_over_verdict(inj["solver_evals"], base["solver_evals"])
    ss = stress.work_over_verdict(inj["solver_simulate_steps"],
                                  base["solver_simulate_steps"])
    vouched = max(inj["solver_evals"] / max(base["solver_evals"], 1),
                  inj["solver_simulate_steps"] / max(base["solver_simulate_steps"], 1))
    kc = stress.kernel_cost_over_verdict(inj["solver_kernel_ms"],
                                         base["solver_kernel_ms"], vouched)
    sv = stress.scenario_verdict(label, inj_ratio, table)
    over = bool(sv and sv[0])
    glob = inj_ratio > stress.live_solve_budget_ratio()
    any_ = ev or ss or kc or over or glob
    flagged += any_
    r = inj["solve_cpu_ms"] / base["solve_cpu_ms"]; ratios.append(r)
    print(f"{label:22s} cpu x{r:.2f} kernel x{inj['solver_kernel_ms']/base['solver_kernel_ms']:.2f} "
          f"evals {inj['solver_evals']}/{base['solver_evals']} ratio {inj_ratio:.1f} "
          f"budget {stress.scenario_budget(label, table)} -> evals={ev} sim={ss} "
          f"kernel={kc} budget={over} global={glob}")
pt, tt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT flagged_{a.arm}_arm={flagged} of {len(LABELS)} scenarios")
print(f"RESULT solve_cpu_ratio_median={sorted(ratios)[len(ratios)//2]:.3f} x (provisional)")
print(f"RESULT scenario_budget_factor={stress.SCENARIO_BUDGET_FACTOR}")
print(f"RESULT thread_factor={pt/tt:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
