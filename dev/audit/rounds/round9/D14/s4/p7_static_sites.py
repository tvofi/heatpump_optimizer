#!/usr/bin/env python3
"""P7 static complement: every candidate datetime-arithmetic site in the package,
and which of them the run-time detector (p7_dst_seams.py) actually reached.

METRIC (one line): `candidates` = BinOp Sub/Add nodes in
custom_components/heatpump_optimizer/*.py where one operand's source mentions a
clock/datetime name (dt_util.now/utcnow/as_local, datetime, timedelta, .replace(
hour=..., or an identifier ending in _at/_time/time/when/now/stamp/start/
midnight/since/until/last); `reached` = those whose file:line the run-time
detector recorded (tools/audit/round9/D14/s4/out/p7_zoneinfo.json).
The heuristic is a seam LIST for a reviewer to walk, not a verdict: an
unreached candidate is a site the synthetic day did not drive, not a clean one.

COMMAND (repository root, after p7_dst_seams.py --json .../out/p7_zoneinfo.json):
  /home/claude/venv314/bin/python tools/audit/round9/D14/s4/p7_static_sites.py
Exact integers; no BLAS; Linux container (box B9); baseline 1936d5ca.
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

PKG = Path("custom_components/heatpump_optimizer")
RUN = Path(__file__).resolve().parent / "out" / "p7_zoneinfo.json"
PAT = re.compile(r"dt_util\.(now|utcnow|as_local)|\bdatetime\b|timedelta|replace\(\s*hour"
                 r"|\b\w*(_at|_time|time|when|now|stamp|start|midnight|since|until|last)\b", re.I)


def main() -> int:
    reached = set()
    if RUN.exists():
        for s in json.loads(RUN.read_text())["sites"]:
            reached.add((s["file"], s["line"]))
    rows = []
    for f in sorted(PKG.glob("*.py")):
        src = f.read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Sub, ast.Add)):
                l, r = ast.get_source_segment(src, node.left) or "", ast.get_source_segment(src, node.right) or ""
                if PAT.search(l) and PAT.search(r) or ("timedelta" in (l + r) and PAT.search(l + r)):
                    rows.append((f.name, node.lineno, (l + " ± " + r)[:90]))
    rows = sorted(set(rows))
    hit = [r for r in rows if (r[0], r[1]) in reached]
    for r in rows:
        print(f"# {'REACHED' if (r[0], r[1]) in reached else 'unreached'} {r[0]}:{r[1]} {r[2]}")
    print(f"RESULT candidates={len(rows)} count")
    print(f"RESULT reached={len(hit)} count")
    print(f"RESULT reached_not_in_candidates={len(reached - {(r[0], r[1]) for r in rows})} count")
    print("RESULT load1=0 thread_factor=1.0 swapins=0 (static, no timing)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
