"""B1 (BAD): copy coordinator._as_float (18 lines) verbatim into pump_arbiter.py
and use the copy there -- a cross-module clone.
"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import PKG, read, write, replace_once
from _b1_common import as_float_source

rel = f"{PKG}/pump_arbiter.py"
s = read(rel)
s = replace_once(s, "from typing import Any\n", "from typing import Any\n\nimport numpy as np\n")
s = replace_once(s, "\ndef state_for(coord: Any) -> ArbiterState:", "\n" + as_float_source("_as_float") + "\n\ndef state_for(coord: Any) -> ArbiterState:")
s = replace_once(s, "    configured = float(coord._thermal_params.dhw_setpoint)\n",
                 "    configured = _as_float(coord._thermal_params.dhw_setpoint, 55.0)\n")
write(rel, s)
