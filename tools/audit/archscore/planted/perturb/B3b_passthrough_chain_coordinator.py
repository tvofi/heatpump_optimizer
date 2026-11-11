"""B3b (BAD): the same meaningless pass-through chain as B3a, applied to the
function G1 improves (coordinator._update_current_state, CC 44, 289 LOC), so
G1 and B3 can be compared on one function.
"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, COORD_CLASS, read, write, pick_cuts, tail_extract, seam_set

cls, name = COORD_CLASS, "_update_current_state"
s = read(COORD)
cuts = pick_cuts(s, cls, name)
assert len(cuts) == 3, cuts
for i, k in reversed(list(enumerate(cuts, 1))):
    s, new = tail_extract(s, cls, name, k, f"{name}_part{i}")
    seam_set(new, "core")
write(COORD, s)
print("cuts", cuts)
