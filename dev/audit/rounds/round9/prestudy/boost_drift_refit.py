"""R9-DIAG-1 feasibility arm: batch-refit the heat-loss scale from the drift
evidence the coordinator holds at warning time.

Reads the interval rows recorded by ``boost_drift_replay.py`` (see
``runs/``) and applies the same Newton relation the interval learner uses —
``dUA = -e·C/(ΔT·Δt)`` — but as one batch least-squares step over a window
of samples, instead of 2 % per sample for days:

    ~/.local/state/hpo/venv-ci/bin/python tools/audit/round9/prestudy/boost_drift_refit.py
"""
from __future__ import annotations

import json
import os
from datetime import datetime

UA, C, DT = 0.15, 10.0, 0.5   # configured; the harness's own house config

HERE = os.path.dirname(os.path.abspath(__file__))


def refit(path: str, day_from: int, day_to: int, exclude_boost: bool = True):
    d = json.load(open(path))
    rows = d["interval_rows"]
    sel, excluded = [], 0
    for i, r in enumerate(rows):
        k = i // 48                       # 48 half-hour rows per day
        if not (day_from <= k <= day_to):
            continue
        if r["err"] is None or r["act"] is None or r["outdoor"] is None:
            continue
        if exclude_boost and r["boost"]:
            excluded += 1
            continue
        sel.append(r)
    if not sel:
        return None
    num = den = 0.0
    for r in sel:
        dT = max(6.0, (r["act"] + r["pred"]) / 2.0 - r["outdoor"])
        e = r["act"] - r["pred"]           # observed - modelled, the learner's sign
        num += -e * C
        den += dT * DT
    delta_u = num / den if den else 0.0
    daily = {row["day"]: row for row in d["daily"]}
    return {
        "n": len(sel), "boost_rows_excluded": excluded,
        "learner_scale_now": daily[day_to]["hh_scale"],
        "batch_refit_scale": round(daily[day_to]["hh_scale"] + delta_u / UA, 3),
    }


if __name__ == "__main__":
    runs = os.path.join(HERE, "runs")
    for fname, truth in (
        ("boost-model-wrong15.json", 1.15),
        ("null-no-boost.json", 1.00),
    ):
        path = os.path.join(runs, fname)
        if not os.path.exists(path):
            continue
        print(f"== {fname} (true scale {truth})")
        for label, args in (
            ("day 10, boost rows excluded (just after the boost days)",
             (9, 10, True)),
            ("day 12, boost rows excluded (3 settled days)",
             (9, 12, True)),
            ("day 12, boost rows included",
             (9, 12, False)),
        ):
            print(f"  {label}: {refit(path, *args)}")
