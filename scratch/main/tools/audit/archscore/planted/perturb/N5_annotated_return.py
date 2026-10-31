"""N5 (NULL): type a returned value through an annotated local, the shape R9-EG-B3b (#1867) used to
type the payload producers: ``return view.as_dict()`` in coordinator._battery_view becomes
``out: dict[str, Any] = view.as_dict()`` then ``return out``. Behaviour and structure are unchanged.

The R9-EG-A4 wave comparison: #1867's review verdict was merge, and the score read it WORSENS,
inadmissible on coord_footprint +3 -- an annotated alias and a bare ``return <name>`` are logic
statements to the footprint, while the ``return cast(..)`` they replaced was plumbing. Recorded as
the score reads it (a miss), so a footprint fix flips it and asks for the re-record.
"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, edit

edit(COORD, "        return view.as_dict()\n",
     "        out: dict[str, Any] = view.as_dict()\n        return out\n")
print("annotated 1 return")
