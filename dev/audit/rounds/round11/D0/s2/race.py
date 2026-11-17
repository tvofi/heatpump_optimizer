"""D0-s2 M4/M5 race (round 11): production plan vs challengers, per d0-grid cell, on the production objective.

Metric (one line): gap_pct = 100*(J_prod - J_best)/|J_prod|, J = OptimizationResult.objective_value of the
  SHIPPED plan (HeatPumpOptimizer.optimize, after _commit_runs and every candidate stage), J_best the lowest J
  over challenger arms that hold feasibility parity (room floor/ceiling deficit, DHW floor deficit, power box
  no worse than production's, each within 0.01 K-step / 1e-6 kW).
Count key: the shipped OptimizationResult the production seam returns (objective_value, power_schedule,
  dhw_power_schedule, trajectories) -- never an input attribute.
Arms (each a full production solve; only _multi_start_minimize's call is wrapped):
  prod    production, cold start (the coordinator's first solve: no _prev_shipped_plan)
  seeds   every _multi_start_minimize call gets 5 structured extra candidates: bang-bang on the cheapest
          steps at 0.8/1.0/1.2 of the call's mean candidate energy, the flat thermostat level, and the
          production arm's own result of the same call (the "previous plan" seed)
  budget  every call at 4x maxiter (ftol/eps untouched, so not #1293's stop change); run only where a production
          L-BFGS-B run inside a multi-start call stopped on its limit (status 1), else identical by determinism
  warm    production with _prev_shipped_plan = best challenger's shipped plan (production's own warm-start seam)
Instrumented symbol: custom_components.heatpump_optimizer.optimizer:_multi_start_minimize (wrapped),
  HeatPumpOptimizer.optimize (driven), coordinator.HeatPumpOptimizerCoordinator._solve_record (record builder).
Perturbation: RACE_SEEDS_OFF=1 drops the structured seeds from the seeds arm (gap must move to <= the
  budget/warm arms' gap; on a cell whose gap comes from seeds it falls toward 0). PROD_MAXITER_SCALE=0.05 starves
  production's own budget (the prod arm only): gap must go up.
Null control (M5): --price flat re-runs the same race with tests/profiles.py prices("flat").
Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D0/s2/race.py \
            [--price flat] [--out FILE.jsonl] CELL [CELL ...]   (or --cells-file F --shard i/k)
  CELL is a line of enum_cells.py (d0-grid line or coord/<scenario>/<price>/<weather>).
Expected: per-cell gap_pct >= 0 by construction (prod is not an arm of the min); values recorded in
  results/*.jsonl; tolerance +-0.05 pct-points across BLAS builds (solver floats).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box B2, 4 vCPU, shared (3 compute seats).
Prints RESULT lines per cell plus thread_factor, load1, swapins at the end.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import json
import time
import argparse
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cells  # noqa: E402
import numpy as np  # noqa: E402
import heatpump_optimizer.optimizer as om  # noqa: E402

REAL_MS = om._multi_start_minimize
FEAS_TOL = 0.01


def _seeds(cands, bounds, prices, prev):
    lo = np.array([b[0] for b in bounds], float)
    hi = np.array([b[1] for b in bounds], float)
    n = lo.size
    pr = np.asarray(prices, float)[:n]
    if pr.size < n:
        pr = np.pad(pr, (0, n - pr.size), mode="edge")
    e = float(np.mean([np.sum(np.clip(np.asarray(c, float), lo, hi)) for c in cands]))
    out = []
    order = np.argsort(pr, kind="stable")
    for f in (0.8, 1.0, 1.2):
        x = lo.copy()
        left = max(0.0, f * e - lo.sum())
        for i in order:
            take = min(hi[i] - lo[i], left)
            x[i] += take
            left -= take
            if left <= 0:
                break
        out.append(x)
    out.append(np.clip(np.full(n, e / max(n, 1)), lo, hi))
    if prev is not None and np.asarray(prev).size == n:
        out.append(np.clip(np.asarray(prev, float), lo, hi))
    return out


def _same(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return a.shape == b.shape and a.tobytes() == b.tobytes()


def run_arm(line, arm, price_override=None, prod_calls=None, warm_plan=None):
    """One full production solve with _multi_start_minimize wrapped for ``arm``.

    Exactness shortcut (seeds, warm): where a call's candidates contain the production arm's
    candidates for the same call index, unchanged, with the same bounds, the production result for
    that call is reused and only the EXTRA candidates are run (with no start move, which production
    already applied to its own); the better of the two by the call's own objective is returned --
    what one _multi_start_minimize over the union returns, up to an exact tie (kept as production).
    Any call whose inputs moved runs in full over the union.
    """
    rec, _ = cells.any_record(line, price_override)
    prices = np.asarray(rec.inputs.forecast.prices, float)
    calls = []
    runs = []
    scale = 4.0 if arm == "budget" else 1.0
    if arm == "prod":
        scale = float(os.environ.get("PROD_MAXITER_SCALE", "1"))
    seeds_on = arm == "seeds" and os.environ.get("RACE_SEEDS_OFF") != "1"
    inside = [False]
    real_run = om._lbfgsb_run

    def run_rec(objective, batch_objective, x0, bounds, args, maxiter, memo=None):
        r = real_run(objective, batch_objective, x0, bounds, args, maxiter, memo)
        if inside[0]:
            runs.append((int(getattr(r, "status", 0)), int(getattr(r, "nit", 0)), int(maxiter)))
        return r

    def wrapped(objective, candidates, bounds, args=(), maxiter=300, batch_objective=None,
                move_starts=lambda c, m: c):
        idx = len(calls)
        base = list(candidates)
        mi = max(1, int(round(maxiter * scale)))
        pc = prod_calls[idx] if prod_calls and idx < len(prod_calls) else None
        extras = []
        if seeds_on:
            extras = _seeds(base, bounds, prices, pc["x"] if pc else None)
        inside[0] = True
        try:
            cached = (os.environ.get("RACE_NOCACHE") != "1" and pc is not None and arm in ("seeds", "warm") and pc["bounds"] == list(bounds)
                      and len(base) >= len(pc["cands"]))
            if cached:
                left = list(base)
                for c in pc["cands"]:
                    hit = next((j for j, y in enumerate(left) if _same(c, y)), None)
                    if hit is None:
                        cached = False
                        break
                    left.pop(hit)
                extras = left + extras
            if cached:
                res = pc["res"]
                if extras:
                    alt = REAL_MS(objective, extras, bounds, args, mi, batch_objective)
                    if float(objective(alt.x, *args)) < float(objective(res.x, *args)):
                        res = alt
            else:
                res = REAL_MS(objective, base + extras, bounds, args, mi, batch_objective, move_starts)
        finally:
            inside[0] = False
        calls.append({"x": np.asarray(res.x, float).copy(), "res": res, "bounds": list(bounds),
                      "cands": [np.asarray(c, float).copy() for c in base], "cached": cached if arm != "prod" else None})
        return res

    opt = rec.optimizer()
    if warm_plan is not None:
        opt._prev_shipped_plan = np.asarray(warm_plan, float)
    c0 = time.process_time()
    with mock.patch.object(om, "_multi_start_minimize", wrapped), mock.patch.object(om, "_lbfgsb_run", run_rec):
        res = opt.optimize(inputs=rec.inputs)
    cpu = time.process_time() - c0
    return rec, res, calls, cpu, runs


def _dhw_of(res, pw):
    d = res.dhw_power_schedule
    d = np.zeros_like(pw) if d is None else np.asarray(d, float)
    return d if d.size == pw.size else np.zeros_like(pw)


def feas(rec, res):
    cfg, p = rec.config, rec.params
    pw = np.asarray(res.power_schedule, float)
    dpw = _dhw_of(res, pw)
    floor, ceil = float(cfg.min_temp), float(cfg.max_temp)
    def deficit(tr, lo=None, hi=None):
        if tr is None:
            return 0.0
        t = np.asarray(tr, float)[1:]
        if t.size == 0 or not np.all(np.isfinite(t)):
            return 0.0
        d = 0.0
        if lo is not None:
            d += float(np.maximum(0.0, lo - t).sum())
        if hi is not None:
            d += float(np.maximum(0.0, t - hi).sum())
        return d
    two = bool(getattr(p, "two_zone_enabled", False))
    rooms = [res.upper_temp_trajectory, res.lower_temp_trajectory] if two else [res.room_temp_trajectory]
    room_lo = sum(deficit(t, lo=floor) for t in rooms)
    room_hi = sum(deficit(t, hi=ceil) for t in rooms)
    dhw_lo = deficit(res.dhw_temp_trajectory, lo=float(p.dhw_min_temp)) if getattr(p, "dhw_enabled", False) else 0.0
    pmax = float(p.max_electrical_power)
    box = float(np.maximum(0.0, -pw).sum() + np.maximum(0.0, pw + dpw - pmax).sum())
    return {"room_lo": room_lo, "room_hi": room_hi, "dhw_lo": dhw_lo, "box": box}


def summarise(rec, res, cpu):
    dt = float(rec.config.dt_hours)
    pw = np.asarray(res.power_schedule, float)
    dpw = _dhw_of(res, pw)
    pr = np.asarray(rec.inputs.forecast.prices, float)[:pw.size]
    return {"J": float(res.objective_value), "energy_sek": float(np.sum(pr * (pw + dpw)) * dt),
            "kwh": float(np.sum(pw + dpw) * dt), "starts": int(getattr(res, "compressor_starts", 0) or 0),
            "status": str(res.status), "cpu_s": round(cpu, 3), "feas": feas(rec, res),
            "step0": [float(pw[0]), float(dpw[0])], "plan": [round(float(v), 4) for v in pw],
            "dhw": [round(float(v), 4) for v in dpw]}


def parity(ch, pr):
    a, b = ch["feas"], pr["feas"]
    return (a["room_lo"] <= b["room_lo"] + FEAS_TOL and a["room_hi"] <= b["room_hi"] + FEAS_TOL
            and a["dhw_lo"] <= b["dhw_lo"] + FEAS_TOL and a["box"] <= b["box"] + 1e-6)


def race(line, price_override=None):
    rec, res, pcalls, cpu, pruns = run_arm(line, "prod", price_override)
    out = {"cell": line, "price_arm": price_override or "cell", "arms": {"prod": summarise(rec, res, cpu)}}
    out["prod_calls"] = len(pcalls)
    out["prod_runs_at_limit"] = sum(1 for st, nit, mi in pruns if st == 1)
    rec, res, scalls, cpu, _ = run_arm(line, "seeds", price_override, prod_calls=pcalls)
    out["arms"]["seeds"] = summarise(rec, res, cpu)
    out["seeds_cached_calls"] = sum(1 for c in scalls if c["cached"])
    if out["prod_runs_at_limit"]:
        rec, res, _, cpu, _ = run_arm(line, "budget", price_override)
        out["arms"]["budget"] = summarise(rec, res, cpu)
        out["budget"] = "run"
    else:
        out["budget"] = "identical: no L-BFGS-B run inside a multi-start call stopped on its limit"
    best_ch = min([a for a in out["arms"] if a != "prod"] + ["prod"], key=lambda a: out["arms"][a]["J"])
    rec, res, _, cpu, _ = run_arm(line, "warm", price_override, prod_calls=pcalls,
                                  warm_plan=out["arms"][best_ch]["plan"])
    out["arms"]["warm"] = summarise(rec, res, cpu)
    out["warm_from"] = best_ch
    prod = out["arms"]["prod"]
    feasible = {a: v for a, v in out["arms"].items() if a != "prod" and parity(v, prod) and np.isfinite(v["J"])}
    if feasible:
        best = min(feasible, key=lambda a: feasible[a]["J"])
        jb = min(feasible[best]["J"], prod["J"])
    else:
        best, jb = None, prod["J"]
    out["best_arm"] = best
    out["gap_abs"] = prod["J"] - jb
    out["gap_pct"] = 100.0 * (prod["J"] - jb) / max(abs(prod["J"]), 1e-9)
    out["energy_gap_sek"] = prod["energy_sek"] - (feasible[best]["energy_sek"] if best else prod["energy_sek"])
    out["step0_differs"] = bool(best) and (abs(prod["step0"][0] - feasible[best]["step0"][0]) > 1e-3
                                            or abs(prod["step0"][1] - feasible[best]["step0"][1]) > 1e-3)
    out["infeasible_arms"] = [a for a in out["arms"] if a != "prod" and a not in feasible]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cells", nargs="*")
    ap.add_argument("--cells-file")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--price", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    lines = list(a.cells)
    if a.cells_file:
        lines += [l.strip() for l in open(a.cells_file) if l.strip()]
    i, k = (int(x) for x in a.shard.split("/"))
    lines = [l for j, l in enumerate(lines) if j % k == i]
    done = set()
    if a.out and os.path.exists(a.out):
        for l in open(a.out):
            try:
                r = json.loads(l)
                # a flat line raced with --price flat is the same solve as without it: key on the price used
                done.add((r["cell"], r["cell"].split("/")[0] if r["price_arm"] == "cell" else r["price_arm"]))
            except Exception:
                pass
    c0, t0 = time.process_time(), time.thread_time()
    for line in lines:
        if (line, a.price or line.split("/")[0]) in done:
            continue
        try:
            r = race(line, a.price)
        except Exception as err:  # recorded, never hidden
            r = {"cell": line, "price_arm": a.price or "cell", "error": repr(err)}
        print(f"RESULT gap_pct[{line}|{a.price or 'cell'}]={r.get('gap_pct', 'nan')} pct best={r.get('best_arm')}", flush=True)
        if a.out:
            with open(a.out, "a") as f:
                f.write(json.dumps(r) + "\n")
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
