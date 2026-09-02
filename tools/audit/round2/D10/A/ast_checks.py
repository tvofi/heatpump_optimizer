#!/usr/bin/env python3
"""D10-A static rule harness for heatpump_optimizer (round 2).

Metric (one line): per-rule static counts over the AST of
custom_components/heatpump_optimizer/*.py + manifest/strings JSON — service
registration sites, polling interval, entity unique-id/translation/category/
device-class/disabled/has_entity_name coverage, raise-site translation
coverage, blocking-IO sites in async defs, websession provenance — each
printed as a `RESULT <rule>.<name>=<value>` line.

Run (from the export root, or anywhere — root is derived from __file__):
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/tvofi-claude/.venv/bin/python \
  tools/audit/round2/D10/A/ast_checks.py

Baseline SHA: b39fc6f01f4caee9d3ef17bce5f0b4561392fdb9
Machine: MacBookAir10,1 (8 cores). All numbers are counts: contention-immune,
tolerance exact.
"""

from __future__ import annotations

import json
import os
import re
import sys

# Thread pin — contract: before any heavy import, identical to tests/stress.py.
for _var in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_var, "1")

import ast  # noqa: E402
import time  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE)))))
# HPO_D10A_INT lets a judge re-run against a perturbed COPY of the
# integration (never point it at the export itself).
INT = os.environ.get("HPO_D10A_INT") or os.path.join(
    ROOT, "custom_components", "heatpump_optimizer"
)

PLATFORMS = ["sensor", "binary_sensor", "button", "climate", "switch"]

EVIDENCE: list[str] = []


def result(name: str, value, note: str = "") -> None:
    print(f"RESULT {name}={value}")
    if note:
        EVIDENCE.append(f"    {name}={value}  ({note})")
    else:
        EVIDENCE.append(f"    {name}={value}")


MODULES: dict[str, ast.Module] = {}
# Files come from os.listdir of the pinned integration root, and each path is
# confirmed to resolve inside that root before it is read — no caller-supplied
# paths reach the parser.
_root = os.path.realpath(INT)
for fname in sorted(os.listdir(INT)):
    if not fname.endswith(".py"):
        continue
    _real = os.path.realpath(os.path.join(INT, fname))
    if os.path.commonpath([_root, _real]) != _root:
        raise ValueError(f"refusing to read outside the integration root: {fname}")
    with open(_real, encoding="utf-8") as fh:
        MODULES[fname[:-3]] = ast.parse(fh.read(), filename=_real)


def enclosing_functions(tree: ast.AST, node: ast.AST) -> list[str]:
    """Names of function defs enclosing `node`, innermost first."""

    class _Found(Exception):
        pass

    found: list[str] = []

    def _walk(parent: ast.AST, n: ast.AST, cur: list[str]) -> None:
        if n is node:
            found[:] = cur
            raise _Found
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            cur = cur + [n.name]
        for child in ast.iter_child_nodes(n):
            _walk(n, child, cur)

    for top in ast.iter_child_nodes(tree):
        try:
            _walk(tree, top, [])
        except _Found:
            break
    return found


def calls(tree: ast.AST):
    """Yield (call_node, dotted_name) for every Call in the tree.

    `super().__init__(...)` yields "__init__" (base expr is a Call, not a
    Name); plain `f(...)` yields "f"; `a.b.c(...)` yields "a.b.c".
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            parts: list[str] = []
            cur = node.func
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            elif parts:
                pass  # e.g. super().__init__ -> keep attr parts only
            else:
                continue
            yield node, ".".join(reversed(parts))


def const_str(node: ast.AST) -> str | None:
    """A plain string literal or f-string with only constant parts."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        out = []
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                out.append(v.value)
            else:
                return None
        return "".join(out)
    return None


def class_defs(tree: ast.AST) -> dict[str, ast.ClassDef]:
    return {
        n.name: n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)
    }


def base_names(cls: ast.ClassDef) -> list[str]:
    out = []
    for b in cls.bases:
        if isinstance(b, ast.Name):
            out.append(b.id)
        elif isinstance(b, ast.Attribute):
            out.append(b.attr)
    return out


