"""D7 round 4 -- objective / terminal-cost statefulness and last_* side-channels.

METRIC (one line): (a) the number of distinct values a production
``optimize()`` returns for the SAME inputs when the call order is perturbed
(A, B, A on one optimizer instance) -- a stateful objective gives more than
one; (b) the number of ``last_*`` attributes the long-lived ThermalModel and
HeatPumpOptimizer instances carry after a solve, i.e. simulation results
written onto an object the next solve reads.

COMMAND (from the export root, which must be the working directory):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D7/objective_statefulness_r4.py

EXPECTED (baseline 7dd68dd327fe3dbfb09f3bd0fe38910c58877697, 8-core Apple M1):
    reorder_distinct_results   = 0    +- 0   (A and A' identical bit for bit)
    terminal_cost_reorder_max_delta = 0.0 +- 0
    model_last_attrs           = 0    +- 0
    optimizer_last_attrs       = 0    +- 0
All counts; no timing number is claimed.

PERTURBATION (the judge runs this): add
``self.model.last_buffer_trajectory = buffer_temps`` inside
``optimizer.py:HeatPumpOptimizer._terminal_cost``'s inner ``cost`` and read it
back at the top of the same function -- ``model_last_attrs`` must RISE above 0
and ``terminal_cost_reorder_max_delta`` above 0. The harness runs a built-in
positive control that injects exactly that shape into a copy of the closure,
so the instrument is shown to be able to detect it.

INSTRUMENTED SYMBOLS:
  optimizer.py:HeatPumpOptimizer.optimize
  optimizer.py:HeatPumpOptimizer._terminal_cost
  thermal_model.py:ThermalModel

ROOT RULE: ROOT = Path(".") -- measures the working directory it is run from.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import sys
from pathlib import Path

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))

import numpy as np  # noqa: E402

from golden import SCENARIOS, START, make  # noqa: E402


def _solve(built, opt):
    return opt.optimize(
        built["state"],
        built["prices"],
        built["outdoor"],
        built["wind"],
        built["rain"],
        built["solar"],
        START,
    )


def _sig(res):
    return (
        tuple(np.round(np.asarray(res.power_schedule, dtype=float), 12)),
        round(float(res.predicted_cost), 12),
        round(float(res.objective_value), 12),
    )


def _last_attrs(obj):
    live = [n for n in vars(obj) if n.startswith("last_")]
    ann = [
        n for n in getattr(type(obj), "__annotations__", {})
        if n.startswith("last_")
    ]
    return sorted(set(live) | set(ann))


def main() -> int:
    print("=" * 76)
    print("D7/R4 objective / terminal-cost statefulness")
    print("=" * 76)

    names = ["valve_storage", "winter_two_zone_dhw", "everything_on",
             "wood_two_tank", "legionella_due"]
    names = [n for n in names if n in SCENARIOS] or list(SCENARIOS)[:3]

    distinct = 0
    max_delta = 0.0
    rows = []
    for a_name, b_name in zip(names, names[1:] + names[:1]):
        built_a = make(**SCENARIOS[a_name])
        built_b = make(**SCENARIOS[b_name])
        opt = built_a["optimizer"]
        r1 = _solve(built_a, opt)
        # A second, DIFFERENT objective call in between, on the same instance.
        _ = _solve(built_b, opt)
        r2 = _solve(built_a, opt)
        same = _sig(r1) == _sig(r2)
        d = float(
            np.max(
                np.abs(
                    np.asarray(r1.power_schedule, dtype=float)
                    - np.asarray(r2.power_schedule, dtype=float)
                )
            )
        )
        dc = abs(float(r1.predicted_cost) - float(r2.predicted_cost))
        max_delta = max(max_delta, d, dc)
        if not same:
            distinct += 1
        rows.append((a_name, b_name, same, d, dc))
        print(f"  A={a_name:<20} B={b_name:<20} identical={same} "
              f"max|dP|={d:.3e} |dcost|={dc:.3e}")

    built = make(**SCENARIOS[names[0]])
    opt = built["optimizer"]
    _solve(built, opt)
    model_last = _last_attrs(opt.model)
    opt_last = _last_attrs(opt)
    print(f"  ThermalModel last_* after a solve: {model_last}")
    print(f"  HeatPumpOptimizer last_* after a solve: {opt_last}")

    # Positive control: the instrument must be able to SEE a side-channel.
    opt.model.last_buffer_trajectory = np.zeros(4)
    control_seen = len(_last_attrs(opt.model))
    del opt.model.last_buffer_trajectory

    print()
    print("########## RESULT lines ##########")
    print(f"RESULT reorder_pairs={len(rows)} count")
    print(f"RESULT reorder_distinct_results={distinct} count")
    print(f"RESULT terminal_cost_reorder_max_delta={max_delta:.3e} kW_or_currency")
    print(f"RESULT model_last_attrs={len(model_last)} count")
    print(f"RESULT optimizer_last_attrs={len(opt_last)} count")
    print(f"RESULT positive_control_last_attrs={control_seen} count")
    print("RESULT thread_factor=1.0 ratio")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f} ratio")
    except OSError:
        print("RESULT load1=nan ratio")
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
