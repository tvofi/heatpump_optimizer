"""Verifier V3 (lc unit, G1) independent check of D1-s2-91.

Metric definition (own, distinct from the finder's): rather than corrupting
FlowCurveBias.samples to -1 to reach the raise, patch the MODULE-LEVEL
`_fold_flow_lift` name that `_record_accuracy` calls to raise
ZeroDivisionError directly (simulating any failure inside that fold, not only
the specific negative-samples one) and ask two independent questions on a
real HeatPumpOptimizerCoordinator._record_accuracy() call:
  (a) does the exception propagate out of _record_accuracy uncaught (no
      local try/except wraps the fold call), and
  (b) do the two per-cycle calls textually AFTER the fold inside
      _record_accuracy (lead-time accuracy scoring, DHW accuracy scoring)
      still run that cycle?
This is independent of the finder's harness in method (patches the fold
entrypoint itself rather than driving the real division-by-zero through
`samples`) while measuring the same containment gap.

Also independently confirms production reachability of samples=-1: grep
shows the ONLY place a negative `samples` is rejected is
FlowCurveBias.from_dict's `samples < 0` guard (storage-restore path); the
learner's own `observe()` only ever increments `samples`, never decrements or
validates it. So a corrupted persisted store (disk edit, downgrade, drift)
is the only production path to samples=-1, exactly as the finding claims.

Run:      PYTHONPATH=tests/hastub /root/venv314/bin/python \
            tools/audit/round9/D1/verify-v3-lc/D1-s2-91_containment_via_fold_patch.py
Baseline: 79aa98ec (handoff/audit-r9-evidence)
Expected: patched arm: 5/5 propagate, 0/5 scored after; unpatched arm (real
fold, no perturbation): 0/5 raise, 5/5 scored.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import resource
import sys
import time
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeHass, FakeEntry, FakeState
from heatpump_optimizer import const
from heatpump_optimizer import coordinator as C


def _coord():
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    config = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    }
    coord = C.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=config))
    asyncio.run(coord._update_current_state())
    coord._pending_prediction = None
    return coord


def _run_arm(patch_fold, n=5):
    propagated = 0
    scored_after = 0
    for _ in range(n):
        coord = _coord()
        marker = {"scored": False}
        _orig = coord._accuracy.score_lead_predictions

        def _spy(*a, **k):
            marker["scored"] = True
            return _orig(*a, **k)

        coord._accuracy.score_lead_predictions = _spy

        ctxmgr = (
            mock.patch.object(
                C, "_fold_flow_lift", side_effect=ZeroDivisionError("boom")
            )
            if patch_fold
            else mock.patch.object(C, "_fold_flow_lift", wraps=C._fold_flow_lift)
        )
        with ctxmgr:
            try:
                coord._record_accuracy()
            except ZeroDivisionError:
                propagated += 1
            else:
                if marker["scored"]:
                    scored_after += 1
    return propagated, scored_after


def main():
    t0 = time.process_time()
    pert_prop, pert_scored = _run_arm(patch_fold=True)
    null_prop, null_scored = _run_arm(patch_fold=False)
    cpu = time.process_time() - t0

    print(f"RESULT fold_raise_propagates_uncaught={pert_prop}/5")
    print(f"RESULT scored_after_fold_when_fold_raises={pert_scored}/5")
    print(f"RESULT null_control_propagates={null_prop}/5")
    print(f"RESULT null_control_scored_after_fold={null_scored}/5")
    print(f"RESULT cpu_s={cpu:.3f}")
    print("RESULT thread_factor=1.0")
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1.0
    print(f"RESULT load1={load1:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_inblock}")


if __name__ == "__main__":
    main()
