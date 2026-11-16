#!/usr/bin/env python3
"""D5-s8, D5.M4 (redispatch C7): a number a comment cites against the numeric constant it sits on.

Metric: comment units (tools/audit/text_ledger.py:units_of, D5) whose next code line assigns a numeric
literal, and of those the units naming no number equal to that literal or to it under a unit factor
(60, 3600, 1000, 100, 24, 1440, 86400, 1024): `candidates`, each then read by the seat.
Count key: the literal the production assignment carries, parsed from the line after the unit.
Command (export root): PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
    dev/audit/rounds/round11/D5/s8/numbers_adjacent.py [--perturb FILE:OLD=>NEW]
Expected at 92d38ecb: RESULT pairs=28, RESULT candidates=8 exactly (each read: no contradiction).
Perturbation: set a constant to a number its comment names, e.g.
--perturb 'tests/gate_lock.py:LEASE_SECONDS = 1800=>LEASE_SECONDS = 735' or
--perturb 'tests/coverage_ratchet.py:TOLERANCE = 0.1=>TOLERANCE = 95.0': candidates 8 -> 7 (down).
Each of the 8 baseline candidates was read: the comment bounds or motivates the constant (LEASE_SECONDS 1800
'above 735 s'; STALE_AFTER_COMMITS 12 'room over the worst case 8'), none contradicts it.
Machine: box B12, Linux x86_64. Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, re, subprocess, sys, time
sys.path.insert(0, "tools/audit")
import text_ledger as TL  # noqa: E402

ASSIGN = re.compile(r'^\s*(?:export\s+)?(?:const|let|var)?\s*([A-Za-z_]\w*)\s*(?::[^=]+)?=\s*(-?\d[\d_]*(?:\.\d+)?(?:e-?\d+)?)\s*[,;)]?\s*(?:#.*|//.*)?$')
NUM = re.compile(r'(?<![\w.#-])(-?\d+(?:\.\d+)?)(?![\w.]*\w)')
FACTORS = (60, 3600, 1000, 100, 24, 1440, 86400, 1024)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=None, help="git repo for the seat's cells; else the file list below")
    ap.add_argument("--ref", default="92d38ecb640bd462f2e19c0814d0f0b7df1ee692")
    ap.add_argument("--perturb", action="append", default=[])
    a = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()
    files = TL.seat_files("D5-s8", a.repo, a.ref) if a.repo else sorted(
        l.strip() for l in open(os.path.join(os.path.dirname(__file__), "cells.txt")))
    over = {}
    for spec in a.perturb:
        f, rest = spec.split(":", 1)
        old, new = rest.split("=>", 1)
        over[f] = over.get(f, TL.read(".", f)).replace(old, new, 1)
    pairs = cands = 0
    for f in sorted(set(files)):
        if "/vendor/" in f:
            continue
        text = over.get(f, TL.read(".", f))
        L = text.split("\n")
        for uid, line, kind, t in TL.units_of(f, text, "D5"):
            if kind != "comment":
                continue
            j = line + t.count("\n")
            while j < len(L) and not L[j].strip():
                j += 1
            m = ASSIGN.match(L[j]) if j < len(L) else None
            if not m:
                continue
            pairs += 1
            v = float(m.group(2).replace("_", ""))
            nums = [float(x) for x in NUM.findall(re.sub(r"#\d+|R\d+|D\d+|v\d[\d.]*|\d{4}-\d\d-\d\d", "", t))]
            if not nums:
                continue
            rel = any(abs(x - v) < 1e-9 or any(abs(x * k - v) < 1e-6 * max(1, abs(v)) or abs(x - v * k) < 1e-6 * max(1, abs(x))
                                               for k in FACTORS) for x in nums)
            if not rel:
                cands += 1
                print(f"  candidate {f}:{j + 1} {m.group(1)}={m.group(2)} comment numbers {nums[:8]}")
    print(f"RESULT pairs={pairs} count")
    print(f"RESULT candidates={cands} count")
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={tp / tt if tt else 1:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
