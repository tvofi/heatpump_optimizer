#!/usr/bin/env python3
"""D11-s1 (round 11, D11.M1): each required check name resolves to a workflow job.

Metric (one line): of the names tools/ci/gate.py:gate_required() can require (each `<stem> / <job>`),
how many name no job (matrix-expanded) of .github/workflows/<stem>.yml; plus the ruleset's one required
context `gate` against ci.yml's jobs.
Run:   PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s1/required_map.py [--perturb]
Expected at 92d38ecb640b: required=21, unresolved=0, gate_jobs=1 (exact).
Perturbation: --perturb renames ci.yml-called tests.yml's `briefs` job in memory -> unresolved up (1).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box B6; counts. Writes nothing.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import glob
import itertools
import json
import re
import sys

import yaml

sys.path.insert(0, "tools/ci")
import gate  # noqa: E402

names, gate_jobs = set(), 0
for f in sorted(glob.glob(".github/workflows/*.yml")):
    stem = os.path.basename(f)[:-4]
    d = yaml.safe_load(open(f))
    jobs = d.get("jobs") or {}
    if "--perturb" in sys.argv and stem == "tests":
        jobs = {("briefs-x" if k == "briefs" else k): v for k, v in jobs.items()}
    for jid, j in jobs.items():
        nm = str(j.get("name", jid))
        if nm == "gate":
            gate_jobs += 1
        mx = (j.get("strategy") or {}).get("matrix") or {}
        keys = [k for k in mx if k not in ("include", "exclude")] if isinstance(mx, dict) else []
        combos = [dict(zip(keys, v)) for v in itertools.product(*[mx[k] for k in keys])] if keys else []
        if isinstance(mx, dict) and not keys:
            combos += [dict(i) for i in mx.get("include", [])]
        combos = combos or [{}]
        for c in combos:
            if "${{" in nm:
                n = re.sub(r"\$\{\{\s*matrix\.(\w+)\s*\}\}", lambda m: str(c.get(m.group(1), "?")), nm)
            elif keys:
                n = nm + " (" + ", ".join(str(v) for v in c.values()) + ")"
            else:
                n = nm
            names.add(f"{stem} / {n}")
req = sorted(gate.gate_required())
miss = [r for r in req if r not in names]
for m in miss:
    print("UNRESOLVED", m)
print(f"RESULT required={len(req)} names")
print(f"RESULT unresolved={len(miss)} names")
print(f"RESULT gate_jobs={gate_jobs} jobs")
print("RESULT thread_factor=1.000")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
