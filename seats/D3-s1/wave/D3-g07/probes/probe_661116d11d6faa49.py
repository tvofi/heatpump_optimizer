#!/usr/bin/env python3
# Metric: count of inputs on which _indoor_humidity_value() differs between the baseline and the mutant that removes the
#   `if not entity_id: return None` early exit, comparing the returned value AND the log records emitted (any level).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_661116d11d6faa49.py
# EXPECTED RESULT inputs_tried=12 count  (entity unset / None / "" x bus states: empty, a live 55 % humidity sensor,
#   an unavailable sensor, a 150 % sensor)
# EXPECTED RESULT inputs_differing=0 count  (with no entity id, InputReader(hass, {}).read() resolves no entity and
#   returns ok=False; its InputHealth is a local of the call and is discarded, so the fall-through returns None too)
# EXPECTED RESULT positive_baseline=55.0 %, positive_mutant=55.0 %  (configured entity: the probe sees the value)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g07 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB RAM).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._indoor_humidity_value, line 9170.
# Perturbation: key 661116d11d6faa49 (GUARD_OFF), line 9170 `if not entity_id:` -> `if False:`, in memory.
#   Direction: none found (would be value or log records differing on an unset entity).
# Null control: a configured entity, where the edited guard is not taken in either arm.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import logging
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402
from harness import FakeState  # noqa: E402

BASE = L.baseline("_indoor_humidity_value")
MUT = L.mutant("_indoor_humidity_value", "if not entity_id:", "if False:")


class Rec(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)
        self.n = []

    def emit(self, r):
        self.n.append((r.name, r.levelno, r.getMessage()))


root = logging.getLogger()
root.setLevel(logging.DEBUG)


def run(fn, states, **cfg):
    c = L.coord(states, **cfg)
    h = Rec()
    root.addHandler(h)
    try:
        v = fn(c)
    except Exception as e:  # an exception is a difference too
        v = f"EXC {type(e).__name__}"
    finally:
        root.removeHandler(h)
    return v, h.n


bus = {
    "empty": {},
    "live55": {"sensor.rh": FakeState("55.0", attributes={"unit_of_measurement": "%"})},
    "unavail": {"sensor.rh": FakeState("unavailable")},
    "rh150": {"sensor.rh": FakeState("150", attributes={"unit_of_measurement": "%"})},
}
cfgs = {"unset": {}, "none": {"indoor_humidity_entity": None}, "empty": {"indoor_humidity_entity": ""}}
tried = differ = 0
for cn, cfg in cfgs.items():
    for bn, st in bus.items():
        tried += 1
        b, bl = run(BASE, st, **cfg)
        m, ml = run(MUT, st, **cfg)
        if (b, len(bl)) != (m, len(ml)):
            differ += 1
            print(f"DIFF cfg={cn} bus={bn} base={b!r}/{len(bl)} mut={m!r}/{len(ml)}")
print(f"RESULT inputs_tried={tried} count")
print(f"RESULT inputs_differing={differ} count")
pb, _ = run(BASE, bus["live55"], indoor_humidity_entity="sensor.rh")
pm, _ = run(MUT, bus["live55"], indoor_humidity_entity="sensor.rh")
print(f"RESULT positive_baseline={pb} %")
print(f"RESULT positive_mutant={pm} %")
L.footer()
