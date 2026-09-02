"""D0 race: production's plan vs challengers on the exact recorded objective.

Metric: per cell, gap = production objective - best comfort-parity challenger
objective (SEK over the horizon, same objective closure, same bounds/args),
where every challenger is production's own L-BFGS-B call re-issued from a
different start or with a different budget. Also: gap_restart = the gap
recovered by re-submitting production's answer to the identical L-BFGS-B
call (fresh curvature memory only), and prod_pg = max |projected gradient|
at production's answer (scipy's PGTOL quantity, default 1e-5).

Command (full 24 h grid, ~15-25 min CPU under the fan-out):
    PYTHONPATH=tests/hastub python tools/audit/round2/D0/race_grid.py
Subsets:
    ... race_grid.py --tz 1 --dhw 1            # two-zone DHW only (40 cells)
    ... race_grid.py --tz 0 --weather winter_cold --tag tariff15 \
        --opt '{"peak_price_per_kw":20.0,"peak_threshold_kw":6.0,"peak_window_minutes":15,"baseline_load_kw":1.0}'
                                              # the capacity tariff (golden capacity_tariff_15min) across 8 prices
    ... race_grid.py --tz 1 --dhw 0 --weather winter_cold --tag smalltank \
        --cfg '{"mixing_valve_mode":"manual","buffer_tank_volume":35.0,"buffer_max_temperature":70.0}' \
        --state '{"buffer_tank_temperature":32.0}'
                                              # golden valve_storage_small_tank across 8 prices (perturbation:
                                              # buffer_tank_volume 750.0 = golden valve_storage; expected gap -> 0)
    ... race_grid.py --price flat              # the null control (20 cells)
    ... race_grid.py --hours 48 --tz 1         # horizon cells
Perturbations (each is the equivalent of the one-line production edit named):
    D0_PERTURB=solves3   -> optimizer._MULTI_START_SOLVES = 3
                            (expected: tz gap DOWN, cells_with_gap DOWN)
    D0_PERTURB=ftol9     -> options["ftol"] = 1e-9 in _multi_start_minimize
                            (expected: gap_restart cells DOWN, prod_nit UP)
    D0_PERTURB=restart   -> _multi_start_minimize re-submits its best result
                            to the same call once (expected: gap_restart -> 0)

Expected on baseline c398fc8 (Apple M1, macOS, python 3.13, scipy 1.18.1):
    sz cells: cells_with_gap_sz = 0 (every arm ties production to 1e-6)
    tz cells: cells_with_gap_tz > 0; mean_gap_pct_tz around 0.5-1.5 %;
    restart_improves_tz > 0. Counts are exact and contention-immune; the CPU
    figure is provisional.

Instrumented symbols: heatpump_optimizer.optimizer:_multi_start_minimize
(recorded), heatpump_optimizer.optimizer:_scoped_minimize (re-issued),
heatpump_optimizer.thermal_model:ThermalModel.simulate_trajectory[_batch]
(counted). Writes only tools/audit/round2/D0/out/.
"""
from __future__ import annotations

import os

for _threads in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_threads, "1")

import argparse
import json
import sys
import time
from pathlib import Path
from unittest import mock

sys.path.insert(0, "tools/audit/round2/D0")

import numpy as np  # noqa: E402

import d0lib as L  # noqa: E402

OUT = Path("tools/audit/round2/D0/out")


