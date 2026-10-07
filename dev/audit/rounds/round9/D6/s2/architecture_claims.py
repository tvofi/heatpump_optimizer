"""D6-s2 harness: docs/architecture.md claims about the package, measured on the package.

Metric: count of architecture.md claims (module count, the module-level homeassistant
importer count and roster, the in-function toucher, the HA-free count, the module map's
completeness, per-platform entity rosters, snapshot ring size, boost duration, the
hacs.json floor) that disagree with the measurement. Module import facts come from an
AST walk of custom_components/heatpump_optimizer/*.py (module-level = statements not
nested in a def/class body); entity rosters from each platform's real async_setup_entry
(names = the entity's translation_key resolved through translations/en.json);
the snapshot ring size read from snapshots.RING_SIZE (a constant read, spot depth);
the boost duration measured through boost.BoostState.set.

Command (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/s2/architecture_claims.py
Perturbation: --perturb patches snapshots.RING_SIZE=9 and boost.BOOST_HOURS=3 in memory;
  architecture_claims_false must go up by 2.
Expected: see REPORT.md (exact).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud container, 4 CPU, Linux.
Root rule: ROOT = Path.cwd().
"""

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import ast
import asyncio
import importlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tests" / "hastub"))
_t0p, _t0t = time.process_time(), time.thread_time()

import harness  # noqa: E402,F401  (puts custom_components on sys.path)

PKG = ROOT / "custom_components/heatpump_optimizer"
DOC = (ROOT / "docs/architecture.md").read_text()
DOCL = DOC.splitlines()
RESULTS = []


def line_of(pat):
    for i, l in enumerate(DOCL, 1):
        if re.search(pat, l):
            return i
    return 0


def claim(pat, what, ok, detail=""):
    RESULTS.append((f"docs/architecture.md:{line_of(pat)}", what, bool(ok), detail))


def ha_imports(path):
    tree = ast.parse(path.read_text())
    top, inner = False, False

    def is_ha(node):
        if isinstance(node, ast.Import):
            return any(a.name.split(".")[0] == "homeassistant" for a in node.names)
        if isinstance(node, ast.ImportFrom):
            return (node.module or "").split(".")[0] == "homeassistant" and node.level == 0
        return False

    def walk(node, nested):
        nonlocal top, inner
        for child in ast.iter_child_nodes(node):
            n = nested or isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda))
            if is_ha(child):
                if nested:
                    inner = True
                else:
                    top = True
            walk(child, n)
    walk(tree, False)
    return top, inner


def modules():
    mods = sorted(p.stem for p in PKG.glob("*.py"))
    top = sorted(m for m in mods if ha_imports(PKG / f"{m}.py")[0])
    inner_only = sorted(m for m in mods if not ha_imports(PKG / f"{m}.py")[0] and ha_imports(PKG / f"{m}.py")[1])
    m = re.search(r"(\d+) modules, of which (\d+) import", DOC)
    claim(r"\d+ modules, of which", f"{m.group(1)} modules", int(m.group(1)) == len(mods), f"measured {len(mods)}")
    claim(r"\d+ modules, of which", f"{m.group(2)} import homeassistant at module level",
          int(m.group(2)) == len(top), f"measured {len(top)}")
    # the named roster
    i = DOC.index("## The Home Assistant boundary")
    para = DOC[i:DOC.index("One module outside", i)]
    named = set(re.findall(r"`(\w+)`", para)) - {"homeassistant"}
    claim(r"^23 of the 66|^\d+ of the \d+ modules", "the named module-level roster is the measured set",
          named == set(top), f"doc-only {sorted(named - set(top))}; code-only {sorted(set(top) - named)}")
    claim(r"One module outside that set", "exactly one more module touches it inside a function: inputs",
          inner_only == ["inputs"], f"measured {inner_only}")
    m = re.search(r"The other (\d+) modules are deliberately free", DOC)
    claim(r"The other \d+ modules", f"{m.group(1)} modules free of it",
          int(m.group(1)) == len(mods) - len(top) - len(inner_only), f"measured {len(mods) - len(top) - len(inner_only)}")
    # module map completeness
    i = DOC.index("## The module map")
    block = DOC[i:DOC.index("## The Home Assistant boundary")]
    mapped = set(re.findall(r"── (\w+)\.py", block))
    claim(r"^## The module map", "the module map lists every module",
          mapped == set(mods), f"unlisted {sorted(set(mods) - mapped)}; stale {sorted(mapped - set(mods))}")


