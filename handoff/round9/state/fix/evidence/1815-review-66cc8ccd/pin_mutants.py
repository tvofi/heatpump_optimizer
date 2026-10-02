"""Run the round-2 base_closures pin in isolation, unmutated and under three mutants."""

import contextlib
import io
import json
import subprocess
import sys

sys.path.insert(0, "tests")
import closure as _closure

_CJ = "tests/closures.json"
_CJ_HEAD = json.loads(_closure.CLOSURES.read_text())["closures"]
REAL = _closure.base_closures


def table(rev):
    s = subprocess.run(
        ["git", "show", f"{rev}:{_CJ}"],
        cwd=_closure.ROOT,
        capture_output=True,
        text=True,
    )
    return json.loads(s.stdout)["closures"] if s.returncode == 0 else None


def pin():
    revs = subprocess.run(
        ["git", "log", "--format=%H", "--", _CJ],
        cwd=_closure.ROOT,
        capture_output=True,
        text=True,
    ).stdout.split()
    anc = next((f"{r}^" for r in revs if table(f"{r}^") not in (None, _CJ_HEAD)), None)
    seen = []
    sel, argv = _closure.select, sys.argv

    def spy(files, base=None):
        seen.append(base)
        return sel(files, base)

    _closure.select = spy
    sys.argv = [
        "closure.py",
        "select",
        "--files",
        _CJ,
        "--diff",
        anc or "HEAD",
        "--json",
    ]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            _closure.main()
    finally:
        _closure.select, sys.argv = sel, argv
    return (
        anc is not None
        and _closure.base_closures(anc) == table(anc) != _CJ_HEAD
        and seen == [table(anc)]
        and _closure.base_closures("refs/heads/no-such-ref-r9-f10-9") is None
    ), anc


print("unmutated  pass=%s anc=%s" % pin())
_closure.base_closures = lambda ref: table("HEAD")
print("M-HEAD     pass=%s" % (pin()[0],))
_closure.base_closures = REAL
src = open("tests/closure.py").read()
# M-None: main passes None
_closure.base_closures = lambda ref: None
print("M-NONE     pass=%s" % (pin()[0],))
_closure.base_closures = REAL
