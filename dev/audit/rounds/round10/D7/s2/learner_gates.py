"""D7.M3 -- learner freeze table: per contamination, does each learner's own gate admit the sample?

Metric: freq_map_defrost_folds = number of FrequencyMap.observe calls made by
coordinator:HeatPumpOptimizerCoordinator._observe_frequency over N=8 intervals with
PumpSignals.defrosting=True (a defrost interval every other learner refuses).
Count key: calls into FrequencyMap.observe (the value the production seam delivers into the map).
Null control: the same 8 intervals with defrosting=False -> 8 folds (the arm works);
the COP learner's gate (_learning_frozen(POWER, OUTDOOR)) on the defrost arm -> refuses.
Run:   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/s2/learner_gates.py [--perturb]
--perturb patches coordinator:_freq_fold_blocked to also return True on defrosting;
the defrost fold count must drop 8 -> 0.  Expected: 8 (exact) at baseline.
Baseline 17f1c55fad1b; machine B5 (macOS arm64), venv-ci. Root rule: cwd.
"""
import os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time
sys.path.insert(0, "custom_components"); sys.path.insert(0, "tests")
from dataclasses import replace
from datetime import datetime, timezone
from unittest import mock
t0p, t0t = time.process_time(), time.thread_time()
from harness import FakeHass, FakeEntry
import heatpump_optimizer.coordinator as C
from heatpump_optimizer.const import (CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY,
    CONF_POWER_ENTITY, CONF_BUFFER_TANK_TEMP_ENTITY)
from heatpump_optimizer.freq_control import FrequencyMap

PERTURB = "--perturb" in sys.argv
cfg = {"tibber_token": "x", "weather_entity": "weather.home",
       "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}
coord = C.HeatPumpOptimizerCoordinator(FakeHass({}), FakeEntry(data=cfg))
base_signals = coord._pump_signals

def scen(name):
    coord._pump_signals = base_signals
    coord._external_heat_active = False
    coord._vent_cusum.tripped = False
    if name == "external_heat": coord._external_heat_active = True
    elif name == "defrost": coord._pump_signals = replace(base_signals, defrosting=True)
    elif name == "pump_offline": coord._pump_signals = replace(base_signals, online=False, freeze_reason="pump_offline")
    elif name == "open_window": coord._vent_cusum.tripped = True

def gates():
    f = coord._learning_frozen
    hl = f(CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY)
    power = f(CONF_POWER_ENTITY)
    return {
        "heat_loss(+gains,+solar)": hl is None,
        "cop_scale(+health,+envelope)": f(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY) is None,
        "flow_bias": f(CONF_OUTDOOR_TEMP_ENTITY) is None,
        "buffer_cooling": f(CONF_BUFFER_TANK_TEMP_ENTITY) is None,
        "curve_learner": f(CONF_INDOOR_TEMP_ENTITY) is None,
        "defrost_derate": power in (None, "defrosting"),
        "accuracy": C._accuracy_freeze_allows_sample(hl),
        "freq_map": not C._freq_fold_blocked(coord),
    }

orig_block = C._freq_fold_blocked
def perturbed(c):
    return orig_block(c) or bool(c._pump_signals.defrosting)

def folds(n=8):
    calls = []
    with mock.patch.object(FrequencyMap, "observe", lambda self, *a, **k: calls.append(a)), \
         mock.patch.object(type(coord), "_freq_entity_reading", lambda self: (40.0, 20.0, 90.0, "sensor")):
        coord._measured_power = 1.5; coord._immersion_active = False
        for _ in range(n):
            coord._observe_frequency(datetime(2026, 1, 15, 3, tzinfo=timezone.utc))
    return len(calls)

ctx = mock.patch.object(C, "_freq_fold_blocked", perturbed) if PERTURB else mock.patch.object(C, "_freq_fold_blocked", orig_block)
with ctx:
    print("contamination | " + " | ".join(gates().keys()))
    for s in ("clean", "external_heat", "defrost", "pump_offline", "open_window"):
        scen(s); g = gates()
        print(f"{s} | " + " | ".join("INGEST" if v else "frozen" for v in g.values()))
        print(f"RESULT {s}.learners_ingesting={sum(g.values())} count")
    scen("clean"); clean = folds()
    scen("defrost"); dfz = folds()
    scen("defrost"); cop_refuses = coord._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY)
print(f"RESULT freq_map_clean_folds={clean} count")
print(f"RESULT freq_map_defrost_folds={dfz} count")
print(f"RESULT cop_gate_on_defrost={cop_refuses!r}")
tf = (time.process_time()-t0p)/max(time.thread_time()-t0t,1e-9)
print(f"RESULT thread_factor={tf:.3f}"); print(f"RESULT load1={os.getloadavg()[0]:.2f}"); print("RESULT swapins=0")
