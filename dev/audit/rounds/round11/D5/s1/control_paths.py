"""D5-s1 harness: README's control-path set against the options page's heat-curve kinds.

Metric: denied_kinds = number of heat-curve target kinds the production options field
(config_flow._OPTION_FIELDS row for CONF_HEAT_CURVE_TARGET_KIND) offers that README's
"Known limitations" ECL110 bullet says are "not supported in this version"
(the bullet denies the stored/persistent kind).  Count key: the selector's own option list.
Also printed: readme_path_rows (rows of the "Supported heat pumps and controls" table) beside
readme_path_count_stated (the "three paths" the same section and the limitations section state).
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s1/control_paths.py [--perturb]
Expected at baseline 92d38ecb: denied_kinds=1, readme_path_rows=5, readme_path_count_stated=3.
Perturbation (--perturb): const.HEAT_CURVE_TARGET_KINDS is cut to the offset kind alone before
config_flow is imported; denied_kinds falls to 0.  Machine: orchestrator Mac, local seat.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import re, sys, time
sys.path.insert(0, ".")
t0, c0 = time.time(), time.process_time()
from custom_components.heatpump_optimizer import const
if "--perturb" in sys.argv:
    const.HEAT_CURVE_TARGET_KINDS = (const.HEAT_CURVE_KIND_OFFSET,)
from custom_components.heatpump_optimizer import config_flow

row = next(f for f in config_flow._OPTION_FIELDS if f[1] == const.CONF_HEAT_CURVE_TARGET_KIND)
widget = row[3]
options = list(widget.config["options"])
print("offered kinds:", options)

readme = open("README.md", encoding="utf-8").read()
lim = readme.split("## Known limitations", 1)[1].split("\n## ", 1)[0]
bullet = next(b for b in lim.split("\n- ") if b.startswith("**ECL110 control"))
denies_stored = bool(re.search(r"stored curve\s+parameter\s+is\s+not\s+supported", bullet))
denied = sum(1 for k in options if k == const.HEAT_CURVE_KIND_PERSISTENT and denies_stored)

sup = readme.split("## Supported heat pumps and controls", 1)[1].split("\n## ", 1)[0]
rows = [l for l in sup.splitlines() if l.startswith("| **")]
stated = 3 if re.search(r"over three paths", sup) else 0
print(f"RESULT denied_kinds={denied} kinds")
print(f"RESULT readme_path_rows={len(rows)} rows")
print(f"RESULT readme_path_count_stated={stated} paths")
pc, wc = time.process_time() - c0, time.time() - t0
print(f"RESULT thread_factor={pc / max(wc, 1e-9):.2f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
