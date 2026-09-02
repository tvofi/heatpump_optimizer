#!/usr/bin/env python3
"""D6 sub-harness: re-execute the closed-loop learning arm the README quotes.

Metric: degree-hours below the comfort floor over three simulated days with a
house that loses 35 % more heat than configured (plant_error=1.35) and a
4.25 kW pump, once with the heat-loss learner on and once off; plus the
learned scale's end value and the drift of an already-correct model.

Command (from the export root):
    PYTHONPATH=tests/hastub python tools/audit/round2/D6/rolling_learning.py

Expected (baseline c398fc84eec25fc44b60d74aae05b9a2da205884, 8-core Apple M1,
numpy/OpenBLAS pinned to one thread): breach_uncorrected ≈ 6.7 degree-hours
(±0.5), breach_learned = 0.0 (exact), scale_end in (1.05, 1.50],
correct_model_drift < 0.12. Degree-hours are contention-immune (deterministic
solve over seeded inputs); wall time is not reported.

Instrumented symbol: tests/rolling.py:run_rolling driving
heatpump_optimizer.coordinator.HeatPumpOptimizerCoordinator with learn=True.
Perturbation: plant_error 1.35 -> 1.0 in the two arms below; breach_uncorrected
goes to zero and the learner's gain vanishes (to_zero).

The helper block of tests/rolling.py (everything before its first
``R.section``) is executed in a private namespace so ``run_rolling`` and
``floor_for`` are reused verbatim without triggering the rest of that suite.
Writes nothing.
"""
import os

for _k in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_k, "1")

import resource
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

_src = open("tests/rolling.py", encoding="utf-8").read().split("\n")
_cut = next(i for i, line in enumerate(_src) if line.startswith("R.section("))
_ns = {"__name__": "rolling_prefix", "__file__": "tests/rolling.py"}
exec(compile("\n".join(_src[:_cut]), "tests/rolling.py[prefix]", "exec"), _ns)

run_rolling = _ns["run_rolling"]
floor_for = _ns["floor_for"]
DT = _ns["DT"]
np = _ns["np"]

TRUE_ERROR = float(os.environ.get("D6_PLANT_ERROR", "1.35"))
BOUND_PUMP = {"heat_pump_max_power": 4.25}

t0 = time.process_time()
learned = run_rolling(days=3, dhw=False, plant_error=TRUE_ERROR, learn=True, config=BOUND_PUMP)
uncorrected = run_rolling(days=3, dhw=False, plant_error=TRUE_ERROR, config=BOUND_PUMP)
correct = run_rolling(days=2, dhw=False, plant_error=1.0, learn=True)

steps = learned["total_steps"]
bound = floor_for(learned["config"], steps)
breach_learned = float(np.sum(np.maximum(0.0, bound - learned["history"]["room"])) * DT)
breach_plain = float(np.sum(np.maximum(0.0, bound - uncorrected["history"]["room"])) * DT)
scale = learned["history"]["heat_loss_scale"]
samples = learned["history"]["heat_loss_samples"]
drift = correct["history"]["heat_loss_scale"]

print(f"RESULT plant_error={TRUE_ERROR} ratio")
print(f"RESULT breach_uncorrected={breach_plain:.3f} degree_hours")
print(f"RESULT breach_learned={breach_learned:.3f} degree_hours")
print(f"RESULT scale_start={float(scale[0]):.4f} ratio")
print(f"RESULT scale_end={float(scale[-1]):.4f} ratio")
print(f"RESULT scale_overshoot_past_true={float(scale[-1]) - TRUE_ERROR:.4f} ratio")
print(f"RESULT scale_last_quarter_std={float(np.std(scale[-len(scale) // 4:])):.5f} ratio")
print(f"RESULT learner_samples={int(samples[-1])} count")
print(f"RESULT correct_model_drift={abs(float(drift[-1]) - 1.0):.4f} ratio")
print(f"RESULT cpu_seconds={time.process_time() - t0:.1f} s")
_pt = time.process_time()
_tt = time.thread_time()
print(f"RESULT thread_factor={(_pt / _tt) if _tt else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
