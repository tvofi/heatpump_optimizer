import sys
path, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(path).read()
assert s.count(old) == 1, (old, s.count(old))
open(path, "w").write(s.replace(old, new))
