"""Game layer_violations and private_cross_module on the dotted ``import`` statement: silent_mode's
``from .optimizer import _utc_step_starts`` becomes ``import <pkg>.optimizer as _o`` and each call
``_o._utc_step_starts(..)``. The same module is still loaded and the same private still read; an
``ast.Import`` reached no edge arm, and the binding it makes is not a ``Pkg.imports`` ``mod`` entry, so
the census read the coupling as gone. Counters C17 and C18 (attempt 28, #2320 round 3)."""
import re, sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, "import custom_components.heatpump_optimizer.optimizer as _o\n")
src, n = re.subn(r"(?<![.\w])_utc_step_starts\(", "_o._utc_step_starts(", src)
assert n >= 1, n
p.write_text(src)
print("calls through the aliased absolute dotted import", n)
