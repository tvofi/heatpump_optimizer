"""G1 (GOOD): extract a cohesive block of a big coordinator method into a named helper.

_update_current_state (289 LOC, CC 44, the coordinator's worst CC) reads the
wood tank's two probes inline. The block has no outputs (it writes only
ctx._current_state.wood_tank_temperature) and two inputs (reader, ctx), so it
moves verbatim into ``_read_wood_tank_temperature(reader, ctx)`` -- the
textbook Extract Method. Seam: core (the host method's seam).
"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, COORD_CLASS, read, write, replace_once, insert_after_method, seam_set, find_method

src = read(COORD)
start = "        # Wood tank temperature (issue #40): re-read from the physical tank\n"
end = "            ctx._current_state.wood_tank_temperature = None\n"
i = src.index(start); j = src.index(end, i) + len(end)
assert src.count(start) == 1
block = src[i:j]
src = src[:i] + "        self._read_wood_tank_temperature(reader, ctx)\n" + src[j:]
body = block  # already at method-body indentation
helper = (
    "    def _read_wood_tank_temperature(self, reader: InputReader, ctx: Any) -> None:\n"
    '        """Wood tank mean from its two probes, stale-aware (issue #40)."""\n'
    + body
)
src = insert_after_method(src, COORD_CLASS, "_update_current_state", helper)
write(COORD, src)
seam_set("_read_wood_tank_temperature", "core")
