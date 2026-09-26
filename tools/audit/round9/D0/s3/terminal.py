"""D0 round 9, seat D0-s3, step D0.M7(b): does the terminal credit change the plan the way its docstring claims?

HeatPumpOptimizer._terminal_cost's docstring: without it "the optimizer always
dumps the last couple of hours: it coasts the house down because the resulting
cold never appears in the objective". The honest reference for what the last
hours of a 24 h plan SHOULD buy is a plan that can see past them: the 48 h
plan on the same tiled profiles, same initial state.

Metric (per cell): tail_ratio = E24[20-24 h] / E48[20-24 h], E the planned
electrical energy (space + DHW, kWh) in hours 20-24 of the plan; and
end_gap = stored-heat proxy: room/zone end temperature of the 24 h plan minus
the 48 h plan's temperature at hour 24 (K). Arms: prod (terminal credit on)
and --perturb noterm (HeatPumpOptimizer._terminal_cost returns zero closures).
A credit that works puts tail_ratio near 1 and end_gap near 0; noterm is the
docstring's counterfactual and must push tail_ratio down.
Count key: the power schedules HeatPumpOptimizer.optimize delivers.

Command (from the export root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    /home/claude/venv314/bin/python tools/audit/round9/D0/s3/terminal.py \
    [--topo one,two] [--dhw 0,1] [--prices ...] [--weather ...] [--perturb noterm]
Expected values: see REPORT.md (baseline 1936d5ca, B3 container).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from race import build, START, PRICES
from profiles import DT
from heatpump_optimizer.optimizer import HeatPumpOptimizer

ORIG_TC = HeatPumpOptimizer._terminal_cost


def _zero_tc(self, prices, outdoor_temps, solar_gains=None, humidity=None):
    def cost(*a, **k):
        return 0.0

    def batch(traj):
        return np.zeros(traj["room"].shape[0])
    return cost, batch


def plan(tz, dhw, pp, wp, hh, perturb):
    o, m, oc, st, pr, ot, wi, ra, so = build(tz, dhw, pp, wp, horizon_h=hh)
    if perturb == "noterm":
        HeatPumpOptimizer._terminal_cost = _zero_tc
    try:
        r = o.optimize(st, pr, ot, wi, ra, so, START)
    finally:
        HeatPumpOptimizer._terminal_cost = ORIG_TC
    sp = np.asarray(r.power_schedule, float)
    dp = np.asarray(r.dhw_power_schedule, float) if r.dhw_power_schedule else 0 * sp
    if r.upper_temp_trajectory:
        room = np.minimum(np.asarray(r.upper_temp_trajectory), np.asarray(r.lower_temp_trajectory))
    else:
        room = np.asarray(r.room_temp_trajectory)
    return sp + dp, room, np.asarray(r.slab_temp_trajectory)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topo", default="one,two")
    ap.add_argument("--dhw", default="0,1")
    ap.add_argument("--prices", default="winter_typical,winter_extreme,winter_moderate,shoulder,summer_negative,flat")
    ap.add_argument("--weather", default="winter_cold,shoulder")
    ap.add_argument("--perturb", default="")
    a = ap.parse_args()
    a0, a1 = int(20 / DT), int(24 / DT)
    ratios_p, ratios_f = [], []
    for t in a.topo.split(","):
        for d in a.dhw.split(","):
            for pp in a.prices.split(","):
                for wp in a.weather.split(","):
                    tz, dhw = t == "two", int(d)
                    p24, r24, s24 = plan(tz, dhw, pp, wp, 24, a.perturb)
                    p48, r48, s48 = plan(tz, dhw, pp, wp, 48, "")
                    e24 = float(p24[a0:a1].sum() * DT)
                    e48 = float(p48[a0:a1].sum() * DT)
                    ratio = e24 / e48 if e48 > 1e-6 else float("nan")
                    end_room = float(r24[-1] - r48[a1 if len(r48) > a1 else a1 - 1])
                    end_slab = float(s24[-1] - s48[a1 if len(s48) > a1 else a1 - 1])
                    (ratios_f if pp == "flat" else ratios_p).append(ratio)
                    print(f"{t}|{d}|{pp}|{wp:<12} E24tail {e24:6.2f} kWh  E48tail {e48:6.2f} kWh  "
                          f"ratio {ratio:6.3f}  end_room {end_room:+.2f} K  end_slab {end_slab:+.2f} K",
                          flush=True)
    rp = np.array([x for x in ratios_p if np.isfinite(x)])
    rf = np.array([x for x in ratios_f if np.isfinite(x)])
    if len(rp):
        print(f"RESULT tail_ratio_mean_priced={rp.mean():.4f}")
        print(f"RESULT tail_ratio_min_priced={rp.min():.4f}")
        print(f"RESULT tail_ratio_max_priced={rp.max():.4f}")
        print(f"RESULT tail_ratio_cells_priced={len(rp)}")
    if len(rf):
        print(f"RESULT tail_ratio_mean_flat={rf.mean():.4f}")
    print(f"RESULT thread_factor={time.process_time()/max(time.thread_time(),1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


if __name__ == "__main__":
    main()
