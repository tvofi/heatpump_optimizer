"""R10-PUMP-MODEL, D2-s2-01: how many ways one hot-water tank is priced.

`ThermalModel.compute_cop_dhw` prices one kWh into the DHW tank. Until this
finding it chose between two laws on `cop_flow_carnot`, a SPACE-circuit flag:
behind a valve, `_cop_law` at the tank's own water temperature (the buffer's
Carnot lift); without one, the plain curve times a linear 0.008/K penalty from
35 C, floored at 0.5. The ruling on #201 (comment 6240984157) accepted one law
on every plant; this census is the judge's two grids from that ruling, landed
so a later seat can re-run them.

Metrics, over a 41-outdoor (-25..15 C) x 51-tank (20..70 C) grid, 1 K steps:
  `dev_cells`    -- cells where the valve and the direct plant price the tank
                    differently (ratio above 1 + 1e-12). 0 when one law prices
                    both plants.
  `worst_ratio`  -- the largest valve/direct ratio on the grid, and its cell.
  `within_ratio` -- ONE direct install (no valve, flow-curve COP on): the
                    tank's price against the space curve's own lift at the same
                    water temperature, at 7 C outdoor / 55 C water. 1.0000 when
                    the tank and the space side pay one lift.
  `below_ref_boost` -- the largest direct-plant tank price over the plain
                    curve's, for a tank below the reference flow. 1.0000 when
                    a cold tank earns no boost.

Null control: `null_max_diff` -- the two plants at a 35 C tank (the reference
flow, where both laws must agree at every outdoor), must be 0.
Perturbation: `--perturb` reinstates the retired linear law on the direct
plant in this process (the old `compute_cop_dhw` body), which must move
`dev_cells` off 0 at a head that has one law.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_dhw_lift_law_grid.py \
        [--root DIR] [--perturb]

Counts and ratios only, deterministic; writes nothing.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--perturb", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    sys.path[:0] = [str(root / "tests" / "hastub"), str(root)]
    import numpy as np
    from custom_components.heatpump_optimizer.thermal_model import (
        ThermalModel,
        ThermalParameters,
    )

    def model(flag: bool, **kw) -> ThermalModel:
        return ThermalModel(ThermalParameters(cop_flow_carnot=flag, **kw))

    valve, direct = model(True), model(False)
    within = model(False, flow_curve_cop=True)
    if args.perturb:
        def linear_law(self, outdoor_temp, dhw_temp, humidity=None):
            base = self._cop_law(outdoor_temp, humidity, None)
            return max(base * max(0.5, 1.0 - 0.008 * (dhw_temp - 35.0)), 1.0)
        for m in (direct, within):
            m.compute_cop_dhw = linear_law.__get__(m)

    outs = np.arange(-25, 16, 1.0)
    tanks = np.arange(20, 71, 1.0)
    dev, worst, boost = 0, (1.0, None), 1.0
    for o in outs:
        for t in tanks:
            a, b = valve.compute_cop_dhw(o, t), direct.compute_cop_dhw(o, t)
            r = max(a, b) / min(a, b)
            if r > 1.0 + 1e-12:
                dev += 1
            if r > worst[0]:
                worst = (r, (float(o), float(t)))
            if t < direct.params.cop_flow_reference_temp:
                boost = max(boost, b / direct._cop_law(o, None, None))
    null = max(abs(valve.compute_cop_dhw(o, 35.0) - direct.compute_cop_dhw(o, 35.0))
               for o in outs)
    space = within._cop_law(7.0, None, None) * within.flow_lift_factor(7.0, 55.0)
    within_ratio = within.compute_cop_dhw(7.0, 55.0) / max(space, 1.0)

    print(f"RESULT cells={len(outs) * len(tanks)} count")
    print(f"RESULT dev_cells={dev} count")
    print(f"RESULT worst_ratio={worst[0]:.4f} at={worst[1]}")
    print(f"RESULT within_ratio={max(within_ratio, 1 / within_ratio):.4f} "
          f"(tank {within.compute_cop_dhw(7.0, 55.0):.4f} vs space lift {space:.4f})")
    print(f"RESULT below_ref_boost={boost:.4f}")
    print(f"RESULT null_max_diff={null:.3e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
