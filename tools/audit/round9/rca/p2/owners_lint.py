"""Round-9 RCA prototype, class P2: one fact, one owner.

P2 is "one fact decided twice by divergent predicates". Its round-9 fixes each
route a sibling seam through the fact's canonical owner. Fixer step 8 already
asks each fix for a rule enumerating the class's seams, but the rule is run once
and thrown away, and its dispositions are free text. This lint is the rule made
durable: a registry names, per fact, the AST shape that decides it and the one
function allowed to hold that shape. Any other hit fails unless it is in the
entry's disposition table with a reason. Three refusals keep it from going green
by skipping: an entry whose shape matches nothing anywhere, an owner that does
not exist, and a disposition whose site no longer hits.

Pure AST over custom_components/heatpump_optimizer/*.py; imports nothing from
the package, so it needs no stub and no venv.

    python3 tools/audit/round9/rca/p2/owners_lint.py            # the tree
    python3 tools/audit/round9/rca/p2/owners_lint.py --ref SHA  # any commit
    python3 tools/audit/round9/rca/p2/owners_lint.py --demo     # fail/pass/null runs
Exit 0 only when every entry is clean. One RESULT line per entry.
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys
import time
from pathlib import Path

PKG = "custom_components/heatpump_optimizer"


# --------------------------------------------------------------------- matchers
def _conf(e):
    if isinstance(e, ast.Name) and e.id.startswith("CONF_"):
        return e.id
    if isinstance(e, ast.Attribute) and e.attr.startswith("CONF_"):
        return e.attr
    return None


def _conf_read(n):
    """`x.get(K)`, `x[K]` (load) or `K in x`: the CONF_ name read, else None."""
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get" and n.args:
        return _conf(n.args[0])
    if isinstance(n, ast.Subscript) and isinstance(n.ctx, ast.Load):
        return _conf(n.slice)
    if isinstance(n, ast.Compare) and len(n.ops) == 1 and isinstance(n.ops[0], (ast.In, ast.NotIn)):
        return _conf(n.left)
    return None


def _decides(n, parents):
    """True when n sits in an if/while/assert/ternary test, a bool op, `not` or bool()."""
    cur = n
    while cur in parents:
        par = parents[cur]
        if isinstance(par, (ast.If, ast.IfExp, ast.While, ast.Assert)) and cur is par.test:
            return True
        if isinstance(par, ast.BoolOp) or (isinstance(par, ast.UnaryOp) and isinstance(par.op, ast.Not)):
            return True
        if isinstance(par, ast.Call) and getattr(par.func, "id", None) == "bool":
            return True
        if isinstance(par, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.stmt)):
            return False
        cur = par
    return False


def match_proxy(keys):
    """A decision-context read of one of the fact's proxy keys."""
    def m(n, parents):
        k = _conf_read(n)
        return k in keys and _decides(n, parents)
    m.live = bool(keys)  # extracted from the predicate: empty means the extraction broke
    return m


def match_node(types, pattern, part=None, pre=None):
    """A node of `types` whose unparsed text (or `part` of it) matches `pattern`.

    `pre` is a cheap structural filter run before the unparse, which is the cost.
    """
    rx = re.compile(pattern)

    def m(n, parents):
        if not isinstance(n, types) or (pre and not pre(n)):
            return False
        if isinstance(n, ast.Attribute) and not isinstance(n.ctx, ast.Load):
            return False
        sub = getattr(n, part) if part else n
        return bool(rx.search(ast.unparse(sub)))
    return m


def match_literal_service_domain(domains):
    """`*.async_call("<domain>", ...)`: an entity write whose domain is a literal."""
    def m(n, parents):
        return (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "async_call"
                and n.args and isinstance(n.args[0], ast.Constant) and n.args[0].value in domains)
    return m


_STAMPS = {"last_updated", "last_changed", "last_reported"}


