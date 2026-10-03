#!/usr/bin/env python3
"""Every Home Assistant name production reaches, against the release hacs.json
declares as its floor (class P11's floor arm; tools/audit/rca/R9-RCA-1869.md).

    python3 tests/ha_floor.py check [--package DIR]       # the gate's arm, alone
    python3 tests/ha_floor.py record [--tag 2025.2.0] [--cache DIR] [TREE ...]
    python3 tests/ha_floor.py verify --image homeassistant/home-assistant:2025.2.0
    python3 tests/ha_floor.py verify-inside tests/ha_floor_names.json   # in HA

`tests/entities.py` imports ``floor_reach`` and ``floor_check`` and runs them on
the PR gate, offline, against ``tests/ha_floor_names.json``. The gate's only
other oracle for Home Assistant is tests/hastub, and a stub may define a name the
floor lacks: v6.3.1 shipped ``Platform.DIAGNOSTICS`` that way (#210) and #1869
imported ``UnsupportedStorageVersionError`` (2026.3+) that way, each green on
every PR-gate lane. Neither is a stub defect -- the stub may model a newer
release -- so the check reads production's reach, never the stub.

THE UNIT, read off production's AST, never off a list. Production is every
``.py`` under the package, subpackages included:

  M  ``import homeassistant.x.y [as z]``, and a constant ``__import__`` or
     ``importlib.import_module`` of a Home Assistant module -> the module exists
  I  ``from homeassistant.x import n``      -> n is bound at module scope of x, or
                                               x.n is a module
  A  ``z.n`` where z names a Home Assistant module -> n is bound in that module.
     z is an alias (``from homeassistant.helpers import storage as z``), a
     local rebind of one (``z2 = z``), or the bare dotted spelling
     (``import homeassistant.a.b`` then ``homeassistant.a.b.n``); a constant
     ``getattr(z, "n")`` with no default reads the same
  C  ``C.n`` where C was imported from Home Assistant, directly or through a
     module alias (``ir.IssueSeverity.WARNING``, ``const.Platform.X``), and is a
     class defined in its module (re-exports followed) whose base chain stays
     in Home Assistant or ends in a builtin or enum base -> n is a member (the
     v6.3.1 shape)

Guarded, and not checked: a node inside the body of a ``try`` whose handlers
catch ImportError, ModuleNotFoundError or AttributeError and do not raise again,
except inside a ``def`` or ``lambda`` there, whose body runs later, outside the
handler; and a node under ``if TYPE_CHECKING:`` where that name is typing's and
the module never rebinds it. ``except Exception`` is not a guard here, the
fail-safe direction. Typing-only, and not checked: an annotation in a module
with ``from __future__ import annotations``, which is never evaluated.

RESIDUAL, NOT READ (0 production sites each when this was written; a seat that
adds one reaches past the check):
  * a re-export between production modules (``from .a import ha_storage`` and
    ``ha_storage.n`` in another file): relative imports are not followed;
  * a chain two or more names past the class (``z.C.n.m``), and an attribute of
    a call's result (``__import__("homeassistant.x").n``);
  * a non-constant ``getattr`` or import, and a rebind other than ``a = b``;
  * a guarded import whose name is used after the guard (NameError, not
    ImportError, at the floor), and a handler written for another reason that
    happens to catch AttributeError (two ``dt_util`` sites under
    ``except (AttributeError, TypeError)``; their names are checked elsewhere);
  * a class member inherited from outside Home Assistant's chain (UNDECIDABLE,
    printed, not failed), and behaviour that changed under an unchanged name
    (``tests/ha_contract.py``'s ground, nightly).

FAIL-CLOSED. The snapshot holds one recorded answer per question, and a question
it does not hold is UNRECORDED, which fails: a new import or a new name cannot
go green by being unknown. The snapshot is never edited by hand; the nightly
floor container answers every recorded question again with Home Assistant
itself (``verify``), so a wrong answer reddens within a night.

RE-RECORDING. A branch that adds a Home Assistant name re-records, in the same
branch: ``python3.13 tests/ha_floor.py record`` (any Python 3.12 or newer: the
upstream source has 3.12 syntax) with ``gh`` authenticated and the network up;
about 30 s from a cold cache. A seat without ``gh`` (a web seat) hands the
re-record to one that has it. Two branches that each re-recorded conflict in the
JSON: take either side, finish the merge, then re-record on the merged tree.

Node ids are kept PER FILE. The RCA's prototype held them in one set across
files whose trees it discarded as it went; CPython recycled the ids, a guard of
one file blessed a node of another, and the #1869 defect went green.
"""
from __future__ import annotations

