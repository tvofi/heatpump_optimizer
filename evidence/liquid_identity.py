"""Independent check of 25612bf3's equivalence claim: with all-zero snow, p * _liquid_fraction(p, 0) is p bit for bit for every finite non-negative float64 p."""
import sys, numpy as np
sys.path.insert(0, sys.argv[1] + "/custom_components")
from heatpump_optimizer.coordinator import _liquid_fraction, _as_float
rng = np.random.default_rng(20261008)
# random bit patterns -> every exponent, incl. subnormals; keep finite, take abs
bits = rng.integers(0, 2**63, size=2_000_000, dtype=np.uint64)
p = np.abs(bits.view(np.float64)); p = p[np.isfinite(p)]
edge = np.array([0.0, -0.0, 5e-324, 1e-10, 1e-9, np.nextafter(1e-9, 0), np.nextafter(1e-9, 1), 1.0, 1e300, np.finfo(float).max, np.finfo(float).tiny])
p = np.concatenate([p, edge])
out = p * _liquid_fraction(p, np.zeros_like(p))
diff = int(np.sum(out.view(np.uint64) != p.view(np.uint64)))
print(f"RESULT finite_values={p.size} bitwise_differing={diff}")
# control: the distinguishing inputs
ctl = np.array([np.inf, np.nan])
print("CONTROL inf/nan ->", (ctl * _liquid_fraction(ctl, np.zeros(2))).tolist())
# the entity clamp: every non-finite or hostile value becomes finite non-negative
hostile = [float("inf"), float("-inf"), float("nan"), "inf", "1e309", "-1e309", "nan", None, "x", True, np.float32("inf"), np.inf, -3, -0.0, 10**400]
vals = [max(0.0, _as_float(v, 0.0)) for v in hostile]
print("RESULT entity_clamp", all(np.isfinite(v) and v >= 0 for v in vals), vals)
