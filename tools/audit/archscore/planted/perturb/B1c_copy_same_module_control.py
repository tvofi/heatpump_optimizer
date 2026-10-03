"""B1c (BAD, detector control): the same 18-line clone as B1, but placed in the
SAME module (coordinator.py, as _as_float_copy, used once). Shows the
duplication detector does fire on a clone -- when it is in the same file.
"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, read, write, replace_once
from _b1_common import as_float_source

s = read(COORD)
s = replace_once(s, "\ndef _storable_sample_count(raw: Any) -> int:", "\n" + as_float_source("_as_float_copy") + "\n\ndef _storable_sample_count(raw: Any) -> int:")
s = replace_once(s, "    return None if temperature is None else _as_float(temperature, 5.0)\n",
                 "    return None if temperature is None else _as_float_copy(temperature, 5.0)\n")
write(COORD, s)
