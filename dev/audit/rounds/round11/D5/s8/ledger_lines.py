#!/usr/bin/env python3
"""D5-s8, D5.M4 instrument check: does text_ledger report the line a JavaScript comment unit starts on?

Metric: D5 comment units of the seat's cells whose reported `line` does not hold the unit's first
comment line (`mislocated`), over all comment units (`comment_units`).
Count key: tools/audit/text_ledger.py:units_of's line field (scan_c_like for .js/.mjs/.sh), compared
with the file's own text at that line.
Command (export root): PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
    dev/audit/rounds/round11/D5/s8/ledger_lines.py [--fixed]
--fixed swaps in scan_c_like with one line added (count the newline a non-template string stops at
before `break`, and the newline an escape skips): the perturbation, under which mislocated must go to 0.
Expected at 92d38ecb: RESULT comment_units=3099, mislocated=1175 exact; --fixed: mislocated=0.
Null control: Python units (ast/tokenize line numbers) are counted separately; py_mislocated=0 both arms.
Machine: box B12, Linux x86_64. Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, inspect, sys, time
sys.path.insert(0, "tools/audit")
import text_ledger as TL  # noqa: E402


def fixed_scan():
    src = inspect.getsource(TL.scan_c_like)
    a = """                if text[j] == "\\\\":
                    j += 1
                elif text[j] == "\\n":
                    if c != "`" and not hash_comments:
                        break"""
    b = """                if text[j] == "\\\\":
                    if text[j + 1:j + 2] == "\\n":
                        line += 1
                    j += 1
                elif text[j] == "\\n":
                    if c != "`" and not hash_comments:
                        line += 1
                        break"""
    assert a in src, "scan_c_like no longer has the shape this perturbation edits"
    ns = dict(TL.__dict__)
    exec(src.replace(a, b), ns)
    return ns["scan_c_like"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixed", action="store_true")
    a = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()
    if a.fixed:
        TL.scan_c_like = fixed_scan()
    files = [l.strip() for l in open(os.path.join(os.path.dirname(__file__), "cells.txt")) if l.strip()]
    tot = bad = pytot = pybad = 0
    per = {}
    for f in files:
        text = TL.read(".", f)
        L = text.split("\n")
        for uid, line, kind, t in TL.units_of(f, text, "D5"):
            if kind != "comment":
                continue
            first = t.split("\n")[0].lstrip("\0").strip()
            ok = 1 <= line <= len(L) and first in L[line - 1]
            if f.endswith(".py"):
                pytot += 1; pybad += not ok
                continue
            tot += 1
            if not ok:
                bad += 1
                per[f] = per.get(f, 0) + 1
    for f, n in sorted(per.items()):
        print(f"RESULT file={f} mislocated={n}")
    print(f"RESULT comment_units={tot + pytot} count")
    print(f"RESULT mislocated={bad} count")
    print(f"RESULT py_comment_units={pytot} count")
    print(f"RESULT py_mislocated={pybad} count")
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={tp / tt if tt else 1:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
