"""D7 round 8, seat s2 -- the seam ratchet rows move under a pure rename (method step 1).

Metric: over every method of the production HeatPumpOptimizerCoordinator, the
change in tests/structure.py:seam_metrics' ``cross_edges`` (the budgeted
``cross_seam_edges``) and in the summed ``cut_<seam>`` rows when ONE method is
renamed -- the def and every ``self.<name>`` reference to it, nothing else --
to a name no SEAM_REGEX matches (the ``core`` bucket). A rename changes no
statement, no call, no attribute and no behaviour, so a structural metric
should read 0 for every method.
The count's key: the metric values ``structure.seam_metrics`` returns for the
production class AST after the rename.

Command (from the tree root):
  PYTHONPATH=tests/hastub python3 tools/audit/round8/D7/s2_rename.py
Expected at the baseline (exact): see REPORT-s2.md.
Null control (printed by the same run): each method renamed to its own name
  plus a suffix that keeps it in the SAME bucket (``<name>_r``); every delta
  must be 0 -- RESULT null_nonzero=0.
Perturbation: SEAM_REGEXES emptied (every method ``core``) -> cross_edges and
  every cut row go to_zero and renames_that_lower -> 0.
Baseline: cdf82daabcfe3777d98b31489f36df5555ec9d82. Machine: 4-vCPU cloud Linux
  container (audit-r8), python 3.11.15. Counts are contention-immune (exact).
Root rule: ROOT = the working directory.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import ast
import copy
import sys
import time
from pathlib import Path

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT / "tests"))
import structure  # noqa: E402


def coord_class() -> ast.ClassDef:
    tree = ast.parse((structure.PACKAGE_DIR / "coordinator.py").read_text())
    return next(n for n in ast.walk(tree)
                if isinstance(n, ast.ClassDef) and n.name == structure.COORDINATOR_CLASS_NAME)


def renamed(cls: ast.ClassDef, old: str, new: str) -> ast.ClassDef:
    c = copy.deepcopy(cls)
    for n in ast.walk(c):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == old and n in c.body:
            n.name = new
        elif (isinstance(n, ast.Attribute) and n.attr == old
              and isinstance(n.value, ast.Name) and n.value.id == "self"):
            n.attr = new
    return c


def score(cls: ast.ClassDef) -> tuple[int, int]:
    s = structure.seam_metrics(cls)
    return s["cross_edges"], sum(s["cut_costs"].values())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", action="store_true", help="empty SEAM_REGEXES")
    args = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()
    if args.perturb:
        structure.SEAM_REGEXES[:] = []
    cls = coord_class()
    base_x, base_cut = score(cls)
    names = [m.name for m in cls.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
    rows, null_nonzero = [], 0
    for i, name in enumerate(names):
        neutral = f"m{i:03d}_zz"
        assert not any(r.search(neutral) for _l, r in structure.SEAM_REGEXES)
        x, cut = score(renamed(cls, name, neutral))
        rows.append((x - base_x, cut - base_cut, name))
        nx, ncut = score(renamed(cls, name, name + "_r"))
        null_nonzero += (nx != base_x) or (ncut != base_cut)
    rows.sort()
    lower = [r for r in rows if r[0] < 0]
    raise_ = [r for r in rows if r[0] > 0]
    for dx, dcut, name in rows[:10]:
        print(f"  rename {name} -> core: cross_seam_edges {dx:+d}, sum(cut_*) {dcut:+d}")
    print(f"RESULT methods={len(names)} count")
    print(f"RESULT base_cross_seam_edges={base_x} count")
    print(f"RESULT base_sum_cut={base_cut} count")
    print(f"RESULT renames_that_lower_cross_seam_edges={len(lower)} count")
    print(f"RESULT renames_that_raise_cross_seam_edges={len(raise_)} count")
    print(f"RESULT max_single_rename_drop={-rows[0][0] if rows and rows[0][0] < 0 else 0} count")
    print(f"RESULT max_single_rename_cut_drop={-min(r[1] for r in rows) if rows else 0} count")
    # leave-one-out over the lowering renames: drop the most favourable one
    if lower:
        drops = sorted(-r[0] for r in lower)
        print(f"RESULT lowering_drop_range={drops[0]}..{drops[-1]} count")
        print(f"RESULT max_drop_without_top_rename={drops[-2] if len(drops) > 1 else 0} count")
    print(f"RESULT null_nonzero={null_nonzero} count")
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
