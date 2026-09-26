

# ===========================================================================
# P6: every read has a producer (round-9 class barrier)
# ===========================================================================
# Class P6 -- a consumer reads a key or field no producer writes, with a
# silent fallback -- recurred in every audit round but one (bugclasses.json).
# Each fix before this one guarded its own instance with a universe the fixer
# supplied: one sensor's payload reads (#1460, above), one slot shape (#1526),
# one fixture device's preview fields (#1262), six hand-listed error codes,
# 13 in-scope entities (#368, which named the solve seed and scoped it out).
# Every arm here reads its universe off production instead, so a new read,
# code, preset, prefill key or seed field is covered the day it lands.
# Each exemption table is a deliberate classification with its reason, and an
# entry that stops matching anything is refused, so the tables only shrink.
R.section("P6: every read has a producer (round-9 class barrier)")

import dataclasses as _p6_dc

from heatpump_optimizer import modbus_prefill as _p6_modbus_prefill

#: Names Home Assistant or the stdlib defines on the objects these probes
#: read; their producer is upstream, so they are not this class.
P6_UPSTREAM_PROBES = {
    "async_update_entry", "_get_reauth_entry", "cur_step", "async_on_unload",
    "async_start_reauth", "last_update_success", "async_items",
    "register_static_path", "async_update_item", "last_updated", "last_changed",
    "last_reported", "isoformat", "temperature_unit",
}
#: Home Assistant's own climate presets (climate/const.py PRESET_*), which the
#: climate component translates and icons itself.
P6_HA_PRESETS = {"none", "eco", "away", "boost", "comfort", "home", "sleep", "activity"}
#: Modules whose dict literals are the payload's consumers' output: an
#: attribute dict naming a key does not produce ``coordinator.data``.
P6_CONSUMER_MODULES = {
    "sensor.py", "binary_sensor.py", "climate.py", "switch.py", "button.py",
    "datetime.py", "number.py", "select.py", "diagnostics.py", "entity.py",
}
#: Seed fields the flow's own install legitimately leaves at the constructor
#: default across solves, each with the reason. Not a place to park a finding.
P6_SEED_DEFAULTS_DECLARED = {
    "room_temperature": "no indoor thermometer: tvofi's A3(e) ruling (D8-s2-01, F7.3)",
    "upper_floor_temperature": "no indoor thermometer: tvofi's A3(e) ruling (D8-s2-01, F7.3)",
    "lower_floor_temperature": "no indoor thermometer: tvofi's A3(e) ruling (D8-s2-01, F7.3)",
    "buffer_tank_temperature": "the flow's install configures no buffer tank",
    "solar_radiation": "the run's clock is 00:00 UTC in January, where 0 W/m2 is the truth",
}

_P6_TREES = {p.name: ast.parse(p.read_text()) for p in sorted(ROOT.glob("*.py"))}
_P6_WALKS = {name: list(ast.walk(tree)) for name, tree in _P6_TREES.items()}
_P6_CATALOGUES = {
    "strings.json": json.loads((ROOT / "strings.json").read_text()),
    "en.json": json.loads((ROOT / "translations" / "en.json").read_text()),
    "sv.json": json.loads((ROOT / "translations" / "sv.json").read_text()),
}
_P6_ICONS = json.loads((ROOT / "icons.json").read_text())


def _p6_consts():
    """Module-level ``NAME = "text"`` across the package, by bare name."""
    out = {}
    for name, tree in _P6_TREES.items():
        for node in tree.body:
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) \
                    and isinstance(node.value.value, str):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        out.setdefault(target.id, node.value.value)
    return out


_P6_CONSTS = _p6_consts()


