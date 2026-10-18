"""Round-4 reviewer's own plants (reviewer-built, not the finder's): P6 class attribute, P7 constant expression.
Usage: python3 -I plants_r4.py <tree> ; copies the tree, rewrites the first three config_flow `_number(1, 24, 1, slider=True)`
copies, and prints literal_clone_copies before and after."""
import sys, shutil, tempfile, re
from pathlib import Path
src = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(src / "tools/audit"))
from archscore import vector
def lc(root): return vector.measure(root, only={"literal_clone_copies"})["literal_clone_copies"]
CF = "custom_components/heatpump_optimizer/config_flow.py"
OLD = "_number(1, 24, 1, slider=True)"
base = lc(src)
print(f"RESULT plant_base literal_clone_copies={base}")
def plant(name, header, reps):
    with tempfile.TemporaryDirectory() as tmp:
        dst = Path(tmp) / "t"
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".git", "node_modules", "dev"))
        p = dst / CF; s = p.read_text()
        for r in reps: s = s.replace(OLD, r, 1)
        i = s.index("\ndef _number(")
        s = s[:i] + "\n" + header + "\n" + s[i:]
        p.write_text(s)
        compile(s, str(p), "exec")
        print(f"RESULT {name} literal_clone_copies={base}->{lc(dst)}")
plant("P6_class_attr", "class _RtH:\n    L0 = 24\n    L1 = 24\n    L2 = 24\n",
      [f"_number(1, _RtH.L{i}, 1, slider=True)" for i in range(3)])
plant("P7_const_expr", "", ["_number(1, 12 * 2, 1, slider=True)", "_number(1, 20 + 4, 1, slider=True)", "_number(1, 48 // 2, 1, slider=True)"])
plant("NULL_unchanged", "", [])
