"""Reviewer's probe (not the finder's): a smart_write valve on a climate that reads no target.

Drives N cycles with the climate 'off' and no temperature attribute, then gives it a target,
and counts the valve writes in each phase. Run from the checkout root:
  PYTHONPATH=tests/hastub:tests python3 <this> [N]
"""
import asyncio, sys
from types import SimpleNamespace
sys.path.insert(0, "tests"); sys.path.insert(0, "tests/hastub"); sys.path.insert(0, "custom_components")
from harness import FakeHass, FakeState, FakeEntry
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord

n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
ent = "climate.valve"
hass = FakeHass({ent: FakeState("off")})
coord = Coord(hass, FakeEntry(data={
    "tibber_token": "x", "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
    "max_temperature": 23.5, "mixing_valve_mode": "smart_write", "mixing_valve_write_entity": ent,
}, entry_id="probe_valve"))
coord.hass.config.units = SimpleNamespace(temperature_unit="°C")
for _ in range(n):
    asyncio.run(coord._command_valve_target())
off_writes = len(hass.services.calls)
hass.states.set(ent, FakeState("heat", attributes={"temperature": 20.0})) if hasattr(hass.states, "set") else hass.states.__setitem__(ent, FakeState("heat", attributes={"temperature": 20.0}))
asyncio.run(coord._command_valve_target())
print(f"RESULT valve_writes_while_climate_off_no_target={off_writes} calls over {n} cycles")
print(f"RESULT valve_writes_after_target_readable={len(hass.services.calls) - off_writes} calls")