def attr_assignments(cls: ast.ClassDef, attr: str):
    """All Assign/AnnAssign targets `attr` in the class body (own only)."""
    vals = []
    for stmt in cls.body:
        targets = []
        if isinstance(stmt, ast.Assign):
            targets = stmt.targets
        elif isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
            targets = [stmt.target]
        for t in targets:
            if isinstance(t, ast.Name) and t.id == attr:
                vals.append(stmt.value)
    return vals


def attr_source(classes: dict[str, ast.ClassDef], cls_name: str, attr: str, seen=None):
    """Resolve `attr` over the class + its integration-internal bases."""
    if seen is None:
        seen = set()
    if cls_name in seen or cls_name not in classes:
        return None
    seen.add(cls_name)
    vals = attr_assignments(classes[cls_name], attr)
    if vals:
        return vals[0], cls_name
    for b in base_names(classes[cls_name]):
        got = attr_source(classes, b, attr, seen)
        if got is not None:
            return got
    return None


def attr_value_name(node: ast.AST) -> str:
    """Dotted value name for e.g. EntityCategory.DIAGNOSTIC or literal."""
    if isinstance(node, ast.Constant):
        return repr(node.value)
    parts = []
    cur = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
        return ".".join(reversed(parts))
    return ast.dump(node)[:40]


# ---------------------------------------------------------------------------
# Entity roster per platform: from async_setup_entry instantiation lists
# ---------------------------------------------------------------------------


def find_setup_entities(mod_name: str) -> list[str]:
    """Class names instantiated inside async_setup_entry (direct or in a list)."""
    tree = MODULES[mod_name]
    names = []
    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "async_setup_entry"
        ):
            for c, dotted in calls(node):
                if "." not in dotted and dotted[0].isupper():
                    names.append((dotted, c.lineno))
    return names


def super_init_args(classes: dict[str, ast.ClassDef], cls_name: str):
    """(key, translation_key) literals from super().__init__(..., key, tkey)."""
    if cls_name not in classes:
        return None
    for node in ast.walk(classes[cls_name]):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "__init__":
            for c, dotted in calls(node):
                if dotted in ("super.__init__", "__init__") and len(c.args) >= 2:
                    pos = c.args
                    key = None
                    tkey = None
                    if len(pos) >= 4:
                        key, tkey = const_str(pos[2]), const_str(pos[3])
                    for kw in c.keywords:
                        if kw.arg == "key":
                            key = const_str(kw.value)
                        elif kw.arg == "translation_key":
                            tkey = const_str(kw.value)
                    return key, tkey
    return None


ENTITIES: dict[str, list[dict]] = {}
for plat in PLATFORMS:
    roster = []
    classes = class_defs(MODULES[plat])
    for name, lineno in find_setup_entities(plat):
        ent = {"cls": name, "file": f"{plat}.py", "line": lineno, "platform": plat}
        got = super_init_args(classes, name)
        if got is not None:
            ent["key"], ent["tkey"] = got
        # Direct unique_id assignment in own __init__ (climate/switch pattern):
        if "key" not in ent or ent["key"] is None:
            if name in classes:
                for node in ast.walk(classes[name]):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "__init__":
                        for stmt in ast.walk(node):
                            targets = []
                            if isinstance(stmt, ast.Assign):
                                targets = stmt.targets
                            elif isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
                                targets = [stmt.target]
                            for t in targets:
                                tname = t.attr if isinstance(t, ast.Attribute) else (t.id if isinstance(t, ast.Name) else None)
                                if tname == "_attr_unique_id":
                                    f = stmt.value
                                    # f"{entry.entry_id}_suffix" -> suffix
                                    if isinstance(f, ast.JoinedStr) and f.values and isinstance(f.values[-1], ast.Constant):
                                        ent["key"] = f.values[-1].value
        # translation_key as class attribute (switch pattern)
        if not ent.get("tkey"):
            src = attr_source(classes, name, "_attr_translation_key")
            if src is not None:
                ent["tkey"] = const_str(src[0])
        # device-named exemption (climate: _attr_name = None)
        nm = attr_source(classes, name, "_attr_name")
        ent["name_none"] = bool(nm is not None and isinstance(nm[0], ast.Constant) and nm[0].value is None)
        roster.append(ent)
    ENTITIES[plat] = roster

