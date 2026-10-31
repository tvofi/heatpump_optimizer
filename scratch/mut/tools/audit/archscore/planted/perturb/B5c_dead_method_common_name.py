"""B5c (BAD): a dead method whose NAME happens to be referenced somewhere else
in the package (``summary`` -- read as ``self._freq_map.summary(...)`` on a
different class). Nothing calls the coordinator's ``summary``.
"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, COORD_CLASS, read, write, insert_after_method, seam_set

s = read(COORD)
s = insert_after_method(s, COORD_CLASS, "_plan_age_minutes", '''    def summary(self) -> dict[str, Any]:
        """A one-line plan summary (nothing calls this)."""
        return {"age_minutes": self._plan_age_minutes(), "mode": self._mode}
''')
write(COORD, s)
seam_set("summary", "core")
