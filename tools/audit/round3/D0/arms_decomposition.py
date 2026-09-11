"""D0-01 attribution harness: WHICH part of a harder search recovers the gap.

METRIC (one line): the same objective gap as ``seed_race.py`` -- (production
objective_value - arm objective_value)/|production objective_value| in percent
-- measured separately for four arms that each change exactly one thing about
the search and nothing about the objective, the bounds, the args or the jac
path: (1) maxiter x10, (2) five extra constant-power starting points,
(3) a restart of L-BFGS-B from production's own answer ("polish"), (4) all
three together. Also runs the DHW/space co-optimisation pass to a fixed point
instead of production's single pass.

COMMAND (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D0/arms_decomposition.py

EXPECTED (baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, 8-core Apple M1,
python 3.11.5 / numpy 2.4.6 / scipy 1.17.1, OpenBLAS threads pinned to 1):
    cells                     = 8
    arm_maxiter_x10_max_pct   = 0.0000 +/- 0.001  (the budget is never the
                                mechanism, in any cell)
    arm_extra_seeds_max_pct   = 1.0430 +/- 0.15   (seeding is the mechanism in
                                6 of the 8 cells)
    arm_extra_seeds_mean_pct  = 0.3909 +/- 0.08
    arm_polish_max_pct        = 1.1703 +/- 0.20   (a plain RESTART from the
                                solver's own answer, no new seed and no bigger
                                budget, is the mechanism in summer_negative)
    arm_polish_mean_pct       = 0.1489 +/- 0.05
    arm_all_max_pct           = 1.0430 +/- 0.15
    coopt_fixpoint_max_pct    = 0.0000 (exact -- the second pass never adopts)
    coopt_extra_passes_adopted = 0     (exact)

INSTRUMENTED SYMBOL: heatpump_optimizer.optimizer:_multi_start_minimize
(replaced per arm) and heatpump_optimizer.optimizer:HeatPumpOptimizer.
_co_optimize (wrapped into a fixed-point loop for the last arm).

PERTURBATION (the judge runs it): D0_ARMS_SEEDS_OFF=1 empties the extra-seed
arm's level list; ``arm_extra_seeds_max_pct`` must then collapse to 0.0000 and
``arm_all_max_pct`` to ``arm_polish_max_pct``, because the "all" arm still
carries the restart. Direction: removing the seeds removes the seed arm's gap
and leaves the restart arm untouched.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round3", "D0"))
import d0lib as L  # noqa: E402
import numpy as np  # noqa: E402
from unittest import mock  # noqa: E402
from heatpump_optimizer.optimizer import HeatPumpOptimizer as HPO  # noqa: E402

LEVELS = () if os.environ.get("D0_ARMS_SEEDS_OFF") else (0.0, 0.25, 0.5, 0.75, 1.0)

CELLS = (("winter_typical", True, False), ("flat", True, False),
         ("winter_extreme", True, False), ("shoulder", False, False),
         ("summer_negative", False, False), ("winter_narrow", True, False),
         ("winter_typical", False, True), ("flat", True, True))

ARMS = (
    ("maxiter_x10", dict(maxiter_mul=10, extra_seed_levels=(), polish=False)),
    ("extra_seeds", dict(maxiter_mul=1, extra_seed_levels=LEVELS, polish=False)),
    ("polish", dict(maxiter_mul=1, extra_seed_levels=(), polish=True)),
    ("all", dict(maxiter_mul=10, extra_seed_levels=LEVELS, polish=True)),
)

_ORIG_COOPT = HPO._co_optimize
COOPT = {"passes": 0, "adopted": 0}


def looped_coopt(self, h, *, space_power, dhw_power, status, best_score,
                 solve_space, p_max):
    """Run production's own co-optimisation pass to a fixed point."""
    sp, dp, st, score = space_power, dhw_power, status, best_score
    for _ in range(8):
        sp2, dp2, st2 = _ORIG_COOPT(self, h, space_power=sp, dhw_power=dp,
                                    status=st, best_score=score,
                                    solve_space=solve_space, p_max=p_max)
        COOPT["passes"] += 1
        if np.allclose(sp2, sp, atol=1e-9) and np.allclose(dp2, dp, atol=1e-9):
            break
        COOPT["adopted"] += 1
        sp, dp, st = sp2, dp2, st2
        sp, st, score = solve_space(dp, sp)
    return sp, dp, st


def main():
    res = {name: [] for name, _ in ARMS}
    coopt_gaps = []
    for price_p, tz, dhw in CELLS:
        opt, m, a, st = L.build(price_p, "winter_cold", two_zone=tz, dhw=dhw)
        prod = opt.optimize(*a)
        o0 = float(prod.objective_value)
        line = [f"CELL {price_p:16s} tz={tz:d} dhw={dhw:d} prod={o0:11.5f}"]
        for name, kw in ARMS:
            o2, m2, a2, s2 = L.build(price_p, "winter_cold", two_zone=tz, dhw=dhw)
            with L.solver(L.stronger(**kw)):
                r = o2.optimize(*a2)
            g = (o0 - float(r.objective_value)) / abs(o0) * 100.0
            res[name].append(g)
            line.append(f"{name}={g:+.4f}%")
        if dhw:
            COOPT["passes"] = COOPT["adopted"] = 0
            o3, m3, a3, s3 = L.build(price_p, "winter_cold", two_zone=tz, dhw=dhw)
            with mock.patch.object(HPO, "_co_optimize", looped_coopt):
                r3 = o3.optimize(*a3)
            g = (o0 - float(r3.objective_value)) / abs(o0) * 100.0
            coopt_gaps.append(g)
            line.append(f"coopt_fixpoint={g:+.4f}% "
                        f"(passes={COOPT['passes']} adopted={COOPT['adopted']})")
        print("  ".join(line), flush=True)
    for name, _ in ARMS:
        v = np.array(res[name])
        print(f"RESULT arm_{name}_max_pct={v.max():.4f} percent")
        print(f"RESULT arm_{name}_mean_pct={v.mean():.4f} percent")
    c = np.array(coopt_gaps) if coopt_gaps else np.array([0.0])
    print(f"RESULT coopt_fixpoint_max_pct={c.max():.4f} percent")
    print(f"RESULT coopt_extra_passes_adopted={COOPT['adopted']} count")
    print(f"RESULT cells={len(CELLS)} count")
    L.print_env()


if __name__ == "__main__":
    main()
