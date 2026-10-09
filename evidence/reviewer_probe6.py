#!/usr/bin/env python3
"""Reviewer probe 6 (review-2066 round 3): follows_ask under noise, lag, outliers, partial following.

Synthetic only. Drives the production order per tick: draw_range.fold (#2065)
then _learn_measured_cop(draw) when it takes one. 6 kW nameplate, 1 kW floor,
outdoor 8 C. Asks: one level per hour (2 ticks at the 30-minute default)
from a seeded uniform 1.5-5.0 kW, 400 ticks (~8 days). Pumps:
  heat_led(t)  drawn = asked * scale / t (the harness's true-COP model; right scale t)
  selfset      drawn 2.2 kW +-3 % whatever is asked (right scale 1.0)
  partial(b)   drawn = 2.5 * (asked/2.5)**b, true COP = model (right scale 1.0)
Perturbations on heat_led(0.7): meter noise 20 %, a one-tick lag, 5 % outliers x3.
Prints folds, first fold tick, learned scale, follows_ask at the end.
"""
import sys, random
sys.path.insert(0, "tests")
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer import draw_range  # noqa: E402
FA = getattr(draw_range, "follows_ask", None)
CFG = {"tibber_token": "x", "weather_entity": "weather.home",
       "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
       "heat_pump_power_entity": "sensor.pump_power"}
STATES = {"sensor.indoor": FakeState("21.0", unit="°C"),
          "sensor.outdoor": FakeState("8.0", unit="°C"),
          "sensor.pump_power": FakeState("2200", unit="W")}
N = int(sys.argv[1]) if len(sys.argv) > 1 else 400
def asks(seed, lo=1.5, hi=5.0, block=2):
    r = random.Random(seed); out = []
    while len(out) < N:
        out += [r.uniform(lo, hi)] * block
    return out[:N]
def run(label, asked, drawn_fn, pmax=6.0, pmin=1.0):
    c = HeatPumpOptimizerCoordinator(FakeHass(dict(STATES)), FakeEntry(
        data=dict(CFG, heat_pump_max_power=pmax, heat_pump_min_power=pmin)))
    c._current_state.outdoor_temperature = 8.0
    learn = c._learn_measured_cop
    takes = learn.__code__.co_argcount > 1
    first = None; prev = None
    for t, a in enumerate(asked):
        c._current_action = {"power": a, "dhw_power": 0.0}
        d = drawn_fn(t, a, c._cop_scale, prev)
        prev = a
        c._measured_power = d
        draw = c._accuracy.draw
        draw_range.fold(draw, d, c._commanded_split(), c._thermal_params,
                        frozen=False, distorted=False, defrost=False)
        n0 = c._cop_samples
        learn(draw) if takes else learn()
        if c._cop_samples > n0 and first is None and abs(d / a - 1) > 0.15:
            first = t
    fa = FA(c._accuracy.draw) if FA else "n/a"
    print(f"RESULT {label}_folded={c._cop_samples}/{N} first_offask_fold={first} scale={c._cop_scale:.3f} follows_ask={fa}")
R = random.Random(99)
run("matched", asks(1), lambda t, a, s, p: a)
run("heat_led_0.7_noise5", asks(2), lambda t, a, s, p: a * s / 0.7 * R.uniform(0.95, 1.05))
run("heat_led_0.7_noise20", asks(3), lambda t, a, s, p: a * s / 0.7 * R.uniform(0.8, 1.2))
run("heat_led_0.7_lag1", asks(4), lambda t, a, s, p: (p if p is not None else a) * s / 0.7)
run("heat_led_0.7_outliers", asks(5), lambda t, a, s, p: a * s / 0.7 * (3.0 if R.random() < 0.05 else 1.0))
run("heat_led_1.3", asks(6), lambda t, a, s, p: a * s / 1.3 * R.uniform(0.95, 1.05))
run("selfset_hourly", asks(7), lambda t, a, s, p: 2.2 * R.uniform(0.97, 1.03))
run("selfset_flat", [1.5 * R.uniform(0.98, 1.02) for _ in range(N)], lambda t, a, s, p: 2.2 * R.uniform(0.97, 1.03))
for b in (0.3, 0.5, 0.6, 0.8):
    run(f"partial_b{b}", asks(10 + int(b * 10)), lambda t, a, s, p, b=b: 2.5 * (a / 2.5) ** b * R.uniform(0.97, 1.03))
# narrow-ask install (ask span under 1.15): a real 0.7 shift
run("heat_led_0.7_narrow_ask", asks(20, 2.8, 3.1), lambda t, a, s, p: a * s / 0.7 * R.uniform(0.98, 1.02))
