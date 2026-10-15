"""R10 I1 sweep: does the short-input block in tests/features.py kill every
`<seq> and i < len(<seq>)` guard the round-10 I1 sweep enumerated?

Metric: every BoolOp `and` in custom_components/heatpump_optimizer with an
operand `<x> < len(<seq>)` (the sweep's LEN family, the rule of
dev/audit/rounds/round10/D14/sweep-I1/enumerate_i1.py) is flipped to `or` in a
copy of the package, one site per arm, and the block of tests/features.py
headed "R10 I1 sweep" -- which builds every fixture it reads -- runs against
that copy in a fresh interpreter. A site is KILLED when the block has a failing
check or raises. get_current_action's twelve sites are a separate block's
(dev/audit/harnesses/r10_i1_action_guards.py) and are reported, not counted.
Null: --null runs every arm with no flip (killed 0).

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_i1_sweep_guards.py [--null]
"""
def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")

import ast
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = str(repo_root(__file__))
PKG = os.path.join(ROOT, "custom_components", "heatpump_optimizer")
NULL = "--null" in sys.argv
OWN_BLOCK = "get_current_action"

RUNNER = r'''
import sys
root, pkg_parent = sys.argv[1], sys.argv[2]
sys.path[:0] = [root + "/tests/hastub", root + "/tests"]
from datetime import datetime, timedelta, timezone
import numpy as np
from harness import Results  # puts custom_components first on sys.path
for name in [m for m in sys.modules if m.split(".")[0] == "heatpump_optimizer"]:
    del sys.modules[name]
sys.path.insert(0, pkg_parent)
import heatpump_optimizer
assert heatpump_optimizer.__file__.startswith(pkg_parent), heatpump_optimizer.__file__
src = open(root + "/tests/features.py").read()
block = src[src.index("# R10 I1 sweep: every per-step"):src.index("# The seam rule, as a barrier (R8-P3;")]
R = Results("sweep block")
exec(block, {"R": R, "np": np, "datetime": datetime, "timedelta": timedelta, "timezone": timezone})
sys.exit(1 if R.failures else 0)
'''


def _is_len_cmp(n):
    return (isinstance(n, ast.Compare) and len(n.ops) == 1
            and isinstance(n.ops[0], ast.Lt) and isinstance(n.comparators[0], ast.Call)
            and getattr(n.comparators[0].func, "id", None) == "len")


def seams():
    out = []
    for name in sorted(os.listdir(PKG)):
        if not name.endswith(".py"):
            continue
        tree = ast.parse(open(os.path.join(PKG, name)).read())
        owner = {}
        for fn in ast.walk(tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for n in ast.walk(fn):
                    owner.setdefault(id(n), fn.name)
        for n in ast.walk(tree):
            if isinstance(n, ast.BoolOp) and isinstance(n.op, ast.And) and any(
                    _is_len_cmp(v) for v in n.values):
                out.append((name, n.lineno, owner.get(id(n), "<module>")))
    return out


def flipped(name, line):
    tree = ast.parse(open(os.path.join(PKG, name)).read())
    for n in ast.walk(tree):
        if (isinstance(n, ast.BoolOp) and isinstance(n.op, ast.And) and n.lineno == line
                and any(_is_len_cmp(v) for v in n.values)):
            n.op = ast.Or()
            return ast.unparse(tree)
    raise RuntimeError(f"no LEN seam at {name}:{line}")


killed = counted = 0
with tempfile.TemporaryDirectory() as tmp:
    for name, line, symbol in seams():
        copy = os.path.join(tmp, "heatpump_optimizer")
        shutil.rmtree(copy, ignore_errors=True)
        shutil.copytree(PKG, copy, ignore=shutil.ignore_patterns("__pycache__"))
        if not NULL:
            with open(os.path.join(copy, name), "w") as fh:
                fh.write(flipped(name, line))
        rc = subprocess.run([sys.executable, "-c", RUNNER, ROOT, tmp],
                            capture_output=True, text=True).returncode
        dead = rc != 0
        own = symbol == OWN_BLOCK
        if not own:
            counted += 1
            killed += dead
        print(f"{name}:{line} {symbol:32s} {'KILLED' if dead else 'survived'}"
              + ("  (get_current_action: not this block's)" if own else ""))
print(f"RESULT sites={counted} killed={killed} null={NULL}")
