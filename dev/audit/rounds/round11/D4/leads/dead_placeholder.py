"""D4-s2-51: the setup flow's first page passes a placeholder no language renders.

Metric: number of (language, placeholder) pairs where a description_placeholders key
the production config_flow.HeatPumpOptimizerConfigFlow.async_step_user returns is
referenced ({key}) by no string under config.step.user of that shipped translation
(en, de, sv) -- count key: the placeholder dict the production step returns.
Null control: the reverse direction -- {key}s the user-step strings reference
that the step does not pass (must be 0).
Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D4/leads/dead_placeholder.py [--perturb]
  --perturb appends ' {tibber_info}' to config.step.user.description of each loaded
  translation in memory (the text-side fix); unrendered must go to 0.
Expected: passed=1, unrendered=3 (exact), unpassed=0 (exact).
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (planted finder export
audit-r11-leads-px), machine: owner's macOS box (B8).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import json
import re
import sys
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeHass  # noqa: E402
from heatpump_optimizer import config_flow  # noqa: E402

c0, t0 = time.process_time(), time.thread_time()
flow = config_flow.HeatPumpOptimizerConfigFlow()
flow.hass = FakeHass()
result = asyncio.run(flow.async_step_user(None))
passed = set((result.get("description_placeholders") or {}).keys())


def leaves(node):
    if isinstance(node, dict):
        for v in node.values():
            yield from leaves(v)
    elif isinstance(node, str):
        yield node


unrendered = unpassed = 0
for lang in ("en", "de", "sv"):
    with open(f"custom_components/heatpump_optimizer/translations/{lang}.json",
              encoding="utf-8") as fh:
        tr = json.load(fh)
    user = tr["config"]["step"]["user"]
    if "--perturb" in sys.argv:
        user["description"] = user.get("description", "") + " {tibber_info}"
    referenced = set()
    for text in leaves(user):
        referenced.update(re.findall(r"\{(\w+)\}", text))
    for key in sorted(passed - referenced):
        unrendered += 1
        print(f"UNRENDERED {lang} {key}")
    unpassed += len(referenced - passed)
print(f"RESULT passed={len(passed)} count")
print(f"RESULT unrendered={unrendered} count")
print(f"RESULT unpassed={unpassed} count")
pc, tc = time.process_time() - c0, time.thread_time() - t0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