def _p6_lit(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return _P6_CONSTS.get(node.id)
    if isinstance(node, ast.Attribute):
        return _P6_CONSTS.get(node.attr)
    return None


# --- arm K: a payload key read off coordinator.data has a producer --------
def _p6_is_data(node, aliases, accessors):
    if isinstance(node, ast.BoolOp):
        return any(_p6_is_data(v, aliases, accessors) for v in node.values)
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


def _p6_arm_k(walks):
    produced = set()
    for name, nodes in walks.items():
        if name in P6_CONSUMER_MODULES:
            continue
        for n in nodes:
            if isinstance(n, ast.Dict):
                produced.update(k for k in map(_p6_lit, filter(None, n.keys)) if k)
            elif isinstance(n, ast.Subscript) and isinstance(n.ctx, ast.Store):
                produced.add(_p6_lit(n.slice))
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "dict":
                produced.update(kw.arg for kw in n.keywords if kw.arg)
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                    and n.func.attr in ("setdefault", "update"):
                if n.func.attr == "setdefault" and n.args:
                    produced.add(_p6_lit(n.args[0]))
                produced.update(kw.arg for kw in n.keywords if kw.arg)
    reads, seams = 0, set()
    for name, nodes in walks.items():
        if name not in P6_CONSUMER_MODULES and name != "__init__.py":
            continue
        fns = [n for n in nodes if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        accessors = {
            fn.name for fn in fns
            if (rets := [r.value for r in ast.walk(fn) if isinstance(r, ast.Return) and r.value])
            and all(_p6_is_data(r, set(), set()) for r in rets)
        }
        for fn in fns:
            body = list(ast.walk(fn))
            aliases = set()
            for n in body:
                if isinstance(n, ast.Assign) and _p6_is_data(n.value, aliases, accessors):
                    aliases.update(t.id for t in n.targets if isinstance(t, ast.Name))
            for n in body:
                key = None
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                        and n.func.attr == "get" and n.args \
                        and _p6_is_data(n.func.value, aliases, accessors):
                    key = _p6_lit(n.args[0])
                elif isinstance(n, ast.Subscript) and isinstance(n.ctx, ast.Load) \
                        and _p6_is_data(n.value, aliases, accessors):
                    key = _p6_lit(n.slice)
                if key:
                    reads += 1
                    if key not in produced:
                        seams.add(f"{name}:{n.lineno} {key}")
    return reads, sorted(seams)


# --- arm G: a getattr/hasattr probe names something production defines ---
def _p6_arm_g(walks):
    defined = set()
    for nodes in walks.values():
        for n in nodes:
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
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                    and n.func.id == "setattr" and len(n.args) >= 2 \
                    and isinstance(n.args[1], ast.Constant):
                defined.add(n.args[1].value)
    probes, seams, upstream_used = 0, [], set()
    for name, nodes in walks.items():
        for n in nodes:
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                    and n.func.id in ("getattr", "hasattr") and len(n.args) >= 2 \
                    and isinstance(n.args[1], ast.Constant) and isinstance(n.args[1].value, str):
                probes += 1
                attr = n.args[1].value
                if attr in P6_UPSTREAM_PROBES:
                    upstream_used.add(attr)
                elif attr not in defined:
                    seams.append(f"{name}:{n.lineno} {attr}")
    return probes, sorted(seams), sorted(P6_UPSTREAM_PROBES - upstream_used)


# --- arm E: an error code a flow can return is in its flow's error table ---
def _p6_arm_e(tree, walks, catalogues):
    """A code inside a flow class is owed by that flow; one in a module-level
    helper by every flow that calls it, transitively; a validator's return
    (a function named ``*problem``) likewise. Unreached: both flows."""
    callers, found = {}, []

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
                if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name) \
                        and target.value.id == "errors":
                    vals = [node.value.body, node.value.orelse] \
                        if isinstance(node.value, ast.IfExp) else [node.value]
                    out += [c for c in map(_p6_lit, vals) if c]
            if any(isinstance(t, ast.Name) and t.id.endswith("problem") for t in node.targets):
                out += [c for c in [_p6_lit(node.value)] if c]
        if isinstance(node, ast.Dict):
            out += [
                c for k, v in zip(node.keys, node.values)
                if isinstance(k, ast.Constant) and k.value == "base" and (c := _p6_lit(v))
            ]
        return out

    def visit(node, stack):
        if isinstance(node, ast.ClassDef):
            stack = stack + [("class", node.name)]
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            stack = stack + [("def", node.name)]
        owner = owner_of(stack)
        found.extend((owner, code, node.lineno) for code in codes_of(node))
        if isinstance(node, ast.Call):
            fn = node.func
            called = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", None)
            if called:
                callers.setdefault(called, set()).add(owner)
        for child in ast.iter_child_nodes(node):
            visit(child, stack)

    visit(tree, [])
    for nodes in walks.values():
        for fn in nodes:
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and fn.name.endswith("problem"):
                found.extend(
                    (("helper", fn.name), code, r.lineno)
                    for r in ast.walk(fn)
                    if isinstance(r, ast.Return) and r.value is not None
                    and (code := _p6_lit(r.value))
                )

    def flows_of(owner, seen=()):
        kind, name = owner
        if kind == "flow":
            return {name}
        if name in seen:
            return set()
        outs = set()
        for caller in callers.get(name, ()):
            outs |= flows_of(caller, seen + (name,))
        return outs or {"config", "options"}

    seams = {
        f"{cat_name}:{flow}.error.{code} ({owner[1]}:{line})"
        for owner, code, line in found
        for flow in flows_of(owner)
        for cat_name, cat in catalogues.items()
        if code not in (cat.get(flow) or {}).get("error", {})
    }
    owed = {(flow, code) for owner, code, _l in found for flow in flows_of(owner)}
    return len({c for _o, c, _l in found}), sorted(seams), owed


# --- arm P: a mode an entity offers is Home Assistant's or translated -----
def _p6_arm_p(trees, catalogues, icons):
    attrs = {"_attr_preset_modes": "preset_mode", "_attr_fan_modes": "fan_mode",
             "_attr_swing_modes": "swing_mode"}
    offered, seams = 0, []
    for name, tree in trees.items():
        platform = name[:-3]
        for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
            tkey, lists = None, {}
            for stmt in cls.body:
                if not isinstance(stmt, (ast.Assign, ast.AnnAssign)):
                    continue
                for t in stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]:
                    if not isinstance(t, ast.Name):
                        continue
                    if t.id == "_attr_translation_key":
                        tkey = _p6_lit(stmt.value)
                    elif t.id in attrs and isinstance(stmt.value, (ast.List, ast.Tuple)):
                        lists[attrs[t.id]] = [_p6_lit(e) for e in stmt.value.elts]
            for attr, values in lists.items():
                for value in values:
                    offered += 1
                    if attr == "preset_mode" and value in P6_HA_PRESETS:
                        continue
                    for cat_name, cat in {**catalogues, "icons.json": icons}.items():
                        node = ((cat.get("entity") or {}).get(platform) or {}).get(tkey or "") or {}
                        node = ((node.get("state_attributes") or {}).get(attr) or {}).get("state") or {}
                        if value not in node:
                            seams.append(
                                f"{cat_name}:entity.{platform}.{tkey}.state_attributes."
                                f"{attr}.state.{value} ({cls.name})"
                            )
    return offered, sorted(seams)


