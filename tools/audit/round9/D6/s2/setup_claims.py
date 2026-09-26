"""D6-s2 harness: docs/setup.md claims, driven through the real config flow and quick_setup.

Metric: count of setup.md claims (image links resolve, the second screen's three groups,
the five quick-setup question defaults, the 500 L / 35 L buffer figures, 'hot water off
removes hot water', quick path derives identical physics to the wizard questionnaire,
the temperature page's seven sliders, the pre-fill offer off by default, 23 option pages,
Quick setup on the first menu) that disagree with the measurement.
Symbols: config_flow.HeatPumpOptimizerConfigFlow / HeatPumpOptimizerOptionsFlow (through
tests/golden.py:capture_config_flow), quick_setup.derive, config_flow._derive_preset.
Key: the value the production seam delivers.

Command (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/s2/setup_claims.py
Perturbation: --perturb patches quick_setup.QUICK_SETUP_BUFFER_VOLUME=400.0 and
  quick_setup.SHIPPED_ANSWERS[dhw_tank]=False in memory; setup_claims_false must go up by >= 2.
Expected: see REPORT.md (exact).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud container, 4 CPU, Linux.
Root rule: ROOT = Path.cwd().
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
from unittest import mock

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tests" / "hastub"))
_t0p, _t0t = time.process_time(), time.thread_time()

import golden  # noqa: E402
from heatpump_optimizer import const, quick_setup  # noqa: E402
import heatpump_optimizer.config_flow as cf  # noqa: E402

DOCP = ROOT / "docs/setup.md"
DOC = DOCP.read_text()
DOCL = DOC.splitlines()
STR = json.loads((ROOT / "custom_components/heatpump_optimizer/strings.json").read_text())
RESULTS = []


def line_of(pat):
    for i, l in enumerate(DOCL, 1):
        if re.search(pat, l):
            return i
    return 0


def claim(pat, what, ok, detail=""):
    RESULTS.append((f"docs/setup.md:{line_of(pat)}", what, bool(ok), detail))


def run():
    pages = golden.capture_config_flow()
    init = pages["_initial"]
    # images
    for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", DOC):
        p = (DOCP.parent / m.group(1))
        claim(re.escape(m.group(1)), f"image {m.group(1)} exists", p.is_file() and p.stat().st_size > 0,
              f"{p.stat().st_size if p.exists() else 0} bytes")
    # screen 2 groups
    us = init["user_sensors"]
    groups = [k for k, v in us.items() if "fields" in v]
    names = [STR["config"]["step"]["user_sensors"].get("sections", {}).get(g, {}).get("name", g) for g in groups]
    doc_groups = re.findall(r"\*\*(Room temperatures|Solar forecast|Heat pump and tanks)\*\*", DOC)
    claim(r"The pickers sit in three groups", "screen 2 has three groups with the documented names",
          len(groups) == 3 and [n.lower() for n in names] == [d.lower() for d in doc_groups], f"{names}")
    # five quick-setup question defaults
    qs = init["quick_setup"]

    def flat(d, o):
        for k, v in d.items():
            if "fields" in v:
                flat(v["fields"], o)
            else:
                o[k] = v
        return o
    qf = flat(qs, {})
    table = {"Two-zone house": "two_zone", "Buffer tank": "buffer_tank", "Hot water tank": "dhw_tank",
             "Wood furnace": "wood_furnace", "Wood buffer tank": "wood_buffer_tank"}
    for label, key in table.items():
        m = re.search(rf"^\| {re.escape(label)} \| (\*\*)?(on|off)(\*\*)? \|", DOC, re.M)
        want = m.group(2) == "on" if m else None
        got = qf.get(key, {}).get("default")
        claim(rf"^\| {re.escape(label)} \|", f"quick setup '{label}' defaults {m.group(2) if m else '?'}",
              got == repr(want), f"form default {got}")
    # 500 L / 35 L
    yes = quick_setup.derive({"buffer_tank": True})
    no = quick_setup.derive({"buffer_tank": False})
    claim(r"500 litres", "buffer yes records 500 L; no leaves the shipped 35 L default",
          yes.get(const.CONF_BUFFER_TANK_VOLUME) == 500.0 and const.CONF_BUFFER_TANK_VOLUME not in no
          and const.DEFAULT_BUFFER_TANK_VOLUME == 35.0,
          f"yes {yes.get(const.CONF_BUFFER_TANK_VOLUME)}, no {no.get(const.CONF_BUFFER_TANK_VOLUME)}, default {const.DEFAULT_BUFFER_TANK_VOLUME}")
    off = quick_setup.derive({"dhw_tank": False})
    claim(r"turning it off removes hot water", "hot water off writes dhw_enabled False",
          off.get(const.CONF_DHW_ENABLED) is False, str(off.get(const.CONF_DHW_ENABLED)))
    # identical physics, single-zone answers
    answers = {"building_structure": "concrete_slab", "building_era": "pre_1960",
               "building_foundation": "none", "heated_area_m2": 180.0,
               "upper_emitter": "radiators", "lower_emitter": "floor"}
    q = quick_setup.derive({**answers, "two_zone": False})
    w = cf._derive_preset(answers, {})
    keys = sorted(set(w) | {k for k in q if k in cf.DERIVED_THERMAL_KEYS})
    diff = {k: (q.get(k), w.get(k)) for k in keys if q.get(k) != w.get(k)}
    claim(r"derives the identical physics", "quick path and wizard questionnaire derive identical physics",
          not diff, f"differing keys {diff}")
    # temperature page: seven sliders
    tp = init["temperature"]
    sliders = [k for k, v in tp.items() if (v.get("config") or {}).get("mode") == "'slider'"]
    claim(r"seven sliders", "temperature page has seven sliders", len(sliders) == 7 == len(tp), f"{len(sliders)}/{len(tp)}")
    # pre-fill offer off by default
    mp = flat(pages["modbus_prefill"], {})
    offer = mp.get(getattr(const, "CONF_PREFILL_OFFER", "prefill_offer"), {}).get("default")
    claim(r"off by default", "the pre-fill offer switch defaults off", offer == "False", str(offer))
    # 23 option pages; quick setup on the first menu
    n_pages = sum(1 for k in pages if not k.startswith("_"))
    claim(r"presents the 23 options pages", "23 options pages", n_pages == 23, str(n_pages))
    first = [k for k, _ in pages["_menu"]["init"]]
    claim(r"\*\*Quick setup\*\* is here too, on the", "Quick setup is on the first menu",
          "quick_setup" in first, str(first))
    claim(r"is the last entry on the", "Quick setup is the last entry on the first menu (before Advanced)",
          [k for k in first if k != "advanced"][-1] == "quick_setup", str(first))


def main():
    patches = []
    if "--perturb" in sys.argv:
        patches = [mock.patch.object(quick_setup, "QUICK_SETUP_BUFFER_VOLUME", 400.0),
                   mock.patch.dict(quick_setup.SHIPPED_ANSWERS, {"dhw_tank": False})]
    for p in patches:
        p.start()
    try:
        run()
    finally:
        for p in patches:
            p.stop()
    for src, what, ok, det in RESULTS:
        print(f"{'true ' if ok else 'FALSE'} {src:22s} {what} -- {det}")
    print(f"RESULT setup_claims={len(RESULTS)} count")
    print(f"RESULT setup_claims_false={sum(not r[2] for r in RESULTS)} count")
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
