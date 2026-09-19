#!/usr/bin/env python3
"""D0 round 5 -- the polished point `_multi_start_minimize` computes and throws away.

METRIC (one line): per cell, the relative gap in percent between the
`OptimizationResult.objective_value` the production `HeatPumpOptimizer.optimize`
seam delivers on fixed inputs and the objective_value it delivers on the SAME
inputs under a one-line edit that stops `_lbfgsb_restart` discarding a strictly
cheaper point; positive means production shipped the more expensive plan.

Instrumented symbols (production, hooked / driven):
  heatpump_optimizer.optimizer:_multi_start_minimize
  heatpump_optimizer.optimizer:_lbfgsb_restart
  heatpump_optimizer.optimizer:_LBFGSB_RESTART_KEEP_REL   (module constant)

Arms
  shipped    : the tree as it stands (KEEP = 2e-2).
  keep0      : PERTURBATION -- `optimizer._LBFGSB_RESTART_KEEP_REL` set to 0.0.
               The restart then keeps any strict improvement instead of only a
               drop of more than 2 % of the prior score. Restored in a finally.
  percand    : the brief's "more L-BFGS-B starts" challenger. For the captured
               production call, each candidate `g` is handed to the production
               `_multi_start_minimize` on its own -- same objective, same bounds,
               same args, same maxiter, same batch_objective, so each candidate
               gets the production polish. The min over candidates is the best
               feasible point production code reaches on this objective.

Expected (baseline eaa2a06, Apple M1, numpy 2.4.6 / scipy 1.17.1, load1 10-25):
  RESULT cells_priced              56       exact
  RESULT cells_with_gap_keep0      10       +-2   (cells > 0.01 %)
  RESULT gap_keep0_pct_max          1.1703  +-0.02
  RESULT gapped_mean                0.2025  +-0.02
  RESULT gapped_loo_drop_most_favourable 0.0949  +-0.02
  RESULT gap_keep0_pct_flat_max     0.0194  +-0.02  (null control)
  RESULT gap_keep0_pct_max_over_flat_max 60.3 +-5
  RESULT worst_cell_sek_delta      -0.6789  +-0.02  SEK/day on an 11.338 SEK bill
  RESULT gap_percand_pct_max        1.4023  +-0.02
A run whose gap_keep0_pct_max is ~0 has measured a fixed tree, not this one.

Command (from the export root):
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D0/restart_race.py \
      --weathers winter_cold,winter_mild
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D0/restart_race.py --quick
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D0/restart_race.py --pass=1
The default grid is all five weather profiles; `--weathers` narrows it (this
run used winter_cold,winter_mild -- the two heating-relevant profiles -- to fit
the round-5 box budget).

Counted-number key: the objective VALUE the production `optimize()` returns
(`OptimizationResult.objective_value`), not a counter derived from bounds or
from the harness's own records. Both arms read it from a real `optimize()`
call on the same machine in the same process.

Findings harness (FROZEN EVIDENCE, deliberately no `live-header` marker):
its header records the round-5 baseline, so on a fixed main it prints the
fixed numbers and a forced comparison would red on success.
"""
import os, sys, time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
assert os.path.isdir(os.path.join(ROOT, "custom_components")), ROOT
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "custom_components"))

import argparse
import numpy as np
from datetime import datetime
from unittest import mock

from profiles import prices, weather, house, DT, N           # noqa: E402
from heatpump_optimizer.thermal_model import (               # noqa: E402
    ThermalModel, ThermalParameters, ThermalState)
from heatpump_optimizer.optimizer import (                   # noqa: E402
    HeatPumpOptimizer, OptimizationConfig)
from heatpump_optimizer import optimizer as optmod           # noqa: E402

BASELINE_SHA = "eaa2a06af16a1b5b006f58a0f36cc92131f80225"
MACHINE = "Apple M1, 8 GB, macOS 25.6.0, numpy 2.4.6, scipy 1.17.1"

PRICE_PROFILES = ("winter_typical", "winter_extreme", "summer_typical",
                  "summer_negative", "shoulder", "winter_narrow",
                  "winter_moderate", "flat")
WEATHER_PROFILES = ("winter_cold", "winter_mild", "summer_warm",
                    "summer_cool", "shoulder")
GAP_TOL = 0.01          # percent: cells at or below this count as no gap
START = datetime(2026, 1, 15)


