#!/usr/bin/env python3
"""D10 round-5 — strict-typing (Platinum) rule instrument, the brief's arm.

METRIC DEFINITION (one line): the number of `error:` lines mypy --strict emits
for `custom_components/heatpump_optimizer`, split by error code, with
`tests/hastub` on MYPYPATH (the brief's "the stub on the path"), plus the
subset of those lines that locate INSIDE the stub (leakage, which the in-tree
ruler's construction guard treats as disqualifying).

COMMAND (run from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round5/D10/typing_brief.py [--mypy PATH]

EXPECTED: RESULT mypy_error_lines=<n>; RESULT mypy_errors_under_package=<n>;
RESULT stub_leakage_lines=<n>; RESULT py_typed_present=0 (the marker file is
absent from the package, which is the second half of the rule).

INSTRUMENTED SYMBOL: custom_components/heatpump_optimizer (whole package), the
same PACKAGE_REL argument the in-tree ruler `tests/typing_ruler.py` passes;
the flags are copied from that file (lines 379-387) so the two runs are the
same command. What differs from the ruler is the STUB: the ruler is stub-free
and pinned to homeassistant-stubs==2026.2.3 (needs Python >= 3.13.2, absent on
this box), this arm puts the vendored `tests/hastub` on MYPYPATH, exactly what
the D10 brief asks for. The two numbers are therefore NOT interchangeable and
are labelled separately here.

PERTURBATION: delete a required annotation, e.g. change
`sensor: SensorEntity` to `sensor` in any entity `__init__`, or drop the
`-> None` from a handler in `__init__.py` -> mypy_error_lines rises. Creating
`custom_components/heatpump_optimizer/py.typed` -> py_typed_present 0 -> 1.

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

import collections  # noqa: E402
import pathlib  # noqa: E402
import re  # noqa: E402
import resource  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[4]
PKG_REL = "custom_components/heatpump_optimizer"
ERROR_RE = re.compile(
    r"^(?P<path>.+?):\d+(?::\d+)?: error: (?P<msg>.*?)(?:  \[(?P<code>[a-z-]+)\])?$"
)
IGNORE_RE = re.compile(r"#\s*type:\s*ignore")


def find_mypy(argv: list[str]) -> str:
    if "--mypy" in argv:
        return argv[argv.index("--mypy") + 1]
    env = os.environ.get("HPO_MYPY")
    if env:
        return env
    return "mypy"


def main() -> None:
    start_wall = time.time()
    mypy = find_mypy(sys.argv[1:])

    env = dict(os.environ)
    env["MYPYPATH"] = str(ROOT / "tests" / "hastub")
    env["PYTHONPATH"] = str(ROOT / "tests" / "hastub")

    with tempfile.TemporaryDirectory() as cache:
        proc = subprocess.run(
            [
                mypy,
                "--strict",
                "--warn-unused-ignores",
                "--show-error-codes",
                "--no-error-summary",
                "--no-incremental",
                "--cache-dir", cache,
                "--python-version", "3.13",
                PKG_REL,
            ],
            cwd=ROOT, capture_output=True, text=True, env=env,
        )

    lines = (proc.stdout + proc.stderr).splitlines()
    total = 0
    under_pkg = 0
    leak = 0
    by_code: collections.Counter[str] = collections.Counter()
    for line in lines:
        if ": error:" not in line:
            continue
        total += 1
        m = ERROR_RE.match(line)
        code = (m.group("code") if m and m.group("code") else "no-code")
        by_code[code] += 1
        path = m.group("path") if m else ""
        if PKG_REL in path:
            under_pkg += 1
        elif "hastub" in path:
            leak += 1

    print(f"RESULT mypy={pathlib.Path(mypy).name} tool")
    print(f"RESULT mypy_returncode={proc.returncode} code")
    print(f"RESULT mypy_error_lines={total} count")
    print(f"RESULT mypy_errors_under_package={under_pkg} count")
    print(f"RESULT stub_leakage_lines={leak} count")
    for code, n in sorted(by_code.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"RESULT by_code[{code}]={n} count")
    print(f"RESULT py_typed_present={int((ROOT / PKG_REL / 'py.typed').exists())} bool")
    ignores = 0
    for f in (ROOT / PKG_REL).rglob("*.py"):
        ignores += len(IGNORE_RE.findall(f.read_text(encoding="utf-8", errors="replace")))
    print(f"RESULT type_ignore_occurrences={ignores} count")

    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = float("nan")
    print(f"RESULT thread_factor=1.0000 ratio")
    print(f"RESULT load1={load1:.3f} load")
    print(f"RESULT swapins={int(resource.getrusage(resource.RUSAGE_SELF).ru_majflt)} count")
    print(f"RESULT wall_s={time.time() - start_wall:.3f} s")


if __name__ == "__main__":
    main()
