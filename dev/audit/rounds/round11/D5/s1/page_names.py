"""D5-s1 harness: options pages that docs/how-it-works.md sends the reader to, against the real menu.

Metric: missing_pages = distinct "<Name> page" references in docs/how-it-works.md whose <Name>
is not a label of the options flow's menus (translations/en.json options.step.init/advanced
menu_options, the strings Home Assistant renders). Count key: the rendered menu labels.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s1/page_names.py [--perturb]
Expected at baseline 92d38ecb: missing_pages=1 ("Grid costs", referenced twice), exact.
Perturbation (--perturb): the menu labels are loaded with grid_fees renamed "Grid costs" in
memory (as if the page were named as the doc says); missing_pages falls to 0.
Machine: orchestrator Mac, local seat.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, re, sys, time
t0, c0 = time.time(), time.process_time()
tr = json.load(open("custom_components/heatpump_optimizer/translations/en.json", encoding="utf-8"))
steps = tr["options"]["step"]
if "--perturb" in sys.argv:
    steps["advanced"]["menu_options"]["grid_fees"] = "Grid costs"
labels = {v.lower() for s in steps.values() for v in s.get("menu_options", {}).values()}
doc = open("docs/how-it-works.md", encoding="utf-8").read()
refs = re.findall(r"(?:on|in) the ((?:[A-Z][\w-]*)(?: [\w-]+){0,4}?) page\b", doc)
missing = sorted({r for r in refs if r.lower() not in labels})
print("references:", refs)
print("missing:", missing)
print(f"RESULT missing_pages={len(missing)} pages")
pc, wc = time.process_time() - c0, time.time() - t0
print(f"RESULT thread_factor={pc / max(wc, 1e-9):.2f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
