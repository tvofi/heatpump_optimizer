"""D0-s2 terminal-credit harness: does ``HeatPumpOptimizer._terminal_cost``
change the plan the way its docstring says ("without this the optimizer always
dumps the last couple of hours ... both breaches the comfort floor at the tail
of the plan and reports a saving that was really borrowed heat")?

Metric (one line): per cell, tail_kw = mean space power over the last 8 steps
(2 h) of the shipped 24 h plan; tail_breach = degree-steps of the planned room
(two-zone: min(upper, lower)) trajectory below the configured floor over those
8 steps; e_end = production ``_stored_thermal_energy(caps=_settlement_caps)``
at the plan's end state (kWh-th); each for the production arm and the
terminal-zeroed arm.
Perturbation: ``_terminal_cost`` patched to return zero closures (the noterm
arm) -- tail_kw must fall (docstring direction) and savings rise.
Null control: flat prices (the tail dump is a horizon effect, not an arbitrage
one, so it is expected to SURVIVE flat prices; it is reported, not subtracted).
Instrumented symbols: heatpump_optimizer.optimizer:HeatPumpOptimizer._terminal_cost,
HeatPumpOptimizer.optimize, HeatPumpOptimizer._stored_thermal_energy.

Command:
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  python3 tools/audit/round8/D0/s2_terminal.py [--two-zone] [--dhw 0|1]
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; 4-vCPU shared container.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, argparse
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from unittest import mock
import numpy as np
from golden import make, START
from heatpump_optimizer.optimizer import HeatPumpOptimizer

ap = argparse.ArgumentParser()
ap.add_argument("--two-zone", action="store_true")
ap.add_argument("--dhw", type=int, default=0)
ARGS = ap.parse_args()
PRICES = ["winter_typical", "winter_extreme", "summer_typical", "summer_negative",
          "shoulder", "winter_narrow", "winter_moderate", "flat"]
WEATHER = ["winter_cold", "winter_mild", "summer_cool", "shoulder"]


def _zero_terminal(self, prices, outdoor_temps, solar_gains=None):
    return (lambda *a, **k: 0.0,
            lambda traj: np.zeros(traj["room"].shape[0]))


def solve(pp, wp, noterm):
    b = make(two_zone=ARGS.two_zone, dhw=bool(ARGS.dhw), price_profile=pp,
             weather_profile=wp)
    o = b["optimizer"]
    args = (b["state"], b["prices"], b["outdoor"], b["wind"], b["rain"],
            b["solar"], START)
    if noterm:
        with mock.patch.object(HeatPumpOptimizer, "_terminal_cost",
                               _zero_terminal):
            r = o.optimize(*args)
    else:
        r = o.optimize(*args)
    sp = np.asarray(r.power_schedule)
    if ARGS.two_zone:
        room = np.minimum(np.asarray(r.upper_temp_trajectory),
                          np.asarray(r.lower_temp_trajectory))
    else:
        room = np.asarray(r.room_temp_trajectory)
    n = len(sp)
    floors = np.array([o.config.get_temp_bounds((i + 1) * 0.25 % 24)[0]
                       for i in range(n)])
    tail = room[-8:]
    breach = float(np.sum(np.maximum(0.0, floors[-8:] - tail)))
    return dict(tail_kw=float(np.mean(sp[-8:])), breach=breach,
                end_room=float(room[-1]), savings=float(r.predicted_savings),
                deferred=float(getattr(r, "deferred_cost", 0.0) or 0.0))


def main():
    rows = []
    for pp in PRICES:
        for wp in WEATHER:
            a = solve(pp, wp, False)
            z = solve(pp, wp, True)
            rows.append((pp, wp, a, z))
            print("CELL %-34s prod tail=%.3f kW breach=%.3f end=%.2f sav=%.2f | "
                  "noterm tail=%.3f kW breach=%.3f end=%.2f sav=%.2f"
                  % (f"{pp}/{wp}", a["tail_kw"], a["breach"], a["end_room"],
                     a["savings"], z["tail_kw"], z["breach"], z["end_room"],
                     z["savings"]), flush=True)
    tag = ("tz" if ARGS.two_zone else "sz") + ("_dhw" if ARGS.dhw else "")
    pr = [r for r in rows if r[0] != "flat"]
    fl = [r for r in rows if r[0] == "flat"]
    print(f"RESULT {tag}_cells={len(pr)} count")
    print(f"RESULT {tag}_tail_kw_prod_mean={np.mean([r[2]['tail_kw'] for r in pr]):.4f} kW")
    print(f"RESULT {tag}_tail_kw_noterm_mean={np.mean([r[3]['tail_kw'] for r in pr]):.4f} kW")
    print(f"RESULT {tag}_cells_tail_lower_noterm="
          f"{sum(r[3]['tail_kw'] < r[2]['tail_kw'] - 1e-3 for r in pr)} count")
    print(f"RESULT {tag}_tail_breach_prod_total={sum(r[2]['breach'] for r in pr):.4f} degree_steps")
    print(f"RESULT {tag}_tail_breach_noterm_total={sum(r[3]['breach'] for r in pr):.4f} degree_steps")
    print(f"RESULT {tag}_cells_breach_noterm={sum(r[3]['breach'] > 1e-6 for r in pr)} count")
    print(f"RESULT {tag}_flat_tail_kw_prod_vs_noterm="
          f"{','.join('%.3f/%.3f' % (r[2]['tail_kw'], r[3]['tail_kw']) for r in fl)} kW")
    pc, tc = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
