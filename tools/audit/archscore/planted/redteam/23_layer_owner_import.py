"""Game layer_violations by climbing a layer: every module that reaches a layer above its own gains an
import of that layer's boundary it never reads (``import homeassistant  # noqa: F401``). Nothing is
decoupled; the module's own layer rises to the one it reaches, so it reads as no longer violating. The
tripwire ``unused_boundary_imports`` refuses the climb. Counter C19."""
import sys
from rt_lib import pkg, metric
root = sys.argv[1]
d = metric("layering", root)["details"]
top = {1: "scipy", 2: "homeassistant"}
done = 0
for v in d["violations"]:
    m, ranks = v.split(" (")
    reached = int(ranks.rstrip(")").split(" -> ")[1])
    p = pkg(root) / (m.replace(".", "/") + ".py")
    src = p.read_text()
    anchor = "from __future__ import annotations\n"
    line = f"\nimport {top[reached]}  # noqa: F401,E402\n"
    p.write_text(src.replace(anchor, anchor + line, 1) if anchor in src else line.lstrip() + src)
    done += 1
assert done, "no violating module"
print("boundary imports added to", done)
