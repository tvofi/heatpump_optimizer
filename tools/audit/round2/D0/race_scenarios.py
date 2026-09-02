"""D0 race over the feature scenarios of tests/golden.py (valve, wood, tariff, horizon...).

Metric: as race_grid.py -- per scenario, production objective minus the best
comfort-parity challenger objective on the exact recorded objective, plus the
restart gap and the projected gradient at production's answer. The scenarios
are built with tests/golden.py:make and the same extra inputs golden.capture
passes (PV surplus, external heat, fuse caps, margins), so the solve is the
one the golden fixtures pin.

Command:
    PYTHONPATH=tests/hastub python tools/audit/round2/D0/race_scenarios.py
    ... race_scenarios.py --only valve        # substring filter
Perturbation: D0_PERTURB=solves3|ftol9|restart as in race_grid.py.

Expected on baseline c398fc8: single-zone scenarios tie (gap < 1e-3);
two-zone scenarios show gaps of the same order as race_grid's tz cells.
Counts exact; CPU provisional. Writes only tools/audit/round2/D0/out/.
"""
from __future__ import annotations

import os

for _threads in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_threads, "1")

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, "tools/audit/round2/D0")

import numpy as np  # noqa: E402

import d0lib as L  # noqa: E402
import golden  # noqa: E402  (tests/golden.py: __main__-guarded)
from race_grid import apply_perturbation  # noqa: E402

OUT = Path("tools/audit/round2/D0/out")

NAMES = [
    "winter_two_zone_dhw", "winter_two_zone_no_dhw", "shoulder_two_zone",
    "tariff_plus_two_zone", "valve_storage", "valve_storage_low_target",
    "valve_storage_smart_write", "valve_storage_small_tank", "wood_two_tank",
    "wood_two_tank_smart_write", "wood_coil", "valve_upper_direct_slab",
    "everything_on", "horizon_48h", "horizon_6h", "capacity_tariff",
    "capacity_tariff_15min", "cycling_cost", "extreme_prices", "negative_prices",
    "fuse_guard", "capacity_curve", "away_setback", "wide_band", "narrow_band",
    "start_below_band", "start_above_band", "confidence_margins", "price_risk",
    "peak_masked", "building_preset", "dhw_large_tank", "dhw_cold_tank",
]