# ---------------------------------------------------------- proxy-key extraction
def proxies(read):
    """Proxy CONF_ names extracted from the canonical predicate bodies (D14-s2-01's rule)."""
    def names(node):
        return {c for x in ast.walk(node) if (c := _conf(x))}
    tm, wf = ast.parse(read(f"{PKG}/thermal_model.py")), ast.parse(read(f"{PKG}/wood_fuel.py"))
    out = {"two_zone_enabled": set(), "dhw_enabled": set(), "wood_furnace_on": set()}
    for n in ast.walk(tm):
        if isinstance(n, ast.If):
            txt = ast.unparse(n)
            if "values['two_zone_enabled']" in txt and "CONF_TWO_ZONE_MODE" not in txt:
                out["two_zone_enabled"] |= names(n)
        if isinstance(n, ast.Assign) and "two_zone_mode" in ast.unparse(n.targets[0]):
            out["two_zone_enabled"] |= names(n.value)
        if isinstance(n, ast.FunctionDef) and n.name == "_dhw_enabled_from_config":
            out["dhw_enabled"] |= names(n)
    for n in ast.walk(wf):
        if isinstance(n, ast.FunctionDef) and n.name in ("wood_furnace_on", "wood_furnace_inferred"):
            out["wood_furnace_on"] |= names(n)
    return out


# ------------------------------------------------------------------- registry
# owners: "file.py::Qual.name" where the shape may live. dispositions: sites the
# rule returns that are not the fact's decision, each with its reason (the
# guarded / not-applicable rows of the finding's own seam table).
def registry(read):
    px = proxies(read)
    return [
        dict(fact="two_zone_enabled", finding="D14-s2-01", match=match_proxy(px["two_zone_enabled"]),
             owners=["thermal_model.py::ThermalParameters.from_config"], dispositions={}),
        dict(fact="wood_furnace_on", finding="D14-s2-01", match=match_proxy(px["wood_furnace_on"]),
             owners=["wood_fuel.py::wood_furnace_on", "wood_fuel.py::wood_furnace_inferred", "wood_fuel.py::wood_fuel_ready"],
             dispositions={
                 "coordinator.py::HeatPumpOptimizerCoordinator._external_heat_config": "guarded: ANDed with wood_furnace_on",
                 "config_flow.py::HeatPumpOptimizerOptionsFlow.async_step_building": "guarded: normalises the flag after wood_furnace_on(merged)",
                 "thermal_model.py::ThermalParameters.from_config": "guarded: under _on = wood_furnace_on(config)",
                 "quick_setup.py::stored_answers": "not a decision: answer read-back",
             }),
        dict(fact="dhw_enabled", finding="D14-s2-01", match=match_proxy(px["dhw_enabled"]),
             owners=["thermal_model.py::_dhw_enabled_from_config"],
             dispositions={
                 "legionella.py::LegionellaGuard.async_track_cycle": "probe presence, not the hot-water fact",
                 "coordinator.py::HeatPumpOptimizerCoordinator._dhw_probe_temperature": "probe presence",
                 "topology.py::rank_sensor_gaps": "probe presence",
                 "sensor.py::_gap_probe_terms": "a volume default",
                 "services.py::handle_set_thermal_params": "service data write",
                 "services.py::handle_apply_topology": "service data write",
                 "services.py::handle_apply_schedule": "service data write",
                 "coordinator.py::HeatPumpOptimizerCoordinator.async_update_thermal_params": "windows update",
                 "quick_setup.py::stored_answers": "not a decision: answer read-back",
             }),
        # D1-s5-01: a state's age. InputReader owns the stamp rule (last_reported
        # first, a future stamp is stale, #775); age_of re-derived it.
        dict(fact="state_age", finding="D1-s5-01",
             match=match_node((ast.Attribute,), r"\.(last_updated|last_changed|last_reported)$",
                              pre=lambda n: n.attr in _STAMPS),
             also=match_node((ast.Call,), r"^getattr\(.*'(last_updated|last_changed|last_reported)'",
                             pre=lambda n: getattr(n.func, "id", None) == "getattr" and len(n.args) > 1
                             and getattr(n.args[1], "value", None) in _STAMPS),
             owners=["inputs.py::state_stamp"],
             dispositions={}),
        # D12-s2-01 (and the thrice-held threshold beside it): whether a step's
        # draw means "on". One formula, held at four sites at baseline.
        dict(fact="on_threshold_kw", finding="D12-s2-01",
             match=match_node((ast.BinOp,), r"min_electrical_power\)? \* 0\.5|0\.5 \* .*min_electrical_power",
                              pre=lambda n: isinstance(n.op, ast.Mult) and 0.5 in (
                                  getattr(n.left, "value", None), getattr(n.right, "value", None))),
             owners=["thermal_model.py::on_threshold_kw"], dispositions={}),
        # D12-s2-02: the domain that writes a configured entity comes from the
        # entity (coordinator._on_off_service, #1526), never a literal.
        dict(fact="entity_write_domain", finding="D12-s2-02",
             match=match_literal_service_domain({"select", "switch", "input_select", "input_boolean", "number", "input_number"}),
             owners=["coordinator.py::_on_off_service"],
             dispositions={
                 "coordinator.py::HeatPumpOptimizerCoordinator._command_frequency": "compressor_freq slot is number-only (config_flow _entity_of('number'))",
             }),
        # D1-s3-01 (fromisoformat outside one tz-normalising parser) is left to
        # the P1 and future-instant barriers (F1.6, F1.9), which own that shape:
        # one shape, one check.
    ]


