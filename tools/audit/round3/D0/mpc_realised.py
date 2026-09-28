"""D0-01 MPC control: is the one-shot objective gap realised in closed loop?

METRIC (one line): realised_cost_gap = (A - B)/A in percent, where A and B are
the realised electricity cost, sum(price*power)*dt, of one simulated 24 h day
driven receding-horizon (re-plan every 4 h against a 24 h horizon, only the
first 4 h of each plan executed, the state advanced through production's own
``HeatPumpOptimizer._replay_end_state``) with the shipped
``_multi_start_minimize`` (A) and with ``seed_race.py``'s strict-superset
challenger (B); realised comfort (degree-steps below 17.0 C) is reported for
both arms so a cheaper day bought below the floor is visible rather than scored.

COMMAND (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D0/mpc_realised.py

EXPECTED (baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, 8-core Apple M1,
python 3.11.5 / numpy 2.4.6 / scipy 1.17.1, OpenBLAS threads pinned to 1):
    three cells, each printing realised_cost_A, realised_cost_B, the gap,
    both arms' degree-steps below 17.0 C and whether the two arms executed an
    identical day. The claim is only that re-planning does NOT wash the
    difference out: cells_not_converged >= 1 of 3, i.e. at least one cell where
    the two arms do not execute the same day. Tolerance +/- 0.2 percentage
    points on any gap; the SIGN of the money is per cell and is not uniform,
    because the objective the solver minimises prices comfort as well as energy.

INSTRUMENTED SYMBOL: heatpump_optimizer.optimizer:_multi_start_minimize
(replaced for arm B only); heatpump_optimizer.optimizer:HeatPumpOptimizer.
_replay_end_state (driven to advance the plant between re-plans).

PERTURBATION (the judge runs it): D0_MPC_SAME_SOLVER=1 runs arm B with the
production solver too. Every gap must be exactly 0.0000 %, every realised
comfort figure identical and identical_day true everywhere -- the loop itself
is deterministic.
"""
import os
import sys
from datetime import timedelta

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round3", "D0"))
import d0lib as L  # noqa: E402
import numpy as np  # noqa: E402

DT = 0.25
HORIZON_STEPS = 96          # 24 h at 15 min
REPLAN_HOURS = 4.0
DAY_HOURS = 24.0
SAME = os.environ.get("D0_MPC_SAME_SOLVER") == "1"
LEVELS = (0.0, 0.25, 0.5, 0.75, 1.0)

CELLS = (("winter_typical", True), ("shoulder", False), ("flat", True))


def day(price_p, two_zone, challenger):
    # horizon_hours=48 only to get 192 tiled steps of price and weather to
    # slice from; the optimizer itself is given a 24 h config below.
    _, _, tiled, _ = L.build(price_p, "winter_cold", two_zone=two_zone,
                             dhw=False, horizon_hours=48)
    _, prices, ot, wi, ra, so, start = tiled
    opt, m, a, state = L.build(price_p, "winter_cold", two_zone=two_zone,
                               dhw=False, horizon_hours=24)
    state = a[0]
    per_tick = int(round(REPLAN_HOURS / DT))
    ticks = int(round(DAY_HOURS / REPLAN_HOURS))
    cost = below = 0.0
    powers = []
    for t in range(ticks):
        off = t * per_tick
        h = slice(off, off + HORIZON_STEPS)
        args = (state, prices[h], ot[h], wi[h], ra[h], so[h],
                start + timedelta(hours=t * REPLAN_HOURS))
        if challenger is None:
            res = opt.optimize(*args)
        else:
            with L.solver(challenger):
                res = opt.optimize(*args)
        p = np.asarray(res.power_schedule, dtype=float)[:per_tick]
        e = slice(off, off + per_tick)
        cost += float(np.sum(prices[e] * p) * DT)
        room, *_ = m.simulate_trajectory(state, p, ot[e], wi[e], ra[e], so[e], DT)
        below += float(np.maximum(0.0, 17.0 - np.asarray(room[1:])).sum())
        powers.append(p)
        state = opt._replay_end_state(state, p, ot[e], wi[e], ra[e], so[e], DT)
    return cost, below, np.concatenate(powers)


def main():
    gaps = []
    not_converged = 0
    for price_p, tz in CELLS:
        ca, ba, pa = day(price_p, tz, None)
        chal = None if SAME else L.stronger(maxiter_mul=1,
                                            extra_seed_levels=LEVELS,
                                            polish=False)
        cb, bb, pb = day(price_p, tz, chal)
        gap = (ca - cb) / ca * 100.0 if abs(ca) > 1e-9 else 0.0
        gaps.append(gap)
        same_day = bool(np.allclose(pa, pb, atol=1e-6))
        not_converged += 0 if same_day else 1
        print(f"CELL {price_p:16s} tz={tz:d} realised_cost_A={ca:9.4f} "
              f"realised_cost_B={cb:9.4f} gap={gap:+7.4f}%  below_A={ba:.4f} "
              f"below_B={bb:.4f}  identical_day={same_day}", flush=True)
        print(f"RESULT realised_cost_gap_{price_p}_tz{int(tz)}={gap:.4f} percent")
        print(f"RESULT realised_below_A_{price_p}_tz{int(tz)}={ba:.4f} degree_steps")
        print(f"RESULT realised_below_B_{price_p}_tz{int(tz)}={bb:.4f} degree_steps")
        print(f"RESULT identical_day_{price_p}_tz{int(tz)}={int(same_day)} bool")
    g = np.abs(np.array(gaps))
    print(f"RESULT cells_not_converged={not_converged}/{len(CELLS)} count")
    print(f"RESULT realised_gap_abs_max_pct={g.max():.4f} percent")
    L.print_env()


if __name__ == "__main__":
    main()
