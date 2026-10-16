#!/usr/bin/env python3
"""The structural ratchet's class row: a move against a merge (R10-STRUCTURE-BLIND).

Written by the R10-STRUCTURE-BLIND fixer (#2235, findings D7-s1-01 and
D7-s3-01; the forward-carried control from the fix review of #2285).
Every arm drives the production ``tests/structure.py:measure`` of ``--structure``
(default ``tests/structure.py``) over an in-memory copy of the tree:
``module_trees`` is swapped and nothing on disk changes.

  null           the unchanged tree, measured twice: every key equal
                 (``null_keys_moved``).
  move           the planted move: the first coordinator method of exactly
                 ``MOVE_LOC`` lines that only ``self.<name>(`` calls reach is
                 cut out of the class verbatim into a module-level
                 ``_r10moved(self, ...)`` helper in coordinator.py, its call
                 sites rewritten to ``_r10moved(self, ...)``. Nothing is
                 improved, so a class row must not fall
                 (``move_class_excess_delta``; ``move_max_class_loc_delta`` is
                 the same move read by the largest-class row).
  merge          the same method duplicated in the class as ``_r10copy``
                 (called beside it) is the base; merging the copy back away is
                 a de-duplication, which a class row must price
                 (``merge_class_excess_delta``).
  six            D7-s3-01's six members: how many the census measures dead
                 (``six_measured_dead``), how many it can only keep by name
                 (``six_name_kept``), how many the source no longer defines
                 (``six_deleted``); the perturbation feeds one load the
                 source types to ``Cusum`` and the count must fall by one
                 (``six_measured_dead_with_a_typed_cusum_reset``).
  second         1201 lines of called, CC-1 code in ``HeatPumpOptimizer``,
                 the second-largest class: D7-s1-01's arm
                 (``second_keys_moved``, the keys that rose).
  separation     ``HA_ENTITY_METHODS``' key, member by member (``fixer.md``
                 step 14): which such members the entity rule covers
                 (``entity_members_keyed``) and which share the name on a class
                 HA never instantiates (``same_name_not_keyed``, printed). A
                 key of the name alone reads the two the same, and the entry
                 would then silence the second set for good.

Command:
  PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_structure_blind.py \
      [--structure PATH] [--package-ref REF]
``--package-ref`` measures the integration as committed at REF instead of the
working tree: the census arm is read on the merge base's package, where the
four members this fix deletes still stand.

Expected, fix-head structure.py on the merge base's package (--package-ref MB):
  RESULT null_keys_moved=0 count
  RESULT move_class_excess_delta=0 lines
  RESULT move_max_class_loc_delta=-12 lines
  RESULT merge_class_excess_delta=-12 lines
  RESULT second_keys_moved=1 count
  RESULT six_measured_dead=4 count
  RESULT six_name_kept=2 count
  RESULT six_deleted=0 count
  RESULT six_measured_dead_with_a_typed_cusum_reset=3 count
  RESULT entity_members_keyed=21 count
  RESULT same_name_not_keyed=2 count
On the fix head's own tree the four it measures dead are deleted: six_measured_dead=0,
six_name_kept=2, six_deleted=4. The merge base's structure.py on the merge base's
package (``--structure`` a base copy, no class_excess_loc row):
move_class_excess_delta and merge_class_excess_delta print ``absent``,
second_keys_moved=0, six_measured_dead=0, six_name_kept=6 -- the base prices
neither the second class nor a merge apart from a move, and measures none of the six.
The base has no ``HA_ENTITY_METHODS``: separation prints ``absent`` for both.
Perturbation: in ``class_excess`` drop ``loc += helper_loc`` -> the move arm
reads -12, a move priced as a gain again.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import ast  # noqa: E402
import importlib.util  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
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
MOVE_LOC = 12
PAD_METHODS, PAD_LINES = 10, 120   # 1201 lines with the call, each under 150
COORD = "HeatPumpOptimizerCoordinator"
# D7-s3-01's six: dead in production, kept alive by a shared name.
SIX = [("drift.py", "Cusum", "reset"), ("inputs.py", "InputReader", "value"),
       ("inputs.py", "InputReader", "text"), ("inputs.py", "InputReader", "flag"),
       ("boost.py", "BoostState", "as_dict"),
       ("coordinator.py", "HeatPumpOptimizerCoordinator", "dhw_temperature")]

args = sys.argv[1:]
spath = Path(args[args.index("--structure") + 1]) if "--structure" in args \
    else ROOT / "tests" / "structure.py"
REF = args[args.index("--package-ref") + 1] if "--package-ref" in args else None
sys.path.insert(0, str(ROOT / "tests"))
spec = importlib.util.spec_from_file_location("structure_under_test", spath)
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
S.REPO_ROOT = ROOT
S.PACKAGE_DIR = ROOT / "custom_components" / "heatpump_optimizer"
S.BUDGET_FILE = ROOT / "tests" / "structure_budgets.json"
S.SEAM_MAP_FILE = ROOT / "tests" / "seam_map.json"
PKG = S.PACKAGE_DIR


def source(path: Path) -> str:
    """A package module's text: the working tree's, or ``--package-ref``'s."""
    if REF is None:
        return path.read_text()
    rel = path.relative_to(ROOT).as_posix()
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{REF}:{rel}"],
                          capture_output=True, text=True, check=True).stdout