# ------------------------------------------------------------------- the scan
def _index(tree):
    parents, qual = {}, {}
    def walk(node, q):
        for c in ast.iter_child_nodes(node):
            parents[c] = node
            cq = q
            if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                cq = f"{q}.{c.name}" if q else c.name
            qual[c] = cq
            walk(c, cq)
    walk(tree, "")
    return parents, qual


def _owner_of(n, parents, qual):
    """Qualname of the innermost function or class enclosing n ('' at module level)."""
    cur = n
    while cur in parents:
        cur = parents[cur]
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return qual[cur]
    return ""


def scan(read, files):
    trees = {}
    for f in files:
        try:
            trees[Path(f).name] = ast.parse(read(f))
        except SyntaxError:
            continue
    defined = set()
    idx = {}
    for name, t in trees.items():
        p, q = _index(t)
        idx[name] = (p, q)
        defined |= {f"{name}::{v}" for v in q.values() if v}
    results = []
    for e in registry(read):
        hits = []
        for name, t in trees.items():
            if name == "const.py":
                continue
            parents, qual = idx[name]
            for n in ast.walk(t):
                if e["match"](n, parents) or (e.get("also") and e["also"](n, parents)):
                    hits.append((name, n.lineno, _owner_of(n, parents, qual)))
        site = lambda h: f"{h[0]}::{h[2]}"  # noqa: E731
        stray = [h for h in hits if site(h) not in e["owners"] and site(h) not in e["dispositions"]]
        missing_owner = [o for o in e["owners"] if o not in defined]
        stale = [d for d in e["dispositions"] if d not in {site(h) for h in hits}]
        dead = not hits and not getattr(e["match"], "live", False)
        results.append((e, hits, stray, missing_owner, stale, dead))
    return results


def report(results, label):
    bad = 0
    for e, hits, stray, missing, stale, dead in results:
        for h in stray:
            print(f"SEAM {e['fact']} {h[0]}:{h[1]} in {h[2] or '<module>'} (outside owner; {e['finding']})")
        for o in missing:
            print(f"OWNER-MISSING {e['fact']} {o}")
        for d in stale:
            print(f"STALE-DISPOSITION {e['fact']} {d}")
        if dead:
            print(f"DEAD-RULE {e['fact']}: the shape matches nothing; the rule would pass by skipping")
        fail = bool(stray or missing or stale or dead)
        bad += fail
        print(f"RESULT p2_owner[{e['fact']}@{label}]={'FAIL' if fail else 'ok'} hits={len(hits)} stray={len(stray)} "
              f"owner_missing={len(missing)} stale={len(stale)}")
    return bad