import argparse
import ast
import base64
import builtins
import enum
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "custom_components" / "heatpump_optimizer"
SNAPSHOT = REPO / "tests" / "ha_floor_names.json"
UPSTREAM = "home-assistant/core"

GUARD_EXC = frozenset({"ImportError", "ModuleNotFoundError", "AttributeError"})
#: Bases a class chain may end in: the enum family and the builtin types. A
#: member they define (``.value``, ``.args``) is answered from this
#: interpreter's own type, never assumed absent.
TERMINAL_BASES = {
    "Enum": enum.Enum, "StrEnum": getattr(enum, "StrEnum", str),
    "IntEnum": enum.IntEnum, "IntFlag": enum.IntFlag, "Flag": enum.Flag,
    **{k: v for k, v in vars(builtins).items() if isinstance(v, type)},
}

_U = "UnsupportedStorageVersionError"
#: Planted trees, ``name -> (recorded, expected verdict, source)``. The snapshot
#: records the questions of the ``recorded`` ones, so a planted defect reads
#: MISSING rather than UNRECORDED; tests/entities.py asserts every verdict (the
#: P11 floor null controls). The expected verdict is ``missing:<line>`` (that
#: site must be named), ``clean`` (the file must not be named), or
#: ``unrecorded:<key>`` (fail-closed must read that question).
FLOOR_CONTROLS = {
    # #1869's shape: the name entered 2026.3.
    "plant_import.py": (True, "missing:1", f"from homeassistant.helpers.storage import {_U}\n"),
    # The same name through a module alias (arm A).
    "plant_alias.py": (True, "missing:2", "from homeassistant.helpers import storage as s\n"
                                          f"s.{_U}\n"),
    # v6.3.1's shape (arm C): the stub had the member, the floor never did.
    "plant_member.py": (True, "missing:2", "from homeassistant.const import Platform\n"
                                           "Platform.DIAGNOSTICS\n"),
    # v6.3.1's name through a module alias, and production's own most common
    # spelling of a member (``ir.IssueSeverity.X``): arm C behind arm A.
    "plant_chained.py": (True, "missing:2", "from homeassistant import const\n"
                                            "const.Platform.DIAGNOSTICS\n"),
    "plant_chained_as.py": (True, "missing:2",
                            "from homeassistant.helpers import issue_registry as ir\n"
                            "ir.IssueSeverity.NO_SUCH_MEMBER_AT_FLOOR\n"),
    # The bare dotted spelling, a local rebind and a constant getattr.
    "plant_bare_dotted.py": (True, "missing:2", "import homeassistant.helpers.storage\n"
                                                f"homeassistant.helpers.storage.{_U}\n"),
    "plant_rebind.py": (True, "missing:3", "from homeassistant.helpers import storage as s\n"
                                           f"s2 = s\ns2.{_U}\n"),
    "plant_getattr.py": (True, "missing:2", "from homeassistant.helpers import storage as s\n"
                                            f"getattr(s, '{_U}')\n"),
    # A getattr with a default is the safe probe, and legitimate.
    "plant_getattr_default.py": (True, "clean", "from homeassistant.helpers import storage as s\n"
                                                f"getattr(s, '{_U}', None)\n"),
    # Guards that are not guards: Exception, a re-raise, a body run later, a
    # TYPE_CHECKING the module rebinds.
    "plant_except_exception.py": (True, "missing:2", f"try:\n    from homeassistant.helpers.storage import {_U}\n"
                                                     "except Exception:\n    pass\n"),
    "plant_reraise.py": (True, "missing:2", f"try:\n    from homeassistant.helpers.storage import {_U}\n"
                                            "except ImportError:\n    raise\n"),
    "plant_deferred.py": (True, "missing:4", "from homeassistant.helpers import storage as s\n"
                                             "try:\n    def f():\n"
                                             f"        return s.{_U}\n"
                                             "except AttributeError:\n    pass\n"),
    "plant_fake_typecheck.py": (True, "missing:3", "TYPE_CHECKING = True\nif TYPE_CHECKING:\n"
                                                   f"    from homeassistant.helpers.storage import {_U}\n"),
    # An annotation is evaluated where annotations are not postponed.
    "plant_no_future.py": (True, "missing:2", "from homeassistant.helpers import storage as s\n"
                                              f"def f(x: s.{_U}) -> None:\n    return None\n"),
    # Guarded, and typing-only: legitimate.
    "plant_guarded.py": (True, "clean", f"try:\n    from homeassistant.helpers.storage import {_U}\n"
                                        "except ImportError:\n    pass\n"),
    "plant_typing.py": (True, "clean", "from __future__ import annotations\n"
                                       "from typing import TYPE_CHECKING\n"
                                       "from homeassistant.helpers import storage as s\n"
                                       "if TYPE_CHECKING:\n    from homeassistant.helpers.storage "
                                       f"import {_U}\n"
                                       f"def f(x: s.{_U}) -> None:\n    return None\n"),
    # Never recorded, so fail-closed must read them, imported and dynamic.
    "plant_unrecorded.py": (False, "unrecorded:module:homeassistant.helpers.frame",
                            "from homeassistant.helpers.frame import report_usage\n"),
    "plant_dynamic.py": (False, "unrecorded:module:homeassistant.helpers.no_such_floor_module",
                         "import importlib\n"
                         "importlib.import_module('homeassistant.helpers.no_such_floor_module')\n"),
}


