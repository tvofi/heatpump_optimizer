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

THE UNIT, read off production's AST, never off a list:

  M  ``import homeassistant.x.y [as z]``    -> the module exists at the floor
  I  ``from homeassistant.x import n``      -> n is bound at module scope of x, or
                                               x.n is a module
  A  ``z.n`` where z names a Home Assistant module -> n is bound in that module
  C  ``C.n`` where C was imported from Home Assistant and is a class defined in
     its module whose base chain stays in that module or ends in a builtin or
     enum base -> n is a member (the v6.3.1 shape)

Guarded, and not checked: a node inside the body of a ``try`` whose handlers
catch ImportError, ModuleNotFoundError or AttributeError, or under
``if TYPE_CHECKING:``. ``except Exception`` is not a guard here, the fail-safe
direction. Typing-only, and not checked: an annotation in a module with
``from __future__ import annotations``, which is never evaluated.

FAIL-CLOSED. The snapshot holds one recorded answer per question, and a question
it does not hold is UNRECORDED, which fails: a new import or a new name cannot
go green by being unknown. Re-record (needs ``gh`` and the network):
``python3 tests/ha_floor.py record``. The snapshot is never edited by hand; the
nightly floor container answers every recorded question again with Home
Assistant itself (``verify``), so a wrong answer reddens within a night.

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

#: Planted trees: the snapshot records the questions of the ``True`` ones, so a
#: planted defect reads MISSING rather than UNRECORDED, and the gate asserts
#: each verdict (tests/entities.py, the P11 floor null controls). ``False``
#: ones are never recorded, so their import must read UNRECORDED.
FLOOR_CONTROLS = {
    # #1869's shape: the name entered 2026.3.
    "plant_import.py": (True, "from homeassistant.helpers.storage import "
                              "UnsupportedStorageVersionError\n"),
    # The same name through a module alias (arm A).
    "plant_alias.py": (True, "from homeassistant.helpers import storage as s\n"
                             "s.UnsupportedStorageVersionError\n"),
    # v6.3.1's shape (arm C): the stub had the member, the floor never did.
    "plant_member.py": (True, "from homeassistant.const import Platform\n"
                              "Platform.DIAGNOSTICS\n"),
    # Guarded twice over, and typing-only: all three are legitimate.
    "plant_guarded.py": (True, "try:\n    from homeassistant.helpers.storage import "
                               "UnsupportedStorageVersionError\n"
                               "except ImportError:\n    pass\n"),
    "plant_typing.py": (True, "from __future__ import annotations\n"
                              "from typing import TYPE_CHECKING\n"
                              "from homeassistant.helpers import storage as s\n"
                              "if TYPE_CHECKING:\n    from homeassistant.helpers.storage "
                              "import UnsupportedStorageVersionError\n"
                              "def f(x: s.UnsupportedStorageVersionError) -> None:\n"
                              "    return None\n"),
    # Never recorded, so fail-closed must read it.
    "plant_unrecorded.py": (False, "from homeassistant.helpers.frame import "
                                   "report_usage\n"),
}