def reader(ref):
    if ref is None:
        return (lambda p: Path(p).read_text()), sorted(str(p) for p in Path(PKG).glob("*.py"))
    ls = subprocess.run(["git", "ls-tree", "--name-only", f"{ref}:{PKG}"], capture_output=True, text=True, check=True)
    return ((lambda p: subprocess.run(["git", "show", f"{ref}:{p}"], capture_output=True, text=True, check=True).stdout),
            [f"{PKG}/{f}" for f in ls.stdout.split() if f.endswith(".py")])


# ------------------------------------------------------------------- demo
_INPUT_CHAIN = '''(
            getattr(state, "last_reported", None)
            or getattr(state, "last_updated", None)
            or getattr(state, "last_changed", None)
        )'''
_AGE_OF_CHAIN = '''getattr(state, "last_updated", None) or getattr(
        state, "last_changed", None
    )'''
_STAMP_OWNER = '''

def state_stamp(state):
    return (getattr(state, "last_reported", None) or getattr(state, "last_updated", None)
            or getattr(state, "last_changed", None))
'''
_WOOD_BODY = '''    if CONF_WOOD_FURNACE_ENABLED in config:
        return bool(config[CONF_WOOD_FURNACE_ENABLED])
    return bool(
        config.get(CONF_EXTERNAL_HEAT_ENABLED)
        or config.get(CONF_WOOD_TANK_TOP_ENTITY)
        or config.get(CONF_WOOD_TANK_BOTTOM_ENTITY)
        or config.get(CONF_VALVE_OUTLET_TEMP_ENTITY)
        or config.get(CONF_EXTERNAL_HEAT_ENTITY)
    )'''
# The round-9 instances routed through their owners, as their fixes would:
# (file, old, new). Every old text is asserted present, so a stale demo cannot
# pass by replacing nothing.
FIXES = {
    "two_zone_enabled": [
        ("config_flow.py", "two_zone=bool(current.get(CONF_UPPER_FLOOR_THERMAL_MASS)),",
         "two_zone=ThermalParameters.from_config(dict(current)).two_zone_enabled,"),
        ("modbus_prefill.py", "if water and current.get(CONF_UPPER_FLOOR_THERMAL_MASS)",
         "if water and ThermalParameters.from_config(dict(current)).two_zone_enabled")],
    "wood_furnace_on": [("topology.py", _WOOD_BODY, "    return wood_furnace_on(config)")],
    "state_age": [
        ("inputs.py", _INPUT_CHAIN, "state_stamp(state)"),
        ("inputs.py", _INPUT_CHAIN, "state_stamp(state)"),
        ("inputs.py", _AGE_OF_CHAIN, "state_stamp(state)"),
        ("inputs.py", "\n\ndef age_of(", _STAMP_OWNER + "\n\ndef age_of(")],
    "on_threshold_kw": [
        ("coordinator.py", 'max(0.1, 0.5 * getattr(self, "_ctx", self)._thermal_params.min_electrical_power)',
         'on_threshold_kw(getattr(self, "_ctx", self)._thermal_params)'),
        ("optimizer.py", "on_threshold = max(0.1, p.min_electrical_power * 0.5)", "on_threshold = on_threshold_kw(p)"),
        ("optimizer.py", "on_threshold = max(0.1, self.model.params.min_electrical_power * 0.5)",
         "on_threshold = on_threshold_kw(self.model.params)"),
        ("pump_arbiter.py", "max(0.1, float(coord._thermal_model.params.min_electrical_power) * 0.5)",
         "on_threshold_kw(coord._thermal_model.params)"),
        ("thermal_model.py", "\n\n@dataclass",
         "\n\ndef on_threshold_kw(params):\n    return max(0.1, params.min_electrical_power * 0.5)\n\n\n@dataclass")],
    "entity_write_domain": [
        ("pump_arbiter.py", 'async_call(\n                "select",', 'async_call(\n                entity.split(".", 1)[0],')],
}

