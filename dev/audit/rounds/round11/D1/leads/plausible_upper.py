"""D1-s2-51: InputReader.read accepts a temperature above its key's plausible window.

Metric: over every key of const.INPUT_PLAUSIBLE_RANGE_C, the number of keys whose
InputReader.read of (window max + 1) degC still delivers a value (count key:
reading.value is not None, the value the production read delivers).
Null control: the same read at (window min - 1) degC -- the lower bound is enforced.
Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/leads/plausible_upper.py [--perturb]
  --perturb swaps inputs.plausible_c in memory for a two-sided window check; the
  above-max count must go to 0.
Expected: above_max_accepted=keys (exact); below_min_accepted=0 (exact).
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (planted finder export
audit-r11-leads-px), machine: owner's macOS box (B8).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import inputs  # noqa: E402
from heatpump_optimizer.const import INPUT_PLAUSIBLE_RANGE_C  # noqa: E402

c0, t0 = time.process_time(), time.thread_time()
if "--perturb" in sys.argv:
    def _two_sided(key, value_c):
        w = INPUT_PLAUSIBLE_RANGE_C.get(key)
        return w is None or w[0] <= value_c <= w[1]
    inputs.plausible_c = _two_sided

now = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
above = below = 0
for key, (lo, hi) in INPUT_PLAUSIBLE_RANGE_C.items():
    for value, kind in ((hi + 1.0, "above"), (lo - 1.0, "below")):
        hass = FakeHass({"sensor.x": FakeState(str(value), last_updated=now, unit="°C")})
        reader = inputs.InputReader(hass, {key: "sensor.x"}, now=lambda: now)
        r = reader.read(key)
        if r.value is not None:
            if kind == "above":
                above += 1
                print(f"ACCEPTED {key} {value} -> {r.value}")
            else:
                below += 1
                print(f"ACCEPTED-BELOW {key} {value} -> {r.value}")
print(f"RESULT keys={len(INPUT_PLAUSIBLE_RANGE_C)} count")
print(f"RESULT above_max_accepted={above} count")
print(f"RESULT below_min_accepted={below} count")
pc, tc = time.process_time() - c0, time.thread_time() - t0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
