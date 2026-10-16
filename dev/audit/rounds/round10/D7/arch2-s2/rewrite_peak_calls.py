#!/usr/bin/env python3
"""ARCH2-s2: rewrite every call of the capacity-charge family onto the PeakBilling record.

``peak_cost(p, b, 6.0, 20.0, 60, 1.0, 3, distinct_days=False)`` becomes
``peak_cost(p, b, PeakBilling(6.0, 20.0, 60, 1.0, 3, distinct_days=False))``: the plan and the
baseline stay positional, everything after them moves into the record verbatim (source text kept),
positional order being the scalar functions' (identical to the record's field order). A positional
call of ``peak_cost_batch`` past ``offset_steps`` is refused, since the batch twin ordered its last
two parameters the other way round.

Command:  python3 dev/audit/rounds/round10/D7/arch2-s2/rewrite_peak_calls.py FILE...
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

#: the three names plus the aliases tests/features.py imports them under
FAMILY = {"peak_cost", "peak_cost_smooth", "peak_cost_batch",
          "_pcb948", "_peak_cost", "_bo_pcb", "_f25_pcb"}
BATCH = {"peak_cost_batch", "_pcb948", "_bo_pcb", "_f25_pcb"}


def rewrite(src: str) -> tuple[str, int]:
    tree = ast.parse(src)
    lines = src.splitlines(keepends=True)
    offs = [0]
    for ln in lines:
        offs.append(offs[-1] + len(ln))

    def at(line: int, col: int) -> int:
        return offs[line - 1] + len(lines[line - 1].encode()[:col].decode())

    edits = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in FAMILY:
            if len(n.args) < 2 or (len(n.args) == 2 and not n.keywords):
                continue
            if any(isinstance(a, ast.Call) and getattr(a.func, "id", "") == "PeakBilling" for a in n.args):
                continue
            if n.func.id in BATCH and len(n.args) > 8:
                raise SystemExit(f"line {n.lineno}: positional batch call past offset_steps")
            rest = [*n.args[2:], *n.keywords]
            start = at(rest[0].lineno, rest[0].col_offset)
            last = rest[-1]
            end = at(last.end_lineno, last.end_col_offset)
            edits.append((start, end))
    out = src
    for start, end in sorted(edits, reverse=True):
        out = out[:start] + "PeakBilling(" + out[start:end] + ")" + out[end:]
    return out, len(edits)


def main(argv: list[str]) -> int:
    for f in argv[1:]:
        p = Path(f)
        new, n = rewrite(p.read_text())
        p.write_text(new)
        print(f"{f}: {n} call(s) rewritten")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
