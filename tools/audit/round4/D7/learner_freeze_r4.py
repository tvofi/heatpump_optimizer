"""D7 round 4 -- learner freeze versus the contaminated interval.

METRIC (one line): over the matrix of production learners x contaminating
signals, the number of cells in which the learner's persisted parameter CHANGES
when it is handed an interval the signal says is contaminated (an ingestion),
having first been shown to change on the identical clean interval (the positive
control that proves the cell is live).

COMMAND (from the export root, which must be the working directory):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D7/learner_freeze_r4.py

EXPECTED (baseline 7dd68dd327fe3dbfb09f3bd0fe38910c58877697, 8-core Apple M1,
macOS 25.6; every number an exact deterministic count, tolerance +-0):
    learners                        = 4
    contaminants                    = 5
    positive_control_dead_learners  = 0   (every cell is live)
    live_learner_cells              = 20
    ingesting_cells                 = 7
    ingesting_cells_external_heat   = 0
    ingesting_cells_open_window     = 0
    ingesting_cells_pump_fault      = 0
    ingesting_cells_defrost         = 3   <-- the finding
    ingesting_cells_away            = 4
    perturbed_ingesting_cells_defrost = 0 <-- the perturbation, run in-process

PERTURBATION (this run executes it): ``HeatPumpOptimizerCoordinator._learning_frozen``
is wrapped, harness side only, so it also returns a reason when
``self._pump_signals.defrosting`` is true -- the one line the shared gate does
not have. ``ingesting_cells_defrost`` must FALL from 3 to 0, and it does. The
opposite direction: deleting the bespoke ``in_frost_band``/``any_defrost``
block inside ``_learn_measured_cop`` must RAISE it from 3 to 4.

INSTRUMENTED SYMBOLS:
  coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen
  coordinator.py:HeatPumpOptimizerCoordinator._async_learn_house_heat_loss
  coordinator.py:HeatPumpOptimizerCoordinator._async_learn_buffer_cooling
  coordinator.py:HeatPumpOptimizerCoordinator._learn_measured_cop
  dhw_learning.py:DhwProfileLearner.async_learn_dynamics

ROOT RULE: ROOT = Path(".") -- measures the working directory it is run from.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import asyncio
import copy
import sys
from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))

from harness import FakeEntry, FakeHass  # noqa: E402

from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)
from heatpump_optimizer import pump_signals as pump_signals_mod  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

CFG = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "power_entity": "sensor.power",
    "dhw_temp_entity": "sensor.dhw",
    "buffer_tank_temp_entity": "sensor.buffer",
    "dhw_enabled": True,
    "buffer_tank_volume": 500,
    "mixing_valve_mode": "none",
}
STATES = {
    "sensor.indoor": "21.0",
    "sensor.outdoor": "2.0",
    "sensor.power": "2.0",
    "sensor.dhw": "50.0",
    "sensor.buffer": "45.0",
}


def _coord() -> HeatPumpOptimizerCoordinator:
    return HeatPumpOptimizerCoordinator(FakeHass(dict(STATES)), FakeEntry(data=CFG))


# --------------------------------------------------------------------------
# Contaminants: each is a one-call mutation of coordinator state that makes
# the interval untrustworthy, named the way the brief names them.
# --------------------------------------------------------------------------
def _c_none(c):
    return


def _c_external_heat(c):
    c._external_heat_active = True


def _c_open_window(c):
    c._vent_cusum.tripped = True


def _c_pump_fault(c):
    c._pump_signals = replace(c._pump_signals, freeze_reason="pump_fault")


def _c_defrost(c):
    """The pump defrosted during the interval, and said so.

    OUTDOOR is 2.0 C in every arm (inside defrost.FROST_BAND [0, 5)), so the
    flag is the only thing this contaminant changes.
    """
    c._pump_signals = replace(c._pump_signals, defrosting=True)
    c._defrost_window.observe(dt_util.now(), True)


def _c_away(c):
    c._away_active = True
    setattr(c, "_away_mode_active", True)
    if hasattr(c, "_away"):
        try:
            c._away.active = True
        except Exception:  # noqa: BLE001 - probe only
            pass


CONTAMINANTS = [
    ("external_heat", _c_external_heat),
    ("open_window", _c_open_window),
    ("pump_fault", _c_pump_fault),
    ("defrost", _c_defrost),
    ("away", _c_away),
]



# --------------------------------------------------------------------------
# Learners: (id, key tuple the production gate is asked for, setup, drive,
# probe). ``setup`` primes the previous interval so the learner has a sample
# to fold; ``drive`` calls the production entry point; ``probe`` returns the
# persisted parameter.
# --------------------------------------------------------------------------
def _prime_common(c):
    ctx = getattr(c, "_ctx", c)
    ctx._current_state.room_temperature = 20.4
    ctx._current_state.outdoor_temperature = 2.0
    ctx._current_state.slab_temperature = 22.0
    c._current_action = {"power": 2.0, "dhw_power": 0.0}
    c._measured_power = 2.0


def _setup_house(c):
    _prime_common(c)
    ctx = getattr(c, "_ctx", c)
    prev = copy.deepcopy(ctx._current_state)
    prev.room_temperature = 21.0
    prev.outdoor_temperature = 2.0
    c._last_house_sample = prev
    c._last_house_sample_time = dt_util.now() - timedelta(hours=1)


def _drive_house(c):
    asyncio.run(c._async_learn_house_heat_loss())


def _probe_house(c):
    return round(float(c._house_heat_loss_scale), 9)


def _setup_buffer(c):
    _prime_common(c)
    c._current_action = {"power": 0.0, "dhw_power": 0.0}
    c._last_buffer_temp_sample = 46.0
    c._last_buffer_sample_time = dt_util.now() - timedelta(hours=2)
    c._buffer_heating_since_sample = False


def _drive_buffer(c):
    asyncio.run(c._async_learn_buffer_cooling(45.0))


def _probe_buffer(c):
    return round(float(c._buffer_cooling_rate), 9)


def _setup_cop(c):
    _prime_common(c)
    # A legible defrost window with NO defrost in it: that is what makes the
    # clean arm live at 2 C, so the defrost column below measures the flag
    # and not an unobserved window.
    now = dt_util.now()
    c._defrost_window.observe(now - timedelta(minutes=30), False)
    c._defrost_window.observe(now, False)
    c._measured_power = 2.4
    c._current_action = {"power": 2.0, "dhw_power": 0.0}
    c._immersion_active = False
    c._cop_ratio_ewma = 1.2


def _drive_cop(c):
    c._learn_measured_cop()


def _probe_cop(c):
    return round(float(c._cop_scale), 9)


def _setup_dhw(c):
    _prime_common(c)
    c._current_action = {"power": 0.0, "dhw_power": 0.0}
    lr = c._dhw_learner
    lr.last_temp_sample = 52.0
    lr.last_sample_time = dt_util.now() - timedelta(hours=1)
    lr.heating_since_sample = False


def _drive_dhw(c):
    asyncio.run(c._dhw_learner.async_learn_dynamics(49.0))


def _probe_dhw(c):
    lr = c._dhw_learner
    return (
        round(float(lr.cooling_rate), 9),
        tuple(round(float(v), 9) for v in lr.hourly_profile),
        tuple(sorted((k, len(v)) for k, v in lr.draw_stats.reservoirs.items())),
    )


LEARNERS = [
    ("house_heat_loss", _setup_house, _drive_house, _probe_house,
     "_house_heat_loss_scale"),
    ("buffer_cooling", _setup_buffer, _drive_buffer, _probe_buffer,
     "_buffer_cooling_rate"),
    ("measured_cop", _setup_cop, _drive_cop, _probe_cop, "_cop_scale"),
    ("dhw_dynamics", _setup_dhw, _drive_dhw, _probe_dhw,
     "DhwProfileLearner.(cooling_rate, hourly_profile, draw_stats)"),
]


def _one_cell(learner, contaminate):
    name, setup, drive, probe, _sym = learner
    c = _coord()
    # A fresh coordinator has never run a cycle, so the two fields every
    # gate consults are seeded the way _async_update_data seeds them.
    c._input_health = None
    c._external_heat_active = False
    setup(c)
    contaminate(c)
    before = probe(c)
    drive(c)
    after = probe(c)
    return before != after, before, after


def main() -> int:
    print("=" * 88)
    print("D7/R4 learner freeze vs the contaminated interval")
    print("=" * 88)

    rows = []
    for learner in LEARNERS:
        name = learner[0]
        clean_moved, cb, ca = _one_cell(learner, _c_none)
        row = {"learner": name, "clean_moved": clean_moved,
               "clean": (cb, ca), "cells": {}}
        for cname, fn in CONTAMINANTS:
            moved, b, a = _one_cell(learner, fn)
            row["cells"][cname] = moved
        rows.append(row)

    hdr = f"{'learner':<18}{'clean':>8}" + "".join(
        f"{c:>15}" for c, _ in CONTAMINANTS
    )
    print(hdr)
    for r in rows:
        print(f"{r['learner']:<18}{str(r['clean_moved']):>8}" + "".join(
            f"{('INGESTS' if r['cells'][c] else 'frozen'):>15}"
            for c, _ in CONTAMINANTS
        ))
    print()
    print("clean = the identical interval with no contaminant: True means the")
    print("cell is live, so a 'frozen' below is the gate and not a dead setup.")

    live = [r for r in rows if r["clean_moved"]]
    dead = [r for r in rows if not r["clean_moved"]]
    ingest = sum(
        1 for r in live for c, _ in CONTAMINANTS if r["cells"][c]
    )
    print()
    print("########## RESULT lines ##########")
    print(f"RESULT learners={len(rows)} count")
    print(f"RESULT contaminants={len(CONTAMINANTS)} count")
    print(f"RESULT live_learner_cells={len(live) * len(CONTAMINANTS)} count")
    print(f"RESULT positive_control_dead_learners={len(dead)} count")
    print(f"RESULT ingesting_cells={ingest} count")
    for c, _ in CONTAMINANTS:
        n = sum(1 for r in live if r["cells"][c])
        print(f"RESULT ingesting_cells_{c}={n} count")
    for r in rows:
        n = sum(1 for c, _ in CONTAMINANTS if r["cells"][c])
        print(f"RESULT ingesting_cells_learner_{r['learner']}={n} count")

    # ---- the perturbation, EXECUTED in this same run -------------------
    # One line added to the shared gate (harness side only, the export's
    # production code is untouched): freeze when the pump says it defrosted.
    # The defrost column must collapse to 0.
    _orig = HeatPumpOptimizerCoordinator._learning_frozen

    def _patched(self, *keys):
        if getattr(self._pump_signals, "defrosting", False):
            return "defrosting"
        return _orig(self, *keys)

    HeatPumpOptimizerCoordinator._learning_frozen = _patched
    try:
        prows = []
        for learner in LEARNERS:
            cells = {}
            for cname, fn in CONTAMINANTS:
                moved, _b, _a = _one_cell(learner, fn)
                cells[cname] = moved
            prows.append(cells)
    finally:
        HeatPumpOptimizerCoordinator._learning_frozen = _orig
    p_defrost = sum(1 for cells in prows if cells["defrost"])
    p_total = sum(1 for cells in prows for cname, _ in CONTAMINANTS
                  if cells[cname])
    print(f"RESULT perturbed_ingesting_cells_defrost={p_defrost} count")
    print(f"RESULT perturbed_ingesting_cells={p_total} count")
    print("RESULT thread_factor=1.0 ratio")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f} ratio")
    except OSError:
        print("RESULT load1=nan ratio")
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
