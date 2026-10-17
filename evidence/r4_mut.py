"""Apply one in-place predicate edit to the round-4 instrument at /tmp/r3probe/mutwt4."""
import sys
from pathlib import Path
LAY = Path("/tmp/r3probe/mutwt4/tools/audit/archscore/metrics/layering.py")

M14_OLD = '''    return path == SELF or path.startswith(SELF + ".") or SELF.startswith(path + ".")'''
M14_NEW = '''    return path == SELF or path.startswith(SELF + ".")'''

M16_OLD = '''    assign = mod.tops.get(name) if name is not None else None
    if isinstance(assign, ast.Assign) and len(assign.targets) == 1 \\'''
M16_NEW = '''    assign = None
    if isinstance(assign, ast.Assign) and len(assign.targets) == 1 \\'''

M18_OLD = '''            elif PRIVATE_ATTRS and isinstance(n, ast.Attribute) and _private(n.attr) \\
                    and (t := _reached(pkg, modalias, m, n.value)) is not None:
                cross(m, t, n.attr)'''
M18_NEW = '''            elif PRIVATE_ATTRS and isinstance(n, ast.Attribute) \\
                    and (t := _reached(pkg, modalias, m, n.value)) is not None:
                if _private(n.attr):
                    cross(m, t, n.attr)
                else:
                    if t != m:
                        edges[m].add(t)'''

MUTANTS = {"M0": None, "M14": (M14_OLD, M14_NEW), "M16": (M16_OLD, M16_NEW), "M18": (M18_OLD, M18_NEW)}
name = sys.argv[1]
edit = MUTANTS[name]
s = LAY.read_text()
if edit is None:
    print(f"mutant {name}: no edit (control)")
else:
    old, new = edit
    assert s.count(old) == 1, f"{name}: anchor found {s.count(old)} times"
    LAY.write_text(s.replace(old, new))
    print(f"mutant {name}: applied")
