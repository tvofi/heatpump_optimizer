import sys, importlib.util
from pathlib import Path
root = Path(sys.argv[1]).resolve()
sys.path[:0] = [str(root/"tests"/"hastub"), str(root/"tests")]
spec = importlib.util.spec_from_file_location("h", root/"dev/audit/harnesses/r10_structure_alias.py")
h = importlib.util.module_from_spec(spec); sys.argv=[str(spec.origin)]; spec.loader.exec_module(h)
print(f"RESULT {sys.argv[0] if False else ''}clean={h.seam_cut(h.COORD.read_text(), {})}")
