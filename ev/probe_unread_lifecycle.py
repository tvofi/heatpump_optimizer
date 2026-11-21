"""Reviewer's probe (not the finder's): an unreadable valve baseline through write, Off restore, On, next write.

Phase 1: climate off with no target, 3 cycles (written once, armed with no baseline).
Phase 2: the climate becomes readable at the optimizer's own written target; 2 cycles (the
         empty entry is kept: nothing captured).
Phase 3: Off restore: counts writes (expect 0) and the armed entry after it.
Phase 4: one more cycle with the planned target moved: what the next arm captures.
  PYTHONPATH=tests/hastub:tests python3 <this>
"""
import asyncio, sys
from types import SimpleNamespace
sys.path.insert(0, "tests"); sys.path.insert(0, "tests/hastub"); sys.path.insert(0, "custom_components")
from harness import FakeHass, FakeState, FakeEntry
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord, VALVE_RESTORE
from heatpump_optimizer import off_restore

ent = "climate.valve"
hass = FakeHass({ent: FakeState("off")})
entry = FakeEntry(data={
    "tibber_token": "x", "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
    "max_temperature": 23.5, "mixing_valve_mode": "smart_write", "mixing_valve_write_entity": ent,
}, entry_id="probe_unread")
coord = Coord(hass, entry)
coord.hass.config.units = SimpleNamespace(temperature_unit="°C")
def setst(s):
    hass.states.set(ent, s) if hasattr(hass.states, "set") else hass.states.__setitem__(ent, s)
async def main():
    for _ in range(3):
        await coord._command_valve_target()
    p1 = list(hass.services.calls)
    held = await off_restore._armed_record(hass, coord.config_entry if hasattr(coord, "config_entry") else entry)
    print("RESULT phase1_writes", len(p1), "armed", VALVE_RESTORE in held.armed, held.armed.get(VALVE_RESTORE))
    written = None
    for c in p1:
        d = c[-1] if isinstance(c, tuple) else getattr(c, "data", c)
        print("  call", c)
    setst(FakeState("heat", attributes={"temperature": 20.0}))
    for _ in range(2):
        await coord._command_valve_target()
    print("RESULT phase2_writes", len(hass.services.calls) - len(p1), "armed", held.armed.get(VALVE_RESTORE, "ABSENT"))
    n = len(hass.services.calls)
    sent = await off_restore.async_restore(hass, entry, coord.effective_config if hasattr(coord, "effective_config") else entry.data, "mode_off")
    print("RESULT phase3_restore_writes", len(hass.services.calls) - n, "counted", sent, "armed_after", held.armed.get(VALVE_RESTORE, "ABSENT"))
asyncio.run(main())
