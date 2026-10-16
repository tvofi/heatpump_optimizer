"""Apply one in-place predicate edit to the instrument at /tmp/r3probe/mutwt, for fix-review.md step 1.
usage: python3 r3_mut.py <MUTANT>
The edit is restored by `git -C /tmp/r3probe/mutwt checkout -- tools/audit/archscore/metrics/layering.py`.
"""
import sys
from pathlib import Path

LAY = Path("/tmp/r3probe/mutwt/tools/audit/archscore/metrics/layering.py")

M11_OLD = "    out: dict[str, str] = {}\n    for n in C.walk(mod.tree):"
M11_NEW = "    out: dict[str, str] = {}\n    return out\n    for n in C.walk(mod.tree):"

M12_OLD = """                else:
                    for a in n.names:
                        if (rel := _self_module(a.name)) is not None:
                            cross(m, rel or "__init__", "")
"""
M12_NEW = """                else:
                    pass
"""

M13_OLD = """    first = node.args[0] if node.args else \\
        next((k.value for k in node.keywords if k.arg == "name"), None)
"""
M13_NEW = """    first = node.args[0] if node.args else None
"""

MUTANTS = {"M0": None, "M11": (M11_OLD, M11_NEW), "M12": (M12_OLD, M12_NEW), "M13": (M13_OLD, M13_NEW)}

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
