#!/usr/bin/env python3
"""Reviewer-built: run tests/entities.py header + the D10-08..D10-12 sections only.
    python entities_slice.py <tree>"""
import os, sys
tree = os.path.abspath(sys.argv[1]); os.chdir(tree)
sys.path[:0] = [os.path.join(tree, p) for p in ("tests/hastub", "custom_components", "tests")]
path = os.path.join(tree, "tests/entities.py")
lines = open(path, encoding="utf-8").read().split("\n")
hdr_end = next(i for i, l in enumerate(lines) if l.startswith('R = Results('))
start = next(i for i, l in enumerate(lines) if 'R.section("Reauthentication (D10-08)")' in l)
end = next(i for i, l in enumerate(lines) if i > start and l.startswith("# The snapshot's wiring, at the values"))
mid = next(i for i, l in enumerate(lines) if i > start and l.startswith("R.section(") and "Coordinator config_entry" in l)
diag = next(i for i, l in enumerate(lines) if l.startswith('R.section("Diagnostics (D10-12)")'))
src = ("\n".join(lines[: hdr_end + 1]) + "\n" * (start - hdr_end) + "\n".join(lines[start:mid])
       + "\n" * (diag - mid) + "\n".join(lines[diag:end]))
ns = {"__file__": path, "__name__": "slice"}
exec(compile(src, path, "exec"), ns)
sys.exit(ns["R"].close("ENTITY SLICE"))
