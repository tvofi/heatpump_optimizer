"""How often a solve calls each twin: scalar against batch, per scenario (counts; contention-immune).

Metric: calls per ``build_case`` solve of ``tariff.peak_cost_smooth`` (scalar capacity term, as the
optimizer module binds it), ``tariff.peak_cost_batch`` and ``ThermalModel.simulate_trajectory`` (scalar).
The batch trajectory wrapper is installed but did not register on this build (a gap, not a zero). With the per-call CPU of
each twin (``bench_peak.py``, ``bench_traj.py``) this prices a merge that makes the scalar a one-row
batch: added CPU = scalar calls x (one-row cost - scalar cost).

Perturbation: ``--root`` at a tree carrying patches/R1_objective_one_row_REJECTED.patch (the scalar
objective as one row of the batch) -- the scalar ``peak_cost_smooth`` and ``simulate_trajectory``
counts must fall to 0 (1 on the space-only tariff solve, its refusal report) and ``peak_cost_batch``
must rise by the same number. Recorded: 7-17 scalar calls per solve fell to 0-1; batch rose by 7-17.

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s3/count_calls.py --root DIR

Counts only. Thread-pinned. Writes nothing.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

root = Path(sys.argv[sys.argv.index("--root") + 1]).resolve()
os.chdir(root)
sys.path[:0] = ["tests", "custom_components"]
sys.argv = ["stress"]
import stress  # noqa: E402
from heatpump_optimizer import optimizer as O  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bench_solve import SPECS  # noqa: E402

counts = {}


def wrap(owner, name, key, rows=False):
    real = getattr(owner, name)

    def counted(*a, **k):
        counts[key] = counts.get(key, 0) + 1
        if rows:
            m = k.get("power_matrix", a[2] if len(a) > 2 else None)
            if m is not None:
                counts[key + "_rows"] = counts.get(key + "_rows", 0) + len(m)
        return real(*a, **k)
    setattr(owner, name, counted)


wrap(O, "peak_cost_smooth", "peak_cost_smooth")
wrap(O, "peak_cost_batch", "peak_cost_batch")
wrap(ThermalModel, "simulate_trajectory", "simulate_trajectory")
wrap(ThermalModel, "simulate_trajectory_batch", "simulate_trajectory_batch", rows=True)
for label, spec in SPECS:
    counts.clear()
    stress.build_case(**spec)
    print(f"{label:30s} " + " ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    for k, v in sorted(counts.items()):
        print(f"RESULT {label}:{k}={v} count")
