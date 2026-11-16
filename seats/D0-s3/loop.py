"""D0.M6 MPC masking: does a race gap survive receding-horizon re-planning?
Round 11 D0-s3, baseline 92d38ecb.

Metric, per gap cell (race_out/cells.jsonl, cell_gap > --min-gap on the call
that ships) and per plant (plant == model; plant = the cell's model with
house_heat_loss_scale x1.2 and every zone's thermal mass x0.85):
  realised_gap = J(prod loop) - J(augmented loop), where J is the PLANT's own
  production objective -- captured from a 24 h `HeatPumpOptimizer.optimize`
  built on the plant at t0 (comfort pull, start/cycling terms, terminal
  credit, energy and DHW terms all in) -- evaluated at the space and DHW power
  each loop actually applied over 24 h. A loop re-plans every --every steps
  (default 4 = hourly) at the cell's own horizon, applies the plan's first
  --every steps to the plant (`ThermalModel.simulate_trajectory_with_dhw`,
  end_state), and carries the previous shipped plan as production's warm
  seed (`HeatPumpOptimizer._prev_shipped_plan`, as coordinator._warm_seeded
  does). The augmented arm is production's solver with D0.M2's structured
  seeds appended to every `_multi_start_minimize` call (in memory).
  Also: step0_differs from the race, realised energy cost (SEK) per arm.
  --days N runs the loop N days (multi-day; J is then summed over days, each
  day scored by its own day-start plant objective).

Enumerator (D0.M6's universe, every race gap cell): loop.py --list
Command (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D0/s3/loop.py [--min-gap 0.01] [--workers 2] [--days 1] [--cells FILE]
Perturbation: --perturb no_seeds makes the augmented arm production itself
(extra seeds empty): realised_gap must be exactly 0 on every cell.
Null control: the flat-price gap cells (D0.M5) run in the same pass.
Output: loop_out/cells[.<tag>].jsonl. Machine: box B3 (shared); CPU provisional.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import json
import time
import argparse
from datetime import timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402

DAY = 96


def _tiled(b, n):
    out = {}
    for k in ("prices", "outdoor", "wind", "rain", "solar"):
        a = np.asarray(b[k], dtype=float)
        base = a[:DAY] if a.size >= DAY else a
        out[k] = np.tile(base, int(np.ceil(n / base.size)))[:n]
    return out


def _plant_obj(L, cell, po, state, start, series, k0):
    """The plant's own 24 h production objective at (state, start)."""
    b = L.build(cell.replace(cell.split("/")[-1], "24h"), param_overrides=po)
    sl = slice(k0, k0 + DAY)
    from profiles import solve_inputs
    inp = solve_inputs(initial_state=state, prices=series["prices"][sl], outdoor_temps=series["outdoor"][sl],
                       wind_speeds=series["wind"][sl], precipitation=series["rain"][sl],
                       solar_radiation=series["solar"][sl], start_time=start)
    with L.Capture() as cap:
        b["optimizer"].optimize(inputs=inp)
    calls = [c for c in cap.calls if c.commit is not None]
    c = calls[-1]
    return c.commit["out_scope"][1], bool(c.args)


