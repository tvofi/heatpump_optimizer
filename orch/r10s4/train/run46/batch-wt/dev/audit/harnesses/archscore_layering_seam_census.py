#!/usr/bin/env python3
"""Census the spellings of a reach into this package, keyed by the node and its relation to the package.

WHY IT EXISTS. `calibrate.py --measure-corpus --only-metric layering` re-derived the corpus vectors for
the `layering` job and `corpus_vectors.json` came back byte-identical. That reads two ways: the rule
reads those trees exactly as the round-1 rule did, or the re-measure was vacuous and nothing was
compared. This is the control. It counts, over the same trees, every form the rule's reach can be
written in, and it refuses to report anything without first firing on a tree that carries all of them
(`PRECONDITION`). A census that matched nothing is the defect it exists to catch, so it exits 1 rather
than printing a zero.

THE FORM SET IS DERIVED, NOT LISTED. Two rounds of this census were an enumeration of the spellings its
author thought of, and each round the review named a form the list had no counter for -- an absolute
`from` self-import while only the dotted `import` counted, then the dotted `import` while only the
`from` form was planted, then the strict PREFIX of the package (`import custom_components`, the
namespace it is nested in) and a dynamic import whose name a module-level constant holds (#2320 rounds
2 and 3). A key here is built from the node's own slot and from the name's RELATION TO SELF -- `anc`,
`self` or `desc`, computed at a dot boundary -- so no spelling of a reach appears in this file, the
planted tree is generated from the same table the classifier keys on, and the two cannot fall out of
step. A shape the classifier has no key for is counted `unkeyed` and refuses the census rather than
reading as a zero; `PRECONDITION` demonstrates that arm by dropping one classifier arm and requiring the
refusal.

    python3 dev/audit/harnesses/archscore_layering_seam_census.py <repo>
    python3 dev/audit/harnesses/archscore_layering_seam_census.py <repo> --corpus

`--corpus` censuses every commit `tools/audit/archscore/calibration/corpus.tsv` names (each pull request
and its parent); without it, the tree at `<repo>`.

Measured (R10-ARCHSCORE-COVERAGE part 3, #2320 round 4, 2026-10-17, Apple M1): see `## Figures` of the
pull request -- the numbers move whenever a corpus tree is added, so the enumerator is the command
above, not a literal here.
"""
from __future__ import annotations

import ast
import csv
import itertools
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from archscore.metrics import common as Mod

PKG = "custom_components/heatpump_optimizer"
SELF = PKG.replace("/", ".")
#: the namespace the package is nested in -- a strict PREFIX of SELF, derived from it.
NS = SELF.split(".")[0]
PIN = "7952d8f9e4fbe9945bc8742e8dc02be8fbe4582c"

#: how a dotted name stands to SELF. Derived from a dot boundary, never a spelling.
RELATIONS = ("anc", "self", "desc")
#: statement slot -> the relations a name in it can stand in. A relative import resolves inside the
#: package, so it is never `anc`. The keys and the planted tree are both generated from this table.
SLOTS = {
    "import": RELATIONS,
    "import_as": RELATIONS,
    "from": RELATIONS,
    "from_as": RELATIONS,
    "from_rel": ("self", "desc"),
    "from_rel_as": ("self", "desc"),
}
DYNAMICS = ("positional", "keyword", "const", "computed")
GUARDS = ("body", "else", "negated", "disjoined")
#: the READ side: how the chain is spelled, the relation of the binding its root name holds, and whether
#: the name read off it is public or private. The layer edge is taken by either; only the crossing is
#: private-only, which is why the two are keyed apart (round-4 review).
READ_SLOTS = ("attr", "getattr")
READ_VISIBILITY = ("public", "private")
#: the classifier's arms, one per node family. `PRECONDITION` drops one and requires `unkeyed` to fire.
ARMS = ("statement", "dynamic", "guard", "read")


