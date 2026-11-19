"""D16.M6 (restore): which written entities off, unload, remove and a duty-mode change return to baseline.

Metric: per trigger, the number of entities the optimizer wrote whose state after the trigger (and one
cycle after it, for off and the duty change) differs from the state it held before the optimizer's first
write; plus the number of restore writes each entity received (the brief: "returned to its baseline, once").
Count key: the entity state the stub's state machine holds after every recorded ``services.async_call`` is
applied to it (select_option -> option, set_value/set_temperature -> value, turn_on/off -> on/off), i.e. the
value the production seam delivered, never an attribute of the harness's own records.

Command (from the export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D16/s3/m6_restore.py [--perturb P]
    P in arbiter | consumers | both | memo | all (in memory only; see install_perturbation)
Arms: off / unload / remove / duty_change (Tuya select, a hot-water-only then an idle step); off_modbus (the Modbus
select, space-only steps: the tank set-point carries the gate); *_disinfecting (the Tuya arm with the integration
holding the pump's disinfection program on, so the arbiter raised the tank to the cycle target 60).
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (exact, counts):
    RESULT unrestored_off=5 (mode, supply, frequency, valve, circulation pump)
    RESULT unrestored_unload=4 / unrestored_remove=4 (supply, frequency, valve, circulation pump)
    RESULT unrestored_duty_change=7 (those four plus both MQTT topics and the heat-curve entity, restored at the
           unload and re-written by the observe-mode reload)
    RESULT unrestored_off_modbus=4 (tank set-point at the gate 40, frequency, valve, circulation pump)
    RESULT unrestored_off_disinfecting=6 / unload_disinfecting=5 / remove_disinfecting=5 / duty_change_disinfecting=8
           (the tank set-point left at 60 in each)
    --perturb arbiter  : off 4, off_modbus 3 (the release() baseline row written on entering Off: mode, tank)
    --perturb consumers: off 1, unload 0, remove 0, off_modbus 1, unload/remove_disinfecting 1 (supply/freq/valve/pump)
    --perturb memo     : unload_disinfecting 4, remove_disinfecting 4 (the hold dropped before release(): tank 50)
    --perturb all      : 0 but duty_change 7, duty_change_disinfecting 7 and off_disinfecting 1 (hold live at Off)
    Per entity: RESULT unrestored_<arm>__<entity>=0|1.
Null control: RESULT null_unrestored_* = 0 -- the same plant, drive and triggers with a plan that starts two hours
ahead (the arbiter serves its baseline row) and commands equal to each entity's baseline, so nothing is owed.
Machine: box B11 (shared). Plant: coord_all_features plus the actuator slots below; the harness builds the plan.
Instrumented symbols: coordinator:HeatPumpOptimizerCoordinator.async_set_mode / _apply_action / _command_frequency /
_command_valve_target / _async_drive_pumps / async_shutdown, pump_arbiter:_arbitrate / release / switch_supply /
_dhw_target, off_restore:async_mode_change / async_restore, heat_curve:publish, legionella:LegionellaGuard.
async_release_switch / async_track_cycle, heatpump_optimizer:async_unload_entry / async_remove_entry.
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import time  # noqa: E402

_T_PROC0, _T_THR0 = time.process_time(), time.thread_time()
sys.path[:0] = ["tests", "custom_components"]

import argparse  # noqa: E402
import asyncio  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import logging  # noqa: E402
from dataclasses import replace  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402

logging.disable(logging.CRITICAL)

import golden  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import off_restore, pump_arbiter  # noqa: E402
from heatpump_optimizer.const import MODE_AUTO, MODE_OFF  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.inputs import InputReader  # noqa: E402
from heatpump_optimizer.optimizer import OptimizationResult  # noqa: E402

T0 = datetime(2026, 1, 10, 6, 0, tzinfo=timezone.utc)
_IDS = itertools.count()
TUYA = ["Heating", "DHW (Hot Water)", "Heating + DHW", "Cooling", "Cooling + DHW"]
#: The GCHV/Rotenso Modbus select: no single heating duty, so a space-only step gates the tank set-point.
MODBUS = ["Off", "Cool + DHW", "Heat + DHW"]

BASELINE = {
    "select.pump_mode": "Heating + DHW",
    "number.dhw_set": "50",
    "number.water_set": "45",
    "switch.hp": "on",
    "number.freq": "70",
    "number.valve": "22",
    "switch.vvc": "on",
    "number.offset": "0",              # the heat-curve entity arm (offset kind: neutral 0)
    "switch.dis": "off",               # the pump's own disinfection program switch
    "mqtt:ecl110/displace/set": "0",   # the ECL110 MQTT arm (neutral displace 0)
    "mqtt:ecl110/command": "0",        # its legacy JSON topic, keyed on the body's command.displace
}


def config(duty="control", windows="08:00-09:00"):
    return {
        **golden.coordinator_scenarios()["coord_all_features"],
        "dhw_setpoint": 50.0,
        "pump_duty_mode": duty,
        "heat_pump_mode_entity": "select.pump_mode",
        "dhw_setpoint_entity": "number.dhw_set",
        "space_setpoint_entity": "number.water_set",
        "space_setpoint_unit": "flow",
        "heat_pump_switch_entity": "switch.hp",
        "compressor_freq_entity": "number.freq",
        "freq_control_mode": "control",
        "mixing_valve_mode": "smart_write",
        "mixing_valve_write_entity": "number.valve",
        "vvc_pump_entity": "switch.vvc",
        "heat_curve_displace_entity": "number.offset",
        "ecl110_displace_set_topic": "ecl110/displace/set",
        "ecl110_command_topic": "ecl110/command",
        "dhw_disinfection_switch_entity": "switch.dis",
        "dhw_disinfection_mode": "control",
        "dhw_windows": windows,  # the null arm's window covers the clock: the circulation pump stays on
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
    }


def states(base=BASELINE, options=TUYA):
    return {
        "select.pump_mode": FakeState(base["select.pump_mode"], attributes={"options": list(options)}),
        "number.dhw_set": FakeState(base["number.dhw_set"], attributes={"min": 40, "max": 63}),
        "number.water_set": FakeState(base["number.water_set"], attributes={"min": 25, "max": 63}),
        "switch.hp": FakeState(base["switch.hp"]),
        "number.freq": FakeState(base["number.freq"], attributes={"min": 20, "max": 90}),
        "number.valve": FakeState(base["number.valve"], attributes={"min": 15, "max": 30}),
        "switch.vvc": FakeState(base["switch.vvc"]),
        "number.offset": FakeState(base["number.offset"], unit="K", attributes={"min": -10, "max": 10, "step": 1}),
        "switch.dis": FakeState(base["switch.dis"]),
        "mqtt:ecl110/displace/set": FakeState(base["mqtt:ecl110/displace/set"]),
        "mqtt:ecl110/command": FakeState(base["mqtt:ecl110/command"]),
        "sensor.indoor": FakeState("21.0", unit="°C"),
        "sensor.outdoor": FakeState("-5.0", unit="°C"),
    }


def plan(duties, start=T0):
    """The harness's own solve result: 's' space 1.5 kW, 'd' hot water 2 kW, '-' idle, from ``start``."""
    n = len(duties)
    return OptimizationResult(
        power_schedule=[1.5 if c in "sb" else 0.0 for c in duties],
        room_temp_trajectory=[21.0] * n, slab_temp_trajectory=[21.0] * n,
        timestamps=[start + timedelta(minutes=15 * i) for i in range(n)], prices=[1.0] * n,
        predicted_cost=0.0, baseline_cost=0.0, predicted_savings=0.0, savings_percentage=0.0,
        optimal_setpoints=[21.0] * n, status="ok",
        dhw_power_schedule=[2.0 if c in "db" else 0.0 for c in duties],
    )


