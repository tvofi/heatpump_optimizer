#!/usr/bin/env python3
"""R10-HOUSE-GRADE (#2816): the house grade against the configured type and era.

WHY IT EXISTS. The owner's house (about 100 years old, new windows and added
insulation) graded near 0: ``envelope_score`` placed the time constant on one
band spanning every shipped preset, so any pre-1960 house sat at its bottom
whatever its envelope did against houses of its own era. The owner's spec
(2026-10-25): envelope loss in W/K, thermal-mass corrected, against typical
for the configured type and era; typical is mid-scale; the owner's case, at
about 1.5x typical pre-1960 loss, lands low but clearly nonzero (30-40).
This harness drives the tree's own ``envelope_score`` on preset houses, so a
later seat can re-take it at its own base.

Arms (each prints RESULT lines):

  eras    Every structure x era preset house, single-zone, configured with
          its own answers, at learned scale 1.0 (loss ratio 1.0). Per cell
          the published grade; ``era_spread`` is max - min over the grid.
          Null control: at ratio 1.0 every era is typical for itself, so the
          spread is 0 and every cell grades 50.
  owner   The pre-1960 houses of every structure at learned scale 1.5 (the
          owner's measured ~1.5x typical). ``owner_min``/``owner_max``.
  curve   One pre-1960 house over scales 0.25-8: ``monotone`` (strictly
          decreasing), ``curve_min`` (> 0: 0 is no data).
  drivers Over the eras and owner cells: ``drivers_max_gap``, the largest
          |sum(points) - (grade - 50)| -- the drivers account for the grade.

Metric (one line): era_spread at ratio 1.0, and owner_min/owner_max.
Command (repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_house_grade.py
Expected at the head:
    EXPECTED RESULT era_spread=0.0
    EXPECTED RESULT owner_min=35.2
    EXPECTED RESULT monotone=True
At the merge base (3b4180dcc): era_spread=100.0, owner grades 0.0 for every
    structure, no drivers.
Baseline SHA: 3b4180dcc. Machine: Darwin arm64, CI venv; float arithmetic on
    fixed inputs, not a solve.
Perturbation: --era-blind -- each house is configured without its era, so it
    is graded against the default era: era_spread rises above 0 at the head.
Null control: ratio 1.0 itself (the eras arm), where a correct normalization
    gives 50 for every era and a band-based grade does not.
Instrumented symbols: coordinator:envelope_score, presets:house_grade,
    presets:derive.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import inspect  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from heatpump_optimizer import presets  # noqa: E402
from heatpump_optimizer.coordinator import envelope_score  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

CONVERGED_SAMPLES = 10**6
SCALES = (0.25, 0.5, 0.8, 1.0, 1.25, 1.5, 2.0, 4.0, 8.0)


def grade(structure, era, scale, era_blind):
    config = {"building_structure": structure, "heated_area_m2": 140.0}
    if not era_blind:
        config["building_era"] = era
    derived = presets.derive(presets.BuildingPreset(structure=structure, era=era))
    params = ThermalParameters.from_config(derived)
    params.house_heat_loss_scale = scale
    args = [params, CONVERGED_SAMPLES, {}]
    if "config" in inspect.signature(envelope_score).parameters:
        args.append(config)
    out = envelope_score(*args)
    drivers = out[2] if len(out) > 2 else []
    return out[0], drivers


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--era-blind", action="store_true")
    a = ap.parse_args()
    gaps = []
    eras = []
    for structure in presets.STRUCTURES:
        for era in presets.ERAS:
            g, drivers = grade(structure, era, 1.0, a.era_blind)
            print(f"eras {structure} {era}: grade={round(g, 1)}")
            eras.append(g)
            if drivers:
                gaps.append(abs(sum(d["points"] for d in drivers) - (g - 50.0)))
    print(f"RESULT era_spread={round(max(eras) - min(eras), 1)}")
    owner = []
    for structure in presets.STRUCTURES:
        g, drivers = grade(structure, presets.ERA_PRE_1960, 1.5, a.era_blind)
        print(f"owner {structure}: grade={round(g, 1)} drivers={drivers}")
        owner.append(g)
        if drivers:
            gaps.append(abs(sum(d["points"] for d in drivers) - (g - 50.0)))
    print(f"RESULT owner_min={round(min(owner), 1)}")
    print(f"RESULT owner_max={round(max(owner), 1)}")
    curve = [grade(presets.STRUCTURE_TIMBER_CRAWLSPACE, presets.ERA_PRE_1960, s,
                   a.era_blind)[0] for s in SCALES]
    print(f"curve {list(zip(SCALES, [round(c, 2) for c in curve]))}")
    print(f"RESULT monotone={all(x > y for x, y in zip(curve, curve[1:]))}")
    print(f"RESULT curve_min={round(min(curve), 2)}")
    print(f"RESULT drivers_max_gap={round(max(gaps), 9) if gaps else None}")


if __name__ == "__main__":
    main()
