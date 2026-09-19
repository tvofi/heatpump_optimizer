#!/usr/bin/env python3
"""D10 round-5 — strict-typing (Platinum) rule instrument, the marker arm.

METRIC DEFINITION (one line): `py_typed_present` = 1 when a PEP-561 `py.typed`
marker file exists in the integration package directory, else 0 — the half of
the Platinum rule that is a FILE, not a toolchain run; carried beside the
source-only `type_ignores` count the ordinary gate already enforces.

COMMAND (run from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round5/D10/strict_typing.py

EXPECTED: RESULT py_typed_present=0 bool; RESULT type_ignores=0 count.

INSTRUMENTED SYMBOL: the package directory
custom_components/heatpump_optimizer (its file list), not a Python symbol —
the rule's marker half is about a file that is either shipped or not.

PERTURBATION: `touch custom_components/heatpump_optimizer/py.typed` ->
py_typed_present rises 0 -> 1. Run the arm against a COPY with
HPO_TYPING_ROOT=<dir containing heatpump_optimizer/> so the tree under
measurement is not written to; the invariant claim is that the count keys on
the file's presence and nothing else.

NOT MEASURED HERE: the pinned mypy census (`tests/typing_ruler.py --mypy`,
mypy 2.3.1 + homeassistant-stubs 2026.2.3 under CPython >= 3.13.2). That
toolchain is not installable on this box and the ruler REFUSES rather than
passing when it is absent, so the recorded census (0, by_code {}) is quoted
from tests/typing_budgets.json, not re-taken. tools/audit/round5/D10/
typing_brief.py is the arm the D10 brief asks for (mypy --strict with the
vendored `tests/hastub` on the path); its number is a different measurement
and is labelled as such there.

BASELINE SHA: eaa2a06af16a1b5b006f58a0f36cc92131f80225 (origin/main, round 5).
MACHINE: 8-core Apple M1, 8 GB, macOS Darwin 25.6.0, Python 3.11.5.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import pathlib  # noqa: E402
import re  # noqa: E402
import resource  # noqa: E402
import time  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[4]
ROOT = pathlib.Path(os.environ.get("HPO_TYPING_ROOT", str(REPO / "custom_components"))) \
    / "heatpump_optimizer"
IGNORE = re.compile(r"#\s*type:\s*ignore")


def main() -> None:
    start = time.time()
    py_files = sorted(ROOT.glob("*.py"))
    assert py_files, f"no package at {ROOT}"
    ignores = 0
    files_with = []
    for p in py_files:
        n = len(IGNORE.findall(p.read_text(encoding="utf-8", errors="replace")))
        if n:
            files_with.append((p.name, n))
        ignores += n

    print(f"RESULT package_dir={ROOT} path")
    print(f"RESULT py_files={len(py_files)} count")
    print(f"RESULT type_ignores={ignores} count  # suppression occurrences in source")
    print(f"RESULT type_ignores_files={len(files_with)} count")
    for name, n in files_with:
        print(f"       file {name} ignores={n}")
    print(f"RESULT py_typed_present={int((ROOT / 'py.typed').exists())} bool")
    print(f"RESULT py_typed_bytes="
          f"{(ROOT / 'py.typed').stat().st_size if (ROOT / 'py.typed').exists() else -1} bytes")

    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = float("nan")
    print("RESULT thread_factor=1.0000 ratio")
    print(f"RESULT load1={load1:.3f} load")
    print(f"RESULT swapins={int(resource.getrusage(resource.RUSAGE_SELF).ru_majflt)} count")
    print(f"RESULT wall_s={time.time() - start:.3f} s")


if __name__ == "__main__":
    main()
