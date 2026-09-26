"""P6 barrier arms (prototype). Every arm derives its universe from production.

K  payload keys: a literal key read off ``coordinator.data`` that no production
   line writes as a key.
G  probe names: ``getattr``/``hasattr`` on a literal no production code defines.
E  flow error codes: a literal error code a flow can return that its flow's
   ``error`` table lacks, in any shipped catalogue.
P  offered values: a preset/fan/swing mode an entity offers that is neither one
   of Home Assistant's own nor translated and iconed where the frontend looks.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

#: Names Home Assistant (or the stdlib) defines on the objects these probes
#: read. Upstream-produced, so not this class. Each entry is a deliberate
#: classification; an entry nothing probes any more is refused (stale).
P6_UPSTREAM_PROBES = {
    "async_update_entry", "_get_reauth_entry", "cur_step", "async_on_unload",
    "async_start_reauth", "last_update_success", "async_items",
    "register_static_path", "async_update_item", "last_updated", "last_changed",
    "last_reported", "isoformat", "temperature_unit",
}
#: Home Assistant's own climate presets (climate/const.py PRESET_*): the
#: climate component translates and icons these itself.
P6_HA_PRESETS = {"none", "eco", "away", "boost", "comfort", "home", "sleep", "activity"}
#: Modules whose own dict literals are the payload's CONSUMERS' output (an
#: attribute dict naming a key is not a producer of ``coordinator.data``).
P6_CONSUMER_MODULES = {
    "sensor.py", "binary_sensor.py", "climate.py", "switch.py", "button.py",
    "datetime.py", "number.py", "select.py", "diagnostics.py", "entity.py",
}


_TREES: dict = {}


def _parse(pkg: Path):
    """One parse per package per run: every arm walks the same trees."""
    if pkg not in _TREES:
        _TREES[pkg] = {p.name: ast.parse(p.read_text()) for p in sorted(pkg.glob("*.py"))}
    return _TREES[pkg]


_WALKS: dict = {}


def _nodes(tree):
    """``ast.walk`` once per tree; four arms read the same node list."""
    key = id(tree)
    if key not in _WALKS:
        _WALKS[key] = list(ast.walk(tree))
    return _WALKS[key]


def _str_consts(trees):
    """Module-level ``NAME = "text"`` across the package, by bare name."""
    out = {}
    for tree in trees.values():
        for node in tree.body:
            if (
                isinstance(node, ast.Assign)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        out.setdefault(target.id, node.value.value)
    return out


def _lit(node, consts):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name) and node.id in consts:
        return consts[node.id]
    if isinstance(node, ast.Attribute) and node.attr in consts:
        return consts[node.attr]
    return None


# --------------------------------------------------------------------- arm K
def _is_data_expr(node, aliases, accessors):
    if isinstance(node, ast.BoolOp):
        return any(_is_data_expr(v, aliases, accessors) for v in node.values)
    if isinstance(node, ast.Attribute) and node.attr == "data":
        base = node.value
        return (isinstance(base, ast.Attribute) and base.attr == "coordinator") or (
            isinstance(base, ast.Name) and base.id in ("coordinator", "coord")
        )
    if isinstance(node, ast.Name):
        return node.id in aliases
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        return node.func.attr in accessors and not node.args
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return node.value.id == "self" and node.attr in accessors
    return False


def arm_k(pkg: Path):
    trees = _parse(pkg)
    consts = _str_consts(trees)
    produced = set()
    for name, tree in trees.items():
        if name in P6_CONSUMER_MODULES:
            continue
        for n in _nodes(tree):
            if isinstance(n, ast.Dict):
                produced.update(k for k in (_lit(x, consts) for x in n.keys if x) if k)
            elif isinstance(n, ast.Subscript) and isinstance(n.ctx, ast.Store):
                k = _lit(n.slice, consts)
                if k:
                    produced.add(k)
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "dict":
                produced.update(kw.arg for kw in n.keywords if kw.arg)
            elif (
                isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute)
                and n.func.attr in ("setdefault", "update")
            ):
                if n.func.attr == "setdefault" and n.args:
                    k = _lit(n.args[0], consts)
                    if k:
                        produced.add(k)
                produced.update(kw.arg for kw in n.keywords if kw.arg)
    reads, seams = [], []
    for name, tree in trees.items():
        if name not in P6_CONSUMER_MODULES and name != "__init__.py":
            continue
        accessors = set()
        for fn in _nodes(tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                rets = [r.value for r in ast.walk(fn) if isinstance(r, ast.Return) and r.value]
                if rets and all(_is_data_expr(r, set(), set()) for r in rets):
                    accessors.add(fn.name)
        for fn in _nodes(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            aliases = set()
            for n in ast.walk(fn):
                if isinstance(n, ast.Assign) and _is_data_expr(n.value, aliases, accessors):
                    aliases.update(t.id for t in n.targets if isinstance(t, ast.Name))
            for n in ast.walk(fn):
                key = None
                if (
                    isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute)
                    and n.func.attr == "get"
                    and n.args
                    and _is_data_expr(n.func.value, aliases, accessors)
                ):
                    key = _lit(n.args[0], consts)
                elif (
                    isinstance(n, ast.Subscript)
                    and isinstance(n.ctx, ast.Load)
                    and _is_data_expr(n.value, aliases, accessors)
                ):
                    key = _lit(n.slice, consts)
                if key:
                    reads.append((name, n.lineno, key))
                    if key not in produced:
                        seams.append(f"{name}:{n.lineno} {key}")
    return {"reads": len(reads), "produced": len(produced), "seams": sorted(set(seams))}


# --------------------------------------------------------------------- arm G
def arm_g(pkg: Path):
    trees = _parse(pkg)
    defined = set()
    for tree in trees.values():
        for n in _nodes(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                defined.add(n.name)
            elif isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store):
                defined.add(n.attr)
            elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                defined.add(n.id)
            elif isinstance(n, ast.keyword) and n.arg:
                defined.add(n.arg)
            elif isinstance(n, ast.arg):
                defined.add(n.arg)
            elif (
                isinstance(n, ast.Call)
                and isinstance(n.func, ast.Name)
                and n.func.id == "setattr"
                and len(n.args) >= 2
                and isinstance(n.args[1], ast.Constant)
            ):
                defined.add(n.args[1].value)
    probes, seams, upstream_used = 0, [], set()
    for name, tree in trees.items():
        for n in _nodes(tree):
            if (
                isinstance(n, ast.Call)
                and isinstance(n.func, ast.Name)
                and n.func.id in ("getattr", "hasattr")
                and len(n.args) >= 2
                and isinstance(n.args[1], ast.Constant)
                and isinstance(n.args[1].value, str)
            ):
                probes += 1
                attr = n.args[1].value
                if attr in P6_UPSTREAM_PROBES:
                    upstream_used.add(attr)
                elif attr not in defined:
                    seams.append(f"{name}:{n.lineno} {attr}")
    return {
        "probes": probes,
        "seams": sorted(seams),
        "stale_upstream": sorted(P6_UPSTREAM_PROBES - upstream_used),
    }


# --------------------------------------------------------------------- arm E
def _flow_of(stack):
    for cls in reversed(stack):
        if "OptionsFlow" in cls:
            return ("options",)
        if "ConfigFlow" in cls:
            return ("config",)
    return ("config", "options")


def arm_e(pkg: Path, catalogues):
    """Error codes a flow can return, from production, against its flow's table.

    A code is owed by the flow that can return it: a literal inside a flow
    class belongs to that flow; one inside a module-level helper (or a
    validator's ``return``) belongs to every flow that calls the helper,
    transitively. A helper nothing calls is owed by both, conservatively.
    """
    trees = _parse(pkg)
    consts = _str_consts(trees)
    tree = trees["config_flow.py"]
    helpers = {}   # function name -> list of (code, line) it can yield
    callers = {}   # function name -> set of flows or helper names calling it

    def owner_of(stack):
        for kind, name in reversed(stack):
            if kind == "class" and "OptionsFlow" in name:
                return ("flow", "options")
            if kind == "class" and "ConfigFlow" in name:
                return ("flow", "config")
        for kind, name in reversed(stack):
            if kind == "def":
                return ("helper", name)
        return ("helper", "<module>")

    def codes_of(node):
        out = []
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if (
                    isinstance(target, ast.Subscript)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "errors"
                ):
                    vals = [node.value]
                    if isinstance(node.value, ast.IfExp):
                        vals = [node.value.body, node.value.orelse]
                    out += [c for c in (_lit(v, consts) for v in vals) if c]
            if any(isinstance(t, ast.Name) and t.id.endswith("problem") for t in node.targets):
                code = _lit(node.value, consts)
                if code:
                    out.append(code)
        if isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and k.value == "base":
                    code = _lit(v, consts)
                    if code:
                        out.append(code)
        return out

    found = []  # (owner, code, line)

    def visit(node, stack):
        if isinstance(node, ast.ClassDef):
            stack = stack + [("class", node.name)]
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            stack = stack + [("def", node.name)]
        owner = owner_of(stack)
        for code in codes_of(node):
            found.append((owner, code, node.lineno))
        if isinstance(node, ast.Call):
            fn = node.func
            called = fn.id if isinstance(fn, ast.Name) else fn.attr if isinstance(fn, ast.Attribute) else None
            if called:
                callers.setdefault(called, set()).add(owner)
        for child in ast.iter_child_nodes(node):
            visit(child, stack)

    visit(tree, [])
    # A validator anywhere in the package whose name ends in "problem" returns
    # the code the caller files under ``errors``.
    for t in trees.values():
        for fn in _nodes(t):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and fn.name.endswith("problem"):
                for r in ast.walk(fn):
                    if isinstance(r, ast.Return) and r.value is not None:
                        code = _lit(r.value, consts)
                        if code:
                            found.append((("helper", fn.name), code, r.lineno))

    def flows_of(owner, seen=()):
        kind, name = owner
        if kind == "flow":
            return {name}
        if name in seen:
            return set()
        outs = set()
        for caller in callers.get(name, ()):
            outs |= flows_of(caller, seen + (name,))
        # config_flow imports some validators under another name; a helper no
        # caller reaches is owed by both flows rather than by neither.
        return outs or {"config", "options"}

    seams = set()
    for owner, code, line in found:
        for flow in sorted(flows_of(owner)):
            for cat_name, cat in catalogues.items():
                if code not in (cat.get(flow) or {}).get("error", {}):
                    seams.add(f"{cat_name}:{flow}.error.{code} ({owner[1]}:{line})")
    return {"codes": len({c for _o, c, _l in found}), "seams": sorted(seams)}


# --------------------------------------------------------------------- arm P
def arm_p(pkg: Path, catalogues, icons):
    trees = _parse(pkg)
    consts = _str_consts(trees)
    offered, seams = 0, []
    attrs = {"_attr_preset_modes": "preset_mode", "_attr_fan_modes": "fan_mode",
             "_attr_swing_modes": "swing_mode"}
    for name, tree in trees.items():
        platform = name[:-3]
        for cls in (n for n in _nodes(tree) if isinstance(n, ast.ClassDef)):
            tkey, lists = None, {}
            for stmt in cls.body:
                if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
                    targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
                    for t in targets:
                        if not isinstance(t, ast.Name):
                            continue
                        if t.id == "_attr_translation_key":
                            tkey = _lit(stmt.value, consts)
                        elif t.id in attrs and isinstance(stmt.value, (ast.List, ast.Tuple)):
                            lists[attrs[t.id]] = [_lit(e, consts) for e in stmt.value.elts]
            for attr, values in lists.items():
                for value in values:
                    offered += 1
                    if value in P6_HA_PRESETS and attr == "preset_mode":
                        continue
                    where = f"entity.{platform}.{tkey}.state_attributes.{attr}.state.{value}"
                    for cat_name, cat in {**catalogues, "icons.json": icons}.items():
                        node = cat.get("entity", {}).get(platform, {}).get(tkey or "", {})
                        node = node.get("state_attributes", {}).get(attr, {}).get("state", {})
                        if value not in node:
                            seams.append(f"{cat_name}:{where} ({cls.name})")
    return {"offered": offered, "seams": sorted(seams)}


# --------------------------------------------------------------------- arm F
def arm_f(pkg: Path, catalogues):
    """Every field the setup pre-fill preview CAN render, labelled where the
    frontend looks. The preview's keys are exactly ``modbus_prefill.infer``'s
    output, so the universe is read off production: the two register tables
    with every register absent (their keys are fixed), plus the named slots.
    A fixture's one resolution is not the universe (#1262 pinned six)."""
    import importlib
    import sys

    sys.path.insert(0, str(pkg.parent))
    try:
        mp = importlib.import_module(f"{pkg.name}.modbus_prefill")
    finally:
        sys.path.pop(0)
    universe = set(mp._hot_water({})) | set(mp._plant({}, {})) | (
        set(mp._NAMED) - {"unit_capacity"}
    )
    seams = []
    for cat_name, cat in catalogues.items():
        for flow, step in (("config", "device_prefill"), ("options", "modbus_prefill")):
            node = ((cat.get(flow) or {}).get("step") or {}).get(step) or {}
            for kind in ("data", "data_description"):
                for key in sorted(universe):
                    if not (node.get(kind) or {}).get(key):
                        seams.append(f"{cat_name}:{flow}.step.{step}.{kind}.{key}")
    return {"universe": len(universe), "seams": seams}


def run_static(pkg: Path):
    catalogues = {
        "strings.json": json.loads((pkg / "strings.json").read_text()),
        "en.json": json.loads((pkg / "translations" / "en.json").read_text()),
        "sv.json": json.loads((pkg / "translations" / "sv.json").read_text()),
    }
    icons = json.loads((pkg / "icons.json").read_text()) if (pkg / "icons.json").exists() else {}
    return {
        "K": arm_k(pkg),
        "G": arm_g(pkg),
        "E": arm_e(pkg, catalogues),
        "P": arm_p(pkg, catalogues, icons),
        "F": arm_f(pkg, catalogues),
    }


if __name__ == "__main__":
    import sys
    import time

    t0 = time.perf_counter()
    res = run_static(Path(sys.argv[1]) / "custom_components" / "heatpump_optimizer")
    wall = time.perf_counter() - t0
    for arm, r in res.items():
        for s in r["seams"]:
            print(f"SEAM {arm} {s}")
        extra = {k: v for k, v in r.items() if k != "seams"}
        print(f"RESULT arm={arm} seams={len(r['seams'])} {extra}")
    print(f"RESULT static_wall_s={wall:.3f}")
