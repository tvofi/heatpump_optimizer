import sys
p, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(p).read()
n = s.count(old)
if n != 1: sys.exit(f"anchor count {n}: {old!r}")
open(p, "w").write(s.replace(old, new))
