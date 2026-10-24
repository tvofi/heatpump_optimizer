#!/usr/bin/env python3
"""Run one block of tests/features.py, from a marker line to the next block.

    python3 tools/audit/seat/features_block.py "<first line of the block>" [END]

features.py runs every block in one process, which takes tens of minutes on a
loaded seat; a mutation proof needs only the block that pins the mutated line.
The block is the text from the line containing START up to END (default: the
script's closing ``sys.exit``), executed in the namespace features.py's own
header builds -- ``R``, ``Coord``, the harness fakes -- with ``__file__``
pointing at features.py, so path arithmetic inside the block resolves as in
the full run. Exit status is the block's ``R.close``: 0 when every check passed.
Run from the repository root under the CI venv.

``--self-test`` runs offline: it executes a two-check block it writes itself.
"""
from __future__ import annotations

import os
import sys

CLOSE = 'sys.exit(R.close("FEATURE CHECKS"))'


def block(source: str, start: str, end: str = CLOSE) -> str:
    """The text of the block whose first line contains ``start``."""
    i = source.rindex("\n", 0, source.index(start)) + 1
    return source[i:source.index(end, i)]


def run(path: str, start: str, end: str = CLOSE) -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(path)))
    sys.path[:0] = [os.path.join(root, p) for p in ("tests/hastub", "custom_components", "tests")]
    source = open(path, encoding="utf-8").read()
    header = source[: source.index('R = Results("Feature modules")')]
    ns: dict = {"__file__": os.path.abspath(path), "__name__": "features_block"}
    exec(compile(header, path, "exec"), ns)
    exec(compile('R = Results("features block")', path, "exec"), ns)
    exec(compile(block(source, start, end), f"{path}[block]", "exec"), ns)
    return ns["R"].close("FEATURES BLOCK")


def _self_test() -> int:
    src = "a\n# start here\nx = 1\n# next\n" + CLOSE + "\n"
    ok = block(src, "start here") == "# start here\nx = 1\n# next\n"
    ok = ok and block(src, "start here", "# next") == "# start here\nx = 1\n"
    print(("  ok  " if ok else "  FAIL") + " a block runs from its marker line to the close")
    print(f"features_block self-test: 1 checks, {0 if ok else 1} failed")
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1:2] == ["--self-test"]:
        sys.exit(_self_test())
    sys.exit(run("tests/features.py", *sys.argv[1:3]))
