"""P3 probe: pump_arbiter._full_draw_c keys its headroom on the rated lift
(thermal_model.FLOW_MIN_LIFT_K, 5 K) while the floor write keys on the
configured one (start_flow_min_lift_k). On a return target, a set-point the
arbiter writes for the plan's FLOOR level is then the one FlowCommand.ceiling_c
tells draw_range commands the pump's MAXIMUM draw.

Grid: configured lift 0.5-15 K (the options range), ceiling 45 C, gate 20 C,
inlet 25-44 C; planned level = p_min of a 1.0-4.0 kW band. A cell contradicts
when the floor set-point sits above the ceiling (so the floor-level write is
the ceiling) and _full_draw_c(ceiling) still calls that ceiling the full draw.
Exit 1 when any cell off the default lift contradicts.
  --null     configured lift fixed at the rated 5 K (expected 0)
  --fixed    counterfactual: _full_draw_c keyed on start_flow_min_lift_k (expected 0)
"""
from __future__ import annotations

import sys
from types import SimpleNamespace

from custom_components.heatpump_optimizer import pump_arbiter as pa
from custom_components.heatpump_optimizer import thermal_model as tm

CEIL, GATE, PMIN, PMAX = 45.0, 20.0, 1.0, 4.0
FIXED = False


def contradicts(lift: float, inlet: float) -> bool:
    cfg = {"flow_min_lift_k": lift}
    floor_c = tm.modulation_floor_flow_c(inlet, GATE, tm.start_flow_min_lift_k(cfg))
    write = tm.flow_setpoint_for_level(PMIN + 1e-9, PMIN, PMAX, CEIL, floor_c)
    pa._return_unit = lambda _c: True
    pa._flow_inlet_c = lambda _i: inlet
    if FIXED:
        pa.FLOW_MIN_LIFT_K = tm.start_flow_min_lift_k(cfg)
    full = pa._full_draw_c(SimpleNamespace(config=cfg), CEIL)
    return write >= full - 1e-9 and floor_c > CEIL + 1e-9


def main(argv: list[str]) -> int:
    global FIXED
    FIXED = "--fixed" in argv
    lifts = [5.0] if "--null" in argv else [x / 2 for x in range(1, 31)]
    inlets = [25.0 + x / 2 for x in range(0, 39)]
    hits = [(l, i) for l in lifts for i in inlets if contradicts(l, i)]
    off_default = [(l, i) for l, i in hits if l != tm.FLOW_MIN_LIFT_K]
    print(f"cells={len(lifts) * len(inlets)} contradictions={len(hits)} off_default_lift={len(off_default)}")
    if hits:
        print("lifts_contradicting=" + ",".join(f"{l:g}" for l in sorted({l for l, _ in hits})))
        l, i = max(hits)
        print(f"example lift={l:g} K inlet={i:g} C: floor-level write {CEIL:g} C is read as the full-draw set-point")
    return 1 if off_default else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
