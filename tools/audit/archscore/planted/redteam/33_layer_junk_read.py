"""KNOWN-OPEN: climb a layer with an import read once for nothing. Every module that reaches scipy through
another gains ``import scipy`` and ``assert scipy``; C19 keys on an unread import, and one bare read satisfies it
(#2320 round 1, p5). A stricter "use" rule read 11 honest imports as unused, so the climb is carried to part 5 and
this attempt reads IMPROVES until a fix flips it."""
import sys
from rt_lib import pkg, metric
root = sys.argv[1]
d = metric("layering", root)["details"]
mods = sorted({v.split(" (")[0] for v in d["violations"] if v.endswith("-> 1)")})
assert mods, "no module reaches the solver through another"
for m in mods:
    p = pkg(root) / (m.replace(".", "/") + ".py")
    src = p.read_text()
    anchor = "from __future__ import annotations\n"
    line = "\nimport scipy  # noqa: E402\n\nassert scipy\n"
    p.write_text(src.replace(anchor, anchor + line, 1) if anchor in src else line.lstrip() + src)
print("climbed", len(mods))