NULL_PROBES = {
    "new sibling re-derives two-zone from a proxy key": [
        ("topology.py", "\n\ndef describe_setup(",
         "\n\ndef _new_seam(config):\n    if config.get(CONF_UPPER_FLOOR_THERMAL_MASS):\n        return 1\n    return 0"
         "\n\n\ndef describe_setup(")],
    "new entity write with a literal domain": [
        ("pump_arbiter.py", "\n\ndef _on_kw(",
         '\n\nasync def _new_write(coord, entity):\n    await coord.hass.services.async_call("switch", "turn_on", {})'
         "\n\n\ndef _on_kw(")],
    "new state-age reader beside the owner": [
        ("coordinator.py", "\n\ndef _on_off_service(",
         "\n\ndef _age2(state, now):\n    return now - state.last_updated\n\n\ndef _on_off_service(")],
    "owner renamed (would pass by skipping)": [
        ("thermal_model.py", "def on_threshold_kw(params):", "def on_kw_renamed(params):")],
    "disposition gone stale (its site now routes through the owner)": [
        ("coordinator.py", 'async_call(\n                "number",', 'async_call(\n                entity_id.split(".", 1)[0],')],
    "shape vanished everywhere (would pass by skipping)": [
        ("thermal_model.py", "    return max(0.1, params.min_electrical_power * 0.5)",
         "    return max(0.1, params.min_electrical_power / 2)")],
}


def overlay(read, edits):
    """read() with the (file, old, new) edits applied, each old replaced once."""
    def r(p):
        text = read(p)
        for f, old, new in edits:
            if p.endswith("/" + f):
                assert old in text, (f, old[:60])
                text = text.replace(old, new, 1)
        return text
    return r


def demo(ref):
    read, files = reader(ref)
    cache = {}
    base = lambda p: cache.setdefault(p, read(p))  # noqa: E731
    print("## A. defect present")
    a = report(scan(base, files), ref)
    print("## B. each fact's instances routed through its owner, one fact at a time")
    per = 0
    for fact, edits in FIXES.items():
        per += report([r for r in scan(overlay(base, edits), files) if r[0]["fact"] == fact], f"{ref}+fix[{fact}]")
    print("## C. every fix applied (the healthy tree the instance PRs leave)")
    healthy = overlay(base, [e for es in FIXES.values() for e in es])
    c = report(scan(healthy, files), f"{ref}+fix[all]")
    print("## D. null probes on the healthy tree: each must fire")
    fired = 0
    for name, edits in NULL_PROBES.items():
        res = scan(overlay(healthy, edits), files)
        report(res, f"probe[{name}]")
        bad = [r[0]["fact"] for r in res if r[2] or r[3] or r[4] or r[5]]
        print(f"RESULT null_probe[{name}]={'FIRES on ' + ','.join(bad) if bad else 'SILENT'}")
        fired += bool(bad)
    print(f"RESULT demo_baseline_entries_failing={a} of {len(FIXES) + 1}")
    print(f"RESULT demo_own_fix_entries_failing={per} of {len(FIXES)}")
    print(f"RESULT demo_healthy_entries_failing={c} count")
    print(f"RESULT demo_null_probes_firing={fired} of {len(NULL_PROBES)}")


def main():
    if "--demo" in sys.argv:
        k = sys.argv.index("--demo")
        t0 = time.perf_counter()
        demo(sys.argv[k + 1] if len(sys.argv) > k + 1 else "1936d5ca")
        print(f"RESULT demo_wall_s={time.perf_counter() - t0:.2f} s")
        return
    t0 = time.perf_counter()
    ref = sys.argv[sys.argv.index("--ref") + 1] if "--ref" in sys.argv else None
    read, files = reader(ref)
    if ref:  # one git-show per file, cached
        cache = {}
        base = read
        read = lambda p: cache.setdefault(p, base(p))  # noqa: E731
    bad = report(scan(read, files), ref or "worktree")
    print(f"RESULT p2_owner_entries_failing={bad} count")
    print(f"RESULT p2_owner_wall_s={time.perf_counter() - t0:.2f} s")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
