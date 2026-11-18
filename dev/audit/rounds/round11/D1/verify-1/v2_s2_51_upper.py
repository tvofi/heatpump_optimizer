"""Verifier D1#1, V2 for D1-s2-51: the upper plausible bound, by margin and by a real sensor-fault value.

Metric: per key of INPUT_PLAUSIBLE_RANGE_C, InputReader.read deliveries (value not None)
at hi+0.01 and hi+50, and at 85 degC (the DS18B20 power-on value) for keys whose hi < 85.
Controls: lo-0.01 must not deliver (lower bound enforced); hi exactly must deliver.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/verify-1/v2_s2_51_upper.py
"""
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import inputs  # noqa: E402
from heatpump_optimizer.const import INPUT_PLAUSIBLE_RANGE_C as W  # noqa: E402

now = datetime(2026, 2, 1, 6, 0, tzinfo=timezone.utc)


def deliv(key, v):
    h = FakeHass({"sensor.t": FakeState(f"{v}", last_updated=now, unit="°C")})
    return inputs.InputReader(h, {key: "sensor.t"}, now=lambda: now).read(key).value is not None


c = {"hi+0.01": 0, "hi+50": 0, "85_above_hi": 0, "85_keys": 0, "lo-0.01": 0, "hi_exact": 0}
for k, (lo, hi) in W.items():
    c["hi+0.01"] += deliv(k, round(hi + 0.01, 2))
    c["hi+50"] += deliv(k, hi + 50)
    c["lo-0.01"] += deliv(k, round(lo - 0.01, 2))
    c["hi_exact"] += deliv(k, hi)
    if 85 > hi:
        c["85_keys"] += 1
        c["85_above_hi"] += deliv(k, 85.0)
for n, v in c.items():
    print(f"RESULT {n}={v} of {len(W)}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
