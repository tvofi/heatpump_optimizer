"""N-staleness probe (round 11, SW2): one on-change key, held quiet, through a real cycle.

Generalises D14-s2-01's staleness_flags.py to any INPUT_ON_CHANGE_MAX_AGE_MINUTES key:
indoor/outdoor fresh, KEY's entity holding a quiet value for HELD minutes as a
report-on-change source (last_reported None: never seen re-reporting), one real
``_update_current_state`` + ``_build_data_dict``.  rc=1 when KEY is published in
``stale_inputs`` (and so turns InputHealthBinarySensor on).

Run: PYTHONPATH=tests/hastub python3 probe.py CONF_KEY [--held MIN] [--perturb inf]
  --held 10      null arm (changed 10 min ago)          -> rc=0
  --perturb inf  INPUT_ON_CHANGE_MAX_AGE_MINUTES[KEY]=inf -> rc=0
"""
import argparse
import asyncio
import sys

sys.path.insert(0, "tests")
from harness import FakeCoordinator, FakeEntry, FakeHass, FakeState, minutes_ago  # noqa: E402
from heatpump_optimizer import binary_sensor, const  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

BINARY = {"CONF_HEAT_PUMP_FAULT_ENTITY": "off", "CONF_HEAT_PUMP_DEFROST_ENTITY": "off",
          "CONF_HEAT_PUMP_ONLINE_ENTITY": "on", "CONF_HEAT_PUMP_BACKUP_HEATER_ENTITY": "off",
          "CONF_HEAT_PUMP_DHW_BOOSTER_ENTITY": "off", "CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY": "off",
          "CONF_EXTERNAL_HEAT_ENTITY": "off"}
QUIET_VALUE = {"CONF_SOLAR_RADIATION_ENTITY": "0.0", "CONF_PV_PRODUCTION_ENTITY": "0.0",
               "CONF_VALVE_OUTLET_TEMP_ENTITY": "35.0", "CONF_WOOD_TANK_TOP_ENTITY": "60.0",
               "CONF_WOOD_TANK_BOTTOM_ENTITY": "40.0"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("key")
    ap.add_argument("--held", type=float, default=255.0)
    ap.add_argument("--perturb", choices=("none", "inf"), default="none")
    a = ap.parse_args()
    key = getattr(const, a.key)
    if a.perturb == "inf":
        const.INPUT_ON_CHANGE_MAX_AGE_MINUTES[key] = float("inf")
    hass = FakeHass()
    fresh = minutes_ago(1)
    hass.states.set("sensor.indoor", FakeState("21.4", last_updated=minutes_ago(20), last_reported=fresh))
    hass.states.set("sensor.outdoor", FakeState("-3.0", last_updated=minutes_ago(20), last_reported=fresh))
    eid = ("binary_sensor." if a.key in BINARY else "sensor.") + "probe_" + a.key.lower()
    val = BINARY.get(a.key) or QUIET_VALUE.get(a.key, "0.0")
    if a.key == "CONF_EXTERNAL_HEAT_ENTITY":
        eid = "binary_sensor.probe_external"
    hass.states.set(eid, FakeState(val, last_updated=minutes_ago(a.held), last_reported=None))
    config = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor", const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
              const.CONF_DHW_TANK_VOLUME: 180.0, key: eid}
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=config))
    asyncio.run(coord._update_current_state())
    data = coord._build_data_dict()
    stale = key in (data.get("stale_inputs") or [])
    on = binary_sensor.InputHealthBinarySensor(FakeCoordinator(data), FakeEntry(data=config)).is_on
    lim = const.INPUT_ON_CHANGE_MAX_AGE_MINUTES.get(key)
    print(f"RESULT key={a.key} limit={lim} held={a.held} in_stale_inputs={int(stale)} input_problem_on={int(bool(on))}")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
