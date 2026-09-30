"""R9-F2.4 companion: what ONE extra bang-bang seed costs and buys (D0-s2-02).

The finder's harness (``tools/audit/round9/D0/s2/race.py``, evidence commit
79aa98ec, sha1 75739b2688b3ea4c3e838258fe0f2e0f0c172ff1) prices the whole
13-rung Emax ladder: ``--perturb add_emax_ladder`` hands production's own
seam every rung at once. The finding's fix scope leaves one cheaper option
open -- a SINGLE seed -- and #1294's refusal stands against the ladder, so
the refusal or the fix has to be priced on the cheaper option, not on the
ladder. This measures it in race.py's own units and cells:

  f0     the objective at the FIRST ``_multi_start_minimize`` call's returned
         x, evaluated on that call's own recorded objective and args -- the
         quantity race.py prints as ``f=`` and the gap is relative to.
  cpu_s  ``time.process_time()`` around the whole ``optimize()``.

Every arm is the same cell solved with one seed appended to the candidate
list production hands its own seam (never replacing one), built exactly as
race.py's ladder builds it: ``_price_ranked_start`` at ``fr`` of the bounds'
max energy, capped by the bounds. ``none`` is the unmodified tree, so the
f0 column of the ``none`` arm is this box's reproduction of race.py's ``f=``
and the cpu column is the baseline the percentage is of.

Run from the repository root of the tree under measurement (race.py inserts
"tests" and "custom_components" relative to the cwd, so it measures the cwd
tree, not the export):

  PYTHONPATH=tests/hastub python3 \
      tools/audit/handoff/r9-f2-solver-4/seed_price.py \
      --export $EXPORT [--fractions none,0.8] [--cells shoulder] \
      [--weather winter_cold,winter_mild,summer_cool,shoulder]

Thread pinning and the cell grid are race.py's own; nothing here re-derives
them. Counts and objective values are contention-immune; the cpu column is
not, so it is read as a ratio of two arms measured in the same process.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from unittest import mock

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", required=True,
                    help="the evidence export's root (79aa98ec)")
    ap.add_argument("--fractions", default="none,0.2,0.4,0.6,0.8,1.0")
    ap.add_argument("--cells", default="shoulder")
    ap.add_argument("--weather",
                    default="winter_cold,winter_mild,summer_cool,shoulder")
    ap.add_argument("--horizon", type=int, default=24)
    a = ap.parse_args()

    sys.path.insert(0, os.path.join(a.export, "tools/audit/round9/D0/s2"))
    import race  # noqa: E402  the finder's own grid and capture
    import numpy as np  # noqa: E402

    M = race.M
    frs: list[float | None] = [
        None if f == "none" else float(f) for f in a.fractions.split(",")
    ]
    rows = []
    for pp in a.cells.split(","):
        for wp in a.weather.split(","):
            for tz in (False, True):
                for dhw in (False, True):
                    cell = (f"{'two' if tz else 'one'}|"
                            f"{'dhw' if dhw else 'nodhw'}|{pp}|{wp}|"
                            f"h{a.horizon}")
                    for fr in frs:
                        f0, cpu, ncand = solve(M, race, np, tz, pp, wp, dhw,
                                               a.horizon, fr)
                        rows.append((cell, fr, f0, cpu, ncand))
                        print(f"{cell:44s} fr={fr!s:5s} f0={f0:.5f} "
                              f"cpu_s={cpu:.2f} n_cand={ncand}", flush=True)
    base = {(c, ): (f, s) for c, fr, f, s, _ in rows if fr is None}
    for fr in frs:
        if fr is None:
            continue
        sel = [(c, f, s) for c, f2, f, s, _ in rows if f2 == fr]
        d = [base[(c,)][0] - f for c, f, _ in sel]
        cpu = [s / base[(c,)][1] for c, _, s in sel]
        print(f"RESULT fr={fr} cells={len(sel)} count")
        print(f"RESULT fr={fr} obj_gain_sum={sum(d):.4f} sek_per_day")
        print(f"RESULT fr={fr} obj_gain_mean={sum(d)/len(d):.4f} sek_per_day")
        print(f"RESULT fr={fr} obj_gain_max={max(d):.4f} sek_per_day")
        print(f"RESULT fr={fr} obj_gain_worse={sum(1 for x in d if x < 0)} count")
        print(f"RESULT fr={fr} obj_gain_zero={sum(1 for x in d if x == 0.0)} count")
        print(f"RESULT fr={fr} cpu_ratio_mean={sum(cpu)/len(cpu):.4f} ratio")
        print(f"RESULT fr={fr} cpu_ratio_max={max(cpu):.4f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


def solve(M, race, np, tz, pp, wp, dhw, horizon, fr):
    """One cell, one arm: the first seam call's f0 and the solve's CPU."""
    o, _m, pr, ot, wi, ra, so, st = race.inputs(tz, pp, wp, dhw, horizon)
    first: dict = {}
    real_ms = M._multi_start_minimize

    def rec(objective, candidates, bounds, *args, **kw):
        cands = list(candidates)
        if fr is not None:
            ub = np.array(bounds, float)[:, 1]
            prs = race.obj_prices({"objective": objective})
            cands = cands + [np.minimum(
                M._price_ranked_start(
                    prs, float(ub.sum() * race.DT) * fr, float(ub.max()),
                    race.DT),
                ub,
            )]
        res = real_ms(objective, cands, bounds, *args, **kw)
        if not first:
            first.update(objective=objective, args=kw.get("args", args),
                         x=np.asarray(res.x, float).copy(), n=len(cands))
        return res

    t0 = time.process_time()
    with mock.patch.object(M, "_multi_start_minimize", rec):
        o.optimize(st, pr, ot, wi, ra, so, race.START)
    cpu = time.process_time() - t0
    f0 = float(first["objective"](first["x"], *first["args"]))
    return f0, cpu, first["n"]


if __name__ == "__main__":
    raise SystemExit(main())
