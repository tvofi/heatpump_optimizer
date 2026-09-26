#!/usr/bin/env python3
"""Leads seat L2, round 9 (D6-s2 cell, docs/setup.md:4-5): how many pages the full wizard shows.

METRIC (one line): screens the initial ConfigFlow shows from `user` to create_entry on the
  full-wizard route ("Continue setup"), each page submitted as pre-filled, per building
  choice (describe / thermal), counted on the flow's own step_ids -- at the pre-Quick-setup
  release v6.6.4 (what docs/setup.md calls "the original eleven-page wizard") and at the tree
  under test. Also: the RELEASE_NOTES.md heading that carries #1251 (the quick-setup path).
KEY: the step_id of every form/menu result the production async_step_<page> returns.
RUN (export root):
  HPO_BASELINE_GIT=/home/claude/heatpump_optimizer PYTHONPATH=tests/hastub \
    /home/claude/venv314/bin/python tools/audit/round9/D6/leads/l2_wizard_pages.py
  (--ref <tag>, default v6.6.4, is git-archived into a tempfile.mkdtemp() root and walked with
  its own tests/hastub in a child process; without HPO_BASELINE_GIT only the tree under test
  is walked.)
PERTURBATION: --with-offer  config_flow's device pre-fill offer is forced on (the stored offer
  switch and prefill_offer.offered patched to True in memory, where the tree has them) -> every
  route shows the device_prefill page: screens go UP by 1 in each tree that has the offer.
EXPECTED at 1936d5ca72a06556eeed4e8e5bf3dea520e517e1: see LEADS-L2.md; exact counts.
MACHINE: leads box, 4-core Linux container.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import re, subprocess, sys, tempfile, time

P0, T0 = time.process_time(), time.thread_time()
SKIP = "--with-offer" in sys.argv
REF = sys.argv[sys.argv.index("--ref") + 1] if "--ref" in sys.argv else "v6.6.4"

WALKER = r'''
import asyncio, sys, logging
sys.path[:0] = ["tests", "tests/hastub", "custom_components"]
logging.disable(logging.CRITICAL)
from harness import FakeHass
from heatpump_optimizer import config_flow as cf, const
SKIP = SKIPFLAG
if SKIP:
    if hasattr(cf, "_prefill_offer_stored"):
        cf._prefill_offer_stored = lambda hass: True
    if hasattr(cf, "prefill_offer"):
        cf.prefill_offer.offered = lambda records: True

def prefilled(r):
    out = {}
    schema = r.get("data_schema")
    for key in (schema.schema if schema else {}):
        try:
            out[str(key.schema)] = key.default()
        except Exception:
            pass
    return out

async def walk(building):
    f = cf.HeatPumpOptimizerConfigFlow()
    f.hass = FakeHass()
    seen = ["user"]
    r = await f.async_step_user({"name": "HPO", const.CONF_PRICE_SOURCE: "entity",
                                 const.CONF_PRICE_ENTITY: "sensor.nordpool",
                                 const.CONF_WEATHER_ENTITY: "weather.home"}) \
        if hasattr(const, "CONF_PRICE_SOURCE") else None
    while r.get("type") in ("form", "menu"):
        step = r["step_id"]
        seen.append(step)
        if len(seen) > 40:
            return seen, "loop"
        if r["type"] == "menu":
            if step == "finish_setup":
                choice = "finish_now" if seen.count("finish_setup") > 1 else "temperature"
            elif step == "building":
                choice = building
            else:
                return seen, "menu:" + step
            r = await getattr(f, "async_step_" + choice)()
            continue
        if step == "device_prefill":
            r = await f.async_step_device_prefill({cf._PREFILL_DEVICE: None})
            continue
        r = await getattr(f, "async_step_" + step)(prefilled(r))
    return seen, r.get("type")

for b in ("building_describe", "thermal"):
    seen, end = asyncio.run(walk(b))
    print("# " + b + ": " + " -> ".join(seen) + " -> " + str(end))
    print("SCREENS " + b + " " + str(len(seen)) + " " + str(end))
'''


def run_tree(root: str) -> dict:
    code = WALKER.replace("SKIPFLAG", "True" if SKIP else "False")
    env = dict(os.environ, PYTHONPATH="tests/hastub")
    out = subprocess.run([sys.executable, "-c", code], cwd=root, env=env,
                         capture_output=True, text=True, timeout=600)
    sys.stdout.write("".join(l + "\n" for l in out.stdout.splitlines() if l.startswith("#")))
    if out.returncode:
        sys.stdout.write(out.stderr[-2000:])
    res = {}
    for line in out.stdout.splitlines():
        if line.startswith("SCREENS"):
            _, b, n, end = line.split()
            res[b] = (int(n), end)
    return res


trees = {"tree": "."}
git = os.environ.get("HPO_BASELINE_GIT")
if git:
    tmp = tempfile.mkdtemp(prefix="l2wiz-")
    arch = subprocess.run(["git", "-C", git, "archive", REF], capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", tmp], input=arch, check=True)
    trees[REF] = tmp
for label, root in trees.items():
    res = run_tree(root)
    for b, (n, end) in res.items():
        short = "describe" if b == "building_describe" else "thermal"
        tag = label.replace(".", "_")
        print(f"RESULT screens_{short}_{tag}={n} count (ends {end})")

notes = open("RELEASE_NOTES.md").read()
head, where = None, None
for line in notes.splitlines():
    if line.startswith("## "):
        head = line[3:].strip()
    if re.match(r"- #1251\b", line):
        where = head
print(f"RESULT quick_setup_pr1251_release={where}")
_p, _t = time.process_time() - P0, time.thread_time() - T0
print(f"RESULT thread_factor={(_p / _t) if _t > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")]
    print(f"RESULT swapins={_sw[0].split()[1] if _sw else 0}")
except OSError:
    print("RESULT swapins=na")
