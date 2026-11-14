"""Reviewer's probe (builder: the fix-review seat): the round's three production edits change no value."""
import math, sys, itertools
import numpy as np
sys.path.insert(0, "custom_components/heatpump_optimizer")
import importlib.util
spec = importlib.util.spec_from_file_location("duty_legs", "custom_components/heatpump_optimizer/duty_legs.py")
try:
    dl = importlib.util.module_from_spec(spec); spec.loader.exec_module(dl)
except Exception:
    sys.path.insert(0, "."); sys.path.insert(0, "tests/hastub")
    from custom_components.heatpump_optimizer import duty_legs as dl
def old_pair(values, upper=math.inf):
    try: pair = [float(v) for v in values]
    except (TypeError, ValueError): return 0.0, 0.0
    if len(pair) != 2: return 0.0, 0.0
    a, b = (v if math.isfinite(v) and 0.0 <= v <= upper else 0.0 for v in pair)
    return a, b
vals = [0.0, -0.0, 1e-300, -1e-300, 0.5, 1.0, 1.0000001, -1.0, 501.0, math.inf, -math.inf, math.nan, True, "0.3", "x", None]
mis = n = 0
for a, b in itertools.product(vals, vals):
    for up in (math.inf, 1.0):
        n += 1
        o, w = old_pair((a, b), up), dl.priced_pair((a, b), up)
        if repr(o) != repr(w): mis += 1; print("MISMATCH", a, b, up, o, w)
for bad in (None, 3, (1,), (1, 2, 3), "ab"):
    n += 1; mis += repr(old_pair(bad)) != repr(dl.priced_pair(bad))
print(f"RESULT priced_pair_cases={n} mismatches={mis}")
rng = np.random.default_rng(7); z = rows = 0
for floor in (None, 1.2):
    for _ in range(200):
        sp = rng.choice([0.0, 0.5, 1.0, 2.5, 6.0], size=(4, 24)) * rng.integers(0, 2, size=(4, 24))
        dh = rng.choice([0.0, 0.8, 2.0, 3.0], size=24)
        w = dl.switch_weights_batch(sp, dh, (0.0, 0.0), 6.0, floor)
        rows += 4; z += int(np.count_nonzero(w)) + int(w.shape != (4,))
        # -0.0 is still zero-valued; sign checked separately
print(f"RESULT zero_pair_rows={rows} nonzero_or_misshapen={z}")
lost0 = dl.lost_share((1.0, 0.0), (0.0, 0.0))
print(f"RESULT availability_at_zero_lost={dl.availability(np.array([0.,2.5]), np.array([2.,0.]), lost0)} lost={lost0}")
print(f"RESULT availability_at_negative_lost={dl.availability(np.array([0.,2.5]), np.array([2.,0.]), -0.1)}")
