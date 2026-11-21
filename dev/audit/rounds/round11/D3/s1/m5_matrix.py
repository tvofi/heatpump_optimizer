#!/usr/bin/env python3
"""D3-s1 M5(b): the kill-overlap matrix -- every closure script x every mutant.

Metric (one line): for each (mutant, closure script of the mutant's file)
pair, the verdict of that script on that mutant with no early stop -- K
killed (`tests/mutation_table.py:killed`: red AND more failing checks than the
traced unmutated baseline), S ran and survived, R reach-skipped (the script's
clean traced baseline never executed the mutated line,
`mutation_table:reach_skip`, so it cannot kill), T timed out; per script its
kills, its UNIQUE kills (mutants no other script kills) and per mutant its
killer count; duplicate kills = sum over killed mutants of (killers - 1).

Mutant set (`build`): every mutant of c2_mutants.json and c3c6_mutants.json,
plus every SURVIVED verdict under state/results/{pre,c2,c3c6}/, de-duplicated
by prescreen.py's key -> matrix_mutants.json. The drives themselves are
prescreen.py's (`run --full --mutants matrix_mutants.json --sub matrix...`,
D3S1_RELAX=0, so only the gate's own reach rule skips a pair).

golden.py (driven in run.sh's default strict mode) prints `N of M GOLDEN
SCENARIOS CHANGED`, which mutation_table.failing_count does not read: its
column is re-judged here on that count against its own baseline's.
tests/stress.py's column is driven alone afterwards (`--sub matrix-stress`,
one worker), as the brief's quiet-window rule requires.

Instrumented symbol: tests/mutation_table.py:killed / reach_skip over
prescreen.py:drive's per-driver runs of each mutated production line.
Perturbation: `--drop SCRIPT` removes one script's column -> `survivors`
rises by exactly that script's unique kills (direction up) and
`duplicate_kills` falls by its non-unique kills; dropping a script with no
unique kill leaves `survivors` unchanged (the null control).

Run (repo root):
  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_matrix.py build
  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_matrix.py table [--drop SCRIPT] [--subs matrix,matrix-extra,matrix-stress]
Expected: exact counts (contention-immune); seconds columns provisional.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-m5 (Linux
x86_64, nproc 4, Intel Xeon @ 2.10GHz), alone on the box.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import re
import hashlib
import json
import sys
import time as _t
_P0, _T0 = _t.process_time(), _t.thread_time()
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "tests")
import mutation_table as mt  # noqa: E402

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "state" / "results"


def key(m: dict) -> str:
    return hashlib.sha1((m["anchor"] + "|" + m["new"]).encode()).hexdigest()[:16]


def label(m: dict) -> str:
    tag = m.get("c2_id") or m.get("r10_id") or m["kind"]
    return f"{m['file'].rsplit('/', 1)[-1]}:{m['line']} {tag}"


def cmd_build(_a) -> int:
    allm: dict[str, dict] = {}
    for f in ("c2_mutants.json", "c3c6_mutants.json"):
        for m in json.loads((HERE / f).read_text()):
            allm.setdefault(key(m), m)
    for sub in ("pre", "c2", "c3c6"):
        for p in sorted((RESULTS / sub).glob("*.json")):
            r = json.loads(p.read_text())
            if r["verdict"] == "SURVIVED":
                allm.setdefault(key(r["mutant"]), r["mutant"])
    out = sorted(allm.values(), key=lambda m: (m["file"], m["line"], m["new"]))
    (HERE / "matrix_mutants.json").write_text(json.dumps(out, indent=1))
    print(f"RESULT matrix_mutants={len(out)}")
    return 0


GOLDEN_CHANGED = re.compile(r"(\d+) of (\d+) GOLDEN SCENARIOS CHANGED")


def golden_count(stdout: str, stderr: str) -> int:
    """golden.py strict prints `N of M GOLDEN SCENARIOS CHANGED`, a form
    mutation_table.failing_count does not read (golden.py is one of its
    DRIVER_EXCLUSIONS); a traceback adds one, as failing_count does."""
    m = GOLDEN_CHANGED.findall(stdout)
    return (int(m[-1][0]) if m else 0) + int("Traceback (most recent call last):" in stderr)


def golden_base() -> int | None:
    b = json.loads((HERE / "state" / "baselines.json").read_text()).get("tests/golden.py")
    if not b:
        return None
    return golden_count(b["run"].get("stdout_tail", ""), b["run"].get("stderr_tail", ""))


def load(subs: list[str]) -> dict[str, dict]:
    """key -> {mutant, cells: {script: verdict}, secs: {script: s}}."""
    rows: dict[str, dict] = {}
    gb = golden_base()
    for sub in subs:
        d = RESULTS / sub
        if not d.exists():
            continue
        for p in sorted(d.glob("*.json")):
            r = json.loads(p.read_text())
            row = rows.setdefault(p.stem, {"mutant": r["mutant"], "cells": {},
                                           "secs": {}})
            for s in r.get("skipped", []):
                row["cells"].setdefault(s, "R")
            for s in r.get("relaxed_skipped", []):
                row["cells"].setdefault(s, "X")
            for s, j in r["runs"].items():
                k = j.get("killed")
                if s == "tests/golden.py" and gb is not None and not j.get("timed_out"):
                    # re-judged on golden's own verdict form (kill = red AND
                    # more scenarios changed than the unmutated baseline's)
                    k = j["rc"] != 0 and golden_count(
                        j.get("stdout_tail", ""), j.get("stderr_tail", "")) > gb
                row["cells"][s] = ("K" if k else
                                   "T" if j.get("timed_out") else "S")
                row["secs"][s] = j.get("seconds", 0.0)
    return rows


def cmd_table(a) -> int:
    subs = a.subs.split(",")
    rows = load(subs)
    want = json.loads((HERE / "matrix_mutants.json").read_text())
    wk = {key(m) for m in want}
    rows = {k: v for k, v in rows.items() if k in wk}
    drop = set(a.drop.split(",")) if a.drop else set()
    scripts = sorted({s for r in rows.values() for s in r["cells"]} - drop)
    kills, uniq, ran, secs = Counter(), Counter(), Counter(), defaultdict(float)
    reach_skipped, timeouts = Counter(), Counter()
    survivors, dup, killed_mut = 0, 0, 0
    per_killers = Counter()
    pairs = Counter()
    for k, r in sorted(rows.items(), key=lambda kv: label(kv[1]["mutant"])):
        cells = {s: v for s, v in r["cells"].items() if s not in drop}
        ks = sorted(s for s, v in cells.items() if v == "K")
        for s, v in cells.items():
            pairs[v] += 1
            if v in "KST":
                ran[s] += 1
                secs[s] += r["secs"].get(s, 0.0)
            if v == "R":
                reach_skipped[s] += 1
            if v == "T":
                timeouts[s] += 1
        for s in ks:
            kills[s] += 1
        if len(ks) == 1:
            uniq[ks[0]] += 1
        if ks:
            killed_mut += 1
            dup += len(ks) - 1
        else:
            survivors += 1
        per_killers[len(ks)] += 1
        if a.verbose:
            print(f"{label(r['mutant'])}\tkillers={','.join(s.rsplit('/', 1)[-1] for s in ks) or '-'}\t"
                  + " ".join(f"{s.rsplit('/', 1)[-1]}={v}" for s, v in sorted(cells.items())))
    print("\nscript\tran\treach_skipped\ttimeouts\tkills\tunique_kills\tsum_seconds(provisional)")
    for s in scripts:
        print(f"{s}\t{ran[s]}\t{reach_skipped[s]}\t{timeouts[s]}\t{kills[s]}\t{uniq[s]}\t{secs[s]:.0f}")
    no_unique = [s for s in scripts if uniq[s] == 0]
    for s in no_unique:
        print(f"NO-UNIQUE-KILL {s} ran={ran[s]} kills={kills[s]} seconds={secs[s]:.0f}")
    print(f"RESULT mutants={len(rows)}")
    print(f"RESULT pairs={sum(pairs.values())}")
    for v in "KSRTX":
        print(f"RESULT pairs_{v}={pairs[v]}")
    print(f"RESULT killed_mutants={killed_mut}")
    print(f"RESULT survivors={survivors}")
    print(f"RESULT duplicate_kills={dup}")
    for n in sorted(per_killers):
        print(f"RESULT mutants_with_{n}_killers={per_killers[n]}")
    print(f"RESULT scripts_without_unique_kill={len(no_unique)}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT thread_factor={(_t.process_time() - _P0) / max(_t.thread_time() - _T0, 1e-9):.2f}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("build", "table"))
    ap.add_argument("--drop")
    ap.add_argument("--subs", default="matrix,matrix-extra,matrix-stress")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    return {"build": cmd_build, "table": cmd_table}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
