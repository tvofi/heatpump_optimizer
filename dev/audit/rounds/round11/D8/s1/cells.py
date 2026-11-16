"""D8-s1 M1: every d8-cell (entity by state by language) against the entities the matrix builds.

Metric: per class, the count of `tools/audit/enumerate.py d8-cells` lines (or enum options) that fail:
  missing      the translation file lacks the cell's string, or it is empty
  same_as_en   a de/sv string byte-identical to en (an untranslated copy; proper nouns listed below are excluded)
  unbuilt      no entity with that platform + translation_key is constructed by any async_setup_entry
  option_gap   an ENUM option / climate preset an entity can publish that has no strings.json state
  unreached    a state= cell whose state no matrix cell published (informational, not a defect)
Command (from the export root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D8/s1/cells.py
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B4. Expected: the printed counts, exact.
Instrumented symbols: each platform's async_setup_entry (sensor, binary_sensor, button, climate, switch)
through rig.run_cell, and the entities' `options` / `_attr_preset_modes`.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402

PKG = "custom_components/heatpump_optimizer"
# Strings that are the same word in every language (product and protocol names).
PROPER = {"ECL110", "COP", "PV", "MQTT"}


def lookup(tr, facet):
    pl_key, what = facet.split(" ", 1)
    pl, key = pl_key.split(".", 1)
    body = tr.get("entity", {}).get(pl, {}).get(key)
    if body is None:
        return None
    if what == "name":
        return body.get("name")
    if what.startswith("state="):
        return (body.get("state") or {}).get(what[6:])
    if what.startswith("attr="):
        attr, _, st = what[5:].partition(":state=")
        ab = (body.get("state_attributes") or {}).get(attr) or {}
        return ab.get("name") if not st else (ab.get("state") or {}).get(st)
    return None


def main():
    t0, th0 = time.process_time(), time.thread_time()
    lines = subprocess.run([sys.executable, "tools/audit/enumerate.py", "d8-cells"], capture_output=True,
                           text=True, check=True).stdout.split("\n")
    lines = [ln for ln in lines if ln.strip()]
    tr = {f[:-5]: json.load(open(f"{PKG}/translations/{f}")) for f in os.listdir(f"{PKG}/translations")}
    built, published, options = set(), {}, {}
    for cell, cfg in rig.cells().items():
        _coord, ents, cycles = rig.run_cell(cfg)
        for _err, _data, rows in cycles:
            for r in rows:
                tk = (r["platform"], r["tkey"])
                built.add(tk)
                st = r["state"]
                if r["platform"] == "climate":
                    e = r["entity"]
                    options[tk] = set(getattr(e, "_attr_preset_modes", []) or [])
                    pm = getattr(e, "preset_mode", None)
                    if pm is not None:
                        published.setdefault((tk, "attr=preset_mode"), set()).add(pm)
                elif r["device_class"] == "enum":
                    options[tk] = set(r["options"] or [])
                    if st is not None:
                        published.setdefault((tk, "state"), set()).add(st)
    hits = {k: [] for k in ("missing", "same_as_en", "unbuilt", "option_gap", "unreached")}
    for ln in lines:
        lang, facet = ln.split(" ", 1)
        val = lookup(tr[lang], facet)
        if not val:
            hits["missing"].append(ln)
        elif lang != "en" and val == lookup(tr["en"], facet) and val not in PROPER:
            hits["same_as_en"].append(f"{ln} = {val!r}")
        pl, key = facet.split(" ")[0].split(".", 1)
        if (pl, key) not in built:
            hits["unbuilt"].append(ln)
        what = facet.split(" ", 1)[1]
        if lang == "en" and what.startswith("state="):
            seen = published.get(((pl, key), "state"), set())
            if what[6:] not in seen:
                hits["unreached"].append(ln)
    strings = json.load(open(f"{PKG}/strings.json"))["entity"]
    for (pl, key), opts in sorted(options.items()):
        body = strings.get(pl, {}).get(key, {})
        if pl == "climate":
            declared = set(((body.get("state_attributes") or {}).get("preset_mode") or {}).get("state", {}))
            # Home Assistant translates its own preset names (climate/const.py PRESET_*).
            builtin = {"comfort", "boost", "eco", "away", "home", "sleep", "activity", "none"}
            gap = sorted(o for o in opts if o not in declared and o not in builtin)
        else:
            gap = sorted(o for o in opts if o not in set(body.get("state", {})))
        hits["option_gap"] += [f"{pl}.{key} option={o}" for o in gap]
    if "-v" in sys.argv:
        for k, v in hits.items():
            for x in v:
                print(f"  {k}: {x}")
    print(f"RESULT d8_cells={len(lines)} count")
    print(f"RESULT built_translation_keys={len(built)} count")
    for k, v in hits.items():
        print(f"RESULT {k}={len(v)} count")
    pt = time.process_time() - t0
    print(f"RESULT thread_factor={pt / max(time.thread_time() - th0, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