def _is_type_checking(test: ast.expr) -> bool:
    return (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
        isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING")


def _guard_body(node: ast.AST) -> list[ast.stmt]:
    """The statements a recognised guard protects, or none."""
    if isinstance(node, ast.Try):
        caught: set[str] = set()
        for handler in node.handlers:
            kinds = handler.type.elts if isinstance(handler.type, ast.Tuple) \
                else [handler.type]
            caught |= {k.id for k in kinds if isinstance(k, ast.Name)}
        return node.body if caught & GUARD_EXC else []
    if isinstance(node, ast.If) and _is_type_checking(node.test):
        return node.body
    return []


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


def floor_reach(trees: dict[str, ast.Module],
                walks: dict[str, list[ast.AST]] | None = None,
                ) -> dict[tuple[str, str, str], list[str]]:
    """``(kind, target, name) -> sites`` for every unguarded reach.

    kind ``M`` (module import), ``I`` (from-import), ``X`` (an attribute of an
    imported name: arm A or C, decided by the snapshot's ``module:`` answer).
    For ``X`` the target is ``"<module>|<imported name or ''>"``: an empty
    imported name means the alias IS the module (``import a.b as z``).
    ``walks`` is ``ast.walk`` of each tree, already listed (tests/entities.py
    has it for P6); one pass over it collects everything the arms read.
    """
    out: dict[tuple[str, str, str], list[str]] = {}
    for fname, tree in sorted(trees.items()):
        evaluated = not any(isinstance(x, ast.ImportFrom) and x.module == "__future__"
                       and any(a.name == "annotations" for a in x.names)
                       for x in tree.body)
        # Per file, always: see the module docstring.
        safe: set[int] = set()
        typing_only: set[int] = set()
        imports: list[ast.Import | ast.ImportFrom] = []
        attributes: list[ast.Attribute] = []
        for node in (walks[fname] if walks is not None else ast.walk(tree)):
            for stmt in _guard_body(node):
                safe.update(id(x) for x in ast.walk(stmt))
            if not evaluated:
                for ann in _annotations(node):
                    typing_only.update(id(x) for x in ast.walk(ann))
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)
            elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
                    and isinstance(node.ctx, ast.Load):
                attributes.append(node)
        alias: dict[str, tuple[str, str]] = {}
        for node in imports:
            site = f"{fname}:{node.lineno}"
            if isinstance(node, ast.ImportFrom):
                if node.level or not node.module \
                        or node.module.split(".")[0] != "homeassistant":
                    continue
                for a in node.names:
                    if id(node) not in safe:
                        out.setdefault(("I", node.module, a.name), []).append(site)
                    alias[a.asname or a.name] = (node.module, a.name)
                continue
            for a in node.names:
                if a.name.split(".")[0] != "homeassistant":
                    continue
                if id(node) not in safe:
                    out.setdefault(("M", a.name, ""), []).append(site)
                if a.asname:
                    alias[a.asname] = (a.name, "")
        for node in attributes:
            if node.value.id in alias and id(node) not in safe \
                    and id(node) not in typing_only:
                mod, name = alias[node.value.id]
                out.setdefault(("X", f"{mod}|{name}", node.attr), []).append(
                    f"{fname}:{node.lineno}")
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
        else:
            mod, imported = target.split("|")
            path = f"{mod}.{imported}" if imported else mod
            is_module = ask(f"module:{path}")
            if is_module == "?":
                continue
            if is_module:
                bound = ask(f"name:{path}:{name}")
                if bound == "?":
                    continue
                checked += 1
                if not bound:
                    missing.append(f"{path}.{name} (attribute) at {where}")
                continue
            if not imported:
                continue  # the import itself is M's finding
            member = ask(f"member:{mod}:{imported}.{name}")
            if member == "?":
                continue
            if member is None:
                undecidable.append(f"{mod}.{imported}.{name}")
                continue
            checked += 1
            if not member:
                missing.append(f"{mod}.{imported}.{name} (class member) at {where}")
    return {"checked": checked, "missing": missing,
            "unrecorded": sorted(unrecorded), "undecidable": undecidable}


def floor_load(path: Path = SNAPSHOT) -> dict:
    return json.loads(path.read_text())


def floor_trees(root: Path = PACKAGE) -> dict[str, ast.Module]:
    return {p.name: ast.parse(p.read_text()) for p in sorted(root.glob("*.py"))}


def floor_control_trees(recorded_only: bool = False) -> dict[str, ast.Module]:
    return {name: ast.parse(src) for name, (rec, src) in FLOOR_CONTROLS.items()
            if rec or not recorded_only}


# --- recording: from upstream source at the tag, never by hand -------------

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
        raise RecordError("record parses upstream source: Python 3.12+ is needed")
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
        return 1 if (r["missing"] or r["unrecorded"]) else 0
    if args.cmd == "verify":
        return verify(args.image)
    if args.cmd == "verify-inside":
        return verify_inside(args.snapshot)
    tag = args.tag or json.loads((REPO / "hacs.json").read_text())["homeassistant"]
    trees = {**floor_trees(), **{f"control/{k}": v
                                 for k, v in floor_control_trees(recorded_only=True).items()}}
    for i, extra in enumerate(args.trees):
        trees.update({f"extra{i}/{k}": v for k, v in floor_trees(extra).items()})
    data = record(tag, args.cache, trees)
    args.out.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
    answers = data["answers"]
    print(f"RECORDED tag={tag} answers={len(answers)} "
          f"true={sum(v is True for v in answers.values())} "
          f"false={sum(v is False for v in answers.values())} "
          f"undecidable={sum(v is None for v in answers.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
