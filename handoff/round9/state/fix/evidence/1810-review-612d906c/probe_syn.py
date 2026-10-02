import sys; sys.path.insert(0,"tests")
import mutation_table as mt, pathlib
for c in mt.candidates(pathlib.Path("/tmp/claude-0/-home-user/d69fb6c6-9321-59bc-b2f8-c2fcd6a0ab8f/scratchpad/syn/x.py")):
    if c["kind"]=="GUARD_OFF": print(repr(c["old"]), "->", repr(c["new"]))