def key_of(data):
    """The written thing a call names: its entity, or ``mqtt:<topic>`` for a publish."""
    data = data or {}
    return data.get("entity_id") or (f"mqtt:{data['topic']}" if "topic" in data else None)


def make_hass(base=BASELINE, options=TUYA):
    """A FakeHass whose disinfection switch follows a write at once (the module reads every write back)."""
    hass = FakeHass(states(base, options))
    real = hass.services.async_call

    async def device(domain, service, data=None, **kw):
        out = await real(domain, service, data, **kw)
        if (data or {}).get("entity_id") == "switch.dis" and service in ("turn_on", "turn_off"):
            hass.states.get("switch.dis").state = "on" if service == "turn_on" else "off"
        return out
    hass.services.async_call = device
    return hass


def settle(hass):
    """Apply every recorded call to the state machine, as the device would; return them."""
    calls = list(hass.services.calls)
    for domain, service, data in calls:
        data = data or {}
        ent = key_of(data)
        if service == "publish" and ent is not None:
            payload = str(data["payload"])
            if payload.startswith("{"):
                payload = str(json.loads(payload)["command"]["displace"])
            hass.states.get(ent).state = payload
            continue
        st = hass.states.get(ent) if isinstance(ent, str) else None
        if st is None:
            continue
        if service == "select_option":
            st.state = str(data["option"])
        elif service in ("set_value", "set_temperature"):
            v = data.get("value", data.get("temperature"))
            st.state = str(int(v) if float(v).is_integer() else v)
        elif service in ("turn_on", "turn_off"):
            st.state = "on" if service == "turn_on" else "off"
    hass.services.calls.clear()
    return calls


