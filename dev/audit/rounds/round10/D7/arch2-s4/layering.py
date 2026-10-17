#!/usr/bin/env python3
"""ARCH2-s4 (round 10, D7): what the persistence boundary imports, and private names crossing modules.

Metric 1: size of the transitive import-time closure (module-level relative imports, TYPE_CHECKING
          and function-scope imports excluded) of store, snapshots, setpoint_check, quiet_windows
          and silent_mode; and whether the solver (optimizer) is in it.
Metric 2: cross-module private imports: names starting with one underscore imported by
          ``from .<module> import`` anywhere in the package (statement-level names, counted).
Seam rule: every ``from .<m> import`` in custom_components/heatpump_optimizer/*.py (this file's walk).
Instrumented symbols: the import statements of the package as Python parses them (ast), on the tree
          at ROOT; with --ref REF the tree is read from git objects at REF.
Command:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s4/layering.py [--ref REF] [--patch P...]
Perturbation: --patch P1_one_utc_clock_owner.patch: the store closure must fall (down) and the solver
          must leave it; the private-import count must fall by the three ``_utc_step_starts`` names.
Expected (baseline 9061fbd3d710, Apple M1, darwin): store 28 with optimizer, private names 17;
          with P1: store 21 without optimizer, private names 14. Exact (static counts).
"""
from __future__ import annotations

import ast
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
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


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tools" / "audit"))
BASELINE = "9061fbd3d710d5894b7083d8a58b8203f9e7aa97"
WATCH = ("store", "snapshots", "setpoint_check", "quiet_windows", "silent_mode")


def graph(pkg: Path):
    mods = {p.stem: p for p in sorted(pkg.glob("*.py"))}
    g, private = {}, 0
    for m, p in mods.items():
        tree = ast.parse(p.read_text())
        skip = set()
        for n in ast.walk(tree):
            if (isinstance(n, ast.If) and "TYPE_CHECKING" in ast.unparse(n.test)) or \
                    isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                skip.update(id(x) for x in ast.walk(n) if x is not n or isinstance(n, ast.If))
        out = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.ImportFrom) and n.level:
                private += sum(1 for a in n.names if a.name.startswith("_") and not a.name.startswith("__"))
                if id(n) in skip:
                    continue
                out.update([n.module.split(".")[0]] if n.module else [a.name for a in n.names])
        g[m] = {o for o in out if o in mods and o != m}
    return g, private


def closure(g, m):
    seen, stack = set(), [m]
    while stack:
        for y in g[stack.pop()]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    seen.discard(m)
    return seen


def main(argv: list[str]) -> int:
    t_cpu, t_thr = time.process_time(), time.thread_time()
    ref = argv[argv.index("--ref") + 1] if "--ref" in argv else BASELINE
    patches = argv[argv.index("--patch") + 1:] if "--patch" in argv else []
    from archscore import score
    with tempfile.TemporaryDirectory(prefix="arch2s4-lay-") as tmp:
        score.tree_of(ref, Path(tmp))
        for p in patches:
            subprocess.run(["git", "apply", "--include=custom_components/*", "--whitespace=nowarn",
                            str((HERE / p).resolve())], cwd=tmp, check=True)
        g, private = graph(Path(tmp) / "custom_components" / "heatpump_optimizer")
    for m in WATCH:
        c = closure(g, m)
        print(f"RESULT closure_{m}={len(c)} modules (optimizer {'IN' if 'optimizer' in c else 'out'})")
    print(f"RESULT private_cross_module_names={private} count")
    cpu, thr = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=n/a (static count; no timing RESULT)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
