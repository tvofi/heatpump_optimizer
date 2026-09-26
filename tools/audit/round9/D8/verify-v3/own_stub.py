#!/usr/bin/env python3
"""D8 verifier V3 (round 9): own measurements for D8-s1-02, D8-s1-03, D8-s2-03 (refresh window),
D8-s3-01 (real device-page grouping), D8-s3-02, D8-s3-03.

METRIC (one line each):
  s1_02_cells_differ       of the DHW-enabled golden topologies after two real cycles, cells
                           where the integer DHW Heating Schedule publishes differs from DHW
                           Heating Plan's slot_count; s1_02_worst_ratio = worst integer/slot_count.
  s1_03_entity_steps       steps (5 topologies x horizon, heat_pump_min_power 1.0 = the default)
                           where production get_current_action says heat_pump_on False and
                           entity.commanded_power_kw(action) > 0.05 kW.
  s1_03_internal_steps     same steps, where coordinator._commanded_power() (settlement,
                           external-heat, COP-fold, frequency seams) > 0.05 kW -- the sibling
                           seam the finding's seam_rule does not grep.
  s2_03_refresh_cpu_<mode> process CPU of one production _async_update_data after
                           async_set_mode(<mode>) on coord_all_features (fetchers injected):
                           the stale-payload window's compute part, off vs auto. Measured: the
                           auto call ran no solve here (8 ms), so only the off number is
                           informative; off has no solve by construction (MODE_OFF branch).
  s3_01_device_page_split  families (the finder's production-defined sets) whose members,
                           placed as the HA frontend 20260128.6 device page places them (bucket
                           by entity_category, else sensor-domain -> Sensors, else Controls;
                           name-sorted within a bucket), occupy >1 run inside a bucket they share;
                           a family whose members sit in different buckets counts as
                           s3_01_cross_bucket instead (a split no name can mend).
  s3_02_currency_asym      entity names whose sv string carries a currency word (valuta/kronor)
                           while the en string carries none (currency/SEK), or vice versa.
  s3_03_dup_enabled        ordered check: UpperFloorTempSensor and IndoorTempSensor both
                           enabled_default and equal native_value in each topology.
COMMAND (repository root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D8/verify-v3/own_stub.py
EXPECTED at baseline 1936d5ca (exact counts): s1_02_cells_differ=2 of 2 (ratio 1.8),
  s1_03_entity_steps=23 and s1_03_internal_steps=23 of 480 (worst 0.46 kW),
  s3_03_dup_enabled=5 of 5, s3_01_device_page_split=2 and s3_01_cross_bucket=2,
  s3_02_currency_asym=1. CPU numbers are provisional (quote load1, thread_factor).
MACHINE: G2-V3 cloud container, 4 CPU, CPython 3.14.0rc2.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import json
import re
import sys
import tempfile
import time
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, "tests/hastub")
_TMP = tempfile.mkdtemp(prefix="d8v3_")
os.environ["HPO_PLANDATA"] = os.path.join(_TMP, "plandata")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const, sensor, button, binary_sensor, climate, switch  # noqa: E402
from heatpump_optimizer import datetime as datetime_platform  # noqa: E402
from heatpump_optimizer.entity import commanded_power_kw, DHWEntityMixin  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from golden import START, coordinator_scenarios  # noqa: E402

CELLS = ["coord_minimal", "coord_dhw", "coord_two_zone", "coord_grid_fee", "coord_all_features"]
PLATFORMS = {"sensor": sensor, "binary_sensor": binary_sensor, "button": button,
             "climate": climate, "switch": switch, "datetime": datetime_platform}


async def _noop(*_a, **_k):
    return None


def build(config, extra=None):
    hass = FakeHass()
    cfg = {**config, const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
           const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor", **(extra or {})}
    hass.states.set("sensor.indoor", FakeState("21.2"))
    hass.states.set("sensor.outdoor", FakeState("-4.0"))
    entry = FakeEntry(data=cfg)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    for name in ("_fetch_tibber_prices", "_fetch_weather_forecast",
                 "_fetch_solar_forecast", "_async_learn_price_shape"):
        setattr(coord, name, _noop)
    entry.runtime_data = coord
    return hass, entry, coord


def inject(coord, shift):
    coord._prices = [{"total": round(0.4 + shift + 0.9 * ((h * 7) % 12) / 12.0, 4),
                      "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
                     for h in range(48)]
    coord._weather_forecast = [{"datetime": (START + timedelta(hours=h)).isoformat(),
                                "temperature": -6.0 + 4.0 * (h % 24) / 24.0 - 3 * shift,
                                "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0}
                               for h in range(48)]
    coord._solar_radiation_forecast = [max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)]


async def cycle(coord, shift):
    inject(coord, shift)
    coord.data = await coord._async_update_data()
    coord.last_update_success = True


def collect(hass, entry):
    out = []
    for plat, module in PLATFORMS.items():
        added = []
        asyncio.run(module.async_setup_entry(hass, entry, added.extend))
        out.extend((plat, e) for e in added)
    return out


def main() -> int:
    t0p, t0t = time.process_time(), time.thread_time()
    scen = coordinator_scenarios()
    s1_02_cells = s1_02_differ = 0
    worst_ratio = 0.0
    s1_03_entity = s1_03_internal = s1_03_steps = 0
    worst_kw = 0.0
    dup_ok = 0
    dt_util.freeze(START + timedelta(hours=3, minutes=5))
    try:
        for cell in CELLS:
            hass, entry, coord = build(scen[cell], {const.CONF_HEAT_PUMP_MIN_POWER: 1.0})
            asyncio.run(cycle(coord, 0.0))
            asyncio.run(cycle(coord, 0.3))
            ents = collect(hass, entry)
            by_cls = {type(e).__name__: e for _, e in ents}
            # ---- s1-02
            sched, plan = by_cls.get("DHWScheduleSensor"), by_cls.get("DHWHeatingPlanSensor")
            if sched is not None and coord.data.get("dhw_enabled") and sched.available and plan.available:
                s1_02_cells += 1
                n_sched = int(str(sched.native_value).split()[0]) if str(sched.native_value)[0].isdigit() else 0
                n_slots = plan.extra_state_attributes.get("slot_count")
                print(f"INFO s1-02 {cell}: schedule='{sched.native_value}' slot_count={n_slots}")
                if n_sched != n_slots:
                    s1_02_differ += 1
                    if n_slots:
                        worst_ratio = max(worst_ratio, n_sched / n_slots)
            # ---- s1-03
            result = coord._optimization_result
            _st, opt = coord._solve_snapshot()
            saved = coord._current_action
            for ts in result.timestamps:
                action = opt.get_current_action(result, ts)
                s1_03_steps += 1
                if action.get("heat_pump_on"):
                    continue
                kw = commanded_power_kw(action) or 0.0
                if kw > 0.05:
                    s1_03_entity += 1
                    worst_kw = max(worst_kw, kw)
                coord._current_action = action
                if coord._commanded_power() > 0.05:
                    s1_03_internal += 1
            coord._current_action = saved
            # ---- s3-03
            up, ind = by_cls["UpperFloorTempSensor"], by_cls["IndoorTempSensor"]
            if (getattr(up, "entity_registry_enabled_default", getattr(up, "_attr_entity_registry_enabled_default", True)) and getattr(ind, "entity_registry_enabled_default", getattr(ind, "_attr_entity_registry_enabled_default", True))
                    and up.native_value == ind.native_value and up.native_value is not None):
                dup_ok += 1
    finally:
        dt_util.freeze(None)
    print(f"RESULT s1_02_cells_differ={s1_02_differ} count (of {s1_02_cells} DHW cells)")
    print(f"RESULT s1_02_worst_ratio={worst_ratio:.1f} ratio (published periods / slots)")
    print(f"RESULT s1_03_entity_steps={s1_03_entity} count (of {s1_03_steps} steps)")
    print(f"RESULT s1_03_internal_steps={s1_03_internal} count (of {s1_03_steps} steps)")
    print(f"RESULT s1_03_worst_kw={worst_kw:.2f} kW")
    print(f"RESULT s3_03_dup_enabled={dup_ok} count (of {len(CELLS)} topologies)")

    # ---- s2-03: the stale window's compute part, off vs auto
    dt_util.freeze(START + timedelta(hours=3, minutes=5))
    try:
        hass, entry, coord = build(scen["coord_all_features"])
        asyncio.run(cycle(coord, 0.0))
        for mode in (const.MODE_OFF, const.MODE_AUTO):
            asyncio.run(coord.async_set_mode(mode, refresh=False))
            inject(coord, 0.1)
            c0 = time.process_time()
            coord.data = asyncio.run(coord._async_update_data())
            print(f"RESULT s2_03_refresh_cpu_{mode}={time.process_time() - c0:.3f} s (x86 container, not a Pi)")
    finally:
        dt_util.freeze(None)

    # ---- s3-01 real device-page grouping; s3-02 currency asymmetry
    root = "custom_components/heatpump_optimizer"
    strings = {lang: json.load(open(f"{root}/translations/{lang}.json"))["entity"] for lang in ("en", "sv")}
    dt_util.freeze(START)
    try:
        hass, entry, coord = build(scen["coord_all_features"])
        asyncio.run(cycle(coord, 0.0))
        ents = collect(hass, entry)
    finally:
        dt_util.freeze(None)
    SENSORISH = {"sensor", "binary_sensor", "calendar", "camera", "device_tracker", "image", "weather"}

    def bucket(plat, e):
        cat = getattr(e, "entity_category", None)
        if cat is not None:
            return str(getattr(cat, "value", cat))
        return "sensor" if plat in SENSORISH else "control"

    fams = {
        "accuracy": lambda p, e: isinstance(e, (sensor.PredictionAccuracySensor, button.DiagnoseIntervalButton)),
        "energy_meters": lambda p, e: isinstance(e, sensor._AccumulatingSensor)
        and not isinstance(e, DHWEntityMixin),
    }
    split = cross = 0
    for lang in ("en", "sv"):
        rows = []
        for p, e in ents:
            key = getattr(e, "_attr_translation_key", None)
            name = (strings[lang].get(p, {}).get(key) or {}).get("name") or ""
            rows.append((bucket(p, e), name, p, e))
        for fam, pred in fams.items():
            members = [r for r in rows if pred(r[2], r[3])]
            buckets = {r[0] for r in members}
            if len(buckets) > 1:
                cross += 1
                print(f"INFO s3-01 {lang} {fam}: members in buckets {sorted(buckets)} -- never adjacent on the device page")
                continue
            b = buckets.pop()
            order = sorted([r for r in rows if r[0] == b], key=lambda r: r[1].casefold())
            pos = sorted(i for i, r in enumerate(order) if pred(r[2], r[3]))
            runs = 1 + sum(1 for a, c in zip(pos, pos[1:]) if c != a + 1)
            print(f"INFO s3-01 {lang} {fam}: bucket {b}, {runs} runs; order "
                  f"{[order[i][1] for i in range(pos[0], pos[-1] + 1)]}")
            split += runs > 1
    print(f"RESULT s3_01_device_page_split={split} count (families x 2 languages)")
    print(f"RESULT s3_01_cross_bucket={cross} count (families x 2 languages)")
    asym = 0
    for plat, keys in strings["en"].items():
        for key, v in keys.items():
            en = (v or {}).get("name") or ""
            sv = ((strings["sv"].get(plat) or {}).get(key) or {}).get("name") or ""
            en_cur = bool(re.search(r"currency|\bSEK\b|\bkr\b", en, re.I))
            sv_cur = bool(re.search(r"valuta|kronor|\bkr\b|\bSEK\b", sv, re.I))
            if en_cur != sv_cur:
                asym += 1
                print(f"INFO s3-02 {plat}.{key}: en='{en}' sv='{sv}'")
    print(f"RESULT s3_02_currency_asym={asym} count")

    pt, tt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={pt / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    with open("/proc/vmstat") as f:
        sw = next((int(l.split()[1]) for l in f if l.startswith("pswpin")), 0)
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