def _real_type_checking(tree: ast.Module) -> bool:
    """``TYPE_CHECKING`` here is typing's, never rebound: a module that assigns
    it (``TYPE_CHECKING = True``) makes ``if TYPE_CHECKING:`` code that runs."""
    imported = any(isinstance(n, ast.ImportFrom) and n.module in ("typing", "typing_extensions")
                   and any(a.name == "TYPE_CHECKING" and not a.asname for a in n.names)
                   for n in ast.walk(tree))
    rebound = any(isinstance(n, ast.Name) and n.id == "TYPE_CHECKING"
                  and isinstance(n.ctx, ast.Store) for n in ast.walk(tree))
    return imported and not rebound


def _is_type_checking(test: ast.expr, real: bool = True) -> bool:
    if isinstance(test, ast.Name):
        return real and test.id == "TYPE_CHECKING"
    return isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING" \
        and isinstance(test.value, ast.Name) and test.value.id in ("typing", "typing_extensions")


def _guard_body(node: ast.AST, real_tc: bool = True) -> list[ast.stmt]:
    """The statements a recognised guard protects, or none. A handler that
    raises again (``except ImportError: raise``) is no guard."""
    if isinstance(node, ast.Try):
        guards = False
        for handler in node.handlers:
            kinds = handler.type.elts if isinstance(handler.type, ast.Tuple) \
                else [handler.type]
            if {k.id for k in kinds if isinstance(k, ast.Name)} & GUARD_EXC:
                if any(isinstance(x, ast.Raise) for b in handler.body for x in ast.walk(b)):
                    return []
                guards = True
        return node.body if guards else []
    if isinstance(node, ast.If) and _is_type_checking(node.test, real_tc):
        return node.body
    return []


_DEFERRED = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)


def _now(stmt: ast.AST, deferred_too: bool):
    """Nodes of ``stmt`` that run when it does: a def or lambda body runs later,
    outside the handler, so a try blesses none of it (``deferred_too`` False)."""
    stack = [stmt]
    while stack:
        n = stack.pop()
        if not deferred_too and isinstance(n, _DEFERRED):
            continue
        yield n
        stack.extend(ast.iter_child_nodes(n))


def _annotations(node: ast.AST) -> list[ast.expr]:
    if isinstance(node, ast.AnnAssign):
        return [node.annotation]
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        a = node.args
        every = a.posonlyargs + a.args + a.kwonlyargs + [
            x for x in (a.vararg, a.kwarg) if x]
        return [x.annotation for x in every if x.annotation] + (
            [node.returns] if node.returns else [])
    return []


def _chain(node: ast.expr) -> list[str] | None:
    """``a.b.c`` as ``["a", "b", "c"]``, or None for anything but names."""
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    return [node.id, *reversed(parts)]


def _dynamic_module(node: ast.Call) -> str | None:
    """The module a constant ``__import__``/``import_module`` call imports."""
    f = node.func
    named = (isinstance(f, ast.Name) and f.id in ("__import__", "import_module")) or (
        isinstance(f, ast.Attribute) and f.attr == "import_module"
        and isinstance(f.value, ast.Name) and f.value.id == "importlib")
    if named and node.args and isinstance(node.args[0], ast.Constant) \
            and isinstance(node.args[0].value, str) \
            and node.args[0].value.split(".")[0] == "homeassistant":
        return node.args[0].value
    return None


