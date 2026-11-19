"""D0-s2 M6 MPC masking (round 11): is a one-shot gap realised once production re-plans in closed loop?

Metric (one line): realised_gap_pct = 100*(Jr_prod - Jr_ch)/|Jr_prod|, Jr = the PRODUCTION objective
  (the true objective closure HeatPumpOptimizer._solve_objectives builds, captured from the day's first
  _multi_start_minimize call, descent relaxation stripped) of the EXECUTED first-24 h space/DHW schedule
  from the cell's start state, each arm driving the loop with its own solver; beside it the realised
  energy SEK, the comfort deficit (K-steps below min_temp, worst zone), DHW deficit below dhw_min_temp,
  and compressor starts of the executed schedule (comfort-pull and cycling terms are inside Jr).
Count key: the executed schedule (what the plant ran), never a planned one.
  Multi-day (--days > 1): Jr_all = the production objective of a days*24 h solve from the start state,
  applied to the whole executed schedule; realised_gap_all_pct is its gap (day-1 Jr stays beside it).
Loop: every R steps the production coordinator builds the record at the plant's state
  (cells.build_record(offset=step, state=plant_state)), the arm's optimizer solves it, the first R steps
  run on the plant (ThermalModel.simulate_trajectory_with_dhw with end_state, valve targets as planned).
  Both arms carry the previous shipped plan as production does (coordinator._warm_seeded semantics).
Arms: prod (production); seeds (production + race.py's 5 structured extra candidates in every
  _multi_start_minimize call, the previous shipped plan shifted by R as the 'previous plan' seed).
Plant: --plant-error 1.0 (plant == model) or e.g. 1.25 (house heat loss x1.25, rolling.py's mismatch).
Instrumented symbol: custom_components.heatpump_optimizer.optimizer:_multi_start_minimize (wrapped),
  HeatPumpOptimizer.optimize (driven per re-plan), ThermalModel.simulate_trajectory_with_dhw (plant).
Perturbation: RACE_SEEDS_OFF=1 makes the seeds arm production: realised_gap_pct must go to_zero (exact).
Null control: run the same cell's flat counterpart line (price axis 'flat').
Command: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D0/s2/mpc.py \
           --days 1 --replan 8 --plant-error 1.0 [--out F.jsonl] CELL [CELL ...]
Expected: per-cell values in results/m6_*.jsonl, tolerance +-0.05 pct-points (solver floats).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box B2, 4 vCPU, shared.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import copy
import json
import time
import argparse
from dataclasses import replace
from functools import partial
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cells  # noqa: E402
import race  # noqa: E402
import numpy as np  # noqa: E402
import heatpump_optimizer.optimizer as om  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, WeatherSeries  # noqa: E402

REAL_MS = om._multi_start_minimize


class _Captured(BaseException):
    pass


def _cfg_and_axes(line, price_override=None):
    if line.startswith("coord/"):
        _, name, price, weather = line.split("/")
        return cells.coord_config(name), price_override or price, weather, 24
    price, weather, topo, dhw, plant, h = cells.parse_cell(line)
    return cells.cell_config(topo, dhw, plant), price_override or price, weather, h


def true_objective(config, price, weather, state, hours=24):
    """The production objective of an ``hours`` solve from ``state``: the first multi-start call's closure."""
    rec, _ = cells.build_record(config, price, weather, hours, state=state)
    got = {}

    def grab(objective, candidates, bounds, args=(), *a, **k):
        f = objective.func if isinstance(objective, partial) else objective
        got["f"], got["args"] = f, args
        raise _Captured()

    opt = rec.optimizer()
    try:
        with mock.patch.object(om, "_multi_start_minimize", grab):
            opt.optimize(inputs=rec.inputs)
    except _Captured:
        pass
    return got.get("f"), got.get("args", ()), rec


def solve(rec, arm, prev_plan, replan):
    prices = np.asarray(rec.inputs.forecast.prices, float)
    seeds_on = arm == "seeds" and os.environ.get("RACE_SEEDS_OFF") != "1"
    shifted = None
    if prev_plan is not None:
        shifted = np.concatenate([prev_plan[replan:], np.repeat(prev_plan[-1:], replan)])

    def wrapped(objective, candidates, bounds, args=(), maxiter=300, batch_objective=None,
                move_starts=lambda c, m: c):
        cands = list(candidates)
        if seeds_on:
            cands = cands + race._seeds(cands, bounds, prices, shifted)
        return REAL_MS(objective, cands, bounds, args, maxiter, batch_objective, move_starts)

    opt = rec.optimizer()
    if prev_plan is not None:
        opt._prev_shipped_plan = np.asarray(prev_plan, float)  # coordinator._warm_seeded
    with mock.patch.object(om, "_multi_start_minimize", wrapped):
        return opt.optimize(inputs=rec.inputs)


