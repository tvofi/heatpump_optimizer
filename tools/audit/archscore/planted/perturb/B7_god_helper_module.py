"""B7 (BAD): "move without decoupling" -- the same five frequency methods as G3,
moved to ``freq_helpers.py`` as free functions that take the coordinator and
reach into its privates (coord._freq_map, coord._freq_watchdog,
coord._freq_fallback, coord._freq_last_write, coord._commanded_power(),
coord._measured_power, coord._spawn, ...). The state stays on the coordinator;
every dependency the methods had is still there, now across a module
boundary and invisible to the class. The shape pump_arbiter.py / away.py /
boost.py already use (see coordinator.py:801 for the metric-driven rationale).
"""
import re
import sys
import textwrap
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, COORD_CLASS, PKG, read, write, replace_once, method_text, find_method
from _freq_common import drop_orphaned_const_imports, HEADER_IMPORTS, FREQ_METHODS, strip_cluster, drop_seams

src0 = read(COORD)
renames = {"_freq_entity_reading": "freq_entity_reading", "_freq_mode": "freq_mode",
           "_observe_frequency": "observe_frequency", "_command_frequency": "command_frequency",
           "_freq_view": "freq_view"}
funcs = []
for name in FREQ_METHODS:
    text = textwrap.dedent(method_text(src0, COORD_CLASS, name))
    text = re.sub(r"\bself\b", "coord", text)
    text = text.replace(f"def {name}(coord", f"def {renames[name]}(coord: Any", 1)
    for old, new in renames.items():
        text = text.replace(f"coord.{old}()", f"{new}(coord)")
    text = text.replace("_as_float(", "_finite(")
    funcs.append(text)
# the fold gate is module-level in coordinator.py and only this cluster uses it: it moves too
tree_fn = find_method(src0, None, "_freq_fold_blocked")
lines = src0.splitlines(keepends=True)
fold = "".join(lines[tree_fn.lineno - 1:tree_fn.end_lineno]).replace("coord._learning_frozen", "coord._learning_frozen")
MODULE = ('"""Inverter frequency helpers (#61): free functions over the coordinator."""\n'
          + HEADER_IMPORTS + "\n\n" + fold + "\n\n" + "\n\n".join(funcs))
MODULE = MODULE.replace("from collections.abc import Callable, Mapping\n", "").replace(
    "from homeassistant.core import HomeAssistant\n", "").replace(
    "    FrequencyMap,\n    FrequencyWatchdog,\n", "")
write(f"{PKG}/freq_helpers.py", MODULE)

src = strip_cluster(src0)
lines = src.splitlines(keepends=True)
fn = find_method(src, None, "_freq_fold_blocked")
src = "".join(lines[:fn.lineno - 1] + lines[fn.end_lineno:])
src = replace_once(src, "from .freq_control import (\n", "from . import freq_helpers\nfrom .freq_control import (\n")
src = replace_once(src, '''            await _best_effort_cycle_step(
                self._command_frequency, "Frequency command skipped: %s")''', '''            await _best_effort_cycle_step(
                lambda: freq_helpers.command_frequency(self),
                "Frequency command skipped: %s")''')
src = replace_once(src, "        self._observe_frequency(now)\n", "        freq_helpers.observe_frequency(self, now)\n")
src = replace_once(src, "self._freq_view()", "freq_helpers.freq_view(self)")
src = replace_once(src, '''from .freq_control import (
    FREQ_MODE_CONTROL,
    FREQ_MODE_OBSERVE,
    FREQ_SOURCE_NUMBER,
    FREQ_WRITE_EPSILON_HZ,
    FREQ_WRITE_MIN_INTERVAL_S,
    FrequencyMap,
    FrequencyWatchdog,
    resolve_reading,
)''', "from .freq_control import FREQ_MODE_CONTROL, FrequencyMap, FrequencyWatchdog")
write(COORD, drop_orphaned_const_imports(src))
drop_seams()
