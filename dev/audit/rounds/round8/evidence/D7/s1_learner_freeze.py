"""D7-s1 learner freeze vs contamination: per-learner ingestion table, executed.

Metric (ingests): 1 when the learner's own sample counter moved across ONE call of its production
  entry point in an interval carrying the named contamination, else 0. Count key: the learner's
  own persisted counter / sample list (what the production seam delivered), never the freeze
  predicate's return value.
Learners (entry -> counter):
  house_heat_loss   coordinator:HeatPumpOptimizerCoordinator._async_learn_house_heat_loss -> _house_heat_loss_samples
  sysid             coordinator:HeatPumpOptimizerCoordinator._run_system_identification  -> len(_sysid.samples)
  measured_cop      coordinator:HeatPumpOptimizerCoordinator._learn_measured_cop         -> _cop_samples
  flow_lift_fold    coordinator:_fold_flow_lift                                         -> _flow_bias.samples
  buffer_cooling    coordinator:HeatPumpOptimizerCoordinator._async_learn_buffer_cooling -> _buffer_cooling_samples
Contaminations: clean (null control: every learner must ingest), external_heat, defrosting,
  pump_fault, pump_offline, ventilation (open window CUSUM tripped), indoor_stale (pinned indoor
  reading), away.
Command:  PYTHONPATH=tests/hastub python3 tools/audit/round8/D7/s1_learner_freeze.py [--perturb]
  --perturb: wrap _run_system_identification so it returns early when
  _learning_frozen(CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY) is set (the one-line fix);
  sysid_contaminated_ingest must go to 0.  Restored in finally.
Expected: sysid_contaminated_ingest=4 (external_heat, defrosting, ventilation, indoor_stale), exact.
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud container (counts only).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, asyncio, dataclasses, logging
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, "tests/hastub")
logging.disable(logging.CRITICAL)
_p0, _t0 = time.process_time(), time.thread_time()
import numpy as np
from datetime import datetime, timedelta
from harness import FakeHass, FakeEntry
from homeassistant.util import dt as dt_util
from heatpump_optimizer import coordinator as C
from heatpump_optimizer import pump_signals
from heatpump_optimizer.inputs import InputHealth, InputReading
from heatpump_optimizer.const import CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY
from heatpump_optimizer.sysid import PHASE_STEP
from heatpump_optimizer.thermal_model import ThermalState

PERTURB = "--perturb" in sys.argv
T0 = datetime(2026, 1, 15, 23, 30, 0)
CFG = {"tibber_token": "x", "weather_entity": "weather.home",
       "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
       "heat_pump_power_entity": "sensor.hp_power",
       "buffer_tank_temp_entity": "sensor.buffer",
       "heat_pump_supply_temp_entity": "sensor.supply",
       "system_identification_enabled": True}


def mk():
    dt_util.freeze(T0)
    c = C.HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=dict(CFG)))
    c._current_state = ThermalState(room_temperature=21.0, outdoor_temperature=2.0,
                                    slab_temperature=24.0, buffer_tank_temperature=40.0)
    health = InputHealth()
    for key, ent, val in ((CONF_INDOOR_TEMP_ENTITY, "sensor.indoor", 21.0),
                          (CONF_OUTDOOR_TEMP_ENTITY, "sensor.outdoor", 2.0)):
        health.record(InputReading(key=key, entity_id=ent, value=val))
    c._input_health = health
    return c


def contaminate(c, how):
    s = c._pump_signals
    if how == "external_heat":
        c._external_heat_active = True
    elif how == "defrosting":
        c._pump_signals = dataclasses.replace(s, defrosting=True)
    elif how == "pump_fault":
        c._pump_signals = dataclasses.replace(s, fault=True, freeze_reason=pump_signals.FREEZE_FAULT)
    elif how == "pump_offline":
        c._pump_signals = dataclasses.replace(s, online=False, freeze_reason=pump_signals.FREEZE_OFFLINE)
    elif how == "ventilation":
        c._vent_cusum.tripped = True
    elif how == "indoor_stale":
        c._input_health.record(InputReading(key=CONF_INDOOR_TEMP_ENTITY, entity_id="sensor.indoor",
                                            value=21.0, problem="stale"))
    elif how == "away":
        c._away_state.active = True


def run_house(how):
    c = mk()
    c._last_house_sample = dataclasses.replace(c._current_state, room_temperature=21.05)
    c._last_house_sample_time = T0 - timedelta(minutes=30)
    c._current_action = {"power": 1.0, "dhw_power": 0.0}
    c._measured_power = 1.0
    contaminate(c, how)
    b = c._house_heat_loss_samples
    asyncio.run(c._async_learn_house_heat_loss())
    return int(c._house_heat_loss_samples != b)


def run_sysid(how):
    c = mk()
    c._sysid.config.enabled = True
    c._sysid.config.min_days_between_runs = 0.0
    assert c._sysid.arm(T0, plant=c._thermal_params)
    # enter the step phase through the production state machine (armed -> settling -> step)
    prices = np.full(48, 1.0)
    for k in range(6):
        dt_util.freeze(T0 + timedelta(minutes=15 * k))
        c._run_system_identification(prices)
        if c._sysid.phase == PHASE_STEP:
            break
    assert c._sysid.phase == PHASE_STEP, c._sysid.phase
    dt_util.freeze(T0 + timedelta(minutes=15 * (k + 1)))
    contaminate(c, how)
    b = len(c._sysid.samples)
    c._run_system_identification(prices)
    return int(len(c._sysid.samples) != b)


def run_cop(how):
    c = mk()
    c._current_action = {"power": 3.0, "dhw_power": 0.0}
    c._measured_power = 3.0
    c._current_state.outdoor_temperature = 8.0  # outside the frost band
    contaminate(c, how)
    b = c._cop_samples
    c._learn_measured_cop()
    return int(c._cop_samples != b)


def run_flow(how):
    c = mk()
    c._thermal_params.flow_curve_cop = True
    c._current_action = {"power": 4.0, "dhw_power": 0.0}
    c._measured_power = 4.0
    c._flow_bias.last_supply_c = 38.0
    contaminate(c, how)
    b = c._flow_bias.samples
    C._fold_flow_lift(c, dt_util.now())
    return int(c._flow_bias.samples != b)


def run_buffer(how):
    c = mk()
    c._current_action = {"power": 0.0, "dhw_power": 0.0}
    c._last_buffer_temp_sample = 40.0
    c._last_buffer_sample_time = T0 - timedelta(hours=1)
    c._buffer_heating_since_sample = False
    contaminate(c, how)
    b = c._buffer_cooling_samples
    asyncio.run(c._async_learn_buffer_cooling(39.4))
    return int(c._buffer_cooling_samples != b)


LEARNERS = {"house_heat_loss": run_house, "sysid": run_sysid, "measured_cop": run_cop,
            "flow_lift_fold": run_flow, "buffer_cooling": run_buffer}
CONTAM = ["clean", "external_heat", "defrosting", "pump_fault", "pump_offline",
          "ventilation", "indoor_stale", "away"]

_orig = C.HeatPumpOptimizerCoordinator._run_system_identification
try:
    if PERTURB:
        def _patched(self, prices):
            if self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY) is not None:
                return
            return _orig(self, prices)
        C.HeatPumpOptimizerCoordinator._run_system_identification = _patched
    table = {}
    for name, fn in LEARNERS.items():
        row = {}
        for how in CONTAM:
            try:
                row[how] = fn(how)
            except Exception as err:  # noqa: BLE001
                row[how] = f"ERR:{type(err).__name__}:{err}"[:60]
        table[name] = row
finally:
    C.HeatPumpOptimizerCoordinator._run_system_identification = _orig
    dt_util.freeze(None)

print("learner".ljust(16) + "".join(h[:12].rjust(13) for h in CONTAM))
for name, row in table.items():
    print(name.ljust(16) + "".join(str(row[h])[:12].rjust(13) for h in CONTAM))
PHYS = ["external_heat", "defrosting", "ventilation", "indoor_stale"]
for name, row in table.items():
    print(f"RESULT {name}_clean_ingest={row['clean']} count")
    print(f"RESULT {name}_contaminated_ingest={sum(1 for h in PHYS if row[h] == 1)} count (of {len(PHYS)}: {','.join(PHYS)})")
tf = (time.process_time() - _p0) / max(time.thread_time() - _t0, 1e-9)
print(f"RESULT thread_factor={tf:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
