import sys; sys.path.insert(0,"tests")
from datetime import datetime
from harness import FakeHass, FakeState, UTC, minutes_ago
from heatpump_optimizer import flow_meter as fm, const
from heatpump_optimizer.inputs import InputReader
NOW = datetime(2026, 2, 1, 12, 0, tzinfo=UTC)
def run(age, unit="L/min", val="15.0"):
    st={"sensor.flow":FakeState(val,last_updated=minutes_ago(age,NOW),unit=unit),
        "sensor.sup":FakeState("45.0",last_updated=minutes_ago(1,NOW),unit="°C"),
        "sensor.ret":FakeState("40.0",last_updated=minutes_ago(1,NOW),unit="°C")}
    cfg={const.CONF_FLOW_METER_ENTITY:"sensor.flow",const.CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY:"sensor.sup",const.CONF_HEAT_PUMP_RETURN_TEMP_ENTITY:"sensor.ret"}
    r=InputReader(FakeHass(st),cfg,now=lambda:NOW)
    kw=fm.read_heat_output_kw(r,cfg)
    h=r.health.readings.get(const.CONF_FLOW_METER_ENTITY)
    return kw, (h.problem if h else None)
print("RESULT fresh(1min) ->", run(1))
print("RESULT stale(90min) ->", run(90))
print("RESULT unit gal/min ->", run(1,"gal/min"))
print("RESULT m3/h 0.9 ->", run(1,"m³/h","0.9"))
