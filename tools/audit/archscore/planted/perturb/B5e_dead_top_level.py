"""B5e (BAD, detector control): a dead top-level function in pump_arbiter.py."""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import PKG, read, write, replace_once

rel = f"{PKG}/pump_arbiter.py"
s = read(rel)
s = replace_once(s, "\ndef state_for(coord: Any) -> ArbiterState:", '''
def _duty_label_unused(duty: str | None) -> str:
    """Human label for a duty (nothing calls this)."""
    return "none" if duty is None else duty.replace("_", " ")


def state_for(coord: Any) -> ArbiterState:''')
write(rel, s)
