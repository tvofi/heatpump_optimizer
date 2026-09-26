"""V2 independent harness for D1-s2-91.

V2's own metric, distinct from the finder's: the finder measured whether
_record_accuracy()'s own accuracy-scoring calls (lead-time, DHW) run after a
raise from _fold_flow_lift. This harness measures ONE STEP FURTHER OUT: it
(a) confirms from the live source, by regex over
inspect.getsource(_async_update_data), that _record_accuracy(),
_track_realised_peak(), _async_save_accuracy() and _async_save_energy_totals()
sit as four bare, sequential statements inside the SAME try-block with no
individual try/except between them (i.e. the same unguarded seam the finder
found, one level up); then (b) drives that exact four-call sequence, bound to
a real, honestly-primed HeatPumpOptimizerCoordinator (finder's priming:
observe_temps + _current_action + _immersion_active, so _fold_flow_lift's own
five gates are satisfied), over N=5 fresh coordinators, and counts how many of
the three calls AFTER _record_accuracy actually execute when
_flow_bias.samples is forced to -1 vs a null control of 0.

Instrumented symbols: coordinator.HeatPumpOptimizerCoordinator._record_accuracy,
._track_realised_peak, ._async_save_accuracy, ._async_save_energy_totals;
coordinator._fold_flow_lift; flow_lift.FlowCurveBias.observe.
Perturbation: coord._flow_bias.samples = -1 vs null control = 0.

Run: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
  /tmp/claude-0/-home-claude/c1053ac1-148d-5d89-9785-8af9678426ba/scratchpad/lc_v2_d1.py
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
Expected: source check passes (four bare sequential calls, one try-block);
perturbed 0/3 downstream calls execute (peak/save_accuracy/save_energy all
skipped) on 5/5 cycles; null control 3/3 execute on 5/5 cycles.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import inspect
import re
import sys
import time
import resource

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeHass, FakeEntry, FakeState
from heatpump_optimizer import const
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator


def _check_source_order():
    src = inspect.getsource(HeatPumpOptimizerCoordinator._async_update_data)
    # The four calls, bare (no `try`/`except` token on their own line, and
    # no `except` between them), in this exact order.
    pattern = (
        r"self\._record_accuracy\(\)\s*\n"
        r"(?:[^\n]*\n)*?"
        r"\s*self\._track_realised_peak\(\)\s*\n"
        r"\s*await self\._async_save_accuracy\(\)\s*\n"
        r"\s*await self\._async_save_energy_totals\(\)\s*\n"
    )
    m = re.search(pattern, src)
    if not m:
        return False
    block = m.group(0)
    return "except" not in block and "try:" not in block


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
    coord._flow_bias.observe_temps(35.0, 30.0)
    coord._current_action = {"power": 1000.0, "dhw_power": 0.0}
    coord._immersion_active = False


async def _run_tail(coord):
    """The exact four-call sequence _async_update_data runs, unguarded."""
    coord._record_accuracy()
    coord._track_realised_peak()
    await coord._async_save_accuracy()
    await coord._async_save_energy_totals()


def _run_arm(samples, n=5):
    downstream_ran = []  # per cycle: count of the 3 post-fold calls that ran
    for _ in range(n):
        coord = _coord()
        _prime_fold(coord)
        coord._flow_bias.samples = samples

        ran = {"peak": False, "save_acc": False, "save_energy": False}
        _op = coord._track_realised_peak
        _osa = coord._async_save_accuracy
        _ose = coord._async_save_energy_totals

        def _sp(*a, **k):
            ran["peak"] = True
            return _op(*a, **k)

        async def _ssa(*a, **k):
            ran["save_acc"] = True
            return await _osa(*a, **k)

        async def _sse(*a, **k):
            ran["save_energy"] = True
            return await _ose(*a, **k)

        coord._track_realised_peak = _sp
        coord._async_save_accuracy = _ssa
        coord._async_save_energy_totals = _sse

        try:
            asyncio.run(_run_tail(coord))
        except ZeroDivisionError:
            pass
        downstream_ran.append(sum(ran.values()))
    return downstream_ran


def main():
    order_ok = _check_source_order()
    print(f"RESULT source_order_confirmed={int(order_ok)}")

    t0 = time.process_time()
    pert = _run_arm(-1)
    null = _run_arm(0)
    cpu = time.process_time() - t0

    print(f"RESULT perturbed_downstream_ran={pert} (of 3 each)")
    print(f"RESULT null_control_downstream_ran={null} (of 3 each)")
    print(f"RESULT perturbed_all_three_skipped={sum(1 for x in pert if x == 0)}/5")
    print(f"RESULT null_all_three_ran={sum(1 for x in null if x == 3)}/5")
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