def relation(name: str) -> str | None:
    """How ``name`` stands to this package: ``anc`` for a strict PREFIX of it (the namespace it is
    nested in), ``self`` for the package, ``desc`` for a path below it, None for everything else."""
    if name == SELF:
        return "self"
    if name.startswith(SELF + "."):
        return "desc"
    return "anc" if SELF.startswith(name + ".") else None


def keys() -> tuple[str, ...]:
    """The key set: the classifier's whole range, as the product of the statement slots against their
    relations plus the dynamic and guard slots. Derived, so a slot or a relation added to the tables
    above extends the census and the planted tree in one edit."""
    return (tuple(f"{slot}:{rel}" for slot, rels in SLOTS.items() for rel in rels)
            + tuple(f"dynamic:{d}" for d in DYNAMICS) + tuple(f"guard:{g}" for g in GUARDS)
            + tuple(f"read_{slot}:{rel}:{vis}" for slot in READ_SLOTS for rel in RELATIONS
                    for vis in READ_VISIBILITY))


def relative_source(mod: str, node: ast.ImportFrom) -> str:
    """The absolute path a relative import's names hang off, from the importing module's own name."""
    base = mod.split(".")[:-1]
    base = base[:len(base) - node.level + 1]
    src = ".".join(base + ([node.module] if node.module else []))
    return f"{SELF}.{src}" if src else SELF


def _dynamic_name(node: ast.Call) -> ast.AST | None:
    """The argument an ``import_module``/``__import__`` call takes its name from, positional or by the
    ``name`` keyword, or None when the call is not one of those."""
    f = node.func
    named = (isinstance(f, ast.Name) and f.id in ("import_module", "__import__")) or (
        isinstance(f, ast.Attribute) and f.attr in ("import_module", "__import__")
        and isinstance(f.value, ast.Name))
    if not named:
        return None
    return node.args[0] if node.args else next((k.value for k in node.keywords if k.arg == "name"), None)


def _dynamic_slot(node: ast.Call, mod: Mod) -> str:
    """Which slot the name sits in: positional, the ``name`` keyword, a module-level string constant, or
    a shape no static read follows."""
    first = _dynamic_name(node)
    if isinstance(first, ast.Constant) and isinstance(first.value, str):
        return "keyword" if not node.args else "positional"
    if isinstance(first, ast.Name):
        assign = mod.tops.get(first.id)
        if isinstance(assign, ast.Assign) and isinstance(assign.value, ast.Constant) \
                and isinstance(assign.value.value, str):
            return "const"
    return "computed"


def bindings(mod: Mod) -> dict[str, str]:
    """Local name -> the absolute dotted path the import statements of this module bind, for every name in
    this package's namespace. This module's OWN reader -- the metric's binding map is not imported here,
    so an arm that changes shape over there cannot move the census with it."""
    out: dict[str, str] = {}
    for n in ast.walk(mod.tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if relation(a.name) is not None:
                    out[a.asname or a.name.split(".")[0]] = a.name if a.asname else a.name.split(".")[0]
        elif isinstance(n, ast.ImportFrom):
            if n.level:
                path = relative_source(mod.name, n)
            elif n.module and relation(n.module) is not None:
                path = n.module
            else:
                continue
            for a in n.names:
                out.setdefault(a.asname or a.name, f"{path}.{a.name}")
    return out


def spells(modbind: dict[str, str], node: ast.AST) -> str | None:
    """The dotted path an expression spells through those bindings: a name, an attribute of one, and a
    ``getattr``/``hasattr``/``setattr`` with a constant name. None where a step is computed."""
    if isinstance(node, ast.Name):
        return modbind.get(node.id)
    if isinstance(node, ast.Attribute):
        base = spells(modbind, node.value)
        return f"{base}.{node.attr}" if base is not None else None
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
            and node.func.id in ("getattr", "hasattr", "setattr") and len(node.args) >= 2 \
            and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str):
        base = spells(modbind, node.args[0])
        return f"{base}.{node.args[1].value}" if base is not None else None
    return None


