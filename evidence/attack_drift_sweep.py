"""Reviewer's sweep (builder: the fix reviewer): diurnal draw swing on a self-setting pump, seeds 1-5."""
import math, random, sys
sys.argv = sys.argv[:1]
sys.path.insert(0, "dev/audit/harnesses")
import cop_duty_floor as h
def drift(n, kw, amp, period, seed):
    rng = random.Random(seed); out = []
    for t in range(n):
        ask = 1.5 * rng.uniform(0.98, 1.02)
        out.append((ask, kw * (1 + amp * math.sin(2 * math.pi * t / period)) * rng.uniform(0.97, 1.03)))
    return out
for period in (48, 96, 192):
    for amp in (0.2, 0.25, 0.3, 0.4):
        for seed in (1, 2, 3, 4, 5):
            h.flat_row(f"selfset_2.2_drift{amp:g}_p{period}_s{seed}", drift(672, 2.2, amp, period, seed))
