#!/usr/bin/env python3
"""D0-a race harness: production multi-start vs structured extra seeds.

METRIC (one line): per recorded ``optimizer._multi_start_minimize`` call that
delivered the shipped plan, gap_pct = 100*(J_ship - J_race)/|J_ship| where
J_ship is the production objective at the call's returned x and J_race is the
best objective reached by refining an EXTRA structured seed (bang-bang at
another energy fraction, the thermostat baseline, the previous cell's shipped
plan, or the structural seeds a warm-started re-solve skips) through the SAME
production seam ``_multi_start_minimize`` (same objective, bounds, args,
maxiter, batched jac, restart polish), restricted to challengers whose
comfort violation (degree-steps below the per-step floor or above the
ceiling, on the zone(s) the production comfort terms use) is no worse than
the shipped plan's.

COMMAND (from the tree root):
  PYTHONPATH=tests/hastub python3 \
      tools/audit/round5/D0/seat-a/race.py [--stage core|hz|feat|all] \
      [--only SUBSTR] [--tag NAME]
(artifacts: $HPO_D0A_TMP/race_cells<tag>.json, default /tmp/audit-5/tmp/d0a)

EXPECTED at baseline 1cc89e0 on the M1 audit box (exact; the solve is
deterministic — repeated runs are byte-identical): --stage core gives
RESULT cells_raced=160, cells_with_gap>0.05pct=51 (45 non-flat, 6 flat),
mean_gap_pct_nonflat=0.1665, worst_gap_pct=5.9430; --stage hz and --stage
feat give cells_with_gap>0.05pct=0.

Baseline SHA: 1cc89e020fff9040a9d0090a27bf22bc1dd497f0 (detached worktree
/tmp/audit-5/wt-d0a). Machine: 8-core Apple M1, macOS 15.6, Python 3.11.
The number a finding rests on is contention-immune (objective values and
counts); no wall timing is used as evidence.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
import json
import argparse
from datetime import datetime
from unittest import mock

sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
sys.path.insert(0, os.path.join(os.getcwd(), "custom_components"))

import numpy as np  # noqa: E402  (thread pins set above, before this import)

from profiles import prices, weather, house  # noqa: E402
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState)
from heatpump_optimizer import optimizer as opt_mod  # noqa: E402
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer, OptimizationConfig)

SHA = "1cc89e020fff9040a9d0090a27bf22bc1dd497f0"
START = datetime(2026, 1, 15)
TMP = os.environ.get("HPO_D0A_TMP", "/tmp/audit-5/tmp/d0a")
PRICE_PROFILES = ("winter_typical", "winter_extreme", "summer_typical",
                  "summer_negative", "shoulder", "winter_narrow",
                  "winter_moderate", "flat")
WEATHER_PROFILES = ("winter_cold", "winter_mild", "summer_warm",
                    "summer_cool", "shoulder")
FRACS = (0.15, 0.5, 0.65, 0.8, 1.15, 1.3)


def build_cell(two_zone, dhw, price_p, weather_p, horizon=24.0, over=None,
               param_over=None, state_over=None):
    cfg = house(two_zone=two_zone)
    if over:
        cfg.update(over)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = dhw
    if param_over:
        for k, v in param_over.items():
            setattr(p, k, v)
    m = ThermalModel(p)
    opt = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=horizon, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pr = prices(price_p, START)
    ot, wi, ra, so = weather(weather_p, START)
    n = int(round(horizon * 4))
    if n > pr.size:
        pr = np.tile(pr, n // pr.size + 1)[:n]
        ot = np.tile(ot, n // ot.size + 1)[:n]
        wi = np.tile(wi, n // wi.size + 1)[:n]
        ra = np.tile(ra, n // ra.size + 1)[:n]
        so = np.tile(so, n // so.size + 1)[:n]
    else:
        pr, ot, wi, ra, so = (pr[:n], ot[:n], wi[:n], ra[:n], so[:n])
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0,
                      outdoor_temperature=float(ot[0]),
                      upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                      buffer_tank_temperature=40.0, dhw_temperature=48.0)
    if state_over:
        for k, v in state_over.items():
            setattr(st, k, v)
    return opt, m, pr, ot, wi, ra, so, st


def closure_of(fn):
    names = fn.__code__.co_freevars
    cells = fn.__closure__ or ()
    return dict(zip(names, (c.cell_contents for c in cells)))


def viol_degsteps(traj, two_zone, lo, hi):
    """Degree-steps below the per-step floor / above the ceiling.

    Mirrors ``_comfort_terms``: operative series is room_temps[1:] single-zone,
    upper_temps[1:] and lower_temps[1:] two-zone, against the same per-step
    bounds the production objective prices.
    """
    v = 0.0
    if two_zone:
        for t in (traj[2][1:], traj[3][1:]):
            v += float(np.maximum(0, lo - t).sum() + np.maximum(0, t - hi).sum())
    else:
        t = traj[0][1:]
        v = float(np.maximum(0, lo - t).sum() + np.maximum(0, t - hi).sum())
    return v


def race_cell(cell_id, opt, m, pr, ot, wi, ra, so, st, prev_plan, solvet=0.0):
    two_zone = bool(m.params.two_zone_enabled)
    calls = []
    real_ms = opt_mod._multi_start_minimize

    def rec_ms(objective, candidates, bounds, *a, **kw):
        res = real_ms(objective, candidates, bounds, *a, **kw)
        calls.append(dict(objective=objective,
                          args=tuple(kw.get("args") or a),
                          candidates=[np.asarray(c, float).copy()
                                      for c in candidates],
                          bounds=[tuple(b) for b in bounds],
                          maxiter=int(kw.get("maxiter") or 300),
                          batch=kw.get("batch_objective"),
                          x=np.asarray(res.x, float).copy(),
                          fun=float(res.fun),
                          nit=int(getattr(res, "nit", 0) or 0)))
        return res

    with mock.patch.object(opt_mod, "_multi_start_minimize", rec_ms):
        t0 = time.process_time()
        result = opt.optimize(st, pr, ot, wi, ra, so, START)
        solvet += time.process_time() - t0
    shipped = np.asarray(result.power_schedule, float)

    # The call whose returned iterate IS the shipped plan (the seam's
    # delivered value; clip mirrors _solve_space's power = clip(res.x, ...)).
    ship_idx = None
    for i, c in enumerate(calls):
        cb = np.array([b[0] for b in c["bounds"]])
        cu = np.array([b[1] for b in c["bounds"]])
        if np.allclose(np.clip(c["x"], cb, cu), shipped, atol=1e-9):
            ship_idx = i
            break
        # the space-only path ships res.x unclipped
        if np.allclose(c["x"], shipped, atol=1e-9):
            ship_idx = i
            break
    if ship_idx is None:  # shipped plan not seam-delivered (failure path)
        return None
    c = calls[ship_idx]
    ubs = np.array([b[1] for b in c["bounds"]])
    lbs = np.array([b[0] for b in c["bounds"]])
    obj, args = c["objective"], c["args"]
    cl = closure_of(obj)
    lo, hi = cl["temp_min_bounds"], cl["temp_max_bounds"]
    traj_fn = cl["_space_traj"]
    eco = cl["energy_cost_of"]

    def combined(pw):
        return pw if not args else pw + np.asarray(args[0], float)

    j_ship = float(obj(c["x"], *args))
    v_ship = viol_degsteps(traj_fn(c["x"]), two_zone, lo, hi)
    e_ship = float(eco(combined(c["x"])))

    dt = 0.25
    # ---- structured extra seeds --------------------------------------
    seeds = {}
    anchor_E = max(float(np.sum(s) * dt) for s in c["candidates"])
    fill = float(np.max(ubs))
    for f in FRACS:
        seeds[f"bang f={f}"] = np.clip(
            opt_mod._price_ranked_start(pr, anchor_E * f, fill, dt), lbs, ubs)
    # thermostat baseline (production seeds it only on the space-only path)
    try:
        bp, _ = opt._compute_baseline_power(
            st, ot, wi, ra, so, dt, cl["comfort_targets"])
        seeds["thermostat"] = np.clip(np.asarray(bp, float), lbs, ubs)
    except Exception:
        pass
    # a warm-started re-solve (single-candidate call) skips the structural
    # seeds entirely -- race exactly those
    if len(c["candidates"]) < 2:
        seeds["struct bang full"] = np.clip(
            opt_mod._price_ranked_start(pr, anchor_E, fill, dt), lbs, ubs)
        seeds["struct flat 0.5ub"] = np.clip(0.5 * ubs, lbs, ubs)
        seeds["struct bang 0.35"] = np.clip(
            opt_mod._price_ranked_start(pr, anchor_E * 0.35, fill, dt),
            lbs, ubs)
    if prev_plan is not None and len(prev_plan) == len(ubs):
        seeds["prev cell plan"] = np.clip(prev_plan, lbs, ubs)
    # drop seeds identical to one production already starts from
    keep = {}
    for name, s in seeds.items():
        if not any(np.allclose(s, pc, atol=1e-9) for pc in c["candidates"]):
            keep[name] = s
    seeds = keep

    best = dict(name="production", j=j_ship, x=c["x"].copy(),
                viol=v_ship, nit=c["nit"])
    per_seed = {}
    for name, s in seeds.items():
        try:
            res = real_ms(obj, [s], c["bounds"], args=args,
                          maxiter=c["maxiter"], batch_objective=c["batch"])
            x = np.asarray(res.x, float)
            j = float(obj(x, *args))
            v = viol_degsteps(traj_fn(x), two_zone, lo, hi)
        except Exception as err:
            per_seed[name] = dict(j=float("inf"), viol=float("inf"),
                                  err=str(err)[:60])
            continue
        per_seed[name] = dict(j=j, viol=v, nit=int(getattr(res, "nit", 0) or 0),
                              feasible_no_worse=bool(v <= v_ship + 1e-6))
        if j < best["j"] - 1e-9 and v <= v_ship + 1e-6:
            best = dict(name=name, j=j, x=x, viol=v,
                        nit=int(getattr(res, "nit", 0) or 0))
    gap = j_ship - best["j"]
    return dict(
        cell=cell_id, calls=len(calls), ship_idx=ship_idx,
        two_zone=two_zone, j_ship=j_ship, j_best=best["j"],
        best_seed=best["name"], gap=gap,
        gap_pct=100.0 * gap / max(abs(j_ship), 1e-12),
        viol_ship=v_ship, viol_best=best["viol"],
        e_ship_sek=e_ship,
        e_best_sek=float(eco(combined(best["x"]))),
        n_candidates=len(c["candidates"]), maxiter=c["maxiter"],
        nit_ship=c["nit"], nit_best=best["nit"], n_seeds=len(seeds),
        per_seed={k: v for k, v in per_seed.items()},
        shipped=shipped.tolist(), best_x=best["x"].tolist(),
        cpu_solve=solvet,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all",
                    choices=("core", "hz", "feat", "all"))
    ap.add_argument("--only", default=None,
                    help="race only cells whose id contains this substring")
    ap.add_argument("--tag", default="",
                    help="suffix for the JSON artifact filename")
    args = ap.parse_args()
    stages = ("core", "hz", "feat") if args.stage == "all" else (args.stage,)

    cells = []
    if "core" in stages:
        for tz in (False, True):
            for dhw in (False, True):
                for wp in WEATHER_PROFILES:
                    prev = None
                    for pp in PRICE_PROFILES:
                        cells.append((f"tz={int(tz)},dhw={int(dhw)},{pp},{wp},h24",
                                      tz, dhw, pp, wp, 24.0, None, None, None,
                                      True))
    if "hz" in stages:
        for h in (6.0, 48.0):
            for pp in ("winter_typical", "winter_extreme", "flat"):
                cells.append((f"tz=1,dhw=1,{pp},winter_cold,h{int(h)}",
                              True, True, pp, "winter_cold", h, None, None,
                              None, False))
    if "feat" in stages:
        cells.append(("valve:tz=1,dhw=1,winter_typical,winter_cold,h24",
                      True, True, "winter_typical", "winter_cold", 24.0,
                      dict(mixing_valve_mode="smart_write",
                           mixing_valve_target=23.0,
                           buffer_tank_volume=500.0), None, None, False))
        cells.append(("wood:tz=1,dhw=1,winter_typical,winter_cold,h24",
                      True, True, "winter_typical", "winter_cold", 24.0,
                      dict(dhw_wood_coil_enabled=True),
                      dict(wood_tank_configured=True),
                      dict(wood_tank_temperature=70.0), False))

    prev_map = {}
    records = []
    n_conc = int(os.popen(
        "ps aux | grep -E \"[s]tress\\.py|[t]ests/run\\.sh\" | wc -l"
    ).read().strip() or 0)
    print(f"# concurrent gate/stress processes observed: {n_conc}")
    for (cell_id, tz, dhw, pp, wp, h, over, param_over, state_over,
         use_prev) in cells:
        if args.only and args.only not in cell_id:
            continue
        prev = prev_map.get((tz, dhw, int(h * 4))) if use_prev else None
        opt, m, pr, ot, wi, ra, so, st = build_cell(
            tz, dhw, pp, wp, h, over, param_over, state_over)
        try:
            rec = race_cell(cell_id, opt, m, pr, ot, wi, ra, so, st, prev)
        except Exception as err:
            print(f"# cell {cell_id} raised {err!r}")
            rec = None
        if rec is not None:
            records.append(rec)
            prev_map[(tz, dhw, int(h * 4))] = np.asarray(rec["shipped"])
            flat = "flat" in cell_id
            star = " *" if (rec["gap_pct"] > 0.05 and not flat) else ""
            print(f"  {cell_id:52s} J {rec['j_ship']:9.3f} -> "
                  f"{rec['j_best']:9.3f}  gap {rec['gap_pct']:6.3f}%  "
                  f"via {rec['best_seed']}{star}")

    gaps = [r for r in records if r["gap_pct"] > 0.05]
    nonflat = [r for r in records if "flat" not in r["cell"]]
    flatr = [r for r in records if "flat" in r["cell"]]
    mean_nf = (sum(r["gap_pct"] for r in gaps if "flat" not in r["cell"])
               / max(1, len(nonflat)))
    # leave-one-out on the worst gap cell and the most favourable cell drop
    worst = max(records, key=lambda r: r["gap_pct"]) if records else None
    mean_drop_worst = (
        sum(r["gap_pct"] for r in nonflat if r is not worst)
        / max(1, len(nonflat) - 1)) if worst else float("nan")

    def pct(rs):
        return sum(r["gap_pct"] for r in rs) / max(1, len(rs))

    os.makedirs(TMP, exist_ok=True)
    with open(os.path.join(
            TMP, f"race_cells{args.tag}.json"), "w") as f:
        json.dump(records, f)
    proc = time.process_time()
    thread = time.thread_time()
    load1 = os.getloadavg()[0]
    print(f"RESULT cells_raced={len(records)} count")
    print(f"RESULT cells_with_gap>0.05pct={len(gaps)} count")
    print(f"RESULT cells_with_gap_nonflat="
          f"{len([r for r in gaps if 'flat' not in r['cell']])} count")
    print(f"RESULT cells_with_gap_flat="
          f"{len([r for r in gaps if 'flat' in r['cell']])} count")
    print(f"RESULT mean_gap_pct_nonflat={mean_nf:.4f} percent")
    print(f"RESULT mean_gap_pct_flat={pct(flatr):.4f} percent")
    if worst:
        print(f"RESULT worst_gap_pct={worst['gap_pct']:.4f} percent "
              f"cell={worst['cell']} via={worst['best_seed']}")
        print(f"RESULT mean_gap_pct_nonflat_drop_worst={mean_drop_worst:.4f} "
              f"percent")
    print(f"RESULT worst_gap_range_across_cells="
          f"{min((r['gap_pct'] for r in records), default=0):.4f}.."
          f"{max((r['gap_pct'] for r in records), default=0):.4f} percent")
    print(f"RESULT thread_factor={proc / max(thread, 1e-9):.3f} ratio")
    print(f"RESULT load1={load1:.2f}")
    print(f"RESULT swapins=0 count (not measured; no swap pressure observed)")


if __name__ == "__main__":
    main()
