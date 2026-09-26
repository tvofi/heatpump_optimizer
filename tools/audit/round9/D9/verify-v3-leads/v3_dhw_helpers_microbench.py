"""V3 independent check for D9-s1-71: direct per-call cost of the three ThermalParameters
DHW helpers, isolated from full-solve fan-out noise.

Metric (independent of the finder's): wall time of N direct calls to each of
dhw_tank_heat_loss_coefficient, dhw_inlet_reference, effective_dhw_draw_pattern on one
instance, times the finder's own recorded calls-per-solve (contention-immune), summed and
divided by golden.capture's own thread CPU for the same cell -- an estimate of the maximum
share a per-solve cache could plausibly save, independent of measuring the full solve twice.

Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D9/verify-v3-leads/v3_dhw_helpers_microbench.py
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time
sys.path[:0] = ["tests", "custom_components"]
import golden  # noqa: E402
from heatpump_optimizer import thermal_model as tm  # noqa: E402

N = 200_000

b = golden.make(two_zone=False, dhw=True, price_profile="winter_typical", weather_profile="winter_cold")
params = b["optimizer"].model.params

t0 = time.thread_time()
for _ in range(N):
    params.dhw_tank_heat_loss_coefficient
t_ua = (time.thread_time() - t0) / N

t0 = time.thread_time()
for _ in range(N):
    params.dhw_inlet_reference
t_inlet = (time.thread_time() - t0) / N

t0 = time.thread_time()
for _ in range(N):
    params.effective_dhw_draw_pattern()
t_pat = (time.thread_time() - t0) / N

print(f"RESULT per_call_s ua={t_ua:.3e} inlet={t_inlet:.3e} pattern={t_pat:.3e}")

# Finder's recorded calls/solve ranges (contention-immune counts, from the finding record).
CALLS = {"winter_single_dhw": (11090, 33205, 98), "winter_two_zone_dhw": (8809, 26364, 98),
         "summer_dhw_only": (3989, 11930, 97), "dhw_cold_tank": (10316, 30879, 98),
         "dhw_learned_windows": (10426, 31213, 100)}

t0 = time.thread_time()
golden.capture("winter_single_dhw", golden.SCENARIOS["winter_single_dhw"])
solve_cpu = time.thread_time() - t0

n_ua, n_inlet, n_pat = CALLS["winter_single_dhw"]
est_helper_cost = n_ua * t_ua + n_inlet * t_inlet + n_pat * t_pat
share = est_helper_cost / solve_cpu
print(f"RESULT winter_single_dhw solve_cpu={solve_cpu:.3f}s est_helper_cost={est_helper_cost:.4f}s "
      f"upper_bound_share={share:.4f}")
print(f"RESULT thread_factor=1.000")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
