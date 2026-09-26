#!/usr/bin/env python3
"""D7 verify-v2 for D7-s2-02: the derate fallback on a latch the production detector sets.

Metric (one line): over a grid of (immersion element kW, outdoor C) cells on a
flag-less install with a heat-pump power meter, the number of cells in which,
after two real input cycles (coordinator._update_current_state reading the
FakeHass meter, so coordinator._detect_immersion sets the latch itself), ONE
settled interval (coordinator._record_accuracy) increments
DefrostDerate.counts while coordinator._cop_fold_blocked is True.
Count key: coord._defrost.counts (the delivered learner state).

Grid: element in (4, 5, 6) kW on a 6 kW-nameplate, 3 kW-commanded pump (the
latch needs measured > 1.15 x nameplate), outdoor in (0.5, 2.5, 4.5) C (inside
the frost band) = 9 cells. Null arm: the same 9 cells at outdoor 7 C (outside
the band) must fold 0. Perturbation (--gate-derate, in memory):
HeatPumpOptimizerCoordinator._settle_defrost returns when _cop_fold_blocked;
count must go to 0. Also prints the published factor() after 24 latched
intervals at 2.5 C, 6 kW element. Counts; contention-immune.

Run (repository root):
    PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D7/verify-v2/derate_latch_grid.py [--gate-derate]
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, cloud container linux. Writes nothing.
"""
from __future__ import annotations
import os
for _p in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_p, "1")
import asyncio, sys, time  # noqa: E402
sys.path.insert(0, ".")
sys.path.insert(0, "tests")
from datetime import timedelta  # noqa: E402
from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as C  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

CMD = 3.0
if "--gate-derate" in sys.argv:
    _o = C.HeatPumpOptimizerCoordinator._settle_defrost

    def _g(self, sample, window):
        if C._cop_fold_blocked(self):
            return
        return _o(self, sample, window)
    C.HeatPumpOptimizerCoordinator._settle_defrost = _g


def build(outdoor, element):
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.0"))
    hass.states.set("sensor.outdoor", FakeState(str(outdoor)))
    hass.states.set("sensor.hp_power", FakeState(str((CMD + element) * 1000), unit="W"))
    hass.states.set("sensor.rh", FakeState("88"))
    coord = C.HeatPumpOptimizerCoordinator(hass, FakeEntry(data={
        "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
        "heat_pump_power_entity": "sensor.hp_power", "heat_pump_max_power": 6.0}))
    coord._current_action = {"power": CMD, "space_power": CMD, "dhw_power": 0.0, "heat_pump_on": True}
    for _ in range(2):
        asyncio.run(coord._update_current_state())
    return coord


def settle(coord, outdoor):
    coord._pending_prediction = {
        "when": dt_util.now() - timedelta(minutes=30), "power": CMD, "space_power": CMD,
        "dhw_power": 0.0, "predicted_temp": 21.0, "price": 1.0, "outdoor": outdoor, "humidity": 88.0}
    coord._record_accuracy()


def grid(outdoors):
    folded = latched = 0
    for el in (4.0, 5.0, 6.0):
        for od in outdoors:
            c = build(od, el)
            blocked = C._cop_fold_blocked(c)
            latched += int(bool(c._immersion_active))
            b = sum(map(sum, c._defrost.counts))
            settle(c, od)
            d = sum(map(sum, c._defrost.counts)) - b
            print(f"  cell element={el} outdoor={od}: latch={c._immersion_active} blocked={blocked} derate_folds={d}")
            folded += int(d > 0 and blocked)
    return folded, latched


def main() -> int:
    c0, t0 = time.process_time(), time.thread_time()
    f, l = grid((0.5, 2.5, 4.5))
    print(f"RESULT cells=9 count")
    print(f"RESULT cells_latched_by_detector={l} count")
    print(f"RESULT derate_folds_while_blocked={f} count")
    fn, ln = grid((7.0,) * 1)
    print(f"RESULT null_outside_band_folds_while_blocked={fn} count  # of 3 cells, latched={ln}")
    c = build(2.5, 6.0)
    for _ in range(24):
        settle(c, 2.5)
    print(f"RESULT factor_after_24_latched={c._defrost.factor(2.5, 88.0):.4f} ratio")
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={(c1-c0)/max(t1-t0,1e-9):.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