def floor_reach(trees: dict[str, ast.Module],
                walks: dict[str, list[ast.AST]] | None = None,
                ) -> dict[tuple[str, str, str], list[str]]:
    """``(kind, target, name) -> sites`` for every unguarded reach.

    kind ``M`` (module import), ``I`` (from-import), ``X`` (an attribute of an
    imported name: arm A or C, decided by the snapshot's ``module:`` answer).
    For ``X`` the target is ``"<module>|<imported name or ''>"``: an empty
    imported name means the alias IS the module (``import a.b as z``). A chain
    one deeper (``z.C.n``, ``ir.IssueSeverity.WARNING``) is ``X`` again, with
    ``z``'s module path as the module and ``C`` as the imported name, so arm C
    reads a member reached through a module alias.
    ``walks`` is ``ast.walk`` of each tree, already listed (tests/entities.py
    has it for P6); one pass over it collects everything the arms read.
    """
    out: dict[tuple[str, str, str], list[str]] = {}

    def emit(kind: str, target: str, name: str, fname: str, node: ast.AST) -> None:
        out.setdefault((kind, target, name), []).append(f"{fname}:{node.lineno}")

    for fname, tree in sorted(trees.items()):
        evaluated = not any(isinstance(x, ast.ImportFrom) and x.module == "__future__"
                            and any(a.name == "annotations" for a in x.names)
                            for x in tree.body)
        real_tc = _real_type_checking(tree)
        # Per file, always: see the module docstring.
        safe: set[int] = set()
        typing_only: set[int] = set()
        imports: list[ast.Import | ast.ImportFrom] = []
        attributes: list[ast.Attribute] = []
        rebinds: list[ast.Assign] = []
        calls: list[ast.Call] = []
        nodes = walks.get(fname) if walks is not None else None
        for node in (nodes if nodes is not None else ast.walk(tree)):
            if isinstance(node, ast.If) and _is_type_checking(node.test, real_tc):
                for stmt in node.body:  # never runs at all, defs included
                    safe.update(id(x) for x in _now(stmt, True))
            else:
                for stmt in _guard_body(node, real_tc):
                    safe.update(id(x) for x in _now(stmt, False))
            if not evaluated:
                for ann in _annotations(node):
                    typing_only.update(id(x) for x in ast.walk(ann))
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)
            elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load):
                attributes.append(node)
            elif isinstance(node, ast.Assign) and len(node.targets) == 1 \
                    and isinstance(node.targets[0], ast.Name) \
                    and isinstance(node.value, ast.Name):
                rebinds.append(node)
            elif isinstance(node, ast.Call):
                calls.append(node)
        alias: dict[str, tuple[str, str]] = {}
        bare: set[str] = set()
        for node in imports:
            if isinstance(node, ast.ImportFrom):
                if node.level or not node.module \
                        or node.module.split(".")[0] != "homeassistant":
                    continue
                for a in node.names:
                    if id(node) not in safe:
                        emit("I", node.module, a.name, fname, node)
                    alias[a.asname or a.name] = (node.module, a.name)
                continue
            for a in node.names:
                if a.name.split(".")[0] != "homeassistant":
                    continue
                if id(node) not in safe:
                    emit("M", a.name, "", fname, node)
                if a.asname:
                    alias[a.asname] = (a.name, "")
                else:
                    bare.add(a.name)
        for node in rebinds:  # ``s2 = s``: the alias travels with the name
            if node.value.id in alias:
                alias.setdefault(node.targets[0].id, alias[node.value.id])
        for node in calls:
            if id(node) in safe:
                continue
            module = _dynamic_module(node)
            if module:
                emit("M", module, "", fname, node)
            elif isinstance(node.func, ast.Name) and node.func.id == "getattr" \
                    and len(node.args) == 2 and not node.keywords \
                    and isinstance(node.args[0], ast.Name) and node.args[0].id in alias \
                    and isinstance(node.args[1], ast.Constant) \
                    and isinstance(node.args[1].value, str):
                mod, name = alias[node.args[0].id]
                emit("X", f"{mod}|{name}", node.args[1].value, fname, node)
        for node in attributes:
            if id(node) in safe or id(node) in typing_only:
                continue
            parts = _chain(node)
            if not parts:
                continue
            if parts[0] in alias:
                mod, name = alias[parts[0]]
                rest = parts[1:]
            elif parts[0] == "homeassistant" and bare:
                # ``import homeassistant.a.b`` then ``homeassistant.a.b.n``:
                # the longest imported prefix is the module.
                prefixes = [i for i in range(1, len(parts))
                            if ".".join(parts[:i]) in bare]
                if not prefixes:
                    continue
                mod, name, rest = ".".join(parts[:prefixes[-1]]), "", parts[prefixes[-1]:]
            else:
                continue
            if len(rest) == 1:
                emit("X", f"{mod}|{name}", rest[0], fname, node)
            elif len(rest) == 2:
                emit("Y", f"{mod}.{name}" if name else mod, f"{rest[0]}.{rest[1]}",
                     fname, node)
    return out


