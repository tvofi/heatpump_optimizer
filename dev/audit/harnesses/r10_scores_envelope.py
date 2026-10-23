#!/usr/bin/env python3
"""R10-SCORES (#2258): the house grade against the Health tab's own heat loss.

WHY IT EXISTS. The owner's plan scores (2026-10-14) read the house at 0 on an
averagely insulated house with new windows. The grade is the time constant
``room_thermal_mass / loss`` mapped from 20-100 h to 0-100; R10-RATIO-SITES
measured that its ``loss`` read the configured zone total times the learned
scale, while the model -- and the Health tab, ``ModelStatusSensor``'s
``heat_loss_w_per_k`` -- uses ``_effective_house_heat_loss``, which carries
the learned lower-floor split. This harness drives the tree's own
``_scores_view`` and compares the grade it publishes with the grade the
Health tab's figure implies, so a later seat can re-take it at its own base.

Arms (each prints RESULT lines):

  split  A two-zone preset house (``presets.derive``) on a coordinator with a
         converged heat-loss learner and no drift alarm, at every split in
         ``RATIOS`` and every scale in ``SCALES`` (2.6 is the RESEED drift
         lead). Per cell: the envelope ``_scores_view`` publishes, and the
         grade of ``room_thermal_mass / house_heat_loss_effective`` read off
         the learning view the Health tab publishes. ``max_abs_gap`` is the
         largest gap over the grid with the split left of 1.
         Null control (``--ratio-override 1.0``): every split is 1.0, where
         the two loss bases are one number, so the gap is 0 at either end --
         which is also what separates this from a scale-only drift.
  ends   The learner at both ends of its input range: zero evidence and
         converged, at the scale clamp's floor and ceiling
         (``HOUSE_HEAT_LOSS_SCALE_MIN``/``_MAX``). Prints the envelope and,
         where the head publishes one, its reason.
  band   The tree's own presets, single-zone and two-zone, each era and
         structure at 140 m2: the time constant and the grade the 20-100 h
         band gives. Reported, not acted on: a band change is a behaviour no
         finding names yet (the design note's rule).
  bundle (optional, ``--bundle PATH``) The owner's diagnostics bundle: the
         stored scale, split and sample count, and the grade on both bases.
         Never commit a bundle: it is a user's private data.

Metric (one line): |envelope - grade(Health's heat loss)| over the split grid.
Command (repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_scores_envelope.py
Expected: at the merge base the gap is non-zero wherever the split left 1
    (86425b9ad: split_max_abs_gap=10.5, at split 0.5 and scale 1.0); at the
    head it is 0 everywhere; under --ratio-override 1.0, 0 at both:
    EXPECTED RESULT split_cells=10
    EXPECTED RESULT split_max_abs_gap=0.0
Baseline SHA: 86425b9ad. Machine: Linux x86_64, CI venv 3.14; the grid is
    float arithmetic on fixed inputs, not a solve.
Perturbation: --ratio-override 1.0 -- the split arm's gap falls to 0.
Null control: the same flag at the merge base -- 0 there too, so the base's
    gap is the split's and not a scale-only drift.
Instrumented symbols: coordinator:HeatPumpOptimizerCoordinator._scores_view,
    coordinator:HeatPumpOptimizerCoordinator._learning_view (via
    house_heat_loss_effective), presets:derive.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import inspect  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass  # noqa: E402

from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer import presets  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

RATIOS = (0.5, 0.8, 1.0, 1.25, 2.0)
SCALES = (1.0, 2.6)
#: A learner well past any convergence threshold the tree may set.
CONVERGED_SAMPLES = 2000


def grade(tau_h):
    """The 20-100 h band, as the score states it (reported beside the tree's)."""
    return round(max(0.0, min(1.0, (tau_h - 20.0) / 80.0)) * 100.0, 1)


def params_from(derived, two_zone):
    p = ThermalParameters()
    p.room_thermal_mass = derived["house_thermal_mass"]
    p.heat_loss_coefficient = derived["house_heat_loss_coefficient"]
    p.slab_thermal_mass = derived["slab_thermal_mass"]
    p.slab_heat_transfer = derived["slab_heat_transfer"]
    p.two_zone_enabled = two_zone
    if two_zone:
        p.upper_floor_thermal_mass = derived["upper_floor_thermal_mass"]
        p.lower_floor_thermal_mass = derived["lower_floor_thermal_mass"]
        p.upper_floor_heat_loss = derived["upper_floor_heat_loss"]
        p.lower_floor_heat_loss = derived["lower_floor_heat_loss"]
    return p


def publish(coord, params, scale, ratio, samples):
    """The envelope the tree publishes and the Health tab's heat loss, kW/K."""
    coord._thermal_params = params
    coord._apply_house_heat_loss_scale(scale)
    coord._lower_floor_loss_ratio = ratio
    params.lower_floor_loss_ratio = ratio
    coord._house_heat_loss_samples = samples
    view = coord._scores_view
    if "advice" in inspect.signature(view).parameters:
        scores = view(coord_mod.model_restart_advice(coord))
    else:
        scores = view()
    learning = coord._learning_view()
    return scores, float(learning["house_heat_loss_effective"])


def arm_split(ratio_override):
    coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data={}))
    derived = presets.derive(presets.BuildingPreset(two_zone=True))
    gaps = []
    for scale in SCALES:
        for ratio in RATIOS:
            r = ratio if ratio_override is None else ratio_override
            params = params_from(derived, True)
            scores, eff = publish(coord, params, scale, r, CONVERGED_SAMPLES)
            want = grade(params.room_thermal_mass / eff)
            got = scores["envelope"]
            gap = None if got is None else round(abs(got - want), 1)
            print(f"split scale={scale} ratio={r}: envelope={got} health_grade={want} "
                  f"health_w_per_k={eff * 1000:.1f} gap={gap}")
            gaps.append(float("inf") if gap is None else gap)
    print(f"RESULT split_cells={len(gaps)}")
    print(f"RESULT split_max_abs_gap={max(gaps)}")


