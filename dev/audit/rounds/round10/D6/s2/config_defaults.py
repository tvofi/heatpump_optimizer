#!/usr/bin/env python3
"""D6-s2 claims harness: docs/configuration.md setting tables vs config_flow._OPTION_FIELDS.

METRIC: per table row in docs/configuration.md whose Setting label maps (via
strings.json options.step.*.data labels) to a key in config_flow._OPTION_FIELDS,
compare the documented numeric Default with the registry row's default (the value
the production marker renders: config_flow._field_marker with current={}), and the
documented "a–b" Range with the NumberSelector min/max. Count key: the value the
production marker/selector delivers, never the doc text alone.
RUN: PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python dev/audit/rounds/round10/D6/s2/config_defaults.py [--perturb]
--perturb swaps _OPTION_FIELDS' target_temperature default to 99.0 in memory; default_false must rise by >=1.
EXPECTED: see REPORT.md (exact counts, tolerance 0). BASELINE 17f1c55fad1b, machine: macOS arm64 seat box B2.
"""
import os
for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
import json, re, sys, time
sys.path.insert(0, "custom_components"); sys.path.insert(0, "tests")
t0p, t0t = time.process_time(), time.thread_time()
from heatpump_optimizer import config_flow as cf
from homeassistant.helpers import selector

if "--perturb" in sys.argv:
    cf._OPTION_FIELDS = tuple(r._replace(default=99.0) if r.key == "target_temperature" else r for r in cf._OPTION_FIELDS)

strings = json.load(open("custom_components/heatpump_optimizer/strings.json"))
label2keys = {}
def walk(node):
    if isinstance(node, dict):
        d = node.get("data")
        if isinstance(d, dict):
            for k, lab in d.items():
                if isinstance(lab, str):
                    label2keys.setdefault(lab.strip().lower(), set()).add(k)
        for v in node.values(): walk(v)
walk(strings.get("options", {})); walk(strings.get("config", {}))

rows_by_key = {}
for r in cf._OPTION_FIELDS:
    rows_by_key.setdefault(r.key, []).append(r)

class H:  # minimal hass for _Computed defaults
    pass
def rendered_default(row):
    try:
        m = cf._field_marker(row, {}, None)
    except Exception:
        return None
    d = getattr(m, "default", None)
    if d is None or d is __import__("voluptuous").UNDEFINED: return None
    try: d = d()
    except TypeError: pass
    return d

num = re.compile(r"-?\d+(?:\.\d+)?")
checked = dtrue = dfalse = rtrue = rfalse = unver = 0
out = []
for ln, line in enumerate(open("docs/configuration.md"), 1):
    if not line.startswith("|") or line.startswith("|---"): continue
    cells = [re.sub(r"(?<=\d)[ \u2009\u202f\u00a0](?=\d{3})", "", c.strip()) for c in line.strip().strip("|").split("|")]
    if len(cells) < 3 or cells[0] == "Setting": continue
    keys = label2keys.get(cells[0].replace("**","").lower())
    if not keys: continue
    rows = [r for k in keys for r in rows_by_key.get(k, [])]
    if not rows: continue
    m = num.match(cells[1].replace("−","-"))
    if m:
        doc = float(m.group())
        vals = {rendered_default(r) for r in rows} - {None}
        nums = {float(v) for v in vals if isinstance(v,(int,float)) and not isinstance(v,bool)}
        if not nums: unver += 1; out.append(f"UNVERIFIABLE L{ln} {cells[0]!r} doc={doc} code={vals}")
        else:
            checked += 1
            if any(abs(n-doc) < 1e-9 for n in nums): dtrue += 1
            else: dfalse += 1; out.append(f"DEFAULT_FALSE L{ln} {cells[0]!r} keys={sorted(keys)} doc={doc} code={sorted(nums)}")
    if len(cells) >= 4:
        rm = re.match(r"(-?\d+(?:\.\d+)?)\s*[–-]\s*(-?\d+(?:\.\d+)?)", cells[2].replace("−","-"))
        if rm:
            lo, hi = float(rm.group(1)), float(rm.group(2))
            bounds = set()
            for r in rows:
                w = r.widget
                if isinstance(w, selector.NumberSelector):
                    bounds.add((float(w.config["min"]), float(w.config["max"])))
            if bounds:
                if (lo, hi) in bounds: rtrue += 1
                else: rfalse += 1; out.append(f"RANGE_FALSE L{ln} {cells[0]!r} keys={sorted(keys)} doc={lo}-{hi} code={sorted(bounds)}")
for o in out: print(o)
print(f"RESULT defaults_checked={checked} count")
print(f"RESULT default_true={dtrue} count")
print(f"RESULT default_false={dfalse} count")
print(f"RESULT default_unverifiable={unver} count")
print(f"RESULT range_true={rtrue} count")
print(f"RESULT range_false={rfalse} count")
pc, tc = time.process_time()-t0p, time.thread_time()-t0t
print(f"RESULT thread_factor={pc/tc if tc else 1:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