def ref_paths() -> list[Path]:
    if REF is None:
        return sorted(PKG.rglob("*.py"))
    rel = PKG.relative_to(ROOT).as_posix()
    out = subprocess.run(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", REF, rel],
                         capture_output=True, text=True, check=True).stdout.split()
    return sorted(ROOT / p for p in out if p.endswith(".py"))


def pick(src: str, others: str) -> ast.FunctionDef:
    """The method the planted move cuts: MOVE_LOC lines, plain, reached by self.<name>( only."""
    tree = ast.parse(src)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == COORD)
    for item in cls.body:
        if not isinstance(item, ast.FunctionDef) or item.decorator_list \
                or S.span_loc(item) != MOVE_LOC or item.name.startswith("__") \
                or "super()" in ast.get_source_segment(src, item):
            continue
        name = item.name
        calls = len(re.findall(rf"\bself\.{name}\(", src))
        loads = len(re.findall(rf"\.{name}\b", src))
        if calls and calls == loads and not re.search(rf"\b{name}\b", others):
            return item
    raise SystemExit("no movable method of %d lines" % MOVE_LOC)


def move(src: str, item: ast.FunctionDef, keep_method: bool, helper: bool) -> str:
    lines = src.splitlines()
    body = lines[item.lineno - 1:item.end_lineno]
    indent = len(body[0]) - len(body[0].lstrip())
    out = lines[:item.lineno - 1] + lines[item.end_lineno:] if not keep_method else lines[:]
    if helper:
        dedented = [ln[indent:] if ln.strip() else ln for ln in body]
        dedented[0] = dedented[0].replace(f"def {item.name}(", "def _r10moved(", 1)
        text = "\n".join(out) + "\n\n\n" + "\n".join(dedented) + "\n"
        return text.replace(f"self.{item.name}(", "_r10moved(self, ").replace(
            "_r10moved(self, )", "_r10moved(self)")
    copy = list(body)
    copy[0] = copy[0].replace(f"def {item.name}(", "def _r10copy(", 1)
    end = next(n for n in ast.parse(src).body
               if isinstance(n, ast.ClassDef) and n.name == COORD).end_lineno
    out = lines[:end] + copy + lines[end:]
    text = "\n".join(out) + "\n"
    return re.sub(rf"(self\.{item.name}\(([^()]*)\))", r"(\1, self._r10copy(\2))", text, count=1)


def pad(src: str) -> str:
    """D7-s1-01's pad: PAD_METHODS chained methods of PAD_LINES, called from __init__."""
    tree = ast.parse(src)
    cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "HeatPumpOptimizer")
    init = next(m for m in cls.body if isinstance(m, ast.FunctionDef) and m.name == "__init__")
    lines = src.splitlines()
    ind, mind = " " * init.body[-1].col_offset, " " * init.col_offset
    block = []
    for m in range(PAD_METHODS):
        block += [f"{mind}def _r10pad{m}(self):", f"{ind}acc = {m}.5"]
        block += [f"{ind}acc = acc * {m * 1000 + k + 2} + {k * 7 + 3}" for k in range(PAD_LINES - 3)]
        block.append(f"{ind}return (acc, {f'self._r10pad{m + 1}()' if m + 1 < PAD_METHODS else 'None'})")
    out = lines[:init.end_lineno] + [f"{ind}self._r10pad0()"] + \
        lines[init.end_lineno:cls.end_lineno] + block + lines[cls.end_lineno:]
    return "\n".join(out) + "\n"


