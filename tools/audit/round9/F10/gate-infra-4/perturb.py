"""Arm demonstrations for R9-F10.4: each perturbation, measured by the OLD
structure.py (base 3bd6f122's own) and the NEW one, on the base tree.

usage: perturb.py <tree-root> <old-structure.py|-> <new-structure.py> <seam_map.json for new> [<seam_map.json for old>]
Prints one row per perturbation: the metric deltas each ratchet shows.
"""

import ast
import importlib.util
import json
import shutil
import sys
import tempfile
import textwrap
from pathlib import Path

ROOT = Path(sys.argv[1])
OLD = None if sys.argv[2] == "-" else Path(sys.argv[2])
NEW = Path(sys.argv[3])
NEW_SEAMS = json.loads(Path(sys.argv[4]).read_text())
PKG = "custom_components/heatpump_optimizer"


def measure(struct: Path, seams: dict, edit) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        shutil.copytree(ROOT / PKG, tmp / PKG)
        (tmp / "tests").mkdir()
        shutil.copy(struct, tmp / "tests" / "structure.py")
        seams = json.loads(json.dumps(seams))
        edit(tmp / PKG, seams)
        (tmp / "tests" / "seam_map.json").write_text(json.dumps(seams))
        name = f"st_{abs(hash((str(struct), id(edit))))}"
        spec = importlib.util.spec_from_file_location(
            name, tmp / "tests" / "structure.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.measure()["metrics"]


def edit_text(rel, fn):
    def apply(pkg, _seams):
        p = pkg / rel
        p.write_text(fn(p.read_text()))

    return apply


def chain(*edits):
    def apply(pkg, seams):
        for e in edits:
            e(pkg, seams)

    return apply


def copy_function_to(src_rel, name, dst_rel, new_name):
    """Append a renamed verbatim copy of top-level function ``name`` to dst."""

    def apply(pkg, _seams):
        text = (pkg / src_rel).read_text()
        node = next(
            n
            for n in ast.parse(text).body
            if isinstance(n, ast.FunctionDef) and n.name == name
        )
        lines = text.splitlines()[node.lineno - 1 : node.end_lineno]
        lines[0] = lines[0].replace(f"def {name}(", f"def {new_name}(", 1)
        p = pkg / dst_rel
        p.write_text(p.read_text() + "\n\n" + "\n".join(lines) + "\n")

    return apply


def method_to_helper(pkg, seams):
    """Move one coordinator method's body into ``_probe_helper(self)`` (#1686)."""
    p = pkg / "coordinator.py"
    text = p.read_text()
    tree = ast.parse(text)
    cls = next(
        n
        for n in tree.body
        if isinstance(n, ast.ClassDef) and n.name == "HeatPumpOptimizerCoordinator"
    )

    def ok(m):
        if not isinstance(m, ast.FunctionDef) or m.decorator_list:
            return False
        a = m.args
        if [x.arg for x in a.args] != ["self"] or a.vararg or a.kwarg or a.kwonlyargs:
            return False
        if any(
            isinstance(
                n,
                (
                    ast.Yield,
                    ast.YieldFrom,
                    ast.FunctionDef,
                    ast.Lambda,
                    ast.AsyncFunctionDef,
                    ast.ClassDef,
                ),
            )
            for n in ast.walk(m)
            if n is not m
        ):
            return False
        if any(isinstance(n, ast.Name) and n.id == "super" for n in ast.walk(m)):
            return False
        refs = sum(
            1
            for n in ast.walk(m)
            if isinstance(n, ast.Attribute)
            and isinstance(n.value, ast.Name)
            and n.value.id == "self"
        )
        return (
            refs >= 6 and m.name in seams["seams"] and seams["seams"][m.name] != "core"
        )

    m = next(x for x in cls.body if ok(x))
    lines = text.splitlines()
    body = lines[m.body[0].lineno - 1 : m.end_lineno]
    helper = ["", "", "def _probe_helper(self):"] + [
        ln[4:] if ln.strip() else ln for ln in body
    ]
    lines[m.body[0].lineno - 1 : m.end_lineno] = ["        return _probe_helper(self)"]
    p.write_text("\n".join(lines + helper) + "\n")
    if any(k.startswith("coordinator.") for k in seams["seams"]):
        seams["seams"]["coordinator._probe_helper"] = seams["seams"][m.name]
    print(f"   (moved {m.name}, seam {seams['seams'][m.name]}, into _probe_helper)")


def add_member(rel, cls_name, text_block):
    def apply(pkg, _seams):
        p = pkg / rel
        src = p.read_text()
        node = next(
            n
            for n in ast.walk(ast.parse(src))
            if isinstance(n, ast.ClassDef) and n.name == cls_name
        )
        lines = src.splitlines()
        lines[node.end_lineno : node.end_lineno] = textwrap.indent(
            text_block, "    "
        ).splitlines()
        p.write_text("\n".join(lines) + "\n")

    return apply


def in_function(rel, fn_name, stmt):
    """Insert ``stmt`` as the first statement of top-level or method ``fn_name``."""

    def apply(pkg, _seams):
        p = pkg / rel
        src = p.read_text()
        fn = next(
            n
            for n in ast.walk(ast.parse(src))
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and n.name == fn_name
        )
        lines = src.splitlines()
        first = fn.body[0]
        indent = " " * first.col_offset
        lines[first.lineno - 1 : first.lineno - 1] = [
            indent + s for s in stmt.splitlines()
        ]
        p.write_text("\n".join(lines) + "\n")

    return apply


def rename_param(rel, fn_name, old, new):
    def apply(pkg, _seams):
        p = pkg / rel
        src = p.read_text()
        tree = ast.parse(src)
        fn = next(
            n
            for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and n.name == fn_name
        )
        lines = src.splitlines()
        old_name = old or fn.args.args[0].arg
        print(f"   (renamed {fn_name}'s {old_name} to {new})")
        for i in range(fn.lineno - 1, fn.end_lineno):
            lines[i] = __import__("re").sub(rf"\b{old_name}\b", new, lines[i])
        p.write_text("\n".join(lines) + "\n")

    return apply


def noop(_pkg, _seams):
    pass


PERTURBATIONS = [
    ("null: no edit", noop),
    (
        "#1738a copy a 12+-line function into another module",
        copy_function_to("grid_fee.py", "parse_month_range", "wear.py", "_probe_copy"),
    ),
    (
        "#1738b read a coordinator private from a platform (by role)",
        in_function(
            "sensor.py", "async_setup_entry", "_probe = entry.runtime_data._last_plan"
        ),
    ),
    (
        "#1738b write one: store, and in-place mutation",
        in_function(
            "sensor.py",
            "async_setup_entry",
            "entry.runtime_data._probe_slot = 1\nentry.runtime_data._listeners.append(None)",
        ),
    ),
    (
        "#1738 attribute stored from outside the class",
        in_function(
            "sensor.py", "async_setup_entry", "entry.runtime_data.probe_public = 1"
        ),
    ),
    ("#1686 move a method body into _helper(self)", method_to_helper),
    (
        "D7-s3-02 an unread @property",
        add_member(
            "wear.py",
            "StartCounter",
            "@property\ndef probe_unread(self):\n    return 1\n",
        ),
    ),
    (
        "D7-s3-02 an unread method whose name is also a local",
        chain(
            add_member(
                "wear.py", "StartCounter", "def probe_local(self):\n    return 1\n"
            ),
            in_function("ledger.py", "_prune", "probe_local = 0\nassert probe_local == 0"),
        ),
    ),
    (
        "D7-s3-02 a method reached only from itself",
        add_member(
            "wear.py",
            "StartCounter",
            "def probe_recur(self, n):\n    return self.probe_recur(n - 1)\n",
        ),
    ),
    (
        "#1738 a module-level import cycle",
        chain(
            edit_text("wear.py", lambda s: s + "\nfrom . import ledger  # noqa\n"),
            edit_text("ledger.py", lambda s: s + "\nfrom . import wear  # noqa\n"),
        ),
    ),
    (
        "#1738 a name reached only through import *",
        chain(
            edit_text("const.py", lambda s: s + "\nPROBE_STAR = 1\n"),
            edit_text(
                "wear.py",
                lambda s: s + "\nfrom .const import *  # noqa\nPROBE_STAR  # noqa\n",
            ),
        ),
    ),
    (
        "null: rename a coordinator-holding parameter",
        rename_param("coordinator.py", "_fold_flow_lift", None, "probe_owner"),
    ),
]


def main():
    seams_old = None
    if OLD is not None:
        old_map = Path(sys.argv[5]) if len(sys.argv) > 5 else None
        seams_old = json.loads(old_map.read_text()) if old_map else {"seams": {}}
    if seams_old:
        # The tree is the base: a member the head deleted is still there, so
        # its base seam rides into the new map (current_action, F10.4).
        for name, seam in seams_old["seams"].items():
            NEW_SEAMS["seams"].setdefault(name, seam)
    base_new = measure(NEW, NEW_SEAMS, noop)
    base_old = measure(OLD, seams_old, noop) if OLD else None
    for label, edit in PERTURBATIONS:
        print(f"== {label}")
        for tag, struct, seams, base in (
            ("old", OLD, seams_old, base_old),
            ("new", NEW, NEW_SEAMS, base_new),
        ):
            if struct is None:
                continue
            try:
                got = measure(struct, seams, edit)
            except Exception as err:  # noqa: BLE001
                print(f"   {tag}: ERROR {type(err).__name__}: {err}")
                continue
            moved = {
                k: got[k] - base[k]
                for k in sorted(set(got) & set(base))
                if got[k] != base[k]
            }
            print(f"   {tag}: {moved if moved else 'nothing moves'}")


main()
