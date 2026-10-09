"""review-2070's own probe (reviewer-built, not the finder's): drives the
production early_cutoff listener on synthetic numbers. Run with
HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub:custom_components:tests."""
import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace as NS

from harness import FakeHass, FakeState
from homeassistant.util import dt as dt_util
from heatpump_optimizer import early_cutoff as ec
from heatpump_optimizer.boost import BoostState
from heatpump_optimizer.const import MODE_AUTO
from heatpump_optimizer.pump_arbiter import ArbiterInputs

SW, ROOM = "switch.hp", "sensor.room"
UTC = timezone.utc


def plan(t0, n=8, room=21.0, start=None):
    traj = [room] * (n + 1)
    if start is not None:
        traj[0] = start
    return NS(timestamps=[t0 + timedelta(minutes=15 * i) for i in range(n)],
              power_schedule=[1.5] * n, dhw_power_schedule=[0.0] * n,
              room_temp_trajectory=traj, duty_floor_kw=None)


def world(t0, sw_since, p):
    hass = FakeHass({SW: FakeState("on", last_updated=sw_since), ROOM: FakeState("21.0")})
    hass.async_create_task = lambda coro: asyncio.run(coro)
    inp = ArbiterInputs(hass=hass, config={"indoor_temp_entity": ROOM, "heat_pump_switch_entity": SW,
                                           "optimization_interval": 30},
                        mode=MODE_AUTO, plan=p, plan_stale=False, entry_released=False,
                        state=NS(dhw_temperature=50.0, lower_floor_temperature=21.0),
                        thermal=None, params=NS(dhw_enabled=False, two_zone_enabled=False),
                        action={"heat_pump_on": True}, measured_power_kw=None, disinfecting=False)
    cfg = NS(get_comfort_temp=lambda h, when=None: 21.0)
    return hass, ec.CutoffInputs(lambda: inp, BoostState(), cfg)


def event(v):
    return NS(data={"new_state": FakeState(f"{v:.2f}", unit="°C")})


def offs(hass):
    return sum(1 for c in hass.services.calls if c[1] == "turn_off")


def at(t):
    dt_util.freeze(t)


# P1 spring-forward: switch on 00:55Z (01:55 CET), reading 01:02Z (03:02 CEST).
t_arm = datetime(2026, 3, 29, 0, 50, tzinfo=UTC)
held = ec.CutoffState()
hass, w = world(t_arm, datetime(2026, 3, 29, 0, 55, tzinfo=UTC), plan(datetime(2026, 3, 29, 0, 45, tzinfo=UTC)))
at(t_arm); asyncio.run(ec.arm(held, w, lambda f: None, dt_util.now()))
at(datetime(2026, 3, 29, 1, 2, tzinfo=UTC)); ec.on_room_event(held, w, event(22.5))
print(f"RESULT P1 dst-spring min_on: run 7 min UTC (67 wall) offs={offs(hass)} held={held.last_held}")

# P1b fall-back: armed 00:35Z (02:35 CEST), interval 30 -> end 01:05Z; reading 00:58Z (02:58 CEST)
#  switch on since 00:20Z. 7 min to the cycle end -> must hold min_off.
held = ec.CutoffState()
hass, w = world(None, datetime(2026, 10, 25, 0, 20, tzinfo=UTC), plan(datetime(2026, 10, 25, 0, 30, tzinfo=UTC)))
at(datetime(2026, 10, 25, 0, 35, tzinfo=UTC)); asyncio.run(ec.arm(held, w, lambda f: None, dt_util.now()))
at(datetime(2026, 10, 25, 1, 3, tzinfo=UTC)); ec.on_room_event(held, w, event(22.5))
print(f"RESULT P1b dst-fall min_off: 2 min to cycle end offs={offs(hass)} held={held.last_held}")

# P2 unscheduled cycle: cut at 12:12Z, a user refresh re-arms at 12:13Z and
# switches the pump back on; a warm reading at 12:24Z.
t0 = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
held = ec.CutoffState()
hass, w = world(t0, t0 - timedelta(minutes=30), plan(t0))
at(t0); asyncio.run(ec.arm(held, w, lambda f: None, t0))
at(t0 + timedelta(minutes=12)); ec.on_room_event(held, w, event(22.0))
n1 = offs(hass)
hass.states.set(SW, FakeState("off", last_updated=t0 + timedelta(minutes=12)))
at(t0 + timedelta(minutes=13)); asyncio.run(ec.arm(held, w, lambda f: None, dt_util.now()))
hass.states.set(SW, FakeState("on", last_updated=t0 + timedelta(minutes=13)))
at(t0 + timedelta(minutes=24)); ec.on_room_event(held, w, event(22.0))
print(f"RESULT P2 unscheduled re-arm: first cut={n1} total cuts={offs(hass)} off-period=1 min "
      f"(second cut after an 11-min run) held={held.last_held}")

# P3 measured-start-room: trajectory[0]=22.5 measured, predicted end 21.0, reading 22.4.
held = ec.CutoffState()
hass, w = world(t0, t0 - timedelta(minutes=30), plan(t0, start=22.5))
at(t0); asyncio.run(ec.arm(held, w, lambda f: None, t0))
at(t0 + timedelta(minutes=3)); ec.on_room_event(held, w, event(22.4))
print(f"RESULT P3 measured-start: threshold={ec.threshold(w.inputs(), w.opt_config, dt_util.now()):.2f} offs={offs(hass)}")

# P4 null: room at the plan's own pre-heat 22.5, reading 22.9 (<= 23.0)
held = ec.CutoffState()
hass, w = world(t0, t0 - timedelta(minutes=30), plan(t0, room=22.5))
at(t0); asyncio.run(ec.arm(held, w, lambda f: None, t0))
at(t0 + timedelta(minutes=3)); ec.on_room_event(held, w, event(22.9))
print(f"RESULT P4 pre-heat null: offs={offs(hass)}")

# P5 services written across every probe: only turn_off on the switch.
print("RESULT P5 domains written:", sorted({(c[0], c[1], c[2].get('entity_id')) for c in hass.services.calls}) or "none")
dt_util.freeze(None)