def arm_ends():
    from heatpump_optimizer.const import HOUSE_HEAT_LOSS_SCALE_MAX, HOUSE_HEAT_LOSS_SCALE_MIN
    coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data={}))
    derived = presets.derive(presets.BuildingPreset(two_zone=True))
    for samples in (0, CONVERGED_SAMPLES):
        for scale in (HOUSE_HEAT_LOSS_SCALE_MIN, HOUSE_HEAT_LOSS_SCALE_MAX):
            scores, eff = publish(coord, params_from(derived, True), scale, 1.0, samples)
            print(f"RESULT ends samples={samples} scale={scale}: envelope={scores['envelope']} "
                  f"reason={(scores.get('reasons') or {}).get('envelope')}")


def arm_band():
    for two_zone in (False, True):
        for structure in sorted(presets.STRUCTURES):
            for era in ("pre_1960", "1960_1980", "1980_2005", "post_2005", "low_energy"):
                d = presets.derive(presets.BuildingPreset(
                    structure=structure, era=era, two_zone=two_zone))
                tau = d["house_thermal_mass"] / d["house_heat_loss_coefficient"]
                print(f"RESULT band two_zone={int(two_zone)} {structure} {era}: "
                      f"tau_h={tau:.1f} grade={grade(tau)}")


def arm_bundle(path):
    with open(path) as fh:
        data = json.load(fh)["data"]
    stores = data["debug"]["stores"]
    th = next(v for k, v in stores.items() if k.endswith("_thermal_learning"))
    params = ThermalParameters.from_config(dict(data["config"]))
    s, r = float(th["house_heat_loss_scale"]), float(th["lower_floor_loss_ratio"])
    n = int(th["house_heat_loss_samples"])
    configured = params.heat_loss_coefficient * s
    params.lower_floor_loss_ratio = r
    effective = coord_mod._effective_house_heat_loss(params, s)
    print(f"RESULT bundle scale={s} ratio={r} samples={n} two_zone={params.two_zone_enabled}")
    print(f"RESULT bundle tau_configured_h={params.room_thermal_mass / configured:.1f} "
          f"grade={grade(params.room_thermal_mass / configured)}")
    print(f"RESULT bundle tau_effective_h={params.room_thermal_mass / effective:.1f} "
          f"grade={grade(params.room_thermal_mass / effective)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ratio-override", type=float, default=None)
    ap.add_argument("--bundle", default=None)
    a = ap.parse_args()
    arm_split(a.ratio_override)
    arm_ends()
    arm_band()
    if a.bundle:
        arm_bundle(a.bundle)


if __name__ == "__main__":
    main()