def run_loop(L, cell, po, augmented, every, days, no_seeds=False):
    from golden import START
    from profiles import solve_inputs
    from heatpump_optimizer.thermal_model import WeatherSeries
    c = L.parse(cell)
    H = c["hours"] * 4
    total = days * DAY
    b = L.build(cell, param_overrides=None)
    plant = L.build(cell, param_overrides=po)
    series = _tiled(b, total + H + DAY)
    state = plant["state"]
    applied_s = np.zeros(total); applied_d = np.zeros(total)
    prev = None
    J = 0.0
    day_objs = []
    extra = None
    if augmented:
        extra = (lambda call: []) if no_seeds else (lambda call: L.structured_seeds(call))
    k = 0
    while k < total:
        if k % DAY == 0:
            start = START + timedelta(hours=0.25 * k)
            day_objs.append((k, _plant_obj(L, cell, po, state, start, series, k)))
        start = START + timedelta(hours=0.25 * k)
        sl = slice(k, k + H)
        ctl = L.build(cell)  # the controller's (learned) model, fresh per solve as the coordinator does
        opt = ctl["optimizer"]
        if prev is not None:
            opt._prev_shipped_plan = prev
        inp = solve_inputs(initial_state=state, prices=series["prices"][sl], outdoor_temps=series["outdoor"][sl],
                           wind_speeds=series["wind"][sl], precipitation=series["rain"][sl],
                           solar_radiation=series["solar"][sl], start_time=start)
        r, _calls, _cpu, _b = L.solve(None, extra_seeds=extra, opt=opt, inputs=inp)
        if str(r.status).startswith("failed"):
            raise RuntimeError(f"solve failed at step {k}: {r.status}")
        sp = np.asarray(r.power_schedule, dtype=float)
        dh = np.asarray(r.dhw_power_schedule or [], dtype=float)
        if dh.size != sp.size:
            dh = np.zeros(sp.size)
        m = min(every, total - k)
        applied_s[k:k + m] = sp[:m]; applied_d[k:k + m] = dh[:m]
        # advance the PLANT m steps under the realised weather
        pm = plant["optimizer"].model
        ws = WeatherSeries(outdoor_temps=series["outdoor"][k:k + m], wind_speeds=series["wind"][k:k + m],
                           precipitation=series["rain"][k:k + m], solar_radiation=series["solar"][k:k + m])
        hours = np.array([(start + timedelta(hours=0.25 * i)).hour + (start + timedelta(hours=0.25 * i)).minute / 60
                          for i in range(m)])
        end = []
        pm.simulate_trajectory_with_dhw(state, sp[:m], dh[:m], ws, start_hour=float(hours[0]), dt_hours=0.25,
                                        dhw_draw_rates=pm.dhw_draw_rates(hours) if c["dhw"] else None,
                                        end_state=end)
        state = end[-1]
        prev = sp
        k += m
    for k0, (obj, has_dhw) in day_objs:
        x = applied_s[k0:k0 + DAY]
        J += float(obj(x, applied_d[k0:k0 + DAY])) if has_dhw else float(obj(x))
    cost = float(np.sum(series["prices"][:total] * (applied_s + applied_d)) * 0.25)
    return J, cost, applied_s, applied_d


def one(args):
    cell, every, days, perturb = args
    import d0s3_lib as L
    t0 = time.process_time(); tt0 = time.thread_time()
    try:
        out = {"cell": cell, "every": every, "days": days}
        for tag, po in (("same", None), ("mis", "mis")):
            if po == "mis":
                p0 = L.build(cell)["optimizer"].model.params
                po = {"house_heat_loss_scale": p0.house_heat_loss_scale * 1.2,
                      "room_thermal_mass": p0.room_thermal_mass * 0.85,
                      "upper_floor_thermal_mass": p0.upper_floor_thermal_mass * 0.85,
                      "lower_floor_thermal_mass": p0.lower_floor_thermal_mass * 0.85}
            Jp, cp, sp, dp = run_loop(L, cell, po, False, every, days)
            Ja, ca, sa, da = run_loop(L, cell, po, True, every, days, no_seeds=perturb == "no_seeds")
            out[tag] = dict(J_prod=Jp, J_aug=Ja, realised_gap=Jp - Ja, cost_prod=cp, cost_aug=ca,
                            applied_l1_kwh=float(np.sum(np.abs(sp - sa) + np.abs(dp - da)) * 0.25))
        out["cell_cpu"] = round(time.process_time() - t0, 3)
        out["cell_thread_cpu"] = round(time.thread_time() - tt0, 3)
        return out
    except Exception as e:  # noqa: BLE001
        import traceback
        return {"cell": cell, "error": f"{type(e).__name__}: {e}", "tb": traceback.format_exc()[-1500:]}


