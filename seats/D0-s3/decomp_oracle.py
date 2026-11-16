"""D0.M7 (decomposition, terminal credit) + D0.M8 (same-information oracle) over
every `python3 tools/audit/enumerate.py d0-grid` line (2400), round 11 D0-s3,
baseline 92d38ecb.

Metrics, per cell (one production solve shared by the three):
  M7a decomp_delta = production `OptimizationResult.objective_value` minus the
      objective_value when `HeatPumpOptimizer._co_optimize` is iterated to a
      fixed point (<= 5 passes, each adopting only a lower score, the method's
      own rule). Hook: optimizer:HeatPumpOptimizer._co_optimize. Positive =
      one pass leaves money on the table. No-DHW cells never call it: the
      count of calls is recorded, not assumed.
  M7b terminal credit: `HeatPumpOptimizer._terminal_cost` replaced by a zero
      closure pair (in memory). Its docstring claims that without it the plan
      "dumps the last couple of hours" and "breaches the comfort floor at the
      tail". Recorded: tail energy (last 2 h, kWh) with/without, tail
      degree-steps below the per-step floor with/without, end room temp.
  M8  same-information oracle (decision 0018 section 1, open loop: one decision
      time, the forecast as issued equals the realised series, so C_fore =
      C_same and the floor is 0). The measured house (plant) is the cell's
      model with house_heat_loss_scale x1.2 and every zone's thermal mass
      x0.85 (the learned model 20 %/15 % off). Costs are SEK of energy
      (price x kWh, space + DHW). C_real = C_model = production's plan (made
      on its learned model); C_same = the plan production's solver ships on
      the PLANT with the pull-to-target zeroed (optimizer._COMFORT_PULL_* = 0;
      least cost inside the bounds: the pull
      is a preference, the bounds stay priced). Both plans are run on the
      plant (`ThermalModel.simulate_trajectory[_with_dhw]`): K*h below the
      per-step floor (`OptimizationConfig.get_temp_bounds`) and above the
      ceiling, and the end room temperature. regret = C_real - C_same, read
      only where both plans hold the floor on the plant; a production plan
      that breaches it on the plant is counted (an `operation` defect, never
      a saving). Model gap (open loop): |plant end room - model end room| K.
      Null: the flat-price cells (D0.M5).

Command (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D0/s3/decomp_oracle.py [--workers 2] [--limit N] [--cells FILE] [--perturb single_pass]
Perturbation: --perturb single_pass caps the iterated arm at the production
single pass (decomp_delta must read 0 on every cell); M7b's perturbation is the
arm itself; M8's: --plant-scale 1.0 makes plant == model, so the model gap
must fall to 0 and prod_plan_breaches_floor_on_plant to 0.
Output: decomp_out/cells.jsonl (resumable). Machine: box B3 (shared).
Expected: see REPORT.md; CPU numbers provisional.
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

TAIL = 8  # steps = 2 h at 15 min


def universe():
    return subprocess.run([sys.executable, "tools/audit/enumerate.py", "d0-grid"], capture_output=True,
                          text=True, check=True).stdout.split()


def _iterating(orig, state, max_passes):
    def co(self, h, *, space_power, dhw_power, status, best_score, solve_space, p_max, planner,
           draw_rates=None):
        state["calls"] += 1
        last = {}

        def ss(*a, **k):
            out = solve_space(*a, **k)
            last["score"] = out[2]
            last["space"] = out[0]
            return out

        sp, dh, st, score = space_power, dhw_power, status, best_score
        for p in range(max_passes):
            last.clear()
            nsp, ndh, nst = orig(self, h, space_power=sp, dhw_power=dh, status=st, best_score=score,
                                 solve_space=ss, p_max=p_max, planner=planner, draw_rates=draw_rates)
            adopted = "space" in last and nsp is last["space"]
            if p > 0 and adopted:
                state["extra_adopted"] += 1
            if not adopted:
                break
            state["passes_adopted"] += 1
            sp, dh, st, score = nsp, ndh, nst, last["score"]
        return sp, dh, st
    return co


def _tail_breach(r, n):
    room = np.asarray(r.room_temp_trajectory, dtype=float)
    return room


def one(cell, perturb=None, plant_scale=1.2):
    import d0s3_lib as L
    from unittest import mock
    from heatpump_optimizer.optimizer import HeatPumpOptimizer
    t0 = time.process_time(); tt0 = time.thread_time()
    rec = {"cell": cell}
    orig_co = HeatPumpOptimizer._co_optimize

    # The iterated arm first: when no pass after the first adopts anything its
    # result IS production's (pass 1 is the unmodified method, later passes
    # returned its own objects), so the production solve is only re-run when
    # a later pass adopted.
    max_passes = 1 if perturb == "single_pass" else 5
    it = {"calls": 0, "passes_adopted": 0, "extra_adopted": 0}
    bi = L.build(cell)
    with mock.patch.object(HeatPumpOptimizer, "_co_optimize", _iterating(orig_co, it, max_passes)):
        ri = bi["optimizer"].optimize(inputs=L.inputs_of(bi))
    rec["co_optimize_calls"] = it["calls"]
    rec["iter_extra_adopted"] = it["extra_adopted"]
    b = L.build(cell)
    if it["extra_adopted"]:
        r = b["optimizer"].optimize(inputs=L.inputs_of(b))
    else:
        r = ri
    rec["prod_objective"] = float(r.objective_value)
    rec["iter_objective"] = float(ri.objective_value)
    rec["decomp_delta"] = rec["prod_objective"] - rec["iter_objective"]
    n = len(r.power_schedule)
    ship = np.asarray(r.power_schedule, dtype=float)
    dhw = np.asarray(r.dhw_power_schedule or [], dtype=float)
    if dhw.size != n:
        dhw = np.zeros(n)
    pr = np.asarray(r.prices, dtype=float)[:n]
    rec["prod_energy_cost"] = float(np.sum(pr * (ship + dhw)) * 0.25)
    si = np.asarray(ri.power_schedule, dtype=float)
    di = np.asarray(ri.dhw_power_schedule or [], dtype=float)
    if di.size != n:
        di = np.zeros(n)
    rec["iter_energy_cost"] = float(np.sum(pr * (si + di)) * 0.25)
    rec["iter_dhw_min"] = float(np.min(ri.dhw_temp_trajectory)) if ri.dhw_temp_trajectory else None
    rec["prod_dhw_min"] = float(np.min(r.dhw_temp_trajectory)) if r.dhw_temp_trajectory else None

    # M7b: terminal credit off
    orig_tc = HeatPumpOptimizer._terminal_cost

    def zero_tc(self, *a, **k):
        orig_tc(self, *a, **k)
        return (lambda *x, **y: 0.0), (lambda traj: np.zeros(traj["room"].shape[0]))
    bt = L.build(cell)
    with mock.patch.object(HeatPumpOptimizer, "_terminal_cost", zero_tc):
        rt = bt["optimizer"].optimize(inputs=L.inputs_of(bt))
    st = np.asarray(rt.power_schedule, dtype=float)
    dt_ = np.asarray(rt.dhw_power_schedule or [], dtype=float)
    if dt_.size != n:
        dt_ = np.zeros(n)
    room_p = np.asarray(r.room_temp_trajectory, dtype=float)
    room_t = np.asarray(rt.room_temp_trajectory, dtype=float)
    opt = b["optimizer"]
    # per-step floor exactly as production builds it (OptimizationConfig.get_temp_bounds)
    from golden import START
    from datetime import timedelta
    floors = np.array([opt.config.get_temp_bounds(((START + timedelta(hours=0.25 * (i + 1))).hour
                                                   + (START + timedelta(hours=0.25 * (i + 1))).minute / 60.0))[0]
                       for i in range(n)])
    rec["tail_kwh_credit"] = float(np.sum(ship[-TAIL:]) * 0.25)
    rec["tail_kwh_nocredit"] = float(np.sum(st[-TAIL:]) * 0.25)
    rec["tail_breach_credit"] = float(np.maximum(0, floors[-TAIL:] - room_p[-TAIL:]).sum()) if room_p.size >= n else None
    rec["tail_breach_nocredit"] = float(np.maximum(0, floors[-TAIL:] - room_t[-TAIL:]).sum()) if room_t.size >= n else None
    rec["end_room_credit"] = float(room_p[-1]) if room_p.size else None
    rec["end_room_nocredit"] = float(room_t[-1]) if room_t.size else None
    rec["nocredit_energy_cost"] = float(np.sum(pr * (st + dt_)) * 0.25)
    rec["credit_plan_l1_kwh"] = float(np.sum(np.abs(st - ship)) * 0.25)

    # M8: same-information oracle on a plant the model mis-learned
    if plant_scale != 1.0:
        p0 = b["optimizer"].model.params
        po = {"house_heat_loss_scale": p0.house_heat_loss_scale * plant_scale,
              "room_thermal_mass": p0.room_thermal_mass * 0.85,
              "upper_floor_thermal_mass": p0.upper_floor_thermal_mass * 0.85,
              "lower_floor_thermal_mass": p0.lower_floor_thermal_mass * 0.85}
    else:
        po = {}
    bp = L.build(cell, param_overrides=po)
    # least cost inside the bounds: the pull-to-target is a preference, not a
    # bound, so its two module weights are zeroed for the oracle solve (and for
    # every evaluation of the objective it captured); the bound penalties and
    # the terminal settlement stay as production prices them.
    from heatpump_optimizer import optimizer as om
    nopull = [mock.patch.object(om, "_COMFORT_PULL_SINGLE_ZONE", 0.0),
              mock.patch.object(om, "_COMFORT_PULL_TWO_ZONE", 0.0)]
    for q in nopull:
        q.start()
    with L.Capture() as capp:
        ro = bp["optimizer"].optimize(inputs=L.inputs_of(bp))
    so = np.asarray(ro.power_schedule, dtype=float)
    do = np.asarray(ro.dhw_power_schedule or [], dtype=float)
    if do.size != n:
        do = np.zeros(n)
    ceils = np.array([opt.config.get_temp_bounds(((START + timedelta(hours=0.25 * (i + 1))).hour
                                                  + (START + timedelta(hours=0.25 * (i + 1))).minute / 60.0))[1]
                      for i in range(n)])
    pm = bp["optimizer"].model
    from heatpump_optimizer.thermal_model import WeatherSeries
    ws = WeatherSeries(outdoor_temps=bp["outdoor"], wind_speeds=bp["wind"], precipitation=bp["rain"],
                       solar_radiation=bp["solar"])
    hrs = (np.arange(n) * 0.25) % 24.0

    def on_plant(space, hot):
        if L.parse(cell)["dhw"]:
            tr = pm.simulate_trajectory_with_dhw(bp["state"], space, hot, ws, start_hour=0.0, dt_hours=0.25,
                                                 dhw_draw_rates=pm.dhw_draw_rates(hrs))
        else:
            tr = pm.simulate_trajectory(bp["state"], space, ws, dt_hours=0.25)
        zones = [tr[0]] + ([tr[2], tr[3]] if pm.params.two_zone_enabled else [])
        lo = sum(float(np.maximum(0, floors - z[1:n + 1]).sum()) for z in zones) * 0.25
        hi = sum(float(np.maximum(0, z[1:n + 1] - ceils).sum()) for z in zones) * 0.25
        return lo, hi, float(tr[0][n])

    real_lo, real_hi, real_end = on_plant(ship, dhw)
    same_lo, same_hi, same_end = on_plant(so, do)
    c_real = rec["prod_energy_cost"]
    c_same = float(np.sum(pr * (so + do)) * 0.25)
    room_model = np.asarray(r.room_temp_trajectory, dtype=float)
    rec.update(C_model=c_real, C_real=c_real, C_same=c_same, regret=c_real - c_same,
               real_breach_below_Kh=real_lo, real_breach_above_Kh=real_hi, real_end_room=real_end,
               same_breach_below_Kh=same_lo, same_breach_above_Kh=same_hi, same_end_room=same_end,
               model_end_room=float(room_model[-1]) if room_model.size else None,
               model_gap_end_room_K=abs(real_end - float(room_model[-1])) if room_model.size else None,
               oracle_status=str(ro.status))
    calls = [c for c in capp.calls if c.commit is not None]
    if calls:
        obj = calls[-1].commit["out_scope"][1]
        args_r, args_s = ((dhw,), (do,)) if calls[-1].args else ((), ())
        jr, js = float(obj(ship, *args_r)), float(obj(so, *args_s))
        # settled: the plant's own pull-free objective (energy + bound
        # penalties + the terminal settlement of the heat left at the end)
        rec.update(J0_real=jr, J0_same=js, regret_settled=jr - js)
    for q in reversed(nopull):
        q.stop()
    rec["cell_cpu"] = round(time.process_time() - t0, 3)
    rec["cell_thread_cpu"] = round(time.thread_time() - tt0, 3)
    return rec


def _safe(args):
    try:
        return one(*args)
    except Exception as e:  # noqa: BLE001
        import traceback
        return {"cell": args[0], "error": f"{type(e).__name__}: {e}", "tb": traceback.format_exc()[-1500:]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--cells", default="")
    ap.add_argument("--perturb", default="")
    ap.add_argument("--plant-scale", type=float, default=1.2)
    ap.add_argument("--out", default=os.path.join(HERE, "decomp_out", "cells.jsonl"))
    a = ap.parse_args()
    cells = [l.strip() for l in open(a.cells)] if a.cells else universe()
    if a.perturb or a.plant_scale != 1.2:
        a.out = a.out.replace(".jsonl", f".{a.perturb or 'p'}{a.plant_scale}.jsonl")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    done = set()
    if os.path.exists(a.out):
        for line in open(a.out):
            d = json.loads(line)
            if "error" not in d:
                done.add(d["cell"])
    todo = [c for c in cells if c not in done]
    random.Random(11).shuffle(todo)
    if a.limit:
        todo = todo[: a.limit]
    from multiprocessing import get_context
    with open(a.out, "a") as fh, get_context("fork").Pool(a.workers) as pool:
        for i, rec in enumerate(pool.imap_unordered(_safe, [(c, a.perturb or None, a.plant_scale) for c in todo])):
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            print(f"[{i + 1}/{len(todo)}] {rec['cell']} d={rec.get('decomp_delta', rec.get('error'))}", flush=True)
    summarize(a.out, cells)


def summarize(path, cells):
    import d0s3_lib as L
    recs = {}
    for line in open(path):
        d = json.loads(line)
        if "error" not in d:
            recs[d["cell"]] = d
    ex = [c for c in cells if c in recs]
    R = [recs[c] for c in ex]
    print(f"RESULT universe={len(cells)} cells")
    print(f"RESULT examined={len(ex)} cells")
    print(f"RESULT co_optimize_cells={sum(1 for r in R if r['co_optimize_calls'])}")
    print(f"RESULT decomp_extra_adopted_cells={sum(1 for r in R if r.get('iter_extra_adopted', 0) > 0)}")
    print(f"RESULT decomp_positive_cells={sum(1 for r in R if r['decomp_delta'] > 1e-6)} max={max((r['decomp_delta'] for r in R), default=0):.5f}")
    moved = [r for r in R if r["credit_plan_l1_kwh"] > 1e-3]
    dump = [r for r in moved if r["tail_kwh_nocredit"] < r["tail_kwh_credit"] - 1e-3]
    rev = [r for r in moved if r["tail_kwh_nocredit"] > r["tail_kwh_credit"] + 1e-3]
    tb = [r for r in moved if (r["tail_breach_nocredit"] or 0) > (r["tail_breach_credit"] or 0) + 1e-3]
    print(f"RESULT terminal_plan_moved_cells={len(moved)}")
    print(f"RESULT terminal_tail_dump_cells={len(dump)} (credit off -> less tail energy)")
    print(f"RESULT terminal_tail_reversed_cells={len(rev)} (credit off -> MORE tail energy)")
    print(f"RESULT terminal_tail_breach_cells={len(tb)} (credit off -> worse tail floor breach)")
    O = [r for r in R if "regret" in r]
    for flat in (False, True):
        sub = [r for r in O if (r["cell"].split("/")[0] == "flat") == flat]
        if sub:
            ok = [r for r in sub if r["real_breach_below_Kh"] <= 1e-3 and r["same_breach_below_Kh"] <= 1e-3]
            rg = np.array([r["regret"] for r in ok]) if ok else np.zeros(1)
            mg = np.array([r["model_gap_end_room_K"] or 0 for r in sub])
            rb = sum(1 for r in sub if r["real_breach_below_Kh"] > 1e-3)
            rs = np.array([r.get("regret_settled", np.nan) for r in ok], dtype=float)
            rs = rs[np.isfinite(rs)]
            if rs.size:
                srt = np.sort(rs)
                print(f"RESULT oracle_{'flat' if flat else 'nonflat'}_regret_settled: n={rs.size} mean={rs.mean():.4f} "
                      f"min={rs.min():.4f} max={rs.max():.4f} drop_max_mean={(srt[:-1].mean() if rs.size > 1 else float('nan')):.4f} "
                      f"neg_cells={(rs < -1e-6).sum()} SEK/horizon")
            print(f"RESULT oracle_{'flat' if flat else 'nonflat'}_cells={len(sub)} both_hold_bounds={len(ok)} "
                  f"regret_mean_SEK={rg.mean():.4f} regret_max_SEK={rg.max():.4f} regret_neg_cells={(rg < -1e-6).sum()} "
                  f"prod_plan_breaches_floor_on_plant={rb} model_gap_end_room_K_mean={mg.mean():.3f}")
    pc = sum(r.get("cell_cpu", 0) for r in R); tc = sum(r.get("cell_thread_cpu", 0) for r in R)
    print(f"RESULT cpu_total_s={pc:.1f} provisional")
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={L.load1():.2f}")
    print(f"RESULT swapins={L.swapins()}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--summary":
        summarize(os.path.join(HERE, "decomp_out", "cells.jsonl"), universe())
    else:
        main()
