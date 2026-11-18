"""R10-LEARNER-ETA: the published learner progress against synthetic ground truth.

Companion to the R10-IDENT Q3 study harness (``eta_rolling.py`` on
study/r10-identifiability @ 4f2d513c9), which scores ETA estimators the tree
never shipped and so reads the same at any head. This one reads what the
tree publishes -- ``_learning_view()["learner_progress"]`` -- on the same
plants and trajectories, once a day, with the weekly snapshot ring taken as
the heartbeat takes it, and scores it against two truths per learner:

* the gate day: the first day the learner's own sample count reaches the
  ``samples_needed`` the view names (the counting phase's honest target);
* the settle day: the study's rule (``eta_rolling.settle_day``) on the
  learner's own end point.

Metrics, one line each (counted over plants x learners x daily checkpoints):
  eta_on_settling   checkpoints publishing ``eta_days`` while the count has
                    already reached the gate -- a day count for a settling
                    learner, the defect; must be 0
  gate_err p10/p50/p90  (checkpoint + eta_days) - gate day, in days, over the
                    checkpoints that publish one
  settle_err p10/p50/p90  the same ETAs scored against the settle day: why the
                    figure names the gate and never convergence
  phase_<p>         checkpoints per published phase
  field             ``absent`` where the view publishes no ``learner_progress``
                    (the baseline), ``present`` otherwise

Command (repository root; STUDY is a directory holding eta_rolling.py and
ident_rolling.py from the study commit, e.g.
``git archive 4f2d513c9 dev/audit/rounds/round10/study-ident | tar -x -C "$X"``):
    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_learner_eta.py \\
        --study "$X/dev/audit/rounds/round10/study-ident" [--plants E1,E2] [--days 42]
Perturbation: ``--alpha-scale 2`` doubles HOUSE_LOSS_ALPHA: the house gate's
    count and its gate day move together, so gate_err stays near where it was
    while samples_needed for the house falls.
Null control: plant E0 (prior = truth): the values have nothing to learn, yet
    the gates still open at a count -- the view counts and names no settle ETA.
"""
from __future__ import annotations

import argparse
import math
import os
import sys
from collections import Counter

import numpy as np


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", required=True)
    ap.add_argument("--plants", default="E0,E1,E2,E3,E4,E5,E6")
    ap.add_argument("--days", type=float, default=42.0)
    ap.add_argument("--seed", type=int, default=20261014)
    ap.add_argument("--alpha-scale", type=float, default=1.0)
    a = ap.parse_args()
    sys.path.insert(0, os.path.abspath(a.study))
    import eta_rolling as er  # noqa: E402  (inserts tests/ and custom_components/)
    import ident_rolling as ir  # noqa: E402
    from homeassistant.util import dt as dt_util  # noqa: E402

    from heatpump_optimizer import coordinator as coord_mod  # noqa: E402

    if a.alpha_scale != 1.0:
        coord_mod.HOUSE_LOSS_ALPHA *= a.alpha_scale
    views: list[dict] = []
    make_arm = ir.make_arm

    def instrumented(*args, **kw):
        arm = make_arm(*args, **kw)
        c = arm["coord"]
        refresh = c._refresh_model_corrections
        step = {"i": 0}

        def tick():
            refresh()
            now = dt_util.now()
            if c._snapshot_ring.due(now):
                c._snapshot_ring.take(now, c._learner_snapshot_payloads(), {}, True)
            if step["i"] % er.SPD == er.SPD - 1:
                views.append(c._learning_view().get("learner_progress"))
            step["i"] += 1

        c._refresh_model_corrections = tick
        return arm

    ir.make_arm = instrumented
    keys = {"house": ("s", "n"), "lower": ("r", "n_lo"), "solar": ("ap", "ap_n"), "gains": ("g", "n")}
    on_settling, gate_err, settle_err, phases = 0, [], [], Counter()
    present = True
    for plant in a.plants.split(","):
        views.clear()
        rec, _truth, _total = er.run(plant, a.days, a.seed)
        if any(v is None for v in views):
            present = False
            continue
        for name, (xk, nk) in keys.items():
            x, n = rec[xk], rec[nk]
            settle = er.settle_day(x, float(np.mean(er.daily(x)[-3:])), x[0])
            for day, view in enumerate(views, start=1):
                row = view[name]
                phases[row["phase"]] += 1
                need, eta = row["samples_needed"], row["eta_days"]
                if eta is None:
                    continue
                hit = np.nonzero(np.asarray(n) >= need)[0] if need is not None else []
                gate_day = (hit[0] + 1) / er.SPD if len(hit) else math.nan
                if row["samples"] >= (need or 0):
                    on_settling += 1
                if math.isfinite(gate_day):
                    gate_err.append(day + eta - gate_day)
                if math.isfinite(settle) and day < settle:
                    settle_err.append(day + eta - settle)
    print(f"RESULT field={'present' if present else 'absent'}")
    if not present:
        return
    print(f"RESULT eta_on_settling={on_settling}")
    for label, errs in (("gate_err", gate_err), ("settle_err", settle_err)):
        if errs:
            p10, p50, p90 = np.percentile(errs, (10, 50, 90))
            print(f"RESULT {label}.p10={p10:+.1f} p50={p50:+.1f} p90={p90:+.1f} n={len(errs)}")
        else:
            print(f"RESULT {label}.n=0")
    for phase, k in sorted(phases.items()):
        print(f"RESULT phase_{phase}={k}")


if __name__ == "__main__":
    main()
