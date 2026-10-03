"""B3a (BAD): split the tree's max-CC function (optimizer.HeatPumpOptimizer.optimize,
CC 48, 376 LOC) into a meaningless pass-through chain: cut its top-level body at
the statement boundaries nearest 25/50/75 % of its span; each fragment
receives every live local as a parameter and ends by tail-calling the next.
No fragment is a concept; the control flow and data are exactly as tangled.
"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import PKG, read, write, pick_cuts, tail_extract

rel = f"{PKG}/optimizer.py"
cls, name = "HeatPumpOptimizer", "optimize"
s = read(rel)
cuts = pick_cuts(s, cls, name)
assert len(cuts) == 3, cuts
for i, k in reversed(list(enumerate(cuts, 1))):
    s, _ = tail_extract(s, cls, name, k, f"_{name}_part{i}")
write(rel, s)
print("cuts", cuts)