def mask_one(args):
    """One re-plan after the first --every steps: is the race gap masked?

    Production's plan is applied for `every` steps on the model (plant ==
    model); production re-plans from there warm-seeded with its own plan; the
    race's best challenger from t0 is shifted by `every` steps (its tail padded
    with the re-plan's last `every` steps) and committed through the re-plan's
    own captured call. masked = the re-plan scores no worse than the shifted
    challenger on the re-plan's objective. Only meaningful where the first
    `every` steps of the two t0 plans agree; where they do not the record says
    so and the closed loop decides.
    """
    cell, every, best_x = args
    import d0s3_lib as L
    from golden import START
    from profiles import solve_inputs
    from heatpump_optimizer.thermal_model import WeatherSeries
    t0 = time.process_time(); tt0 = time.thread_time()
    try:
        c = L.parse(cell)
        b = L.build(cell)
        H = c["hours"] * 4
        series = _tiled(b, H + DAY + every)
        r0, calls0, _, _ = L.solve(b)
        sp = np.asarray(r0.power_schedule, dtype=float)
        dh = np.asarray(r0.dhw_power_schedule or [], dtype=float)
        if dh.size != sp.size:
            dh = np.zeros(sp.size)
        bx = np.asarray(best_x, dtype=float)
        head_same = bool(np.allclose(bx[:every], sp[:every], atol=1e-3))
        m = b["optimizer"].model
        ws = WeatherSeries(outdoor_temps=series["outdoor"][:every], wind_speeds=series["wind"][:every],
                           precipitation=series["rain"][:every], solar_radiation=series["solar"][:every])
        hours = (np.arange(every) * 0.25) % 24
        end = []
        m.simulate_trajectory_with_dhw(b["state"], sp[:every], dh[:every], ws, start_hour=0.0, dt_hours=0.25,
                                       dhw_draw_rates=m.dhw_draw_rates(hours) if c["dhw"] else None, end_state=end)
        b1 = L.build(cell)
        opt = b1["optimizer"]; opt._prev_shipped_plan = sp
        sl = slice(every, every + H)
        inp = solve_inputs(initial_state=end[-1], prices=series["prices"][sl], outdoor_temps=series["outdoor"][sl],
                           wind_speeds=series["wind"][sl], precipitation=series["rain"][sl],
                           solar_radiation=series["solar"][sl], start_time=START + timedelta(hours=0.25 * every))
        r1, calls1, _, _ = L.solve(None, opt=opt, inputs=inp)
        ship = [k for k in calls1 if k.commit is not None]
        call = ship[-1]
        px, ps = L.shipped_of(call)
        cand = np.concatenate([bx[every:], px[-every:]])[: px.size]
        cx, cs = L.committed(call, cand)
        return {"cell": cell, "every": every, "head_same": head_same, "replan_score": ps,
                "shifted_challenger_score": cs, "masked": bool(ps <= cs + 1e-9), "residual": ps - cs,
                "cell_cpu": round(time.process_time() - t0, 3), "cell_thread_cpu": round(time.thread_time() - tt0, 3)}
    except Exception as e:  # noqa: BLE001
        import traceback
        return {"cell": cell, "error": f"{type(e).__name__}: {e}", "tb": traceback.format_exc()[-1500:]}


def gap_cells(min_gap):
    out = []
    for line in open(os.path.join(HERE, "race_out", "cells.jsonl")):
        d = json.loads(line)
        if "error" in d or d["cell"].startswith("coord/"):
            continue
        if d["cell_gap"] > min_gap:
            out.append(d["cell"])
    return sorted(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-gap", type=float, default=0.01)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--every", type=int, default=4)
    ap.add_argument("--days", type=int, default=1)
    ap.add_argument("--cells", default="")
    ap.add_argument("--perturb", default="")
    ap.add_argument("--tag", default="")
    ap.add_argument("--mask", action="store_true", help="one re-plan masking test on every gap cell")
    a = ap.parse_args()
    if a.mask:
        return run_mask(a)
    cells = [l.strip() for l in open(a.cells) if l.strip()] if a.cells else gap_cells(a.min_gap)
    tag = a.tag or f"d{a.days}e{a.every}{('.' + a.perturb) if a.perturb else ''}"
    path = os.path.join(HERE, "loop_out", f"cells.{tag}.jsonl")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    done = set()
    if os.path.exists(path):
        done = {json.loads(l)["cell"] for l in open(path) if "error" not in json.loads(l)}
    todo = [c for c in cells if c not in done]
    from multiprocessing import get_context
    with open(path, "a") as fh, get_context("fork").Pool(a.workers) as pool:
        for i, rec in enumerate(pool.imap_unordered(one, [(c, a.every, a.days, a.perturb) for c in todo])):
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            print(f"[{i + 1}/{len(todo)}] {rec['cell']} {rec.get('same', {}).get('realised_gap', rec.get('error'))}",
                  flush=True)
    summarize(path, cells)


