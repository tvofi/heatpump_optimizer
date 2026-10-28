"""Run entities.py's shape-claim pins (R10-996 block + _R996 msg checks) against a given env_drift.py."""
import sys, importlib.util, io as _d7_io, contextlib as _d7_contextlib, ast as _ast_af
from pathlib import Path
src, ent = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("env_drift_mut", src)
_env_drift = importlib.util.module_from_spec(spec); sys.modules["env_drift_mut"] = _env_drift
spec.loader.exec_module(_env_drift)
class _R:
    fails = []; n = 0
    def check(self, name, ok, detail=""):
        self.n += 1
        if not ok: self.fails.append(name); print("FAIL", name, "|", detail)
R = _R()
lines = Path(ent).read_text().splitlines()
def idx(prefix): return next(i for i, l in enumerate(lines) if l.startswith(prefix))
a = idx("_R996_MSG = "); b = idx("# The instance counter.")
block = "\n".join(lines[a:b]).replace('Path("tests/env_drift.py")', 'Path(SRC)')
g = dict(globals()); g["SRC"] = src
exec(compile(block, "pins", "exec"), g)
print(f"RESULT pins={R.n} fails={len(R.fails)}")
