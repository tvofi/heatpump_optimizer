"""Game layer_violations by re-spelling a PUBLIC higher-layer import through the namespace ABOVE the
package: price_model's ``from .inputs import normalize_price_per_kwh`` becomes ``import custom_components
as _cc`` and each call ``_cc.heatpump_optimizer.inputs.normalize_price_per_kwh(..)``. The name is public,
so there is no crossing to take -- but the module is still reached, and the statement above the package
loads nothing of ours, so the EDGE has to come from the read. Counter C17 (attempt 38, #2320 round 4)."""
import re, sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "price_model.py"
src = p.read_text()
line = "from .inputs import normalize_price_per_kwh\n"
assert src.count(line) == 1
src = src.replace(line, "import custom_components as _cc\n")
src, n = re.subn(r"(?<![.\w])normalize_price_per_kwh\(",
                 "_cc.heatpump_optimizer.inputs.normalize_price_per_kwh(", src)
assert n >= 1, n
p.write_text(src)
print("public calls through the namespace below the package", n)
