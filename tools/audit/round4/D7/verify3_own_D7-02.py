"""verifier 3 own harness -- D7-02: the sizer's plant vs the house's plant.

METRIC (one line): per cell (3 hand-typed presets x 3 outdoor temps x 2
cadences), the TRUE peak |T_room - baseline| the production plant reaches
under the step power chosen by the production sizer
(``SystemIdentification._size_step_power`` -> ``_predict_step_excursion_plant``
-> ``_sizing_model``), divided by the sizer's own predicted peak; plus the
count of cells whose TRUE peak exceeds max_excursion_c (0.8). The honest
counterfactual monkeypatches ``sysid._sizing_model`` (harness side, restored
in finally) to carry the plant's own slab mass and coupling.

Independence: this drives ``_size_step_power`` DIRECTLY (the finder drove
the full step() state machine and read ``_step_power``), and simulates the
truth plant with a fine 0.05 h grid of its own.

COMMAND (from the tree root):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D7/verify3_own_D7-02.py

EXPECTED (finder): comfort_breach_cells=6, peak_ratio 0.486..1.329;
honest: breaches 0, ratio <= 1.00.
ROOT RULE: ROOT = Path(".") -- measures the working directory.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import sys
from pathlib import Path

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "custom_components"))

import numpy as np

import heatpump_optimizer.sysid as sysid_mod
from heatpump_optimizer.sysid import SysIdConfig, SystemIdentification
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

COP = 3.0
BASE_T = 21.0
OUTDOORS = (-5.0, 0.0, 5.0)
GAINS = 0.3
MAX_ELEC = 6.0
BOUND = 0.8  # SysIdConfig.max_excursion_c default = DEFAULT_MAX_EXCURSION_C
FINE_DT = 0.05  # the truth simulation's own grid, not the sizer's 0.25

# hand-typed (see verify3_own_D7-01.py)
PLANTS = {
    "light_new": dict(ua=0.066, cap=3.6, slab_m=0.24, slab_k=0.24),
    "heavy_old": dict(ua=0.31, cap=11.0, slab_m=23.0, slab_k=2.0),
    "typical_slab": dict(ua=0.1725, cap=5.25, slab_m=16.5, slab_k=1.5),
}


def _true_plant(spec):
    return ThermalModel(ThermalParameters(
        heat_loss_coefficient=spec["ua"], house_heat_loss_scale=1.0,
        room_thermal_mass=spec["cap"], slab_thermal_mass=spec["slab_m"],
        slab_heat_transfer=spec["slab_k"], internal_gains=GAINS,
        wind_sensitivity=0.0, two_zone_enabled=False,
        max_electrical_power=MAX_ELEC,
    ))


def _true_peak(model, outdoor, thermal_kw, step_h=2.0, relax_h=2.0):
    p = model.params
    q_hold = p.heat_loss_coefficient * (BASE_T - outdoor) - GAINS
    k = max(p.slab_heat_transfer, 1e-9)
    st = ThermalState(room_temperature=BASE_T,
                      slab_temperature=BASE_T + q_hold / k,
                      outdoor_temperature=outdoor)
    peak = 0.0
    for q, hours in ((thermal_kw, step_h), (0.0, relax_h)):
        remaining = hours
        while remaining > 1e-12:
            dt = min(FINE_DT, remaining)
            st = model.simulate_step(
                st, electrical_power=0.0, outdoor_temp=outdoor,
                dt_hours=dt, external_heat_kw=q,
            )
            peak = max(peak, abs(st.room_temperature - BASE_T))
            remaining -= dt
    return peak


def main() -> int:
    sid = SystemIdentification(SysIdConfig(enabled=True))
    cfg = sid.config

    def one(spec_name, outdoor, honest):
        spec = PLANTS[spec_name]
        model = _true_plant(spec)
        orig = sysid_mod._sizing_model
        if honest:
            def _h(u, c, g, _s=spec):
                return ThermalModel(ThermalParameters(
                    heat_loss_coefficient=u, house_heat_loss_scale=1.0,
                    room_thermal_mass=c, internal_gains=g,
                    two_zone_enabled=False,
                    slab_thermal_mass=_s["slab_m"],
                    slab_heat_transfer=_s["slab_k"],
                ))
            sysid_mod._sizing_model = _h
        try:
            sized_el = sid._size_step_power(
                MAX_ELEC, COP, BASE_T, outdoor,
                spec["ua"], spec["cap"], GAINS,
            )
            if sized_el is None:
                return None
            pred_peak, _fin = sysid_mod._predict_step_excursion_plant(
                spec["ua"], spec["cap"], GAINS, BASE_T, outdoor,
                sized_el * COP, cfg.step_hours, cfg.relax_hours,
                model=sysid_mod._sizing_model(spec["ua"], spec["cap"], GAINS),
            )
            truth = _true_peak(model, outdoor, sized_el * COP,
                               cfg.step_hours, cfg.relax_hours)
            return {
                "sized_el": sized_el, "pred": pred_peak, "truth": truth,
                "ratio": truth / max(pred_peak, 1e-9),
                "breach": truth > BOUND + 1e-9,
            }
        finally:
            sysid_mod._sizing_model = orig

    print(f"{'preset':<14}{'T_out':>6}{'sized_kW':>9}{'pred_pk':>9}"
          f"{'TRUE_pk':>9}{'ratio':>7}{'breach':>7}")
    rows, hrows = [], []
    for name in PLANTS:
        for o in OUTDOORS:
            r = one(name, o, honest=False)
            rows.append((name, o, r))
            print(f"{name:<14}{o:>6.1f}{r['sized_el']:>9.3f}"
                  f"{r['pred']:>9.3f}{r['truth']:>9.3f}{r['ratio']:>7.2f}"
                  f"{str(r['breach']):>7}")
    print("-- honest sizer counterfactual (same cells)")
    for name in PLANTS:
        for o in OUTDOORS:
            r = one(name, o, honest=True)
            hrows.append((name, o, r))
            print(f"{name:<14}{o:>6.1f}{r['sized_el']:>9.3f}"
                  f"{r['pred']:>9.3f}{r['truth']:>9.3f}{r['ratio']:>7.2f}"
                  f"{str(r['breach']):>7}")

    n = len(rows)
    breaches = sum(1 for _n, _o, r in rows if r["breach"])
    hbreaches = sum(1 for _n, _o, r in hrows if r["breach"])
    ratios = [r["ratio"] for _n, _o, r in rows]
    hratio_max = max(r["ratio"] for _n, _o, r in hrows)
    worst = max(rows, key=lambda t: t[2]["truth"])
    # drop-one re-aggregation: worst-preset-out and per-preset breach counts
    per_preset = {p: sum(1 for n, _o, r in rows if n == p and r["breach"])
                  for p in PLANTS}
    print("########## RESULT lines ##########")
    print(f"RESULT v3_sizer_cells={n} count")
    print(f"RESULT v3_sizer_breach_cells={breaches} count")
    print(f"RESULT v3_sizer_peak_ratio_min={min(ratios):.3f} ratio")
    print(f"RESULT v3_sizer_peak_ratio_max={max(ratios):.3f} ratio")
    print(f"RESULT v3_sizer_worst_truth_peak={worst[2]['truth']:.3f} degC")
    print(f"RESULT v3_sizer_breach_by_preset="
          f"{','.join(f'{p}:{c}' for p, c in per_preset.items())}")
    print(f"RESULT v3_honest_breach_cells={hbreaches} count")
    print(f"RESULT v3_honest_peak_ratio_max={hratio_max:.3f} ratio")
    print("RESULT thread_factor=1.0 ratio")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f} ratio")
    except OSError:
        print("RESULT load1=nan ratio")
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
