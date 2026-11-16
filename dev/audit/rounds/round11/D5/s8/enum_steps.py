#!/usr/bin/env python3
"""D5-s8 enumerators for D5.M1-M4: print each step's universe over the seat's cells, one item per line.

  M1  reader path x `document` row of `text_ledger.py outline` (3 reader paths of D5.md step 1)
  M2  `heading` and `link` rows of `outline`
  M3  `text_ledger.py units --dim D6` rows of the files outline lists as documents
  M4  `text_ledger.py units --dim D5` rows of the cells
Command (export root): python3 dev/audit/rounds/round11/D5/s8/enum_steps.py --step M1|M2|M3|M4 \
    [--repo <git repo> --ref 92d38ecb640bd462f2e19c0814d0f0b7df1ee692]   (else reads cells.txt beside it)
Expected at 92d38ecb: M1 0, M2 0, M3 0 lines (all 44 cells are .py/.mjs/.js/.sh code; outline
prints no row for a non-document), M4 3628 lines. Counts, exact. Machine: box B12.
"""
import argparse, os, sys
sys.path.insert(0, "tools/audit")
import text_ledger as TL  # noqa: E402

READERS = ("new-user-HACS-to-first-plan", "feature-user(two-tank,ECL110,capacity-tariff)", "developer-running-tests")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", required=True, choices=["M1", "M2", "M3", "M4"])
    ap.add_argument("--repo")
    ap.add_argument("--ref", default="92d38ecb640bd462f2e19c0814d0f0b7df1ee692")
    a = ap.parse_args()
    files = TL.seat_files("D5-s8", a.repo, a.ref) if a.repo else [
        l.strip() for l in open(os.path.join(os.path.dirname(__file__), "cells.txt")) if l.strip()]
    rows = [(f, ln, k, t) for f in files for ln, k, t in TL.outline(f, TL.read(".", f))]
    docs = [f for f, _, k, _ in rows if k == "document"]
    if a.step == "M1":
        for r in READERS:
            for d in docs:
                print(f"{r}\t{d}")
    elif a.step == "M2":
        for f, ln, k, t in rows:
            if k in ("heading", "link"):
                print(f"{f}\t{ln}\t{k}\t{t}")
    elif a.step == "M3":
        for uid, ln, k, t in TL.enumerate_units(".", docs, "D6"):
            print(f"{uid}\t{ln}\t{k}")
    else:
        for uid, ln, k, t in TL.enumerate_units(".", files, "D5"):
            print(f"{uid}\t{ln}\t{k}")


if __name__ == "__main__":
    main()