# --- arm F: every field the setup pre-fill preview can render is labelled -
def _p6_prefill_universe():
    """The preview's keys are exactly ``modbus_prefill.infer``'s output: the two
    register tables' fixed keys (read with every register absent) plus the
    named slots. One fixture's resolution is not the universe (#1262)."""
    mp = _p6_modbus_prefill
    return set(mp._hot_water({})) | set(mp._plant({}, {})) | (set(mp._NAMED) - {"unit_capacity"})


def _p6_arm_f(catalogues, universe):
    seams = []
    for cat_name, cat in catalogues.items():
        for flow, step in (("config", "device_prefill"), ("options", "modbus_prefill")):
            node = ((cat.get(flow) or {}).get("step") or {}).get(step) or {}
            for kind in ("data", "data_description"):
                seams += [
                    f"{cat_name}:{flow}.step.{step}.{kind}.{key}"
                    for key in sorted(universe)
                    if not (node.get(kind) or {}).get(key)
                ]
    return seams


# --- arm S: a solve seed is a producer's, not the constructor's -----------
# D12-s1-01's shape. The flow's own install (no thermometer, hot water on),
# the clock moving one plan step per cycle, a 6 h horizon because only the
# seed is read: a numeric field equal to its constructor default at EVERY
# solve had no producer on this install.
def _p6_seed_log(cycles=2):
    log = []
    _hass, _entry, coord = _d801_coordinator(_FLOW_CONFIG)
    coord._opt_config.horizon_hours = 6.0
    snap = coord._solve_snapshot

    def recording_snapshot():
        state, optimizer = snap()
        log.append({f.name: getattr(state, f.name) for f in _p6_dc.fields(state)})
        return state, optimizer

    coord._solve_snapshot = recording_snapshot

    async def run():
        for cycle in range(cycles):
            dt_util.freeze(_D801_START + timedelta(minutes=15 * cycle))
            await coord._update_current_state()
            await coord.async_run_optimization()

    try:
        asyncio.run(run())
    finally:
        dt_util.freeze(None)
    return log


def _p6_seed_seams(log):
    defaults = ThermalState()
    return [
        f.name
        for f in _p6_dc.fields(ThermalState)
        if isinstance(d := getattr(defaults, f.name), (int, float))
        and not isinstance(d, bool)  # None is an honest "unknown"; flags seed nothing
        and len(log) >= 2
        and all(seed[f.name] == d for seed in log)
    ]


