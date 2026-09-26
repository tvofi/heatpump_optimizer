"""V3 independent check for D2-s2-81: verify the 0.5x divisor on the L1 floor term directly on
_comfort_terms, with synthetic inputs, independent of running a full optimize() solve.

Method: build a HeatPumpOptimizer via golden.make, then call _comfort_terms twice on synthetic
one-step trajectories that undershoot temp_min_bounds by a known amount X, once with
two_zone_enabled True and once False (same undershoot X in both), and check whether the L1
component of the returned penalty is exactly half in the two-zone case.

Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/verify-v3-leads/v3_comfort_floor_unit.py
"""
import os, sys
sys.path[:0] = ["tests", "custom_components"]
import numpy as np  # noqa: E402
import golden  # noqa: E402
from heatpump_optimizer import optimizer as optmod  # noqa: E402

b = golden.make(two_zone=True, dhw=False, price_profile="flat", weather_profile="winter_cold")
opt = b["optimizer"]

n = 4
X = 1.0  # undershoot, degC
comfort_targets = np.full(n, 20.0)
temp_min_bounds = np.full(n, 20.0)
temp_max_bounds = np.full(n, 26.0)
comfort_band = np.full(n, 2.0)

# two-zone: both zones undershoot by X
two_zone_temps = np.full(n + 1, 20.0 - X)
opt.model.params.two_zone_enabled = True
penalty_2z, _ = opt._comfort_terms(
    two_zone_temps, two_zone_temps, two_zone_temps,
    comfort_targets, temp_min_bounds, temp_max_bounds, comfort_band,
)

# single-zone: room undershoots by X
opt.model.params.two_zone_enabled = False
penalty_1z, _ = opt._comfort_terms(
    two_zone_temps, two_zone_temps, two_zone_temps,
    comfort_targets, temp_min_bounds, temp_max_bounds, comfort_band,
)

weight = opt.config.comfort_weight
L1 = optmod._COMFORT_FLOOR_L1
# Isolate the L1 term analytically: penalty = weight_scale * (quad_terms*coeffs + L1_term*L1)
# Two-zone: 0.5*weight*(sum(X^2)*10*2 + sum(X)*L1*2); single: weight*(sum(X^2)*10 + sum(X)*L1)
expected_2z_L1_coeff = 0.5 * weight * (n + n) * L1  # undershoot_u + undershoot_l, each n steps, each X
expected_1z_L1_coeff = weight * n * L1

print(f"RESULT penalty_two_zone={penalty_2z:.6f} penalty_single_zone={penalty_1z:.6f}")
print(f"RESULT comfort_weight={weight} L1_const={L1}")
# Per-degree-of-undershoot L1 price, isolated by re-running at X and 2X and differencing the
# linear component is messy with the quadratic mixed in; instead directly assert the coefficient
# the two branches use in source is 0.5x weight vs weight (read from the executed function object,
# not from a second grep) by perturbing only the linear order: use X small enough quadratic is
# negligible relative to scale, then compare ratio of *marginal* penalties.
X2 = 1e-4
two_zone_temps2 = np.full(n + 1, 20.0 - X2)
opt.model.params.two_zone_enabled = True
penalty_2z_small, _ = opt._comfort_terms(
    two_zone_temps2, two_zone_temps2, two_zone_temps2,
    comfort_targets, temp_min_bounds, temp_max_bounds, comfort_band,
)
opt.model.params.two_zone_enabled = False
penalty_1z_small, _ = opt._comfort_terms(
    two_zone_temps2, two_zone_temps2, two_zone_temps2,
    comfort_targets, temp_min_bounds, temp_max_bounds, comfort_band,
)
# At X2 tiny, quadratic term (~X2^2) is negligible next to the linear term (~X2): penalty/X2 ~ L1 price/step
per_step_price_2z = penalty_2z_small / X2 / (2 * n)  # two zones, n steps each
per_step_price_1z = penalty_1z_small / X2 / n
print(f"RESULT per_zone_per_step_L1_price two_zone={per_step_price_2z:.4f} single_zone={per_step_price_1z:.4f} "
      f"ratio={per_step_price_2z / per_step_price_1z:.4f}")
print("RESULT expected_ratio=0.5000 (each two-zone zone should price undershoot the same as single-zone)")
