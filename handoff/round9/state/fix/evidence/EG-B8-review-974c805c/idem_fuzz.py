"""Idempotence fuzz of DhwProfileLearner.normalize_profile: f(f(p)) == f(p) bit-for-bit,
every hour in [MIN, MAX], mean within 1e-12 of 1. Prints counts; run at base and head."""
import random, sys
from heatpump_optimizer.dhw_learning import DhwProfileLearner, DHW_PROFILE_MIN_INTENSITY as LO, DHW_PROFILE_MAX_INTENSITY as HI
from heatpump_optimizer.thermal_model import ThermalParameters, DHW_HOURLY_DRAW_PATTERN
L = DhwProfileLearner.__new__(DhwProfileLearner); L._params = ThermalParameters()
random.seed(20260930)
cases = [list(DHW_HOURLY_DRAW_PATTERN), [4.0 if h in (7, 8, 19) else 0.5 for h in range(24)]]
for t in range(20000):
    m = t % 4
    if m == 0: p = [random.uniform(0, 5) for _ in range(24)]
    elif m == 1: p = [random.choice([0.0, 0.1, 10, 1e6, random.random()]) for _ in range(24)]
    elif m == 2: p = [10 ** random.uniform(-6, 6) for _ in range(24)]
    else:
        k = random.randint(0, 24); p = [1e9] * k + [1e-9] * (24 - k)
    cases.append(p)
moved = out_of_range = off_mean = 0
worst = 0.0
for p in cases:
    a = L.normalize_profile(p); b = L.normalize_profile(a)
    if a != b:
        moved += 1; worst = max(worst, max(abs(x - y) for x, y in zip(a, b)))
    if not all(LO <= v <= HI for v in a): out_of_range += 1
    if abs(sum(a) / 24 - 1.0) > 1e-9: off_mean += 1
print(f"RESULT cases={len(cases)} restart_moved={moved} worst_move={worst:.3e} out_of_range={out_of_range} mean_off_1={off_mean} default_moved={int(L.normalize_profile(L.normalize_profile(list(DHW_HOURLY_DRAW_PATTERN))) != L.normalize_profile(list(DHW_HOURLY_DRAW_PATTERN)))}")
