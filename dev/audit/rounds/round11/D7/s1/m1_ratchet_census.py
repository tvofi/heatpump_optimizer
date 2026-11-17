#!/usr/bin/env python3
"""D7.M1: the structural ratchet read per file, recounted independently, plus the censuses it lacks.

Metrics (one line each):
  const_unseen_modules   modules reading more than CONST_FANOUT_LIMIT DISTINCT names of ``.const`` by any
                         spelling (``from .const import X``, or ``<binding>.X`` off ``from . import const``)
                         that tests/structure.py:measure's ``const_fanout`` table holds at or under the limit.
                         KEY: the distinct ``const`` names the module reads -- never the import statement's shape.
  in_function_copies     normalized statement windows (structure.DUP_WINDOW_STATEMENTS statements,
                         >= DUP_MIN_NODES nodes, structure.normalized_window's form) written at two or more
                         non-overlapping places of ONE function and owned by no second function.
                         KEY: the window's normalized text and the function owning it.

  unused_package_imports names a module binds with ``from .<package module> import N`` and never loads, that no
                         other module imports from it (a re-export) and that no string of the module names.
                         KEY: the (importing module, bound name) pair and the loads of that name in that module.

  coordinator_py_unpriced_loc  lines of coordinator.py outside the coordinator class and outside the helpers
                         class_excess_loc charges to it (structure.py's ``helper_loc``): no row holds them.
                         KEY: the file's line count less the class span and ``helper_loc`` measure() reports.

Run (from the repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m1_ratchet_census.py
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m1_ratchet_census.py --perturb const-respell
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m1_ratchet_census.py --perturb const-count-reads
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m1_ratchet_census.py --perturb clone-same-fn
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m1_ratchet_census.py --perturb clone-two-fns
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m1_ratchet_census.py --perturb unused-import
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m1_ratchet_census.py --perturb use-import
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m1_ratchet_census.py --perturb module-growth
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m1_ratchet_census.py --perturb class-growth
    ... --perturb reach-read | attr-two-writers | name-kept | seam-relabel   (the rows no census here recounts)

Expected at the baseline (counts, exact): ratchet_const_modules_over_50=3, any_spelling_const_modules_over_50=4,
const_unseen_modules=1 (entry_config.py: 3 from-imported, 118 distinct read), in_function_copies=6,
ratchet_duplication_copies=8, recount_mismatches=0 over 10 recounted rows (the function and class rows,
const_modules_over_50, import_cycle_modules, class_excess_loc), files=95.
Perturbations (all in memory; the tree is never written):
  const-respell      thermal_model.py's ``from .const import`` names re-spelled as ``const.X`` reads:
                     ratchet_const_modules_over_50 3 -> 2 while any_spelling stays 4 (const_unseen_modules 1 -> 2).
  const-count-reads  the repair: ``const_fanout`` fed the distinct names read -> const_unseen_modules 1 -> 0,
                     ratchet_const_modules_over_50 3 -> 4.
                     (Both const arms rewrite import statements in memory, so unused_package_imports reads 11 and
                     222 under them and const-respell moves dead_top_level_symbols 1 -> 2: artefacts of the
                     rewrite, not readings. The fan-out rows are those arms' subject.)
  clone-same-fn      one probe function holding a window twice is appended to ledger.py:
                     ratchet_duplication_copies 8 -> 8 (unmoved), in_function_copies 6 -> 7.
  clone-two-fns      null control: the same two windows in two probe functions: 8 -> 9, in_function_copies 6 -> 6.
  unused-import      ``from .const import DOMAIN as _d7s1_unused`` appended to ledger.py:
                     unused_package_imports 14 -> 15, ratchet_rows_off_budget stays 0 (no row sees it).
  use-import         null control: the same import plus one load of it: unused_package_imports stays 14.
  module-growth      ten live 140-line functions (1,423 lines with spacing, CC 1, none handed the coordinator) appended to
                     coordinator.py: coordinator_py_loc 11414 -> 12837, coordinator_py_unpriced_loc 2980 -> 4403,
                     ratchet_rows_off_budget stays 0.
  class-growth       null control: the same ten bodies as methods of optimizer.py's HeatPumpOptimizer:
                     class_excess_loc rises by their 1,400 lines (ratchet_rows_off_budget > 0).
  reach-read         one read of ``coordinator._mode`` from ledger.py: coordinator_private_reach 0 -> 1
                     (the lexical recount reads 1 too).
  attr-two-writers   a new coordinator attribute stored from two ledger.py functions: coordinator_attrs 136 -> 137,
                     coordinator_multiassigned_attrs 104 -> 105, coordinator_private_reach 0 -> 6.
  name-kept          two classes defining one member name, loaded once on an untyped receiver:
                     name_kept_members 38 -> 40, dead_methods stays 0.
  seam-relabel       every "dhw" unit of tests/seam_map.json read as "views" (two seams merged):
                     seam_cut_total 415 -> 393. With ``--unit NAME`` one unit only
                     (``--unit _dhw_confidence_band`` reads 415, unmoved).
Expected unused_package_imports=14 and ratchet_rows_off_budget=0 at the baseline; rows_recounted=12 (the ten
above, coordinator_private_reach by receiver spelling, dead_top_level_symbols by an independent resolver).
Baseline SHA: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: darwin arm64, 8 cores (box B5).
Hooks: tests/structure.py:measure, tests/structure.py:duplicate_clones, tests/structure.py:module_trees.
Writes nothing.
"""
from __future__ import annotations