_p6_k_reads, _p6_k = _p6_arm_k(_P6_WALKS)
_p6_g_probes, _p6_g, _p6_g_stale = _p6_arm_g(_P6_WALKS)
_p6_e_codes, _p6_e, _p6_e_owed = _p6_arm_e(_P6_TREES["config_flow.py"], _P6_WALKS, _P6_CATALOGUES)
_p6_p_offered, _p6_p = _p6_arm_p(_P6_TREES, _P6_CATALOGUES, _P6_ICONS)
_p6_universe = _p6_prefill_universe()
_p6_f = _p6_arm_f(_P6_CATALOGUES, _p6_universe)
_p6_seeds = _p6_seed_log()
_p6_s = _p6_seed_seams(_p6_seeds)
_p6_s_open = sorted(set(_p6_s) - set(P6_SEED_DEFAULTS_DECLARED))
_p6_s_stale = sorted(set(P6_SEED_DEFAULTS_DECLARED) - set(_p6_s))

R.check(
    "every coordinator.data key a platform reads is one production writes (P6 K)",
    _p6_k_reads > 0 and not _p6_k,
    f"{len(_p6_k)} of {_p6_k_reads} reads have no producer: {_p6_k[:6]}",
)
R.check(
    "every getattr/hasattr probe names what production or upstream defines (P6 G)",
    _p6_g_probes > 0 and not _p6_g and not _p6_g_stale,
    f"test-double-only: {_p6_g}; upstream entries nothing probes: {_p6_g_stale}",
)
R.check(
    "every error code a flow can return is in that flow's error table, in every "
    "catalogue (P6 E)",
    _p6_e_codes > 0 and not _p6_e,
    f"{len(_p6_e)} raw: {_p6_e[:6]}",
)
R.check(
    "every non-standard mode an entity offers is translated and iconed (P6 P)",
    _p6_p_offered > 0 and not _p6_p,
    f"{len(_p6_p)} raw: {_p6_p[:6]}",
)
R.check(
    "every field the pre-fill preview can render has a label and a description, "
    "in both flows and every catalogue (P6 F)",
    len(_p6_universe) > 0 and not _p6_f,
    f"{len(_p6_f)} of {len(_p6_universe)} keys x 2 flows x 2 kinds x 3 catalogues "
    f"render raw: {_p6_f[:6]}",
)
R.check(
    "no solve seed stays at its constructor default unless declared, and no "
    "declaration is stale (P6 S)",
    len(_p6_seeds) >= 2 and not _p6_s_open and not _p6_s_stale,
    f"solves={len(_p6_seeds)} undeclared={_p6_s_open} stale={_p6_s_stale}",
)

# NULL CONTROLS: each arm, handed its own defect, must see it. A check that
# cannot fail pins nothing (the repository's most repeated detector defect).
_p6_null_k = dict(_P6_WALKS)
_p6_null_k["sensor.py"] = _P6_WALKS["sensor.py"] + list(ast.walk(ast.parse(
    "def _p6_probe(self):\n    return self.coordinator.data.get('p6_no_producer_writes_this')\n"
)))
_p6_null_g = {"sensor.py": list(ast.walk(ast.parse("getattr(c, 'p6_only_a_double_has_this', None)")))}
_p6_null_cat = json.loads(json.dumps(_P6_CATALOGUES))
_p6_null_code = sorted(
    code for flow, code in _p6_e_owed
    if flow == "config" and code in _p6_null_cat["en.json"]["config"]["error"]
)[0]
del _p6_null_cat["en.json"]["config"]["error"][_p6_null_code]
_p6_null_key = sorted(_p6_universe)[0]
for _p6_step in _p6_null_cat["sv.json"]["options"]["step"].values():
    (_p6_step.get("data") or {}).pop(_p6_null_key, None)
_p6_null_p = {"climate.py": ast.parse(
    "class C:\n    _attr_translation_key = 'p6'\n    _attr_preset_modes = ['p6_custom']\n"
)}
_p6_default_seed = {f.name: getattr(ThermalState(), f.name) for f in _p6_dc.fields(ThermalState)}
R.check(
    "and each P6 arm fires on its own planted defect (null controls)",
    any("p6_no_producer_writes_this" in s for s in _p6_arm_k(_p6_null_k)[1])
    and any("p6_only_a_double_has_this" in s for s in _p6_arm_g(_p6_null_g)[1])
    and any(_p6_null_code in s for s in _p6_arm_e(
        _P6_TREES["config_flow.py"], _P6_WALKS, _p6_null_cat)[1])
    and any(_p6_null_key in s for s in _p6_arm_f(_p6_null_cat, _p6_universe))
    and any("p6_custom" in s for s in _p6_arm_p(_p6_null_p, _P6_CATALOGUES, _P6_ICONS)[1])
    and "dhw_temperature" in _p6_seed_seams([_p6_default_seed, _p6_default_seed])
    and "dhw_temperature" not in _p6_seed_seams(
        [_p6_default_seed, {**_p6_default_seed, "dhw_temperature": 54.9}]
    ),
    f"code={_p6_null_code} key={_p6_null_key}",
)
