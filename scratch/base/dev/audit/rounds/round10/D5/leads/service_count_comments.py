"""Leads seat (round 10), owner D5-s3, step D5.M4: stated service counts in code comments vs the registry.

Metric: number of count statements in the docstrings and comments of
  custom_components/heatpump_optimizer/{__init__,services}.py of the form
  "<number> services|handlers|``hass.services.async_register`` calls" whose number differs from
  the count of actions __init__._async_register_services actually registers on a FakeHass.
  Only numbers >= 10 are read as whole-registry counts; smaller ones in these files name
  subsets ("one of two services that write to the config entry").
Count key: len(hass.services.async_services()[DOMAIN]) after awaiting the production
  _async_register_services, and the number of FakeServices.async_register calls it made.
Command (from the export root):
  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D5/leads/service_count_comments.py [--perturb]
Expected at baseline 17f1c55fad1b: registered=13, stated_counts=5, stale_count_statements=4 (tolerance 0).
Perturbation (--perturb, in memory): services.async_register_services also registers one extra
  action; registered becomes 14 and stale_count_statements must rise to 5 (the "thirteen" docstring
  goes stale too), i.e. the count follows the registry, not the text.
Seam rule: the regex STATED below over every comment/docstring token of the two files.
Machine: macOS arm64 (leads seat). Counts only, contention-immune.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import io
import re
import sys
import time
import tokenize
from pathlib import Path

sys.path.insert(0, "tests")
sys.path.insert(0, ".")
t0p, t0t = time.process_time(), time.thread_time()

from harness import FakeHass  # noqa: E402
import custom_components.heatpump_optimizer as integ  # noqa: E402
from custom_components.heatpump_optimizer import const  # noqa: E402
from custom_components.heatpump_optimizer import services as svc  # noqa: E402

WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen".split())}
STATED = re.compile(
    r"\b(\d+|" + "|".join(WORDS) + r")\s+(?:services|handlers|``hass\.services\.async_register``\s+calls)\b",
    re.IGNORECASE)

if "--perturb" in sys.argv:
    _orig = svc.async_register_services

    def _plus_one(hass):
        _orig(hass)
        hass.services.async_register(const.DOMAIN, "leads_extra_action", lambda call: None)

    svc.async_register_services = _plus_one

hass = FakeHass()
calls = []
_reg = hass.services.async_register


def _counting(domain, service, handler, schema=None, **kw):
    calls.append(service)
    return _reg(domain, service, handler, schema=schema, **kw)


hass.services.async_register = _counting
asyncio.run(integ._async_register_services(hass))
registered = len(hass.services.async_services().get(const.DOMAIN, {}))

stated = stale = 0
for rel in ("custom_components/heatpump_optimizer/__init__.py",
            "custom_components/heatpump_optimizer/services.py"):
    src = Path(rel).read_text()
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type not in (tokenize.COMMENT, tokenize.STRING):
            continue
        text = " ".join(tok.string.split())
        for m in STATED.finditer(text):
            n = m.group(1).lower()
            n = int(n) if n.isdigit() else WORDS[n]
            if n < 10:  # a subset ("one of two services that ..."), not a registry count
                continue
            stated += 1
            ok = n == registered
            stale += not ok
            print(f"{rel}:{tok.start[0]}+ states '{m.group(0)}' -> {n} vs registered {registered}: {'ok' if ok else 'STALE'}")

print(f"RESULT registered_actions={registered} count")
print(f"RESULT async_register_calls={len(calls)} count")
print(f"RESULT stated_counts={stated} count")
print(f"RESULT stale_count_statements={stale} count")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=na")
