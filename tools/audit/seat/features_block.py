#!/usr/bin/env python3
"""Run one block of tests/features.py, from a marker line to the next block.

    python3 tools/audit/seat/features_block.py [--prelude 'import line']... "<first line of the block>" [END]
    python3 tools/audit/seat/features_block.py [--prelude 'import line']... --through "<marker line>"

features.py runs every block in one process, which takes tens of minutes on a
loaded seat; a mutation proof needs only the block that pins the mutated line.
The block is the text from the line containing START up to END (default: the
script's closing ``sys.exit``), executed in the namespace features.py's own
header builds -- ``R``, ``Coord``, the harness fakes -- with ``__file__``
pointing at features.py, so path arithmetic inside the block resolves as in
the full run. Exit status is the block's ``R.close``: 0 when every check passed.
Run from the repository root under the CI venv.

``--prelude`` (repeatable) runs one line, typically an import an earlier block
made, before the block. ``--through MARKER`` takes no block: it runs the whole
script from the top up to the line holding MARKER, the state every earlier
block builds, and exits with that prefix's ``R.close``.

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


def through(source: str, marker: str) -> str:
    """The script from the header's end up to the line holding ``marker``."""
    i = source.rindex("\n", 0, source.index(marker)) + 1
    return source[source.index('R = Results("Feature modules")'):i]


def run(path: str, start: str | None, end: str = CLOSE, prelude: tuple = (), upto: str | None = None) -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(path)))
    sys.path[:0] = [os.path.join(root, p) for p in ("tests/hastub", "custom_components", "tests")]
    source = open(path, encoding="utf-8").read()
    header = source[: source.index('R = Results("Feature modules")')]
    ns: dict = {"__file__": os.path.abspath(path), "__name__": "features_block"}
    exec(compile(header, path, "exec"), ns)
    exec(compile('R = Results("features block")', path, "exec"), ns)
    for line in prelude:
        exec(compile(line, f"{path}[prelude]", "exec"), ns)
    if upto is not None:
        exec(compile(through(source, upto), f"{path}[through]", "exec"), ns)
        return ns["R"].close("FEATURES THROUGH")
    exec(compile(block(source, start, end), f"{path}[block]", "exec"), ns)
    return ns["R"].close("FEATURES BLOCK")


def _self_test() -> int:
    import shutil
    import tempfile
    results = []

    def check(name: str, ok: bool) -> None:
        results.append(ok)
        print(("  ok  " if ok else "  FAIL") + " " + name)

    src = "a\n# start here\nx = 1\n# next\n" + CLOSE + "\n"
    check("a block runs from its marker line to the close",
          block(src, "start here") == "# start here\nx = 1\n# next\n"
          and block(src, "start here", "# next") == "# start here\nx = 1\n")
    fake = (
        "class Results:\n"
        "    def __init__(self, name): self.bad = 0\n"
        "    def close(self, name): return self.bad\n"
        'R = Results("Feature modules")\n'
        "seed = 5\n"
        "# first block\n"
        "R.bad += seed != 5\n"
        "# second block\n"
        "R.bad += math.floor(2.5) != 2\n"
        + CLOSE + "\n")
    check("through stops before the marker line", through(fake, "second block").endswith("R.bad += seed != 5\n")
          and "math" not in through(fake, "second block"))
    tmp = tempfile.mkdtemp(prefix="fblock-")
    try:
        os.makedirs(os.path.join(tmp, "tests"))
        path = os.path.join(tmp, "tests", "features.py")
        open(path, "w").write(fake)
        check("a block needing an import an earlier block made fails without --prelude",
              _expect_error(lambda: run(path, "second block"), NameError))
        check("--prelude supplies that import and the block passes", run(path, "second block", prelude=("import math",)) == 0)
        check("--through runs the prefix and the state it builds, no block", run(path, None, upto="second block") == 0)
        bad = fake.replace("seed = 5", "seed = 6")
        open(path, "w").write(bad)
        check("--through reports the prefix's own failure (null control)", run(path, None, upto="second block") == 1)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    failed = results.count(False)
    print(f"features_block self-test: {len(results)} checks, {failed} failed")
    return 1 if failed else 0


def _expect_error(fn, exc) -> bool:
    try:
        fn()
    except exc:
        return True
    return False


def _main(argv: list[str]) -> int:
    prelude, upto, pos = [], None, []
    it = iter(argv)
    for a in it:
        if a == "--prelude":
            prelude.append(next(it, ""))
        elif a == "--through":
            upto = next(it, None)
        else:
            pos.append(a)
    if upto is not None and pos or upto is None and not pos:
        print(__doc__)
        return 2
    return run("tests/features.py", pos[0] if pos else None, *pos[1:2], prelude=tuple(prelude), upto=upto)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--self-test"]:
        sys.exit(_self_test())
    sys.exit(_main(sys.argv[1:]))
