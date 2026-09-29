#!/usr/bin/env python3
"""
Verifier's own harness for D6-s1-01, written independently of s1's.

Metric definition (mine, deliberately different from s1's):
For each PEP 508 package name in manifest.json's `requirements`, check (a)
whether the bare name appears anywhere in README.md at all (not just inside
the "## Requirements" section -- a stricter test of "never named" than s1's
section-scoped check), and (b) whether the package is a genuine runtime
dependency, established here by parsing every production .py file's AST and
looking for an `ast.Import`/`ast.ImportFrom` naming the package OR a call to
`importlib.import_module("<package>")` (a literal string match would count
the word appearing in a comment; this requires it to be an actual import
statement or dynamic-import call node, which is a stricter, different check
than s1's plain substring-in-source-text scan).
Command: python3 tools/audit/round8/D6/v1_requirements_gap.py
Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
Perturbation: same as s1 -- add a package to manifest.json requirements not
mentioned anywhere in README and not imported; my anywhere_undocumented
count must increase by 1, and the used_count must NOT change (the added
package is not actually imported).
"""
import ast
import glob
import json
import os
import re

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

manifest = json.load(open("custom_components/heatpump_optimizer/manifest.json", encoding="utf-8"))
reqs = manifest["requirements"]
pkg_names = [re.split(r"[<>=!~\[]", r, 1)[0].strip() for r in reqs]

readme = open("README.md", encoding="utf-8").read().lower()
anywhere_undocumented = [p for p in pkg_names if p.lower() not in readme]

used = []
for f in glob.glob("custom_components/heatpump_optimizer/*.py"):
    try:
        tree = ast.parse(open(f, encoding="utf-8").read(), filename=f)
    except SyntaxError:
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top in pkg_names and top not in used:
                    used.append(top)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                top = node.module.split(".")[0]
                if top in pkg_names and top not in used:
                    used.append(top)
        elif isinstance(node, ast.Call):
            # importlib.import_module("threadpoolctl") style dynamic import
            func = node.func
            is_import_module = (
                (isinstance(func, ast.Attribute) and func.attr == "import_module")
                or (isinstance(func, ast.Name) and func.id == "import_module")
            )
            if is_import_module and node.args and isinstance(node.args[0], ast.Constant):
                val = node.args[0].value
                if isinstance(val, str):
                    top = val.split(".")[0]
                    if top in pkg_names and top not in used:
                        used.append(top)

really_undocumented_and_used = [p for p in anywhere_undocumented if p in used]

print(f"RESULT manifest_requirements_count={len(pkg_names)} packages", pkg_names)
print(f"RESULT anywhere_undocumented_count={len(anywhere_undocumented)} packages", anywhere_undocumented)
print(f"RESULT ast_import_used_count={len(used)} packages", used)
print(f"RESULT anywhere_undocumented_and_used_count={len(really_undocumented_and_used)} packages", really_undocumented_and_used)

load1 = os.getloadavg()[0]
print(f"RESULT load1={load1} load")
print("RESULT thread_factor=1.0 ratio")
