"""D8-s2 / D8.M3: ordering and naming of every entity, every language.

Metric (one line each, RESULT keys):
  fam_runs_excess_entity_id_<platform>: sum over declared families (const.
    ENTITY_FAMILY_OVERRIDES, else translation key's lead token) of (runs-1)
    in the sorted entity_id list of that platform, built entities only.
    Key: the entity_id each built entity carries (production's suggested id).
  fam_runs_excess_name_<lang>: same, over the display names the frontend
    shows (strings.json for en, translations/<lang>.json otherwise), all
    platforms in one sort, per-language collation as tests/entities.py.
  tr_missing_<lang>/tr_extra_<lang>: leaf key paths of strings.json absent
    from / extra in translations/<lang>.json.  tr_placeholder_<lang>: leaves
    whose {placeholder} set differs from strings.json.
  name_missing_<lang>: built entities whose translation key has no name.
  enum_state_untranslated_<lang>: ENUM sensor options lacking a state string.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D8/s2/m3_naming.py [-v] [--perturb-lifetime-ids]
Instrumented symbols: heatpump_optimizer.{sensor,binary_sensor,button,switch,
  climate,datetime}.async_setup_entry (entity_id, translation_key) and
  heatpump_optimizer.const.ENTITY_FAMILY_OVERRIDES.
Perturbation: --perturb-lifetime-ids rewrites each lifetime-family member's
  entity_id to <platform>.heat_pump_optimizer_lifetime_<key> in memory (what a
  suggested-id move would deliver): fam_runs_excess_entity_id_sensor must fall.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, macOS arm64 (orchestrator box).
Expected at baseline: the counts in REPORT.json, exact (deterministic, +-0).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
t0p, t0t = time.process_time(), time.thread_time()
import rig  # noqa: E402
from heatpump_optimizer import const  # noqa: E402

ROOT = Path("custom_components/heatpump_optimizer")
STR = json.loads((ROOT / "strings.json").read_text())
LANGS = sorted(p.stem for p in (ROOT / "translations").glob("*.json"))
TR = {l: json.loads((ROOT / "translations" / f"{l}.json").read_text()) for l in LANGS}
VERBOSE = "-v" in sys.argv
PERTURB = "--perturb-lifetime-ids" in sys.argv

SV_TAIL = str.maketrans({"å": "z\u0001", "ä": "z\u0002", "ö": "z\u0003"})
COLL = {
    "en": lambda n: n.casefold(),
    "sv": lambda n: n.casefold().translate(SV_TAIL),
    "de": lambda n: n.casefold().translate(str.maketrans("äöü", "aou")),
}


def fam(key):
    return const.ENTITY_FAMILY_OVERRIDES.get(key, key.split("_")[0])


def runs_excess(order, label):
    """sum(runs-1) over families of >=2 members in ``order`` (list of keys)."""
    pos = {}
    for i, k in enumerate(order):
        pos.setdefault(fam(k), []).append(i)
    total, detail = 0, []
    for f, ps in sorted(pos.items()):
        if len(ps) < 2:
            continue
        r = 1 + sum(1 for a, b in zip(ps, ps[1:]) if b != a + 1)
        if r > 1:
            total += r - 1
            detail.append(f"{f}:{r}runs[{','.join(order[p] for p in ps)}]")
    if detail:
        print(f"DETAIL {label}: " + "; ".join(detail))
    return total


def leaves(d, path=()):
    if isinstance(d, dict):
        for k, v in d.items():
            yield from leaves(v, path + (k,))
    else:
        yield path, d


ents = rig.all_entities()
results = {}

# --- entity_id sort, per platform and global --------------------------------
ids = []
for (plat, key), (_p, e, _sc) in ents.items():
    eid = e.entity_id
    if PERTURB and fam(key) == "lifetime":
        eid = f"{plat}.heat_pump_optimizer_lifetime_{key}"
    ids.append((eid, plat, key))
ids.sort()
if VERBOSE:
    for eid, p, k in ids:
        print(f"ID {eid} fam={fam(k)}")
for plat in rig.PLATFORMS:
    order = [k for eid, p, k in ids if p == plat]
    results[f"fam_runs_excess_entity_id_{plat}"] = runs_excess(order, f"id {plat}")
results["fam_runs_excess_entity_id_all"] = runs_excess([k for _, _, k in ids], "id all")

# --- display-name sort, per language ----------------------------------------
for lang in ["en"] + [l for l in LANGS if l != "en"]:
    src = STR if lang == "en" else TR[lang]
    rows, missing = [], []
    for (plat, key), (_p, e, _sc) in ents.items():
        name = src["entity"].get(plat, {}).get(key, {}).get("name")
        if not name:
            missing.append(f"{plat}.{key}")
            name = f"~{key}"
        rows.append((COLL.get(lang, str.casefold)(name), name, plat, key))
    rows.sort()
    if VERBOSE:
        for r in rows:
            print(f"NAME {lang} {r[1]!r} {r[2]}.{r[3]} fam={fam(r[3])}")
    results[f"name_missing_{lang}"] = len(missing)
    if missing:
        print(f"DETAIL name_missing {lang}: {missing}")
    results[f"fam_runs_excess_name_{lang}"] = runs_excess([r[3] for r in rows], f"name {lang}")
    dup = {}
    for r in rows:
        dup.setdefault(r[0], []).append(f"{r[2]}.{r[3]}")
    d = {k: v for k, v in dup.items() if len(v) > 1}
    results[f"name_duplicate_{lang}"] = len(d)
    if d:
        print(f"DETAIL name_duplicate {lang}: {d}")

# --- strings.json against every translation file ------------------------------
ph = re.compile(r"\{(\w+)\}")
sl = dict(leaves(STR))
for lang in LANGS:
    tl = dict(leaves(TR[lang]))
    miss = sorted(set(sl) - set(tl))
    extra = sorted(set(tl) - set(sl))
    bad_ph = sorted(p for p in set(sl) & set(tl)
                    if isinstance(sl[p], str) and isinstance(tl[p], str)
                    and set(ph.findall(sl[p])) != set(ph.findall(tl[p])))
    results[f"tr_missing_{lang}"] = len(miss)
    results[f"tr_extra_{lang}"] = len(extra)
    results[f"tr_placeholder_{lang}"] = len(bad_ph)
    for nm, lst in (("missing", miss), ("extra", extra), ("placeholder", bad_ph)):
        if lst:
            print(f"DETAIL tr_{nm} {lang}: " + ", ".join(".".join(p) for p in lst[:40])
                  + (f" ... (+{len(lst)-40})" if len(lst) > 40 else ""))
    if lang == "en":
        diff = sorted(p for p in set(sl) & set(tl) if sl[p] != tl[p])
        results["tr_en_value_diff"] = len(diff)
        if diff:
            print("DETAIL en value diff: " + ", ".join(".".join(p) for p in diff[:40]))

# --- ENUM sensors: every option has a state string in every language --------
for lang in ["en"] + [l for l in LANGS if l != "en"]:
    src = STR if lang == "en" else TR[lang]
    bad = []
    for (plat, key), (_p, e, _sc) in ents.items():
        opts = getattr(e, "_attr_options", None) or getattr(e, "options", None)
        dc = str(getattr(e, "_attr_device_class", "") or getattr(e, "device_class", "") or "")
        if plat != "sensor" or not opts or "enum" not in dc.lower():
            continue
        states = src["entity"].get(plat, {}).get(key, {}).get("state", {})
        bad += [f"{key}:{o}" for o in opts if o not in states]
    results[f"enum_state_untranslated_{lang}"] = len(bad)
    if bad:
        print(f"DETAIL enum untranslated {lang}: {bad}")

results["entities_built"] = len(ents)
for k, v in results.items():
    print(f"RESULT {k}={v} count")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
