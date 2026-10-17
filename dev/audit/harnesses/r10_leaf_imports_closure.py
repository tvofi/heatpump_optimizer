#!/usr/bin/env python3
"""R10-LEAF-IMPORTS (ARCH2-s4 P1, ARCH3-s6 P4): which package modules load the solver at run time.

    python3 dev/audit/harnesses/r10_leaf_imports_closure.py census REF
    python3 dev/audit/harnesses/r10_leaf_imports_closure.py block

census: the package at git ref REF, extracted to a temporary directory; every module but
``__init__`` is imported in its own fresh interpreter (tests/hastub on the path) and the line says
whether ``heatpump_optimizer.optimizer`` and ``scipy`` are then in ``sys.modules``. The last line
counts the modules and the import failures, so a census that imported nothing cannot read as
"every module is free of the solver". Run it at the merge base and at the head and diff the two:
the revert arm is the base reading the leaves IN.

block: tests/features.py's R10-LEAF-IMPORTS checks run verbatim on the working tree (from the block's
opening comment to the vocabulary check) under a minimal Results, so a mutant is judged by the
committed check without running the whole script. Mutate a leaf's import back to the optimizer and
the leaf's check must fail; the unmutated tree must print ``0 FAILED``.
"""
from __future__ import annotations

import io
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PKG = "heatpump_optimizer"


def census(ref: str) -> int:
    hastub = REPO / "tests" / "hastub"
    with tempfile.TemporaryDirectory(prefix="leaf-closure-") as tmp:
        arc = subprocess.run(["git", "-C", str(REPO), "archive", ref, "custom_components"],
                             capture_output=True, check=True).stdout
        tarfile.open(fileobj=io.BytesIO(arc)).extractall(tmp, filter="data")
        root = Path(tmp) / "custom_components"
        env = {**os.environ, "PYTHONPATH": os.pathsep.join([str(hastub), str(root)])}
        mods = sorted(p.stem for p in (root / PKG).glob("*.py") if p.stem != "__init__")
        fail = solver = 0
        for m in mods:
            r = subprocess.run(
                [sys.executable, "-c",
                 f"import sys, {PKG}.{m}; "
                 f"print('IN' if '{PKG}.optimizer' in sys.modules else 'out', "
                 "'scipy' if 'scipy' in sys.modules else '-')"],
                capture_output=True, text=True, env=env)
            if r.returncode:
                fail += 1
                print(f"{m} IMPORT-FAILED {(r.stderr.strip().splitlines() or [''])[-1][:120]}")
                continue
            solver += r.stdout.startswith("IN")
            print(m, r.stdout.strip())
        print(f"TOTAL modules={len(mods)} solver_in={solver} import_failures={fail}")
        return 1 if fail or not mods else 0


def block() -> int:
    src = (REPO / "tests" / "features.py").read_text().splitlines(keepends=True)
    a = next(i for i, l in enumerate(src) if l.startswith("# R10-LEAF-IMPORTS (ARCH2-s4 P1"))
    b = next(i for i in range(a, len(src)) if src[i].startswith('    f"payload lacks')) + 2
    sys.path[:0] = [str(REPO / "tests" / "hastub"), str(REPO / "tests"), str(REPO / "custom_components")]

    class Results:
        fails = 0

        @staticmethod
        def check(name, ok, detail=""):
            print(("  ok   " if ok else "  FAIL ") + name + ("" if ok else f"  [{detail}]"))
            Results.fails += not ok

    ns = {"R": Results, "sys": sys, "_Path": Path, "__name__": "leaf_block"}
    exec(compile("".join(src[a:b]), "tests/features.py:R10-LEAF-IMPORTS", "exec"), ns)
    print(f"{Results.fails} FAILED")
    return 1 if Results.fails else 0


if __name__ == "__main__":
    if sys.argv[1:2] == ["census"] and len(sys.argv) == 3:
        raise SystemExit(census(sys.argv[2]))
    if sys.argv[1:] == ["block"]:
        raise SystemExit(block())
    raise SystemExit(__doc__)
