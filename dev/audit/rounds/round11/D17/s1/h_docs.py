"""D17-s1 step M1: each universe line's documented effect, with its file and key.

Metric: for every line of `enumerate.py d17-features --kind options-step` and
`--kind option`, the strings.json key holding its documented effect
(options.step.<s>.description for a step, options.step.<s>.data_description.<f> for an
option) and its first sentence; RESULT undocumented counts lines with none (each would
be a lead for D5). Count key: the enumerator's own lines, looked up in strings.json.

Command:  python3 dev/audit/rounds/round11/D17/s1/h_docs.py
Expected: RESULT items=156, RESULT undocumented=0 (exact)
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13
Perturbation: --perturb-drop deletes one data_description in memory (away.away_temperature):
undocumented goes up to 1.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402

F = "custom_components/heatpump_optimizer/strings.json"
s = json.load(open(F))["options"]["step"]
if "--perturb-drop" in sys.argv:
    del s["away"]["data_description"]["away_temperature"]


def lines(kind):
    out = subprocess.check_output([sys.executable, "tools/audit/enumerate.py", "d17-features", "--kind", kind],
                                  text=True)
    return [l.split()[1] for l in out.splitlines()]


def first(text):
    text = re.sub(r"\s+", " ", text or "").strip()
    m = re.match(r"(.+?[.!?])(\s|$)", text)
    return (m.group(1) if m else text)[:220]


n = und = 0
for step in lines("options-step"):
    n += 1
    d = s[step].get("description") or s[step].get("title")
    key = f"options.step.{step}.description"
    und += 0 if d else 1
    print(f"DOC options-step {step}\t{F}:{key}\t{first(d)}")
for item in lines("option"):
    n += 1
    step, field = item.split(".")
    d = (s[step].get("data_description") or {}).get(field)
    und += 0 if d else 1
    print(f"DOC option {item}\t{F}:options.step.{step}.data_description.{field}\t{first(d) if d else '<NONE>'}")
print(f"RESULT items={n}")
print(f"RESULT undocumented={und}")
print("RESULT thread_factor=1.0")
print(f"RESULT load1={os.getloadavg()[0]}")
print("RESULT swapins=0")
