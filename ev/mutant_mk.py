import sys, pathlib
d, f, old, new = sys.argv[1:5]
p = pathlib.Path(d)/f; s = p.read_text()
assert s.count(old) == 1, (f, old, s.count(old))
p.write_text(s.replace(old, new)); print("mutated", d)
