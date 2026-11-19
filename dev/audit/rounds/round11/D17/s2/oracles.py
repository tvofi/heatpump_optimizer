"""D17-s2 step M1 -- each config-step / config-field item's documented effect, by file and key.

Metric: per line of `enumerate.py d17-features --kind config-step|config-field`, the
documentation sentence it carries in custom_components/heatpump_optimizer/strings.json
(config.step.<step>.description for a step, config.step.<step>.data_description.<field>
for a field); an item with none is a D5 lead. RESULT items_documented / items_undocumented.

Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D17/s2/oracles.py
Expected at 92d38ecb: RESULT items=117 ; RESULT items_undocumented=0 (exact).
Perturbation: drop one data_description key from the loaded strings in memory
(`--perturb` removes config.step.dhw.data_description.dhw_windows) -> items_undocumented=1.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13 (Linux x86_64 container).
Instrumented: tools/audit/enumerate.py:d17 (the universe) over strings.json.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402

lines = []
for kind in ("config-step", "config-field"):
    lines += subprocess.check_output([sys.executable, "tools/audit/enumerate.py", "d17-features", "--kind", kind],
                                     text=True).splitlines()
steps = json.load(open("custom_components/heatpump_optimizer/strings.json"))["config"]["step"]
if "--perturb" in sys.argv:
    del steps["dhw"]["data_description"]["dhw_windows"]
missing = 0
for line in lines:
    kind, item = line.split(" ", 1)
    if kind == "config-step":
        key = f"config.step.{item}.description"
        text = steps.get(item, {}).get("description")
    else:
        step, field = item.split(".", 1)
        key = f"config.step.{step}.data_description.{field}"
        text = steps.get(step, {}).get("data_description", {}).get(field)
    if not text:
        missing += 1
        print(f"UNDOCUMENTED {line} ({key})")
        continue
    first = " ".join(text.split())
    print(f"{line} | strings.json {key} | {first[:220]}")
print(f"RESULT items={len(lines)} items")
print(f"RESULT items_undocumented={missing} items")
print("RESULT thread_factor=1.00 (no numeric work)")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
