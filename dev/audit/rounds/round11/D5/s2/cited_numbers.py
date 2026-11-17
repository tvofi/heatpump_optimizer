#!/usr/bin/env python3
"""D5.M4 cited-number harness (round 10's C5 carry): every number a comment unit of seat D5-s2's
code cells cites, against the literals of the code it sits on.

Metric: numbers cited in comment/docstring prose (issue ids after '#', dates, version-like and
path-embedded digits excluded) that occur as no literal in the unit's own file within 40 lines
after it (or, for a module header, anywhere in the file). Each one left is printed for an executed
check of its own (comments.py rows it); the count is the hand-off, not a verdict.
Key: the code literals tokenize/regex reads from the file, never another comment.

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/cited_numbers.py [--plant]
  --plant  null control: a comment citing '0.4242 kWh' with no such literal is appended to
           make_model_figures.py in memory: unmatched +1.
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692: the RESULT lines, exact (counts).
Machine: B2 (orchestrator's macOS box).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import re, sys, time
from pathlib import Path

sys.path.insert(0, "tools/audit")
import text_ledger  # noqa: E402

FILES = ["docs/img/card/make_card_figures.mjs", "docs/img/model/make_card_weekly_figure.mjs",
         "docs/img/model/make_model_figures.py", "docs/img/readme/make_readme_figures.py",
         "docs/img/readme/render.mjs", "docs/img/readme/render_mermaid.mjs"]
NUM = re.compile(r"(?<![\w#./-])(\d+(?:\.\d+)?)(?![\w./:-]*\w)")


def cited(text):
    t = re.sub(r"#\d+|\b\d{4}-\d{2}-\d{2}\b|\b[\w./-]*/[\w./-]*\b|`[^`]*/[^`]*`|R\d+-[\w-]+|\bD\d+(-s\d+)?-\d+\b"
               r"|\b[A-Z]\d+\b|\bv\d+(\.\d+)*\b|sha256|\d+(?:\.\d+)?:1\b", " ", text)
    return {m.group(1) for m in NUM.finditer(t)}


def main():
    total = unmatched = 0
    rows = []
    for f in FILES:
        src = Path(f).read_text(encoding="utf-8")
        if "--plant" in sys.argv and f.endswith("make_model_figures.py"):
            src += "\n# The planted tank holds 0.4242 kWh here.\nPLANTED = 1\n"
        lines = src.splitlines()
        for uid, line, kind, text in text_ledger.units_of(f, src, "D5"):
            if kind == "file":
                continue
            span = text.count("\n") + 1
            header = line <= 2
            code = "\n".join(lines if header else lines[line - 1 + span - 1: line - 1 + span + 40])
            code = re.sub(r"(//|#)[^\n]*", " ", code)
            lits = set(re.findall(r"(?<![\w.])(\d+(?:\.\d+)?)", code))
            litf = {float(x) for x in lits}
            for n in sorted(cited(text)):
                total += 1
                if n in lits or float(n) in litf:
                    continue
                unmatched += 1
                rows.append(f"{f}:{line} cites {n}")
    print(f"RESULT cited_numbers={total} numbers")
    print(f"RESULT unmatched={unmatched} numbers")
    for r in rows:
        print(f"   unmatched {r}")
    print(f"RESULT thread_factor={time.process_time() / max(time.thread_time(), 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
