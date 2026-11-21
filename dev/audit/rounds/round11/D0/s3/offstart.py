"""D0-s3 offstart: production's multi-start has no all-off start, and on a
storage plant at negative prices it ships a plan its own objective scores worse
than the plan L-BFGS-B reaches from "off" (round 11 D0-s3, baseline 92d38ecb,
box B3).

Metric (one line): per cell, gap_off = J(shipped) - J(off-arm), both on the
true objective `_commit_runs` scores the shipped plan with, where the off-arm is
production's own `_multi_start_minimize` run from the lower-bound vector alone
(same descent objective, bounds, args, maxiter, continuation) and committed
through production's `_commit_runs`; read on the call whose plan ships.
Key: the true-objective value the production seam delivers (`_commit_runs`'
scope objective at the committed plan), never an input attribute. Comfort is
read beside it: degree-steps above the ceiling on the model's own trajectory
(`ThermalModel.simulate_trajectory`) for the shipped and the off-arm plan.

Cells: the d0-grid lines (`python3 tools/audit/enumerate.py d0-grid`) with
price summer_negative and weather summer_warm (60: the house sits above its
ceiling and the price pays to run), and their flat-price twins (60) as the
null control (D0.M5): at a flat positive price nothing pays the pump to run, so
gap_off must vanish there.

Command (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D0/s3/offstart.py [--workers 2] [--perturb off_in_prod] [--cells FILE]
Perturbation: --perturb off_in_prod appends the lower-bound (all-off) vector to
the candidate list of every production `_multi_start_minimize` call (in memory,
the Capture wrapper): gap_off must fall to <= 1e-4 on every cell (count of gap
cells moves to_zero), the shipped plan's ceiling breach down.
Expected (unperturbed): see REPORT.md, finding D0-s3-02. Counts and objective
values are contention-immune; CPU is provisional.
Machine: box B3 (4 cores shared by three seats).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import json
import time
import argparse
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402

GAP_EPS = 1e-4


def universe():
    out = subprocess.run([sys.executable, "tools/audit/enumerate.py", "d0-grid"], capture_output=True,
                         text=True, check=True).stdout.split()
    base = [c for c in out if c.startswith("summer_negative/summer_warm/")]
    return base + ["flat/" + c.split("/", 1)[1] for c in base]


def one(args):
    cell, perturb = args
    import d0s3_lib as L
    t0 = time.process_time(); tt0 = time.thread_time()
    try:
        b = L.build(cell)

        def off(call):
            return [np.array([q[0] for q in call.bounds], dtype=float)]
        r, calls, cpu, _ = L.solve(b, extra_seeds=off if perturb == "off_in_prod" else None)
        ship = np.asarray(r.power_schedule, dtype=float)
        rows = [c for c in calls if c.commit is not None]
        shipped = [c for c in rows if np.allclose(L.shipped_of(c)[0][: ship.size], ship[: L.shipped_of(c)[0].size],
                                                  atol=1e-6) and L.shipped_of(c)[0].size == ship.size]
        c = shipped[-1] if shipped else rows[-1]
        px, ps = L.shipped_of(c)
        lo = np.array([q[0] for q in c.bounds], dtype=float)
        ox, os_ = L.committed(c, L.run_ms(c, [lo]).x)
        pb, ob = L.comfort_breach(c, px), L.comfort_breach(c, ox)
        return {"cell": cell, "perturb": perturb or "", "J_shipped": ps, "J_off": os_, "gap_off": ps - os_,
                "rel_gap": (ps - os_) / abs(ps) if ps else 0.0,
                "shipped_kwh": float(np.sum(px) * 0.25), "off_kwh": float(np.sum(ox) * 0.25),
                "energy_shipped": L.energy_cost(c, px), "energy_off": L.energy_cost(c, ox),
                "above_ceiling_shipped": pb[1], "above_ceiling_off": ob[1],
                "below_floor_shipped": pb[0], "below_floor_off": ob[0],
                "from_shipped_call": bool(shipped), "prod_cpu": round(cpu, 3),
                "cell_cpu": round(time.process_time() - t0, 3), "cell_thread_cpu": round(time.thread_time() - tt0, 3)}
    except Exception as e:  # noqa: BLE001
        import traceback
        return {"cell": cell, "error": f"{type(e).__name__}: {e}", "tb": traceback.format_exc()[-1500:]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--perturb", default="")
    ap.add_argument("--cells", default="")
    a = ap.parse_args()
    cells = [l.strip() for l in open(a.cells) if l.strip()] if a.cells else universe()
    path = os.path.join(HERE, "offstart_out", f"cells{('.' + a.perturb) if a.perturb else ''}.jsonl")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    done = set()
    if os.path.exists(path):
        done = {json.loads(l)["cell"] for l in open(path) if "error" not in json.loads(l)}
    todo = [c for c in cells if c not in done]
    from multiprocessing import get_context
    with open(path, "a") as fh, get_context("fork").Pool(a.workers) as pool:
        for i, rec in enumerate(pool.imap_unordered(one, [(c, a.perturb) for c in todo])):
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            print(f"[{i + 1}/{len(todo)}] {rec['cell']} gap_off={rec.get('gap_off', rec.get('error'))}", flush=True)
    summarize(path, cells)


def summarize(path, cells):
    import d0s3_lib as L
    recs = {}
    for line in open(path):
        d = json.loads(line)
        if "error" not in d:
            recs[d["cell"]] = d
    R = [recs[c] for c in cells if c in recs]
    print(f"RESULT universe={len(cells)} cells examined={len(R)}")
    for arm in ("summer_negative", "flat"):
        sub = [r for r in R if r["cell"].startswith(arm + "/")]
        if not sub:
            continue
        g = np.array([r["gap_off"] for r in sub])
        rel = np.array([r["rel_gap"] for r in sub])
        pos = g > GAP_EPS
        srt = np.sort(g)
        print(f"RESULT {arm}_gap_cells={int(pos.sum())}/{len(sub)} (gap_off > {GAP_EPS})")
        print(f"RESULT {arm}_gap_off: min={g.min():.4f} max={g.max():.4f} mean={g.mean():.4f} "
              f"drop_most_favourable_mean={(srt[:-1].mean() if len(g) > 1 else float('nan')):.4f} objective units")
        print(f"RESULT {arm}_rel_gap: max={rel.max():.4f} mean_over_gap_cells={(rel[pos].mean() if pos.any() else 0):.4f}")
        if pos.any():
            dce = np.array([r["above_ceiling_shipped"] - r["above_ceiling_off"] for r in sub])[pos]
            de = np.array([r["energy_off"] - r["energy_shipped"] for r in sub])[pos]
            print(f"RESULT {arm}_gap_cells_extra_ceiling_degree_steps: mean={dce.mean():.3f} max={dce.max():.3f}")
            print(f"RESULT {arm}_gap_cells_energy_saved_by_shipping_SEK: mean={de.mean():.3f} max={de.max():.3f}")
            plants = {}
            for r in sub:
                if r["gap_off"] > GAP_EPS:
                    p = r["cell"].split("/")[4]
                    plants[p] = plants.get(p, 0) + 1
            print(f"RESULT {arm}_gap_cells_by_plant={json.dumps(plants, sort_keys=True)}")
    pc = sum(r.get("cell_cpu", 0) for r in R); tc = sum(r.get("cell_thread_cpu", 0) for r in R)
    print(f"RESULT cpu_total_s={pc:.1f} provisional")
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={L.load1():.2f}")
    print(f"RESULT swapins={L.swapins()}")


if __name__ == "__main__":
    main()