async def cycle(c, minute, post=False):
    """The cycle's write half at T0+minute: the arbiter and supply (and the MQTT and heat-curve arms the
    action publishes), frequency, valve, circulation pump; ``post`` adds the disinfection follower."""
    dt_util.freeze(T0 + timedelta(minutes=minute))
    c._last_optimization = T0 + timedelta(minutes=minute)  # a fresh plan
    await c._apply_action()
    await c._command_frequency()
    await c._command_valve_target()
    await c._async_drive_pumps()
    if post:
        # The cycle's legionella step: read the switch, then follow the boost (async_observe's order).
        c._legionella.disinfect.observe(InputReader(c.hass, dict(c.entry.data)))
        await c._legionella.async_track_cycle(None)


def new_coord(hass, entry):
    c = HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = c
    c._freq_map.recommend = lambda *_a, **_k: 45.0  # input: a frequency map with evidence
    c._freq_last_write = None  # input: no write inside the rate limit (construction stamps the wall clock)
    return c


async def drive(c, null=False, duties="dd--dd--", disinfect=False):
    """Write phase: a hot-water-only step, then an idle step, of the harness's plan.

    Null arm: the plan starts two hours ahead, so the arbiter serves its baseline row; the action keeps the
    supply on and the valve at its reading, the frequency map answers the reading, the circulation pump's
    window covers the clock: every write equals the baseline, so nothing can be owed back."""
    c._mode = MODE_AUTO
    c._optimization_result = plan(duties, start=T0 + timedelta(hours=2) if null else T0)
    c._current_action = {"heat_pump_on": True, "displace_value": 0.0 if null else 2.0,
                         "valve_target": 22.0 if null else 20.0}
    if null:
        c._freq_map.recommend = lambda *_a, **_k: 70.0
    written = set()
    await cycle(c, 1)
    if disinfect and not null:
        # A planned disinfection run starts the pump's program (the integration holds the switch on); the
        # arbiter's next pass raises the tank to the cycle temperature (pump_arbiter._dhw_target).
        await c._legionella.disinfect.turn_on(dhw_blocked=False)
    written |= {key_of(d) for _do, _s, d in settle(c.hass)}
    if not null:
        c._current_action = {"heat_pump_on": False, "displace_value": 3.0, "valve_target": 18.0}
    await cycle(c, 31)
    written |= {key_of(d) for _do, _s, d in settle(c.hass)}
    return written