def thread_factor():
    return (time.process_time() / time.thread_time()) if time.thread_time() else 0.0


def swapins():
    try:
        import psutil
        return int(psutil.swap_memory().sin)
    except Exception:
        return -1


def load1():
    try:
        return float(os.getloadavg()[0])
    except Exception:
        return -1.0


def mksetup(tz, price_p, weather_p, dhw, hours):
    cfg = house(two_zone=tz)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = dhw
    m = ThermalModel(p)
    opt = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=hours, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pr = prices(price_p, START)
    ot, wi, ra, so = weather(weather_p, START)
    st = ThermalState(
        room_temperature=21.0, slab_temperature=22.0,
        outdoor_temperature=float(ot[0]), upper_floor_temperature=21.0,
        lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
        dhw_temperature=48.0)
    return opt, m, pr, ot, wi, ra, so, st


def shipped(tz, price_p, weather_p, dhw, hours):
    opt, m, pr, ot, wi, ra, so, st = mksetup(tz, price_p, weather_p, dhw, hours)
    r = opt.optimize(st, pr, ot, wi, ra, so, START)
    return opt, m, pr, ot, wi, ra, so, st, r


def keep0(tz, price_p, weather_p, dhw, hours):
    opt, m, pr, ot, wi, ra, so, st = mksetup(tz, price_p, weather_p, dhw, hours)
    old = optmod._LBFGSB_RESTART_KEEP_REL
    optmod._LBFGSB_RESTART_KEEP_REL = 0.0
    try:
        r = opt.optimize(st, pr, ot, wi, ra, so, START)
    finally:
        optmod._LBFGSB_RESTART_KEEP_REL = old
    return r


def capture(tz, price_p, weather_p, dhw, hours):
    """Re-run the shipped solve, recording every _multi_start_minimize call."""
    cap = []
    real = optmod._multi_start_minimize

    def rec(objective, candidates, bounds, *a, **kw):
        res = real(objective, candidates, bounds, *a, **kw)
        cap.append(dict(objective=objective,
                        candidates=[np.array(c, dtype=float) for c in candidates],
                        bounds=list(bounds), kw=dict(kw), res=res))
        return res

    opt, m, pr, ot, wi, ra, so, st = mksetup(tz, price_p, weather_p, dhw, hours)
    with mock.patch.object(optmod, "_multi_start_minimize", rec):
        r = opt.optimize(st, pr, ot, wi, ra, so, START)
    return cap, r


def best_objective(opt, m, st, ot, wi, ra, so, pr, power, dhw_power):
    """Score a plan with the production objective the solve used.

    The captured call's closure is the objective; a fresh objective is built
    here by re-running the capture-free solve is not possible, so score with
    `optimize`'s own reported value where available and, for a challenger
    point, with the captured closure.
    """
    raise NotImplementedError


def percand_gap(tz, price_p, weather_p, dhw, hours):
    """Best feasible point production code reaches, candidate by candidate."""
    cap, r = capture(tz, price_p, weather_p, dhw, hours)
    out = []
    for c in cap:
        obj = c["objective"]
        kw = c["kw"]
        args = kw.get("args", ())
        bnds = c["bounds"]
        lo = np.array([b[0] for b in bnds])
        hi = np.array([b[1] for b in bnds])
        x_sh = np.clip(np.asarray(c["res"].x, dtype=float), lo, hi)
        f_sh = float(obj(x_sh, *args))
        f_best = f_sh
        per = []
        for g in c["candidates"]:
            rr = optmod._multi_start_minimize(
                obj, [g], bnds, args=args, maxiter=kw.get("maxiter"),
                batch_objective=kw.get("batch_objective"), fd_eps=1e-4)
            f = float(obj(np.clip(np.asarray(rr.x, dtype=float), lo, hi), *args))
            per.append(f)
            if f < f_best:
                f_best = f
        out.append(dict(n_cand=len(c["candidates"]), f_shipped=f_sh,
                        f_best_cand=f_best, per_cand=per,
                        maxiter=kw.get("maxiter")))
    return out, r