def floor_check(reach, answers: dict[str, bool | None]) -> dict[str, list[str] | int]:
    """MISSING, UNRECORDED and UNDECIDABLE lines, and how many reaches were checked."""
    missing: list[str] = []
    unrecorded: set[str] = set()
    undecidable: list[str] = []
    checked = 0

    def ask(key: str) -> bool | None | str:
        if key not in answers:
            unrecorded.add(key)
            return "?"
        return answers[key]

    def attribute(mod: str, imported: str, name: str, where: str) -> None:
        """Arm A or C: ``name`` read off ``mod.imported`` (or ``mod`` itself)."""
        nonlocal checked
        path = f"{mod}.{imported}" if imported else mod
        is_module = ask(f"module:{path}")
        if is_module == "?":
            return
        if is_module:
            bound = ask(f"name:{path}:{name}")
            if bound == "?":
                return
            checked += 1
            if not bound:
                missing.append(f"{path}.{name} (attribute) at {where}")
            return
        if not imported:
            return  # the import itself is M's finding
        member = ask(f"member:{mod}:{imported}.{name}")
        if member == "?":
            return
        if member is None:
            undecidable.append(f"{mod}.{imported}.{name}")
            return
        checked += 1
        if not member:
            missing.append(f"{mod}.{imported}.{name} (class member) at {where}")

    for (kind, target, name), sites in sorted(reach.items()):
        where = ", ".join(sites)
        if kind == "M":
            ok = ask(f"module:{target}")
            if ok == "?":
                continue
            checked += 1
            if not ok:
                missing.append(f"import {target} at {where}")
        elif kind == "I":
            ok = ask(f"module:{target}")
            if ok == "?":
                continue
            if not ok:
                checked += 1
                missing.append(f"{target} is not a module, at {where}")
                continue
            bound = ask(f"name:{target}:{name}")
            if bound == "?":
                continue
            checked += 1
            if not bound:
                missing.append(f"{target}.{name} at {where}")
        elif kind == "X":
            mod, imported = target.split("|")
            attribute(mod, imported, name, where)
        else:  # Y: ``z.C.n``, read only where z names a module
            inner, member = name.split(".")
            if ask(f"module:{target}") is True:
                attribute(target, inner, member, where)
    return {"checked": checked, "missing": missing,
            "unrecorded": sorted(unrecorded), "undecidable": undecidable}


def floor_load(path: Path = SNAPSHOT) -> dict:
    return json.loads(path.read_text())


def floor_trees(root: Path = PACKAGE, reuse: dict[str, ast.Module] | None = None,
                ) -> dict[str, ast.Module]:
    """Every production module, subpackages included, keyed by its path under
    ``root``; ``reuse`` supplies trees already parsed (P6's, keyed alike)."""
    out = {}
    for p in sorted(root.rglob("*.py")):
        rel = p.relative_to(root).as_posix()
        out[rel] = (reuse or {}).get(rel) or ast.parse(p.read_text())
    return out


def floor_control_trees(recorded_only: bool = False) -> dict[str, ast.Module]:
    return {name: ast.parse(src) for name, (rec, _expect, src) in FLOOR_CONTROLS.items()
            if rec or not recorded_only}


def floor_control_failures(result: dict) -> list[str]:
    """Each planted tree whose verdict is not the one ``FLOOR_CONTROLS`` expects."""
    named = " ".join(result["missing"])
    bad = []
    for name, (_rec, expect, _src) in FLOOR_CONTROLS.items():
        kind, _, arg = expect.partition(":")
        if kind == "missing" and f"{name}:{arg}" not in named:
            bad.append(f"{name}: expected its line {arg} named")
        elif kind == "clean" and name in named:
            bad.append(f"{name}: legitimate, but named")
        elif kind == "unrecorded" and arg not in result["unrecorded"]:
            bad.append(f"{name}: expected {arg} unrecorded")
    expected_unrecorded = {e.partition(":")[2] for _r, e, _s in FLOOR_CONTROLS.values()
                           if e.startswith("unrecorded:")}
    extra = set(result["unrecorded"]) - expected_unrecorded
    if extra:
        bad.append(f"unrecorded beyond the planted ones: {sorted(extra)}")
    return bad


