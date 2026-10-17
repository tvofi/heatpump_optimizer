import sys
from pathlib import Path
LAY = Path("/tmp/r3probe/mutwt5/tools/audit/archscore/metrics/layering.py")
M18_OLD = ("            elif _ends_chain(parent, n) and isinstance(n, ast.Attribute) \\\n"
            "                    and (t := _reached(pkg, modalias, m, n.value)) is not None:\n"
            "                cross(m, t, n.attr, private=PRIVATE_ATTRS)")
M18_NEW = ("            elif _ends_chain(parent, n) and isinstance(n, ast.Attribute) and _private(n.attr) \\\n"
            "                    and (t := _reached(pkg, modalias, m, n.value)) is not None:\n"
            "                cross(m, t, n.attr, private=PRIVATE_ATTRS)")
M19_OLD = "    p = parent.get(id(node))\n    return not (isinstance(p, ast.Attribute) and p.value is node)"
M19_NEW = "    return True"
M20_OLD = "    if not isinstance(assign, (ast.Assign, ast.AnnAssign)):"
M20_NEW = "    if not isinstance(assign, ast.Assign):"
M14_OLD = '    return path == SELF or path.startswith(SELF + ".") or SELF.startswith(path + ".")'
M14_NEW = '    return path == SELF or path.startswith(SELF + ".")'
MUT = {"M0": None, "M18": (M18_OLD, M18_NEW), "M19": (M19_OLD, M19_NEW), "M20": (M20_OLD, M20_NEW), "M14": (M14_OLD, M14_NEW)}
n = sys.argv[1]; e = MUT[n]; s = LAY.read_text()
if e is None: print(f"{n}: no edit")
else:
    o, w = e; assert s.count(o) == 1, f"{n}: anchor x{s.count(o)}"; LAY.write_text(s.replace(o, w)); print(f"{n}: applied")
