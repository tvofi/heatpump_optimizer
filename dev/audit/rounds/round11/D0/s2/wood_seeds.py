"""D0-s2 wood seed collapse (round 11): a charged wood tank zeroes the space-only multi-start's structured starts.

Mechanism measured: HeatPumpOptimizer's space-only solve scales its seed by (1 - _wood_covered_share(...)); a
two-tank (wood) house whose tank covers the thermostat reference gets share 1.0, so seed_power, baseline_energy
and every _price_ranked_start built from it are all-zero vectors; the multi-start then holds one live start
(the price-weighted guess) and on mild days ships the all-off plan that a one-run challenger beats.
Metrics (one line each):
  zero_starts   = candidates with sum(x) == 0 among the candidates of the space-only _multi_start_minimize call
                  (the call with no DHW args), per cell, counted on what production hands the multi-start.
  gap_abs       = race.py's J_prod - J_best feasible challenger (production objective units), per cell.
Count key: the candidate vectors production passes to _multi_start_minimize; the shipped OptimizationResult.
Universe (--census): every two-zone/no-dhw/wood line of enum_cells.py (the space-only wood path in this seat's
  cells: 4 prices x 5 weathers x 3 horizons = 60); --race CELLS races the named cells (the gap cells).
Instrumented symbol: custom_components.heatpump_optimizer.optimizer:_wood_covered_share (patched under the
  perturbation), optimizer:_multi_start_minimize (wrapped, candidates counted), HeatPumpOptimizer.optimize.
Perturbation: WOOD_SHARE_OFF=1 patches optimizer._wood_covered_share to return 0.0 (the one-line production edit
  "seed from the reference unscaled"): zero_starts must go DOWN (to 0 on the cells where only the share zeroed
  them) and gap_abs must go DOWN on the zero-plan cells.
Null control: --price flat on the race (the collapse is price-independent: the gap is expected to SURVIVE flat,
  which is why it is named solver structure, not price optimality).
Command: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D0/s2/wood_seeds.py \
           --census | --race CELL [CELL ...] [--price flat]      (prefix WOOD_SHARE_OFF=1 for the perturbation)
Expected (92d38ecb, box B2): see results/wood_seeds*.txt; tolerance exact for counts, +-0.01 for gap_abs.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box B2, 4 vCPU, shared.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
import argparse
import subprocess
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cells  # noqa: E402
import race  # noqa: E402
import numpy as np  # noqa: E402
import heatpump_optimizer.optimizer as om  # noqa: E402

REAL_MS = om._multi_start_minimize


def census_cell(line):
    rec, _ = cells.cell_record(line)
    seen = []

    def wrapped(objective, candidates, bounds, args=(), *a, **k):
        if not args:  # the space-only call
            seen.append(sum(1 for c in candidates if float(np.sum(np.asarray(c, float))) == 0.0))
            seen.append(len(candidates))
        return REAL_MS(objective, candidates, bounds, args, *a, **k)

    with mock.patch.object(om, "_multi_start_minimize", wrapped):
        res = rec.optimizer().optimize(inputs=rec.inputs)
    kwh = float(np.sum(res.power_schedule) * rec.config.dt_hours)
    return (seen[0], seen[1], kwh) if seen else (None, None, kwh)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--census", action="store_true")
    ap.add_argument("--race", nargs="*")
    ap.add_argument("--price")
    a = ap.parse_args()
    off = os.environ.get("WOOD_SHARE_OFF") == "1"
    patch = mock.patch.object(om, "_wood_covered_share", lambda *x, **k: 0.0) if off else \
        mock.patch.object(om, "_wood_covered_share", om._wood_covered_share)
    tag = "off" if off else "prod"
    c0, t0 = time.process_time(), time.thread_time()
    with patch:
        if a.census:
            allc = subprocess.run([sys.executable, os.path.join(HERE, "enum_cells.py")], capture_output=True,
                                  text=True, check=True).stdout.split()
            lines = [l for l in allc if not l.startswith("coord/") and l.split("/")[2] == "two-zone"
                     and l.split("/")[3] == "no-dhw" and l.split("/")[4] == "wood"]
            tot = zc = collapsed = 0
            for l in lines:
                z, n, kwh = census_cell(l)
                print(f"RESULT zero_starts[{l}|{tag}]={z} of {n} kWh_shipped={kwh:.3f}", flush=True)
                tot += 1
                zc += (z or 0)
                collapsed += int(bool(n) and z is not None and z >= n - 1)
            print(f"RESULT census_cells={tot} cells")
            print(f"RESULT census_cells_all_but_one_start_zero[{tag}]={collapsed} cells")
            print(f"RESULT census_zero_starts_total[{tag}]={zc} starts")
        for l in a.race or []:
            r = race.race(l, a.price)
            p = r["arms"]["prod"]
            print(f"RESULT gap_abs[{l}|{a.price or 'cell'}|{tag}]={r['gap_abs']:.4f} J "
                  f"gap_pct={r['gap_pct']:.3f} prod_kWh={p['kwh']:.3f} best={r['best_arm']}", flush=True)
    pc, tc = time.process_time() - c0, time.thread_time() - t0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        for l in open("/proc/vmstat"):
            if l.startswith("pswpin"):
                sw = int(l.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