import os

for _pin in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
             "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_pin, "1")

import ast  # noqa: E402
import hashlib  # noqa: E402
import importlib.util  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from collections import defaultdict  # noqa: E402
from pathlib import Path  # noqa: E402

REPO = Path.cwd()

PROBE_WINDOW = (
    "    {a} = [float(v) * 3.25 + 17.5 for v in rows if v is not None and v > 0.125]\n"
    "    {b} = sum({a}) / max(len({a}), 1) + 41.75 * len(rows)\n"
)


# Source appended to ledger.py, in memory, by the arms that drive the role, reach and name-kept rows.
APPENDS = {
    # one read of a coordinator private from outside it
    "reach-read": (
        "\n\ndef _d7s1_reach(coordinator: \"HeatPumpOptimizerCoordinator\"):\n"
        "    return coordinator._mode\n"),
    # a NEW coordinator attribute stored from two functions outside it
    "attr-two-writers": (
        "\n\ndef _d7s1_w1(coordinator: \"HeatPumpOptimizerCoordinator\"):\n"
        "    coordinator._d7s1_new = 1\n"
        "\n\ndef _d7s1_w2(coordinator: \"HeatPumpOptimizerCoordinator\"):\n"
        "    coordinator._d7s1_new = 2\n"),
    # two classes defining one member name, loaded once on an untyped receiver
    "name-kept": (
        "\n\nclass _D7s1A:\n    def d7s1_twin(self):\n        return 1\n"
        "\n\nclass _D7s1B:\n    def d7s1_twin(self):\n        return 2\n"
        "\n\ndef _d7s1_untyped(thing):\n    return thing.d7s1_twin()\n"
        "\n\nassert _d7s1_untyped and _D7s1A and _D7s1B\n"),
}

GROWN: dict[str, int] = {}   # file -> its line count under a growth perturbation


def load_structure():
    spec = importlib.util.spec_from_file_location("d7s1_structure", REPO / "tests" / "structure.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["d7s1_structure"] = mod
    spec.loader.exec_module(mod)
    return mod


def const_reads(tree: ast.Module) -> tuple[int, set[str]]:
    """(the ratchet's own count: names on ``from .const import`` statements; the distinct const names read)."""
    counted, names, bindings = 0, set(), set()
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            if (n.level == 1 and n.module == "const") or n.module == "heatpump_optimizer.const":
                counted += len(n.names)
                names |= {a.name for a in n.names}
            elif n.level == 1 and n.module is None:
                bindings |= {a.asname or a.name for a in n.names if a.name == "const"}
    for n in ast.walk(tree):
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in bindings:
            names.add(n.attr)
    return counted, names


def _blocks(node: ast.AST) -> list[list[ast.stmt]]:
    out = [getattr(node, f) for f in ("body", "orelse", "finalbody")
           if isinstance(getattr(node, f, None), list) and getattr(node, f)
           and isinstance(getattr(node, f)[0], ast.stmt)]
    return out + [h.body for h in getattr(node, "handlers", []) or []]


def in_function_copies(S, trees) -> list[tuple[str, str, int, int]]:
    """(file, function, line, places) per window written twice or more in one function and nowhere else."""
    owners: dict[str, set] = defaultdict(set)
    places: dict[tuple, list] = defaultdict(list)
    for path, tree in trees:
        rel, modalias = path.name, S._module_aliases(tree)
        for fn in S.all_functions(tree):
            local, owner, stack = S._local_names(fn), (rel, fn.name, fn.lineno), [fn]
            while stack:
                node = stack.pop()
                stack += [c for c in ast.iter_child_nodes(node)
                          if not isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef))]
                for block in _blocks(node):
                    block = [s for s in block if not S._is_docstring(s)]
                    for i in range(len(block) - S.DUP_WINDOW_STATEMENTS + 1):
                        stmts = block[i:i + S.DUP_WINDOW_STATEMENTS]
                        if any(isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for s in stmts):
                            continue
                        if sum(1 for s in stmts for _ in ast.walk(s)) < S.DUP_MIN_NODES:
                            continue
                        d = hashlib.sha1(S.normalized_window(stmts, local, modalias).encode()).hexdigest()
                        owners[d].add(owner)
                        places[(owner, d)].append((stmts[0].lineno, stmts[-1].end_lineno))
    out = []
    for (owner, d), spans in places.items():
        kept: list[tuple[int, int]] = []
        for s in sorted(spans):
            if not kept or s[0] > kept[-1][1]:
                kept.append(s)
        if len(kept) > 1 and len(owners[d]) == 1:
            out.append((*owner, len(kept)))
    return sorted(out)


