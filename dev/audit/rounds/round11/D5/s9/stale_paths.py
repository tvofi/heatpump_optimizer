#!/usr/bin/env python3
"""D5-s9 M4 (C2/C1): comment units in the seat's cells that cite a repository path absent at the ref.

Metric: count of (unit, cited path) pairs where a D5 comment unit in the seat's cells names a path
under docs/, tools/, dev/, .claude/ or .github/ that is not a tracked file or directory at the ref;
per file. Also `moved_refs`: the stale refs whose basename is tracked elsewhere at the ref (a move the
comment did not follow), and `contradicted`: stale refs where the code under the comment itself
reads the moved path (the comment is false of the statement it sits on).
Count key: the tracked tree at the ref (`git ls-tree`) and the path literal the code under the comment
reads, never the comment's own wording: restoring a file at the cited path or correcting the comment
both move the count.

Run (export root; --repo is a git repository holding the baseline):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D5/s9/stale_paths.py \
      --repo /home/user/heatpump_optimizer [--perturb]
Expected at 92d38ecb: RESULT stale_refs=17 exact (FILE lines: tests/entities.py=13, tests/run.sh=3,
tests/structure.py=1), RESULT moved_refs=14, RESULT contradicted=2. Pure text over a pinned tree, exact.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box B12 container, 4 vCPU.
Instrumented: tools/audit/text_ledger.py:units_of (the D5 units) over the tracked tree at the ref;
`contradicted` reads tests/entities.py's own `_handovers == [...]` and `_preflight = Path(...)` literals.
Perturbations (--perturb, in memory):
  restore  : every cited stale path is added to the tracked set (the moves undone) -> stale_refs to 0
  null     : the same scan over the D5 units of tests/features.py's sibling cell is not run (outside
             the seat); the in-seat null is the 66 files printing no FILE line.
"""
import os
for _threads in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_threads, "1")

import argparse, re, subprocess, sys, time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path("tools/audit").resolve()))
import text_ledger  # noqa: E402

SEAT = "D5-s9"
ROOTS = ("docs/", "tools/", "dev/", ".claude/", ".github/")
PATH_RE = re.compile(r"(?<![\w/.-])(\.?/?(?:[\w.-]+/)+[\w.-]+\.[A-Za-z]{1,5})(?![\w/])")
# Cited paths that are illustrations, not references (each judged in context):
EXEMPT = {
    ("tests/entities.py", "docs/arch.md"): "inside a quoted Markdown sample a link check is fed",
    ("tests/entities.py", "docs/img/p.svg"): "inside a quoted Markdown sample a link check is fed",
    ("tests/entities.py", "docs/img/x.svg"): "inside a quoted Markdown sample a link check is fed",
}


def tracked(repo, ref):
    out = subprocess.check_output(["git", "-C", repo, "ls-tree", "-r", "--name-only", ref], text=True).split("\n")[:-1]
    s = set(out)
    for f in out:
        p = Path(f).parent
        while str(p) != ".":
            s.add(str(p)); p = p.parent
    return s


def stale(repo, ref, extra=()):
    tree = tracked(repo, ref) | set(extra)
    files = text_ledger.seat_files(SEAT, repo, ref)
    rows = []
    for f in files:
        for uid, line, kind, text in text_ledger.units_of(f, text_ledger.read(".", f), "D5"):
            if kind != "comment" and kind != "docstring":
                continue
            for m in PATH_RE.finditer(text):
                p = m.group(1)
                p = p[2:] if p.startswith("./") else p
                if not p.startswith(ROOTS) or (f, p) in EXEMPT:
                    continue
                if p not in tree:
                    rows.append((f, uid, line, p))
    return rows


def contradicted(rows, repo, ref):
    """Stale refs whose moved twin is the literal the next 40 code lines under the unit read."""
    tree = tracked(repo, ref)
    n = 0
    for f, uid, line, p in rows:
        lines = text_ledger.read(".", f).splitlines()[int(line) - 1:int(line) + 40]
        code = "\n".join(l for l in lines if not l.lstrip().startswith("#"))
        twins = [t for t in tree if t.endswith("/" + p.rsplit("/", 1)[-1]) and t != p]
        if any(f'"{t}"' in code for t in twins):
            n += 1
            print("CONTRADICTED", uid, p, "code reads", [t for t in twins if f'"{t}"' in code][0], sep="\t")
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--ref", default="92d38ecb640bd462f2e19c0814d0f0b7df1ee692")
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    t0, t0t = time.process_time(), time.thread_time()
    rows = stale(a.repo, a.ref)
    per = defaultdict(int)
    for f, uid, line, p in rows:
        per[f] += 1
        print("STALE", uid, line, p, sep="\t")
    for f in sorted(per):
        print(f"FILE {f} stale_refs={per[f]}")
    print(f"RESULT stale_refs={len(rows)}")
    print(f"RESULT stale_units={len({r[1] for r in rows})}")
    print(f"RESULT files_with_stale={len(per)}")
    tree = tracked(a.repo, a.ref)
    moved = [r for r in rows if any(t.endswith("/" + r[3].rsplit("/", 1)[-1]) for t in tree)]
    print(f"RESULT moved_refs={len(moved)}")
    print(f"RESULT contradicted={contradicted(rows, a.repo, a.ref)}")
    if a.perturb:
        after = stale(a.repo, a.ref, extra=[r[3] for r in rows])
        print(f"RESULT perturb_restore stale_refs {len(rows)}->{len(after)}")
    pc, tc = time.process_time() - t0, time.thread_time() - t0t
    print(f"RESULT thread_factor={pc / tc if tc > 1e-9 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        sw = int(next(l.split()[1] for l in open("/proc/vmstat") if l.startswith("pswpin")))
    except (OSError, StopIteration):
        pass
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
