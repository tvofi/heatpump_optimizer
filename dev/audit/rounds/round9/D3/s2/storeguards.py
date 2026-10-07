#!/usr/bin/env python3
"""D3-s2 round 9 seam rule for D3-s2-01: enumerate the store-boundary guard sites in scope.

Metric: every GUARD_OFF / RETURN_DEL / EXCEPT_RAISE site (pool.py's inventory, i.e.
  tests/mutation_table.py:candidates plus pool.py's extra operators) whose enclosing function is a
  persisted-state parser -- a classmethod/function named from_dict, from_store, _from_dict,
  restore*, load*, _grid_of, _stored_peaks -- in the eight D3-s2 modules. Writes storeguards.json (a pool file prescreen.py
  can drive with D3S2_POOL=storeguards.json).
Command:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D3/s2/storeguards.py
Expected: RESULT store_guard_sites=<n> sites (exact at the baseline).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B2.
Instrumented symbol: tests/mutation_table.py:candidates over the eight modules.
Perturbation: adding a parser name to PARSERS (or a guard to a from_dict) raises the count.
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pool  # noqa: E402

PARSERS = re.compile(r"^(_?from_dict|from_store|_?restore\w*|_?load\w*|_grid_of|_stored_peaks)$")
KINDS = {"GUARD_OFF", "RETURN_DEL", "EXCEPT_RAISE", "NP_CLIP", "CLAMP_DROP"}


def enclosing(tree):
    spans = []
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            spans.append((n.lineno, n.end_lineno, n.name))
    return spans


def main() -> int:
    inv = pool.inventory()
    out = []
    cache = {}
    for m in inv:
        if m["kind"] not in KINDS:
            continue
        if m["file"] not in cache:
            cache[m["file"]] = enclosing(ast.parse((pool.ROOT / m["file"]).read_text()))
        names = [nm for a, b, nm in cache[m["file"]] if a <= m["line"] <= b]
        if any(PARSERS.match(nm) for nm in names):
            m = dict(m, parser=names[0] if names else "")
            out.append(m)
    for i, m in enumerate(out, 1):
        m["id"] = f"S{i:02d}"
        print(f"{m['id']} {m['kind']:12s} {m['file'].split('/')[-1]}:{m['line']} [{m['parser']}] {m['old'].strip()[:70]}")
    (pool.HERE / "storeguards.json").write_text(json.dumps({"pool": out}, indent=1, sort_keys=True) + "\n")
    print(f"RESULT store_guard_sites={len(out)} sites")
    return 0


if __name__ == "__main__":
    sys.exit(main())
