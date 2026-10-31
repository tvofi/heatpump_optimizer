"""EG-B5 (#1743) behaviour fingerprint: every tests/golden.py scenario solved at its own prices
and at prices - 2.0 (the shift that tempts the co-optimisation replan), one sha1[:12] per solve of
the published power, DHW, reason and predictive_info fields. Run at two trees in one environment
and diff the output: a verbatim move prints identical lines.
    PYTHONPATH=tests/hastub:custom_components python3 tools/audit/round9/EG-B5/golden_hashes.py
"""
import sys, hashlib, json
import numpy as np
sys.path[:0] = ["tests"]
from golden import make, SCENARIOS, START, external_heat_for
out = {}
for name, sc in SCENARIOS.items():
    b = make(**sc)
    for shift in (0.0, -2.0):
        try:
            r = b["optimizer"].optimize(b["state"], np.asarray(b["prices"], dtype=float) + shift,
                b["outdoor"], b["wind"], b["rain"], b["solar"], START, None, None,
                external_heat_kw=external_heat_for(len(b["prices"])))
            d = {k: getattr(r, k) for k in ("power_schedule", "dhw_power_schedule", "dhw_reasons", "space_reasons", "predictive_info", "dhw_temp_trajectory")}
            out[f"{name}{shift}"] = hashlib.sha1(json.dumps(d, sort_keys=True, default=repr).encode()).hexdigest()[:12]
        except Exception as e:
            out[f"{name}{shift}"] = "ERR " + repr(e)[:80]
for k, v in out.items(): print(k, v)