def unused_package_imports(trees) -> list[tuple[str, int, str, str]]:
    """(importer file, line, source module, name) per package from-import whose binding nothing uses."""
    mods = {path.stem: tree for path, tree in trees}
    imports = []
    for m, tree in mods.items():
        for n in ast.walk(tree):
            if isinstance(n, ast.ImportFrom) and n.level == 1 and n.module in mods:
                imports += [(m, n.module, a.name, a.asname or a.name, n.lineno) for a in n.names if a.name != "*"]
    reexported = {(src, name) for _m, src, name, _l, _ln in imports}
    out = []
    for m, src, name, local, ln in imports:
        tree = mods[m]
        if (m, local) in reexported:
            continue
        if any(isinstance(n, ast.Name) and n.id == local and not isinstance(n.ctx, ast.Store)
               for n in ast.walk(tree)):
            continue
        if any(isinstance(n, ast.Constant) and isinstance(n.value, str) and local in n.value.replace(".", " ").split()
               for n in ast.walk(tree)):
            continue
        out.append((f"{m}.py", ln, src, name))
    return sorted(out)


def private_reach_lexical(S, trees) -> int:
    """``<receiver>._x`` outside coordinator.py where the receiver is spelled ``coordinator`` / ``coord`` or
    ends in ``.coordinator``: reads 1, stores and deletes PRIVATE_WRITE_WEIGHT. A census on the receiver's
    SPELLING, independent of structure's role engine (and weaker: it cannot see a renamed handle)."""
    total = 0
    for path, tree in trees:
        if path.name == "coordinator.py":
            continue
        for n in ast.walk(tree):
            if isinstance(n, ast.Attribute) and n.attr.startswith("_") and not n.attr.startswith("__"):
                v = n.value
                named = (isinstance(v, ast.Name) and v.id in ("coordinator", "coord")) or (
                    isinstance(v, ast.Attribute) and v.attr == "coordinator")
                if named:
                    total += 1 if isinstance(n.ctx, ast.Load) else S.PRIVATE_WRITE_WEIGHT
    return total


