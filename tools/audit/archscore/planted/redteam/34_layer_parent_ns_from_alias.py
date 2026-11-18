"""Game private_cross_module through a from-import of the namespace ABOVE the package, aliased:
silent_mode's ``from .optimizer import _utc_step_starts`` becomes ``from custom_components import
heatpump_optimizer as _p`` and each call ``_p.optimizer._utc_step_starts(..)``. The alias binds the
namespace's child, which the import index files as a name outside the package, so the private read off
``_p`` crossed nothing. Counters C17 and C18 (attempt 34, #2320 round 3)."""
import re, sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, "from custom_components import heatpump_optimizer as _p\n")
src, n = re.subn(r"(?<![.\w])_utc_step_starts\(", "_p.optimizer._utc_step_starts(", src)
assert n >= 1, n
p.write_text(src)
print("calls through the parent namespace's aliased from-import", n)