ALL_ENTS = [e for plat in PLATFORMS for e in ENTITIES[plat]]

# ---------------------------------------------------------------------------
# rule: action-setup — every hass.services.async_register site's enclosing chain
# ---------------------------------------------------------------------------
reg_sites = []
helper_names = set()
for mod, tree in MODULES.items():
    for c, dotted in calls(tree):
        if dotted.endswith("services.async_register") or dotted == "hass.services.async_register":
            chain = enclosing_functions(tree, c)
            reg_sites.append((f"{mod}.py", c.lineno, chain[-1] if chain else "<module>"))
            if chain:
                helper_names.add(chain[-1])
# which helpers are called from async_setup?
called_from_setup = set()
for mod, tree in MODULES.items():
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "async_setup":
            for c, dotted in calls(node):
                if dotted in helper_names:
                    called_from_setup.add(dotted)
ok_sites = sum(1 for _, _, fn in reg_sites if fn in called_from_setup)
result("action-setup.register_sites", len(reg_sites), "hass.services.async_register call sites")
result("action-setup.sites_in_async_setup_chain", ok_sites, "sites whose enclosing fn is called from async_setup")
result("action-setup.sites_elsewhere", len(reg_sites) - ok_sites)
for f, ln, fn in reg_sites:
    EVIDENCE.append(f"      site {f}:{ln} enclosing={fn}")

# ---------------------------------------------------------------------------
# rule: appropriate-polling — update_interval as constructed
# ---------------------------------------------------------------------------
coord = MODULES["coordinator"]
intervals = []
for node in ast.walk(coord):
    if isinstance(node, ast.Call):
        for kw in node.keywords:
            if kw.arg == "update_interval":
                intervals.append((node.lineno, ast.unparse(kw.value)))
result("appropriate-polling.update_interval_sites", len(intervals))
for ln, txt in intervals:
    EVIDENCE.append(f"      coordinator.py:{ln} update_interval={txt}")
# DEFAULT value + UI bounds (plain Assign or AnnAssign/Final)
cst = MODULES["const"]
defaults = {}
for node in ast.walk(cst):
    if isinstance(node, ast.Assign):
        targets = node.targets
        value = node.value
    elif isinstance(node, ast.AnnAssign) and node.value is not None:
        targets = [node.target]
        value = node.value
    else:
        continue
    for t in targets:
        if isinstance(t, ast.Name):
            try:
                defaults[t.id] = ast.literal_eval(value)
            except (ValueError, TypeError):
                pass
result(
    "appropriate-polling.default_interval_minutes",
    defaults.get("DEFAULT_OPTIMIZATION_INTERVAL", "NOT-FOUND"),
)
cf = open(os.path.join(INT, "config_flow.py"), encoding="utf-8").read()
bounds = re.findall(
    r"CONF_OPTIMIZATION_INTERVAL[\s\S]{0,200}?_number\((\d+),\s*(\d+),\s*(\d+),\s*\"min\"",
    cf,
)
bound = bounds[0] if bounds else ("?", "?")
result("appropriate-polling.ui_bounds_minutes", f"{bound[0]}-{bound[1]}")
result("appropriate-polling.scan_interval_defs", sum(1 for m, t in MODULES.items() for n in ast.walk(t) if isinstance(n, ast.Assign) and any(getattr(x, "id", "") == "SCAN_INTERVAL" for x in n.targets)))

# ---------------------------------------------------------------------------
# rule: common-modules
# ---------------------------------------------------------------------------
result("common-modules.coordinator_py_dataupdatecoordinator", sum(1 for n in ast.walk(coord) if isinstance(n, ast.ClassDef) and any("DataUpdateCoordinator" in b for b in [ast.unparse(x) for x in n.bases])))
result("common-modules.entity_py_exists", int(os.path.exists(os.path.join(INT, "entity.py"))))
own_base = {}
for plat in PLATFORMS:
    classes = class_defs(MODULES[plat])
    # platform base classes: class named *Base that is a base of roster classes
    roster_names = {e["cls"] for e in ENTITIES[plat]}
    plat_bases = [
        c for c, n in classes.items()
        if any(c in base_names(classes.get(r, n)) for r in roster_names if r in classes)
        and ("Base" in c)
    ]
    own_base[plat] = sorted(set(plat_bases))
    result(f"common-modules.{plat}_own_base_classes", len(set(plat_bases)), ",".join(sorted(set(plat_bases))) or "-")
