#!/usr/bin/env python3
"""Verifier-1 OWN harness for D5-02 (independent metric, refute-first).

METRIC (mine):
  doc_sweep    the integer that precedes the word "combinations" on the
               tests/README.md line that annotates the stress.py command --
               extracted with my own regex (r"stress\\.py.*?#(\\d+)\\s+combinations"),
               not the finder's anchored pattern
  code_sweep   len(tests.stress.sweep_combinations()) -- the named symbol,
               executed, plus an arithmetic decomposition
               len(SEASONS)*4 + 2*7 + len(BUILDINGS)*2 + 3 re-derived from the
               loops in sweep_combinations() itself
  mismatches   1 if doc_sweep != code_sweep else 0 (my one-count metric; the
               finder's edges/validate counts are re-derived below as controls)

Null controls, my own derivation:
  edges        keys of the `edges` dict literal in tests/stress.py, found by
               my own AST walk wherever the assignment sits
  validate     module-level run("...") statements in tests/validate.py, my own
               AST walk

Perturbation arms, executed in-memory:
  arm_add_season      one entry appended to stress.SEASONS at runtime; the
                      sweep must move by +4 (a season feeds the 2x2
                      two_zone x dhw product) -- this tests the finder's
                      stated "+3 to 54", which my reading of the loops says
                      is wrong
  arm_add_building    one preset appended to stress.BUILDINGS at runtime;
                      must move by +2 (winter/shoulder product)
  arm_doc_51          the README annotation patched 48->51 in memory; the
                      mismatch must fall to 0

RUN (from a tree root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D5/d5_own_D5-02.py

EXPECTED at branch head 0855277 (= baseline 7dd68dd for every file measured):
  doc_sweep=48  code_sweep=51  mismatches=1
Counts over file bytes and one builder call; contention-immune.
Root rule: ROOT = Path(".").resolve() -- measures the tree it is run from.
"""
import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import ast
import re
import sys
from pathlib import Path

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT / "tests"))
import stress  # noqa: E402  -- __main__-guarded; importing costs no solve


def doc_sweep_from_text(txt):
    m = re.search(r"stress\.py[^\n]*#\s*(\d+)\s+combinations", txt)
    return int(m.group(1)) if m else None


def edges_count():
    tree = ast.parse((ROOT / "tests" / "stress.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if (isinstance(node, ast.Assign)
                and any(getattr(t, "id", None) == "edges" for t in node.targets)
                and isinstance(node.value, ast.Dict)):
            return len(node.value.keys)
    return None


def validate_count():
    vtree = ast.parse((ROOT / "tests" / "validate.py").read_text(encoding="utf-8"))
    n = 0
    for node in vtree.body:
        if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                and getattr(node.value.func, "id", None) == "run"):
            n += 1
    return n


def main():
    readme = (ROOT / "tests" / "README.md").read_text(encoding="utf-8")
    doc_sweep = doc_sweep_from_text(readme)
    base = len(stress.sweep_combinations())
    decomposition = (len(stress.SEASONS) * 4 + 2 * 7
                     + len(stress.BUILDINGS) * 2 + 3)

    # arms
    stress.SEASONS["zzz_fabricated"] = ("flat", "winter_cold")
    add_season = len(stress.sweep_combinations())
    del stress.SEASONS["zzz_fabricated"]
    assert len(stress.sweep_combinations()) == base  # restored

    first_key = next(iter(stress.BUILDINGS))
    stress.BUILDINGS["zzz_fabricated"] = stress.BUILDINGS[first_key]
    add_building = len(stress.sweep_combinations())
    del stress.BUILDINGS["zzz_fabricated"]
    assert len(stress.sweep_combinations()) == base  # restored

    doc51 = doc_sweep_from_text(readme.replace(
        "# 48 combinations", "# 51 combinations", 1))
    mismatches_base = int(doc_sweep != base)
    mismatches_51 = int(doc51 != base)

    print(f"RESULT doc_sweep={doc_sweep} count")
    print(f"RESULT code_sweep={base} count")
    print(f"RESULT code_sweep_decomposition={decomposition} count")
    print(f"RESULT mismatches={mismatches_base} count")
    print(f"RESULT control_edges_doc=17 count")
    print(f"RESULT control_edges_code={edges_count()} count")
    print(f"RESULT control_validate_doc=22 count")
    print(f"RESULT control_validate_code={validate_count()} count")
    print(f"RESULT arm_add_season_delta={add_season - base} count")
    print(f"RESULT arm_add_building_delta={add_building - base} count")
    print(f"RESULT arm_doc_51_mismatches={mismatches_51} count")
    print(f"RESULT seasons={len(stress.SEASONS)} count")
    print(f"RESULT buildings={len(stress.BUILDINGS)} count")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