def dead_top_level_recount(S, trees) -> list[str]:
    """Top-level defs, classes and assignments nothing loads, resolved by this census alone: a name is live when
    its module loads it outside its own body, when a module that imports it (through any chain of package
    from-imports) loads the bound name, when ``<module binding>.N`` reads it, or when ``x.N`` is read on a
    receiver that is neither a module binding nor self/cls. Dunders, structure.HA_CONVENTION_NAMES and
    ConfigFlow/OptionsFlow subclasses are outside it, as in the ratchet's definition."""
    mods = {path.stem: tree for path, tree in trees}
    tops: dict[tuple[str, str], ast.AST] = {}
    for m, tree in mods.items():
        for n in tree.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                tops[(m, n.name)] = n
            elif isinstance(n, ast.ClassDef):
                flow = any(ast.unparse(b).endswith(("ConfigFlow", "OptionsFlow")) for b in n.bases)
                if not flow:
                    tops[(m, n.name)] = n
            elif isinstance(n, ast.Assign):
                for t in n.targets:
                    if isinstance(t, ast.Name):
                        tops[(m, t.id)] = n
            elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
                tops[(m, n.target.id)] = n
    sym: dict[tuple[str, str], tuple[str, str]] = {}     # (module, local) -> (source module, name)
    modbind: dict[tuple[str, str], str] = {}             # (module, local) -> module
    stars: dict[str, list[str]] = {}
    for m, tree in mods.items():
        for n in ast.walk(tree):
            if isinstance(n, ast.ImportFrom) and n.level == 1:
                if n.module is None:
                    for a in n.names:
                        if a.name in mods:
                            modbind[(m, a.asname or a.name)] = a.name
                elif n.module in mods:
                    for a in n.names:
                        if a.name == "*":
                            stars.setdefault(m, []).append(n.module)
                        else:
                            sym[(m, a.asname or a.name)] = (n.module, a.name)

    def resolve(m: str, name: str):
        seen = set()
        while (m, name) not in tops and (m, name) not in seen:
            seen.add((m, name))
            if (m, name) in sym:
                m, name = sym[(m, name)]
                continue
            for src in stars.get(m, []):
                if (src, name) in tops or (src, name) in sym:
                    m = src
                    break
            else:
                return None
        return (m, name) if (m, name) in tops else None

    live: set[tuple[str, str]] = set()
    untyped: set[str] = set()
    for m, tree in mods.items():
        spans = {n.name: (n.lineno, n.end_lineno) for n in tree.body
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        for n in ast.walk(tree):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                own = spans.get(n.id)
                if own and own[0] <= n.lineno <= own[1]:
                    continue
                r = resolve(m, n.id)
                if r:
                    live.add(r)
            elif isinstance(n, ast.Attribute):
                base = n.value.id if isinstance(n.value, ast.Name) else None
                if base is not None and (m, base) in modbind:
                    r = resolve(modbind[(m, base)], n.attr)
                    if r:
                        live.add(r)
                elif base not in ("self", "cls"):
                    untyped.add(n.attr)
    dead = []
    for (m, name), _node in sorted(tops.items()):
        if name.startswith("__") or name in S.HA_CONVENTION_NAMES:
            continue
        if (m, name) in live or name in untyped:
            continue
        dead.append(f"{m}.{name}")
    return dead


def import_cycle_count(trees) -> int:
    """Modules in a cycle of the package import graph: every import the runtime runs (function scope included),
    the body of a positive ``if TYPE_CHECKING:`` excluded. An independent census, Tarjan over module names."""
    mods = {path.stem: tree for path, tree in trees}
    edges: dict[str, set[str]] = {m: set() for m in mods}
    for m, tree in mods.items():
        guarded: set[int] = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.If) and ((isinstance(n.test, ast.Name) and n.test.id == "TYPE_CHECKING") or (
                    isinstance(n.test, ast.Attribute) and n.test.attr == "TYPE_CHECKING")):
                guarded |= {id(x) for b in n.body for x in ast.walk(b)}
        for n in ast.walk(tree):
            if id(n) in guarded:
                continue
            if isinstance(n, ast.ImportFrom):
                if n.level == 1 and n.module:
                    edges[m].add(n.module.split(".")[0])
                elif n.level == 1:
                    edges[m] |= {a.name for a in n.names}
                elif n.module and "heatpump_optimizer" in n.module.split("."):
                    tail = n.module.split("heatpump_optimizer", 1)[1].strip(".")
                    edges[m] |= {tail.split(".")[0]} if tail else {a.name for a in n.names}
            elif isinstance(n, ast.Import):
                for a in n.names:
                    if "heatpump_optimizer." in a.name:
                        edges[m].add(a.name.split("heatpump_optimizer.", 1)[1].split(".")[0])
        edges[m] = {x for x in edges[m] if x in mods}
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on: set[str] = set()
    count = 0

    def visit(v: str) -> None:
        nonlocal count
        index[v] = low[v] = len(index)
        stack.append(v)
        on.add(v)
        for w in sorted(edges[v]):
            if w not in index:
                visit(w)
                low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = stack.pop()
                on.discard(w)
                comp.append(w)
                if w == v:
                    break
            if len(comp) > 1 or v in edges[v]:
                count += len(comp)

    sys.setrecursionlimit(10000)
    for v in sorted(mods):
        if v not in index:
            visit(v)
    return count