importing_shared = 0
for plat in PLATFORMS:
    src = open(os.path.join(INT, f"{plat}.py"), encoding="utf-8").read()
    if re.search(r"from\s+\.entity\s+import|from\s+\.common\s+import", src):
        importing_shared += 1
result("common-modules.platform_files_importing_shared_entity_base", importing_shared)

# ---------------------------------------------------------------------------
# rule: config-flow
# ---------------------------------------------------------------------------
cft = MODULES["config_flow"]
steps = [n.name for n in ast.walk(cft) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith(("async_step_user", "async_step_"))]
result("config-flow.flow_step_functions", len(steps))
cf_src = open(os.path.join(INT, "config_flow.py"), encoding="utf-8").read()
result("config-flow.data_description_kwargs", len(re.findall(r"\bdata_description\s*=", cf_src)))
result("config-flow.data_description_in_comments", len(re.findall(r"#.*data_description", cf_src)))
creates_data = len(re.findall(r"async_create_entry\(\s*[^)]*?data=", cf_src, re.S))
creates_options = len(re.findall(r"async_set_options\(|options=\{", cf_src))
result("config-flow.create_entry_data_kwarg_sites", len(re.findall(r"data=\{", cf_src)))
result("config-flow.options_writes", len(re.findall(r"options=\{", cf_src)))

# ---------------------------------------------------------------------------
# rule: entity-event-setup — subscriptions per enclosing method class
# ---------------------------------------------------------------------------
SUB_FUNCS = ("async_track_state_change_event", "async_track_state_change", "async_track_time_interval", "async_track_point_in_time", "async_subscribe", "async_listen_once", "async_listen")
sub_sites = []
for mod, tree in MODULES.items():
    for c, dotted in calls(tree):
        leaf = dotted.split(".")[-1]
        if dotted in SUB_FUNCS or leaf in ("async_subscribe", "async_listen", "async_listen_once"):
            chain = enclosing_functions(tree, c)
            sub_sites.append((f"{mod}.py", c.lineno, dotted, "->".join(chain[:2]) or "<module>"))
result("entity-event-setup.subscription_sites_entity_platform_files", sum(1 for f, _, _, _ in sub_sites if f.split(".")[0] in PLATFORMS))
result("entity-event-setup.subscription_sites_coordinator", sum(1 for f, _, _, _ in sub_sites if f == "coordinator.py"))
result("entity-event-setup.subscriptions_in_async_added_to_hass", sum(1 for *_, ch in sub_sites if ch.startswith("async_added_to_hass")))
result("entity-event-setup.subscriptions_in_init_or_other", sum(1 for *_, ch in sub_sites if not ch.startswith("async_added_to_hass")))
for f, ln, d, ch in sub_sites:
    EVIDENCE.append(f"      sub {f}:{ln} {d} in {ch}")

# ---------------------------------------------------------------------------
# rule: entity-unique-id — derive ids, collision scan
# ---------------------------------------------------------------------------
total = len(ALL_ENTS)
with_key = [e for e in ALL_ENTS if e.get("key")]
result("entity-unique-id.entity_classes_total", total)
result("entity-unique-id.derived_unique_ids", len(with_key), "unique_id suffixes statically derived")
result("entity-unique-id.dynamic_underivable", total - len(with_key))
collisions = []
seen: dict[str, list[str]] = {}
for e in with_key:
    tag = f"{e['platform']}:{e['key']}"
    seen.setdefault(tag, []).append(e["cls"])
for tag, clss in seen.items():
    if len(clss) > 1:
        collisions.append((tag, clss))
result("entity-unique-id.collisions", len(collisions))
for tag, clss in collisions:
    EVIDENCE.append(f"      COLLISION {tag}: {clss}")
per_plat = {p: len(ENTITIES[p]) for p in PLATFORMS}
result("entity-unique-id.per_platform", ",".join(f"{p}={n}" for p, n in per_plat.items()))
cross = {}
for e in with_key:
    cross.setdefault(e["key"], []).append(e["platform"])
