"""D0-s2 aggregate (round 11): M4 gaps per cell, M5 flat null per cell, leave-one-out, plant properties.

Reads results/m4_shard*.jsonl and results/m5_flat.jsonl that race.py wrote (every number here is a
race.py number; this script only aggregates), and results/m6_*.jsonl that mpc.py wrote.
Metric definitions:
  gap_pct            race.py's: 100*(J_prod - J_best feasible challenger)/|J_prod|, production objective
  price_gap_pct      gap_pct(cell) - gap_pct(the cell's flat counterpart), the part a price spread explains
  a "gap cell"       gap_pct > TOL (0.05 pct-points, the BLAS tolerance race.py states)
  survives_flat      the flat counterpart's gap_pct > TOL as well
  fsp_above_min      flow-setpoint-behind-valve: share of on-steps (space > 0.05 kW) planned above
                     min_electrical_power + 0.05 kW (the plan leaves the minimum level)
  mvb_differs        manual-valve-buffer: L1 distance (kWh) between its shipped space plan and the plain
                     cell's (same price/weather/zones/DHW/horizon)
Command: python3 dev/audit/rounds/round11/D0/s2/analyse.py   (no solver; numpy only)
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
"""
import glob
import json
import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
TOL = 0.05
PMIN = 1.0  # tests/profiles.py:house heat_pump_min_power


def load(pattern):
    out = {}
    for f in sorted(glob.glob(os.path.join(RES, pattern))):
        for l in open(f):
            try:
                r = json.loads(l)
            except ValueError:
                continue
            out[r["cell"]] = r
    return out


def flat_of(cell):
    p = cell.split("/")
    return f"coord/{p[1]}/flat/{p[3]}" if cell.startswith("coord/") else "flat/" + "/".join(p[1:])


def loo(vals):
    v = np.asarray(sorted(vals), float)
    if v.size < 5:
        return None
    return {"cells": int(v.size), "min": float(v[0]), "max": float(v[-1]), "mean": float(v.mean()),
            "mean_drop_most_favourable": float(v[:-1].mean())}


