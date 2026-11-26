#!/usr/bin/env python3
"""Enumerator: which D3 wave survivors sit in a function that differs from the wave baseline at REF.

    python3 -I dev/audit/rounds/round11/PLAN/d3_fnstate.py D3-FOLD.json REF [REF...] [--group G] [--ids]

D3-FOLD.json is build_d3_fold.py's output (the fold of the judge record at
a826f55f8c). For each REF it prints, per group, how many survivors' enclosing
functions are byte-identical to the baseline (same), differ (changed), are no
longer defined under that name in that file (gone), or sit at module level
(module: compare the patch text by hand). --ids lists the changed and gone ids.
A fixer runs it at its own merge base: a changed or gone survivor is re-located
by its patch text, never by its line. With two refs (a pull request's merge
base and its head) the difference is what that pull request rewrites.
"""
from __future__ import annotations

import ast
import collections
import json
import subprocess
import sys

PKG = "custom_components/heatpump_optimizer/"
_cache: dict = {}


def functions(ref: str, name: str) -> dict:
    key = (ref, name)
    if key not in _cache:
        run = subprocess.run(["git", "show", f"{ref}:{PKG}{name}"], capture_output=True, text=True)
        out: dict = {}
        if run.returncode == 0:
            lines = run.stdout.splitlines()

            def walk(node, pre):
                for c in ast.iter_child_nodes(node):
                    if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        if not isinstance(c, ast.ClassDef):
                            out[pre + c.name] = "\n".join(lines[c.lineno - 1:c.end_lineno])
                        walk(c, pre + c.name + ".")
                    else:
                        walk(c, pre)
            walk(ast.parse(run.stdout), "")
        _cache[key] = out
    return _cache[key]


def state(base: str, ref: str, name: str, fn: str) -> str:
    if fn == "<module>":
        return "module"
    at = functions(ref, name)
    if fn not in at:
        return "gone"
    return "same" if at[fn] == functions(base, name).get(fn) else "changed"


def main(argv: list[str]) -> int:
    ids = "--ids" in argv
    only = argv[argv.index("--group") + 1] if "--group" in argv else None
    args = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] != "--group")]
    fold = json.load(open(args[0]))
    for ref in args[1:]:
        total: collections.Counter = collections.Counter()
        for group, entry in sorted(fold["groups"].items()):
            if only and group != only:
                continue
            count: collections.Counter = collections.Counter()
            moved = []
            for row in entry["findings"]:
                s = state(fold["baseline"], ref, row["file"], row["fn"])
                count[s] += 1
                if s in ("changed", "gone"):
                    moved.append(f"{row['id']} {row['file']} {row['fn']} {s}")
            total.update(count)
            print(f"{ref} {group}: " + " ".join(f"{k} {count[k]}" for k in ("same", "changed", "gone", "module")))
            if ids:
                for line in moved:
                    print("  " + line)
        print(f"{ref} total: " + " ".join(f"{k} {total[k]}" for k in ("same", "changed", "gone", "module")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