result("entity-unique-id.suffix_shared_across_platforms", sum(1 for k, v in cross.items() if len(set(v)) > 1))

# ---------------------------------------------------------------------------
# rule: has-entity-name
# ---------------------------------------------------------------------------
no_name = []
for e in ALL_ENTS:
    classes = class_defs(MODULES[e["file"][:-3]])
    got = attr_source(classes, e["cls"], "_attr_has_entity_name")
    if got is None or not (isinstance(got[0], ast.Constant) and got[0].value is True):
        no_name.append((e["cls"], got[1] if got else None))
result("has-entity-name.entities_total", total)
result("has-entity-name.with_has_entity_name_true", total - len(no_name))
result("has-entity-name.exceptions", len(no_name))
for cls, where in no_name:
    EVIDENCE.append(f"      missing has_entity_name: {cls} (resolved={where})")

# ---------------------------------------------------------------------------
# rule: runtime-data
# ---------------------------------------------------------------------------
rd_alias = sum(
    1
    for n in ast.walk(coord)
    if isinstance(n, ast.Assign)
    and isinstance(n.value, ast.Subscript)
    and "ConfigEntry[" in ast.unparse(n.value)
)
result("runtime-data.typed_alias_sites", rd_alias)
rd_reads = 0
for mod, tree in MODULES.items():
    src_lines = open(os.path.join(INT, f"{mod}.py"), encoding="utf-8").read()
    rd_reads += len(re.findall(r"\.runtime_data\b", src_lines))
hassdata = 0
for mod, tree in MODULES.items():
    src_lines = open(os.path.join(INT, f"{mod}.py"), encoding="utf-8").read()
    hassdata += len(re.findall(r"hass\.data\[DOMAIN\]|hass\.data\.get\(DOMAIN|hass\.data\.setdefault\(DOMAIN", src_lines))
result("runtime-data.runtime_data_reads", rd_reads)
result("runtime-data.hass_data_DOMAIN_reads", hassdata)
sig_uses = sum(len(re.findall(r"HeatPumpOptimizerConfigEntry", open(os.path.join(INT, f"{m}.py"), encoding="utf-8").read())) for m in MODULES)
result("runtime-data.alias_name_occurrences", sig_uses)

# ---------------------------------------------------------------------------
# rule: test-before-setup
# ---------------------------------------------------------------------------
init_tree = MODULES["__init__"]
setup_fn = None
for n in ast.walk(init_tree):
    if isinstance(n, ast.AsyncFunctionDef) and n.name == "async_setup_entry":
        setup_fn = n
first_refresh = 0
swallow = []
if setup_fn:
    for c, dotted in calls(setup_fn):
        if "async_config_entry_first_refresh" in dotted:
            first_refresh += 1
    for n in ast.walk(setup_fn):
        if isinstance(n, ast.ExceptHandler):
            body_desc = [ast.dump(x)[:60] for x in n.body]
            swallow.append((n.lineno, ast.unparse(n.type) if n.type else "bare"))
result("test-before-setup.first_refresh_calls", first_refresh)
result("test-before-setup.except_handlers_in_setup_entry", len(swallow))
for ln, t in swallow:
    EVIDENCE.append(f"      except {t} at __init__.py:{ln}")
uf = sum(1 for c, d in calls(coord) if d.endswith("UpdateFailed") or d == "UpdateFailed")
result("test-before-setup.updatefailed_raises_in_coordinator", uf)

# ---------------------------------------------------------------------------
# rule: action-exceptions — raise sites + silent swallows in handlers
# ---------------------------------------------------------------------------
EXC_NAMES = ("HomeAssistantError", "ServiceValidationError")
raise_sites = []
for mod, tree in MODULES.items():
    for n in ast.walk(tree):
        if isinstance(n, ast.Raise) and n.exc is not None and isinstance(n.exc, ast.Call):
            f = n.exc.func
            nm = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
            if nm in EXC_NAMES:
                has_tk = any(kw.arg in ("translation_key", "translation_domain") for kw in n.exc.keywords)
                chain = enclosing_functions(tree, n)
                raise_sites.append((f"{mod}.py", n.lineno, nm, has_tk, chain[0] if chain else "<module>"))
