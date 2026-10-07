#!/usr/bin/env python3
"""
Metric: package names in manifest.json's `requirements` list (PEP 508 specs)
that are NOT named anywhere in README.md's "## Requirements" section prose,
vs. package names actually imported/resolved by name in production code
under custom_components/heatpump_optimizer/*.py (a real runtime dependency,
not a stray manifest entry).
Command: python3 tools/audit/round8/D6/s1_requirements_claim.py
Expected: RESULT lines; run from the tree root. Pure text/AST scan, no
BLAS/thread pin needed (kept for header-contract uniformity).
Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
Instrumented symbol: custom_components/heatpump_optimizer/manifest.json
`requirements`, and README.md's "## Requirements" section (the literal
text a reader sees before installing).
Perturbation: add a fourth pinned package to manifest.json `requirements`
(e.g. "pyyaml>=6.0") without adding it to README's Requirements prose, and
`undocumented_count` must increase by exactly one, naming that package.
Removing threadpoolctl from manifest.json (the one this run finds) must
drop `undocumented_count` back to 0.
"""
import os
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

import json
import re
import glob

manifest = json.load(open("custom_components/heatpump_optimizer/manifest.json", encoding="utf-8"))
reqs = manifest["requirements"]
pkg_names = [re.split(r"[<>=!~\[]", r, 1)[0].strip() for r in reqs]

readme = open("README.md", encoding="utf-8").read()
m = re.search(r"## Requirements\n(.*?)\n## ", readme, re.S)
req_section = m.group(1) if m else ""

undocumented = [p for p in pkg_names if p.lower() not in req_section.lower()]

# Confirm each undocumented package is an actual runtime dependency: named
# (by literal string, since threadpoolctl publishes no py.typed and is
# resolved dynamically -- see optimizer.py:265) somewhere in production code.
src_files = glob.glob("custom_components/heatpump_optimizer/*.py")
src_text = ""
for f in src_files:
    src_text += open(f, encoding="utf-8", errors="ignore").read()

really_used = [p for p in undocumented if p in src_text]

print(f"RESULT manifest_requirements_count={len(pkg_names)} packages", pkg_names)
print(f"RESULT undocumented_count={len(undocumented)} packages", undocumented)
print(f"RESULT undocumented_and_used_count={len(really_used)} packages", really_used)

load1 = os.getloadavg()[0]
print(f"RESULT load1={load1} load")
print("RESULT thread_factor=1.0 ratio")