def install_perturbation(kind):
    """In memory only. 'arbiter': entering Off writes release()'s baseline row (mode, hot water) first.
    'consumers': the supply switch, the frequency, the valve and the circulation pump register with off_restore and
    arm before each write (neutral on for the two switches, the pre-write reading for the two numbers)."""
    undo = []
    if kind in ("memo", "all"):
        # The unload drops the disinfection hold before the arbiter's release computes its baseline row.
        from heatpump_optimizer import legionella
        orig_rel = legionella.LegionellaGuard.async_release_switch

        async def release_switch(self):
            await orig_rel(self)
            self.disinfect.memo = None
        legionella.LegionellaGuard.async_release_switch = release_switch
        undo.append(lambda: setattr(legionella.LegionellaGuard, "async_release_switch", orig_rel))
    if kind in ("arbiter", "both", "all"):
        orig = off_restore.async_mode_change

        async def mode_change(hass, entry, cfg, old, new):
            sent = await orig(hass, entry, cfg, old, new)
            coord = getattr(entry, "runtime_data", None)
            if new == MODE_OFF and old != MODE_OFF and coord is not None:
                inp = coord.arbiter_inputs()
                if pump_arbiter.state_for(coord).written:
                    now = dt_util.now()
                    await pump_arbiter._command(coord, inp, replace(
                        pump_arbiter.desired(coord, inp, None, now), space_setpoint=None), now)
            return sent
        off_restore.async_mode_change = mode_change
        undo.append(lambda: setattr(off_restore, "async_mode_change", orig))
    if kind in ("consumers", "both", "all"):
        from heatpump_optimizer import coordinator as cmod
        from heatpump_optimizer.inputs import read_setpoint, write_setpoint

        async def write_switch(hass, entity, value):
            await pump_arbiter.switch_supply(hass, entity, bool(value))

        def reading(hass, entity):
            try:
                return float(hass.states.get(entity).state)
            except (AttributeError, TypeError, ValueError):
                return None
        off_restore.register_consumer("h_supply", lambda cfg: off_restore.Restorer(
            cfg.heat_pump_switch_entity, write_switch, neutral=1.0) if cfg.heat_pump_switch_entity else None)
        off_restore.register_consumer("h_freq", lambda cfg: off_restore.Restorer(
            cfg.compressor_freq_entity, write_setpoint, baseline_of=reading) if cfg.compressor_freq_entity else None)
        off_restore.register_consumer("h_valve", lambda cfg: off_restore.Restorer(
            cfg.mixing_valve_write_entity, write_setpoint, baseline_of=reading) if cfg.mixing_valve_write_entity else None)

        async def write_vvc(hass, entity, value):
            await hass.services.async_call("homeassistant", "turn_on" if value else "turn_off", {"entity_id": entity})
        off_restore.register_consumer("h_vvc", lambda cfg: off_restore.Restorer(
            cfg.vvc_pump_entity, write_vvc, neutral=1.0) if cfg.vvc_pump_entity else None)
        orig_pump = cmod.HeatPumpOptimizerCoordinator._async_set_pump

        async def set_pump(self, entity_id, on, reason):
            if self._mode != MODE_OFF and self._pump_commanded.get(entity_id) != on:
                await arm(self, "h_vvc")
            await orig_pump(self, entity_id, on, reason)
        cmod.HeatPumpOptimizerCoordinator._async_set_pump = set_pump
        orig_sw, orig_f, orig_v = pump_arbiter.switch_supply, cmod.HeatPumpOptimizerCoordinator._command_frequency, \
            cmod.HeatPumpOptimizerCoordinator._command_valve_target
        orig_set_mode = cmod.HeatPumpOptimizerCoordinator.async_set_mode

        async def arm(c, key):
            await off_restore.async_arm(c.hass, c.entry, cmod._ctx_of(c)._config, key)

        async def switch_supply(hass, entity, on):
            entry = next(iter(_LIVE), None)
            if entry is not None and entry.runtime_data is not None and not entry.runtime_data._entry_released:
                await arm(entry.runtime_data, "h_supply")
            await orig_sw(hass, entity, on)

        async def cmd_freq(self):
            if self._mode != MODE_OFF:
                await arm(self, "h_freq")
            await orig_f(self)

        async def cmd_valve(self):
            if self._mode != MODE_OFF:
                await arm(self, "h_valve")
            await orig_v(self)
        pump_arbiter.switch_supply = switch_supply
        cmod.HeatPumpOptimizerCoordinator._command_frequency = cmd_freq
        cmod.HeatPumpOptimizerCoordinator._command_valve_target = cmd_valve

        def _undo():
            pump_arbiter.switch_supply = orig_sw
            cmod.HeatPumpOptimizerCoordinator._command_frequency = orig_f
            cmod.HeatPumpOptimizerCoordinator._command_valve_target = orig_v
            cmod.HeatPumpOptimizerCoordinator.async_set_mode = orig_set_mode
            cmod.HeatPumpOptimizerCoordinator._async_set_pump = orig_pump
            for k in ("h_supply", "h_freq", "h_valve", "h_vvc"):
                off_restore._CONSUMERS.pop(k, None)
                off_restore._WRITERS.pop(k, None)
        undo.append(_undo)
    return undo


_LIVE: list = []
TRIGGERS = ("off", "unload", "remove", "duty_change", "off_modbus", "off_disinfecting", "unload_disinfecting",
            "remove_disinfecting", "duty_change_disinfecting")
