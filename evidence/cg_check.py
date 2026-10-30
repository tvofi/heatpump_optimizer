# Reviewer's extract of tests/features.py's R10-COP-GATE r4 check (same fixtures, verbatim body).
import sys
from datetime import timedelta
sys.path.insert(0, "tests")
from harness import FakeEntry as _FakeEntry, FakeHass as _FakeHass, FakeState
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as _Coord
_L5_CFG = {"tibber_token": "x","weather_entity": "weather.home","indoor_temp_entity": "sensor.indoor","outdoor_temp_entity": "sensor.outdoor","heat_pump_power_entity": "sensor.pump_power"}
_L5_STATES = {"sensor.indoor": FakeState("21.0", unit="°C"),"sensor.outdoor": FakeState("-10.0", unit="°C"),"sensor.pump_power": FakeState("2700", unit="W")}
_CF_STATES = dict(_L5_STATES, **{"sensor.outdoor": FakeState("8.0", unit="°C")})
def _cf_coord(p_max=14.0, p_min=1.0):
    cfg = dict(_L5_CFG, heat_pump_max_power=p_max, heat_pump_min_power=p_min)
    return _Coord(_FakeHass(dict(_CF_STATES)), _FakeEntry(data=cfg))
def _cg_aged(age):
    coord = _cf_coord()
    coord._current_state.outdoor_temperature = 8.0
    coord._current_action = {"power": 1.5, "dhw_power": 0.0}
    coord._measured_power = 1.5
    coord._record_accuracy()
    coord._pending_prediction["when"] -= age
    coord._record_accuracy()
    return len(coord._accuracy.samples), len(coord._accuracy.draw.samples)
ages = [timedelta(minutes=1), timedelta(minutes=30), timedelta(hours=3)] + [timedelta(minutes=m) for m in (2,4,118,121)]
res = {str(a): _cg_aged(a) for a in ages}
print(res)
ok = res[str(timedelta(minutes=1))]==(0,0) and res[str(timedelta(minutes=30))]==(1,1) and res[str(timedelta(hours=3))]==(0,0)
print("RESULT check", "PASS" if ok else "FAIL")