def main():
    m4, m5 = load("m4_shard*.jsonl"), load("m5_flat.jsonl")
    universe = [l.strip() for l in open(os.path.join(RES, "m4_order.txt")) if l.strip()]
    ok4 = {c: r for c, r in m4.items() if "gap_pct" in r}
    err4 = {c: r for c, r in m4.items() if "error" in r}
    print(f"RESULT m4_examined={len(ok4)} cells  (errors {len(err4)}, universe {len(universe)})")
    gaps = {c: r["gap_pct"] for c, r in ok4.items()}
    gc = {c: g for c, g in gaps.items() if g > TOL}
    print(f"RESULT m4_gap_cells={len(gc)} cells")
    if gaps:
        print(f"RESULT m4_gap_max={max(gaps.values()):.4f} pct")
    m5ok = 0
    survive, price_gaps = 0, {}
    for c, g in gaps.items():
        f = m5.get(flat_of(c))
        if f and "gap_pct" in f:
            m5ok += 1
            price_gaps[c] = g - f["gap_pct"]
            if g > TOL and f["gap_pct"] > TOL:
                survive += 1
    print(f"RESULT m5_cells_with_null={m5ok} cells")
    print(f"RESULT m5_gap_cells_surviving_flat={survive} cells")
    pg = {c: v for c, v in price_gaps.items() if v > TOL and gaps[c] > TOL}
    print(f"RESULT m5_price_attributable_gap_cells={len(pg)} cells")
    # per-axis strata
    for k, name in enumerate(("price", "weather", "zones", "dhw", "plant", "horizon")):
        by = defaultdict(list)
        for c, g in gaps.items():
            if c.startswith("coord/"):
                key = "coord" if k != 0 else c.split("/")[2]
            else:
                key = c.split("/")[k]
            by[key].append(g)
        for key, v in sorted(by.items()):
            v = np.asarray(v)
            print(f"  {name:8s} {key:28s} n={v.size:4d} gap>tol={int((v > TOL).sum()):4d} "
                  f"mean={v.mean():.4f} max={v.max():.4f}")
    # leave-one-out over price x weather planes of the gap
    plane = defaultdict(list)
    for c, g in gaps.items():
        if not c.startswith("coord/"):
            plane["/".join(c.split("/")[:2])].append(g)
    means = {k: float(np.mean(v)) for k, v in plane.items()}
    lo = loo(list(means.values()))
    if lo:
        print(f"RESULT m4_plane_mean_gap_loo={json.dumps(lo)}")
    pgl = loo([v for v in price_gaps.values()])
    if pgl:
        print(f"RESULT m5_price_gap_loo={json.dumps(pgl)}")
    # top cells
    for c in sorted(gc, key=lambda c: -gc[c])[:25]:
        f = m5.get(flat_of(c), {})
        r = ok4[c]
        print(f"  TOP {c:70s} gap={gc[c]:.3f} flat={f.get('gap_pct', float('nan')):.3f} best={r['best_arm']} "
              f"dE={r['energy_gap_sek']:.2f}SEK E={r['arms']['prod']['energy_sek']:.1f} step0={r['step0_differs']}")
    # flow-setpoint property and manual-valve-buffer property
    fsp, mvb = [], []
    for c, r in ok4.items():
        if c.startswith("coord/"):
            continue
        p = c.split("/")
        plan = np.asarray(r["arms"]["prod"]["plan"])
        if p[4] == "flow-setpoint-behind-valve":
            on = plan > 0.05
            fsp.append((c, float((plan[on] > PMIN + 0.05).mean()) if on.any() else float("nan"),
                        float(plan.max())))
        if p[4] == "manual-valve-buffer":
            q = "/".join(p[:4] + ["plain", p[5]])
            if q in ok4:
                other = np.asarray(ok4[q]["arms"]["prod"]["plan"])
                mvb.append((c, float(np.abs(plan - other).sum() * 0.25)))
    if fsp:
        v = np.array([x[1] for x in fsp])
        print(f"RESULT fsp_cells={len(fsp)} cells")
        print(f"RESULT fsp_cells_never_above_min={int(np.sum(v == 0))} cells")
        print(f"RESULT fsp_above_min_share_mean={np.nanmean(v):.3f} ratio")
    if mvb:
        v = np.array([x[1] for x in mvb])
        print(f"RESULT mvb_pairs={len(mvb)} cells")
        print(f"RESULT mvb_identical_to_plain={int(np.sum(v < 1e-3))} cells")
        print(f"RESULT mvb_l1_kwh_median={np.median(v):.3f} kWh")
    # M6
    m6 = {}
    for f in sorted(glob.glob(os.path.join(RES, "m6_*.jsonl"))):
        for l in open(f):
            r = json.loads(l)
            m6[(r["cell"], r["days"], r["replan"], r["plant_error"], r["price_arm"])] = r
    if m6:
        rg = [r["realised_gap_pct"] for r in m6.values() if "realised_gap_pct" in r]
        print(f"RESULT m6_loops={len(m6)} loops (with realised gap {len(rg)})")
        if rg:
            print(f"RESULT m6_realised_gap_positive={int(np.sum(np.asarray(rg) > TOL))} loops")
        for k, r in sorted(m6.items()):
            print(f"  M6 {k} realised={r.get('realised_gap_pct', 'nan')} dE={r.get('realised_energy_gap_sek', 'nan')} "
                  f"ddef={r.get('deficit_delta', 'nan')} dstarts={r.get('starts_delta', 'nan')} err={r.get('error', '')[:80]}")
    # flow-setpoint-behind-valve against its flat null: does the plan leave the minimum level more where a
    # price spread exists?
    fsp_pairs = []
    for c, r in ok4.items():
        if c.startswith("coord/") or c.split("/")[4] != "flow-setpoint-behind-valve":
            continue
        f = m5.get(flat_of(c))
        if not f or "arms" not in f:
            continue
        def share(plan):
            plan = np.asarray(plan)
            on = plan > 0.05
            return float((plan[on] > PMIN + 0.05).mean()) if on.any() else float("nan")
        fsp_pairs.append((share(r["arms"]["prod"]["plan"]), share(f["arms"]["prod"]["plan"])))
    vs = lambda c: c.replace("flow-setpoint-behind-valve", "valve-storage")  # noqa: E731
    fpairs = [c for c in ok4 if not c.startswith("coord/") and c.split("/")[4] == "flow-setpoint-behind-valve"
              and vs(c) in ok4]
    ident = [c for c in fpairs if ok4[vs(c)]["arms"]["prod"]["plan"] == ok4[c]["arms"]["prod"]["plan"]]
    print(f"RESULT fsp_plan_identical_to_valve_storage={len(ident)} of {len(fpairs)} pairs")
    if fsp_pairs:
        v = np.array(fsp_pairs)
        ok = np.isfinite(v).all(axis=1)
        print(f"RESULT fsp_pairs_with_flat={int(ok.sum())} cells")
        print(f"RESULT fsp_above_min_share_cell_mean={np.mean(v[ok, 0]):.3f} ratio")
        print(f"RESULT fsp_above_min_share_flat_mean={np.mean(v[ok, 1]):.3f} ratio")
    # manual-valve-buffer against the same cell with the buffer below the store threshold (mvb_nobuffer.py)
    mv = load("mvb_cell.jsonl")
    mvok = [r for r in mv.values() if "l1_kwh" in r]
    if mvok:
        l1 = np.array([r["l1_kwh"] for r in mvok])
        print(f"RESULT mvb_nostore_cells={len(mvok)} cells (errors {len(mv) - len(mvok)})")
        print(f"RESULT mvb_nostore_identical={int(np.sum(l1 < 1e-3))} cells")
        heat = [r for r in mvok if r["store_kwh"] > 0.1]
        print(f"RESULT mvb_nostore_identical_with_heat={sum(1 for r in heat if r['l1_kwh'] < 1e-3)} of {len(heat)} cells")
        print(f"RESULT mvb_nostore_l1_median={np.median(l1):.3f} kWh")
    # M6 summary: day-1 realised gap over loops at plant == model, R16, its LOO
    if m6:
        base = [r for k, r in m6.items() if k[1] == 1.0 and k[2] == 16 and k[3] == 1.0 and k[4] == "cell"
                and "realised_gap_pct" in r]
        if base:
            v = [r["realised_gap_pct"] for r in base]
            print(f"RESULT m6_base_loops={len(base)} loops")
            print(f"RESULT m6_base_realised_gap_loo={json.dumps(loo(v))}")
            print(f"RESULT m6_base_realised_positive={sum(1 for x in v if x > TOL)} loops")
            print(f"RESULT m6_base_realised_negative={sum(1 for x in v if x < -TOL)} loops")
            print(f"RESULT m6_base_realised_energy_sek_sum={sum(r['realised_energy_gap_sek'] for r in base):.3f} SEK")
    missing = [c for c in universe if c not in ok4]
    print(f"RESULT m4_not_reached={len(missing)} cells")


if __name__ == "__main__":
    main()
