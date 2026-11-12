#!/usr/bin/env python3
"""Run one block of tests/features.py, from a marker line to the next block.

    python3 tools/audit/seat/features_block.py [--prelude 'import line']... "<first line of the block>" [END]
    python3 tools/audit/seat/features_block.py [--prelude 'import line']... --through "<marker line>"
    python3 tools/audit/seat/features_block.py --emit-prelude OUT "<first line of the block>" [END]

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

``--emit-prelude OUT`` writes to OUT the earlier top-level statements the
block reads, found by running it until no ``NameError`` is left: each missing
name takes its last binding before the use (before the block, or before the
prelude statement that needed it at module level). Run the block with
``--prelude 'exec(open("OUT").read())'``. It derives from the tree it runs on,
so a mutant run needs no hand-copied prelude; exits 0 once the block runs
without raising (its checks are not judged), 1 on a name no earlier statement
binds or on any other exception.

``--self-test`` runs offline: it executes a two-check block it writes itself.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
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


def _binders(source: str, start: str) -> dict[str, list[ast.stmt]]:
    """Each name's top-level binding statements between the header and the block, in order."""
    lo = source[: source.index('R = Results("Feature modules")')].count("\n") + 1
    hi = source[: source.index(start)].count("\n") + 1
    out: dict[str, list[ast.stmt]] = {}
    for n in ast.parse(source).body:
        if not lo < n.lineno < hi:
            continue
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names = {n.name}
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            names = {(a.asname or a.name).split(".")[0] for a in n.names}
        elif isinstance(n, (ast.Assign, ast.AnnAssign)):
            targets = n.targets if isinstance(n, ast.Assign) else [n.target]
            names = {x.id for t in targets for x in ast.walk(t) if isinstance(x, ast.Name)}
        else:
            continue
        for name in names:
            out.setdefault(name, []).append(n)
    return out


def emit_prelude(path: str, start: str, end: str, out: str) -> int:
    """Write the statements the block reads from earlier to ``out``; 0 once it runs without a NameError."""
    source = open(path, encoding="utf-8").read()
    lines, binders = source.splitlines(keepends=True), _binders(source, start)
    block_line = source[: source.index(start)].count("\n") + 1
    chosen: list[ast.stmt] = []
    while True:
        text, origin = "", []
        for n in sorted(chosen, key=lambda n: n.lineno):
            seg = "".join(lines[n.lineno - 1:n.end_lineno])
            text, origin = text + seg, origin + [n.lineno] * seg.count("\n")
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        cmd = [sys.executable, os.path.abspath(__file__), "--prelude", f"exec(open({out!r}).read())", start, end]
        root = os.path.dirname(os.path.dirname(os.path.abspath(path)))
        err = subprocess.run(cmd, capture_output=True, text=True, cwd=root).stderr
        missing = re.findall(r"NameError: name '(\w+)' is not defined", err)
        if "Traceback" not in err:
            print(f"features_block: prelude of {len(chosen)} statement(s) written to {out}")
            return 0
        if not missing:
            print(f"features_block: the block raised other than a NameError:\n{err[-2000:]}")
            return 1
        at = re.findall(r'File "<string>", line (\d+), in <module>', err)
        before = origin[int(at[-1]) - 1] if at else block_line
        found = [n for n in binders.get(missing[-1], []) if n.lineno < before]
        if not found or found[-1] in chosen:
            print(f"features_block: no earlier statement binds {missing[-1]!r} before line {before}")
            return 1
        chosen.append(found[-1])


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
        check("_main: a block with --prelude passes", _main(["--prelude", "import math", "second block"], path) == 0)
        check("_main: --through takes the marker and no block", _main(["--through", "second block"], path) == 0)
        check("_main: --through with a block, or no argument, is a usage error, rc 2",
              _main(["--through", "second block", "first block"], path) == 2 and _main([], path) == 2)
        bad = fake.replace("seed = 5", "seed = 6")
        open(path, "w").write(bad)
        check("--through reports the prefix's own failure (null control)", run(path, None, upto="second block") == 1)
        open(path, "w").write(fake.replace("seed = 5\n", "import math\nseed = 4\ndef f(): return seed\nseed = 5\n")
                              .replace("R.bad += math.floor(2.5) != 2\n", "R.bad += math.floor(2.5) != 2 or f() != 5\n"))
        prel = os.path.join(tmp, "prel.py")
        emitted = emit_prelude(path, "second block", CLOSE, prel)
        body = open(prel).read()
        passed = run(path, "second block", prelude=(f"exec(open({prel!r}).read())",))
        check("--emit-prelude takes each name's last earlier binding and the block passes on it",
              emitted == 0 and body == "import math\ndef f(): return seed\nseed = 5\n" and passed == 0)
        open(path, "w").write(fake.replace("math.floor", "nowhere.floor"))
        check("--emit-prelude refuses a name no earlier statement binds (null control)",
              emit_prelude(path, "second block", CLOSE, prel) == 1)
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


def _main(argv: list[str], path: str = "tests/features.py") -> int:
    prelude, upto, emit, pos = [], None, None, []
    it = iter(argv)
    for a in it:
        if a == "--prelude":
            prelude.append(next(it, ""))
        elif a == "--through":
            upto = next(it, None)
        elif a == "--emit-prelude":
            emit = next(it, None)
        else:
            pos.append(a)
    if upto is not None and pos or upto is None and not pos or emit is not None and upto is not None:
        print(__doc__)
        return 2
    if emit is not None:
        return emit_prelude(path, pos[0], *(pos[1:2] or [CLOSE]), out=emit)
    return run(path, pos[0] if pos else None, *pos[1:2], prelude=tuple(prelude), upto=upto)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--self-test"]:
        sys.exit(_self_test())
    sys.exit(_main(sys.argv[1:]))