#: The pump arbiter's slots (pump_arbiter._SLOTS' mode and hot water); the rest have no restore owner.
ARBITER_SLOTS = ("select.pump_mode", "number.dhw_set")


async def run(trigger, null=False):
    disinfect = trigger.endswith("_disinfecting")
    trigger = trigger.removesuffix("_disinfecting")
    modbus = trigger.endswith("_modbus")
    base = {**BASELINE, "select.pump_mode": "Heat + DHW"} if modbus else BASELINE
    hass = make_hass(base, MODBUS if modbus else TUYA)
    entry_id = f"m6s3_{trigger}_{int(null)}_{next(_IDS)}"
    windows = "05:00-09:00" if null else "08:00-09:00"
    entry = FakeEntry(data=config(windows=windows), entry_id=entry_id)
    _LIVE[:] = [entry]
    c = new_coord(hass, entry)
    written = await drive(c, null, duties="ssssssss" if modbus else "dd--dd--", disinfect=disinfect)
    trigger = trigger.removesuffix("_modbus")
    written.discard(None)
    after = []
    if trigger == "off":
        await c.async_set_mode(MODE_OFF, refresh=False)
        after += settle(hass)
        for minute in (32, 46, 61):  # the cycles and arbiter passes that follow, still off
            await cycle(c, minute, post=True)
            after += settle(hass)
    elif trigger in ("unload", "remove", "duty_change"):
        await integration.async_unload_entry(hass, entry)
        after += settle(hass)
        if trigger == "remove":
            await integration.async_remove_entry(hass, entry)
            after += settle(hass)
        if trigger == "duty_change":
            # The options save that changes the duty mode reloads the entry (async_update_options).
            entry2 = FakeEntry(data=config(duty="observe", windows=windows), entry_id=entry_id)
            _LIVE[:] = [entry2]
            c2 = new_coord(hass, entry2)
            c2._freq_map.recommend = c._freq_map.recommend
            c2._mode = MODE_AUTO
            c2._optimization_result = c._optimization_result
            c2._current_action = dict(c._current_action)
            await cycle(c2, 46, post=True)
            after += settle(hass)
    unrestored = sorted(e for e in written if str(hass.states.get(e).state) != base[e])
    restores = {e: sum(1 for _d, _s, data in after if key_of(data) == e) for e in sorted(written)}
    finals = {e: hass.states.get(e).state for e in sorted(written)}
    return written, unrestored, restores, finals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", choices=("none", "arbiter", "consumers", "both", "memo", "all"), default="none")
    args = ap.parse_args()
    dt_util.DEFAULT_TIME_ZONE = timezone.utc
    undo = install_perturbation(args.perturb)
    try:
        for trig in TRIGGERS:
            written, unrestored, restores, finals = asyncio.run(run(trig))
            print(f"# {trig}: written={sorted(written)}")
            print(f"#   final={finals}")
            print(f"#   writes after trigger={restores}")
            print(f"#   not at baseline={unrestored}")
            print(f"RESULT unrestored_{trig}={len(unrestored)} entities")
            arb = [e for e in unrestored if e in ARBITER_SLOTS]
            print(f"RESULT unrestored_{trig}_arbiter_slots={len(arb)} entities")
            print(f"RESULT unrestored_{trig}_unregistered={len(unrestored) - len(arb)} entities")
            for e in sorted(written):
                print(f"RESULT unrestored_{trig}__{e}={int(e in unrestored)} bool")
            print(f"RESULT written_{trig}={len(written)} entities")
            print(f"RESULT restored_more_than_once_{trig}={sum(1 for e, n in restores.items() if n > 1 and e not in unrestored)} entities")
        for trig in TRIGGERS:
            written, unrestored, _r, finals = asyncio.run(run(trig, null=True))
            print(f"# null {trig}: written={sorted(written)} not at baseline={unrestored} final={finals}")
            print(f"RESULT null_unrestored_{trig}={len(unrestored)} entities")
            print(f"RESULT null_written_{trig}={len(written)} entities")
    finally:
        for u in undo:
            u()
        dt_util.freeze(None)
    proc, thr = time.process_time() - _T_PROC0, time.thread_time() - _T_THR0
    print(f"RESULT thread_factor={proc / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/self/stat") as fh:
            print(f"RESULT swapins={fh.read().split()[11]}")
    except OSError:
        print("RESULT swapins=n/a")


if __name__ == "__main__":
    main()
