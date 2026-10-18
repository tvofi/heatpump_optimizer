"""review-2401 r2: run tests/arch_score.py's hub_spellings() alone (cheap), at the tree given as argv[1]."""
import sys, runpy
from pathlib import Path
root = Path(sys.argv[1]); sys.argv = [str(root / "tests/arch_score.py")]
sys.path[:0] = [str(root / "tests"), str(root / "tests/hastub")]
g = runpy.run_path(str(root / "tests/arch_score.py"), run_name="arch_score_lib")
g["hub_spellings"](); r = g["R"]
fails = [c for c in getattr(r, "results", getattr(r, "checks", []))]
print("HEAD", root.name); r.summary() if hasattr(r, "summary") else None
