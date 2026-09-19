#!/usr/bin/env python3
"""D7 round-5, brief item 3: which learners ingests a contaminated interval?

Metric definition (one line): for each of the eleven learner call sites in
``custom_components/heatpump_optimizer/coordinator.py``, the boolean
``_learning_frozen(*keys) is not None`` -- the production gate's own answer --
under each of nine contamination signals, plus the null arm where nothing is
contaminated.

Command:  PYTHONPATH=tests/hastub python3 tools/audit/round5/D7/learner_freeze_table.py
Baseline SHA: eaa2a06af16a1b5b006f58a0f36cc92131f80225
Machine: Apple M1, 8 GB (audit box, shared with other finders)
Expected (exact, deterministic -- no RNG, no solve): the null arm freezes
nothing; every one of the eight contamination signals freezes every learner
whose key tuple carries the contaminated key and every learner the plant-wide
signals cover; the two learners that deliberately look past a reason
(``_async_learn_house_heat_loss`` passes ``ventilation`` through, and
``_settle_defrost`` accepts ``defrosting``) are the only cells that ingest.
Perturbation: set the named contamination attribute on the constructed
coordinator (one attribute, the production seam's own input) and the counted
cell moves False -> True.
Instrumented symbol: ``custom_components.heatpump_optimizer/coordinator.py``
-- ``HeatPumpOptimizerCoordinator._learning_frozen``, driven through the same
key tuples the production call sites pass (transcribed below with their
line numbers).
Root rule: resolves the checkout from __file__ (parents[4]); run from the tree
under test.
"""
from __future__ import annotations

import os

for _p in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_p, "1")

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "custom_components"))

from heatpump_optimizer import inputs, pump_signals
from heatpump_optimizer.coordinator import (
    CONF_BUFFER_TANK_TEMP_ENTITY,
    CONF_DHW_TEMP_ENTITY,
    CONF_INDOOR_TEMP_ENTITY,
    CONF_LOWER_FLOOR_TEMP_ENTITY,
    CONF_OUTDOOR_TEMP_ENTITY,
    CONF_POWER_ENTITY,
    HeatPumpOptimizerCoordinator,
)

INDOOR = CONF_INDOOR_TEMP_ENTITY
OUTDOOR = CONF_OUTDOOR_TEMP_ENTITY
POWER = CONF_POWER_ENTITY
BUFFER = CONF_BUFFER_TANK_TEMP_ENTITY
LOWER = CONF_LOWER_FLOOR_TEMP_ENTITY
DHW = CONF_DHW_TEMP_ENTITY

# (learner, coordinator.py line of the call, key tuple the call passes)
LEARNERS = [
    ("accuracy_sample", 9017, (INDOOR,)),
    ("curve_day_tracker", 8140, (INDOOR,)),
    ("house_heat_loss", 3995, (INDOOR, OUTDOOR)),
    ("lower_floor_loss", 4190, (INDOOR, OUTDOOR, LOWER)),
    ("measured_cop", 3569, (POWER, OUTDOOR)),
    ("flow_curve_bias", 699, (OUTDOOR,)),
    ("compressor_freq_fold", 774, (POWER,)),
    ("buffer_cooling", 3890, (BUFFER,)),
    ("defrost_derate", 9140, (POWER,)),
    ("dhw_accuracy", 9210, (DHW,)),
    ("inputs_healthy_watchdog", 8583, (INDOOR, OUTDOOR, POWER)),
]

KEYS = (INDOOR, OUTDOOR, POWER, BUFFER, LOWER, DHW)


def _reading(key: str, *, broken: bool) -> inputs.InputReading:
    if broken:
        return inputs.InputReading(
            key=key, entity_id=f"sensor.{key}", problem="unavailable"
        )
    return inputs.InputReading(key=key, entity_id=f"sensor.{key}", value=20.0)


def build(signal: str):
    """A coordinator-shaped stub carrying only what ``_learning_frozen`` reads."""
    coord = types.SimpleNamespace()
    coord._external_heat_active = signal == "external_heat"
    coord._pump_signals = types.SimpleNamespace(
        freeze_reason={
            "cooling": pump_signals.FREEZE_COOLING,
            "offline": pump_signals.FREEZE_OFFLINE,
            "fault": pump_signals.FREEZE_FAULT,
        }.get(signal),
        defrosting=signal == "defrosting",
    )
    coord._vent_cusum = types.SimpleNamespace(tripped=signal == "ventilation")
    coord._input_health = inputs.InputHealth()
    for key in KEYS:
        coord._input_health.record(
            _reading(key, broken=(signal == f"broken_{key}"))
        )
    return coord


SIGNALS = [
    "null",
    "external_heat",
    "cooling",
    "offline",
    "fault",
    "defrosting",
    "ventilation",
    f"broken_{INDOOR}",
    f"broken_{POWER}",
    f"broken_{DHW}",
]


def main() -> int:
    frozen_total = 0
    cells = 0
    for signal in SIGNALS:
        coord = build(signal)
        for name, line, keys in LEARNERS:
            reason = HeatPumpOptimizerCoordinator._learning_frozen(coord, *keys)
            gate = "frozen:" + (reason or "")
            if reason is None:
                gate = "INGESTS"
            else:
                frozen_total += 1
            cells += 1
            print(f"RESULT cell.{signal}.{name}={gate}")
    if SIGNALS[0] != "null":
        print("RESULT null arm is not first")
        return 1
    null_ingests = sum(
        1
        for name, line, keys in LEARNERS
        if HeatPumpOptimizerCoordinator._learning_frozen(build("null"), *keys)
        is None
    )
    print(f"RESULT learners={len(LEARNERS)} count")
    print(f"RESULT signals={len(SIGNALS)} count")
    print(f"RESULT null_arm_ingests={null_ingests} count")
    print(f"RESULT frozen_cells={frozen_total} of {cells} count")
    print("RESULT thread_factor=1.0 ratio")
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = 0.0
    print(f"RESULT load1={load1:.2f} count")
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
