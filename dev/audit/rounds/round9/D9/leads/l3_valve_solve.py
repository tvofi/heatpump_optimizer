"""l3_valve_solve: what one two-zone throttling-valve solve costs, and whether the stress gate samples it.

Metric (one line): per golden scenario, simulate-step-equivalents and L-BFGS-B evaluations per
optimize() as the gate's own meter counts them (tests/stress.py:SolverWork around each call), and
optimize() thread CPU in tests/stress.py:reference_solve units; plus the count of
tests/stress.py:sweep_combinations() cases whose built plant throttles (key = the
mixing_valve_mode of the ThermalParameters build_case hands optimize(), not the spec text).
Cells: valve_storage, valve_storage_smart_write, valve_upper_direct_slab, wood_two_tank (valve);
controls winter_two_zone_no_dhw, shoulder_two_zone (two-zone, no valve).
Perturbation: --perturb novalve sets mixing_valve_mode='none' on the valve cells (config change);
their counts and CPU ratio must fall toward the controls.
Command:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/leads/l3_valve_solve.py [--perturb novalve]
Expected: stress_sweep_valve_cases=0 of 51 (exact); counts exact per build; CPU ratios provisional.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: shared 4-core Linux leads box, venv314.
Instrumented symbols: heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize (metered by
tests/stress.py:SolverWork, which hooks _scoped_minimize and the ThermalModel simulate kernels).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import copy, sys, time
import numpy as np
sys.path[:0] = ["tests", "custom_components"]
import golden  # noqa: E402
import stress  # noqa: E402
from heatpump_optimizer import optimizer as om, mixing_valve  # noqa: E402

PERTURB = "--perturb" in sys.argv and sys.argv[sys.argv.index("--perturb") + 1] == "novalve"
_O = om.HeatPumpOptimizer.optimize
C = {}


def metered(self, *a, **k):
    t, p = time.thread_time(), time.process_time()
    w = stress.SolverWork()
    with w:
        res = _O(self, *a, **k)
    C["cpu"] += time.thread_time() - t
    C["proc"] += time.process_time() - p
    C["steps"] += w.simulate_steps
    C["evals"] += w.evaluations
    return res


class _Stop(Exception):
    pass


def sentinel(self, *a, **k):
    raise _Stop(self.model.params.mixing_valve_mode)


# 1) stress sweep coverage: optimize() is a sentinel here, so no sweep solve runs.
om.HeatPumpOptimizer.optimize = sentinel
valve_cases = seen = 0
combos = stress.sweep_combinations()
for spec in combos:
    try:
        stress.build_case(**{k: v for k, v in spec.items() if k != "label"})
    except _Stop as e:
        seen += 1
        valve_cases += bool(mixing_valve.is_throttling(e.args[0]))
assert seen == len(combos), (seen, len(combos))
om.HeatPumpOptimizer.optimize = metered

ref = float(np.median([stress.reference_solve()[2] / 1000.0 for _ in range(3)]))
VALVE = ("valve_storage", "valve_storage_smart_write", "valve_upper_direct_slab", "wood_two_tank")
CTRL = ("winter_two_zone_no_dhw", "shoulder_two_zone")
rows = {}
for name in VALVE + CTRL:
    spec = copy.deepcopy(golden.SCENARIOS[name])
    if PERTURB and name in VALVE:
        spec.setdefault("config_overrides", {})["mixing_valve_mode"] = "none"
    C.update(steps=0, evals=0, cpu=0.0, proc=0.0)
    golden.capture(name, spec)
    rows[name] = dict(C)
    print(f"cell {name:26s} step_equivalents={C['steps']:9d} evaluations={C['evals']:6d} "
          f"solve_cpu={C['cpu']:.2f}s ratio_to_ref={C['cpu'] / ref:.1f}", flush=True)
vs = [rows[n]["steps"] for n in VALVE]
cs = [rows[n]["steps"] for n in CTRL]
ve = [rows[n]["evals"] for n in VALVE]
ce = [rows[n]["evals"] for n in CTRL]
vr = [rows[n]["cpu"] / ref for n in VALVE]
cr = [rows[n]["cpu"] / ref for n in CTRL]
print(f"RESULT stress_sweep_valve_cases={valve_cases} of {len(combos)} count")
print(f"RESULT valve_step_equivalents_min={min(vs)} max={max(vs)} count")
print(f"RESULT control_step_equivalents_min={min(cs)} max={max(cs)} count")
print(f"RESULT valve_evaluations_min={min(ve)} max={max(ve)} count")
print(f"RESULT control_evaluations_min={min(ce)} max={max(ce)} count")
print(f"RESULT cpu_ratio_to_reference_valve_min={min(vr):.1f} max={max(vr):.1f} ratio")
print(f"RESULT cpu_ratio_to_reference_control_min={min(cr):.1f} max={max(cr):.1f} ratio")
print(f"RESULT reference_solve_cpu_s={ref:.4f}")
print(f"RESULT perturbed={int(PERTURB)}")
tf = sum(r["proc"] for r in rows.values()) / max(sum(r["cpu"] for r in rows.values()), 1e-9)
print(f"RESULT thread_factor={tf:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = int(next(l.split()[1] for l in open("/proc/vmstat") if l.startswith("pswpin")))
except Exception:  # noqa: BLE001
    sw = -1
print(f"RESULT swapins={sw}")
