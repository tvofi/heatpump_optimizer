"""D8.M3 ordering and naming over the CONSTRUCTED entity set.

Metric: per coordinator scenario (tests/golden.py:coordinator_scenarios), the
entities every platform's real async_setup_entry adds; a declared family
(const.ENTITY_FAMILY_OVERRIDES, else the translation key's lead token) of >=2
constructed members is SPLIT when its members' display names (translations
en/sv, keyed by entity._attr_translation_key) do not form one contiguous run
in the name sort. Count key: the translation_key/name the constructed entity
delivers. Also: entity_id per-platform sort, untranslated keys, duplicate names.
Command: PYTHONPATH=tests/hastub:tests python3 dev/audit/rounds/round10/D8/s2/order.py [--all|--enabled] [--control]
Expected: see REPORT.md, exact (counts). Baseline 17f1c55fad1b, macOS arm64.
"""
import os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, json, asyncio, time
from pathlib import Path
from datetime import timedelta
def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path[:0] = [str(ROOT/"tests/hastub"), str(ROOT/"tests"), str(ROOT/"custom_components")]
t0p, t0t = time.process_time(), time.thread_time()
import golden
from harness import FakeEntry, FakeHass
from homeassistant.util import dt as dt_util
from heatpump_optimizer import const
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator, _with_sensor_advisor
import importlib

TR = ROOT/"custom_components/heatpump_optimizer/translations"
EN = json.loads((TR/"en.json").read_text())["entity"]
SV = json.loads((TR/"sv.json").read_text())["entity"]
SVT = str.maketrans({"å": "z\u0001", "ä": "z\u0002", "ö": "z\u0003"})
COLL = {"en": lambda n: n.casefold(), "sv": lambda n: n.casefold().translate(SVT)}
MODE = "enabled" if "--enabled" in sys.argv else "all"

def build(config):
    hass = FakeHass(); entry = FakeEntry(data=config)
    c = HeatPumpOptimizerCoordinator(hass, entry)
    S = golden.START
    c._prices = [{"total": round(0.6+0.5*(h%12)/12,4), "starts_at": (S+timedelta(hours=h)).isoformat(), "level": "NORMAL"} for h in range(48)]
    c._weather_forecast = [{"datetime": (S+timedelta(hours=h)).isoformat(), "temperature": -5+3*(h%24)/24, "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0} for h in range(48)]
    c._solar_radiation_forecast = [max(0.0, 200*(1-abs(12-(h%24))/12)) for h in range(48)]
    c._forecast_arrays()
    c.data = asyncio.run(_with_sensor_advisor(c, dict(c._build_data_dict())))
    entry.runtime_data = c
    out = []
    for plat in const.PLATFORMS:
        mod = importlib.import_module(f"heatpump_optimizer.{plat}")
        added = []
        def add(es, *a, **k):
            for e in es: e.hass = hass
            added.extend(es)
        asyncio.run(mod.async_setup_entry(hass, entry, add))
        for e in added:
            en_ = getattr(type(e), "entity_registry_enabled_default", None)
            enabled = e.entity_registry_enabled_default if isinstance(en_, property) else getattr(e, "_attr_entity_registry_enabled_default", True)
            out.append((str(plat), getattr(e, "_attr_translation_key", None), e.entity_id, bool(enabled)))
    return out

def runs(order, members):
    pos = [i for i, r in enumerate(order) if r in members]
    return 0 if len(pos) < 2 else 1 + sum(1 for a, b in zip(pos, pos[1:]) if b != a+1)

ov = dict(const.ENTITY_FAMILY_OVERRIDES)
if "--control" in sys.argv:  # positive control: home one entity in a far family
    ov["optimal_setpoint"] = "cost"
total = {"split_en": 0, "split_sv": 0, "untranslated": 0, "dup_name_en": 0, "id_split": 0}
seen = {}
dt_util.freeze(golden.START)
try:
    for scen, cfg in golden.coordinator_scenarios().items():
        ents = build(cfg)
        if MODE == "enabled": ents = [e for e in ents if e[3]]
        rows = []
        for plat, key, eid, en_ in ents:
            n_en = EN.get(plat, {}).get(key, {}).get("name"); n_sv = SV.get(plat, {}).get(key, {}).get("name")
            if n_en is None or n_sv is None:
                total["untranslated"] += 1; print(f"UNTRANSLATED {scen} {plat}:{key}")
                continue
            rows.append((plat, key, eid, n_en, n_sv))
        fam = {}
        for r in rows: fam.setdefault(ov.get(r[1], r[1].split("_")[0]), set()).add((r[0], r[1]))
        fam = {k: v for k, v in fam.items() if len(v) >= 2}
        for lang, idx in (("en", 3), ("sv", 4)):
            order = [(r[0], r[1]) for r in sorted(rows, key=lambda r: COLL[lang](r[idx]))]
            for tok, mem in sorted(fam.items()):
                n = runs(order, mem)
                if n > 1:
                    total[f"split_{lang}"] += 1
                    names = sorted((r[idx] for r in rows if (r[0], r[1]) in mem), key=COLL[lang])
                    print(f"SPLIT {scen} {lang} {tok} runs={n} {names}")
        # entity_id sort within a platform: family by object-id lead token
        for plat in {r[0] for r in rows}:
            pr = sorted([r for r in rows if r[0] == plat], key=lambda r: r[2])
            ids = [(r[0], r[1]) for r in pr]
            for tok, mem in fam.items():
                m = {x for x in mem if x[0] == plat}
                if len(m) >= 2 and runs(ids, m) > 1:
                    total["id_split"] += 1; print(f"IDSPLIT {scen} {plat} {tok}")
        from collections import Counter
        c = Counter(r[3] for r in rows)
        total["dup_name_en"] += sum(1 for v in c.values() if v > 1)
        print(f"CELL {scen} entities={len(rows)} families={len(fam)}")
finally:
    dt_util.freeze(None)
for k, v in total.items(): print(f"RESULT {k}={v} count")
tp, tt = time.process_time()-t0p, time.thread_time()-t0t
print(f"RESULT thread_factor={tp/tt:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
