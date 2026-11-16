"""Reviewer's reproduction (the reviewer's instrument, not the finder's): corpus_mirror.safe_extract."""
import io, sys, zipfile, tempfile, traceback, importlib
from pathlib import Path
sys.path.insert(0, "tools/audit/seat")
cm = importlib.import_module("corpus_mirror")
def z(members):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", zipfile.ZIP_DEFLATED) as f:
        for n, d in members: f.writestr(n, d)
    return b.getvalue()
for label, members in [("null control: a, b/c", [("a", b"x"), ("b/c", b"y")]),
                       ("member named '.'", [(".", b"x")]),
                       ("members 'a' then 'a/b'", [("a", b"x"), ("a/b", b"y")])]:
    d = Path(tempfile.mkdtemp()) / "out"
    try:
        print(f"{label}: returned {cm.safe_extract(z(members), d)!r}")
    except Exception as e:
        print(f"{label}: RAISED {type(e).__name__} (uncaught by safe_extract)")
# caps: a member past MAX_MEMBER / archive past MAX_ARCHIVE, with the real caps lowered so the fixture is small
for cap in ("MAX_MEMBER", "MAX_ARCHIVE"):
    old = getattr(cm, cap); setattr(cm, cap, 10)
    d = Path(tempfile.mkdtemp()) / "out"
    # incompressible-ish so the ratio cap does not fire first
    import os
    data = os.urandom(64)
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", zipfile.ZIP_STORED) as f: f.writestr("m", data)
    print(f"{cap}=10, one stored 64-byte member: returned {cm.safe_extract(b.getvalue(), d)!r}")
    setattr(cm, cap, old)
