# Judge cross-check: D8-s1-01's harness under D2-s3-01's perturbation (the seam's 1 h span -> 15 min, only inside _current_spot_price).
import runpy, sys
from datetime import timedelta
from unittest import mock
sys.path[:0] = ["tests", "tests/hastub", "custom_components"]
from heatpump_optimizer import coordinator as cm
class _Span:
    def __call__(self, *a, **kw):
        if kw == {"hours": 1} and not a: return timedelta(minutes=15)
        return timedelta(*a, **kw)
if "--perturb" in sys.argv:
    sys.argv.remove("--perturb")
    orig = cm.HeatPumpOptimizerCoordinator._current_spot_price
    def patched(self):
        with mock.patch.object(cm, "timedelta", _Span()):
            return orig(self)
    cm.HeatPumpOptimizerCoordinator._current_spot_price = patched
runpy.run_path("tools/audit/round9/D8/s1/price15.py", run_name="__main__")
