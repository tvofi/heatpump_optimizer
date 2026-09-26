#!/usr/bin/env python3
"""D8 round 9, verifier V2 (independent): entity values against the ACTUATOR.

The oracle here is the service call the production cycle makes on the heat
pump supply switch (``heat_pump_switch_entity`` -> ``switch.turn_on/turn_off``
recorded by FakeHass.services.calls), not the plan's action dict the finders
read. Every entity is built through its platform's real ``async_setup_entry``;
every cycle is the production ``_async_update_data`` (weather through the
registered ``weather.get_forecasts`` service; prices injected by replacing the
Tibber fetch only; solve in-process through tests/replay.InProcessWorker).
Prices: tests/profiles.py prices("winter_typical") (hourly, 48 h).

METRICS (one RESULT per finding, each keyed on the value the entity returns):
  s1_02_runs_mismatch   cycles where the integer leading DHW Heating Schedule's
                        state != number of contiguous runs of dhw_power > 0.1 kW
                        in the same payload's dhw_schedule (the entity's own
                        threshold, its own list); + null arm: cycles whose every
                        run is one step long (must be equal there)
  s1_03_power_vs_switch cycles where Recommended Power > 0.05 kW while the cycle's
                        last supply-switch call is turn_off (default
                        heat_pump_min_power 1.0 kW), 5 topologies x 24 hourly
                        instants; + the same at min_power 0.2 (null arm)
  s2_01_unavailable     cells with a fresh payload (last_update_success True)
                        where climate.available is False; arms: no indoor entity
                        (5 topologies), indoor configured and reading (null),
                        indoor configured but 'unavailable' state
  s2_02_off_while_on    arms where the cycle's last supply-switch call is turn_on
                        while climate.hvac_action is OFF (mode off + live boost);
                        null arm: same boost at mode auto
  s2_03_split_writes    immediate state writes made by climate.async_set_hvac_mode
                        (OFF) / OptimizerEnableSwitch.async_turn_off after a cycle
                        that heats, in which (hvac_mode OFF / is_on False) and
                        (hvac_action HEATING / attribute mode != 'off') coexist
RUN:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D8/verify-v2/v2_entities.py [--only s1_02,s1_03,...]
      [--perturb-s103]  commanded_power_kw returns 0.0 when heat_pump_on is False
      [--perturb-s201]  climate.available = CoordinatorEntity.available
      [--perturb-s202]  hvac_action checks heat_pump_on before the mode-off test
      [--perturb-s203]  climate.hvac_action / switch mode attribute read coordinator.mode
EXPECTED at 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (exact counts): printed per
  RESULT line; see verify-v2.md for the recorded values.
MACHINE: G2-V2 cloud container, 4 CPU (shared with 2 other seats), CPython 3.14.0rc2.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import logging  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402
from zoneinfo import ZoneInfo  # noqa: E402

_TMP = tempfile.mkdtemp(prefix="d8v2_")
os.environ["HPO_PLANDATA"] = os.path.join(_TMP, "plandata")
sys.path[:0] = ["tests", "tests/hastub", "custom_components"]
logging.disable(logging.CRITICAL)

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from replay import InProcessWorker  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from homeassistant.components.climate import HVACAction, HVACMode  # noqa: E402
from heatpump_optimizer import boost, climate, sensor, switch, const  # noqa: E402
from heatpump_optimizer import entity as ent_mod  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from golden import coordinator_scenarios  # noqa: E402
import profiles  # noqa: E402

TZ = ZoneInfo("Europe/Stockholm")
T0 = datetime(2026, 2, 10, 0, 0, tzinfo=TZ)
HP = "switch.hp_supply"
_WORKER = InProcessWorker()
cm._ensure_worker = lambda: _WORKER


def price_rows(start: datetime) -> list[dict]:
    day0 = start.replace(hour=0, minute=0)
    base = list(profiles.prices("winter_typical", day0.replace(tzinfo=None)))
    per_h = int(round(1 / profiles.DT))
    vals = [float(v) for v in base[::per_h]]
    vals = vals + [v * 1.05 for v in vals]
    return [{"total": round(v, 4), "starts_at": (day0 + timedelta(hours=h)).isoformat(),
             "level": "NORMAL"} for h, v in enumerate(vals)]


def build(config: dict, indoor: str | None = "21.2", outdoor: float = -6.0):
    hass = FakeHass()
    cfg = {**config, const.CONF_HEAT_PUMP_SWITCH_ENTITY: HP,
           const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.v2_out"}
    if indoor is not None:
        cfg[const.CONF_INDOOR_TEMP_ENTITY] = "sensor.v2_in"
    entry = FakeEntry(data=cfg)
    coord = cm.HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = coord
    hass.states.set(HP, FakeState("on"))

    async def fetch() -> None:
        coord._prices = price_rows(dt_util.now())
    coord._fetch_tibber_prices = fetch

    async def forecasts(call):
        now = dt_util.now()
        return {"weather.home": {"forecast": [
            {"datetime": (now + timedelta(hours=h)).isoformat(),
             "temperature": outdoor + 2.0 * ((h % 24) / 24.0), "wind_speed": 3.0,
             "precipitation": 0.0, "humidity": 80.0} for h in range(48)]}}
    hass.services.async_register("weather", "get_forecasts", forecasts)
    ents: list = []
    for mod in (sensor, climate, switch):
        added: list = []
        asyncio.run(mod.async_setup_entry(hass, entry, added.extend))
        ents.extend(added)
    for e in ents:
        e.hass = hass
    return hass, entry, coord, ents


def set_inputs(hass, now, indoor, outdoor):
    if indoor is not None:
        hass.states.set("sensor.v2_in", FakeState(str(indoor), last_updated=now, unit="°C"))
    hass.states.set("sensor.v2_out", FakeState(str(outdoor), last_updated=now, unit="°C"))


def cycle(hass, coord, now, indoor="21.2", outdoor=-6.0):
    dt_util.freeze(now)
    set_inputs(hass, now, indoor, outdoor)
    n0 = len(hass.services.calls)
    coord.data = asyncio.run(coord._async_update_data())
    coord.last_update_success = True
    sw = [c for c in hass.services.calls[n0:]
          if isinstance(c[2], dict) and c[2].get("entity_id") == HP]
    return sw[-1][1] if sw else None


def tkey(ents, key):
    return next(e for e in ents if getattr(e, "_attr_translation_key", None) == key)


def clim(ents):
    return next(e for e in ents if isinstance(e, climate.HeatPumpOptimizerClimate))


# ---------------------------------------------------------------- s1-02
def s1_02():
    cells = {k: v for k, v in coordinator_scenarios().items() if "dhw_tank_volume" in v}
    cells["coord_dhw_nowindows"] = {**cells["coord_dhw"]}
    cells["coord_dhw_nowindows"].pop("dhw_windows", None)
    mism = total = null_cycles = null_mism = 0
    per_cell = {}
    for name, cfg in cells.items():
        hass, entry, coord, ents = build(cfg)
        ent = tkey(ents, "dhw_heating_schedule")
        bad = 0
        for k in range(6):
            now = T0 + timedelta(hours=4 * k, minutes=5)
            cycle(hass, coord, now, "21.0", -8.0 + k)
            sched = coord.data.get("dhw_schedule") or []
            on = [s.get("dhw_power", 0) > 0.1 for s in sched]
            runs = sum(1 for i, x in enumerate(on) if x and (i == 0 or not on[i - 1]))
            lens, cur = [], 0
            for x in on + [False]:
                if x:
                    cur += 1
                elif cur:
                    lens.append(cur)
                    cur = 0
            val = ent.native_value
            n = int(str(val).split()[0]) if val and str(val)[0].isdigit() else 0
            total += 1
            if n != runs:
                mism += 1
                bad += 1
            if lens and max(lens) == 1:
                null_cycles += 1
                null_mism += n != runs
            print(f"  s1_02 {name} {now:%H:%M}: state={val!r} runs={runs} steps_on={sum(on)} run_lengths={lens}")
        per_cell[name] = bad
    dt_util.freeze(None)
    print(f"RESULT s1_02_runs_mismatch={mism} count (of {total} cycles)")
    print(f"RESULT s1_02_per_cell={per_cell}")
    print(f"RESULT s1_02_null_single_step_cycles={null_cycles} count, mismatched={null_mism}")


# ---------------------------------------------------------------- s1-03
def s1_03(pmins=(1.0, 0.2)):
    for pmin in pmins:
        bad = total = 0
        worst = 0.0
        per = {}
        for name, cfg in coordinator_scenarios().items():
            c = {**cfg, "heat_pump_min_power": pmin}
            hass, entry, coord, ents = build(c)
            rec = tkey(ents, "recommended_power")
            act = tkey(ents, "heat_pump_action")
            b = 0
            for k in range(24):
                now = T0 + timedelta(hours=k, minutes=5)
                call = cycle(hass, coord, now, f"{20.6 + 0.05 * (k % 6):.2f}", -6.0 + 0.3 * k)
                total += 1
                v = rec.native_value
                if call == "turn_off" and isinstance(v, (int, float)) and v > 0.05:
                    b += 1
                    worst = max(worst, v)
                    print(f"  s1_03 pmin={pmin} {name} {now:%H:%M}: rec={v} action={act.native_value} switch={call}")
            per[name] = b
            bad += b
        dt_util.freeze(None)
        tag = str(pmin).replace(".", "_")
        vals = list(per.values())
        print(f"RESULT s1_03_power_vs_switch_min{tag}={bad} count (of {total} cycles) worst={worst:.2f} kW")
        print(f"RESULT s1_03_min{tag}_per_cell={per} drop_max_cell={bad - max(vals)}")


# ---------------------------------------------------------------- s2-01
def s2_01():
    arms = {"no_indoor": None, "indoor_reading": "21.3", "indoor_unavailable": "unavailable"}
    for arm, ind in arms.items():
        unav = cells = cur_none = 0
        for name, cfg in coordinator_scenarios().items():
            if ind is None:
                hass, entry, coord, ents = build(cfg, indoor=None)
            else:
                hass, entry, coord, ents = build(cfg)
            cycle(hass, coord, T0 + timedelta(hours=6, minutes=5), ind, -6.0)
            c = clim(ents)
            cells += 1
            unav += (coord.last_update_success and bool(coord.data)) and not c.available
            cur_none += c.current_temperature is None
        dt_util.freeze(None)
        print(f"RESULT s2_01_unavailable_{arm}={unav} count (of {cells} cells); current_temperature None in {cur_none}")


# ---------------------------------------------------------------- s2-02
def s2_02():
    for mode in (const.MODE_OFF, const.MODE_AUTO):
        bad = arms = 0
        for name, cfg in coordinator_scenarios().items():
            channels = ["space"] + (["dhw"] if "dhw_tank_volume" in cfg else [])
            for ch in channels:
                hass, entry, coord, ents = build(cfg)
                coord._mode = mode
                now = T0 + timedelta(hours=10, minutes=5)
                dt_util.freeze(now)
                boost.held_for(coord).until.clear()
                boost.held_for(coord).set(ch, True, now)
                call = cycle(hass, coord, now, "21.0", -6.0)
                c = clim(ents)
                arms += 1
                if call == "turn_on" and c.hvac_action == HVACAction.OFF:
                    bad += 1
                print(f"  s2_02 mode={mode} {name} boost_{ch}: switch={call} hvac_mode={c.hvac_mode} hvac_action={c.hvac_action}")
                boost.held_for(coord).until.clear()
        dt_util.freeze(None)
        print(f"RESULT s2_02_off_while_on_mode_{mode}={bad} count (of {arms} arms)")


# ---------------------------------------------------------------- s2-03
def s2_03():
    split = writes = vs_actuator = 0
    solves = []
    real_run = cm.HeatPumpOptimizerCoordinator.async_run_optimization

    async def counted(self, *a, **k):
        solves.append(1)
        return await real_run(self, *a, **k)
    cm.HeatPumpOptimizerCoordinator.async_run_optimization = counted
    for name in ("coord_minimal", "coord_dhw"):
        cfg = coordinator_scenarios()[name]
        for which in ("climate", "switch"):
            hass, entry, coord, ents = build(cfg)
            coord._mode = const.MODE_BOOST  # a cycle that certainly heats
            now = T0 + timedelta(hours=10, minutes=5)
            call = cycle(hass, coord, now, "21.0", -6.0)
            c = clim(ents)
            sw = next(e for e in ents if isinstance(e, switch.OptimizerEnableSwitch))
            snaps = []

            def rec_write(e=None):
                snaps.append({"hvac_mode": c.hvac_mode, "hvac_action": c.hvac_action,
                              "is_on": sw.is_on,
                              "sw_mode_attr": (sw.extra_state_attributes or {}).get("mode")})
            tasks = []
            for e in (c, sw):
                e.async_write_ha_state = rec_write
                e._entry = entry
            entry.async_create_background_task = lambda h, coro, name=None: (tasks.append(coro), coro.close())
            t0 = time.perf_counter()
            if which == "climate":
                asyncio.run(c.async_set_hvac_mode(HVACMode.OFF))
            else:
                asyncio.run(sw.async_turn_off())
            s = snaps[0] if snaps else None
            writes += 1
            if s is None:
                print(f"  s2_03 {name} {which}: no immediate write")
                continue
            live_off = (s["hvac_mode"] == HVACMode.OFF) if which == "climate" else (s["is_on"] is False)
            payload_on = (s["hvac_action"] == HVACAction.HEATING) if which == "climate" else (s["sw_mode_attr"] != const.MODE_OFF)
            split += live_off and payload_on
            # V2 oracle: the supply switch's last commanded state at the write instant
            actuator_on = call == "turn_on"
            vs_actuator += (s["hvac_action"] == HVACAction.HEATING) != actuator_on
            print(f"  s2_03 {name} {which}: switch_before={call} write={s}")
            del solves[:]
            # how long the stale write stands on this box: one production cycle
            t1 = time.perf_counter()
            cycle(hass, coord, now + timedelta(seconds=30), "21.0", -6.0)
            print(f"  s2_03 {name} {which}: after refresh hvac_action={c.hvac_action} is_on={sw.is_on} "
                  f"mode_attr={(sw.extra_state_attributes or {}).get('mode')} refresh_wall={time.perf_counter() - t1:.2f}s "
                  f"solves_in_refresh={len(solves)} switch_after={hass.services.calls[-1][1] if hass.services.calls else None}")
        dt_util.freeze(None)
    cm.HeatPumpOptimizerCoordinator.async_run_optimization = real_run
    print(f"RESULT s2_03_split_writes={split} count (of {writes} writes)")
    print(f"RESULT s2_03_hvac_action_vs_actuator={vs_actuator} count (of {writes} writes)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="s1_02,s1_03,s2_01,s2_02,s2_03")
    ap.add_argument("--perturb-s103", action="store_true")
    ap.add_argument("--perturb-s201", action="store_true")
    ap.add_argument("--perturb-s202", action="store_true")
    ap.add_argument("--perturb-s203", action="store_true")
    a = ap.parse_args()
    if a.perturb_s103:
        real = ent_mod.commanded_power_kw
        sensor.commanded_power_kw = lambda act: (0.0 if act and act.get("heat_pump_on") is False
                                                 and act.get("power") is not None else real(act))
    Cl = climate.HeatPumpOptimizerClimate
    if a.perturb_s201:
        Cl.available = property(lambda self: super(Cl, self).available)
    if a.perturb_s202 or a.perturb_s203:
        def hvac_action(self):
            d = self.coordinator.data
            if not d:
                return None
            act = d.get("current_action", {})
            mode = self.coordinator.mode if a.perturb_s203 else d.get("mode", const.MODE_AUTO)
            if a.perturb_s202 and (act.get("heat_pump_on") or act.get("power_normalized", 0) > 0.1):
                return HVACAction.HEATING
            if mode == const.MODE_OFF:
                return HVACAction.OFF
            if act.get("power_normalized", 0) > 0.1 or act.get("heat_pump_on"):
                return HVACAction.HEATING
            return HVACAction.IDLE
        Cl.hvac_action = property(hvac_action)
    if a.perturb_s203:
        Sw = switch.OptimizerEnableSwitch
        orig = Sw.extra_state_attributes.fget

        def attrs(self):
            out = dict(orig(self) or {})
            if "mode" in out:
                out["mode"] = self.coordinator.mode
            return out
        Sw.extra_state_attributes = property(attrs)
    t0, th0 = time.process_time(), time.thread_time()
    for name in a.only.split(","):
        globals()[name.strip()]()
    cpu, thr = time.process_time() - t0, time.thread_time() - th0
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
