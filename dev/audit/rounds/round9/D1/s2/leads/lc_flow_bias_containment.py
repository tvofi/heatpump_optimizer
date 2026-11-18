"""LC catch-up lead (D3-s2-raised, D1-s2-owned): whether a raise out of
FlowCurveBias.observe (reachable if flow_lift.py:210's negative-samples guard
regresses) is contained per cycle by coordinator._record_accuracy, or fails
the whole _async_update_data update.

Metric: over N=5 real per-cycle calls to the real
HeatPumpOptimizerCoordinator._record_accuracy(), with `_flow_bias.samples`
forced to -1 (the state `from_dict`'s guard exists to refuse -- as if that
guard had regressed) and every gate `_fold_flow_lift` itself checks
satisfied, count of calls that (a) raise ZeroDivisionError out of
`_record_accuracy` uncaught, and (b) leave the two per-cycle bookkeeping
calls that follow `_fold_flow_lift` inside `_record_accuracy` (lead-time
accuracy scoring) un-run for that cycle. A null-control arm repeats the same
five cycles with `samples` left at a normal non-negative value (0), where the
guard is intact and `observe` never raises.

Instrumented symbols: coordinator:_fold_flow_lift, coordinator.
HeatPumpOptimizerCoordinator._record_accuracy, flow_lift:FlowCurveBias.observe.
Perturbation: `coord._flow_bias.samples = -1` (bypasses flow_lift.py:210's
`samples < 0` guard directly -- the state the guard exists to keep
unreachable), vs. the null-control `samples = 0`.

Run: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
  tools/audit/round9/D1/s2/leads/lc_flow_bias_containment.py
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
Expected: perturbed arm 5/5 raises, 5/5 scoring calls skipped that cycle;
null-control arm 0/5 raises, 5/5 scoring calls run.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import sys
import time
import resource

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeHass, FakeEntry, FakeState
from heatpump_optimizer import const
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator


def _coord():
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    config = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    }
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=config))
    asyncio.run(coord._update_current_state())
    return coord


def _prime_fold(coord):
    """Satisfy _fold_flow_lift's own five gates (not re-implement them)."""
    coord._flow_bias.observe_temps(35.0, 30.0)  # fresh supply reading
    coord._current_action = {"power": 1000.0, "dhw_power": 0.0}
    coord._immersion_active = False
    # compressor_draw_distorted is a read-only property on a frozen
    # dataclass; its default (no distortion evidence) already passes.


def _run_arm(samples, n=5):
    raises = 0
    scored_after = 0
    for _ in range(n):
        coord = _coord()
        _prime_fold(coord)
        coord._flow_bias.samples = samples
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
    return raises, scored_after


def main():
    t0 = time.process_time()
    pert_raises, pert_scored = _run_arm(-1)
    null_raises, null_scored = _run_arm(0)
    cpu = time.process_time() - t0
    print(f"RESULT perturbed_raises={pert_raises}/5")
    print(f"RESULT perturbed_scored_after_fold={pert_scored}/5")
    print(f"RESULT null_control_raises={null_raises}/5")
    print(f"RESULT null_control_scored_after_fold={null_scored}/5")
    print(f"RESULT cpu_s={cpu:.3f}")
    print(f"RESULT thread_factor=1.0")
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1.0
    print(f"RESULT load1={load1:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_inblock}")


if __name__ == "__main__":
    main()
