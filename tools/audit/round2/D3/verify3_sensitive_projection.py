#!/usr/bin/env python3
"""Verifier seat 3, D3-10: is the proposed SENSITIVE projection BLAS-stable?

Metric: per SENSITIVE fixture, the relative gap between the COMMITTED golden
value (recorded on another machine) and a fresh capture on this machine, for
baseline_cost and predicted_cost, plus the absolute compressor_starts gap;
and the verdict the finder's proposed rule would return (baseline_cost and
predicted_cost within 5 %, compressor starts within 2).

Run from the repository root:

    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
    PYTHONPATH=tests/hastub .venv/bin/python \
      tools/audit/round2/D3/verify3_sensitive_projection.py

Expected (baseline c398fc84eec25fc44b60d74aae05b9a2da205884, 8-core Apple M1,
numpy on OpenBLAS): projection_fails=0 of 5, worst_rel_gap <= 0.05 exactly;
tolerance: counts are exact, the gaps are the numbers under test.

Instrumented symbol: heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize,
reached through tests/golden.py:capture for the five names in
tests/env_drift.py:SENSITIVE. Call count is reported so the RESULT cannot be
a constant.

Perturbation: apply tools/audit/round2/D3/mutants/M01.patch (the
thermal_model.dhw_coil_draw_reduction clamp the finder used to show the
unjudged branch) and re-run; projection_fails must rise from 0 to at least 1
(wood_coil). Direction: up.

Writes nothing outside its own directory.
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

import argparse
import json
import platform
import resource
import sys
import time
from pathlib import Path

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import golden  # noqa: E402  (tests/golden.py)
from heatpump_optimizer.optimizer import HeatPumpOptimizer  # noqa: E402

SENSITIVE = (
    "valve_storage_smart_write",
    "wood_two_tank",
    "wood_two_tank_smart_write",
    "wood_coil",
    "valve_upper_direct_slab",
)
REL_TOL = 0.05        # the finder's "within 5 %"
STARTS_TOL = 2        # the finder's "compressor starts within 2"

_CALLS = {"optimize": 0}
_real_optimize = HeatPumpOptimizer.optimize


def _counting_optimize(self, *a, **kw):
    _CALLS["optimize"] += 1
    return _real_optimize(self, *a, **kw)


HeatPumpOptimizer.optimize = _counting_optimize


def _rel(a: float, b: float) -> float:
    """Relative gap, referenced to the committed value."""
    if a == 0.0:
        return 0.0 if b == 0.0 else float("inf")
    return abs(b - a) / abs(a)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixtures", default="tests/golden")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    fixtures = Path(args.fixtures)
    rows = []
    t0 = time.process_time()
    w0 = time.time()
    for name in SENSITIVE:
        committed = json.loads((fixtures / f"{name}.json").read_text())
        fresh = golden.capture(name, golden.SCENARIOS[name])
        row = {
            "scenario": name,
            "committed": {
                k: committed.get(k)
                for k in ("baseline_cost", "predicted_cost", "compressor_starts")
            },
            "fresh": {
                k: fresh.get(k)
                for k in ("baseline_cost", "predicted_cost", "compressor_starts")
            },
        }
        row["rel_baseline_cost"] = _rel(
            committed["baseline_cost"], fresh["baseline_cost"]
        )
        row["rel_predicted_cost"] = _rel(
            committed["predicted_cost"], fresh["predicted_cost"]
        )
        row["d_starts"] = abs(
            int(committed["compressor_starts"]) - int(fresh["compressor_starts"])
        )
        # Exactly the rule under test.
        row["projection_passes"] = (
            row["rel_baseline_cost"] <= REL_TOL
            and row["rel_predicted_cost"] <= REL_TOL
            and row["d_starts"] <= STARTS_TOL
        )
        # For reference: what the existing exact comparison says.
        row["exact_identical"] = all(
            committed.get(k) == fresh.get(k) for k in sorted(set(committed) | set(fresh))
        )
        row["n_leaves_differing"] = sum(
            1
            for k in sorted(set(committed) | set(fresh))
            if committed.get(k) != fresh.get(k)
        )
        rows.append(row)
        print(
            f"  {name:28s} baseline {committed['baseline_cost']:>12.6f} -> "
            f"{fresh['baseline_cost']:>12.6f} ({100 * row['rel_baseline_cost']:6.3f} %)  "
            f"predicted {committed['predicted_cost']:>11.6f} -> "
            f"{fresh['predicted_cost']:>11.6f} ({100 * row['rel_predicted_cost']:6.3f} %)  "
            f"starts {committed['compressor_starts']} -> {fresh['compressor_starts']} "
            f"(d={row['d_starts']})  "
            f"{'PASS' if row['projection_passes'] else 'FAIL'}  "
            f"exact:{'same' if row['exact_identical'] else str(row['n_leaves_differing']) + ' fields differ'}"
        )
    cpu = time.process_time() - t0
    wall = time.time() - w0

    fails = sum(1 for r in rows if not r["projection_passes"])
    worst = max(
        max(r["rel_baseline_cost"], r["rel_predicted_cost"]) for r in rows
    )
    worst_starts = max(r["d_starts"] for r in rows)
    exact_diff = sum(1 for r in rows if not r["exact_identical"])

    print()
    print(f"RESULT projection_fails={fails} count")
    print(f"RESULT exact_comparison_fails={exact_diff} count")
    print(f"RESULT worst_rel_gap={worst:.6f} fraction")
    print(f"RESULT worst_starts_gap={worst_starts} count")
    print(f"RESULT optimize_calls={_CALLS['optimize']} count")
    print(f"RESULT margin_to_5pct={REL_TOL - worst:.6f} fraction")
    ru = resource.getrusage(resource.RUSAGE_SELF)
    thread_cpu = ru.ru_utime + ru.ru_stime
    print(f"RESULT thread_factor={cpu / max(thread_cpu, 1e-9):.4f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={ru.ru_nswap} count")
    print(f"RESULT cpu_s={cpu:.2f} s   wall_s={wall:.2f} s")
    print(f"machine: {platform.platform()} {platform.processor()}")

    if args.out:
        Path(args.out).write_text(
            json.dumps(
                {
                    "rel_tol": REL_TOL,
                    "starts_tol": STARTS_TOL,
                    "projection_fails": fails,
                    "exact_comparison_fails": exact_diff,
                    "worst_rel_gap": worst,
                    "optimize_calls": _CALLS["optimize"],
                    "load1": os.getloadavg()[0],
                    "rows": rows,
                },
                indent=1,
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