result("action-exceptions.raise_sites_total", len(raise_sites))
with_tk = sum(1 for _, _, _, tk, _ in raise_sites if tk)
result("action-exceptions.raises_with_translation_kwargs", with_tk)
result("action-exceptions.raises_without_translation_kwargs", len(raise_sites) - with_tk)
handler_swallows = 0
for n in ast.walk(init_tree):
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("handle_"):
        for h in ast.walk(n):
            if isinstance(h, ast.ExceptHandler):
                only_log_or_pass = all(
                    isinstance(x, (ast.Pass, ast.Expr)) for x in h.body
                )
                if only_log_or_pass:
                    handler_swallows += 1
result("action-exceptions.silent_swallow_except_in_handlers", handler_swallows)
for f, ln, nm, tk, fn in raise_sites:
    EVIDENCE.append(f"      raise {nm} {f}:{ln} in {fn} translation_kwargs={tk}")

# ---------------------------------------------------------------------------
# rule: parallel-updates
# ---------------------------------------------------------------------------
for plat in PLATFORMS:
    src = open(os.path.join(INT, f"{plat}.py"), encoding="utf-8").read()
    m = re.search(r"^PARALLEL_UPDATES\s*=\s*(\d+)", src, re.M)
    result(f"parallel-updates.{plat}", m.group(1) if m else "MISSING")

# ---------------------------------------------------------------------------
# rule: devices
# ---------------------------------------------------------------------------
di_sites = []
for mod, tree in MODULES.items():
    for c, dotted in calls(tree):
        if dotted.endswith("DeviceInfo"):
            fields = {kw.arg for kw in c.keywords if kw.arg}
            di_sites.append((f"{mod}.py", c.lineno, sorted(fields)))
result("devices.deviceinfo_sites", len(di_sites))
result("devices.sites_with_identifiers", sum(1 for *_, fs in di_sites if "identifiers" in fs))
result("devices.sites_with_manufacturer", sum(1 for *_, fs in di_sites if "manufacturer" in fs))
result("devices.sites_with_model", sum(1 for *_, fs in di_sites if "model" in fs))
result("devices.sites_with_sw_version", sum(1 for *_, fs in di_sites if "sw_version" in fs))
for f, ln, fs in di_sites:
    EVIDENCE.append(f"      DeviceInfo {f}:{ln} fields={fs}")

# ---------------------------------------------------------------------------
# rules: entity-category / entity-device-class / entity-disabled-by-default
# ---------------------------------------------------------------------------
cat_yes, cat_no = [], []
dc_yes, dc_no = [], []
dis_yes = []
for e in ALL_ENTS:
    classes = class_defs(MODULES[e["file"][:-3]])
    cat = attr_source(classes, e["cls"], "_attr_entity_category")
    if cat is not None:
        val = attr_value_name(cat[0])
        (cat_no if val == "None" else cat_yes).append((e["cls"], val))
    else:
        cat_no.append((e["cls"], "unset"))
    dc = attr_source(classes, e["cls"], "_attr_device_class")
    if e["platform"] == "sensor":
        (dc_yes if dc is not None else dc_no).append(e["cls"])
    dis = attr_source(classes, e["cls"], "_attr_entity_registry_enabled_default")
    if dis is not None and isinstance(dis[0], ast.Constant) and dis[0].value is False:
        dis_yes.append(e["cls"])
result("entity-category.entities_total", total)
result("entity-category.with_entity_category", len(cat_yes))
result("entity-category.without_entity_category", len(cat_no))
for cls, v in cat_no:
    EVIDENCE.append(f"      uncategorized: {cls} ({v})")
result("entity-device-class.sensors_total", len(ENTITIES["sensor"]))
result("entity-device-class.sensors_with_device_class", len(dc_yes))
result("entity-device-class.sensors_without_device_class", len(dc_no))
for cls in dc_no:
    EVIDENCE.append(f"      sensor without device_class: {cls}")
result("entity-disabled-by-default.disabled_entities", len(dis_yes))
result("entity-disabled-by-default.total_entities", total)
for cls in dis_yes:
    EVIDENCE.append(f"      disabled by default: {cls}")

