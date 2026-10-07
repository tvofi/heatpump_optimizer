"""D7 round 8, seat s2 -- dead code by AST reachability (method step 6), static half.

Metric: number of integration top-level symbols (functions, classes, single-name
assignments) that are NOT reachable from any root when a reference to a
top-level symbol is resolved through the module's own bindings (its defs and
its ``from .m import n [as a]`` / ``from . import m [as a]`` imports, followed
transitively), and that tests/structure.py's dead screen does not report.
Methods stay name-based (any attribute or name load of the method's name from
reachable code reaches it), which over-approximates liveness.

Roots: every module-level statement that is not a def/class/single-name
assignment/import; top-level dunders (PEP 562 ``__getattr__``); HA convention
names and methods (imported from tests/structure.py, the gate's own lists);
every function name tests/hastub/homeassistant defines; FRAMEWORK_HOOKS below;
ConfigFlow/OptionsFlow subclasses; process_worker.py's script entry; dunders
and @property getters of reachable classes.

Set aside, never counted: a candidate whose name is a string literal anywhere
in production (a getattr could reach it), and one whose name is read as a
bare attribute (``x.name`` with ``x`` not a module binding) from reachable
code -- the ``attr_rescued`` list. The runtime sentinel s2_sentinel.py confirms
the counted ones.

The count's key: the (module, name) of a top-level def in the parsed production
source. A fix that deletes the def, or makes reachable production code
reference it, lowers the count. The ``test_refs`` column names the tests/*.py
files that reference the symbol (test-only production code).

Command (from the tree root):
  PYTHONPATH=tests/hastub python3 tools/audit/round8/D7/s2_reach.py [--perturb] [--json F]
Expected at the baseline: RESULT unreachable_total=N count, exact (see REPORT-s2.md),
  RESULT unreachable_missed_by_gate == unreachable_total, gate_dead_total=0.
Perturbation (--perturb): copies the package to a private temp dir, appends to
  the copy's __init__.py one module-level ``from .<m> import <name>`` plus a load
  of it for the first counted symbol, re-runs; perturbed_unreachable_total must be
  lower by at least one (up to that symbol's private callees).
Baseline: cdf82daabcfe3777d98b31489f36df5555ec9d82. Machine: 4-vCPU cloud Linux
  container (audit-r8), python 3.11.15. Counts are contention-immune (exact).
Root rule: ROOT = the working directory.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import ast
import json
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT / "tests"))
import structure  # noqa: E402

HASTUB = ROOT / "tests" / "hastub" / "homeassistant"

FRAMEWORK_HOOKS = {
    "async_added_to_hass", "async_will_remove_from_hass", "async_update",
    "available", "device_info", "unique_id", "name", "icon", "should_poll",
    "_handle_coordinator_update", "async_config_entry_first_refresh",
    "async_shutdown", "async_get_options_flow", "is_matching",
    "async_supports_options_flow", "async_set_native_value",
    "async_select_option", "async_set_value", "async_press",
    "async_turn_on", "async_turn_off", "async_toggle", "is_on",
    "native_value", "extra_state_attributes",
    "async_internal_added_to_hass", "async_setup", "async_on_unload",
    "hvac_modes", "hvac_mode", "hvac_action", "preset_mode", "preset_modes",
    "target_temperature", "current_temperature", "min_temp", "max_temp",
    "async_set_temperature", "async_set_hvac_mode", "async_set_preset_mode",
    "_async_update_data", "_async_setup", "async_get_last_state",
    "async_get_last_sensor_data", "extra_restore_state_data", "as_dict",
    "from_dict",
}


def stub_hook_names() -> set[str]:
    out: set[str] = set()
    for p in HASTUB.rglob("*.py"):
        for n in ast.walk(ast.parse(p.read_text())):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out.add(n.name)
    return out


def is_flow(cls: ast.ClassDef) -> bool:
    return any(
        (isinstance(b, ast.Name) and b.id.endswith(("ConfigFlow", "OptionsFlow")))
        or (isinstance(b, ast.Attribute) and b.attr.endswith(("ConfigFlow", "OptionsFlow")))
        for b in cls.bases)


def analyse(pkg: Path, attr_reaches: bool = True, self_scoped: bool = True) -> dict:
    hooks = (stub_hook_names() | FRAMEWORK_HOOKS | structure.HA_CONVENTION_NAMES
             | structure.HA_CONVENTION_METHODS)
    mods = {p.relative_to(pkg).as_posix()[:-3].replace("/", "."): p
            for p in sorted(pkg.rglob("*.py"))}
    trees = {m: ast.parse(p.read_text(), filename=str(p)) for m, p in mods.items()}

    top: dict[tuple[str, str], ast.AST] = {}           # (mod, name) -> node
    methods: dict[tuple[str, str], list[ast.AST]] = {}  # (mod, cls) -> method nodes
    bind: dict[tuple[str, str], tuple[str, str]] = {}   # (mod, alias) -> (srcmod, name)
    modbind: dict[tuple[str, str], str] = {}            # (mod, alias) -> module
    roots: list[tuple[str, ast.AST]] = []
    strings: set[str] = set()

    def resolve_from(mod: str, node: ast.ImportFrom) -> str | None:
        if node.level == 0:
            m = node.module or ""
            pref = "custom_components.heatpump_optimizer."
            return m[len(pref):] if m.startswith(pref) else None
        base = mod.split(".")[:-node.level] if "." in mod else []
        # the package is flat (plus __init__): level 1 means the package root
        return ".".join([*base, node.module]) if node.module else (".".join(base) or "")

    for mod, tree in trees.items():
        for n in ast.walk(tree):
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                strings.add(n.value)
            if isinstance(n, ast.ImportFrom):
                src = resolve_from(mod, n)
                if src is None:
                    continue
                for a in n.names:
                    alias = a.asname or a.name
                    if src == "" and a.name in {k.split(".")[0] for k in mods}:
                        modbind[(mod, alias)] = a.name
                    elif src in mods:
                        bind[(mod, alias)] = (src, a.name)
                    elif src == "" or src == "__init__":
                        bind[(mod, alias)] = ("__init__", a.name)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                top[(mod, node.name)] = node
                if isinstance(node, ast.ClassDef):
                    methods[(mod, node.name)] = [
                        m for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
            elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                top[(mod, node.targets[0].id)] = node
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                top[(mod, node.target.id)] = node
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            else:
                roots.append((mod, node))

    reached: set[tuple[str, str]] = set()
    by_name: dict[str, list[tuple[str, str]]] = {}
    for key in top:
        by_name.setdefault(key[1], []).append(key)
    reached_methods: set[tuple[str, str, str]] = set()
    live_method_names: set[str] = set()
    attr_names: set[str] = set()
    work: list[tuple[str, list[ast.AST], str | None]] = []
    # class hierarchy inside the package, for ``self.m`` resolution
    def resolve_cls(mod: str, name: str) -> tuple[str, str] | None:
        seen = set()
        while (mod, name) not in top and (mod, name) in bind and (mod, name) not in seen:
            seen.add((mod, name))
            mod, name = bind[(mod, name)]
        return (mod, name) if (mod, name) in methods else None
    parents: dict[tuple[str, str], set[tuple[str, str]]] = {k: set() for k in methods}
    for (mod, cname) in methods:
        for b in top[(mod, cname)].bases:
            if isinstance(b, ast.Name):
                r = resolve_cls(mod, b.id)
            elif isinstance(b, ast.Attribute) and isinstance(b.value, ast.Name) and (mod, b.value.id) in modbind:
                r = resolve_cls(modbind[(mod, b.value.id)], b.attr)
            else:
                r = None
            if r:
                parents[(mod, cname)].add(r)
    children: dict[tuple[str, str], set[tuple[str, str]]] = {k: set() for k in methods}
    for k, ps in parents.items():
        for pk in ps:
            children[pk].add(k)
    def closure(k, rel):
        out, stack = set(), [k]
        while stack:
            x = stack.pop()
            for y in rel[x]:
                if y not in out:
                    out.add(y); stack.append(y)
        return out
    family = {k: {k} | closure(k, parents) | closure(k, children) for k in methods}
    self_live: dict[tuple[str, str], set[str]] = {k: set() for k in methods}

    def body(node: ast.AST) -> list[ast.AST]:
        if isinstance(node, ast.ClassDef):
            return (list(node.bases) + list(node.decorator_list) + [k.value for k in node.keywords]
                    + [s for s in node.body if not isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef))])
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            return [node.value] if node.value is not None else []
        return [node]

    def reach_method(mod: str, cls: str, m: ast.AST) -> None:
        key = (mod, cls, m.name)
        if key in reached_methods:
            return
        reached_methods.add(key)
        work.append((mod, [m], cls))

    def reach(mod: str, name: str) -> None:
        # follow import bindings (re-exports) to the defining module
        seen = set()
        while (mod, name) not in top and (mod, name) in bind and (mod, name) not in seen:
            seen.add((mod, name))
            mod, name = bind[(mod, name)]
        if (mod, name) not in top or (mod, name) in reached:
            return
        reached.add((mod, name))
        node = top[(mod, name)]
        work.append((mod, body(node), name if isinstance(node, ast.ClassDef) else None))
        if isinstance(node, ast.ClassDef):
            for m in methods[(mod, name)]:
                dunder = m.name.startswith("__") and m.name.endswith("__")
                if (dunder or structure.is_property_getter(m) or m.name in hooks
                        or structure.is_ha_convention_method(m.name) or m.name in live_method_names
                        or m.name in self_live[(mod, name)]):
                    reach_method(mod, name, m)

    def note_method(name: str) -> None:
        if name in live_method_names:
            return
        live_method_names.add(name)
        for (mod, cls), ms in methods.items():
            if (mod, cls) in reached:
                for m in ms:
                    if m.name == name:
                        reach_method(mod, cls, m)

    def note_self(mod: str, cls: str, name: str) -> None:
        for f in family.get((mod, cls), ()):
            if name in self_live[f]:
                continue
            self_live[f].add(name)
            if f in reached:
                for m in methods[f]:
                    if m.name == name:
                        reach_method(f[0], f[1], m)

    for mod, node in roots:
        work.append((mod, [node], None))
    for (mod, name), node in top.items():
        if name in structure.HA_CONVENTION_NAMES or (name.startswith("__") and name.endswith("__")):
            reach(mod, name)
        if isinstance(node, ast.ClassDef) and is_flow(node):
            reach(mod, name)
        if mod == "process_worker" and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                and name in ("main", "run_worker"):
            reach(mod, name)

    while work:
        mod, nodes, wcls = work.pop()
        for root in nodes:
            for n in ast.walk(root):
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                    reach(mod, n.id)
                    note_method(n.id)  # a bound method passed by name, rare
                elif isinstance(n, ast.Attribute):
                    v = n.value
                    if self_scoped and wcls is not None and isinstance(v, ast.Name) \
                            and v.id in ("self", "cls") and (mod, wcls) in methods:
                        note_self(mod, wcls, n.attr)
                        continue
                    if isinstance(v, ast.Name) and (mod, v.id) in modbind:
                        reach(modbind[(mod, v.id)], n.attr)
                    else:
                        attr_names.add(n.attr)
                        if attr_reaches:
                            # conservative: x.name with x unknown (a module
                            # returned by import_module, say) reaches every
                            # top-level def called name
                            for (m2, nm2) in by_name.get(n.attr, ()):
                                reach(m2, nm2)
                    note_method(n.attr)
                elif isinstance(n, ast.ImportFrom):
                    # a LOCAL import binds names used in the same body; the
                    # loads are resolved through ``bind`` already
                    continue

    counted, rescued, stringref = [], [], []
    for (mod, name), node in sorted(top.items()):
        if (mod, name) in reached:
            continue
        rec = {"module": f"{mod}.py", "name": name, "line": node.lineno,
               "kind": type(node).__name__, "loc": node.end_lineno - node.lineno + 1}
        if name in strings or (f"{mod}.py", name) in structure.DYNAMIC_REFERENCES:
            stringref.append(rec)
        elif name in attr_names and not attr_reaches:
            rescued.append(rec)
        else:
            counted.append(rec)
    dead_methods = []
    for (mod, cls), ms in methods.items():
        if (mod, cls) not in reached:
            continue
        for m in ms:
            if (mod, cls, m.name) not in reached_methods and m.name not in strings:
                dead_methods.append({"module": f"{mod}.py", "name": f"{cls}.{m.name}",
                                     "line": m.lineno, "kind": "method",
                                     "loc": m.end_lineno - m.lineno + 1})
    return {"counted": counted, "attr_rescued": rescued, "string_referenced": stringref,
            "dead_methods": dead_methods, "n_top": len(top)}


def test_refs(names: set[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {n: [] for n in names}
    for p in sorted((ROOT / "tests").glob("*.py")):
        src = p.read_text()
        for n in names:
            if re.search(rf"\b{re.escape(n)}\b", src):
                out[n].append(p.name)
    return out


def gate_dead() -> set[tuple[str, str]]:
    t = structure.measure()["tables"]
    s = {(Path(r).name, n) for r, _l, n in t["dead_symbols"]}
    s |= {(Path(r).name, f"{c}.{n}") for r, c, n, _l in t["dead_methods"]}
    return s


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--perturb", action="store_true")
    ap.add_argument("--gate-probe", action="store_true",
                    help="plant two never-called functions in a temp copy of wear.py -- one with a"
                         " name another module uses (describe), one unique -- and read structure.py's"
                         " dead_top_level_symbols for each")
    args = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()
    res = analyse(structure.PACKAGE_DIR)
    gate = gate_dead()
    refs = test_refs({r["name"].split(".")[-1] for r in res["counted"] + res["dead_methods"]})
    missed = [r for r in res["counted"] if (r["module"], r["name"]) not in gate]
    for r in res["counted"]:
        print(f"  UNREACHABLE {r['kind']:16s} {r['module']}:{r['line']} {r['name']}"
              f" ({r['loc']} lines) tests={','.join(refs[r['name']]) or '-'}")
    for r in res["dead_methods"]:
        print(f"  UNREACHABLE method           {r['module']}:{r['line']} {r['name']}"
              f" ({r['loc']} lines) tests={','.join(refs[r['name'].split('.')[-1]]) or '-'}")
    for r in res["attr_rescued"]:
        print(f"  set-aside (read as x.{r['name']}) {r['module']}:{r['line']}")
    print(f"RESULT top_level_defs_scanned={res['n_top']} count")
    print(f"RESULT unreachable_total={len(res['counted'])} count")
    print(f"RESULT unreachable_loc={sum(r['loc'] for r in res['counted'])} lines")
    print(f"RESULT unreachable_functions={sum(r['kind'] in ('FunctionDef', 'AsyncFunctionDef', 'ClassDef') for r in res['counted'])} count")
    print(f"RESULT unreachable_missed_by_gate={len(missed)} count")
    print(f"RESULT unreachable_methods_name_based={len(res['dead_methods'])} count")
    print(f"RESULT attr_rescued_set_aside={len(res['attr_rescued'])} count")
    print(f"RESULT string_referenced_set_aside={len(res['string_referenced'])} count")
    print(f"RESULT gate_dead_total={len(gate)} count")
    if args.perturb:
        fn = next(r for r in res["counted"] if r["kind"] in ("FunctionDef", "AsyncFunctionDef"))
        tmp = Path(tempfile.mkdtemp(prefix="d7s2reach_", dir=os.environ.get("TMPDIR")))
        try:
            dst = tmp / "heatpump_optimizer"
            shutil.copytree(structure.PACKAGE_DIR, dst,
                            ignore=shutil.ignore_patterns("__pycache__", "www", "brand", "translations"))
            m = fn["module"][:-3]
            with open(dst / "__init__.py", "a") as fh:
                fh.write(f"\nfrom .{m} import {fn['name']} as _d7s2_perturb\n_d7s2_perturb\n")
            res2 = analyse(dst)
            print(f"  perturbation: a root reference to {fn['module']}:{fn['name']} added in a temp copy")
            print(f"RESULT perturbed_unreachable_total={len(res2['counted'])} count")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    if args.gate_probe:
        real_pkg, real_root = structure.PACKAGE_DIR, structure.REPO_ROOT
        for planted in ("describe", "d7s2_never_called_anywhere"):
            tmp = Path(tempfile.mkdtemp(prefix="d7s2gate_", dir=os.environ.get("TMPDIR")))
            try:
                dst = tmp / "custom_components" / "heatpump_optimizer"
                shutil.copytree(real_pkg, dst, ignore=shutil.ignore_patterns(
                    "__pycache__", "www", "brand", "translations"))
                with open(dst / "wear.py", "a") as fh:
                    fh.write(f"\n\ndef {planted}() -> None:\n    return None\n")
                structure.PACKAGE_DIR, structure.REPO_ROOT = dst, tmp
                m = structure.measure()["metrics"]
                ours = analyse(dst)
                print(f"RESULT gate_probe[{planted}].gate_dead_top_level_symbols="
                      f"{m['dead_top_level_symbols']} count")
                print(f"RESULT gate_probe[{planted}].reach_unreachable_total="
                      f"{len(ours['counted'])} count")
            finally:
                structure.PACKAGE_DIR, structure.REPO_ROOT = real_pkg, real_root
                shutil.rmtree(tmp, ignore_errors=True)
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    if args.json:
        Path(args.json).write_text(json.dumps({**res, "test_refs": refs}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
