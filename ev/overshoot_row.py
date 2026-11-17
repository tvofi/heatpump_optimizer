"""Reviewer's row for the void rule's direction (#3662): a heat-led pump of true
scale 0.8 under a plan whose ask over-reacts to the scale (asked = H / scale**2,
so the heat ask moves AGAINST the dither's coin by a full step). Uses the head
harness's run() with a per-tick ask computed from the live scale via `true`
wrapper: we drive pairs ourselves. argv: none."""
import sys, random
sys.path.insert(0, "dev/audit/harnesses")
import cop_duty_floor as h
from custom_components.heatpump_optimizer import draw_range

def go(n=672, true=0.8, H=1.5):
    c = h.coord(4.0, 1.0)
    rnd = random.Random(1)
    for tick in range(n):
        asked = H / c._cop_scale ** 2 * rnd.uniform(0.99, 1.01)
        drawn = asked * c._cop_scale / true
        c._current_action = {"power": asked, "dhw_power": 0.0}
        c._measured_power = drawn
        d = c._accuracy.draw
        draw_range.fold(d, drawn, c._commanded_split(), c._thermal_params, frozen=False, distorted=False, defrost=False)
        c._learn_measured_cop(d)
    return f"OVERSHOOT folded={c._cop_samples}/{n} scale={c._cop_scale:.3f} verdict={c._measured_cop.scale_response} evidence={draw_range.ask_evidence(d)}"

print(go())
