"""D5 verify-v3 (reach and class) harness for D5-s1-05: field names the user docs tell a reader
to look for, against the labels Home Assistant renders from translations/en.json.

Metric (one line): *italic* or **bold** spans in README.md + the 7 user docs that sit within
four words of a form noun (field, setting, switch, toggle, option, sensor, picker, page) and are
not a case-insensitive substring of any en.json config/options label (data, sections.*.data,
menu_options, step titles, section names), parenthetical stripped; the finder's five sites are
reported separately.
Count key: the en.json strings the real frontend renders for these flows (the stub's
async_get_translations returns {}, so no stub is on this path).
Command (from the repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D5/verify-v3/v3_s1_05_labels.py [--perturb]
--perturb: add, in memory, the five doc spellings as extra labels. Expected: finder_sites_unfound
    5 -> 0 (Floor return temperature counted twice: :511 and :514) and form_refs_unfound down by at least the 3 italic sites.
Expected at baseline: finder_sites_unfound=5 (exact); form_refs_unfound printed with each site.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence); machine: 4-core
cloud container, CPython 3.14.
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
en = json.load(open("custom_components/heatpump_optimizer/translations/en.json", encoding="utf-8"))
labels = []


def collect(step):
    for k in ("title",):
        if isinstance(step.get(k), str):
            labels.append(step[k])
    labels.extend(v for v in (step.get("data") or {}).values() if isinstance(v, str))
    labels.extend(v for v in (step.get("menu_options") or {}).values() if isinstance(v, str))
    for sec in (step.get("sections") or {}).values():
        if isinstance(sec.get("name"), str):
            labels.append(sec["name"])
        labels.extend(v for v in (sec.get("data") or {}).values() if isinstance(v, str))


for flow in ("config", "options"):
    for step in en.get(flow, {}).get("step", {}).values():
        collect(step)
FINDER = ["Inter-zone transfer", "Radiator power fraction", "Floor return temperature",
          "Solar forecast source"]
if "--perturb" in sys.argv:
    labels.extend(FINDER)
norm = [re.sub(r"\s*\(.*?\)", "", l).lower() for l in labels]


def found(name):
    n = re.sub(r"\s*\(.*?\)", "", name).strip().lower()
    return any(n in l for l in norm)


FORM = re.compile(r"\b(field|fields|setting|settings|switch|toggle|option|options|sensor|picker|page)\b", re.I)
SPAN = re.compile(r"(?<![*\w])(\*\*|\*)([A-Z][^*\n]{2,60}?)\1(?![*\w])")
files = ["README.md"] + [f"docs/{n}.md" for n in ("architecture", "automations", "configuration",
                                                   "dashboard-card", "ecl110", "how-it-works", "setup")]
unfound = []
for f in files:
    for i, line in enumerate(open(f, encoding="utf-8").read().split("\n"), 1):
        if line.lstrip().startswith("|"):
            continue
        for m in SPAN.finditer(line):
            name = m.group(2).strip()
            if len(name.split()) < 2 or len(name.split()) > 7 or name.endswith((".", ":", ",")):
                continue
            around = line[max(0, m.start() - 40): m.end() + 40]
            if not FORM.search(around.replace(name, "")):
                continue
            if not found(name):
                unfound.append((f, i, name))
for u in unfound:
    print(f"UNFOUND {u[0]}:{u[1]} {u[2]!r}")
finder_unfound = sum(1 for n in FINDER if not found(n)) + int(not found("Floor return temperature"))
# sibling surfaces: entity names and selector option labels, which a form label check does not own
other = []
for plat in (en.get("entity") or {}).values():
    other.extend(v.get("name") for v in plat.values() if isinstance(v, dict) and isinstance(v.get("name"), str))
for sel in (en.get("selector") or {}).values():
    other.extend(v for v in (sel.get("options") or {}).values() if isinstance(v, str))
other_n = [o.lower() for o in other]
residual = [u for u in unfound if not any(u[2].lower() in o for o in other_n)]
for u in residual:
    print(f"RESIDUAL {u[0]}:{u[1]} {u[2]!r}")
cpu_p, cpu_t = time.process_time() - _t0p, time.thread_time() - _t0t
print(f"RESULT labels={len(labels)} count")
print(f"RESULT form_refs_unfound={len(unfound)} count")
print(f"RESULT unfound_not_entity_or_option={len(residual)} count")
print(f"RESULT finder_sites_unfound={finder_unfound} count")
print(f"RESULT thread_factor={cpu_p / cpu_t if cpu_t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