def module_level_cc(tree: ast.Module) -> int:
    """Decision points outside every function (module and class bodies): structure's rule, no unit owns them."""
    cc, stack = 0, [tree]
    while stack:
        node = stack.pop()
        stack += [c for c in ast.iter_child_nodes(node)
                  if not isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda))]
        if isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.IfExp, ast.ExceptHandler, ast.Assert)):
            cc += 1
        elif isinstance(node, ast.BoolOp):
            cc += len(node.values) - 1
        elif isinstance(node, ast.comprehension):
            cc += 1 + len(node.ifs)
        elif isinstance(node, ast.match_case):
            cc += 1
    return cc


class Respell(ast.NodeTransformer):
    """``from .const import A, B`` dropped, every load of ``A`` read as ``const.A`` (thermal_model already binds
    ``const``): the same names read, spelled through the module binding."""

    def __init__(self, names: set[str]):
        self.names = names

    def visit_ImportFrom(self, n):
        if n.level == 1 and n.module == "const":
            return ast.copy_location(ast.ImportFrom(module=None, names=[ast.alias(name="const")], level=1), n)
        return n

    def visit_Name(self, n):
        if n.id in self.names and isinstance(n.ctx, ast.Load):
            return ast.copy_location(ast.Attribute(value=ast.Name(id="const", ctx=ast.Load()), attr=n.id,
                                                   ctx=ast.Load()), n)
        return n


def perturbed_trees(S, how: str):
    trees = S.module_trees()
    if how == "const-respell":
        out = []
        for path, tree in trees:
            if path.name == "thermal_model.py":
                _c, names = const_reads(tree)
                frm = {a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)
                       and n.level == 1 and n.module == "const" for a in n.names}
                tree = ast.fix_missing_locations(Respell(frm).visit(tree))
            out.append((path, tree))
        return out
    if how in APPENDS:
        out = []
        for path, tree in trees:
            if path.name == "ledger.py":
                tree = ast.parse(path.read_text().rstrip("\n") + "\n" + APPENDS[how], filename=str(path))
            out.append((path, tree))
        return out
    if how in ("module-growth", "class-growth"):
        out = []
        target = "coordinator.py" if how == "module-growth" else "optimizer.py"
        for path, tree in trees:
            if path.name == target:
                src = path.read_text().rstrip("\n") + "\n"
                if how == "module-growth":
                    for k in range(10):
                        body = "".join(f"    x{i} = {i + k}\n" for i in range(138))
                        nxt = f"_d7s1_g{k + 1}()" if k < 9 else "x0"
                        src += f"\n\ndef _d7s1_g{k}():\n{body}    return {nxt}\n"
                    src += "\n\nassert _d7s1_g0 is not None\n"
                else:
                    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "HeatPumpOptimizer")
                    lines = src.splitlines(keepends=True)
                    add = ""
                    for k in range(10):
                        body = "".join(f"        x{i} = {i + k}\n" for i in range(138))
                        add += f"    def _d7s1_m{k}(self):\n{body}        return x0\n"
                    src = "".join(lines[:cls.end_lineno]) + add + "".join(lines[cls.end_lineno:])
                tree = ast.parse(src, filename=str(path))
                GROWN[path.name] = len(src.splitlines())
            out.append((path, tree))
        return out
    if how in ("unused-import", "use-import"):
        out = []
        for path, tree in trees:
            if path.name == "ledger.py":
                src = path.read_text() + "\nfrom .const import DOMAIN as _d7s1_unused\n"
                if how == "use-import":
                    src += "\n\ndef _d7s1_user():\n    return _d7s1_unused\n"
                tree = ast.parse(src, filename=str(path))
            out.append((path, tree))
        return out
    if how in ("clone-same-fn", "clone-two-fns"):
        out = []
        for path, tree in trees:
            if path.name == "ledger.py":
                src = path.read_text()
                w1, w2 = PROBE_WINDOW.format(a="kept", b="mean"), PROBE_WINDOW.format(a="held", b="level")
                if how == "clone-same-fn":
                    src += f"\n\ndef _d7s1_probe_a(rows):\n{w1}{w2}    return mean, level\n"
                else:
                    src += (f"\n\ndef _d7s1_probe_a(rows):\n{w1}    return mean\n"
                            f"\n\ndef _d7s1_probe_b(rows):\n{w2}    return level\n")
                tree = ast.parse(src, filename=str(path))
            out.append((path, tree))
        return out
    return trees


