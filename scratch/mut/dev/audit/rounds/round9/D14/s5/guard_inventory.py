#!/usr/bin/env python3
# D14-s5 detector for bug class I1 ("a mutation kill miscounted, or a guard
# whose deletion leaves the gate green"): which production GUARDS can the
# mutation ratchet never see?
#
# METRIC: uncovered = number of guard seams in custom_components/heatpump_optimizer
#   (enumerated independently by AST, three shapes below) for which
#   tests/mutation_table.py:candidates() yields NO mutant on the seam's line, so
#   tests/mutation_table.py:unpinned_sites -- the ratchet that "stops a guard
#   from leaving the tree unaccounted for" -- can never count it.  Count key:
#   the (file, line) set candidates() delivers, never the guard's source text.
#   Shapes:
#     EXIT   an `if`/`elif` whose body ends in return/raise/continue/break
#            (covered iff candidates() has a GUARD_OFF on that line)
#     CLAMP  min()/max() with two or more positional args, np.clip/np.minimum/np.maximum/np.fmin/
#            np.fmax/math.fmin/math.fmax  (covered iff a CLAMP_DROP on that line)
#     TERN   a conditional expression `a if <compare/finite test> else b`
#            (covered iff ANY candidate on that line)
# INSTRUMENTED SYMBOLS: tests/mutation_table.py:candidates, inventory,
#   unpinned_sites.
# COMMAND (repo root):
#   PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
#     tools/audit/round9/D14/s5/guard_inventory.py [--perturb widen] [--list]
#   --fixture   run only the clean/re-introduction fixture
#   --history   re-find the ledger's I1 instances at their pre-fix commits
# EXPECTED (baseline 1936d5ca, box B9): see REPORT.md; exact (AST, deterministic).
# MACHINE: box B9 cloud container, CPython 3.14.0rc2.  BASELINE: 1936d5ca72a0.
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")

import argparse
import ast
import collections
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
import mutation_table as mt  # noqa: E402  the instrument under test

PKG = ROOT / "custom_components" / "heatpump_optimizer"
CLAMP_ATTR = {("np", "clip"), ("np", "minimum"), ("np", "maximum"),
              ("np", "fmin"), ("np", "fmax"), ("numpy", "clip"),
              ("math", "fmin"), ("math", "fmax")}
EXITS = (ast.Return, ast.Raise, ast.Continue, ast.Break)


def _finite_or_cmp(test: ast.AST) -> bool:
    for n in ast.walk(test):
        if isinstance(n, ast.Compare):
            return True
        if isinstance(n, ast.Call):
            f = n.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
            if name in ("isfinite", "isnan", "isinf", "_finite"):
                return True
    return False


def seams(src: str) -> list[tuple[str, int, str]]:
    """(shape, line, enclosing def) for every guard seam in one source."""
    tree = ast.parse(src)
    out = []

    def visit(node, where):
        for ch in ast.iter_child_nodes(node):
            w = where
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                w = f"{where}.{ch.name}" if where else ch.name
            if isinstance(ch, ast.If) and ch.body and isinstance(ch.body[-1], EXITS):
                out.append(("EXIT", ch.lineno, w))
            if isinstance(ch, ast.Call):
                f = ch.func
                if isinstance(f, ast.Name) and f.id in ("min", "max") and len(ch.args) >= 2:
                    out.append(("CLAMP", ch.lineno, w))
                elif (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name)
                      and (f.value.id, f.attr) in CLAMP_ATTR):
                    out.append(("CLAMP", ch.lineno, w))
            if isinstance(ch, ast.IfExp) and _finite_or_cmp(ch.test):
                out.append(("TERN", ch.lineno, w))
            visit(ch, w)
    visit(tree, "")
    return out


def covered(shape: str, line: int, cands: dict[int, set[str]]) -> bool:
    kinds = cands.get(line, set())
    if shape == "EXIT":
        return "GUARD_OFF" in kinds
    if shape == "CLAMP":
        return "CLAMP_DROP" in kinds
    return bool(kinds)


def candidates_by_line(path: Path, cand_fn) -> dict[int, set[str]]:
    d: dict[int, set[str]] = collections.defaultdict(set)
    for s in cand_fn(path):
        d[s["line"]].add(s["kind"])
    return d


