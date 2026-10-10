#!/usr/bin/env python3
"""Run ONLY features.py's early-cut-off block, from features.py's own source.

Executes, in one namespace, the real bytes of tests/features.py:
  * the module header (imports, Results, harness fakes),
  * the `_Coord` helper class and the `_asyncio`/`_FakeEntry` imports,
  * the pump-arbiter preamble that defines `_PaNS`/`_PaCoord`/`_PA_TUYA`/`_pa_aio`,
  * the early-cut-off block verbatim, to the file's final sys.exit.
Nothing is re-implemented: every check is features.py's own. Same idea as
tools/audit/seat/features_block.py, but with the two extra helper segments the
early-cut-off block needs (features_block.py's header-only namespace lacks them).

usage: miniec.py <features.py path>
exit status = the block's own R.close (0 = every early-cut-off check passed).
"""
from __future__ import annotations

import sys


def seg(source: str, start_marker: str, end_marker: str | None,
        back_to_line: bool = False, include_end_line: bool = False) -> str:
    i = source.index(start_marker)
    if back_to_line:
        i = source.rindex("\n", 0, i) + 1
    if end_marker is None:
        return source[i:]
    j = source.index(end_marker, i)
    j = source.rindex("\n", 0, j) + 1
    if include_end_line:
        j = source.index("\n", j) + 1
    return source[i:j]


def main(path: str) -> int:
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(path)))
    sys.path[:0] = [os.path.join(root, p) for p in ("tests/hastub", "custom_components", "tests")]
    source = open(path, encoding="utf-8").read()
    header = source[: source.index('R = Results("Feature modules")')]
    asyncio_imp = seg(source, "import asyncio as _asyncio", "def _zone_coord")
    pa_pre = seg(source, "import asyncio as _pa_aio", "\ndef _pa_run(")
    block = seg(source, "a warm room stops a space-heating pump", None, back_to_line=True)

    ns: dict = {"__file__": path, "__name__": "miniec"}
    exec(compile(header, path, "exec"), ns)          # noqa: S102
    exec(compile('R = __import__("harness").Results("Feature modules")', path, "exec"), ns)
    exec(compile(asyncio_imp, path, "exec"), ns)     # noqa: S102
    exec(compile(pa_pre, path, "exec"), ns)          # noqa: S102
    try:
        exec(compile(block, path + "[ec-block]", "exec"), ns)  # noqa: S102
    except SystemExit as exc:
        return int(exc.code or 0)
    return int(ns["R"].close("FEATURES EC BLOCK"))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
