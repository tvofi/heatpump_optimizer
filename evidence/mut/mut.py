import sys
path, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(path).read()
n = s.count(old)
if n != 1:
    sys.exit("anchor occurs %d times in %s: %r" % (n, path, old))
open(path, "w").write(s.replace(old, new))