def measure(edits: dict[str, str], add: tuple[str, ...] = (), drop: tuple[str, ...] = ()) -> dict:
    orig, orig_seams = S.module_trees, S.load_seam_map

    def trees():
        return [(p, ast.parse(edits[p.name] if p.name in edits else source(p), filename=str(p)))
                for p in ref_paths()]

    def seams():
        m = {k: v for k, v in orig_seams().items() if k not in drop}
        m.update({k: m.get("__init__", next(iter(m.values()))) for k in add})
        return m

    S.module_trees, S.load_seam_map = trees, seams
    try:
        result = S.measure()
        result["metrics"]["_tables"] = result["tables"]
        return result["metrics"]
    finally:
        S.module_trees, S.load_seam_map = orig, orig_seams


def delta(a: dict, b: dict, key: str) -> str:
    return str(b[key] - a[key]) if key in a and key in b else "absent"


coord_src = source(PKG / "coordinator.py")
others = "\n".join(source(p) for p in ref_paths() if p.name != "coordinator.py")
item = pick(coord_src, others)
print(f"moved method: {COORD}.{item.name} ({S.span_loc(item)} lines)")

base = measure({})
again = measure({})
moved = measure({"coordinator.py": move(coord_src, item, keep_method=False, helper=True)},
                add=("coordinator._r10moved",), drop=(item.name,))
copied = measure({"coordinator.py": move(coord_src, item, keep_method=True, helper=False)},
                 add=("_r10copy",))
second = measure({"optimizer.py": pad(source(PKG / "optimizer.py"))})

print(f"RESULT null_keys_moved={sum(1 for k in base if k != '_tables' and again.get(k) != base[k])} count")
print(f"RESULT move_class_excess_delta={delta(base, moved, 'class_excess_loc')} lines")
print(f"RESULT move_max_class_loc_delta={delta(base, moved, 'max_class_loc')} lines")
print(f"RESULT merge_class_excess_delta={delta(copied, base, 'class_excess_loc')} lines")
rose = sorted(k for k in base if k != "_tables" and second.get(k, base[k]) > base[k])
print(f"second-class keys that rose: {rose}")
print(f"RESULT second_keys_moved={len(rose)} count")


def six(metrics: dict) -> tuple[int, int, int]:
    """(measured dead, kept by name, gone from the source) of D7-s3-01's six."""
    t = metrics["_tables"]
    dead = {(Path(rel).name, cls, name) for rel, cls, name, _line in t["dead_methods"]}
    kept = {(Path(rel).name, cls, name) for rel, cls, name in t["name_kept"]}
    gone = sum(1 for f, c, m in SIX
               if not re.search(rf"\n    (async )?def {m}\(", source(PKG / f).split(f"class {c}", 1)[1]
                                .split("\nclass ", 1)[0]))
    return sum(1 for m in SIX if m in dead), sum(1 for m in SIX if m in kept), gone


d, k, g = six(base)
print(f"RESULT six_measured_dead={d} count")
print(f"RESULT six_name_kept={k} count")
print(f"RESULT six_deleted={g} count")
fed = measure({"drift.py": source(PKG / "drift.py") + "\n\nCusum(threshold=1.0, drift=0.0).reset()\n"})
print(f"RESULT six_measured_dead_with_a_typed_cusum_reset={six(fed)[0]} count")


def separation() -> tuple[str, str, list[str]]:
    """``HA_ENTITY_METHODS`` keyed with the class, against keyed on the name.

    Returns (members the entity rule covers, the two counts as text, and the
    members that share a name in the set on a class HA never instantiates --
    the sites a name-only entry would have silenced).
    """
    if not hasattr(S, "HA_ENTITY_METHODS"):
        return "absent", "absent", []
    trees = [(p, ast.parse(source(p), filename=str(p))) for p in ref_paths()]
    pkg = S.Package(trees)
    keyed, only_name = 0, []
    for (mod, cls), node in sorted(pkg.classes.items()):
        for item in node.body:
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                    or item.name not in S.HA_ENTITY_METHODS:
                continue
            fam = pkg.family((mod, cls))
            entity = any(b.endswith(S.HA_ENTITY_BASE_SUFFIX)
                         for owner in fam for b in pkg.external_bases(owner))
            if entity:
                keyed += 1
            else:
                only_name.append(f"{mod}.{cls}.{item.name}")
    return str(keyed), str(len(only_name)), only_name


keyed, not_keyed, sites = separation()
print(f"RESULT entity_members_keyed={keyed} count")
print(f"RESULT same_name_not_keyed={not_keyed} count")
for site in sites:
    print(f"  not keyed (a name-only entry would silence it): {site}")
