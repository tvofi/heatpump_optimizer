"""Game layer_violations by re-spelling a PUBLIC higher-layer from-import through the namespace ABOVE the
package: disinfection's ``from .inputs import UNBOUNDED, parse_bool`` becomes ``import custom_components
as _cc`` and both reads the full dotted path ``_cc.heatpump_optimizer.inputs.*``. Two public names of the
same module, no crossing either way, and the same reach. Counter C17 (attempt 39, #2320 round 4)."""
import re, sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "disinfection.py"
src = p.read_text()
line = "from .inputs import UNBOUNDED, parse_bool\n"
assert src.count(line) == 1
src = src.replace(line, "import custom_components as _cc\n")
src, n = re.subn(r"(?<![.\w])parse_bool\(", "_cc.heatpump_optimizer.inputs.parse_bool(", src)
assert n >= 1, n
src, m = re.subn(r"(?<![.\w])UNBOUNDED(?![.\w])", "_cc.heatpump_optimizer.inputs.UNBOUNDED", src)
assert m >= 1, m
p.write_text(src)
print("public calls and constants through the namespace below the package", n, m)
