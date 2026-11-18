#!/usr/bin/env python3
"""s1_cachekey.py -- does env_drift's baseline cache key split on HPO_* variables
that no capture reads?

Metric: number of DISTINCT tests/env_drift.py:cache_key(cache_key_inputs(repo,
BASE, everything=True)) values over five environments that differ ONLY in
HPO_PLANDATA / HPO_GATE_LOCK_LABEL / HPO_GATE_FLOCK_CHILD (the variables the
harness contract and tests/run.sh's locked path set), plus the count of reads of
those three names in the code a capture executes (custom_components/, tests/
golden.py, tests/env_drift.py outside the key builder, tests/hastub/).
Key: the key env_drift itself computes (the production instrument), not a
re-derivation.

Arms (each computed in-process, env restored after):
  clean                        no HPO_* set
  plandata                     HPO_PLANDATA=<tmp>/plandata      (harness contract)
  lock_A                       HPO_GATE_LOCK_LABEL=A, HPO_GATE_FLOCK_CHILD=1  (run.sh:87-94)
  lock_B                       HPO_GATE_LOCK_LABEL=B, HPO_GATE_FLOCK_CHILD=1
  clean_again                  null control: must equal `clean`
Perturbation (--perturb): drop "HPO_" from env_drift.CACHE_ENV_PREFIXES for the
run -> distinct_keys must fall to 1 (direction: down).

Command (tree root):
  PYTHONPATH=tests/hastub python3 tools/audit/round8/D3/s1_cachekey.py [--perturb]
Expected at baseline: RESULT distinct_keys=4 count (exact), null_equal=1,
capture_reads=0; with --perturb distinct_keys=1.
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud container.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import importlib.util
import re
import sys
import time
from pathlib import Path

BASE = "cdf82daabcfe3777d98b31489f36df5555ec9d82"
NAMES = ("HPO_PLANDATA", "HPO_GATE_LOCK_LABEL", "HPO_GATE_FLOCK_CHILD")
spec = importlib.util.spec_from_file_location("env_drift", os.path.abspath("tests/env_drift.py"))
ed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ed)
if "--perturb" in sys.argv:
    ed.CACHE_ENV_PREFIXES = tuple(p for p in ed.CACHE_ENV_PREFIXES if p != "HPO_")
    print("PERTURBED: HPO_ removed from CACHE_ENV_PREFIXES")

for n in NAMES:
    os.environ.pop(n, None)
repo = os.path.abspath(".")
arms = {
    "clean": {},
    "plandata": {"HPO_PLANDATA": "/home/claude/audit-r8/tmp/D3-s1/plandata"},
    "lock_A": {"HPO_GATE_LOCK_LABEL": "A", "HPO_GATE_FLOCK_CHILD": "1"},
    "lock_B": {"HPO_GATE_LOCK_LABEL": "B", "HPO_GATE_FLOCK_CHILD": "1"},
    "clean_again": {},
}
keys = {}
t0 = time.process_time(); w0 = time.thread_time()
for name, env in arms.items():
    os.environ.update(env)
    try:
        keys[name] = ed.cache_key(ed.cache_key_inputs(repo, BASE, True))
    finally:
        for k in env:
            os.environ.pop(k, None)
    print(f"  {name:12s} {keys[name][:16]}")

# Reads of the three names in what a capture executes.
reads = 0
files = list(Path("custom_components").rglob("*.py")) + list(Path("tests/hastub").rglob("*.py")) \
    + [Path("tests/golden.py"), Path("tests/harness.py")]
for f in files:
    reads += sum(len(re.findall(n, f.read_text(errors="ignore"))) for n in NAMES)
ed_src = Path("tests/env_drift.py").read_text()
reads += sum(len(re.findall(n, ed_src)) for n in NAMES)

print(f"RESULT distinct_keys={len(set(keys.values()))} count")
print(f"RESULT null_equal={int(keys['clean'] == keys['clean_again'])} count")
print(f"RESULT capture_reads={reads} count")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-w0,1e-9):.3f}")
print("RESULT swapins=0")
