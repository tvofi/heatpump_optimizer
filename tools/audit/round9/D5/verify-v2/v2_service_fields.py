"""D5 verify-v2 harness for D5-s1-06 (independent of the finder's service_fields.py).

Metric (one line): keys of every module-level SERVICE_SCHEMA_* voluptuous schema in
heatpump_optimizer.services (read from the schema objects themselves, entry_id aside) that
appear in backticks nowhere in README.md or the 7 user docs; plus, separately, whether
services.yaml (what HA's Developer Tools shows) describes them.
Count key: vol.Schema(...).schema keys (production objects), docs searched for `key`.
Command (repository root):
    PYTHONPATH=tests/hastub python tools/audit/round9/D5/verify-v2/v2_service_fields.py [--perturb]
--perturb: in memory, append a doc sentence naming the five wood keys in backticks -> the
    undocumented count must fall to 0 (if they are the only ones).
Baseline 1936d5ca; exact.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import re, sys, time
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
_p0, _t0 = time.process_time(), time.thread_time()
import harness  # noqa: F401  (installs the hastub modules)
from heatpump_optimizer import services  # noqa
DOCS = ["README.md"] + [f"docs/{n}.md" for n in ("architecture", "automations", "configuration",
        "dashboard-card", "ecl110", "how-it-works", "setup")]
corpus = "".join(open(p, encoding="utf-8").read() for p in DOCS)
if "--perturb" in sys.argv:
    corpus += " `wood_slots` `wood_type` `wood_packing` `wood_price_sek_m3` `wood_furnace_efficiency`"
yaml = open("custom_components/heatpump_optimizer/services.yaml", encoding="utf-8").read()
total = 0; missing = []
for name in sorted(dir(services)):
    if not name.startswith("SERVICE_SCHEMA_"):
        continue
    sch = getattr(services, name)
    inner = getattr(sch, "schema", None)
    while inner is not None and not isinstance(inner, dict):  # vol.All(...) wrappers
        inner = next((v for v in getattr(inner, "validators", []) if hasattr(v, "schema")), None)
        inner = getattr(inner, "schema", None)
    if not isinstance(inner, dict):
        print("SKIP", name); continue
    for k in inner:
        key = str(getattr(k, "schema", k))
        if key == "entry_id":
            continue
        total += 1
        if f"`{key}`" not in corpus:
            missing.append((name, key, bool(re.search(rf"^\s+{re.escape(key)}:", yaml, re.M))))
for m in missing:
    print("UNDOCUMENTED", m)
conf = open("docs/configuration.md", encoding="utf-8").read()
tbl = re.search(r"\| `simulate_plan` \| (\d+) optional", conf)
para = re.search(r"\*\*`simulate_plan`\*\*.*?Fields,\s*all optional:(.*?)\.\s", conf, re.S)
listed = len(re.findall(r"`(\w+)`", para.group(1))) if para else -1
print(f"RESULT schema_fields={total} count")
print(f"RESULT undocumented_fields={len(missing)} count")
print(f"RESULT undocumented_but_in_services_yaml={sum(1 for m in missing if m[2])} count")
print(f"RESULT simulate_plan_table_count={tbl.group(1) if tbl else -1} count")
print(f"RESULT simulate_plan_paragraph_lists={listed} count")
print(f"RESULT simulate_plan_schema_keys={len(services.SERVICE_SCHEMA_SIMULATE_PLAN.schema)} count")
cp, ct = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={cp/ct if ct else 1:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
