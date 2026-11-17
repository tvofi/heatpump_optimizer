"""Reviewer's attack rows (builder: the fix reviewer, not the finder), run with the head's
dev/audit/harnesses/cop_duty_floor.py: a 2.2 kW self-setting pump under the harness's flat
1.5 kW asks (4 kW nameplate, open loop) whose draw swings on its own, whatever is asked.
amp=0 is the null control (the PR's own selfset_2.2_flat recipe through this generator)."""
import math, random, sys
sys.argv = sys.argv[:1]
sys.path.insert(0, "dev/audit/harnesses")
import cop_duty_floor as h
def sig(n, kw, parts, seed, phase=0.0):
    rng = random.Random(seed); out = []
    for t in range(n):
        ask = 1.5 * rng.uniform(0.98, 1.02)
        f = 1 + sum(a * math.sin(2 * math.pi * t / p + phase) for a, p in parts)
        out.append((ask, kw * f * rng.uniform(0.97, 1.03)))
    return out
h.flat_row("selfset_2.2_swing0_control_s1", sig(672, 2.2, [], 1))
h.flat_row("selfset_2.2_swing0.15_p64_s1", sig(672, 2.2, [(0.15, 64)], 1))
h.flat_row("selfset_2.2_swing0.15_p80_s1", sig(672, 2.2, [(0.15, 80)], 1))
h.flat_row("selfset_2.2_swing0.3_p96_s1", sig(672, 2.2, [(0.3, 96)], 1))
h.flat_row("selfset_2.2_swing0.15_p120_s1", sig(672, 2.2, [(0.15, 120)], 1))
h.flat_row("selfset_2.2_mix_daily0.1_5day0.2_phasepi_s1", sig(672, 2.2, [(0.1, 48), (0.2, 240)], 1, math.pi))
h.flat_row("selfset_2.2_mix_daily0.1_5day0.2_phase0_s1", sig(672, 2.2, [(0.1, 48), (0.2, 240)], 1, 0.0))