def run_mask(a):
    best = {}
    for line in open(os.path.join(HERE, "race_out", "cells.jsonl")):
        d = json.loads(line)
        if "error" in d or d["cell"].startswith("coord/") or d["cell_gap"] <= a.min_gap:
            continue
        rows = [r for r in d["calls"] if r["ships"] and "best_x" in r]
        if rows:
            best[d["cell"]] = rows[-1]["best_x"]
    path = os.path.join(HERE, "loop_out", f"mask.e{a.every}.jsonl")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    done = set()
    if os.path.exists(path):
        done = {json.loads(l)["cell"] for l in open(path) if "error" not in json.loads(l)}
    todo = [c for c in sorted(best) if c not in done]
    from multiprocessing import get_context
    with open(path, "a") as fh, get_context("fork").Pool(a.workers) as pool:
        for i, rec in enumerate(pool.imap_unordered(mask_one, [(c, a.every, best[c]) for c in todo])):
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            print(f"[{i + 1}/{len(todo)}] {rec['cell']} masked={rec.get('masked', rec.get('error'))}", flush=True)
    R = [json.loads(l) for l in open(path)]
    R = [r for r in R if "error" not in r and r["cell"] in best]
    hs = [r for r in R if r["head_same"]]
    print(f"RESULT gap_cells={len(best)} (cell_gap > {a.min_gap})")
    print(f"RESULT examined={len(R)}")
    print(f"RESULT head_same={len(hs)} masked_of_head_same={sum(r['masked'] for r in hs)}")
    print(f"RESULT head_differs={len(R) - len(hs)}")
    import d0s3_lib as L
    pc = sum(r.get("cell_cpu", 0) for r in R); tc = sum(r.get("cell_thread_cpu", 0) for r in R)
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={L.load1():.2f}")
    print(f"RESULT swapins={L.swapins()}")


def summarize(path, cells):
    import d0s3_lib as L
    recs = {}
    for line in open(path):
        d = json.loads(line)
        if "error" not in d:
            recs[d["cell"]] = d
    R = [recs[c] for c in cells if c in recs]
    print(f"RESULT universe={len(cells)} gap cells")
    print(f"RESULT examined={len(R)} cells")
    for tag in ("same", "mis"):
        for flat in (False, True):
            sub = [r[tag] for r in R if (r["cell"].split("/")[0] == "flat") == flat]
            if not sub:
                continue
            g = np.array([s["realised_gap"] for s in sub])
            print(f"RESULT {tag}_{'flat' if flat else 'nonflat'}: n={len(g)} realised_gap_pos={(g > 1e-4).sum()} "
                  f"neg={(g < -1e-4).sum()} mean={g.mean():.5f} min={g.min():.5f} max={g.max():.5f} "
                  f"loo_drop_max_mean={(np.sort(g)[:-1].mean() if len(g) > 1 else float('nan')):.5f}")
    pc = sum(r.get("cell_cpu", 0) for r in R); tc = sum(r.get("cell_thread_cpu", 0) for r in R)
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={L.load1():.2f}")
    print(f"RESULT swapins={L.swapins()}")


def list_universe(min_gap=1e-4):
    """D0.M6's enumerator: every race cell (grid and coordinator capture) whose
    shipped call has a gap above the race's GAP_EPS, one per line."""
    for line in open(os.path.join(HERE, "race_out", "cells.jsonl")):
        d = json.loads(line)
        if "error" not in d and d["cell_gap"] > min_gap:
            print(d["cell"])


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        list_universe()
    else:
        main()
