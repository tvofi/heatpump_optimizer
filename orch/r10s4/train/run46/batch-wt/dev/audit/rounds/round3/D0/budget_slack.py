"""D0 non-finding harness: is the solver's ITERATION BUDGET ever the binding
constraint, and is any scored starting point ever discarded unrefined?

METRIC (one line): for every production ``_multi_start_minimize`` call across
the grid, ``nit/maxiter`` of the returned result (how much of the iteration
budget the winning start consumed), the L-BFGS-B termination ``status``, and
``len(candidates) - _MULTI_START_SOLVES`` (how many scored starting points the
cap discards without refining them).

COMMAND (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D0/budget_slack.py

EXPECTED (baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, 8-core Apple M1,
python 3.11.5 / numpy 2.4.6 / scipy 1.17.1, OpenBLAS threads pinned to 1):
    solver_calls              = 39   +/- 0   (32 cells; the DHW cells that
                                     re-solve space in _co_optimize add 7)
    max_nit_over_maxiter      = 0.2350 +/- 0.05   (never near 1.0)
    mean_nit_over_maxiter     = 0.0609 +/- 0.02
    max_nit                   = 47   +/- 8
    calls_hitting_maxiter     = 0    (exact)
    candidates_discarded_max  = 0    (exact -- every call passes exactly
                                     _MULTI_START_SOLVES = 4 candidates or
                                     fewer, so the cap discards nothing)
    calls_on_batched_jac      = 39   (exact)
    status_histogram          = {0: 39}; termination_reasons =
                                {'CONVERGENCE': 39}

INSTRUMENTED SYMBOL: heatpump_optimizer.optimizer:_multi_start_minimize
(wrapped, pass-through) and heatpump_optimizer.optimizer:_MULTI_START_SOLVES
(read).

PERTURBATION (the judge runs it): D0_MAXITER_CUT=3 wraps the production
multi-start so ``maxiter`` is forced to 3 -- ``calls_hitting_maxiter`` must
then rise above 0 and ``max_nit_over_maxiter`` reach 1.0, proving the counter
is reading the real solver and not a constant.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round3", "D0"))
import d0lib as L  # noqa: E402
import numpy as np  # noqa: E402
from heatpump_optimizer import optimizer as OM  # noqa: E402

CUT = os.environ.get("D0_MAXITER_CUT")

PRICES = ("winter_typical", "winter_extreme", "summer_typical",
          "summer_negative", "shoulder", "winter_narrow",
          "winter_moderate", "flat")
CONFIGS = (("single", False, False), ("two_zone", True, False),
           ("single+dhw", False, True), ("two_zone+dhw", True, True))


def main():
    cap = L.Capture()
    if CUT:
        real = OM._multi_start_minimize

        def cut(objective, candidates, bounds, args=(), maxiter=300,
                batch_objective=None, fd_eps=1e-4):
            return real(objective, candidates, bounds, args=args,
                        maxiter=int(CUT), batch_objective=batch_objective,
                        fd_eps=fd_eps)
        OM._multi_start_minimize = cut
    for price_p in PRICES:
        for name, tz, dhw in CONFIGS:
            opt, m, a, st = L.build(price_p, "winter_cold", two_zone=tz, dhw=dhw)
            with cap.record():
                opt.optimize(*a)
    calls = cap.calls
    maxiter_used = int(CUT) if CUT else None
    ratio = np.array([c["nit"] / (maxiter_used or c["maxiter"]) for c in calls])
    hit = sum(1 for c in calls if c["nit"] >= (maxiter_used or c["maxiter"]))
    disc = max(len(c["candidates"]) - OM._MULTI_START_SOLVES for c in calls)
    print(f"RESULT solver_calls={len(calls)} count")
    print(f"RESULT max_nit_over_maxiter={ratio.max():.4f} fraction")
    print(f"RESULT mean_nit_over_maxiter={ratio.mean():.4f} fraction")
    print(f"RESULT max_nit={max(c['nit'] for c in calls)} iterations")
    print(f"RESULT calls_hitting_maxiter={hit} count")
    print(f"RESULT candidates_discarded_max={max(0, disc)} count")
    print(f"RESULT multi_start_solves={OM._MULTI_START_SOLVES} count")
    print(f"RESULT calls_on_batched_jac="
          f"{sum(1 for c in calls if c['batched'])} count")
    st = {}
    for c in calls:
        st[c["status"]] = st.get(c["status"], 0) + 1
    print(f"RESULT status_histogram={st} count")
    msgs = {}
    for c in calls:
        key = c["message"].split(":")[0]
        msgs[key] = msgs.get(key, 0) + 1
    print(f"RESULT termination_reasons={msgs} count")
    L.print_env()


if __name__ == "__main__":
    main()
