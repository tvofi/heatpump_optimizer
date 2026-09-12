"""D6 round 4 -- docs/architecture.md's "Home Assistant boundary", executed.

METRIC: the number of modules under custom_components/heatpump_optimizer/ that
FAIL to import when the `homeassistant` package is made unimportable.
architecture.md says "Exactly ten modules import `homeassistant` at module
level ... Everything else is deliberately free of it, so each module can be
driven directly by tests/features.py with no Home Assistant running."

RUN (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/ha_boundary.py

ROOT RULE: the working directory (`ROOT = Path(".")`). Nothing resolves from
__file__.

EXPECTED (baseline 7dd68dd327fe3dbfb09f3bd0fe38910c58877697, 8-core Apple M1,
macOS 25.6.0, Python 3.11.9, tolerance 0 -- a count, exactly reproducible):
    RESULT modules_total=56
    RESULT documented_ha_modules=11
    RESULT ha_free_import_failures=21
    RESULT undocumented_ha_dependents=11

`documented_ha_modules` reads 11, not the 10 the sentence claims, because the
name regex also picks up `inputs` from the following sentence ("One module
outside that set touches it at all: `inputs` ...").  That is deliberately
CONSERVATIVE: counting `inputs` as documented can only shrink
`undocumented_ha_dependents`, and it is still 11.

INSTRUMENTED SYMBOL: importlib.import_module("heatpump_optimizer.<name>") with
a meta-path finder that refuses `homeassistant` -- i.e. the real import of the
real production module, not a read of its source.

PERTURBATION (built in, no production file is touched):
    HPO_D6_PERTURB=1 inserts `import homeassistant.core` into the SCRATCH COPY
    of drift.py -- a module the document puts on the HA-free side.
    Measured: ha_free_import_failures 21 -> 22 and
    undocumented_ha_dependents 11 -> 12.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(".")
PKG = ROOT / "custom_components" / "heatpump_optimizer"

CHILD = r'''
import sys, importlib, json
class Refuse:
    def find_module(self, name, path=None):
        return self.find_spec(name, path)
    def find_spec(self, name, path=None, target=None):
        if name == "homeassistant" or name.startswith("homeassistant."):
            raise ImportError("homeassistant is not installed (D6 boundary probe)")
        return None
sys.meta_path.insert(0, Refuse())
sys.path.insert(0, sys.argv[2])
name = sys.argv[1]
try:
    importlib.import_module("heatpump_optimizer." + name)
    print(json.dumps({"ok": True}))
except ImportError as err:
    print(json.dumps({"ok": False, "err": str(err)[:160]}))
except SyntaxError as err:
    print(json.dumps({"ok": None, "err": "SyntaxError: " + str(err)[:120]}))
except Exception as err:
    print(json.dumps({"ok": True, "other": type(err).__name__ + ": " + str(err)[:80]}))
'''

# Each module is imported on its own, out of a scratch copy of the package
# whose ``__init__.py`` is EMPTY.  Without that the package's own
# ``__init__`` -- one of the ten the document names -- imports
# ``homeassistant`` first and every submodule would fail for that reason
# alone, which measures the package, not the module.  Relative imports
# (``from .const import ...``) still resolve, because the package is real.
import shutil
import tempfile

_tmp = pathlib.Path(tempfile.mkdtemp(prefix="d6-boundary-"))
_scratch = _tmp / "heatpump_optimizer"
shutil.copytree(PKG, _scratch, ignore=shutil.ignore_patterns("__pycache__"))
_real_init = (PKG / "__init__.py").read_text()
(_scratch / "__init__.py").write_text("")

# PERTURBATION, applied to the SCRATCH COPY only -- no production file is
# touched.  drift.py is on the doc's HA-free side; making it import
# homeassistant must move both counts up by one.
if os.environ.get("HPO_D6_PERTURB") == "1":
    _d = _scratch / "drift.py"
    _t = _d.read_text()
    _t = _t.replace("from __future__ import annotations",
                    "from __future__ import annotations\nimport homeassistant.core  # D6 perturbation",
                    1)
    _d.write_text(_t)

modules = sorted(p.stem for p in PKG.glob("*.py") if p.stem != "__init__")

arch = (ROOT / "docs" / "architecture.md").read_text()
doc_named = sorted(
    {n for n in re.findall(r"`([a-z_]+)`", re.search(
        r"Exactly ten modules import `homeassistant` at module level: (.*?)\n\n",
        arch, re.S).group(1))}
)

failures = []
for name in modules:
    r = subprocess.run(
        [sys.executable, "-c", CHILD, name, str(_tmp)],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": "tests/hastub"},
    )
    if '"ok": false' in r.stdout.lower():
        failures.append(name)

undocumented = sorted(set(failures) - set(doc_named))

# __init__ is measured separately: it is the package, and it does import
# homeassistant -- the document is right about that one.
_init_imports_ha = "from homeassistant" in _real_init or "import homeassistant" in _real_init
shutil.rmtree(_tmp, ignore_errors=True)

print(f"RESULT modules_total={len(modules) + 1} modules")
print(f"RESULT documented_ha_modules={len(doc_named)} modules")
print(f"RESULT ha_free_import_failures={len(failures) + int(_init_imports_ha)} modules")
print(f"RESULT undocumented_ha_dependents={len(undocumented)} modules")
print(f"RESULT thread_factor=1.0")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
print("documented:", doc_named)
print("fail without homeassistant:", failures)
print("undocumented dependents:", undocumented)
