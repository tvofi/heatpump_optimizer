import sys
sys.path.insert(0, "tools/audit/archscore")
from metrics import common as C
from metrics.footprint import coord_footprint
root = sys.argv[1]
pkg = C.load(root)
eng = C.engine(pkg) if hasattr(C, "engine") else None
total, charged = coord_footprint(pkg, eng)
print("TOTAL", total)
for c in charged: print(c)