def rosters():
    from harness import FakeEntry, FakeHass
    from heatpump_optimizer import const
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    en = json.loads((PKG / "translations/en.json").read_text())["entity"]
    hass = FakeHass()
    entry = FakeEntry(data={"dhw_tank_volume": 180.0})
    c = HeatPumpOptimizerCoordinator(hass, entry)
    asyncio.run(c._update_current_state())
    entry.runtime_data = c
    for plat, pat in (("binary_sensor", r"── binary_sensor\.py"), ("button", r"── button\.py"),
                      ("switch", r"── switch\.py")):
        added = []
        mod = importlib.import_module(f"heatpump_optimizer.{plat}")
        asyncio.run(mod.async_setup_entry(hass, entry, lambda e, *a, **k: added.extend(e)))
        names = sorted(en.get(plat, {}).get(getattr(e, "_attr_translation_key", None) or getattr(e, "translation_key", ""), {}).get("name", "?")
                       for e in added)
        start = line_of(pat) - 1
        text = " ".join(DOCL[start:start + 4]).split("#", 1)[1]
        stop = re.search(r"├── (?!.*#\s)", text)
        text = re.split(r"├──", text)[0]
        text = text.replace("│", " ")
        text = re.sub(r"\s*#\s*", " ", text)
        doc_names = [re.sub(r"\s+", " ", x).strip(" ,.") for x in text.split(",") if x.strip(" ,.")]
        norm = lambda s: re.sub(r"[^a-z]", "", s.lower())
        if plat == "button":
            # prose paraphrase: each doc item must be a word-subset of one entity name
            words = lambda s: set(re.findall(r"[a-z]+", s.lower())) - {"learning", "system"}
            ok = len(doc_names) == len(names) and all(
                any(words(d) <= words(n) | {"identification"} for n in names) for d in doc_names)
        else:
            ok = sorted(map(norm, doc_names)) == sorted(map(norm, names))
        claim(pat, f"{plat}.py roster", ok, f"doc {doc_names} vs entities {names}")


def constants():
    from heatpump_optimizer import boost, snapshots
    m = re.search(r"weekly, last (\d+) kept", DOC)
    ring = getattr(snapshots, "RING_SIZE")
    claim(r"weekly, last \d+ kept", f"snapshots: last {m.group(1)} kept", int(m.group(1)) == ring, f"RING_SIZE {ring}")
    now = datetime(2026, 1, 15, 12, tzinfo=timezone.utc)
    st = boost.BoostState() if hasattr(boost, "BoostState") else None
    hours = None
    if st is not None:
        try:
            st.set(boost.CHANNEL_DHW, True, now)
            hours = (st.until[boost.CHANNEL_DHW] - now).total_seconds() / 3600
        except Exception as exc:  # pragma: no cover
            hours = f"err {exc!r}"
    if hours is None:
        hours = boost.BOOST_HOURS
    claim(r"Two-hour maximum-heat", "boost: two-hour overlays", hours == 2, f"measured {hours} h")
    hacs = json.loads((ROOT / "hacs.json").read_text())["homeassistant"]
    claim(r"2025\.2\.0 is the first", "the floor is 2025.2.0 (hacs.json)", hacs == "2025.2.0", hacs)


def main():
    patches = []
    if "--perturb" in sys.argv:
        from heatpump_optimizer import boost, snapshots
        patches = [mock.patch.object(snapshots, "RING_SIZE", 9), mock.patch.object(boost, "BOOST_HOURS", 3)]
    for p in patches:
        p.start()
    try:
        modules()
        rosters()
        constants()
    finally:
        for p in patches:
            p.stop()
    for src, what, ok, det in RESULTS:
        print(f"{'true ' if ok else 'FALSE'} {src:28s} {what} -- {det}")
    print(f"RESULT architecture_claims={len(RESULTS)} count")
    print(f"RESULT architecture_claims_false={sum(not r[2] for r in RESULTS)} count")
    tp, tt = time.process_time() - _t0p, time.thread_time() - _t0t
    print(f"RESULT thread_factor={tp / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "na"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
