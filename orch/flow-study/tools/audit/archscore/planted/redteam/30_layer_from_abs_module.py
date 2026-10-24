"""Game private_cross_module through a module binding made by an absolute from-import: silent_mode's
``from .optimizer import _utc_step_starts`` becomes ``from <pkg> import optimizer as _o`` and each call
``_o._utc_step_starts(..)``. ``_targets`` resolved the edge (so ``layer_violations`` held), but the
binding ``_o`` comes from a statement ``Pkg.imports`` files as external, so it was in no ``modalias``
and the private read off it was no crossing. Counters C17 and C18 (attempt 30, #2320 round 3)."""
import re, sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, "from custom_components.heatpump_optimizer import optimizer as _o\n")
src, n = re.subn(r"(?<![.\w])_utc_step_starts\(", "_o._utc_step_starts(", src)
assert n >= 1, n
p.write_text(src)
print("calls through the absolute from-import's module binding", n)