def root_of(node: ast.AST) -> ast.AST:
    """The name a chain is rooted at, through attributes and ``getattr`` calls."""
    while True:
        if isinstance(node, ast.Attribute):
            node = node.value
        elif isinstance(node, ast.Call) and node.args and isinstance(node.func, ast.Name) \
                and node.func.id in ("getattr", "hasattr", "setattr"):
            node = node.args[0]
        else:
            return node


def chain_end(parent: dict[int, ast.AST], node: ast.AST) -> bool:
    """Is this the node a dotted chain ends on? An attribute that is another attribute's ``value`` is a
    step of that chain, and the rule takes the edge once, on the outermost node (round-4 review)."""
    p = parent.get(id(node))
    return not (isinstance(p, ast.Attribute) and p.value is node)


def read_form(modbind: dict[str, str], mods: frozenset[str], parent: dict[int, ast.AST],
              node: ast.AST) -> str | None:
    """The read form a node spells: an attribute a dotted chain ENDS on, or a ``getattr`` with a constant
    name, whose receiver resolves to a module of this package. The key carries the direction the binding
    its root name holds roots in (anc/self/desc) and whether the name read off it is public or private --
    the layer edge is taken by either, and only the crossing is private-only (round-4 review)."""
    if not chain_end(parent, node):
        return None
    if isinstance(node, ast.Attribute):
        slot, receiver, name = "attr", node.value, node.attr
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
            and node.func.id in ("getattr", "hasattr", "setattr") and len(node.args) >= 2 \
            and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str):
        slot, receiver, name = "getattr", node.args[0], node.args[1].value
    else:
        return None
    path = spells(modbind, receiver)
    rel = relation(spells(modbind, root_of(receiver)) or "")
    if path is None or rel is None:
        return None
    if path == SELF:
        reached = "__init__"
    elif path.startswith(SELF + "."):
        reached = path[len(SELF) + 1:]
    else:
        return None
    if reached not in mods:
        return None
    vis = "private" if name.startswith("_") and not name.startswith("__") else "public"
    return f"read_{slot}:{rel}:{vis}"

def spelling(node: ast.AST, mod: Mod, mods: frozenset[str], parent: dict[int, ast.AST],
             modbind: dict[str, str], arms: tuple[str, ...] = ARMS) -> str | None:
    """The form of a reach into this package that ``node`` spells, or None. The key is the node's slot
    and the name's relation to SELF; nothing in it is a spelling."""
    if "statement" in arms and isinstance(node, ast.Import):
        for a in node.names:
            if (rel := relation(a.name)) is not None:
                return f"{'import_as' if a.asname else 'import'}:{rel}"
    elif "statement" in arms and isinstance(node, ast.ImportFrom):
        if node.level:
            src, slot = relative_source(mod.name, node), "from_rel"
        else:
            src, slot = node.module or "", "from"
        if (rel := relation(src)) is None:
            return None
        return f"{slot + ('_as' if any(a.asname for a in node.names) else '')}:{rel}"
    elif "dynamic" in arms and isinstance(node, ast.Call) and _dynamic_name(node) is not None:
        return f"dynamic:{_dynamic_slot(node, mod)}"
    elif "guard" in arms and isinstance(node, ast.If) and "TYPE_CHECKING" in ast.unparse(node.test):
        bare = (isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING") or (
            isinstance(node.test, ast.Attribute) and node.test.attr == "TYPE_CHECKING")
        if bare:
            return "guard:else" if node.orelse else "guard:body"
        return "guard:negated" if isinstance(node.test, ast.UnaryOp) else "guard:disjoined"
    elif "read" in arms:
        return read_form(modbind, mods, parent, node)
    return None