def widened_candidates(path: Path):
    """--perturb widen: candidates() plus GUARD_OFF for every `if`/`elif`
    whatever its test's line span or else-branch -- the widening a fix would
    make.  Must drive `uncovered` DOWN."""
    yield from mt.candidates(path)
    src = path.read_text()
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.If):
            yield dict(kind="GUARD_OFF", file=str(path), line=n.lineno, old="", new="")


def measure(files, cand_fn):
    rows = []
    for p in files:
        src = p.read_text()
        cands = candidates_by_line(p, cand_fn)
        for shape, line, where in seams(src):
            rows.append((str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),
                         shape, line, where, covered(shape, line, cands)))
    return rows


FIXTURE_CLEAN = '''
import math
LIMIT = 3.0
def f(x, y):
    if not math.isfinite(x):
        return None
    y = max(y, 0.0)
    return min(x, LIMIT) + y
'''
# One-line re-introduction: the same guard with its test split over two lines.
FIXTURE_REINTRO = FIXTURE_CLEAN.replace(
    "    if not math.isfinite(x):\n",
    "    if (not math.isfinite(x)\n            or x < 0):\n")


def fixture() -> tuple[int, int]:
    d = Path(tempfile.mkdtemp(prefix="d14s5-i1-"))
    res = []
    for name, src in (("clean.py", FIXTURE_CLEAN), ("reintro.py", FIXTURE_REINTRO)):
        p = d / name
        p.write_text(src)
        res.append(sum(1 for r in measure([p], mt.candidates) if not r[4]))
    return res[0], res[1]


# The ledger's I1 instances whose guard is a production line (tools/audit/
# bugclasses.json lists them; the pre-fix commit is the pin's parent, read
# from this worktree's git history): (instance, pre-fix commit, file, def, needle)
HISTORY = [
    ("R5 D3-04 #1312", "076f4a35^", "coordinator.py", "_mixing_valve_view", ">= 2"),
    ("R5 D3-05 #1313", "076f4a35^", "price_model.py", "quarter_confidence", "min(1.0"),
    ("R5 D3-06 #1314", "076f4a35^", "coordinator.py", "_fold_capacity_envelope", "isfinite"),
    ("R5 D3-07 #1315", "6438f8f6^", "sensor.py", "_finite", "ndarray"),
    ("R5 D3-08 #1316", "6438f8f6^", "curve_learning.py", "_step_down", "np.clip"),
    ("R5 D3-09 #1317", "6438f8f6^", "topology.py", "peak_miss_sek", "max(int(count), 1)"),
]


def history() -> list[str]:
    out = []
    d = Path(tempfile.mkdtemp(prefix="d14s5-i1h-"))
    for inst, ref, fname, fn, needle in HISTORY:
        src = subprocess.run(["git", "show", f"{ref}:custom_components/heatpump_optimizer/{fname}"],
                             cwd=ROOT, capture_output=True, text=True).stdout
        p = d / fname
        p.write_text(src)
        lines = src.splitlines()
        rows = [r for r in measure([p], mt.candidates)
                if r[3].split(".")[-1] == fn and needle in lines[r[2] - 1]]
        if not rows:
            # the guard's line holds the needle but its seam is the enclosing if
            rows = [r for r in measure([p], mt.candidates) if r[3].split(".")[-1] == fn]
            verdict = f"no seam line carries {needle!r}; {len(rows)} seams in def"
        else:
            verdict = ", ".join(f"{r[1]}@{r[2]} {'inventoried' if r[4] else 'INVISIBLE'}"
                                for r in rows)
        out.append(f"{inst} {ref} {fname}:{fn}: {verdict}")
    return out


PROBE_BASE = "\n\ndef _d14s5_probe(x):\n    y = x\n    return y\n"
PROBE_VISIBLE = ("\n\ndef _d14s5_probe(x):\n    if x != x:\n        return 0.0\n"
                 "    y = x\n    return y\n")
PROBE_INVISIBLE = ("\n\ndef _d14s5_probe(x):\n    if (x != x\n            or x is None):\n"
                   "        return 0.0\n    y = x\n    return y\n")


