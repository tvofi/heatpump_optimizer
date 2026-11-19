#!/usr/bin/env python3
"""D5-s5 step enumerators: print one step's universe over the seat's cells, one item per line.

    python3 dev/audit/rounds/round11/D5/s5/step_universe.py M1|M2|M3|M4

Cells: cells.tsv beside this file, the output of
`python3 tools/audit/check_scopes.py --repo <git repo> --ref 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 --seat D5-s5`
(the export has no .git). D5.md: M1 = each reader path x each `document` row `text_ledger.py outline`
prints; M2 = the `heading` and `link` rows; M3 = the `units --dim D6` of those documents; M4 = the
`units --dim D5` of the cells. Run from the export root. Baseline counts: M1 0, M2 0, M3 0, M4 3631.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, "tools/audit")
import text_ledger as tl  # noqa: E402

READERS = ("new-user-hacs-to-first-plan", "feature-config-two-tank-ecl110-capacity-tariff", "developer-running-tests")


def main(step):
    files = sorted({l.split("\t")[2] for l in (HERE / "cells.tsv").read_text().splitlines() if l.count("\t") >= 2})
    rows = [(f, ln, kind, t) for f in files for ln, kind, t in tl.outline(f, tl.read(".", f))]
    docs = [f for f, _, kind, _ in rows if kind == "document"]
    if step == "M1":
        for r in READERS:
            for d in docs:
                print(f"{r}\t{d}")
    elif step == "M2":
        for f, ln, kind, t in rows:
            if kind in ("heading", "link"):
                print(f"{f}:{ln}\t{kind}\t{t}")
    elif step == "M3":
        for u in tl.enumerate_units(".", docs, "D6"):
            print(f"{u[0]}\t{u[1]}\t{u[2]}")
    elif step == "M4":
        for u in tl.enumerate_units(".", files, "D5"):
            print(f"{u[0]}\t{u[1]}\t{u[2]}")
    else:
        print("usage: step_universe.py M1|M2|M3|M4", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ""))
