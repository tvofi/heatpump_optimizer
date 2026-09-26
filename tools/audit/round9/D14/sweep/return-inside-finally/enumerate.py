#!/usr/bin/env python3
"""D14 sweep, class "return inside finally" (PEP 765 hazard: a return/break/continue directly in
a finally clause discards an in-flight exception from the try it closes).
Finding: D7-s3-51 (verified, low -- tests/nightly_ha.py:_async_check_a4 returns from inside a
finally block; on CPython 3.14 this is a SyntaxWarning; of 2 arms where the broken-price refresh
raises a BaseException the try does not catch and the recovery refresh also raises, both arms
return normally instead of propagating -- swallowed=2 of 2).
This box's default python3 (3.11.15) predates PEP 765's SyntaxWarning (3.14+), so this enumerator
uses an AST walk instead of --W error::SyntaxWarning: it widens the seam rule from
tests/nightly_ha.py alone to every .py file under tests/, custom_components/heatpump_optimizer/
and tools/, and distinguishes a `return` (always escapes the finally, whatever its nesting) from a
`break`/`continue` (escapes only if not already caught by a loop nested inside the same finally).
"""
import ast
import glob

def hazards(path):
    src = open(path, encoding="utf-8").read()
    try:
        tree = ast.parse(src, path)
    except SyntaxError:
        return []
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        for stmt in node.finalbody:
            for sub in ast.walk(stmt):
                if isinstance(sub, ast.Return):
                    out.append((path, sub.lineno, "return", True))
                elif isinstance(sub, (ast.Break, ast.Continue)):
                    # only a hazard if no enclosing loop inside the finally catches it first
                    enclosing_loop = False
                    for anc in ast.walk(stmt):
                        if isinstance(anc, (ast.For, ast.While)) and sub in ast.walk(anc) and anc is not sub:
                            if any(sub is d for d in ast.walk(anc)) and anc.body and stmt is not sub:
                                enclosing_loop = True
                    out.append((path, sub.lineno, type(sub).__name__.lower(), not enclosing_loop))
    return out

if __name__ == "__main__":
    for pattern in ["tests/*.py", "custom_components/heatpump_optimizer/*.py", "tools/**/*.py"]:
        for f in sorted(glob.glob(pattern, recursive=True)):
            for path, lineno, kind, escapes in hazards(f):
                print(f"SEAM {path}:{lineno} {kind} escapes_finally={escapes}")
