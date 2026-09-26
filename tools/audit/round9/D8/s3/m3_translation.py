"""D8-s3 / D8.M3 -- English/Swedish entity-name parity by concept token.

Metric (one line): entities (all six platforms, via async_setup_entry) whose
English name carries a concept token of CONCEPTS (family leads, qualifiers,
role words) while their Swedish name carries none of that token's Swedish
counterparts; plus translation-key set differences strings/en/sv.
Count key: the entity's own translation_key resolved through
translations/en.json and translations/sv.json, as the frontend resolves it.

Command (repo root):
    PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python tools/audit/round9/D8/s3/m3_translation.py
    ... --perturb  (in memory: sv sensor.sensor_gap_advisor name ->
                    "Sensorlucka, rådgivare")
Expected: concept_mismatch=1 (Sensor-Gap Advisor -> "Sensorlucka i valutan";
          exact), key_set_differences=0; --perturb -> concept_mismatch=0 (to_zero).
Null control: the 16 other concept tokens over the same 74 names read 0
mismatches -- the mapping is not a generator of misses.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud container B4 (linux).
Instrumented: heatpump_optimizer.sensor:SensorGapAdvisorSensor (translation_key
sensor_gap_advisor) and every entity's _attr_translation_key via async_setup_entry.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import roster  # noqa: E402
import golden  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

t0p, t0t = time.process_time(), time.thread_time()
if "--perturb" in sys.argv:
    roster.STRINGS["sv"]["sensor"]["sensor_gap_advisor"] = {"name": "Sensorlucka, rådgivare"}

# English token -> Swedish counterparts (any one satisfies), case-folded.
CONCEPTS = {
    "(lifetime)": ("(totalt)",), "(next 24 h)": ("(nästa 24 h)",),
    "(optimizer)": ("(optimeraren)",), "(estimated)": ("(uppskattad)",),
    "(model)": ("(modell)",), "(now)": ("aktuell", "(nu)"),
    "advisor": ("råd",), "cost": ("kostnad",), "learning": ("inlärning",),
    "dhw": ("varmvatten",), "plan ": ("plan",), "temperature": ("temperatur",),
    "savings": ("spar", "besparing"), "energy": ("energi",), "power": ("effekt",),
    "price": ("pris",), "solar": ("sol",), "recommendation": ("rekommender",),
}

hass, entry, coord = roster.build_coordinator(golden.coordinator_scenarios()["coord_all_features"])
try:
    ents = roster.collect(hass, entry, coord)
finally:
    dt_util.freeze(None)

mismatch, checked = [], 0
per_token = {t: 0 for t in CONCEPTS}
for p, e in ents:
    key = getattr(e, "_attr_translation_key", None)
    en = ((roster.STRINGS["en"].get(p, {}).get(key) or {}).get("name") or "").casefold()
    sv = ((roster.STRINGS["sv"].get(p, {}).get(key) or {}).get("name") or "").casefold()
    if not en:
        continue
    checked += 1
    for tok, svs in CONCEPTS.items():
        if tok in en and not any(s in sv for s in svs):
            mismatch.append((e.entity_id, en, sv, tok))
            per_token[tok] += 1
for m in mismatch:
    print("MISMATCH", *m)


def keyset(d):
    return {(p, k) for p, v in d.items() for k in v}


diff = (keyset(roster.STRINGS["en"]) ^ keyset(roster.STRINGS["sv"])) | (
    keyset(roster.STRINGS["en"]) ^ keyset(roster.STRINGS["strings"]))
print(f"RESULT names_checked={checked} count")
print(f"RESULT concept_mismatch={len(mismatch)} count")
print(f"RESULT concept_mismatch_other_tokens={sum(v for t, v in per_token.items() if t != 'advisor')} count")
print(f"RESULT key_set_differences={len(diff)} count")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = next(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin "))
except Exception:
    sw = -1
print(f"RESULT swapins={sw}")
