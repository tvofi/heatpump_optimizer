"""Run one tests/features.py block on its own: the suite's prologue plus the block.

The mutation proof runs once per mutant and the full suite is 3588 checks, so a
block that carries its own fixtures can be sliced out and run in seconds. This
execs tests/features.py's own prologue -- everything up to and including the
``Results`` instance the checks report to -- and then the source between two
markers, verbatim. Nothing here restates an assertion: the checks that run are
the suite's own bytes, so a mutant that fools this runner fools the suite too.

    PYTHONPATH=tests/hastub python3 \
        tools/audit/handoff/r9-f2-solver-4/run_block.py \
        [--begin '# -- R9-F2.4:'] [--end '# -- R9-F2.5:']

Exit status is the block's own: 1 when any check in it failed. A marker that is
not found is an error, not an empty run -- a slice that silently matched nothing
would report zero checks and read as a pass.
"""
from __future__ import annotations

import argparse
import os
import sys

PROLOGUE_END = 'R = Results("Feature modules")'


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", default="tests/features.py")
    ap.add_argument("--begin", default="# -- R9-F2.4:")
    ap.add_argument("--end", default="# -- R9-F2.5:")
    a = ap.parse_args()

    # `python tests/features.py` gets its own directory on sys.path for free and
    # imports `harness` from it; this runner lives elsewhere, so put the suite's
    # directory there itself. harness.py then adds "tests" and
    # "custom_components" relative to the cwd, which is the tree under
    # measurement -- the same rule the round-9 harnesses state.
    sys.path.insert(0, os.path.dirname(os.path.abspath(a.features)))

    with open(a.features, encoding="utf-8") as fh:
        src = fh.read()
    for needle in (a.begin, a.end, PROLOGUE_END):
        if needle not in src:
            print(f"REFUSED: {needle!r} not in {a.features}")
            return 2
    cut = src.index(PROLOGUE_END) + len(PROLOGUE_END)
    start = src.index(a.begin)
    stop = src.index(a.end, start)
    if not start < stop:
        print("REFUSED: the end marker precedes the begin marker")
        return 2
    prologue, block = src[:cut], src[start:stop]
    ns: dict = {"__name__": "__r9f24_block__", "__file__": a.features}
    exec(compile(prologue, a.features, "exec"), ns)  # noqa: S102
    exec(compile(block, a.features, "exec"), ns)  # noqa: S102
    print(f"RESULT block_lines={block.count(chr(10))} count")
    return int(ns["R"].close("R9-F2.4 BLOCK CHECKS"))


if __name__ == "__main__":
    raise SystemExit(main())
