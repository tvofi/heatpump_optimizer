import sys, os
path = "tests/entities.py"
sys.path[:0] = ["tests/hastub", "custom_components", "tests"]
src = open(path, encoding="utf-8").read()
h = src.index('R = Results("Entities and platforms")'); h = src.index("\n", h) + 1
s = src.rindex("\n", 0, src.index('R.section("Config entry migration")')) + 1
e = src.index("_new = FakeEntry()", s)
code = src[:h] + src[s:e] + '\nsys.exit(R.close("MIGRATION BLOCK"))\n'
ns = {"__name__": "__main__", "__file__": os.path.abspath(path)}
exec(compile(code, path + "[mig]", "exec"), ns)