# --- recording: from upstream source at the tag, never by hand -------------

#: Written into the snapshot, where a seat with a conflict in it will read it.
RECORD_NOTE = (
    "Recorded by `tests/ha_floor.py record` from upstream source; never edit by hand. "
    "A branch that adds a Home Assistant name re-records: Python 3.12+ "
    "(`python3.13 tests/ha_floor.py record`) with `gh` authenticated. On a merge "
    "conflict in this file, take either side, finish the merge, then re-record.")
REMEDY = ("re-record with Python 3.12+ and an authenticated gh "
          "(`python3.13 tests/ha_floor.py record`; a seat without gh hands it on), "
          "or guard the reach")

class RecordError(RuntimeError):
    pass


class _Scope:
    """One upstream module: run-time module-scope names, classes, import origins."""

    def __init__(self, module: str, tree: ast.Module, package: bool):
        self.names: set[str] = set()
        self.classes: dict[str, ast.ClassDef] = {}
        self.origins: dict[str, tuple[str, str]] = {}
        self.star = False
        base = module if package else module.rpartition(".")[0]
        self._base = base.split(".")
        self._visit(tree.body)

    def _absolute(self, node: ast.ImportFrom) -> str:
        if not node.level:
            return node.module or ""
        parts = self._base[: len(self._base) - (node.level - 1)]
        return ".".join(parts + ([node.module] if node.module else []))

    def _visit(self, stmts: list[ast.stmt]) -> None:
        for s in stmts:
            if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self.names.add(s.name)
                if isinstance(s, ast.ClassDef):
                    self.classes[s.name] = s
            elif isinstance(s, ast.Assign):
                for t in s.targets:
                    self.names.update(y.id for y in ast.walk(t) if isinstance(y, ast.Name))
            elif isinstance(s, ast.AnnAssign) and s.value is not None:
                self.names.update(
                    y.id for y in ast.walk(s.target) if isinstance(y, ast.Name))
            elif isinstance(s, ast.Import):
                self.names.update((a.asname or a.name).split(".")[0] for a in s.names)
            elif isinstance(s, ast.ImportFrom):
                source = self._absolute(s)
                for a in s.names:
                    if a.name == "*":
                        self.star = True
                        continue
                    self.names.add(a.asname or a.name)
                    self.origins[a.asname or a.name] = (source, a.name)
            elif type(s).__name__ == "TypeAlias":
                self.names.add(s.name.id)  # type: ignore[attr-defined]
            elif isinstance(s, ast.If):
                if not _is_type_checking(s.test):
                    self._visit(s.body)
                self._visit(s.orelse)
            elif isinstance(s, ast.Try):
                self._visit(s.body)
                for h in s.handlers:
                    self._visit(h.body)
                self._visit(s.orelse)
                self._visit(s.finalbody)


def _class_body(cls: ast.ClassDef) -> set[str]:
    """Class attributes at run time: an annotation with no value binds none."""
    body: set[str] = set()
    for s in cls.body:
        if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body.add(s.name)
        elif isinstance(s, ast.Assign):
            for t in s.targets:
                body.update(y.id for y in ast.walk(t) if isinstance(y, ast.Name))
        elif isinstance(s, ast.AnnAssign) and s.value is not None:
            body.update(y.id for y in ast.walk(s.target) if isinstance(y, ast.Name))
    return body


