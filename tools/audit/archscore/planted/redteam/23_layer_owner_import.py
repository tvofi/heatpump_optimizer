"""Game layer_bound by importing the boundary: every module that reaches scipy only through another package
module gains its own ``import scipy  # noqa: F401``. Nothing is decoupled; a count of modules that reach the
boundary WITHOUT importing it would read each as no longer a leak. layer_bound counts the modules a boundary
binds, importing it or reaching it, so the move reads as nothing."""
import sys
from rt_lib import pkg, metric
root = sys.argv[1]
reach = metric("layering", root)["details"]["reach"]["scipy"]
assert reach, "no module reaches scipy through another"
for m in reach:
    p = pkg(root) / (m.replace(".", "/") + ".py")
    src = p.read_text()
    anchor = "from __future__ import annotations\n"
    p.write_text(src.replace(anchor, anchor + "\nimport scipy  # noqa: F401,E402\n", 1) if anchor in src
                 else "import scipy  # noqa: F401\n" + src)
print("own scipy import added to", len(reach))