def apply_perturbation(name: str | None):
    """Monkeypatch equivalents of the one-line production edits."""
    patches = []
    if not name:
        return patches
    if name == "solves3":
        patches.append(mock.patch.object(L.opt_mod, "_MULTI_START_SOLVES", 3))
    elif name == "ftol9":
        real = L.opt_mod._scoped_minimize

        def tight(*a, **kw):
            opts = dict(kw.get("options") or {})
            opts["ftol"] = 1e-9
            kw["options"] = opts
            return real(*a, **kw)

        patches.append(mock.patch.object(L.opt_mod, "_scoped_minimize", tight))
    elif name == "restart":
        real_ms = L.opt_mod._multi_start_minimize

        def restarting(objective, candidates, bounds, args=(), maxiter=300,
                       batch_objective=None, fd_eps=1e-4):
            res = real_ms(objective, candidates, bounds, args=args,
                          maxiter=maxiter, batch_objective=batch_objective,
                          fd_eps=fd_eps)
            again = real_ms(objective, [res.x], bounds, args=args,
                            maxiter=maxiter, batch_objective=batch_objective,
                            fd_eps=fd_eps)
            if float(objective(again.x, *args)) < float(objective(res.x, *args)):
                return again
            return res

        patches.append(mock.patch.object(L.opt_mod, "_multi_start_minimize", restarting))
    else:
        raise SystemExit(f"unknown D0_PERTURB {name!r}")
    for p in patches:
        p.start()
    return patches


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--price", default=None)
    ap.add_argument("--weather", default=None)
    ap.add_argument("--tz", default=None, help="0/1")
    ap.add_argument("--dhw", default=None, help="0/1")
    ap.add_argument("--hours", type=int, default=24)
    ap.add_argument("--random", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--tag", default="")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--opt", default=None, help="JSON OptimizationConfig overrides, e.g. a capacity tariff")
    ap.add_argument("--cfg", default=None, help="JSON house config overrides")
    ap.add_argument("--state", default=None, help="JSON ThermalState overrides")
    a = ap.parse_args()
    opt_over = json.loads(a.opt) if a.opt else None
    cfg_over = json.loads(a.cfg) if a.cfg else None
    state_over = json.loads(a.state) if a.state else None

    perturb = os.environ.get("D0_PERTURB") or None
    patches = apply_perturbation(perturb)
    OUT.mkdir(parents=True, exist_ok=True)

    cells = []
    for price in L.PRICE_PROFILES:
        if a.price and price != a.price:
            continue
        for wx in L.WEATHER_PROFILES:
            if a.weather and wx != a.weather:
                continue
            for tz in (False, True):
                if a.tz is not None and tz != bool(int(a.tz)):
                    continue
                for dhw in (True, False):
                    if a.dhw is not None and dhw != bool(int(a.dhw)):
                        continue
                    cells.append((price, wx, tz, dhw))
    if a.limit:
        cells = cells[: a.limit]

    rows = []
    clock = L.CpuClock()
    prod_cpu = 0.0
    t_wall = time.perf_counter()
    for price, wx, tz, dhw in cells:
        cell = L.build_cell(price, wx, two_zone=tz, dhw=dhw, hours=a.hours,
                            opt_overrides=opt_over, config_overrides=cfg_over,
                            state_overrides=state_over)
        with clock:
            t0 = time.process_time()
            with L.Recorder() as rec:
                res = cell.solve()
            prod_cpu += time.process_time() - t0
            call = rec.adopted_call(res)
            if call is None:
                print(f"  {cell.name}: no adopted call (status {res.status!r}); skipped")
                continue
            raced = L.race(
                cell, call, random_starts=a.random,
                include=("third", "restart", "budget", "seeds", "random", "polish"),
                bang_fracs=(0.6, 0.8, 1.0, 1.2),
            )
            row = L.summarize(cell, call, raced, verbose=not a.quiet)
        row.update({
            "price": price, "weather": wx, "tz": tz, "dhw": dhw,
            "hours": a.hours, "n_calls": len(rec.calls),
            "adopted_call": call.index,
            "sim_calls": rec.sim_calls, "sim_batch_rows": rec.sim_batch_rows,
            "status": res.status,
            "predicted_cost": float(res.predicted_cost),
            "baseline_cost": float(res.baseline_cost),
            "arms": {
                arm.name: {
                    "score": arm.score, "energy": arm.energy, "nit": arm.nit,
                    "nfev": arm.nfev, "under": arm.feas["under"],
                    "over": arm.feas["over"], "msg": arm.message,
                    "parity": L.parity_ok(raced["production"], arm),
                } for arm in raced["arms"]
            },
        })
        rows.append(row)
        if a.quiet:
            print(f"  {cell.name}: obj {row['prod_score']:.3f} gap {row['gap_feasible']:+.4f} "
                  f"({row['gap_feasible_pct']:.2f} %) restart {row['gap_restart']:+.4f} "
                  f"pg {row['prod_pg']:.2g} nit {row['prod_nit']} bill {row['prod_energy']:.2f}")
    wall = time.perf_counter() - t_wall

    for p in reversed(patches):
        p.stop()

    tag = a.tag or (perturb or "baseline")
    out_path = OUT / f"race_grid_{a.hours}h_{tag}.json"
    out_path.write_text(json.dumps({
        "baseline_sha": "c398fc84eec25fc44b60d74aae05b9a2da205884",
        "perturbation": perturb, "hours": a.hours, "rows": rows,
    }, indent=1, default=float))

    # ---- aggregates ---------------------------------------------------
    thr = 1e-3  # SEK on the objective: below this is solver noise
    print()
    print(f"RESULT cells={len(rows)} count")
    for label, sel in (("sz", [r for r in rows if not r["tz"]]),
                       ("tz", [r for r in rows if r["tz"]]),
                       ("tz_dhw", [r for r in rows if r["tz"] and r["dhw"]]),
                       ("tz_nodhw", [r for r in rows if r["tz"] and not r["dhw"]])):
        if not sel:
            continue
        gaps = np.array([r["gap_feasible"] for r in sel])
        pct = np.array([r["gap_feasible_pct"] for r in sel])
        bill_pct = np.array([r["energy_gap_feasible_pct_bill"] for r in sel])
        restart = np.array([r["gap_restart"] for r in sel])
        pg = np.array([r["prod_pg"] for r in sel])
        with_gap = int(np.sum(gaps > thr))
        print(f"RESULT cells_{label}={len(sel)} count")
        print(f"RESULT cells_with_gap_{label}={with_gap} count")
        print(f"RESULT restart_improves_{label}={int(np.sum(restart > thr))} count")
        print(f"RESULT pg_above_pgtol_{label}={int(np.sum(pg > 1e-5))} count")
        print(f"RESULT mean_gap_sek_{label}={gaps.mean():.4f} SEK")
        print(f"RESULT max_gap_sek_{label}={gaps.max():.4f} SEK")
        print(f"RESULT mean_gap_pct_{label}={pct.mean():.3f} pct_of_objective")
        print(f"RESULT max_gap_pct_{label}={pct.max():.3f} pct_of_objective")
        print(f"RESULT mean_energy_gap_pct_bill_{label}={bill_pct.mean():.3f} pct_of_bill")
        print(f"RESULT mean_restart_gap_sek_{label}={restart.mean():.4f} SEK")
        if len(sel) >= 2:
            drop = np.argmax(pct)
            loo = np.delete(pct, drop)
            print(f"RESULT loo_mean_gap_pct_{label}={loo.mean():.3f} pct_of_objective")
            print(f"RESULT loo_min_gap_pct_{label}={pct.min():.3f} pct_of_objective")
            print(f"RESULT loo_dropped_{label}={sel[drop]['cell']} cell")
    flat = [r for r in rows if r["price"] == "flat" and r["tz"]]
    if flat:
        g = np.array([r["gap_feasible"] for r in flat])
        p = np.array([r["gap_feasible_pct"] for r in flat])
        print(f"RESULT null_flat_cells_tz={len(flat)} count")
        print(f"RESULT null_flat_cells_with_gap_tz={int(np.sum(g > thr))} count")
        print(f"RESULT null_flat_mean_gap_sek_tz={g.mean():.4f} SEK")
        print(f"RESULT null_flat_mean_gap_pct_tz={p.mean():.3f} pct_of_objective")
    nonflat = [r for r in rows if r["price"] != "flat" and r["tz"]]
    if nonflat:
        g = np.array([r["gap_feasible"] for r in nonflat])
        print(f"RESULT nonflat_mean_gap_sek_tz={g.mean():.4f} SEK")
    step0 = [r for r in rows if r["gap_feasible"] > thr and r["step0_best"] is not None]
    if step0:
        differs = sum(1 for r in step0 if abs(r["step0_prod"] - r["step0_best"]) > 0.05)
        print(f"RESULT step0_differs_among_gap_cells={differs} count")
    print(f"RESULT production_cpu_total={prod_cpu:.2f} s")
    print(f"RESULT wall_total={wall:.1f} s")
    print(f"RESULT provisional=true flag")
    L.footer(clock)
    return 0


if __name__ == "__main__":
    sys.exit(main())
