"""D2 -- COP is not monotone in outdoor temperature once the Carnot flow
correction is on.

METRIC: for each flow temperature on a grid, the number of adjacent pairs on a
0.5 K outdoor-temperature sweep where `ThermalModel.compute_cop(T_out, flow)`
STRICTLY DECREASES as T_out increases, and the largest such decrease, in COP
units.  Physics: at a fixed flow temperature the lift T_flow - T_out shrinks as
T_out rises, so a heat pump's COP must be non-decreasing in T_out.  Any
strictly-decreasing pair is a violated physical bound.

COMMAND (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D2/cop_monotonicity.py

EXPECTED at baseline ae36eff: `violating_flow_temps=7_of_7`,
`violating_flow_temps_kelvin_band_-20_20=5_of_7`,
`worst_drop_kelvin_band_-20_20=0.02093` COP (tolerance 1e-4 -- pure arithmetic,
no solver, no BLAS, reproducible bit-for-bit), and the null arm
`violating_flow_temps_carnot_off=0_of_7`.

HEADER CORRECTION, round-3 orchestrator, 2026-09-11.  This block previously read
`violating_flow_temps=6 of 7` and `worst_drop_kelvin_band_-20_20=0.15959`, which
this script has never printed.  All three D2 panel verifiers re-ran it per this
header and each reported 7_of_7 and 0.02093; the orchestrator reproduced the same
two lines before editing.  The finding is unaffected -- only this expectation was
wrong, and a judge re-running blind against the old text would have recorded a
mismatch that does not exist.

PERTURBATION (direction stated): set `cop_flow_carnot = False` (the default,
and what `ThermalParameters.from_config` sets when no mixing valve throttles) ->
violations must fall to 0.  That arm is run here as `..._carnot_off` and is the
control: it isolates the Carnot block as the cause rather than the nameplate
curve.

BASELINE SHA: ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1
MACHINE: 8-core Apple M1, 8 GB, numpy 2.4.6 / scipy 1.17.1 on OpenBLAS
INSTRUMENTED SYMBOL: custom_components/heatpump_optimizer/thermal_model.py
    :ThermalModel.compute_cop  (and its inlined twin in
    :ThermalModel.simulate_trajectory_batch, checked here for parity)
"""
import d2lib  # noqa: F401  -- thread pin + sys.path, must be first
import numpy as np

from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
)

d2lib.repo_root_ok()

FLOWS = (36.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0)
OUT_FULL = np.arange(-20.0, 35.01, 0.5)
# The band a Nordic heating plan actually spends its year in.  Kept separate so
# the finding cannot be waved away as "only above 27 C".
OUT_BAND = np.arange(-20.0, 20.01, 0.5)


def model(carnot: bool) -> ThermalModel:
    p = ThermalParameters()
    p.cop_flow_carnot = carnot
    p.defrost_derate = None      # isolate: the derate has its own sweep
    return ThermalModel(p)


def sweep(m: ThermalModel, outs: np.ndarray) -> dict:
    rows = {}
    for flow in FLOWS:
        cops = np.array([m.compute_cop(float(o), flow_temp=flow) for o in outs])
        d = np.diff(cops)
        neg = d[d < -1e-12]
        rows[flow] = {
            "n_decreasing_pairs": int(neg.size),
            "worst_drop": float(-neg.min()) if neg.size else 0.0,
            "peak_at": float(outs[int(np.argmax(cops))]),
            "peak": float(cops.max()),
            "end": float(cops[-1]),
        }
    return rows


def main() -> int:
    on = sweep(model(True), OUT_FULL)
    on_band = sweep(model(True), OUT_BAND)
    off = sweep(model(False), OUT_FULL)

    viol = sum(1 for r in on.values() if r["n_decreasing_pairs"])
    viol_band = sum(1 for r in on_band.values() if r["n_decreasing_pairs"])
    viol_off = sum(1 for r in off.values() if r["n_decreasing_pairs"])

    d2lib.result("violating_flow_temps", f"{viol}_of_{len(FLOWS)}")
    d2lib.result("violating_flow_temps_carnot_off", f"{viol_off}_of_{len(FLOWS)}")
    d2lib.result("violating_flow_temps_kelvin_band_-20_20",
                 f"{viol_band}_of_{len(FLOWS)}")

    worst_band = max(r["worst_drop"] for r in on_band.values())
    d2lib.result("worst_drop_kelvin_band_-20_20", round(worst_band, 5), "COP")
    worst_full = max(r["worst_drop"] for r in on.values())
    d2lib.result("worst_drop_full_sweep", round(worst_full, 5), "COP")

    # Leave-one-out over the seven flow cells (COMMON.md item 6).
    per_cell = {f: on[f]["worst_drop"] for f in FLOWS}
    best = max(per_cell, key=per_cell.get)
    rest = [v for f, v in per_cell.items() if f != best]
    d2lib.result("loo_cells", len(FLOWS))
    d2lib.result("loo_range", round(max(per_cell.values()) - min(per_cell.values()), 5))
    d2lib.result("loo_worst_drop_without_best_cell", round(max(rest), 5), "COP")

    for flow in FLOWS:
        r = on[flow]
        rel = (r["peak"] - r["end"]) / r["peak"] if r["peak"] else 0.0
        d2lib.result(
            f"flow_{flow:g}",
            f"peak_at={r['peak_at']:g}C peak={r['peak']:.4f} "
            f"at_35C={r['end']:.4f} rel_loss={rel:.3f} "
            f"decreasing_pairs={r['n_decreasing_pairs']} "
            f"worst_step={r['worst_drop']:.5f}",
        )
    for flow in FLOWS:
        rb = on_band[flow]
        d2lib.result(
            f"band_flow_{flow:g}",
            f"peak_at={rb['peak_at']:g}C decreasing_pairs={rb['n_decreasing_pairs']} "
            f"worst_step={rb['worst_drop']:.5f} "
            f"loss_peak_to_20C={rb['peak'] - rb['end']:.5f}",
        )

    # The identity a fix must restore, stated so a verifier can key on it.
    d2lib.result(
        "identity",
        "for_all_flow>ref: d(compute_cop)/d(T_out) >= 0; violated above",
    )
    d2lib.env_footer()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
