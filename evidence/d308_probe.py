"""Reviewer's probe (mine): execs entities.py's #1218 block (from `_D308_DS =` to the synthetic-predicate
comment) against closures.json as recorded, and against a copy with a third full-coverage closure."""
import json, sys, tempfile
from pathlib import Path
ROOT = Path("/Users/timmalmstrom/hpo-seats/1851-review/wt")
sys.path.insert(0, str(ROOT / "tests"))
import closure as _closure
src = (ROOT / "tests/entities.py").read_text().splitlines()
a = next(i for i, l in enumerate(src) if l.startswith('_D308_DS = '))
b = next(i for i, l in enumerate(src) if i > a and l.startswith("# The predicate itself"))
block = "\n".join(src[a:b])
variant = sys.argv[1]
if variant == "old-predicate":
    block = block.replace("_D308_FULLCOV == _D308_ADMITTED", "_D308_FULLCOV == [_D308_DS]")
if variant == "third":
    c = json.loads(_closure.CLOSURES.read_text())
    c["closures"]["tests/zz_third_fullcov.py"] = list(c["closures"]["tests/deployment_shape.py"])
    t = Path(tempfile.mkdtemp()) / "closures.json"; t.write_text(json.dumps(c))
    _closure.CLOSURES = t
class R:
    @staticmethod
    def check(name, ok, detail=""):
        print(("  ok   " if ok else "  FAIL ") + name.split("(#1218)")[0][:70] + ("" if ok else f"  [{str(detail)[:240]}]"))
_integration_py = {str(q.relative_to(_closure.ROOT)) for q in (_closure.ROOT / "custom_components/heatpump_optimizer").rglob("*.py") if "__pycache__" not in str(q)}
import json as json
exec(block, {"R": R, "_closure": _closure, "_integration_py": _integration_py, "json": json, "__name__": "probe"})