def feasibility(m, st, ot, wi, ra, so, power, min_floor=16.5):
    """Comfort-floor violation in degree-steps and the room min, from the model."""
    room, slab, up, lo, _, _, _ = m.simulate_trajectory(
        st, np.asarray(power, dtype=float), ot, wi, ra, so, DT)
    rr = room[1:]
    return float(np.maximum(0.0, min_floor - rr).sum()), float(rr.min()), float(rr.max())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="pas", default="all",
                    choices=("1", "2", "all"))
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--weathers", default="",
                    help="comma-separated weather profiles; default all five, "
                         "--quick forces winter_cold")
    ap.add_argument("--hours", type=int, default=24)
    a = ap.parse_args()

    prices_used = PRICE_PROFILES
    if a.weathers:
        weathers_used = tuple(w for w in a.weathers.split(",") if w)
    elif a.quick:
        weathers_used = ("winter_cold",)
    else:
        weathers_used = WEATHER_PROFILES
    tzs = (False, True)
    dhws = (False, True)

    t_start = time.monotonic()
    rows = []
    print(f"# baseline {BASELINE_SHA}  machine {MACHINE}")
    print(f"# pass1 grid: {len(prices_used)} prices x {len(weathers_used)} weather "
          f"x 2 topologies x 2 dhw, horizon {a.hours} h")

    if a.pas in ("1", "all"):
        for pp in prices_used:
            for wp in weathers_used:
                for tz in tzs:
                    for dhw in dhws:
                        t0 = time.monotonic()
                        opt0, m, pr, ot, wi, ra, so, st = mksetup(tz, pp, wp, dhw, a.hours)
                        r0 = opt0.optimize(st, pr, ot, wi, ra, so, START)
                        o0 = float(r0.objective_value)
                        c0 = float(r0.predicted_cost)
                        r1 = keep0(tz, pp, wp, dhw, a.hours)
                        o1 = float(r1.objective_value)
                        c1 = float(r1.predicted_cost)
                        gap = 100.0 * (o0 - o1) / max(abs(o0), 1e-12)
                        rows.append(dict(price=pp, weather=wp, tz=tz, dhw=dhw,
                                         obj0=o0, obj1=o1, sek0=c0, sek1=c1,
                                         gap_pct=gap, sec=time.monotonic() - t0))
                        print(f"CELL {pp} {wp} tz={int(tz)} dhw={int(dhw)} "
                              f"obj {o0:.6f}->{o1:.6f} gap={gap:.4f}% "
                              f"sek {c0:.3f}->{c1:.3f} d={c0 - c1:.4f} "
                              f"[{time.monotonic() - t0:.1f}s]", flush=True)

    priced = [r for r in rows if r["price"] != "flat"]
    flat = [r for r in rows if r["price"] == "flat"]
    gapped = [r for r in priced if r["gap_pct"] > GAP_TOL]
    flat_gapped = [r for r in flat if r["gap_pct"] > GAP_TOL]

    if a.pas in ("1", "all") and rows:
        gaps = [r["gap_pct"] for r in rows if r["price"] != "flat"]
        print("\n--- pass 1 aggregates (priced cells) ---")
        print(f"RESULT cells_total={len(rows)} count")
        print(f"RESULT cells_priced={len(priced)} count")
        print(f"RESULT cells_with_gap_keep0={len(gapped)} count")
        print(f"RESULT gap_keep0_pct_max={max(gaps):.4f} percent")
        print(f"RESULT gap_keep0_pct_min={min(gaps):.4f} percent")
        print(f"RESULT gap_keep0_pct_max_over_flat_max="
              f"{(max(gaps) / max(max((r['gap_pct'] for r in flat), default=0.0), 1e-9)):.1f} ratio")
        # The aggregate that matters is over the cells that HAVE a gap: a mean
        # over all 56 priced cells is a referendum on row counts (46 of them are
        # exactly zero), which is what COMMON.md refuses as an aggregate.
        if gapped:
            gg = sorted(r["gap_pct"] for r in gapped)
            print(f"RESULT gapped_cells={len(gg)} count")
            print(f"RESULT gapped_range_min={gg[0]:.4f} percent")
            print(f"RESULT gapped_range_max={gg[-1]:.4f} percent")
            print(f"RESULT gapped_mean={sum(gg) / len(gg):.4f} percent")
            print(f"RESULT gap_keep0_pct_loo_drop_most_favourable="
                  f"{(sum(gg) - gg[-1]) / max(len(gg) - 1, 1):.4f} percent")
            print(f"RESULT sek_delta_max={max(r['sek0'] - r['sek1'] for r in gapped):.4f} SEK_per_day")
            worst = max(gapped, key=lambda r: r["sek0"] - r["sek1"])
            print(f"RESULT worst_cell_sek_delta={worst['sek0'] - worst['sek1']:.4f} SEK_per_day")
            print(f"RESULT worst_cell_bill={worst['sek0']:.3f} SEK_per_day")
            print(f"RESULT worst_cell_sek_share="
                  f"{100.0 * (worst['sek0'] - worst['sek1']) / max(abs(worst['sek0']), 1e-9):.2f} percent_of_bill")
            n_worse = sum(1 for r in gapped if r["sek0"] - r["sek1"] < 0)
            print(f"RESULT gapped_cells_where_money_rises={n_worse} count")
        if flat:
            print(f"RESULT gap_keep0_pct_flat_max="
                  f"{max(r['gap_pct'] for r in flat):.4f} percent")
            print(f"RESULT gap_keep0_pct_flat_min="
                  f"{min(r['gap_pct'] for r in flat):.4f} percent")

    if a.pas in ("2", "all") and gapped:
        print("\n--- pass 2: per-candidate challenger + feasibility parity ---")
        print(f"# flat cells with a keep0 gap (control for this arm): "
              f"{[(r['price'], round(r['gap_pct'], 4)) for r in flat_gapped]}")
        best = 0.0
        for r0 in list(gapped) + list(flat_gapped):
            t0 = time.monotonic()
            try:
                out, rr = percand_gap(r0["tz"], r0["price"], r0["weather"],
                                      r0["dhw"], a.hours)
            except Exception as e:                       # pragma: no cover
                print(f"CHAL {r0['price']} {r0['weather']} tz={int(r0['tz'])} "
                      f"dhw={int(r0['dhw'])} failed: {e}", flush=True)
                continue
            for c in out:
                gap = 100.0 * (c["f_shipped"] - c["f_best_cand"]) / max(abs(c["f_shipped"]), 1e-12)
                best = max(best, gap)
                print(f"CHAL {r0['price']} {r0['weather']} tz={int(r0['tz'])} "
                      f"dhw={int(r0['dhw'])} ncand={c['n_cand']} maxiter={c['maxiter']} "
                      f"prod={c['f_shipped']:.6f} bestcand={c['f_best_cand']:.6f} "
                      f"gap={gap:.4f}% per_cand={[round(v, 5) for v in c['per_cand']]} "
                      f"[{time.monotonic() - t0:.1f}s]", flush=True)
            # feasibility parity between the shipped and keep0 plans
            _, m, pr, ot, wi, ra, so, st = mksetup(
                r0["tz"], r0["price"], r0["weather"], r0["dhw"], a.hours)
            r0s = shipped(r0["tz"], r0["price"], r0["weather"], r0["dhw"], a.hours)[-1]
            r0k = keep0(r0["tz"], r0["price"], r0["weather"], r0["dhw"], a.hours)
            vs, mn_s, mx_s = feasibility(m, st, ot, wi, ra, so, np.asarray(r0s.power_schedule))
            vk, mn_k, mx_k = feasibility(m, st, ot, wi, ra, so, np.asarray(r0k.power_schedule))
            dhw_s = min(r0s.dhw_power_schedule) if r0s.dhw_power_schedule else 0.0
            print(f"FEAS {r0['price']} {r0['weather']} tz={int(r0['tz'])} dhw={int(r0['dhw'])} "
                  f"viol_shipped={vs:.6f} viol_keep0={vk:.6f} room_shipped={mn_s:.4f}"
                  f"..{mx_s:.4f} room_keep0={mn_k:.4f}..{mx_k:.4f} dhw_min={dhw_s:.4f}",
                  flush=True)
        print(f"RESULT gap_percand_pct_max={best:.4f} percent")

    print("\n--- measurement conditions ---")
    print(f"RESULT thread_factor={thread_factor():.4f} ratio")
    print(f"RESULT load1={load1():.2f} count")
    print(f"RESULT swapins={swapins()} count")
    _n = os.popen('ps aux | grep -c "[s]tress.py"').read().strip()
    print(f"RESULT concurrent_stress_procs={_n} count")
    print(f"# wall {time.monotonic() - t_start:.1f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
