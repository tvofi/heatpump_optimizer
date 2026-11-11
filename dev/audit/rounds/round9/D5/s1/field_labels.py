"""D5-s1 harness: field names docs/configuration.md tells a reader to look for, against the UI.

Metric (one line): references in docs/configuration.md "## Changing settings later" to an
options field by a name the rendered form does not show -- (A) a table row under a page
heading (### <menu label>) whose first cell, parentheticals stripped, is no field label of
that page's options step; (B) an italic *Name* in any of README.md and the seven user docs that ends like a field
label (temperature|sensor|source|switch|entity|enabled|mode|control|feedback|experiment|
cycle|limit) and that no string in translations/en.json carries ("HP ..." names are the
GCHV Modbus package's own entities and are skipped).
Rows that name several fields at once ("A / B", "A, B", "The six ...", weekday list) are
composites and skipped.
Count key: the labels custom_components/heatpump_optimizer/translations/en.json gives
options.step.<id>.data (and .sections.*.data), with <id> resolved from the menu labels
options.step.init/advanced.menu_options -- the strings Home Assistant renders on the form.
Command (from the repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D5/s1/field_labels.py [--perturb]
--perturb relabels, in memory, thermal_model_zones' radiator_power_fraction to "Radiator
    power fraction" (the doc's name). Expected: unfindable_field_refs down by 1 (5 -> 4).
Expected at baseline: unfindable_field_refs=5 (A=2, B=3), exact.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B1 (linux container).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import re
import sys
import time

_t0p, _t0t = time.process_time(), time.thread_time()
EN = "custom_components/heatpump_optimizer/translations/en.json"
d = json.load(open(EN, encoding="utf-8"))
if "--perturb" in sys.argv:
    d["options"]["step"]["thermal_model_zones"]["sections"]["split"]["data"][
        "radiator_power_fraction"] = "Radiator power fraction"


def norm(s):
    return re.sub(r"\s*\(.*?\)\s*", " ", s).strip().strip("*`").strip().lower()


steps = d["options"]["step"]
menu = {**{v: k for k, v in steps["init"]["menu_options"].items()},
        **{v: k for k, v in steps["advanced"]["menu_options"].items()}}


def labels_of(node, out):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "data" and isinstance(v, dict):
                out.update(norm(t) for t in v.values() if isinstance(t, str))
            labels_of(v, out)
    return out


page_labels = {step: labels_of(steps.get(step, {}), set()) for step in menu.values()}
all_strings = set()


def strings_of(node):
    if isinstance(node, dict):
        for v in node.values():
            strings_of(v)
    elif isinstance(node, list):
        for v in node:
            strings_of(v)
    elif isinstance(node, str):
        all_strings.add(norm(node))


strings_of(d)
lines = open("docs/configuration.md", encoding="utf-8").read().split("\n")
start = next(i for i, l in enumerate(lines) if l.startswith("## Changing settings later"))
end = next(i for i, l in enumerate(lines) if l.startswith("## The hydronic layout catalog"))
bad_a, bad_b, page, hdr = [], [], None, None
for i in range(start, end):
    line = lines[i]
    m = re.match(r"^###\s+(.*)", line)
    if m:
        page, hdr = m.group(1).strip(), None
        continue
    if line.startswith("|"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if hdr is None:
            hdr = cells
            continue
        if set(line.replace("|", "").strip()) <= set("-: "):
            continue
        name = cells[0]
        if hdr[0] != "Setting" or page not in menu:
            continue
        if re.search(r" / |, |^The |Monday", name):
            continue  # composite row
        if norm(name) not in page_labels[menu[page]]:
            bad_a.append((i + 1, page, name))
    else:
        hdr = None
DOCS = ["README.md"] + [f"docs/{n}.md" for n in (
    "architecture", "automations", "configuration", "dashboard-card", "ecl110",
    "how-it-works", "setup")]
LABEL_END = r"(?:temperature|sensor|source|switch|entity|enabled|mode|control|feedback|experiment|cycle|limit)"
for path in DOCS:
    for n, line in enumerate(open(path, encoding="utf-8").read().split("\n"), 1):
        for m in re.finditer(r"(?<![*\w])\*([A-Z][^*\n]{3,70}?" + LABEL_END + r")\*(?!\*)", line):
            name = m.group(1)
            if name.startswith("HP "):
                continue
            if norm(name) not in all_strings:
                bad_b.append((f"{path}:{n}", name))
for r in bad_a:
    print(f"A configuration.md:{r[0]} page '{r[1]}' row '{r[2]}' is no field on that page")
for r in bad_b:
    print(f"B {r[0]} italic '{r[1]}' is no UI string")
cpu_p, cpu_t = time.process_time() - _t0p, time.thread_time() - _t0t
print(f"RESULT pages_resolved={len(menu)} count")
print(f"RESULT table_rows_unfindable={len(bad_a)} count")
print(f"RESULT italic_refs_unfindable={len(bad_b)} count")
print(f"RESULT unfindable_field_refs={len(bad_a) + len(bad_b)} count")
print(f"RESULT thread_factor={cpu_p / cpu_t if cpu_t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
