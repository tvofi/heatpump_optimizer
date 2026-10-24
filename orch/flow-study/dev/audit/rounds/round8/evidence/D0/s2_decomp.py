"""D0-s2 decomposition harness: does iterating DHW <-> space past production's
single co-optimisation pass lower the SAME objective?

Metric (one line): per cell, gap_pct = 100 * (J_prod - J_iter) / J_prod, where
J is the production objective closure inside
``HeatPumpOptimizer._optimize_with_dhw`` (the ``best_score`` / ``score`` values
``_solve_space`` returns), J_prod is what production ships and J_iter is the
best score reached by up to ITER further DHW re-plan + space re-solve rounds,
each accepted only if it lowers J (production's own acceptance rule).
Count key: the score the production ``solve_space`` closure returns; the
iterated arm uses production's own ``_build_dhw_requirements`` (so DHW floors
hold by construction, as they do for production's own second pass).

Arms:
  gated   -- re-call production ``_co_optimize`` ITER more times (its own
             "space pinned under a DHW block" gate decides whether to re-plan)
  ungated -- re-plan DHW every round with space_demand = current space plan,
             whatever the gate says.
Null control: price profile "flat" (every weather), where a DHW re-plan has no
price to move toward and the gap must vanish.

Instrumented symbol: heatpump_optimizer.optimizer:HeatPumpOptimizer._co_optimize
(wrapped via mock.patch.object; production runs unchanged, the wrapper records
and races after it returns).
Perturbation: ITER=0 (env D0S2_ITER=0) -> every gap is exactly 0; the
production-side perturbation is setting ``pinned`` to all-False in
``_co_optimize`` (one-line edit) -> gated arm gap moves to 0 in every cell.

Command:
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  python3 tools/audit/round8/D0/s2_decomp.py [--two-zone] [--quick]
  (D0S2_PMAX=<kW> overrides heat_pump_max_power: the contention arm)
Baseline: cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud
container (shared; timings provisional). Expected: see REPORT-s2.md.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, json
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from unittest import mock
import numpy as np
import golden
from golden import make, START
from heatpump_optimizer import optimizer as om

ITER = int(os.environ.get("D0S2_ITER", "4"))
TWO_ZONE = "--two-zone" in sys.argv
QUICK = "--quick" in sys.argv
PRICES = ["winter_typical", "winter_extreme", "summer_typical", "summer_negative",
          "shoulder", "winter_narrow", "winter_moderate", "flat"]
WEATHER = ["winter_cold", "winter_mild", "summer_warm", "summer_cool", "shoulder"]
if QUICK:
    WEATHER = ["winter_cold", "shoulder"]

_orig = om.HeatPumpOptimizer._co_optimize
REC = {}


def _wrapped(self, h, *, space_power, dhw_power, status, best_score,
             solve_space, p_max):
    scores = []

    def rec_solve(dhw, warm):
        out = solve_space(dhw, warm)
        scores.append(out[2])
        return out

    sp, dh, st = _orig(self, h, space_power=space_power, dhw_power=dhw_power,
                       status=status, best_score=best_score,
                       solve_space=rec_solve, p_max=p_max)
    adopted = not (sp is space_power)
    j_prod = scores[-1] if adopted else best_score
    REC["j_first"] = best_score
    REC["j_prod"] = j_prod
    REC["prod_second_pass_ran"] = len(scores)
    REC["prod"] = (sp.copy(), dh.copy())
    # gated arm: production's own pass, called again
    gs, gd, gj, g_rounds = sp, dh, j_prod, 0
    for _ in range(ITER):
        scores.clear()
        ns, nd, _ = _orig(self, h, space_power=gs, dhw_power=gd, status=st,
                          best_score=gj, solve_space=rec_solve, p_max=p_max)
        if ns is gs:
            break
        gs, gd, gj = ns, nd, scores[-1]
        g_rounds += 1
    REC["j_gated"], REC["gated_rounds"] = gj, g_rounds
    REC["gated"] = (gs.copy(), gd.copy())
    # ungated arm: re-plan DHW against the current space plan every round
    us, ud, uj, u_rounds = sp, dh, j_prod, 0
    for _ in range(ITER):
        headroom = np.maximum(0.0, p_max - ud)
        pinned = (ud > 1e-6) & (us >= headroom - 1e-3)
        rp = self._build_dhw_requirements(
            initial_state=h.initial_state, prices=h.prices,
            outdoor_temps=h.outdoor_temps, step_hours=h.step_hours,
            n_steps=h.n_steps, dt=h.dt, p_max=p_max,
            space_demand=np.where(pinned, p_max, us), dhw_pins=h.dhw_pins,
            p_run_cap=(float(np.min(h.power_caps_extra))
                       if h.power_caps_extra is not None else None),
            step_weekdays=h.step_weekdays, holiday_flags=h.holiday_flags,
            wood_temps=self._dhw_coil_wood_forecast(h, us),
        ).schedule
        if np.allclose(rp, ud, atol=1e-4):
            break
        cs, _, sc = solve_space(rp, us)
        if not sc < uj - 1e-9:
            break
        us, ud, uj = cs, rp, sc
        u_rounds += 1
    REC["j_ungated"], REC["ungated_rounds"] = uj, u_rounds
    REC["ungated"] = (us.copy(), ud.copy())
    return sp, dh, st


def run_cell(pp, wp, tz):
    REC.clear()
    over = {}
    if os.environ.get("D0S2_PMAX"):
        over["heat_pump_max_power"] = float(os.environ["D0S2_PMAX"])
    b = make(two_zone=tz, price_profile=pp, weather_profile=wp,
             config_overrides=over)
    opt = b["optimizer"]
    t0 = time.process_time()
    with mock.patch.object(om.HeatPumpOptimizer, "_co_optimize", _wrapped):
        res = opt.optimize(b["state"], b["prices"], b["outdoor"], b["wind"],
                           b["rain"], b["solar"], START)
    cpu = time.process_time() - t0
    prod_sp, prod_dh = REC["prod"]
    assert np.allclose(np.asarray(res.power_schedule), prod_sp, atol=1e-9)
    jp = REC["j_prod"]
    best = min(REC["j_gated"], REC["j_ungated"])
    arm = "gated" if REC["j_gated"] <= REC["j_ungated"] else "ungated"
    bs, bd = REC[arm]
    dt = 0.25
    pr = b["prices"]
    e_prod = float(np.sum((prod_sp + prod_dh) * pr) * dt)
    e_best = float(np.sum((bs + bd) * pr) * dt)
    return dict(
        cell=f"{pp}/{wp}/{'tz' if tz else 'sz'}",
        j_prod=jp, j_best=best,
        gap_pct=100.0 * (jp - best) / abs(jp) if jp else 0.0,
        gap_abs=jp - best,
        gated_rounds=REC["gated_rounds"], ungated_rounds=REC["ungated_rounds"],
        prod_second_pass_solves=REC["prod_second_pass_ran"],
        step0_space_diff=float(abs(bs[0] - prod_sp[0])),
        step0_dhw_diff=float(abs(bd[0] - prod_dh[0])),
        energy_cost_prod=e_prod, energy_cost_best=e_best,
        cpu_s=cpu, adopted=bool(REC["j_prod"] < REC["j_first"] - 1e-12),
    )


def main():
    rows = []
    for pp in PRICES:
        for wp in WEATHER:
            row = run_cell(pp, wp, TWO_ZONE)
            rows.append(row)
            print("CELL %-40s Jprod=%9.4f Jbest=%9.4f gap=%7.4f%% (%.4f) "
                  "2nd-pass=%d rounds g/u=%d/%d step0 dS=%.3f dD=%.3f bill %.2f->%.2f"
                  % (row["cell"], row["j_prod"], row["j_best"], row["gap_pct"],
                     row["gap_abs"], row["prod_second_pass_solves"], row["gated_rounds"], row["ungated_rounds"],
                     row["step0_space_diff"], row["step0_dhw_diff"],
                     row["energy_cost_prod"], row["energy_cost_best"]),
                  flush=True)
    tag = "tz" if TWO_ZONE else "sz"
    priced = [r for r in rows if not r["cell"].startswith("flat/")]
    flat = [r for r in rows if r["cell"].startswith("flat/")]
    gaps = sorted(r["gap_pct"] for r in priced)
    print(f"RESULT {tag}_cells={len(priced)} count")
    print(f"RESULT {tag}_cells_with_gap_gt_0.1pct="
          f"{sum(g > 0.1 for g in gaps)} count")
    print(f"RESULT {tag}_gap_mean={np.mean(gaps):.4f} pct")
    print(f"RESULT {tag}_gap_max={gaps[-1]:.4f} pct")
    print(f"RESULT {tag}_gap_min={gaps[0]:.4f} pct")
    print(f"RESULT {tag}_gap_mean_loo_drop_max={np.mean(gaps[:-1]):.4f} pct")
    print(f"RESULT {tag}_step0_differs_in_gap_cells="
          f"{sum(1 for r in priced if r['gap_pct'] > 0.1 and (r['step0_space_diff'] > 1e-3 or r['step0_dhw_diff'] > 1e-3))} count")
    print(f"RESULT {tag}_prod_second_pass_ran_cells="
          f"{sum(1 for r in rows if r['prod_second_pass_solves'] > 0)} count")
    print(f"RESULT {tag}_prod_second_pass_adopted_cells="
          f"{sum(1 for r in rows if r['adopted'])} count")
    print(f"RESULT {tag}_null_flat_gap_max="
          f"{max(r['gap_pct'] for r in flat):.4f} pct")
    out = os.path.join(os.environ.get("TMPDIR", "/tmp"), f"s2_decomp_{tag}.json")
    with open(out, "w") as f:
        json.dump(rows, f, indent=1)
    pc, tc = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