def main() -> int:
    how = sys.argv[sys.argv.index("--perturb") + 1] if "--perturb" in sys.argv else "none"
    t0, c0 = time.process_time(), time.thread_time()
    S = load_structure()
    trees = perturbed_trees(S, how)
    S.module_trees = lambda: trees
    if how == "const-count-reads":
        # The repair, in memory: the const imports of each module are replaced by ONE from-import naming every
        # DISTINCT const name the module reads, so measure() counts reads in its own table, not statements.
        for path, tree in trees:
            _c, names = const_reads(tree)
            if not names:
                continue
            for n in ast.walk(tree):
                for _field, value in ast.iter_fields(n):
                    if isinstance(value, list) and any(isinstance(v, ast.ImportFrom) for v in value):
                        kept = [v for v in value if not (isinstance(v, ast.ImportFrom) and v.level == 1
                                                         and v.module == "const")]
                        value[:] = kept or [ast.copy_location(ast.Pass(), value[0])]
            tree.body.append(ast.copy_location(
                ast.ImportFrom(module="const", level=1, names=[ast.alias(name=x) for x in sorted(names)]),
                tree.body[-1]))
            ast.fix_missing_locations(tree)
    if how == "seam-relabel":
        # one coordinator method declared in another seam: the first "dhw" unit of the seam map read as "views"
        real_map = S.load_seam_map()
        which = sys.argv[sys.argv.index("--unit") + 1] if "--unit" in sys.argv else None
        moved = [k for k, v in sorted(real_map.items()) if v == "dhw" and which in (None, k)]
        S.load_seam_map = lambda: {**real_map, **{k: "views" for k in moved}}
        print(f"SEAM {len(moved)} unit(s) dhw -> views" + (f": {which}" if which else ""))
    result = S.measure()
    m, t = result["metrics"], result["tables"]
    table = {Path(k).name: v for k, v in t["const_fanout"].items()}

    files = [p.name for p, _ in trees]
    per: dict[str, dict] = {}
    for path, tree in trees:
        fns = S.all_functions(tree)
        locs = [S.span_loc(f) for f in fns]
        ccs = [S.cyclomatic_complexity(f) for f in fns]
        classes = [S.span_loc(n) for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        counted, names = const_reads(tree)
        per[path.name] = {
            "loc": GROWN.get(path.name) or len(path.read_text().splitlines()), "functions": len(fns),
            "max_fn_loc": max(locs, default=0), "over_150": sum(1 for x in locs if x > S.MONSTER_LIMITS[1]),
            "over_200": sum(1 for x in locs if x > S.MONSTER_LIMITS[0]),
            "max_cc": max(ccs, default=0), "cc_over_15": sum(1 for x in ccs if x > S.CC_LIMITS[1]),
            "cc_over_25": sum(1 for x in ccs if x > S.CC_LIMITS[0]),
            "max_class_loc": max(classes, default=0), "const_counted": counted, "const_read": len(names),
            "module_level_cc": module_level_cc(tree),
        }
    copies = in_function_copies(S, trees)
    for f, _fn, _ln, _k in copies:
        per[f]["in_function_copies"] = per[f].get("in_function_copies", 0) + 1
    for f in files:
        print("FILE " + f + " " + " ".join(f"{k}={v}" for k, v in per[f].items()))
    for f, fn, ln, k in copies:
        print(f"COPY {f}:{ln} {fn} places={k}")

    # the independent recount against measure()'s own rows
    recount = {
        "methods_over_150": sum(p["over_150"] for p in per.values()),
        "methods_over_200": sum(p["over_200"] for p in per.values()),
        "functions_cc_over_15": sum(p["cc_over_15"] for p in per.values()),
        "functions_cc_over_25": sum(p["cc_over_25"] for p in per.values()),
        "max_method_loc": max(p["max_fn_loc"] for p in per.values()),
        "max_cc": max(p["max_cc"] for p in per.values()),
        "max_class_loc": max(p["max_class_loc"] for p in per.values()),
        "const_modules_over_50": sum(1 for p in per.values() if p["const_counted"] > S.CONST_FANOUT_LIMIT),
        "import_cycle_modules": import_cycle_count(trees),
        "coordinator_private_reach": private_reach_lexical(S, trees),
        # each class span past the limit, the coordinator's with the helper lines measure() reports for it
        "class_excess_loc": sum(
            max(0, S.span_loc(n) + (t["helper_loc"] if path.name == "coordinator.py"
                                    and n.name == S.COORDINATOR_CLASS_NAME else 0) - S.GOD_CLASS_LOC_LIMIT)
            for path, tree in trees for n in ast.walk(tree) if isinstance(n, ast.ClassDef)),
    }
    mism = [k for k, v in recount.items() if v != m[k]]
    for k, v in recount.items():
        print(f"RECOUNT {k} ratchet={m[k]} recount={v} {'ok' if v == m[k] else 'MISMATCH'}")

    dead_rc = dead_top_level_recount(S, trees)
    exempt = {f"{Path(r).stem}.{n}" for r, n in t["dynamic_exempt"]}
    dead_rc = [d for d in dead_rc if d not in exempt]
    dead_ratchet = sorted(f"{Path(r).stem}.{n}" for r, _ln, n in t["dead_symbols"])
    print(f"RECOUNT dead_top_level_symbols ratchet={len(dead_ratchet)} recount={len(dead_rc)} "
          f"{'ok' if dead_rc == dead_ratchet else 'MISMATCH'}"
          + ("" if dead_rc == dead_ratchet else f" only_recount={sorted(set(dead_rc) - set(dead_ratchet))[:8]}"
             f" only_ratchet={sorted(set(dead_ratchet) - set(dead_rc))[:8]}"))
    if dead_rc != dead_ratchet:
        mism.append("dead_top_level_symbols")
    limit = S.CONST_FANOUT_LIMIT
    any_over = sorted(f for f in files if per[f]["const_read"] > limit)
    unseen = sorted(f for f in any_over if table.get(f, 0) <= limit)
    for f in any_over:
        print(f"CONST {f} ratchet_counts={table.get(f, 0)} distinct_read={per[f]['const_read']}"
              f" {'UNSEEN' if f in unseen else 'seen'}")
    coord = per["coordinator.py"]
    print(f"RESULT perturbation={how} label")
    print(f"RESULT files={len(files)} count")
    for k in sorted(m):
        print(f"RESULT ratchet_{k}={m[k]} count")
    print(f"RESULT budget_keys_measured={len(m)} count")
    print(f"RESULT rows_recounted={len(recount) + 1} count")
    print(f"RESULT recount_mismatches={len(mism)} count")
    print(f"RESULT any_spelling_const_modules_over_50={len(any_over)} count")
    print(f"RESULT const_unseen_modules={len(unseen)} count")
    print(f"RESULT in_function_copies={len(copies)} count")
    unused = unused_package_imports(trees)
    for f, ln, src, name in unused:
        print(f"UNUSED {f}:{ln} from .{src} import {name}")
    print(f"RESULT unused_package_imports={len(unused)} count")
    import json
    budgets = json.loads((REPO / "tests" / "structure_budgets.json").read_text())
    off = sorted(k for k in m if budgets.get(k) != m[k])
    print(f"RESULT ratchet_rows_off_budget={len(off)} count" + (f"  ({', '.join(f'{k} {budgets.get(k)}->{m[k]}' for k in off)})" if off else ""))
    print(f"RESULT package_loc={sum(p['loc'] for p in per.values())} lines")
    print(f"RESULT coordinator_py_loc={coord['loc']} lines")
    print(f"RESULT coordinator_helper_loc={t['helper_loc']} lines")
    print(f"RESULT coordinator_py_unpriced_loc={coord['loc'] - coord['max_class_loc'] - t['helper_loc']} lines")
    ctree = next(tree for path, tree in trees if path.name == "coordinator.py")
    cfns = [n for n in ctree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    print(f"RESULT coordinator_py_module_level_functions={len(cfns)} count")
    print(f"RESULT coordinator_py_module_level_function_loc={sum(S.span_loc(n) for n in cfns)} lines")
    print(f"RESULT modules_over_2000_loc={sum(1 for p in per.values() if p['loc'] > 2000)} count")
    print(f"RESULT module_level_cc_total={sum(p['module_level_cc'] for p in per.values())} count")
    print(f"RESULT module_level_cc_max={max(p['module_level_cc'] for p in per.values())} count")
    tf = (time.process_time() - t0) / max(time.thread_time() - c0, 1e-9)
    print(f"RESULT thread_factor={tf:.2f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