def touches(node: ast.AST, mod: Mod, mods: frozenset[str], parent: dict[int, ast.AST],
           modbind: dict[str, str]) -> bool:
    """Does ``node`` name this package's namespace at all, whether or not ``spelling`` has a key for its
    shape? The detector behind the ``unkeyed`` count: a form the classifier does not key refuses the
    census instead of reading as a zero (round-3 review)."""
    if isinstance(node, ast.Import):
        return any(relation(a.name) is not None for a in node.names)
    if isinstance(node, ast.ImportFrom):
        src = relative_source(mod.name, node) if node.level else (node.module or "")
        return relation(src) is not None
    if isinstance(node, ast.Call) and _dynamic_name(node) is not None:
        return True
    if isinstance(node, ast.If) and "TYPE_CHECKING" in ast.unparse(node.test):
        return True
    return read_form(modbind, mods, parent, node) is not None


def census(root: Path, arms: tuple[str, ...] = ARMS) -> dict[str, int]:
    """Per tree: the count of each form, and `unkeyed` for a package-naming node with no key."""
    from archscore.metrics import common as C

    # `common.load` is an lru_cache on the PATH, and `plant` rewrites one in place, so a cached
    # Pkg for this root would be the tree as it was before the rewrite (#2320 round 4).
    C.reset_caches()
    C.load.cache_clear()
    out: dict[str, int] = {}
    pkg = C.load(str(root))
    mods = frozenset(pkg.mods)
    for mod in pkg.mods.values():
        parent = {id(c): n for n in C.walk(mod.tree) for c in ast.iter_child_nodes(n)}
        modbind = bindings(mod)
        for n in C.walk(mod.tree):
            key = spelling(n, mod, mods, parent, modbind, arms)
            if key is not None:
                out[key] = out.get(key, 0) + 1
            elif touches(n, mod, mods, parent, modbind):
                out["unkeyed"] = out.get("unkeyed", 0) + 1
    return out


def plant(root: Path) -> None:
    """A tree carrying one instance of every key the classifier can emit, generated from the same
    tables the classifier keys on. `snippet` is the one place a spelling appears, and it is written per
    SLOT, instanced with a name chosen by the key's RELATION -- so a relation or a slot added above is
    planted here without a second edit."""
    p = root / PKG / "silent_mode.py"
    src = p.read_text()
    anchor = "from .optimizer import _utc_step_starts\n"
    assert src.count(anchor) == 1, "the planted tree is not the pin"
    mod = sorted(f.stem for f in (root / PKG).glob("*.py") if f.stem != "__init__")[0]

    def names(rel: str) -> tuple[str, str, str]:
        """(dotted name, base, leaf) for a statement whose name stands in this relation to the package."""
        if rel == "anc":
            return NS, NS, SELF.split(".")[-1]
        if rel == "self":
            return SELF, SELF, mod
        return f"{SELF}.{mod}", f"{SELF}.{mod}", "_utc_step_starts"

    def snippet(key: str) -> str:
        name, base, leaf = names(key.split(":")[1]) if key.split(":")[0] in SLOTS else ("", "", "")
        slot = key.split(":")[0]
        if slot == "import":
            return f"import {name}\n"
        if slot == "import_as":
            return f"import {name} as _t\n"
        if slot in ("from", "from_as"):
            return f"from {base} import {leaf}{' as _t' if slot == 'from_as' else ''}\n"
        if slot in ("from_rel", "from_rel_as"):
            rel = key.split(":")[1]
            inner = f"from . import {mod}" if rel == "self" else f"from .{mod} import _x"
            return f"{inner}{' as _t' if slot == 'from_rel_as' else ''}\n"
        if slot == "dynamic":
            d = key.split(":")[1]
            if d == "positional":
                return f'importlib.import_module(".{mod}", __package__)\n'
            if d == "keyword":
                return f'importlib.import_module(name=".{mod}", package=__package__)\n'
            if d == "const":
                return f'_MOD = ".{mod}"\nimportlib.import_module(_MOD, __package__)\n'
            return 'importlib.import_module(f".{_MOD}", __package__)\n'
        if slot.startswith("read_"):
            rel, vis = key.split(":")[1], key.split(":")[2]
            leaf = "_x" if vis == "private" else "reachable_name"
            # the receiver the read is taken off, in the alias's own terms: the namespace dotted down to
            # the module, the package dotted down to it, or the module the alias holds.
            # ONE ALIAS PER KEY: a shared name would be rebound by the next snippet and every read
            # would resolve through the last binding only.
            alias = "_" + key.replace(":", "_")
            recv = {"anc": f"{alias}.{SELF.split('.')[-1]}.{mod}", "self": f"{alias}.{mod}",
                    "desc": alias}[rel]
            binding = {"anc": NS, "self": SELF, "desc": f"{SELF}.{mod}"}[rel]
            read = f"getattr({recv}, '{leaf}')" if slot == "read_getattr" else f"{recv}.{leaf}"
            return f"import {binding} as {alias}\n{read}\n"
        if key == "guard:body":
            return f"if TYPE_CHECKING:\n    from .{mod} import _x  # noqa: F401\n"
        if key == "guard:else":
            return f"if TYPE_CHECKING:\n    pass\nelse:\n    from .{mod} import _x  # noqa: F401\n"
        if key == "guard:negated":
            return f"if not TYPE_CHECKING:\n    from .{mod} import _x  # noqa: F401\n"
        return f"if TYPE_CHECKING or False:\n    from .{mod} import _x  # noqa: F401\n"

    body = "import importlib\n" + "".join(snippet(k) for k in keys())
    p.write_text(src.replace(anchor, body))
    ast.parse(p.read_text())


