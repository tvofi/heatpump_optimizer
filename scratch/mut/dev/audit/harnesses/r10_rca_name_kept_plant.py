#!/usr/bin/env python3
"""A dead member kept alive by a shared name: does the ratchet refuse it? (R10-N-structure-blind).

Written by the round-10 root-cause seat for N-structure-blind (#2235,
``dev/audit/rca/R10-N-structure-blind.md``). Every arm drives the production
``tests/structure.py:measure`` of ``--structure`` (default ``tests/structure.py``)
over an in-memory copy of the tree: ``module_trees`` is swapped, nothing on disk
changes. Each arm compares the measured rows with ``--budgets`` (default
``tests/structure_budgets.json``) the way ``ratchet`` does: a row over its
budget is a refusal.

  clean   the unchanged tree.
  plant   ``diagnostics.py`` (a module Home Assistant loads) gains a live class
          ``PlantedRecord`` whose ``as_dict`` nothing calls but an untyped
          ``x.as_dict()``; other classes define ``as_dict``, so the census can
          only keep it by name.
  null    the same plant with the member uniquely named (``zz_unique_member``,
          loaded as ``x.zz_other_name()``): no other class keeps it, so
          ``dead_methods`` measures it dead.
  typed   the plant with its receiver annotated ``PlantedRecord``: the load now
          reaches the member, which is live, and nothing is name-kept.

Command:
  PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_rca_name_kept_plant.py \
      [--structure PATH --budgets PATH]

Expected, with the name_kept_members row (this seat's head):
  RESULT clean_refused=0 count   RESULT plant_refused=1 count (name_kept_members)
  RESULT null_refused=1 count (dead_methods)   RESULT typed_refused=0 count
  and *_name_kept = clean N, plant N+1, null N, typed N.
Expected, origin/main's own structure.py and budgets (no row): plant_refused=0 --
the dead member passes; null_refused=1, the control still fails.
Perturbation: drop the ``name_kept_members`` row from ``measure()`` and the
plant arm reads refused=0 again.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import ast  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
args = sys.argv[1:]
spath = Path(args[args.index("--structure") + 1]) if "--structure" in args \
    else ROOT / "tests" / "structure.py"
bpath = Path(args[args.index("--budgets") + 1]) if "--budgets" in args \
    else ROOT / "tests" / "structure_budgets.json"
sys.path.insert(0, str(ROOT / "tests"))
spec = importlib.util.spec_from_file_location("structure_under_test", spath)
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
S.REPO_ROOT = ROOT
S.PACKAGE_DIR = ROOT / "custom_components" / "heatpump_optimizer"
S.SEAM_MAP_FILE = ROOT / "tests" / "seam_map.json"
TARGET = "diagnostics.py"
ENTRY = "async def async_get_config_entry_diagnostics("
FIRST = '    coord = entry.runtime_data if hasattr(entry, "runtime_data") else None\n'


def planted(src: str, member: str, load: str, annotation: str = "Any") -> str:
    """``src`` with a live PlantedRecord whose ``member`` only ``x.<load>()`` reads."""
    assert src.count(ENTRY) == 1 and src.count(FIRST) == 1, "diagnostics.py moved: re-anchor"
    src = src.replace(ENTRY, f"def _planted_root(x: {annotation}) -> int:\n"
                             f"    x.{load}()\n    return PlantedRecord().used()\n\n\n" + ENTRY)
    src = src.replace(FIRST, FIRST + "    _planted_root(entry)\n")
    return src + (f"\n\nclass PlantedRecord:\n    def {member}(self) -> dict:\n"
                  "        return {}\n\n    def used(self) -> int:\n        return 1\n")


def measure(edit) -> dict:
    orig = S.module_trees

    def trees():
        out = []
        for path in sorted(S.PACKAGE_DIR.rglob("*.py")):
            text = path.read_text()
            if path.name == TARGET and edit:
                text = edit(text)
            out.append((path, ast.parse(text, filename=str(path))))
        return out

    S.module_trees = trees
    try:
        result = S.measure()
    finally:
        S.module_trees = orig
    return {**result["metrics"], "_name_kept": len(result["tables"]["name_kept"])}


budgets = {k: v for k, v in json.loads(bpath.read_text()).items() if k != "recorded_at"}
ARMS = {
    "clean": None,
    "plant": lambda s: planted(s, "as_dict", "as_dict"),
    "null": lambda s: planted(s, "zz_unique_member", "zz_other_name"),
    "typed": lambda s: planted(s, "as_dict", "as_dict", '"PlantedRecord"'),
}
for arm, edit in ARMS.items():
    m = measure(edit)
    over = sorted(k for k in budgets if k in m and m[k] > budgets[k])
    print(f"RESULT {arm}_name_kept={m['_name_kept']} count")
    print(f"RESULT {arm}_dead_methods={m['dead_methods']} count")
    print(f"RESULT {arm}_refused={len(over)} count{(' (' + ', '.join(over) + ')') if over else ''}")
print(f"RESULT row_in_budgets={'name_kept_members' in budgets}")