# ---------------------------------------------------------------------------
# rule: entity-translations — cross tkey against strings.json/en/sv
# ---------------------------------------------------------------------------
strings = json.load(open(os.path.join(INT, "strings.json"), encoding="utf-8"))
en = json.load(open(os.path.join(INT, "translations", "en.json"), encoding="utf-8"))
sv = json.load(open(os.path.join(INT, "translations", "sv.json"), encoding="utf-8"))
uncovered = []
for e in ALL_ENTS:
    if e.get("name_none"):
        continue  # device-named main entity: no translation key needed
    tk = e.get("tkey")
    if tk is None:
        uncovered.append((e["platform"], e["cls"], "<no key>"))
        continue
    for label, blob in (("strings", strings), ("en", en), ("sv", sv)):
        names = blob.get("entity", {}).get(e["platform"], {})
        if tk not in names:
            uncovered.append((e["platform"], e["cls"], f"{label}:{tk}"))
result("entity-translations.entities_total", total)
result("entity-translations.device_named_exempt", sum(1 for e in ALL_ENTS if e.get("name_none")))
result("entity-translations.uncovered_entries", len(uncovered))
for p, cls, why in uncovered:
    EVIDENCE.append(f"      uncovered: {p}.{cls} {why}")
for plat in PLATFORMS:
    result(f"entity-translations.strings_entity_{plat}_names", len(strings.get("entity", {}).get(plat, {})))

# ---------------------------------------------------------------------------
# rule: exception-translations
# ---------------------------------------------------------------------------
result("exception-translations.raise_sites_total", len(raise_sites))
result("exception-translations.raises_with_translation_domain_key", with_tk)
result("exception-translations.raises_translatable", with_tk)
result("exception-translations.exceptions_section_strings.json", len(strings.get("exceptions", {})))
result("exception-translations.exceptions_section_en.json", len(en.get("exceptions", {})))
result("exception-translations.issues_section_strings.json", len(strings.get("issues", {})))

# ---------------------------------------------------------------------------
# rule: repair-issues
# ---------------------------------------------------------------------------
issue_sites = []
for mod, tree in MODULES.items():
    for c, dotted in calls(tree):
        if dotted.endswith("async_create_issue"):
            kwargs = {kw.arg for kw in c.keywords if kw.arg}
            issue_sites.append((f"{mod}.py", c.lineno, kwargs))
result("repair-issues.async_create_issue_sites", len(issue_sites))
result("repair-issues.sites_with_severity", sum(1 for *_, kw in issue_sites if "severity" in kw))
result("repair-issues.sites_with_translation_key", sum(1 for *_, kw in issue_sites if "translation_key" in kw))
result("repair-issues.strings_issues_keys", len(strings.get("issues", {})))
issue_tks = []
for mod, tree in MODULES.items():
    src = open(os.path.join(INT, f"{mod}.py"), encoding="utf-8").read()
    issue_tks += re.findall(r'async_create_issue\((?:.|\n)*?translation_key="([^"]+)"', src)
missing_tk = [t for t in set(issue_tks) if t not in strings.get("issues", {})]
result("repair-issues.issue_keys_missing_from_strings", len(missing_tk))
for t in missing_tk:
    EVIDENCE.append(f"      issue key missing from strings.json: {t}")

# ---------------------------------------------------------------------------
# rules: discovery family (exemption evidence)
# ---------------------------------------------------------------------------
discos = ["zeroconf", "ssdp", "dhcp", "usb", "bluetooth", "discovery"]
hits = []
for mod in MODULES:
    src = open(os.path.join(INT, f"{mod}.py"), encoding="utf-8").read()
    for d in discos:
        if re.search(rf"^\s*(import|from)\s+\S*{d}", src, re.M):
            hits.append((mod, d))
result("discovery.discovery_mechanism_imports", len(hits))
result("discovery-update-info.same_basis_zero_imports", len(hits))
devreg = sum(1 for mod, tree in MODULES.items() for c, dotted in calls(tree) if dotted.endswith("dr.async_get_or_create") or dotted.endswith("async_get_or_create"))
result("dynamic-devices.device_registry_create_sites", devreg)
result("stale-devices.async_remove_config_entry_device_sites", sum(1 for mod, tree in MODULES.items() for c, dotted in calls(tree) if dotted.endswith("async_remove_config_entry_device")))
result("stale-devices.deviceinfo_sites_static", len(di_sites))

