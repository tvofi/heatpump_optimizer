"""Judge (round 8) production-side perturbation for D2-s2-02.

Wraps price_model.prices_from_entity_state so that raw attribute values are
converted to SEK/kWh by the state's unit_of_measurement (öre/kWh x0.01,
SEK/MWh x0.001) BEFORE production parses them -- the fix the finding proposes,
applied in-process (never on disk) -- then runs s2_price_unit.py unchanged.
Expected: import ratio_* -> 1.0000 for every unit; export ratios unchanged
(the _pv_export_price seam is not patched), which shows the export seam is a
second, independent read.
Command (tree root): PYTHONPATH=tests/hastub python3 tools/audit/round8/D2/judge_price_unit_fix.py
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, runpy, copy
sys.path.insert(0, "tests"); sys.path.insert(0, ".")
from custom_components.heatpump_optimizer import price_model as pm
F = {"öre/kWh": 0.01, "SEK/MWh": 0.001}
orig = pm.prices_from_entity_state

def fixed(state, vat=1.0, surcharge=0.0):
    attrs = getattr(state, "attributes", None) or {}
    unit = attrs.get("unit_of_measurement") or getattr(state, "unit", None) \
        or getattr(state, "_unit", None)
    f = F.get(unit, 1.0)
    if f != 1.0:
        st = copy.copy(state)
        a = copy.deepcopy(dict(attrs))
        for k in ("raw_today", "raw_tomorrow"):
            for r in a.get(k) or []:
                r["value"] = float(r["value"]) * f
        st.attributes = a
        state = st
    return orig(state, vat, surcharge)

pm.prices_from_entity_state = fixed
try:
    sys.argv = ["s2_price_unit.py"]
    runpy.run_path("tools/audit/round8/D2/s2_price_unit.py", run_name="__main__")
finally:
    pm.prices_from_entity_state = orig