def tree_of(repo: Path, sha: str, into: Path) -> Path:
    into.mkdir(parents=True, exist_ok=True)
    archive = subprocess.run(["git", "-C", str(repo), "archive", sha, PKG],
                             capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(into)], input=archive, check=True)
    return into


def main(argv: list[str]) -> int:
    repo = Path(argv[1]).resolve()
    sys.path.insert(0, str(repo / "tools" / "audit"))
    shas: list[str] = []
    if "--corpus" in argv:
        with open(repo / "tools/audit/archscore/calibration/corpus.tsv") as f:
            rows = list(csv.DictReader(f, delimiter="\t"))
        shas = sorted({r["sha"] for r in rows} | {r["parent"] for r in rows})
    total = dict.fromkeys(keys(), 0)
    total["unkeyed"] = 0
    with tempfile.TemporaryDirectory(prefix="layering-seam-census-") as tmp:
        if shas:
            print(f"corpus trees censused: {len(shas)}")
            for sha in shas:
                for k, v in census(tree_of(repo, sha, Path(tmp) / sha[:8])).items():
                    total[k] = total.get(k, 0) + v
        else:
            for k, v in census(repo).items():
                total[k] = total.get(k, 0) + v
        for k, v in total.items():
            print(f"RESULT {k}={v} count")
        t = tree_of(repo, PIN, Path(tmp) / "planted")
        plant(t)
        planted = census(t)
        # the control for the unkeyed arm: drop one classifier arm and the same tree must refuse.
        dropped = census(t, arms=tuple(a for a in ARMS if a != "statement"))
    fired = {k: v for k, v in planted.items() if k != "unkeyed"}
    missing = sorted(set(keys()) - set(fired))
    for k in keys():
        print(f"RESULT planted_{k}={fired.get(k, 0)} count")
    print(f"RESULT planted_unkeyed={planted.get('unkeyed', 0)} count")
    zero = sorted(k for k in keys() if not fired.get(k))
    ok = (not zero and not planted.get("unkeyed") and not total.get("unkeyed")
          and dropped.get("unkeyed", 0) > 0)
    print(f"PRECONDITION {'ok' if ok else 'FAILED'}: the planted tree fires every derived key "
          f"({len(keys())}), no tree leaves a package-naming node unkeyed, and dropping an arm "
          f"({dropped.get('unkeyed', 0)} unkeyed) refuses; planted zero: {zero or 'none'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
