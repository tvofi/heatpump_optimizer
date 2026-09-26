"""D8-s3 / D8.M3 -- family splits under entity_id, English-name and Swedish-name sort.

Metric (one line): families (defined by a PRODUCTION symbol -- class, mixin,
input slot or card literal, never by name) whose members, less those homed in
a second family, occupy more than one contiguous run of the whole six-platform
roster sorted by English / Swedish name (entity_id: runs beyond one per domain).
Count key: entity_id and translation_key as each entity carries them after
the real async_setup_entry, names resolved through translations/en.json and
sv.json exactly as the frontend resolves translation_key.

Command (repo root):
    PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python tools/audit/round9/D8/s3/m3_families.py
    ... --perturb  (in memory: the Diagnose Last Interval button's English and
                    Swedish names take the family's lead token -- "Prediction
                    Accuracy Diagnose Last Interval" / "Prognosnoggrannhet
                    diagnostisera senaste intervallet")
Expected: families_split_unexplained_name_en=2, _name_sv=2 (accuracy and
          energy_meters; exact); --perturb -> 1 and 1 (down; accuracy joins).
Null control: families_split_* for the families whose members share a
translation-key lead (ecl110, tariff, card_headline) read 0 in every ordering.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud container B4 (linux).
Instrumented: heatpump_optimizer.button:DiagnoseIntervalButton,
heatpump_optimizer.sensor:PredictionAccuracySensor, entity:DHWEntityMixin,
sensor:_AccumulatingSensor, and every platform's async_setup_entry.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import re
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import roster  # noqa: E402
import golden  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import sensor, button, entity as entity_mod  # noqa: E402

t0p, t0t = time.process_time(), time.thread_time()
if "--perturb" in sys.argv:
    roster.STRINGS["en"]["button"]["diagnose_last_interval"] = {
        "name": "Prediction Accuracy Diagnose Last Interval"}
    roster.STRINGS["sv"]["button"]["diagnose_last_interval"] = {
        "name": "Prognosnoggrannhet diagnostisera senaste intervallet"}

hass, entry, coord = roster.build_coordinator(
    golden.coordinator_scenarios()["coord_all_features"])
try:
    ents = roster.collect(hass, entry, coord)
finally:
    dt_util.freeze(None)

card = (roster.ROOT / "www/heatpump-optimizer-card.js").read_text()
card_suffixes = set(re.findall(r'"(_plan_[a-z_]+)"', card))

FAMILIES = {
    # DHW Heavy Day Demand is a hot-water subject outside the mixin (its own
    # evidence gate); listed by class so the family is the subject, not the name.
    "dhw": lambda p, e: isinstance(e, (entity_mod.DHWEntityMixin, sensor.DHWHeavyDaySensor)),
    "ecl110": lambda p, e: getattr(e, "_input_slots", None) == sensor.ECL110_TOPIC_SLOTS,
    "tariff": lambda p, e: isinstance(e, (sensor.MonthlyPeakSensor, sensor.PowerHeadroomSensor)),
    "learning": lambda p, e: isinstance(e, (sensor.ComfortWeightSensor, sensor.CurrentCOPSensor,
                                            sensor.ObservedCOPSensor, button.ResetComfortWeightButton,
                                            button.SystemIdentificationButton)),
    "accuracy": lambda p, e: isinstance(e, (sensor.PredictionAccuracySensor, button.DiagnoseIntervalButton)),
    "pv": lambda p, e: isinstance(e, sensor.PVSurplusSensor),
    "card_headline": lambda p, e: any(e.entity_id.endswith(s) for s in card_suffixes),
    "energy_meters": lambda p, e: isinstance(e, sensor._AccumulatingSensor),
}

rows = []
for p, e in ents:
    key = getattr(e, "_attr_translation_key", None)
    en = (roster.STRINGS["en"].get(p, {}).get(key) or {}).get("name") or ""
    sv = (roster.STRINGS["sv"].get(p, {}).get(key) or {}).get("name") or ""
    rows.append({"p": p, "e": e, "id": e.entity_id, "en": en, "sv": sv})

ORDERS = {
    "entity_id": sorted(range(len(rows)), key=lambda i: rows[i]["id"]),
    "name_en": sorted(range(len(rows)), key=lambda i: rows[i]["en"].casefold()),
    "name_sv": sorted(range(len(rows)), key=lambda i: rows[i]["sv"].casefold()),
}


def runs(order, members):
    pos = sorted(order.index(i) for i in members)
    if len(pos) < 2:
        return 0
    return 1 + sum(1 for a, b in zip(pos, pos[1:]) if b != a + 1)


fam_members = {fam: [i for i, r in enumerate(rows) if pred(r["p"], r["e"])]
               for fam, pred in FAMILIES.items()}


def domain_excess(order, members):
    """entity_id sort puts the domain first, so a family spanning domains is
    split by construction; count only runs beyond one per domain."""
    by_dom = {}
    for i in members:
        by_dom.setdefault(rows[i]["p"], []).append(i)
    if len(members) < 2:
        return 0
    return 1 + sum(max(runs(order, m), 1) - 1 for m in by_dom.values())


split = {o: 0 for o in ORDERS}
unexplained = {o: 0 for o in ORDERS}
for fam, members in fam_members.items():
    # Members also homed in another production-defined family: a split they
    # cause is a trade-off between two families, not a naming defect.
    shared = {i for i in members
              for f2, m2 in fam_members.items() if f2 != fam and i in m2}
    own = [i for i in members if i not in shared]
    for oname, order in ORDERS.items():
        count = domain_excess if oname == "entity_id" else runs
        n = count(order, members)
        # Shared members are transparent: dropped from the sequence, so they
        # neither split the rest nor count as its gaps.
        n_own = count([i for i in order if i not in shared], own)
        field = {"entity_id": "id", "name_en": "en", "name_sv": "sv"}[oname]
        if n > 1:
            split[oname] += 1
            print(f"SPLIT {fam} {oname}: {n} runs over {sorted(rows[i][field] for i in members)}")
        if n_own > 1:
            unexplained[oname] += 1
            print(f"SPLIT_UNEXPLAINED {fam} {oname}: {n_own} runs over "
                  f"{sorted(rows[i][field] for i in own)}")
        print(f"RESULT {fam}_runs_{oname}={n} count")
    print(f"RESULT {fam}_members={len(members)} count")
for oname in ORDERS:
    print(f"RESULT families_split_{oname}={split[oname]} count")
    print(f"RESULT families_split_unexplained_{oname}={unexplained[oname]} count")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = next(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin "))
except Exception:
    sw = -1
print(f"RESULT swapins={sw}")