class _Upstream:
    """Answers ``floor_check``'s questions from upstream source at ``tag``."""

    def __init__(self, tag: str, cache: Path):
        self.tag, self.cache = tag, cache
        self._scopes: dict[str, _Scope | None] = {}
        self.answers: dict[str, bool | None] = {}

    def _fetch(self, module: str) -> tuple[str, bool] | None:
        """(source, is_package) of ``module`` at the tag; None only on a 404."""
        root = self.cache / self.tag
        root.mkdir(parents=True, exist_ok=True)
        stem = module.replace(".", "/")
        for path, package in ((f"{stem}.py", False), (f"{stem}/__init__.py", True)):
            hit = root / path.replace("/", "__")
            if hit.exists():
                return hit.read_text(), package
        if (root / f"{module}.absent").exists():
            return None
        for path, package in ((f"{stem}.py", False), (f"{stem}/__init__.py", True)):
            r = subprocess.run(
                ["gh", "api", f"repos/{UPSTREAM}/contents/{path}?ref={self.tag}"],
                capture_output=True, text=True)
            if r.returncode == 0:
                src = base64.b64decode(json.loads(r.stdout)["content"]).decode()
                (root / path.replace("/", "__")).write_text(src)
                return src, package
            if "HTTP 404" not in r.stderr:
                # A network or auth failure is not an answer; recording it as
                # one would write a false "absent".
                raise RecordError(f"gh api {path}@{self.tag}: {r.stderr.strip()[:200]}")
        (root / f"{module}.absent").write_text("")
        return None

    def scope(self, module: str) -> _Scope | None:
        if module not in self._scopes:
            got = self._fetch(module) if module.split(".")[0] == "homeassistant" else None
            self._scopes[module] = None if got is None else _Scope(
                module, ast.parse(got[0]), got[1])
        return self._scopes[module]

    def member(self, module: str, cls: str, attr: str, depth: int = 0) -> bool | None:
        """True/False when the class chain is decidable, else None.

        A re-export (``from .const import HVACMode`` in climate/__init__.py) is
        followed to the defining module; a base ends the chain decidably only
        in that module's classes, another Home Assistant module, or a builtin
        or enum base."""
        s = self.scope(module)
        if s is None or depth > 8:
            return None
        if cls not in s.classes:
            if cls in s.origins and s.origins[cls][0].split(".")[0] == "homeassistant":
                return self.member(*s.origins[cls], attr, depth + 1)
            return None
        node = s.classes[cls]
        if attr in _class_body(node):
            return True
        verdicts: list[bool | None] = []
        for base in node.bases:
            label = ast.unparse(base).split("[")[0]
            if label in s.classes:
                verdicts.append(self.member(module, label, attr, depth + 1))
            elif label in s.origins and s.origins[label][0].split(".")[0] == "homeassistant":
                verdicts.append(self.member(*s.origins[label], attr, depth + 1))
            elif label.rpartition(".")[2] in TERMINAL_BASES:
                verdicts.append(hasattr(TERMINAL_BASES[label.rpartition(".")[2]], attr))
            else:
                verdicts.append(None)
        if not node.bases:
            verdicts.append(hasattr(object, attr))
        if any(v is True for v in verdicts):
            return True
        if all(v is False for v in verdicts):
            return False
        return None

    def answer(self, key: str) -> bool | None:
        kind, _, rest = key.partition(":")
        if kind == "module":
            return self.scope(rest) is not None
        if kind == "name":
            module, name = rest.rsplit(":", 1)
            s = self.scope(module)
            if s is None:
                return False
            if name in s.names or self.scope(f"{module}.{name}") is not None:
                return True
            if s.star:
                raise RecordError(f"{key}: {module} star-imports; not decidable")
            return False
        module, member = rest.rsplit(":", 1)
        cls, attr = member.split(".", 1)
        return self.member(module, cls, attr)


class _Recording(dict):
    """The answers ``floor_check`` asks for, fetched as it asks: the record
    walks exactly the check's own decision path, so it records nothing the
    check never reads and misses nothing it does."""

    def __init__(self, upstream: _Upstream):
        super().__init__()
        self.upstream = upstream

    def __contains__(self, key: object) -> bool:
        return True

    def __missing__(self, key: str) -> bool | None:
        self[key] = value = self.upstream.answer(key)
        return value


def record(tag: str, cache: Path, trees: dict[str, ast.Module]) -> dict:
    if sys.version_info < (3, 12):
        raise RecordError("record parses upstream source with 3.12 syntax: run it under "
                          "Python 3.12+ (`python3.13 tests/ha_floor.py record`), with gh "
                          "authenticated")
    answers = _Recording(_Upstream(tag, cache))
    floor_check(floor_reach(trees), answers)
    return {"tag": tag, "upstream": UPSTREAM, "answers": dict(sorted(answers.items()))}


# --- verification: Home Assistant itself answers each question --------------