def loop(line, arm, days, replan, plant_error, price_override=None):
    config, price, weather, hours = _cfg_and_axes(line, price_override)
    rec0, _ = cells.build_record(config, price, weather, hours)
    s0 = copy.deepcopy(rec0.inputs.state)
    pp = replace(copy.deepcopy(rec0.params))
    for k in ("heat_loss_coefficient", "upper_floor_heat_loss", "lower_floor_heat_loss"):
        if hasattr(pp, k):
            setattr(pp, k, getattr(pp, k) * plant_error)
    plant = ThermalModel(pp)
    total = int(days * 96)
    _, ot, wi, ra, so = cells._series(price, weather, cells_start(), (total + 8) / 4.0)
    pr_all = cells._series(price, weather, cells_start(), (total + 8) / 4.0)[0]
    state = copy.deepcopy(s0)
    ex_s, ex_d, rooms, tanks = [], [], [], []
    prev = None
    two = bool(getattr(rec0.params, "two_zone_enabled", False))
    for step in range(0, total, replan):
        rec, _ = cells.build_record(config, price, weather, hours, offset=step, state=state)
        res = solve(rec, arm, prev, replan)
        pw = np.asarray(res.power_schedule, float)
        dpw = race._dhw_of(res, pw)
        prev = pw.copy()
        r = min(replan, total - step, pw.size)
        vt = getattr(res, "valve_target_schedule", None)
        vt = None if vt is None or len(vt) < r else np.asarray(vt, float)[:r]
        if vt is not None and not np.all(np.isfinite(vt)):
            vt = None
        end = []
        out = plant.simulate_trajectory_with_dhw(
            state, pw[:r], dpw[:r],
            WeatherSeries(outdoor_temps=ot[step:step + r], wind_speeds=wi[step:step + r],
                          precipitation=ra[step:step + r], solar_radiation=so[step:step + r]),
            start_hour=((step % 96) * 0.25), dt_hours=0.25, valve_targets=vt, end_state=end)
        room, slab, up, lo, tank = out[0], out[1], out[2], out[3], out[4]
        for j in range(1, r + 1):
            rooms.append(min(float(up[j]), float(lo[j])) if two else float(room[j]))
            tanks.append(float(tank[j]))
        state = end[-1]
        ex_s += [float(v) for v in pw[:r]]
        ex_d += [float(v) for v in dpw[:r]]
    ex_s, ex_d = np.array(ex_s), np.array(ex_d)
    on = (ex_s + ex_d) > 0.05
    f, args, rec_s = true_objective(config, price, weather, s0)
    d1 = slice(0, 96)
    jr = None
    if f is not None:
        a = (ex_d[d1],) if len(args) >= 1 and args[0] is not None and np.asarray(args[0]).size == 96 else ()
        jr = float(f(ex_s[d1], *a))
    jr_all = jr
    if total > 96:
        fa, aa, _ = true_objective(config, price, weather, s0, hours=total / 4.0)
        jr_all = None
        if fa is not None:
            b = (ex_d,) if len(aa) >= 1 and aa[0] is not None and np.asarray(aa[0]).size == total else ()
            jr_all = float(fa(ex_s, *b))
    cfg = rec0.config
    return {
        "cell": line, "arm": arm, "days": days, "replan": replan, "plant_error": plant_error,
        "price_arm": price_override or "cell",
        "Jr_day1": jr,
        "Jr_all": jr_all,
        "energy_sek": float(np.sum(pr_all[:total] * (ex_s + ex_d)) * 0.25),
        "room_deficit": float(np.maximum(0.0, float(cfg.min_temp) - np.array(rooms)).sum()),
        "dhw_deficit": float(np.maximum(0.0, float(rec0.params.dhw_min_temp) - np.array(tanks)).sum())
        if getattr(rec0.params, "dhw_enabled", False) else 0.0,
        "starts": int(np.sum(on[1:] & ~on[:-1]) + (1 if on[0] else 0)),
        "kwh": float(np.sum(ex_s + ex_d) * 0.25),
        "step0": [float(ex_s[0]), float(ex_d[0])],
    }


def cells_start():
    import golden
    return golden.START


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cells", nargs="*")
    ap.add_argument("--cells-file")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--days", type=float, default=1)
    ap.add_argument("--replan", type=int, default=8)
    ap.add_argument("--plant-error", type=float, default=1.0)
    ap.add_argument("--price", default=None)
    ap.add_argument("--out")
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
                done.add((r["cell"], r.get("days"), r.get("replan"), r.get("plant_error"), r.get("price_arm")))
            except Exception:
                pass
    c0, t0 = time.process_time(), time.thread_time()
    for line in lines:
        key = (line, a.days, a.replan, a.plant_error, a.price or "cell")
        if key in done:
            continue
        out = {"cell": line, "days": a.days, "replan": a.replan, "plant_error": a.plant_error,
               "price_arm": a.price or "cell"}
        try:
            c1 = time.process_time()
            p = loop(line, "prod", a.days, a.replan, a.plant_error, a.price)
            s = loop(line, "seeds", a.days, a.replan, a.plant_error, a.price)
            out.update({"prod": p, "seeds": s, "cpu_s": round(time.process_time() - c1, 2)})
            if p["Jr_day1"] is not None and s["Jr_day1"] is not None:
                out["realised_gap_pct"] = 100.0 * (p["Jr_day1"] - s["Jr_day1"]) / max(abs(p["Jr_day1"]), 1e-9)
            if p.get("Jr_all") is not None and s.get("Jr_all") is not None:
                out["realised_gap_all_pct"] = 100.0 * (p["Jr_all"] - s["Jr_all"]) / max(abs(p["Jr_all"]), 1e-9)
            out["realised_energy_gap_sek"] = p["energy_sek"] - s["energy_sek"]
            out["deficit_delta"] = s["room_deficit"] - p["room_deficit"]
            out["dhw_deficit_delta"] = s["dhw_deficit"] - p["dhw_deficit"]
            out["starts_delta"] = s["starts"] - p["starts"]
        except Exception as err:
            out["error"] = repr(err)
        print(f"RESULT realised_gap_pct[{line}|d{a.days}|R{a.replan}|e{a.plant_error}|{a.price or 'cell'}]="
              f"{out.get('realised_gap_pct', 'nan')} pct", flush=True)
        if a.out:
            with open(a.out, "a") as f:
                f.write(json.dumps(out) + "\n")
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
