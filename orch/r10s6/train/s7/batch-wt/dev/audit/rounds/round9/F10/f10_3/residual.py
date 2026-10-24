#!/usr/bin/env python3
"""F10.3 barrier residual, re-derived: production `if`/`elif` tests spanning
more than one line, and clamp calls (tests/mutation_table.py:_clamp_call)
spanning more than one line -- the shapes the single-line format does not
reach (tvofi's card C7). Null control: the same count over single-line ones.
"""
import ast, sys
from pathlib import Path
sys.path.insert(0, "tests")
import mutation_table as mt
ml_if = sl_if = ml_cl = sl_cl = tern = 0
for p in sorted(mt.PRODUCTION.rglob("*.py")):
    for n in ast.walk(ast.parse(p.read_text())):
        if isinstance(n, ast.If):
            if n.test.end_lineno > n.test.lineno: ml_if += 1
            else: sl_if += 1
        if isinstance(n, ast.Call) and len(n.args) >= 2 and mt._clamp_call(n.func):
            if n.end_lineno > n.lineno: ml_cl += 1
            else: sl_cl += 1
        if isinstance(n, ast.IfExp): tern += 1
print(f"RESULT multi_line_if_tests={ml_if} count\nRESULT single_line_if_tests={sl_if} count")
print(f"RESULT multi_line_clamps={ml_cl} count\nRESULT single_line_clamps={sl_cl} count")
print(f"RESULT ternaries={tern} count (no operator mutates one)")
