"""D0.M4 + D0.M5 race over D0-s3's cells (round 11, baseline 92d38ecb).

Metric: per cell, gap = production's true-objective score of the plan it ships
from each captured `optimizer._multi_start_minimize` call minus the best
committed challenger's score on the SAME captured objective, bounds and args
(objective units = SEK at price_weight 1), with comfort parity required
(challenger's degree-steps below the per-step floor and above the ceiling on
`ThermalModel.simulate_trajectory` no worse than production's + 1e-3).
Key: the score the production seam delivers (`_commit_runs`' scope objective at
the committed plan), never an input attribute.

Command (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D0/s3/race.py [--workers 2] [--limit N] [--cells FILE] [--perturb seeds_in_prod]
Enumerator: race.py --list (D0.M4); race.py --list | grep -E '^flat/|/flat$' (D0.M5).
Universe: `python3 tools/audit/enumerate.py d0-grid` lines whose price is in
summer_typical, summer_negative, shoulder, flat (1200), plus the five
tests/golden.py coordinator captures on those four prices (20, named
coord/<capture>/<price>).
Output: race_out/cells.jsonl (one JSON line per cell, resumable), RESULT lines.
Perturbation: --perturb seeds_in_prod appends the structured seeds to
production's own candidate list (in memory, `_multi_start_minimize` wrapper):
every seeds-arm gap must fall to <= 0 (gap count moves down).
Expected: see REPORT.md (counts are contention-immune; CPU numbers provisional).
Machine: box B3, 4 cores shared by three seats.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import json
import time
import random
import argparse
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402

PRICES = ("summer_typical", "summer_negative", "shoulder", "flat")
GAP_EPS = 1e-4  # objective units; a gap below this is solver noise


def universe():
    out = subprocess.run([sys.executable, "tools/audit/enumerate.py", "d0-grid"], capture_output=True,
                         text=True, check=True).stdout.split()
    grid = [c for c in out if c.split("/")[0] in PRICES]
    import d0s3_lib as L
    return grid + [f"coord/{n}/{p}" for n in L.COORD_NAMES for p in PRICES]


def one(cell, perturb=None):
    import d0s3_lib as L
    t0 = time.process_time(); tt0 = time.thread_time()
    rec = {"cell": cell}
    if cell.startswith("coord/"):
        _, n, p = cell.split("/")
        opt, inp = L.coord_record(n, p)
        b = None
    else:
        b = L.build(cell)
        opt, inp = b["optimizer"], L.inputs_of(b)
    extra = (lambda call: L.structured_seeds(call)) if perturb == "seeds_in_prod" else None
    r, calls, cpu, binding = L.solve(None, extra_seeds=extra, opt=opt, inputs=inp)
    rec.update(prod_cpu=round(cpu, 3), status=str(r.status), binding=binding, n_calls=len(calls))
    ship = np.asarray(r.power_schedule, dtype=float)
    dhw = np.asarray(r.dhw_power_schedule if r.dhw_power_schedule is not None else [], dtype=float)
    if dhw.size != ship.size:
        dhw = np.zeros_like(ship)
    pr = np.asarray(r.prices, dtype=float)[: ship.size]
    rec["plan_energy_cost"] = float(np.sum(pr * (ship + dhw[: ship.size])) * 0.25)
    rec["plan_energy_kwh"] = float(np.sum(ship + dhw[: ship.size]) * 0.25)
    rows = []
    for k, c in enumerate(calls):
        px, ps = L.shipped_of(c)
        R = L.race_call(c, binding=binding > 0)
        b_lo, b_hi = L.comfort_breach(c, px)
        best = None
        for name, (s, x) in R.arms.items():
            if not np.isfinite(s):
                continue
            lo, hi = L.comfort_breach(c, x)
            parity = (not np.isfinite(b_lo)) or (lo <= b_lo + 1e-3 and hi <= b_hi + 1e-3)
            if parity and (best is None or s < best[1]):
                best = (name, s, x, lo, hi)
        row = {"k": k, "n": len(c.bounds), "prod": ps,
               "arms": {n: R.prod - v[0] for n, v in R.arms.items() if np.isfinite(v[0])},
               "race_cpu": round(R.cpu, 3), "prod_breach": [b_lo, b_hi],
               "ships": bool(np.allclose(px[: ship.size], ship[: px.size], atol=1e-6)) if px.size == ship.size else False}
        if best is not None:
            name, s, x, lo, hi = best
            row.update(best_arm=name, gap=ps - s, best_breach=[lo, hi],
                       energy_prod=L.energy_cost(c, px), energy_best=L.energy_cost(c, x),
                       step0_prod=float(px[0]), step0_best=float(x[0]),
                       step0_differs=bool(abs(float(px[0]) - float(x[0])) > 1e-3),
                       best_x=[round(float(v), 6) for v in x])
        rows.append(row)
    rec["calls"] = rows
    shipped = [rw for rw in rows if rw["ships"]]
    pick = shipped[-1] if shipped else (max(rows, key=lambda rw: rw.get("gap", 0.0)) if rows else None)
    rec["cell_gap"] = pick.get("gap", 0.0) if pick else 0.0
    rec["cell_gap_from_shipped_call"] = bool(shipped)
    rec["max_call_gap"] = max((rw.get("gap", 0.0) for rw in rows), default=0.0)
    if b is not None:
        c = L.parse(cell)
        if c["plant"] == "manual-valve-buffer":
            b0 = L.build(cell, extra_cfg={"buffer_tank_volume": 0.0, "mixing_valve_mode": "none"})
            r0 = b0["optimizer"].optimize(inputs=L.inputs_of(b0))
            x0 = np.asarray(r0.power_schedule, dtype=float)
            rec["no_buffer_plan_l1_kwh"] = float(np.sum(np.abs(x0 - ship)) * 0.25)
            rec["no_buffer_energy_cost"] = float(np.sum(pr * x0) * 0.25)
        if c["plant"] == "flow-setpoint-behind-valve":
            pmin = float(opt.model.params.min_electrical_power)
            run = ship > 1e-6
            rec["flow_clamped"] = bool(opt.config.clamp_planned_levels)
            rec["flow_running_steps"] = int(run.sum())
            rec["flow_steps_above_min"] = int((ship > pmin * 1.02).sum())
            rec["flow_steps_sub_min"] = int(((ship > 1e-6) & (ship < pmin - 1e-6)).sum())
            tot = ship + dhw
            rec["flow_steps_total_sub_min"] = int(((tot > 1e-6) & (tot < pmin - 1e-6)).sum())
            rec["flow_steps_total_above_min"] = int((tot > pmin * 1.02).sum())
    rec["cell_cpu"] = round(time.process_time() - t0, 3)
    rec["cell_thread_cpu"] = round(time.thread_time() - tt0, 3)
    return rec


def _safe(args):
    cell, perturb = args
    try:
        return one(cell, perturb)
    except Exception as e:  # noqa: BLE001
        import traceback
        return {"cell": cell, "error": f"{type(e).__name__}: {e}", "tb": traceback.format_exc()[-1500:]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--cells", default="")
    ap.add_argument("--perturb", default="")
    ap.add_argument("--out", default=os.path.join(HERE, "race_out", "cells.jsonl"))
    a = ap.parse_args()
    cells = [l.strip() for l in open(a.cells)] if a.cells else universe()
    if a.perturb:
        a.out = a.out.replace(".jsonl", f".{a.perturb}.jsonl")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    done = set()
    if os.path.exists(a.out):
        for line in open(a.out):
            try:
                d = json.loads(line)
                if "error" not in d:
                    done.add(d["cell"])
            except ValueError:
                pass
    todo = [c for c in cells if c not in done]
    random.Random(11).shuffle(todo)
    if a.limit:
        todo = todo[: a.limit]
    t0 = time.process_time(); tt0 = time.thread_time()
    from multiprocessing import get_context
    with open(a.out, "a") as fh, get_context("fork").Pool(a.workers) as pool:
        for i, rec in enumerate(pool.imap_unordered(_safe, [(c, a.perturb or None) for c in todo])):
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            print(f"[{i + 1}/{len(todo)}] {rec['cell']} gap={rec.get('cell_gap', rec.get('error'))}", flush=True)
    summarize(a.out, cells)
    import d0s3_lib as L
    recs = [json.loads(l) for l in open(a.out)]
    pc = sum(r.get("cell_cpu", 0) for r in recs); tc = sum(r.get("cell_thread_cpu", 0) for r in recs)
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f} (worker process_cpu/thread_cpu over all cells)")
    print(f"RESULT load1={L.load1():.2f}")
    print(f"RESULT swapins={L.swapins()}")


def summarize(path, cells):
    recs = {}
    for line in open(path):
        d = json.loads(line)
        if "error" not in d:
            recs[d["cell"]] = d
    ex = [c for c in cells if c in recs]
    gaps = {c: recs[c]["cell_gap"] for c in ex}
    pos = {c: g for c, g in gaps.items() if g > GAP_EPS}
    print(f"RESULT universe={len(cells)} cells")
    print(f"RESULT examined={len(ex)} cells")
    print(f"RESULT gap_cells={len(pos)} cells (gap > {GAP_EPS} objective units)")
    for p in PRICES:
        sub = [c for c in ex if c.split("/")[0] == p or c.endswith('/' + p) and c.startswith("coord/")]
        sp = [c for c in sub if c in pos]
        mx = max((gaps[c] for c in sub), default=0.0)
        print(f"RESULT gap_cells_{p}={len(sp)}/{len(sub)} max_gap={mx:.5f}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        # D0.M4's enumerator (1220 lines); D0.M5's is this piped through grep for flat
        print("\n".join(universe()))
    elif len(sys.argv) > 1 and sys.argv[1] == "--summary":
        summarize(os.path.join(HERE, "race_out", "cells.jsonl"), universe())
    else:
        main()