def inputs_for(name: str, built: dict):
    opt = built["optimizer"]
    n = len(built["prices"])
    kw = {}
    if name in golden.PARTIAL_PRICE_SCENARIOS:
        kw["price_known"] = golden.known_mask(n, int(n * 0.55))
    if name in golden.RISK_SCENARIOS and "price_known" in kw:
        kw["price_sigma"] = np.where(kw["price_known"], 0.0, 0.5)
    if name in golden.PV_SCENARIOS:
        kw["pv_surplus"] = golden.pv_surplus_for(n, built["solar"])
    if name in golden.EXTERNAL_HEAT_SCENARIOS:
        kw["external_heat_kw"] = golden.external_heat_for(n)
    if name in golden.CAP_SCENARIOS:
        kw["power_caps_extra"] = np.full(n, opt.model.params.max_electrical_power * 0.6)
    if name in golden.ENVELOPE_CAP_SCENARIOS:
        p_max = opt.model.params.max_electrical_power
        kw["power_caps_extra"] = np.clip(p_max * np.linspace(1.0, 0.6, n), 0.6 * p_max, p_max)
    if name in golden.SNOW_SCENARIOS:
        liquid = np.where(np.arange(n) < n // 2, 0.0, 1.0)
        built["rain"] = np.asarray(built["rain"], dtype=float) * liquid
    if name in golden.MARGIN_SCENARIOS:
        kw["min_temp_margins"] = np.minimum(0.1 + np.arange(n) * (0.7 / max(n - 1, 1)), 0.8)
        kw["min_temp_floors"] = np.full(n, 18.5)
    return kw


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--random", type=int, default=3)
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    perturb = os.environ.get("D0_PERTURB") or None
    patches = apply_perturbation(perturb)
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    clock = L.CpuClock()
    for name in NAMES:
        if a.only and a.only not in name:
            continue
        spec = golden.SCENARIOS[name]
        built = golden.make(**spec)
        kw = inputs_for(name, built)
        opt = built["optimizer"]
        cell = L.Cell(
            name=name, optimizer=opt, model=opt.model, state=built["state"],
            prices=built["prices"], outdoor=built["outdoor"], wind=built["wind"],
            rain=built["rain"], solar=built["solar"],
            two_zone=bool(opt.model.params.two_zone_enabled),
            dhw=bool(opt.model.params.dhw_enabled), hours=int(spec.get("hours", 24)),
            price_profile=spec.get("price_profile", "winter_typical"),
            weather_profile=spec.get("weather_profile", "winter_cold"),
        )
        with clock:
            with L.Recorder() as rec:
                res = cell.solve(**kw)
            call = rec.adopted_call(res)
            if call is None:
                print(f"  {name}: no adopted call among {len(rec.calls)} (status {res.status!r}); skipped")
                continue
            raced = L.race(cell, call, random_starts=a.random,
                           include=("third", "restart", "budget", "seeds", "random", "polish"),
                           bang_fracs=(0.6, 0.8, 1.0, 1.2))
            row = L.summarize(cell, call, raced, verbose=False)
        row.update({"tz": cell.two_zone, "dhw": cell.dhw, "n_calls": len(rec.calls),
                    "adopted_call": call.index, "status": res.status,
                    "predicted_cost": float(res.predicted_cost),
                    "arms": {arm.name: {"score": arm.score, "energy": arm.energy, "nit": arm.nit,
                                        "nfev": arm.nfev, "under": arm.feas["under"], "over": arm.feas["over"],
                                        "min_temp": arm.feas["min_temp"], "msg": arm.message,
                                        "parity": L.parity_ok(raced["production"], arm)}
                             for arm in raced["arms"]}})
        if a.verbose:
            for arm in sorted(raced["arms"], key=lambda x: x.score)[:8]:
                print(f"      {arm.name:<22} obj {arm.score:10.4f} energy {arm.energy:8.2f} under {arm.feas['under']:.4f} "
                      f"over {arm.feas['over']:.4f} min {arm.feas['min_temp']:.2f} nit {arm.nit} parity {L.parity_ok(raced['production'], arm)} [{arm.message[:32]}]")
        rows.append(row)
        print(f"  {name:<28} {'tz' if cell.two_zone else 'sz'} calls {len(rec.calls)} obj {row['prod_score']:9.3f} "
              f"gap {row['gap_feasible']:+.4f} ({row['gap_feasible_pct']:.2f} %) restart {row['gap_restart']:+.4f} "
              f"pg {row['prod_pg']:.2g} nit {row['prod_nit']} [{row['best_feasible']}] bill {row['prod_energy']:.2f}")
    for p in reversed(patches):
        p.stop()
    (OUT / f"race_scenarios_{perturb or 'baseline'}{'_' + a.only if a.only else ''}.json").write_text(
        json.dumps({"baseline_sha": "c398fc84eec25fc44b60d74aae05b9a2da205884", "rows": rows}, indent=1, default=float))
    thr = 1e-3
    print()
    print(f"RESULT scenarios={len(rows)} count")
    for label, sel in (("sz", [r for r in rows if not r["tz"]]), ("tz", [r for r in rows if r["tz"]])):
        if not sel:
            continue
        g = np.array([r["gap_feasible"] for r in sel]); pct = np.array([r["gap_feasible_pct"] for r in sel])
        rs = np.array([r["gap_restart"] for r in sel])
        print(f"RESULT scenarios_{label}={len(sel)} count")
        print(f"RESULT scenarios_with_gap_{label}={int(np.sum(g > thr))} count")
        print(f"RESULT scenarios_restart_improves_{label}={int(np.sum(rs > thr))} count")
        print(f"RESULT scenarios_mean_gap_pct_{label}={pct.mean():.3f} pct_of_objective")
        print(f"RESULT scenarios_max_gap_pct_{label}={pct.max():.3f} pct_of_objective")
        if len(sel) >= 2:
            loo = np.delete(pct, np.argmax(pct))
            print(f"RESULT scenarios_loo_mean_gap_pct_{label}={loo.mean():.3f} pct_of_objective")
    print("RESULT provisional=true flag")
    L.footer(clock)
    return 0


if __name__ == "__main__":
    sys.exit(main())
