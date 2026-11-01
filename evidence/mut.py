import sys, pathlib
p = pathlib.Path("tests/doc_claims.py"); s = p.read_text()
old, new = sys.argv[1], sys.argv[2]
assert s.count(old) == 1, (old, s.count(old)); p.write_text(s.replace(old, new))
