#!/usr/bin/env python3
"""Which package modules load the solver at run time, at a git ref (R10-LEAF-IMPORTS).

    python3 tools/audit/seat/solver_closure_census.py REF

The package at REF is extracted to a temporary directory; every module but ``__init__`` is
imported in its own fresh interpreter (tests/hastub on the path) and the line says whether
``heatpump_optimizer.optimizer`` and ``scipy`` are then in ``sys.modules``. The last line counts
the modules and the import failures and the exit status is 1 on any failure, so a census that
imported nothing cannot read as "every module is free of the solver". Run it at a merge base and
at a head and diff the two: the base reading a leaf IN is the revert arm of a head reading it out.

It lives here rather than under dev/audit/harnesses/: harness_headers.py reads that directory
from a child process, a read only CI's Linux recording sees, so a new file there is an INERT
READS under-approximation no Darwin seat can record. The mutation proof's block runner is
features_block.py beside this file.
"""
from __future__ import annotations

import io
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


REPO = repo_root(__file__)
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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    raise SystemExit(census(sys.argv[1]))
