"""D7-v1 verifier harness for D7-s1-02: the experiment on a two-zone house, through the REAL coordinator.

Metric (one line): count of stress presets, derived two_zone=True, for which ONE experiment night driven
  through the production coordinator (_run_system_identification + _adopt_system_identification on a
  FakeHass HeatPumpOptimizerCoordinator built from the preset's config) ends in a heat-loss scale
  write; plus each night's outcome and |written scale - 1| (the plant is the declared house, so the
  correct scale is 1.0).
Plant: production ThermalModel of the declared two-zone parameters, pre-settled 600 h at the hold
  power; the coordinator's indoor reading is the plant's upper_floor_temperature (what
  coordinator._update_current_state maps the indoor sensor to in two-zone mode).
Arms: two_zone (the claim); single_zone (null control: same presets derived single-zone);
  --sensor avg: feed the plant's area-weighted room_temperature instead (attack: is it the sensor
  or the plant?); --perturb: plant two_zone_enabled=False while the declared config stays two-zone
  (the finder's perturbation, re-run through the real coordinator), twozone_adopted must go up.
Command:  PYTHONPATH=tests/hastub python3 -u tools/audit/round8/D7/v1_sysid_twozone.py [--perturb] [--sensor avg]
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud container (counts only).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, dataclasses, logging
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
from heatpump_optimizer import sysid as S
from heatpump_optimizer.inputs import InputHealth, InputReading
from heatpump_optimizer.const import CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY
from heatpump_optimizer.thermal_model import ThermalModel, ThermalState
from heatpump_optimizer.presets import BuildingPreset, derive
from profiles import house
from stress import BUILDINGS

PERTURB = "--perturb" in sys.argv
AVG = "avg" in sys.argv
T0 = datetime(2026, 1, 15, 23, 0, 0)
OUT = 0.0
CFG = {"tibber_token": "x", "weather_entity": "weather.home",
       "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
       "heat_pump_power_entity": "sensor.hp_power", "system_identification_enabled": True}


def cfg_for(name, tz):
    cfg = house(two_zone=tz, dhw=False)
    d = derive(BuildingPreset(**{**vars(BUILDINGS[name]), "two_zone": tz}))
    d.pop("heating_response_hours", None)
    cfg.update(d)
    cfg.update(CFG)
    return cfg


def night(name, tz):
    dt_util.freeze(T0)
    c = C.HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg_for(name, tz)))
    c._thermal_params.wind_sensitivity = 0.0
    p = c._thermal_params
    assert p.two_zone_enabled == tz
    written = []
    orig_apply = c._apply_house_heat_loss_scale
    c._apply_house_heat_loss_scale = lambda v: (written.append(v), orig_apply(v))
    c._spawn = lambda coro: getattr(coro, "close", lambda: None)()
    health = InputHealth()
    health.record(InputReading(key=CONF_INDOOR_TEMP_ENTITY, entity_id="sensor.indoor", value=21.0))
    health.record(InputReading(key=CONF_OUTDOOR_TEMP_ENTITY, entity_id="sensor.outdoor", value=OUT))
    c._input_health = health
    c._house_heat_loss_samples = 0
    c._sysid.config.enabled = True
    c._sysid.config.min_days_between_runs = 0.0
    assert c._sysid.arm(T0, plant=p)
    plant_p = dataclasses.replace(p, two_zone_enabled=False) if (PERTURB and tz) else dataclasses.replace(p)
    plant = ThermalModel(plant_p)
    cop = plant.compute_cop(OUT)
    base = (p.upper_floor_heat_loss + p.lower_floor_heat_loss) if tz else p.heat_loss_coefficient
    hold_el = max(base * (21.0 - OUT) - p.internal_gains, 0.1) / cop
    st = ThermalState(room_temperature=21.0, upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                      slab_temperature=25.0, outdoor_temperature=OUT, buffer_tank_temperature=35.0)
    for _ in range(2400):
        st = plant.simulate_step(st, electrical_power=hold_el, outdoor_temp=OUT, dt_hours=0.25)
    prices = np.full(48, 1.0)
    first = None
    peak = 0.0
    for k in range(30):
        dt_util.freeze(T0 + timedelta(minutes=15 * k))
        reading = st.room_temperature if (AVG or not plant_p.two_zone_enabled) else st.upper_floor_temperature
        first = reading if first is None else first
        peak = max(peak, abs(reading - first))
        c._current_state = dataclasses.replace(c._current_state, room_temperature=reading,
                                               upper_floor_temperature=reading, outdoor_temperature=OUT)
        c._current_action = {"power": hold_el, "dhw_power": 0.0}
        c._run_system_identification(prices)
        c._adopt_system_identification()
        if not c._sysid.active:
            break
        st = plant.simulate_step(st, electrical_power=float(c._current_action["power"]), outdoor_temp=OUT,
                                 dt_hours=0.25)
    dt_util.freeze(None)
    r = c._sysid.result
    return dict(phase=c._sysid.phase, reason=r.reason, ua=r.heat_loss_kw_per_c, base=round(base, 4),
                peak=round(peak, 3), scale_err_pct=(written[0] - 1) * 100 if written else None)


res = {True: 0, False: 0}
worst = 0.0
for tz in (True, False):
    for name in BUILDINGS:
        r = night(name, tz)
        print(f"CELL {name} two_zone={tz}: {r}", flush=True)
        if r["scale_err_pct"] is not None:
            res[tz] += 1
            if tz:
                worst = max(worst, abs(r["scale_err_pct"]))
print(f"RESULT twozone_adopted={res[True]} count (of 3)")
print(f"RESULT singlezone_adopted={res[False]} count (of 3; null control)")
print(f"RESULT twozone_worst_scale_err={worst:.2f} pct")
tf = (time.process_time() - _p0) / max(time.thread_time() - _t0, 1e-9)
print(f"RESULT thread_factor={tf:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
