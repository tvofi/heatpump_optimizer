import sys
p, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(p).read(); assert s.count(old) == 1, s.count(old)
open(p, "w").write(s.replace(old, new))