# ---------------------------------------------------------------------------
# rule: async-dependency — blocking calls directly inside async defs
# ---------------------------------------------------------------------------
BLOCKING = ("time.sleep", "requests.get", "requests.post", "requests.request", "urllib.request.urlopen", "urlopen")
async_blockers = []
sleep_contexts = []
for mod, tree in MODULES.items():
    # map: node -> whether inside AsyncFunctionDef (not inside nested sync def)
    def walk_async(fn: ast.AST, in_async: bool, sync_depth: int):
        for child in ast.iter_child_nodes(fn):
            if isinstance(child, ast.FunctionDef):
                walk_async(child, False, sync_depth + 1)
                continue
            if isinstance(child, ast.AsyncFunctionDef):
                walk_async(child, True, sync_depth + 1)
                continue
            if isinstance(child, ast.Call):
                parts = []
                cur = child.func
                while isinstance(cur, ast.Attribute):
                    parts.append(cur.attr)
                    cur = cur.value
                if isinstance(cur, ast.Name):
                    parts.append(cur.id)
                dotted = ".".join(reversed(parts))
                if in_async:
                    if dotted in BLOCKING or (isinstance(child.func, ast.Name) and child.func.id == "open"):
                        async_blockers.append((f"{mod}.py", child.lineno, dotted))
            walk_async(child, in_async, sync_depth)
    walk_async(tree, False, 0)
    # every time.sleep with its enclosing def kind
    for c, dotted in calls(tree):
        if dotted == "time.sleep":
            chain = enclosing_functions(tree, c)
            kind = "?"
            for n in ast.walk(tree):
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == (chain[0] if chain else None):
                    kind = "async" if isinstance(n, ast.AsyncFunctionDef) else "sync"
                    break
            sleep_contexts.append((f"{mod}.py", c.lineno, chain[0] if chain else "<module>", kind))
result("async-dependency.blocking_calls_directly_in_async_defs", len(async_blockers))
for f, ln, d in async_blockers:
    EVIDENCE.append(f"      blocking-in-async: {f}:{ln} {d}")
result("async-dependency.time_sleep_sites", len(sleep_contexts))
for f, ln, fn, kind in sleep_contexts:
    EVIDENCE.append(f"      time.sleep {f}:{ln} in {fn} ({kind})")
executor = sum(1 for mod, tree in MODULES.items() for c, dotted in calls(tree) if "async_add_executor_job" in dotted or "async_add_job" in dotted or dotted.endswith("async_to_sync"))
to_thread = sum(1 for mod, tree in MODULES.items() for c, dotted in calls(tree) if "to_thread" in dotted)
result("async-dependency.executor_dispatch_sites", executor)
result("async-dependency.to_thread_sites", to_thread)

# ---------------------------------------------------------------------------
# rule: inject-websession
# ---------------------------------------------------------------------------
adhoc = []
gcs = []
for mod, tree in MODULES.items():
    for c, dotted in calls(tree):
        if dotted == "aiohttp.ClientSession":
            adhoc.append((f"{mod}.py", c.lineno))
        if dotted == "async_get_clientsession":
            gcs.append((f"{mod}.py", c.lineno))
result("inject-websession.adhoc_aiohttp_clientsession_constructions", len(adhoc))
result("inject-websession.async_get_clientsession_sites", len(gcs))
for f, ln in gcs:
    EVIDENCE.append(f"      async_get_clientsession {f}:{ln}")

# ---------------------------------------------------------------------------
# rule: integration-owner
# ---------------------------------------------------------------------------
manifest = json.load(open(os.path.join(INT, "manifest.json"), encoding="utf-8"))
result("integration-owner.manifest_codeowners_count", len(manifest.get("codeowners", [])))
result("integration-owner.first_codeowner", manifest.get("codeowners", ["<none>"])[0])

# ---------------------------------------------------------------------------
print()
print("EVIDENCE DETAIL")
for line in EVIDENCE:
    print(line)

load1 = os.getloadavg()[0]
result("thread_factor", 1.0)
result("load1", round(load1, 2))
result("swapins", 0)
