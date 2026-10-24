"""D0 round 9, seat D0-s3, step D0.M7(a): does iterating DHW <-> space more than once change cost?

Metric: per DHW-enabled cell, gap = (J_prod - J_iter) / |J_prod| in %, J the
production objective (OptimizationResult.objective_value) of the shipped plan;
J_iter is the same field when HeatPumpOptimizer._co_optimize is wrapped to run
up to K rounds (each round is production's own _co_optimize, handed the
previous round's adopted space/DHW pair and that pair's own solve_space score)
instead of production's single round. Arm "free" runs production's round
first, then drops the `pinned` trigger: each later round re-plans DHW against the solved space profile
(HeatPumpOptimizer._build_dhw_requirements, space_demand = that profile) and
adopts it only when production's own solve_space scores it lower -- the same
adoption rule _co_optimize applies.
Counts per cell: rounds that triggered (pinned any / coil), rounds adopted.
Count key: J as the production objective returns it for the delivered plan.

Command (from the export root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    /home/claude/venv314/bin/python tools/audit/round9/D0/s3/decomp.py \
    [--k 5] [--topo one,two] [--prices ...] [--weather ...] [--arm iter|free]
Perturbation: --k 1 reproduces production exactly, so every gap must go to_zero.
Expected values: see REPORT.md (baseline 1936d5ca, B3 container).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from race import build, floor_violation, energy_cost, PRICES, WEATHER, START
from heatpump_optimizer.optimizer import HeatPumpOptimizer

ORIG_CO = HeatPumpOptimizer._co_optimize


def make_wrapper(k, arm, log):
    def wrapped(self, h, *, space_power, dhw_power, status, best_score,
                solve_space, p_max):
        rounds = []
        for i in range(k):
            seen = []

            def ss(d, w):
                r = solve_space(d, w)
                seen.append(r)
                return r

            if arm == "free" and i > 0:
                replanned = self._build_dhw_requirements(
                    initial_state=h.initial_state, prices=h.prices,
                    outdoor_temps=h.outdoor_temps, step_hours=h.step_hours,
                    n_steps=h.n_steps, dt=h.dt, p_max=p_max,
                    space_demand=np.asarray(space_power, float),
                    dhw_pins=h.dhw_pins,
                    p_run_cap=(float(np.min(h.power_caps_extra))
                               if h.power_caps_extra is not None else None),
                    step_weekdays=h.step_weekdays, holiday_flags=h.holiday_flags,
                    wood_temps=self._dhw_coil_wood_forecast(h, space_power),
                    humidity=h.humidity,
                ).schedule
                if np.allclose(replanned, dhw_power, atol=1e-4):
                    rounds.append("same")
                    break
                cs, cst, sc = ss(replanned, space_power)
                if sc < best_score - 1e-9:
                    space_power, dhw_power, status, best_score = cs, replanned, cst, sc
                    rounds.append("adopt")
                    continue
                rounds.append("reject")
                break
            s2, d2, st2 = ORIG_CO(self, h, space_power=space_power,
                                  dhw_power=dhw_power, status=status,
                                  best_score=best_score, solve_space=ss,
                                  p_max=p_max)
            if s2 is space_power and d2 is dhw_power:
                rounds.append("reject" if seen else "notrigger")
                if arm == "free":
                    continue
                break
            rounds.append("adopt")
            space_power, dhw_power, status = s2, d2, st2
            best_score = seen[-1][2]
        log.append(rounds)
        return space_power, dhw_power, status
    return wrapped


def run(tz, pp, wp, k, arm):
    o, m, oc, st, pr, ot, wi, ra, so = build(tz, 1, pp, wp)
    log = []
    HeatPumpOptimizer._co_optimize = make_wrapper(k, arm, log)
    try:
        r = o.optimize(st, pr, ot, wi, ra, so, START)
    finally:
        HeatPumpOptimizer._co_optimize = ORIG_CO
    return r, oc, log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--topo", default="one,two")
    ap.add_argument("--prices", default=",".join(PRICES))
    ap.add_argument("--weather", default="winter_cold,shoulder,summer_warm")
    ap.add_argument("--arm", default="iter")
    a = ap.parse_args()
    gaps_priced, gaps_flat, adopted_extra, n = [], [], 0, 0
    for t in a.topo.split(","):
        tz = t == "two"
        for pp in a.prices.split(","):
            for wp in a.weather.split(","):
                rp, oc, logp = run(tz, pp, wp, 1, "iter")
                rk, _, logk = run(tz, pp, wp, a.k, a.arm)
                jp, jk = float(rp.objective_value), float(rk.objective_value)
                gap = 100.0 * (jp - jk) / max(abs(jp), 1e-12)
                vp, vk = floor_violation(rp, oc), floor_violation(rk, oc)
                s0 = abs(rp.power_schedule[0] - rk.power_schedule[0]) + abs(
                    rp.dhw_power_schedule[0] - rk.dhw_power_schedule[0])
                extra = sum(x.count("adopt") for x in logk) - sum(x.count("adopt") for x in logp)
                adopted_extra += max(extra, 0)
                n += 1
                (gaps_flat if pp == "flat" else gaps_priced).append(gap)
                print(f"{t}|{pp}|{wp:<12} J {jp:9.4f} -> {jk:9.4f} gap {gap:8.4f}%  "
                      f"dE {energy_cost(rp)-energy_cost(rk):7.3f} SEK viol {vp:.3f}/{vk:.3f} "
                      f"step0 {s0:.3f}  prod {logp} k{a.k} {logk}", flush=True)
    gp, gf = np.array(gaps_priced or [0.0]), np.array(gaps_flat or [0.0])
    print(f"RESULT cells={n}")
    print(f"RESULT extra_rounds_adopted={adopted_extra}")
    print(f"RESULT gap_mean_priced={gp.mean():.4f} %")
    print(f"RESULT gap_max_priced={gp.max():.4f} %")
    print(f"RESULT gap_min_priced={gp.min():.4f} %")
    if len(gp) > 1:
        print(f"RESULT gap_mean_priced_drop_best={np.sort(gp)[:-1].mean():.4f} %")
    print(f"RESULT gap_mean_flat={gf.mean():.4f} %")
    print(f"RESULT thread_factor={time.process_time()/max(time.thread_time(),1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


if __name__ == "__main__":
    main()
