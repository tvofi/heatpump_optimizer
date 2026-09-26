#!/usr/bin/env python3
"""D8 round 9, verifier V2 (independent) for D8-s3-01, D8-s3-02, D8-s3-03.

Entities: every entity of the six platforms through the real async_setup_entry
on a coordinator built as HeatPumpOptimizerCoordinator(FakeHass, FakeEntry(cfg))
with one _update_current_state and _build_data_dict (no solve needed for names).
Names: translation_key resolved through translations/<lang>.json, as the
frontend resolves it; sort = str.casefold (en) / Swedish collation approximated
by casefold with a-z < å < ä < ö.

METRICS
  s3_01_global_runs_<fam>_<lang>   contiguous runs of family members in the whole
      roster sorted by name (families by PRODUCTION class: accuracy =
      PredictionAccuracySensor + DiagnoseIntervalButton; meters = every
      _AccumulatingSensor subclass instance)
  s3_01_section_runs_<fam>_<lang>  the same, but within the device-page section
      each member is listed in (HA device page: Controls = non-sensor domains
      with entity_category None; Sensors = sensor/binary_sensor with category
      None; Configuration; Diagnostic), summed over sections, only
      enabled-by-default entities (the page hides disabled ones)
  s3_02_sv_orphan_qualifier        entities whose sv name contains 'valuta'
      while the en name carries no currency/cost/price/SEK token; plus
      s3_02_sv_missing_role: en name ends in 'Advisor' and sv carries no 'råd'
  s3_03_same_source_enabled_pairs  unordered pairs of enabled-by-default sensors
      with the same production _reading_key AND equal native_value over 3
      input cycles in 4 configs (single-zone, two-zone with lower-floor
      thermometer, DHW, all-features) while the value moves between cycles
RUN:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D8/verify-v2/v2_names.py [--perturb-s301] [--perturb-s303]
      --perturb-s301: DiagnoseIntervalButton en name 'Prediction Accuracy: Diagnose Last Interval'
      --perturb-s303: UpperFloorTempSensor._attr_entity_registry_enabled_default = False
EXPECTED at 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (exact counts): see verify-v2.md.
MACHINE: G2-V2 cloud container, 4 CPU, CPython 3.14.0rc2.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")

import asyncio  # noqa: E402
import json  # noqa: E402
import logging  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402
from pathlib import Path  # noqa: E402
from zoneinfo import ZoneInfo  # noqa: E402

sys.path[:0] = ["tests", "tests/hastub", "custom_components"]
logging.disable(logging.CRITICAL)

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import binary_sensor, button, climate, sensor, switch, const  # noqa: E402
from heatpump_optimizer import datetime as dtp  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from golden import coordinator_scenarios  # noqa: E402

ROOT = Path("custom_components/heatpump_optimizer")
TR = {l: json.loads((ROOT / f"translations/{l}.json").read_text())["entity"] for l in ("en", "sv")}
PLAT = {"sensor": sensor, "binary_sensor": binary_sensor, "button": button,
        "climate": climate, "switch": switch, "datetime": dtp}
TZ = ZoneInfo("Europe/Stockholm")
T0 = datetime(2026, 2, 10, 7, 0, tzinfo=TZ)
SV_ORDER = {"å": "{", "ä": "|", "ö": "}"}


def skey(name: str, lang: str) -> str:
    s = name.casefold()
    if lang == "sv":
        s = "".join(SV_ORDER.get(ch, ch) for ch in s)
    return s


def build(cfg, states):
    hass = FakeHass()
    for k, v in states.items():
        hass.states.set(k, FakeState(str(v), last_updated=dt_util.now(), unit="°C"))
    entry = FakeEntry(data=cfg)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = coord
    asyncio.run(coord._update_current_state())
    coord.data = coord._build_data_dict()
    out = []
    for p, mod in PLAT.items():
        added: list = []
        asyncio.run(mod.async_setup_entry(hass, entry, added.extend))
        out += [(p, e) for e in added]
    return hass, coord, out


def name(p, e, lang):
    key = getattr(e, "_attr_translation_key", None) or getattr(e, "translation_key", None)
    n = ((TR[lang].get(p) or {}).get(key) or {}).get("name")
    return n if n else f"<{p}:{key}>"


def enabled(e):
    v = getattr(e, "entity_registry_enabled_default", None)
    if isinstance(v, bool):
        return v
    return getattr(e, "_attr_entity_registry_enabled_default", True)


def section(p, e):
    cat = getattr(e, "_attr_entity_category", None) or getattr(e, "entity_category", None)
    if cat:
        return str(cat)
    return "sensors" if p in ("sensor", "binary_sensor") else "controls"


def runs(ordered, member):
    r, prev = 0, False
    for x in ordered:
        m = member(x)
        if m and not prev:
            r += 1
        prev = m
    return r


def s3_01(perturb):
    if perturb:
        TR["en"]["button"]["diagnose_last_interval"]["name"] = "Prediction Accuracy: Diagnose Last Interval"
    cfg = {**coordinator_scenarios()["coord_all_features"],
           const.CONF_INDOOR_TEMP_ENTITY: "sensor.i", const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.o"}
    dt_util.freeze(T0)
    _, _, ents = build(cfg, {"sensor.i": 21.0, "sensor.o": -3.0})
    fams = {
        "accuracy": lambda pe: isinstance(pe[1], (sensor.PredictionAccuracySensor, button.DiagnoseIntervalButton)),
        "meters": lambda pe: isinstance(pe[1], sensor._AccumulatingSensor),
    }
    for lang in ("en", "sv"):
        glob = sorted(ents, key=lambda pe: skey(name(*pe, lang), lang))
        for f, m in fams.items():
            members = [name(*pe, lang) for pe in glob if m(pe)]
            print(f"  {lang} {f}: {members} sections={[section(*pe) for pe in glob if m(pe)]} "
                  f"enabled={[enabled(pe[1]) for pe in glob if m(pe)]}")
            print(f"RESULT s3_01_global_runs_{f}_{lang}={runs(glob, m)} count")
            vis = [pe for pe in glob if enabled(pe[1])]
            secs = {}
            for pe in vis:
                secs.setdefault(section(*pe), []).append(pe)
            tot = sum(runs(v, m) for v in secs.values())
            nsec = sum(1 for v in secs.values() if any(m(pe) for pe in v))
            print(f"RESULT s3_01_section_runs_{f}_{lang}={tot} count over {nsec} section(s)")
    dt_util.freeze(None)


def s3_02():
    orphan = missing = checked = 0
    for p, keys in TR["en"].items():
        for k, v in keys.items():
            en = (v or {}).get("name")
            sv = ((TR["sv"].get(p) or {}).get(k) or {}).get("name")
            if not en or not sv:
                continue
            checked += 1
            enl, svl = en.lower(), sv.lower()
            if "valuta" in svl and not any(t in enl for t in ("currency", "cost", "price", "sek", "savings", "money")):
                orphan += 1
                print(f"  orphan qualifier {p}.{k}: en={en!r} sv={sv!r}")
            if enl.endswith("advisor") and "råd" not in svl:
                missing += 1
                print(f"  missing role {p}.{k}: en={en!r} sv={sv!r}")
    print(f"RESULT s3_02_names_checked={checked} count")
    print(f"RESULT s3_02_sv_orphan_qualifier={orphan} count")
    print(f"RESULT s3_02_sv_missing_role={missing} count")


def s3_03(perturb):
    if perturb:
        sensor.UpperFloorTempSensor._attr_entity_registry_enabled_default = False
    base = coordinator_scenarios()
    io = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.i", const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.o"}
    cfgs = {
        "single_zone": {**base["coord_minimal"], **io},
        "two_zone_lower_probe": {**base["coord_two_zone"], **io,
                                 const.CONF_LOWER_FLOOR_TEMP_ENTITY: "sensor.l"},
        "dhw": {**base["coord_dhw"], **io},
        "all_features": {**base["coord_all_features"], **io},
    }
    pair_hits: dict[tuple, int] = {}
    for cname, cfg in cfgs.items():
        series: dict[str, list] = {}
        meta = {}
        for k in range(3):
            dt_util.freeze(T0 + timedelta(minutes=10 * k))
            _, _, ents = build(cfg, {"sensor.i": 20.4 + 0.3 * k, "sensor.o": -3.0 - k, "sensor.l": 19.1 + 0.2 * k})
            for p, e in ents:
                if p != "sensor" or not enabled(e):
                    continue
                rk = getattr(e, "_reading_key", None)
                if rk is None:
                    continue
                series.setdefault(e.entity_id, []).append(e.native_value)
                meta[e.entity_id] = rk
        ids = sorted(series)
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                va, vb = series[a], series[b]
                if (meta[a] == meta[b] and va == vb and len(set(map(str, va))) > 1
                        and all(isinstance(x, (int, float)) for x in va)):
                    pair_hits[(a, b)] = pair_hits.get((a, b), 0) + 1
                    print(f"  {cname}: {a} == {b} key={meta[a]} values={va}")
        dt_util.freeze(None)
    full = sum(1 for v in pair_hits.values() if v == len(cfgs))
    print(f"RESULT s3_03_same_source_enabled_pairs={full} count (pairs equal in all {len(cfgs)} configs)")


def main() -> int:
    t0, th0 = time.process_time(), time.thread_time()
    s3_01("--perturb-s301" in sys.argv)
    s3_02()
    s3_03("--perturb-s303" in sys.argv)
    cpu, thr = time.process_time() - t0, time.thread_time() - th0
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