def verify_inside(snapshot: Path) -> int:
    """Run inside the floor image. Every recorded answer, asked again."""
    import importlib

    data = json.loads(snapshot.read_text())
    import homeassistant.const as ha_const

    origin = Path(ha_const.__file__).resolve()
    if snapshot.resolve().parent in origin.parents:
        print(f"FAIL homeassistant resolved beside the snapshot: {origin}")
        return 1
    if ha_const.__version__ != data["tag"]:
        print(f"FAIL running Home Assistant {ha_const.__version__}, snapshot {data['tag']}")
        return 1

    def importable(module: str) -> bool:
        try:
            importlib.import_module(module)
        except ImportError:
            return False
        return True

    wrong: list[str] = []
    asked = 0
    for key, recorded in sorted(data["answers"].items()):
        kind, _, rest = key.partition(":")
        if kind == "module":
            actual: bool | None = importable(rest)
        elif kind == "name":
            module, name = rest.rsplit(":", 1)
            actual = importable(module) and (
                hasattr(importlib.import_module(module), name)
                or importable(f"{module}.{name}"))
        else:
            module, member = rest.rsplit(":", 1)
            cls, attr = member.split(".", 1)
            if recorded is None:
                continue
            owner = getattr(importlib.import_module(module), cls, None)
            actual = None if not isinstance(owner, type) else hasattr(owner, attr)
        asked += 1
        if actual != recorded:
            wrong.append(f"{key}: recorded {recorded}, Home Assistant {data['tag']} says {actual}")
    print(f"VERIFY tag={data['tag']} asked={asked} wrong={len(wrong)}")
    for line in wrong:
        print("WRONG", line)
    return 1 if (wrong or asked == 0) else 0


def verify(image: str) -> int:
    """Host half: stage the two files and run ``verify-inside`` in the image."""
    with tempfile.TemporaryDirectory(prefix="ha-floor-") as tmp:
        stage = Path(tmp)
        (stage / "ha_floor.py").write_bytes(Path(__file__).read_bytes())
        (stage / "ha_floor_names.json").write_bytes(SNAPSHOT.read_bytes())
        command = ["docker", "run", "--rm", "-v", f"{stage}:/hpo-floor:ro",
                   "--entrypoint", "python3", image,
                   "/hpo-floor/ha_floor.py", "verify-inside",
                   "/hpo-floor/ha_floor_names.json"]
        print("$ " + " ".join(command), flush=True)
        return subprocess.run(command).returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    rec = sub.add_parser("record")
    rec.add_argument("--tag", help="default: the floor hacs.json declares")
    rec.add_argument("--cache", type=Path, default=Path(tempfile.gettempdir()) / "ha-floor-cache")
    rec.add_argument("--out", type=Path, default=SNAPSHOT)
    rec.add_argument("trees", nargs="*", type=Path,
                     help="extra package directories whose reach is recorded too")
    chk = sub.add_parser("check")
    chk.add_argument("--package", type=Path, default=PACKAGE)
    ver = sub.add_parser("verify")
    ver.add_argument("--image", required=True)
    ins = sub.add_parser("verify-inside")
    ins.add_argument("snapshot", type=Path)
    args = parser.parse_args(argv)
    if args.cmd == "check":
        r = floor_check(floor_reach(floor_trees(args.package)), floor_load()["answers"])
        print(f"RESULT checked={r['checked']} missing={len(r['missing'])} "
              f"unrecorded={len(r['unrecorded'])} undecidable={len(r['undecidable'])}")
        for kind in ("missing", "unrecorded", "undecidable"):
            for line in r[kind]:
                print(kind.upper(), line)
        if r["missing"] or r["unrecorded"]:
            print("REMEDY:", REMEDY)
            return 1
        return 0
    if args.cmd == "verify":
        return verify(args.image)
    if args.cmd == "verify-inside":
        return verify_inside(args.snapshot)
    tag = args.tag or json.loads((REPO / "hacs.json").read_text())["homeassistant"]
    trees = {**floor_trees(), **{f"control/{k}": v
                                 for k, v in floor_control_trees(recorded_only=True).items()}}
    for i, extra in enumerate(args.trees):
        trees.update({f"extra{i}/{k}": v for k, v in floor_trees(extra).items()})
    data = {"_comment": RECORD_NOTE, **record(tag, args.cache, trees)}
    args.out.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
    answers = data["answers"]
    print(f"RECORDED tag={tag} answers={len(answers)} "
          f"true={sum(v is True for v in answers.values())} "
          f"false={sum(v is False for v in answers.values())} "
          f"undecidable={sum(v is None for v in answers.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
