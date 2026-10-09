#!/usr/bin/env python3
"""Reviewer probe 4 (review-2066 round 2): over-refusal of the off-ask gate on correct pumps.

Synthetic only. 6 kW nameplate, 1.5 kW floor (a correctly configured
modulating pump), outdoor 8 C. Seeded RNG. Each case prints folds out of N,
the first tick that folded, and the learned cop_scale. True cop_scale is 1.0
unless the case states an efficiency shift, where the ratio meter/ask is
1/eff and the right scale is eff.
"""
import sys, random
sys.path.insert(0, "tests")
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
CFG = {"tibber_token": "x", "weather_entity": "weather.home",
       "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
       "heat_pump_power_entity": "sensor.pump_power"}
STATES = {"sensor.indoor": FakeState("21.0", unit="°C"),
          "sensor.outdoor": FakeState("8.0", unit="°C"),
          "sensor.pump_power": FakeState("2200", unit="W")}
def go(pairs, pmax=6.0, pmin=1.5):
    c = HeatPumpOptimizerCoordinator(FakeHass(dict(STATES)), FakeEntry(
        data=dict(CFG, heat_pump_max_power=pmax, heat_pump_min_power=pmin)))
    c._current_state.outdoor_temperature = 8.0
    first = None; refs = {}
    for i, (cmd, meas) in enumerate(pairs):
        c._current_action = {"power": cmd, "dhw_power": 0.0}
        c._measured_power = meas
        before = c._cop_samples
        c._learn_measured_cop()
        if c._cop_samples > before and first is None: first = i
        r = getattr(getattr(c, "_measured_cop", None), "refusal", None)
        refs[r] = refs.get(r, 0) + 1
    return c._cop_samples, first, c._cop_scale, refs
N = 96
def asks(rng): return [rng.uniform(2.0, 5.0) for _ in range(N)]
cases = {}
rng = random.Random(1); a = asks(rng); cases["follow_noise10"] = [(x, x * rng.uniform(0.9, 1.1)) for x in a]
rng = random.Random(2); a = asks(rng); cases["follow_noise20"] = [(x, x * rng.uniform(0.8, 1.2)) for x in a]
rng = random.Random(3); a = asks(rng); cases["eff0.8_noise5"] = [(x, x * 1.25 * rng.uniform(0.95, 1.05)) for x in a]
rng = random.Random(4); a = asks(rng); cases["eff0.8_noise10"] = [(x, x * 1.25 * rng.uniform(0.9, 1.1)) for x in a]
rng = random.Random(5); a = asks(rng); lag = [a[0]] + a[:-1]; cases["follow_lag1tick"] = list(zip(a, lag))
rng = random.Random(6); cases["selfmod_steady"] = [(1.5 * rng.uniform(0.98, 1.02), 2.2 * rng.uniform(0.98, 1.02)) for _ in range(N)]
for k, pairs in cases.items():
    n, first, s, refs = go(pairs)
    top = ",".join(f"{r}:{v}" for r, v in sorted(refs.items(), key=lambda t: -t[1]) if r)
    print(f"RESULT {k}_folded={n}/{N} first_fold_tick={first} cop_scale={s:.3f} refusals[{top}]")
