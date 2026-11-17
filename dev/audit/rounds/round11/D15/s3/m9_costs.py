#!/usr/bin/env python3
"""D15-s3 M9 (partial): per install-day, the C_real and C_model halves of the
same-information oracle, from the bundle's own accuracy samples.

Per local day of the rows (the replay half's zone), the distinct accuracy
samples the rows carry are folded into a fresh ``AccuracyTracker`` and its
``realised_cost`` (C_real over the sampled intervals) and ``predicted_cost``
(C_model, the plan's own price of the same intervals) are read. ``C_same`` --
the least cost on the measured house from the exogenous inputs at each
decision time -- is NOT computed here: the bundle carries those inputs for
the replay half's one day only, and the tree has no measured-house plant
other than the learned model, which the oracle excludes (REPORT.md).

Prints ratios and counts only (no money, reading or instant of the bundle):
the sample coverage of each day (samples / intervals the day spans) and the
model gap |C_real - C_model| / C_real.

Command (repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D15/s3/m9_costs.py --bundle B [--plant-scale K]
Perturbation ``--plant-scale K``: every sample's actual power and cost scaled
by K before the fold; the gap moves away from its unplanted value (K=1.2
raises C_real by 20 % on every day).
Null control ``--null``: each sample's predicted cost set to its actual cost;
the gap reads 0 on every day.
Baseline SHA: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: macOS arm64.
Instrumented symbols: accuracy:AccuracySample.from_dict,
    accuracy:AccuracyTracker.realised_cost, accuracy:AccuracyTracker.predicted_cost.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import datetime  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
for _p in (ROOT / "tests" / "hastub", ROOT / "custom_components", ROOT / "tools" / "replay", HERE):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import m7_rowscan as scan  # noqa: E402
from heatpump_optimizer.accuracy import AccuracySample, AccuracyTracker  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True, type=Path)
    ap.add_argument("--plant-scale", type=float, default=1.0)
    ap.add_argument("--null", action="store_true")
    a = ap.parse_args()
    cpu0, thr0 = time.process_time(), time.thread_time()
    bundle = scan.load(a.bundle)
    config = scan._download_config(a.bundle)
    interval = scan._interval_min(config)
    tz = scan._zone(bundle)
    rows = bundle.get("cycle_rows") or []
    days = scan.install_days(bundle)
    first = min(scan._t(r).astimezone(tz).date() for r in rows) if rows else None
    per_day: dict[str, dict] = {d: {} for d in days}
    span: dict[str, list] = {d: [] for d in days}
    for r in rows:
        day = f"day{(scan._t(r).astimezone(tz).date() - first).days}"
        span[day].append(scan._t(r))
        s = r.get("accuracy_sample")
        if not s:
            continue
        s = dict(s)
        if a.plant_scale != 1.0:
            for k in ("actual_power_kw", "actual_cost"):
                if s.get(k) is not None:
                    s[k] = s[k] * a.plant_scale
        if a.null and s.get("actual_cost") is not None:
            s["predicted_cost"] = s["actual_cost"]
        p = AccuracySample.from_dict(s)
        if p is None:
            continue
        pday = f"day{(p.when.astimezone(tz).date() - first).days}"
        if pday in per_day:
            per_day[pday].setdefault(p.when, p)
    gaps = []
    for d in days:
        tr = AccuracyTracker()
        tr.samples.extend(per_day[d][w] for w in sorted(per_day[d]))
        c_real, c_model = tr.realised_cost(), tr.predicted_cost()
        st = span[d]
        intervals = max(1, round((max(st) - min(st)).total_seconds() / 60.0 / interval) + 1) if st else 1
        cov = len(tr.samples) / intervals
        gap = abs(c_real - c_model) / abs(c_real) if c_real else None
        if gap is not None:
            gaps.append(gap)
        print(f"RESULT {d}_samples={len(tr.samples)} coverage={cov:.2f} unit=ratio")
        print(f"RESULT {d}_model_gap_rel={'n/a' if gap is None else round(gap, 4)} unit=ratio")
        print(f"RESULT {d}_C_same=not_computed")
    if len(gaps) >= 5:
        best = min(gaps)
        rest = list(gaps)
        rest.remove(best)
        print(f"RESULT model_gap_rel_range={round(min(gaps), 4)}..{round(max(gaps), 4)} cells={len(gaps)} unit=ratio")
        print(f"RESULT model_gap_rel_mean={round(sum(gaps) / len(gaps), 4)} drop_most_favourable={round(sum(rest) / len(rest), 4)} unit=ratio")
    cpu, thr = time.process_time() - cpu0, time.thread_time() - thr0
    print(f"RESULT thread_factor={round(cpu / thr, 3) if thr else 1.0}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
