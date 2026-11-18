"""D5-s1 harness: identifiers the user docs name in `code` spans, against the shipped code.

Metric (one line): inline-code identifiers in README.md + the seven user docs (outside
fences; dotted, call-form, CamelCase or snake_case; file names, paths and entity ids
excluded) with a part that is no module, def, class, attribute, argument, keyword, name or
string/word literal in custom_components/heatpump_optimizer/*.py, its *.json,
services.yaml or the bundled card.
Count key: the AST of the production package (ast.walk over every module), not grep of
the docs against themselves.
Command (from the repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D5/s1/doc_symbols.py [--perturb]
--perturb drops, in memory, the def/attribute name "marginal_cop" and the word from the
    literal pool, as a rename of ThermalModel.marginal_cop would. Expected: missing up (0 -> >=1).
Expected at baseline: missing=1 (how-it-works "direct_radiation", named as what the code
deliberately does NOT request -- a true negative mention, not stale), exact.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B1 (linux container).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast
import pathlib
import re
import sys
import time

_t0p, _t0t = time.process_time(), time.thread_time()
PKG = pathlib.Path("custom_components/heatpump_optimizer")
names, lits = set(), set()
for p in PKG.glob("*.py"):
    for n in ast.walk(ast.parse(p.read_text(encoding="utf-8"))):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(n.name)
        elif isinstance(n, ast.arg):
            names.add(n.arg)
        elif isinstance(n, ast.Name):
            names.add(n.id)
        elif isinstance(n, ast.Attribute):
            names.add(n.attr)
        elif isinstance(n, ast.keyword) and n.arg:
            names.add(n.arg)
        elif isinstance(n, ast.Constant) and isinstance(n.value, str):
            lits.add(n.value)
            lits.update(re.findall(r"\w+", n.value))
for extra in [*PKG.glob("*.json"), PKG / "services.yaml", PKG / "www/heatpump-optimizer-card.js"]:
    lits.update(re.findall(r"\w+", extra.read_text(encoding="utf-8")))
mods = {p.stem for p in PKG.glob("*.py")}
if "--perturb" in sys.argv:
    names.discard("marginal_cop")
    lits.discard("marginal_cop")

DOCS = ["README.md"] + [f"docs/{n}.md" for n in (
    "architecture", "automations", "configuration", "dashboard-card", "ecl110",
    "how-it-works", "setup")]
SKIP_DOMAINS = {"sensor", "switch", "binary_sensor", "number", "climate", "heatpump_optimizer",
                "input_number", "weather", "mqtt", "notify", "input_boolean",
                "device_tracker", "person", "calendar"}
checked, missing = 0, []
for path in DOCS:
    fence = False
    for i, line in enumerate(open(path, encoding="utf-8").read().split("\n"), 1):
        if line.startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        for m in re.finditer(r"`([^`\s]+)`", line):
            s = m.group(1)
            if re.search(r"\.(py|md|json|yaml|toml|js|mjs|txt)$", s) or "/" in s or ":" in s:
                continue
            if not re.fullmatch(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*(?:\(\))?", s):
                continue
            if "_" not in s and "." not in s and "(" not in s and not re.fullmatch(r"[A-Z][a-z]+[A-Z]\w+", s):
                continue
            parts = s.rstrip("()").split(".")
            if parts[0] in SKIP_DOMAINS:
                continue
            checked += 1
            if not all(p in names or p in mods or p in lits for p in parts):
                missing.append(f"{path}:{i} {s}")
for m in missing:
    print("missing", m)
cpu_p, cpu_t = time.process_time() - _t0p, time.thread_time() - _t0t
print(f"RESULT identifiers_checked={checked} count")
print(f"RESULT missing={len(missing)} count")
print(f"RESULT thread_factor={cpu_p / cpu_t if cpu_t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