def ratchet_probe() -> tuple[int, int, object, object]:
    """Drive the production ratchet (inventory -> unpinned_sites ->
    ratchet_refusal) over a scratch copy of price_model.py with one new,
    undispositioned guard: single-line test vs the same guard split over two
    lines.  Returns (delta_visible, delta_invisible, refusal_visible,
    refusal_invisible)."""
    rel = "custom_components/heatpump_optimizer/price_model.py"
    d = Path(tempfile.mkdtemp(prefix="d14s5-i1r-"))
    orig_root = mt.ROOT
    budgets = mt.load_budgets()
    counts = []
    try:
        mt.ROOT = d
        for tail in (PROBE_BASE, PROBE_VISIBLE, PROBE_INVISIBLE):
            p = d / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text((orig_root / rel).read_text() + tail)
            counts.append(len(mt.unpinned_sites(budgets, mt.inventory([p]))))
    finally:
        mt.ROOT = orig_root
    base = counts[0]
    rv = mt.ratchet_refusal(base, [None] * counts[1])
    ri = mt.ratchet_refusal(base, [None] * counts[2])
    return counts[1] - base, counts[2] - base, rv, ri


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", choices=["none", "widen"], default="none")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--fixture", action="store_true")
    ap.add_argument("--history", action="store_true")
    a = ap.parse_args()
    import time
    c0, t0 = time.process_time(), time.thread_time()
    clean, reintro = fixture()
    print(f"RESULT fixture_clean_uncovered={clean} count")
    print(f"RESULT fixture_reintro_uncovered={reintro} count")
    dv, di, rv, ri = ratchet_probe()
    print(f"RESULT ratchet_delta_visible_guard={dv} count")
    print(f"RESULT ratchet_delta_invisible_guard={di} count")
    print(f"RESULT ratchet_refuses_visible={int(rv == 1)} count")
    print(f"RESULT ratchet_refuses_invisible={int(ri == 1)} count")
    if a.fixture:
        return 0
    if a.history:
        for line in history():
            print("  HIST", line)
    files = sorted(PKG.glob("*.py"))
    cand_fn = widened_candidates if a.perturb == "widen" else mt.candidates
    rows = measure(files, cand_fn)
    tot = collections.Counter(r[1] for r in rows)
    unc = collections.Counter(r[1] for r in rows if not r[4])
    for shape in ("EXIT", "CLAMP", "TERN"):
        print(f"RESULT seams_{shape}={tot[shape]} count")
        print(f"RESULT uncovered_{shape}={unc[shape]} count")
    fin = [r for r in rows if r[1] == "EXIT" and not r[4]]
    print(f"RESULT uncovered={sum(unc.values())} count")
    print(f"RESULT seams={sum(tot.values())} count")
    # which inventory rule excludes each uncovered EXIT seam
    why = collections.Counter()
    for f, shape, line, where, cov in rows:
        if shape != "EXIT" or cov:
            continue
        src_line = (ROOT / f).read_text().splitlines()[line - 1].strip()
        node = next(n for n in ast.walk(ast.parse((ROOT / f).read_text()))
                    if isinstance(n, ast.If) and n.lineno == line)
        if src_line.startswith("elif"):
            why["elif"] += 1
        elif node.orelse:
            why["has else"] += 1
        elif node.test.end_lineno != node.test.lineno:
            why["multi-line test"] += 1
        else:
            why["trailing comment after the colon"] += 1
    for k, v in sorted(why.items()):
        print(f"RESULT uncovered_EXIT_because[{k}]={v} count")
    per_file = collections.Counter(r[0] for r in rows if not r[4])
    print("  top files:", ", ".join(f"{Path(k).name}={v}" for k, v in per_file.most_common(8)))
    if a.list:
        for r in rows:
            if not r[4]:
                print(f"  SEAM {r[1]} {r[0]}:{r[2]} {r[3]}")
    c1, t1 = time.process_time() - c0, time.thread_time() - t0
    print(f"RESULT thread_factor={c1 / t1 if t1 else 1:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=n/a")
    return 0


if __name__ == "__main__":
    sys.exit(main())
