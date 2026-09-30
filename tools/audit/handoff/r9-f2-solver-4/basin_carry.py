"""R9-F2.4 companion: the P4 basin carry, re-measured at this PR's merge base.

F2.1 (#1694) disclosed a P4 basin effect in the golden scenario
``everything_on``: summed degree-steps below ``config.min_temp`` over both zone
trajectories moved 0.276 -> 0.896, and its body ruled it not a regression (the
sub-17.0 steps all fall in the night-setback window, where the solver's own
floor is min_temp - 0.5, and against that floor the priced breach fell
0.00194 -> 0). This PR's brief carries the instruction to re-measure that
number at its own merge base, because the on/off threshold fix here could in
principle move the basin.

It cannot, and this is the measurement that says so rather than the argument:
the fix touches only what happens AFTER the solve (_power_to_heat_pump_schedule,
get_current_action, the arbiter's duty split, the published power), so the
objective, the plan and the trajectories must be byte-identical. Reported per
scenario:

  cost       the capture's own predicted_cost, and its compressor_starts
  deg_steps  sum over the zone trajectories of max(0, min_temp - T), #1694's
             rule, which counts config.min_temp at every step including the
             night-setback window (its caveat, restated here, not re-derived)
  on_true    steps whose on schedule is True -- the field this PR does move
  plan_sha1  sha1 of the plan's power and DHW schedules, so "byte-identical"
             is a comparison and not an adjective

Run from the repository root of the tree under measurement:

  PYTHONPATH=tests/hastub python3 \
      tools/audit/handoff/r9-f2-solver-4/basin_carry.py [--scenarios a,b]
"""
from __future__ import annotations

import argparse
import hashlib
import sys

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402

import golden  # noqa: E402

DEFAULT = ("everything_on", "winter_two_zone_no_dhw", "shoulder")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", default=",".join(DEFAULT))
    a = ap.parse_args()
    for name in a.scenarios.split(","):
        spec = dict(golden.SCENARIOS[name])
        cap = golden.capture(name, spec)
        probe = dict(spec)
        probe.pop("param_overrides", None)
        min_temp = float(golden.make(**spec)["optimizer"].config.min_temp)
        zones = {
            k: cap[k]
            for k in ("room_temp_trajectory", "upper_temp_trajectory",
                      "lower_temp_trajectory")
            if cap.get(k)
        }
        deg = {
            k: float(np.clip(min_temp - np.asarray(v, dtype=float), 0, None).sum())
            for k, v in zones.items()
        }
        space = np.asarray(cap["power_schedule"], dtype=float)
        dhw = np.asarray(cap.get("dhw_power_schedule") or np.zeros_like(space),
                         dtype=float)
        blob = space.tobytes() + dhw.tobytes()
        on = cap.get("heat_pump_on_schedule") or []
        print(f"{name:26s} cost={cap.get('predicted_cost')!r} "
              f"starts={cap.get('compressor_starts')!r} "
              f"min_temp={min_temp} deg_steps={sum(deg.values()):.6f} "
              f"{ {k: round(v, 6) for k, v in deg.items()} } "
              f"on_true={sum(1 for x in on if x)}/{len(on)} "
              f"plan_sha1={hashlib.sha1(blob).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
