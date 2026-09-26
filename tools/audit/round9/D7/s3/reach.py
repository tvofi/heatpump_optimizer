#!/usr/bin/env python3
"""D7.M6 -- dead code by AST reachability from the integration's real roots.

Metric: the number of class-body functions (methods AND @property getters) and
top-level symbols in custom_components/heatpump_optimizer that no LIVE
production code reaches, where "live" is the closure from Home Assistant's
entry points (module-level statements, HA_CONVENTION_NAMES/METHODS and the
entity-attribute surface HA reads), and a reach edge is a load of the name
from a node already reached.  Differs from tests/structure.py's
dead_top_level_symbols / dead_methods in exactly two declared ways:
  (1) a @property getter is a node like any method (structure.py's method
      screen skips every property by construction, is_property_getter);
  (2) a reference counts only when it sits in a reached node (structure.py
      counts a load from anywhere, including from code that is itself dead).
Count key: the production DEFINITION (module, Class.name) -- a fix deletes the
definition or adds a live production load of its name; nothing in the input
config can move it.

Edges are name-based and deliberately over-approximate liveness: `x.N` from a
reached node reaches every method/property/top-level symbol named N anywhere
(except `mod.N` through a module binding, which resolves exactly), so every
symbol this reports dead is dead under the MOST generous reading.  A
getattr/hasattr/setattr with a string constant is a load of that name; the
CONF_/DEFAULT_ getattr(const, f"...") tables are resolved literally.

Command (repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D7/s3/reach.py [--perturb-live NAME ...] [--list]
--perturb-live NAME appends the bare expression statement `NAME` / `object().NAME` (a live
module-level load) to the
source of the module defining NAME, in memory -- the one-line production edit
a fix that re-wires the symbol makes.  Each dead NAME passed must lower
dead_reachability_total by exactly 1 (properties) -- the judge's perturbation.
Expected at 1936d5ca: dead_reachability_total = 9 +- 0 (count, contention
immune).  Machine: B5 cloud container (linux).  Baseline 1936d5ca72a0.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import ast
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, "tests")
import structure as S  # noqa: E402  (HA_CONVENTION_*, DYNAMIC_REFERENCES)

PKG = Path("custom_components/heatpump_optimizer")

# The attribute surface Home Assistant reads off an entity / flow / coordinator
# instance by convention, so a property of this name is a root.  Taken from the
# upstream Entity/SensorEntity/BinarySensorEntity/ClimateEntity/SwitchEntity/
# ButtonEntity/DateTimeEntity/CoordinatorEntity/DataUpdateCoordinator APIs.
HA_ATTRIBUTE_SURFACE = {
    "available", "device_info", "name", "unique_id", "icon", "entity_picture",
    "entity_category", "entity_registry_enabled_default", "has_entity_name",
    "translation_key", "translation_placeholders", "should_poll",
    "assumed_state", "force_update", "attribution", "state", "state_attributes",
    "capability_attributes", "extra_state_attributes", "native_value",
    "native_unit_of_measurement", "unit_of_measurement", "device_class",
    "state_class", "options", "suggested_display_precision",
    "suggested_unit_of_measurement", "last_reset", "is_on",
    "current_temperature", "target_temperature", "target_temperature_high",
    "target_temperature_low", "target_temperature_step", "hvac_mode",
    "hvac_modes", "hvac_action", "preset_mode", "preset_modes",
    "supported_features", "min_temp", "max_temp", "temperature_unit",
    "precision", "current_humidity", "fan_mode", "fan_modes", "coordinator",
    "last_update_success", "data", "entity_description", "config_entry",
    "flow_manager",
}

ap = argparse.ArgumentParser()
ap.add_argument("--perturb-live", action="append", default=[])
ap.add_argument("--list", action="store_true")
args = ap.parse_args()

t0 = time.process_time()
tt0 = time.thread_time()

src: dict[str, str] = {}
for p in sorted(PKG.glob("*.py")):
    src[p.stem] = p.read_text()
trees = {m: ast.parse(s) for m, s in src.items()}

# --perturb-live: find the defining module(s) and append a live load.
for name in args.perturb_live:
    hit = False
    for m, t in trees.items():
        for n in ast.walk(t):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == name:
                hit = True
        if hit:
            src[m] = src[m] + f"\n{name}\n" if any(
                isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == name
                for n in trees[m].body) else src[m] + f"\nobject().{name}\n"
            trees[m] = ast.parse(src[m])
            break
    if not hit:
        sys.exit(f"--perturb-live {name}: no such definition")

# ---- nodes -----------------------------------------------------------------
# node id: (module, qual); kind: func|class|const|method|property
nodes: dict[tuple[str, str], dict] = {}
by_attr: dict[str, set] = defaultdict(set)      # member name -> node ids
top: dict[tuple[str, str], tuple[str, str]] = {}  # (mod,name) -> node id
root_bodies: list[tuple[str, list[ast.AST], set]] = []  # (module, ast list, own-span-excl)


def add(mod, qual, kind, body, line, extra_live=()):
    nid = (mod, qual)
    nodes[nid] = {"kind": kind, "body": body, "line": line}
    return nid


for m, t in trees.items():
    live_stmts = []
    for n in t.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            nid = add(m, n.name, "func", [n.args, *n.body, *(n.returns and [n.returns] or [])], n.lineno)
            top[(m, n.name)] = nid
            live_stmts += n.decorator_list + list(n.args.defaults) + [d for d in n.args.kw_defaults if d]
        elif isinstance(n, ast.ClassDef):
            cls_live = []
            nid = add(m, n.name, "class", cls_live, n.lineno)
            top[(m, n.name)] = nid
            live_stmts += n.decorator_list + n.bases + [k.value for k in n.keywords]
            for b in n.body:
                if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    kind = "property" if S.is_property_getter(b) else "method"
                    mid = add(m, f"{n.name}.{b.name}", kind, [b.args, *b.body], b.lineno)
                    by_attr[b.name].add(mid)
                    live_stmts += b.decorator_list + list(b.args.defaults) + [d for d in b.args.kw_defaults if d]
                else:
                    cls_live.append(b)  # class-body statement: runs when class is defined
        else:
            if isinstance(n, (ast.Assign, ast.AnnAssign)):
                targets = n.targets if isinstance(n, ast.Assign) else [n.target]
                names = [x.id for x in targets if isinstance(x, ast.Name)]
                if names and n.value is not None:
                    for nm in names:
                        nid = add(m, nm, "const", [n.value], n.lineno)
                        top[(m, nm)] = nid
                    continue
            live_stmts.append(n)
    root_bodies.append((m, live_stmts, set()))

# import bindings (mirrors structure.bound_references)
sym_bind: dict[tuple[str, str], tuple[str, str]] = {}
mod_bind: dict[tuple[str, str], str] = {}
for m, t in trees.items():
    for n in ast.walk(t):
        if isinstance(n, ast.ImportFrom) and n.level >= 1:
            srcmod = n.module or "__init__"
            for a in n.names:
                b = a.asname or a.name
                if a.name in trees and n.module is None:
                    mod_bind[(m, b)] = a.name
                else:
                    sym_bind[(m, b)] = (srcmod, a.name)


def resolve(m, name):
    seen = set()
    while (m, name) not in top and (m, name) in sym_bind and (m, name) not in seen:
        seen.add((m, name))
        m, name = sym_bind[(m, name)]
    # package-root lazy re-export (__init__.__getattr__ over _LAZY_ATTRS)
    return top.get((m, name))


top_by_name: dict[str, set] = defaultdict(set)
for (m, nm), nid in top.items():
    top_by_name[nm].add(nid)


def targets_of(mod, stmts, self_nid=None):
    out = set()
    const_prefix_lookup = False
    for s in stmts:
        for n in ast.walk(s):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                r = resolve(mod, n.id)
                if r and r != self_nid:
                    out.add(r)
            elif isinstance(n, ast.Attribute):
                base = n.value.id if isinstance(n.value, ast.Name) else None
                if (mod, base) in mod_bind:
                    r = top.get((mod_bind[(mod, base)], n.attr))
                    if r:
                        out.add(r)
                else:
                    out |= by_attr.get(n.attr, set())
                    if base not in ("self", "cls"):
                        out |= top_by_name.get(n.attr, set())
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                    and n.func.id in ("getattr", "hasattr", "setattr") and len(n.args) >= 2:
                a1 = n.args[1]
                if isinstance(a1, ast.Constant) and isinstance(a1.value, str):
                    out |= by_attr.get(a1.value, set()) | top_by_name.get(a1.value, set())
                if isinstance(a1, ast.JoinedStr) and a1.values and isinstance(a1.values[0], ast.Constant):
                    const_prefix_lookup = a1.values[0].value
                    # every literal string in this statement joined to the prefix
                    for c in ast.walk(s):
                        if isinstance(c, ast.Constant) and isinstance(c.value, str):
                            out |= top_by_name.get(const_prefix_lookup + c.value, set())
    return out


# a getattr(const, f"CONF_{x}") table: its literals live in a dict display
# assembled OUTSIDE the call statement; resolve literally module-wide.
def prefix_tables(mod):
    out = set()
    t = trees[mod]
    prefixes = set()
    for n in ast.walk(t):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "getattr" \
                and len(n.args) >= 2 and isinstance(n.args[1], ast.JoinedStr) and n.args[1].values \
                and isinstance(n.args[1].values[0], ast.Constant):
            prefixes.add(n.args[1].values[0].value)
    if prefixes:
        for n in ast.walk(t):
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                for p in prefixes:
                    out |= top_by_name.get(p + n.value, set())
    return out


# ---- roots -------------------------------------------------------------------
reached: set = set()
frontier: list = []


def reach(nid):
    if nid not in reached:
        reached.add(nid)
        frontier.append(nid)


seed = set()
for m, stmts, _ in root_bodies:
    seed |= targets_of(m, stmts)
for nid, info in nodes.items():
    name = nid[1].split(".")[-1]
    if name.startswith("__") and name.endswith("__"):
        seed.add(nid)
    if name in S.HA_CONVENTION_NAMES:
        seed.add(nid)
    if info["kind"] in ("method", "property") and (
            S.is_ha_convention_method(name) or name in HA_ATTRIBUTE_SURFACE):
        seed.add(nid)
for nid in seed:
    reach(nid)

while frontier:
    nid = frontier.pop()
    m = nid[0]
    info = nodes[nid]
    tg = targets_of(m, info["body"], self_nid=nid if info["kind"] == "func" else None)
    if info["kind"] == "class":
        # a reached class runs its body statements (already in body) and
        # makes its conventional members reachable through the instance;
        # its prefix tables resolve literally
        pass
    tg |= prefix_tables(m) if info["kind"] in ("func", "method", "property") else set()
    for x in tg:
        reach(x)

# ConfigFlow/OptionsFlow subclasses are found by HA via the manifest/handler
dead = []
for nid, info in sorted(nodes.items()):
    if nid in reached:
        continue
    if info["kind"] == "class":
        # structure.py exempts flow handlers; so do we
        continue
    dead.append((nid, info))

# report
static_names = set()
for m, t in trees.items():
    for n in ast.walk(t):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
            static_names.add(n.id)
        elif isinstance(n, ast.Attribute):
            static_names.add(n.attr)
by_kind = defaultdict(int)
for nid, info in dead:
    by_kind[info["kind"]] += 1
    if args.list:
        print(f"DEAD {info['kind']:8s} {nid[0]}.py:{info['line']} {nid[1]}")
print(f"RESULT nodes_total={len(nodes)} count")
print(f"RESULT reached={len(reached)} count")
print(f"RESULT dead_reachability_total={len(dead)} count")
for k in ("func", "const", "method", "property"):
    print(f"RESULT dead_{k}={by_kind[k]} count")
cpu, th = time.process_time() - t0, time.thread_time() - tt0
print(f"RESULT thread_factor={cpu / th if th else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
