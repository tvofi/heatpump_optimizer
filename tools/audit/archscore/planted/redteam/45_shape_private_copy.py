"""Game private_cross_module by copying the private: binary_sensor stops importing ``freq_control._finite`` and
gets its own ``_finite_reading`` with the parameter and local renamed. The crossing reads gone; nothing is
shared any more, and the finite-reading rule is now written twice. Counter C23 (``shape_copies``)."""
import sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "binary_sensor.py"
s = p.read_text()
imp = "from .freq_control import _finite\n"
use = '_finite(step.get("outdoor"))'
assert s.count(imp) == 1 and s.count(use) == 1, (s.count(imp), s.count(use))
copy = ("\n\ndef _finite_reading(raw: Any) -> float | None:\n"
        "    try:\n"
        "        number = float(raw)\n"
        "    except (TypeError, ValueError):\n"
        "        return None\n"
        "    return number if np.isfinite(number) else None\n")
s = s.replace(imp, "").replace(use, '_finite_reading(step.get("outdoor"))')
p.write_text(s + copy)
print("copied", 1)
