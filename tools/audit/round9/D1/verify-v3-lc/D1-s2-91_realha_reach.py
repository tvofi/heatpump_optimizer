"""Verifier V3 (lc unit, G1) real-HA reachability check of D1-s2-91.

Metric: on a real HeatPumpOptimizerCoordinator built on a genuine
homeassistant.core.HomeAssistant (2026.2.3, no tests/hastub anywhere on
sys.path), with `_flow_bias.samples` forced to -1 the same way the finder
does, does `coord._record_accuracy()` still raise ZeroDivisionError
uncaught? This answers the lens question directly: is the path reachable in
real Home Assistant, not only through tests/hastub's FakeHass.

Run:      PYTHONPATH=custom_components:tests /root/venvha/bin/python \
            tools/audit/round9/D1/verify-v3-lc/D1-s2-91_realha_reach.py
Baseline: 79aa98ec (handoff/audit-r9-evidence)
Expected: 5/5 raises on real HA, matching the stub result.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys
import time
import resource

sys.path.insert(0, os.path.dirname(__file__))
import _realha_rig as rig  # noqa: E402


def main():
    t0 = time.process_time()
    raises = 0
    scored_after = 0
    for _ in range(5):
        coord = rig.build_coordinator()
        coord._flow_bias.observe_temps(35.0, 30.0)
        coord._current_action = {"power": 1000.0, "dhw_power": 0.0}
        coord._immersion_active = False
        coord._flow_bias.samples = -1
        coord._pending_prediction = None
        marker = {"scored": False}
        _orig = coord._accuracy.score_lead_predictions

        def _spy(*a, **k):
            marker["scored"] = True
            return _orig(*a, **k)

        coord._accuracy.score_lead_predictions = _spy
        try:
            coord._record_accuracy()
        except ZeroDivisionError:
            raises += 1
        else:
            if marker["scored"]:
                scored_after += 1
    cpu = time.process_time() - t0
    print(f"RESULT realha_raises={raises}/5")
    print(f"RESULT realha_scored_after_fold={scored_after}/5")
    print(f"RESULT cpu_s={cpu:.3f}")
    rig.tail()


if __name__ == "__main__":
    main()
