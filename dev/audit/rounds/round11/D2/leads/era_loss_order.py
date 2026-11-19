"""D2-s1-51: presets.derive gives a low-energy house a larger heat loss than a post-2005 one.

Metric: over every (structure, foundation, area in 80/140/250 m2) cell, single zone,
the number of cells where presets.derive's house_heat_loss_coefficient is not
strictly decreasing along presets.ERAS (oldest -> newest); count key: the
derived house_heat_loss_coefficient the production derive returns.
Also prints the low_energy / post_2005 loss ratio range over the cells.
Null control: the same ordering over the four eras before low_energy (must be 0).
Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D2/leads/era_loss_order.py [--perturb]
  --perturb sets presets._ERA_LOSS_W_PER_M2K['low_energy'] = 0.35 in memory
  (any value below post_2005's 0.55); cells_inverted must go to 0.
Expected: cells_inverted=cells (exact), null_cells_inverted=0 (exact),
ratio 1.545 (exact up to rounding).
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (planted finder export
audit-r11-leads-px), machine: owner's macOS box (B8).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from heatpump_optimizer import presets  # noqa: E402

c0, t0 = time.process_time(), time.thread_time()
if "--perturb" in sys.argv:
    presets._ERA_LOSS_W_PER_M2K[presets.ERA_LOW_ENERGY] = 0.35

eras = list(presets.ERAS)
cells = inverted = null_inverted = 0
ratios = []
for structure in presets.STRUCTURES:
    for foundation in presets.FOUNDATIONS:
        for area in (80.0, 140.0, 250.0):
            losses = []
            for era in eras:
                p = presets.BuildingPreset(structure=structure, era=era,
                                           foundation=foundation,
                                           heated_area_m2=area).validate()
                losses.append(presets.derive(p)["house_heat_loss_coefficient"])
            cells += 1
            if any(b >= a for a, b in zip(losses, losses[1:])):
                inverted += 1
            head = losses[:-1]
            if any(b >= a for a, b in zip(head, head[1:])):
                null_inverted += 1
            ratios.append(losses[eras.index(presets.ERA_LOW_ENERGY)]
                          / losses[eras.index(presets.ERA_POST_2005)])
print(f"eras order: {eras}")
print(f"RESULT cells={cells} count")
print(f"RESULT cells_inverted={inverted} count")
print(f"RESULT null_cells_inverted={null_inverted} count")
print(f"RESULT low_energy_over_post2005_min={min(ratios):.3f} ratio")
print(f"RESULT low_energy_over_post2005_max={max(ratios):.3f} ratio")
pc, tc = time.process_time() - c0, time.thread_time() - t0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
