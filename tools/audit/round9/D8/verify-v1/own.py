#!/usr/bin/env python3
"""D8 round 9, verifier V1: independent re-measures of the nine D8 findings, no solve.

METRICS (one line each; every count keyed on the production property's return):
  s1_01_wrong_minutes   of 1440 minutes of 2026-01-15, minutes where coordinator
      _current_spot_price() differs from the entry whose [start, next start) covers now
      (15-min list, each quarter priced differently); null arms: hourly list, and a flat 15-min list
  s1_02_mismatch        synthetic DHW schedules (runs of k consecutive 15-min steps, k=1..4,
      2 runs each): DHWScheduleSensor leading integer != coordinator._plan_slots slot count
  s1_03_power_while_off of 10 space powers 0.05..0.50 kW at min_power 1.0 (on-threshold 0.5),
      published through optimizer.get_current_action (heat_pump_on_schedule absent) and
      _build_data_dict: steps where CurrentPowerSensor > 0.05 and HeatPumpActionSensor == 'off'
  s2_01_climate_unavailable  climate.available False after _build_data_dict with no indoor
      entity configured (arm A) vs indoor configured and read (arm B, control)
  s2_02_off_while_on    climate.hvac_action == OFF while current_action (after boost.overlay)
      has heat_pump_on True, per boost channel, at live+payload mode off; null at mode auto
  s2_03_split           after coord._mode is set to off with payload mode auto (the state the
      publish_then_refresh write sees): climate hvac_mode vs hvac_action off-ness, switch is_on
      vs attribute mode
  s3_*                  read translations/en.json, sv.json and the sensor classes directly
RUN:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D8/verify-v1/own.py
EXPECTED at 1936d5ca (evidence tree 6f51db2c), exact: s1_01 1425 (null hourly 0, flat15 0; --fix-price 0);
  s1_02 3 of 4; s1_03 9 of 10 (--gate-power 0); s2_01 no-indoor 0 / with-indoor 1; s2_02 2, null 0;
  s2_03 2; s3_sv_gap_name 'Sensorlucka i valutan'; s3_upper_enabled True, same_reading_key True.
MACHINE: G2-V1 cloud container, 4 CPU, CPython 3.14. Clock frozen, Europe/Stockholm.
PERTURB: --fix-price (s1_01 -> 0), --gate-power (s1_03 -> 0) in memory.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")

import asyncio
import json
import logging
import sys
import time
import types
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

sys.path[:0] = ["tests", "tests/hastub", "custom_components"]
logging.disable(logging.CRITICAL)

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from homeassistant.components.climate import HVACAction  # noqa: E402
from heatpump_optimizer import boost, climate, sensor, switch  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from heatpump_optimizer import entity as ent_mod  # noqa: E402
from heatpump_optimizer.const import MODE_AUTO, MODE_OFF  # noqa: E402

TZ = ZoneInfo("Europe/Stockholm")
DAY = datetime(2026, 1, 15, 0, 0, tzinfo=TZ)
BASE = {"tibber_token": "x", "weather_entity": "weather.home", "target_temperature": 21.0,
        "min_temperature": 17.0, "max_temperature": 23.0,
        "outdoor_temp_entity": "sensor.outdoor"}
C = "custom_components/heatpump_optimizer"


def mk(cfg):
    hass = FakeHass()
    entry = FakeEntry(data=cfg)
    coord = cm.HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = coord
    return hass, entry, coord


def setup(mod, hass, entry):
    out: list = []
    asyncio.run(mod.async_setup_entry(hass, entry, out.extend))
    return out


def s1_01(arm: str) -> int:
    """arm: 'quarter' (15-min, quarters differ), 'hourly' (null), 'flat15' (null)."""
    if "--fix-price" in sys.argv:
        def fixed(self):
            now = dt_util.now()
            ent = [(datetime.fromisoformat(p["starts_at"]), p) for p in self._prices]
            for i, (s, p) in enumerate(ent):
                e = ent[i + 1][0] if i + 1 < len(ent) else s + timedelta(hours=1)
                if s <= now < e:
                    return cm._raw_value(p) or 0.0
            return 0.0
        cm.HeatPumpOptimizerCoordinator._current_spot_price = fixed
    _, _, coord = mk(BASE)
    if arm == "hourly":
        coord._prices = [{"total": round(1.0 + 0.01 * h, 4),
                          "starts_at": (DAY + timedelta(hours=h)).isoformat()} for h in range(48)]
    else:
        coord._prices = [{"total": round(1.0 + (0 if arm == "flat15" else 0.01 * (q // 4) + 0.07 * (q % 4)), 4),
                          "starts_at": (DAY + timedelta(minutes=15 * q)).isoformat()}
                         for q in range(192)]
    step = 60 if arm == "hourly" else 15
    wrong = 0
    for m in range(1440):
        now = DAY + timedelta(minutes=m, seconds=30)
        dt_util.freeze(now)
        want = coord._prices[m // step]["total"]
        if abs(coord._current_spot_price() - want) > 1e-9:
            wrong += 1
    dt_util.freeze(None)
    return wrong


def s1_02() -> tuple[int, int]:
    hass, entry, coord = mk({**BASE, "dhw_tank_volume": 200.0})
    ents = setup(sensor, hass, entry)
    ent = next(e for e in ents if e._attr_translation_key == "dhw_heating_schedule")
    bad = total = 0
    for k in (1, 2, 3, 4):
        powers = [0.0] * 96
        for start in (8, 40):
            for j in range(k):
                powers[start + j] = 3.0
        ts = [DAY + timedelta(minutes=15 * i) for i in range(96)]
        sched = [{"time": t.isoformat(), "dhw_power": p} for t, p in zip(ts, powers)]
        coord.data = {"dhw_schedule": sched}
        pub = int(str(ent.native_value).split()[0])
        slots = len(cm.HeatPumpOptimizerCoordinator._plan_slots(ts, powers, [1.0] * 96, 0.25))
        total += 1
        bad += pub != slots
        print(f"  s1_02 run_len={k}: schedule_sensor={pub} plan_slots={slots}")
    return bad, total


class _Res(types.SimpleNamespace):
    """A two-step result; any field get_current_action reads beyond these is None."""

    def __getattr__(self, name):
        return None


def s1_03() -> tuple[int, float]:
    if "--gate-power" in sys.argv:
        real = ent_mod.commanded_power_kw
        sensor.commanded_power_kw = lambda a: (0.0 if a and a.get("heat_pump_on") is False
                                               and a.get("power") is not None else real(a))
    hass, entry, coord = mk({**BASE, "indoor_temp_entity": "sensor.indoor",
                             "heat_pump_min_power": 1.0})
    ents = {e._attr_translation_key: e for e in setup(sensor, hass, entry)}
    bad, worst = 0, 0.0
    for i in range(1, 11):
        p = round(0.05 * i, 2)
        res = _Res(timestamps=[DAY, DAY + timedelta(minutes=15)],
                                    power_schedule=[p, p], optimal_setpoints=[21.0, 21.0],
                                    prices=[1.0, 1.0], displace_schedule=None, predictive_info={},
                                    heat_pump_on_schedule=None, dhw_power_schedule=None)
        try:
            coord._current_action = coord._optimizer.get_current_action(res, DAY)
        except Exception as err:  # the result shape may need more fields
            print(f"  s1_03 get_current_action raised {type(err).__name__}: {err}")
            return -1, 0.0
        dt_util.freeze(DAY)
        coord.data = coord._build_data_dict()
        rec, st = ents["recommended_power"].native_value, ents["heat_pump_action"].native_value
        if st == "off" and isinstance(rec, (int, float)) and rec > 0.05:
            bad += 1
            worst = max(worst, rec)
    dt_util.freeze(None)
    return bad, worst


def s2_01(with_indoor: bool) -> bool:
    cfg = {**BASE, **({"indoor_temp_entity": "sensor.indoor"} if with_indoor else {})}
    hass, entry, coord = mk(cfg)
    dt_util.freeze(DAY)
    for eid, v in (("sensor.indoor", 21.3), ("sensor.outdoor", -4.0)):
        hass.states.set(eid, FakeState(str(v), last_updated=DAY, unit="°C"))
    asyncio.run(coord._update_current_state())
    coord.data = coord._build_data_dict()
    coord.last_update_success = True
    cl = setup(climate, hass, entry)[0]
    dt_util.freeze(None)
    return bool(cl.available)


def s2_02() -> tuple[int, int]:
    hass, entry, coord = mk({**BASE, "indoor_temp_entity": "sensor.indoor",
                             "dhw_tank_volume": 200.0})
    cl = setup(climate, hass, entry)[0]
    off_arms = null_arms = 0
    for mode, arm in ((MODE_OFF, "off"), (MODE_AUTO, "auto")):
        for ch in (boost.CHANNEL_SPACE, boost.CHANNEL_DHW):
            coord._mode = mode
            action = {"power": 0.0, "mode": "off", "power_normalized": 0.0, "heat_pump_on": False}
            held = types.SimpleNamespace(until={ch: DAY + timedelta(hours=1)})
            boost.overlay(action, held, max_power=5.0, max_temp=23.0, ecl_max=0.0)
            coord._current_action = action
            coord.data = coord._build_data_dict()
            coord.data["mode"] = mode
            ha = cl.hvac_action
            hit = action.get("heat_pump_on") and ha in (HVACAction.OFF, HVACAction.IDLE)
            print(f"  s2_02 mode={arm} channel={ch}: heat_pump_on={action['heat_pump_on']} hvac_action={ha}")
            if arm == "off":
                off_arms += bool(hit)
            else:
                null_arms += bool(hit)
    return off_arms, null_arms


def s2_03() -> int:
    hass, entry, coord = mk({**BASE, "indoor_temp_entity": "sensor.indoor"})
    cl = setup(climate, hass, entry)[0]
    sw = next(e for e in setup(switch, hass, entry) if isinstance(e, switch.OptimizerEnableSwitch))
    coord._mode = MODE_AUTO
    coord._current_action = {"power": 3.0, "mode": "normal", "power_normalized": 0.6,
                             "heat_pump_on": True}
    coord.data = coord._build_data_dict()
    coord.data["mode"] = MODE_AUTO
    splits = 0
    for live in (MODE_OFF,):
        coord._mode = live  # what async_set_mode(refresh=False) leaves before the solve
        off_live = str(cl.hvac_mode) in ("off", "HVACMode.OFF")
        off_payload = cl.hvac_action == HVACAction.OFF
        splits += off_live != off_payload
        splits += (sw.is_on) != (sw.extra_state_attributes.get("mode") != MODE_OFF)
        print(f"  s2_03 live=off: hvac_mode={cl.hvac_mode} hvac_action={cl.hvac_action} "
              f"switch is_on={sw.is_on} attr mode={sw.extra_state_attributes.get('mode')}")
    return splits


def s3() -> dict:
    en = json.load(open(f"{C}/translations/en.json"))["entity"]
    sv = json.load(open(f"{C}/translations/sv.json"))["entity"]
    out = {}
    names = []
    for plat, d in en.items():
        for k, v in d.items():
            if "name" in v:
                names.append((plat, k, v["name"], sv.get(plat, {}).get(k, {}).get("name")))
    out["sv_gap_name"] = sv["sensor"]["sensor_gap_advisor"]["name"]
    out["en_gap_name"] = en["sensor"]["sensor_gap_advisor"]["name"]
    for lang, idx in (("en", 2), ("sv", 3)):
        srt = sorted((n[idx] or "").casefold() for n in names)
        pos = {n[1]: srt.index((n[idx] or "").casefold()) for n in names}
        out[f"acc_gap_{lang}"] = abs(pos["diagnose_interval" if "diagnose_interval" in pos else
                                         next(k for k in pos if "diagnos" in k)]
                                     - pos["prediction_accuracy"]) if "prediction_accuracy" in pos else None
    out["names"] = len(names)
    up = sensor.UpperFloorTempSensor
    ind = sensor.IndoorTempSensor
    out["upper_enabled"] = getattr(up, "_attr_entity_registry_enabled_default", True)
    out["indoor_enabled"] = getattr(ind, "_attr_entity_registry_enabled_default", True)
    out["same_reading_key"] = getattr(up, "_reading_key", None) == getattr(ind, "_reading_key", None)
    return out


def main() -> int:
    t_cpu, t_thr = time.process_time(), time.thread_time()
    print(f"RESULT s1_01_wrong_minutes={s1_01('quarter')} count (of 1440)")
    print(f"RESULT s1_01_null_hourly={s1_01('hourly')} count (of 1440)")
    print(f"RESULT s1_01_null_flat15={s1_01('flat15')} count (of 1440)")
    b, n = s1_02()
    print(f"RESULT s1_02_mismatch={b} count (of {n} schedules)")
    b, w = s1_03()
    print(f"RESULT s1_03_power_while_off={b} count (of 10 powers) worst={w} kW")
    print(f"RESULT s2_01_available_no_indoor={int(s2_01(False))} bool")
    print(f"RESULT s2_01_available_with_indoor={int(s2_01(True))} bool")
    o, z = s2_02()
    print(f"RESULT s2_02_off_while_on={o} count (of 2 channels, mode off)")
    print(f"RESULT s2_02_null_mode_auto={z} count (of 2 channels)")
    print(f"RESULT s2_03_split={s2_03()} count (of 2 entity writes)")
    r = s3()
    for k, v in r.items():
        print(f"RESULT s3_{k}={v}")
    cpu, thr = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=" + [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
