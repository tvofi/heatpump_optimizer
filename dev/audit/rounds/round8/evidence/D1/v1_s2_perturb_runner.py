"""D1 verifier v1: re-runs the finder's s2_ledger_fuzz.py under the finder's own
stated perturbation (MonthlyLedger.from_dict leaf-guards lines[*].kwh/sek and
drops the month on failure), applied in-process and never on disk.
Command (tree root): PYTHONPATH=tests/hastub <thread pins> python3 tools/audit/round8/D1/v1_s2_perturb_runner.py
"""
import os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import runpy, sys
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from heatpump_optimizer import ledger as lg
orig = lg.MonthlyLedger.from_dict.__func__

def guarded(cls, data):
    led = orig(cls, data)
    bad = []
    for k, v in led.months.items():
        try:
            for e in (v.get("lines") or {}).values():
                if isinstance(e, dict):
                    float(e.get("kwh", 0.0)); float(e.get("sek", 0.0))
        except (TypeError, ValueError, OverflowError):
            bad.append(k)
    for k in bad:
        del led.months[k]
    return led
lg.MonthlyLedger.from_dict = classmethod(guarded)
try:
    sys.argv = ["s2_ledger_fuzz.py"]
    runpy.run_path("tools/audit/round8/D1/s2_ledger_fuzz.py", run_name="__main__")
finally:
    lg.MonthlyLedger.from_dict = classmethod(orig)
