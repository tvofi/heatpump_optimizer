#!/usr/bin/env python3
"""Print one audit universe, one item per line, so a finder can report `universe=N examined=n`.

Usage: python3 -I tools/audit/enumerate.py <universe> [--repo DIR] [options]
  d0-grid [--plane price-weather]   tests/profiles.py price x weather, x zones x dhw x plant x horizon
  d0-modules             package-internal import closure of optimizer.py + dhw_planner.py, plus coordinator.py
  d1-lifecycle           async_track_* / async_call_later / listener / task registrations and the entry points
  d1-stores              store.py DOMAINS keys, and one `upgrade` line per earlier *_STORE_VERSION /
                         CONFIG_ENTRY_VERSION step
  d1-inputs              every configured entity slot: a config_flow.py `_F` key behind an entity selector,
                         and each key entry_config.py's FACTORY_KEPT keeps as an entity assignment
  d1-solve-state         every `self.<attr>` the solve-thread entries (SOLVE_FNS) touch
  d1-excepts             every except handler, broad or narrow
  d1-parsers             defs named *parse*, and json.loads / .json() / async_subscribe sites
  d2-identities [--cells]   dev/audit/config/identities.json, one line per identity; --cells crosses each
                         with its grid (population axes, tests/golden.py SCENARIOS, or levels the register states)
  d3-sites [--state S] [--by-file] [--ast]   the mutation universe, `<file>:<line> <kind> <state>`, joined
                         to the ledger through tests/mutation_table.py's own `inventory` and
                         `disposition_matches`; --ast is the ledger-free fallback (if/ifexp/minmax/except)
  d8-cells               strings.json entity name / state / attribute, once per translation file
  d9-collections         coordinator.py `self.<attr>` bound to a container, once per class and attribute
  d9-attributes          classes defining or assigning extra_state_attributes
  d9-solves              calls of the solver entry, then of each function holding one, to a fixed point
  d12-cells [--pairs]    every level `check_scopes.py --population` reads, each level one of its NO-READ
                         axes declares in objective.json, the card and the blueprints
                         (--pairs: every pair of levels from two axes), each `not run` until a ledger row
  --ledger TSV           with any universe: each line beside its ledger row's asserting test, or `not run`
                         (rows: item, test; for d12-cells: cell, source, test); a row naming no item,
                         an unlisted source or no test is refused
  d14-classes [--status open]   dev/audit/config/bugclasses.json entries that carry a status
  d15-installs           dev/audit/config/bundles.json, one line per bundle an install sent
  d16-writes [--cells]   every call of, or reference to, `services.async_call` (`write ... domain=<literal>`,
                         `domain=?` when the domain is no literal; a literal on READ_ONLY_DOMAINS is no write)
                         and every `log_held` site; --cells crosses each with the plan states of STATES, and
                         refuses unless const.py's PUMP_DUTY_MODES equal the duty modes those states name
  d17-features [--kind K]   services.yaml keys, strings.json steps/fields/entities, blueprints; --kind prints
                         the lines of one prefix (KINDS)
  --briefs               the acceptance of a brief that names a universe: every `enumerate.py <universe>`
                         a dev/governance/dimensions/D*.md cites, with its --cells or --pairs, runs
                         non-empty; an unknown universe or a tree citing none is refused
Stdout is the universe only (deterministic, sorted; `wc -l` is its size); a second identical item on
one line gets a ` #2` suffix so no two lines are equal. Diagnostics go to stderr.
Exit 0 on success. Exit 2 with a message on stderr when a source is missing or yields zero items: an
empty universe is a refusal, never a pass.
Null control: --self-test runs every universe on the live tree (>=1 line, sorted, no duplicates), and
per universe plants a fake repo (--repo) whose count it states, deletes one item and reads the count
move, then empties or removes the source and reads the refusal. It prints `SELF-TEST passed (N arms)`
or names the failing arm and exits 1.
"""
import argparse, ast, collections, contextlib, io, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

PKG = "custom_components/heatpump_optimizer"
OBJECTIVE, IDENTITIES, BUNDLES = "dev/audit/config/objective.json", "dev/audit/config/identities.json", "dev/audit/config/bundles.json"
# D16.md's plan states, one axis: (state, the duty mode it runs under). A seat adds rows, never drops one.
STATES = (("idle", "control"), ("min-cold-tank", "control"), ("partial", "control"), ("full", "control"),
          ("dhw-only", "control"), ("both", "control"), ("boost-partial", "control"), ("disinfection", "control"),
          ("baseline", "control"), ("restart", "control"), ("upgrade", "control"), ("unavailable", "control"),
          ("observe", "observe"), ("off", "off"))
# service domains whose calls read and never command an entity
READ_ONLY_DOMAINS = ("weather",)
# d17-features' line prefixes; dev/audit/config/scopes.json's D17 `kind` axis is held equal by check_scopes.py
KINDS = ("service", "config-step", "config-field", "options-step", "option", "entity", "blueprint")
# D0.md step 4's axes; the last two plants are the cells round 10's escapes showed no seat drove
TOPOLOGY, DHW, HORIZON_H = ("single-zone", "two-zone"), ("dhw", "no-dhw"), (6, 24, 48)
PLANT = ("plain", "valve-storage", "wood", "manual-valve-buffer", "flow-setpoint-behind-valve")
USER_PLATFORMS = ("switch", "button", "climate", "datetime", "number", "select")
LIFE_CALLS = {"async_call_later", "async_on_unload", "async_create_task", "async_create_background_task",
              "async_add_executor_job", "async_listen", "async_listen_once", "add_update_listener"}
ENTRY_FNS = ("async_setup", "async_setup_entry", "async_unload_entry", "async_remove_entry",
             "async_migrate_entry", "async_update_options")
# D1.md step 4's solve-thread entries, D9.md's solver entry, and what counts as a retained collection
SOLVE_FNS, SOLVER_ENTRY = ("_solve_record", "_solve_hubs"), "_multi_start_minimize"
CONTAINERS = {"dict", "list", "set", "deque", "defaultdict", "OrderedDict", "Counter"}
# decision 0018 section 1: the four sources that examine a generality cell
SOURCES = ("simulation", "bundle", "install-report", "property-test")


class Refuse(Exception):
    pass


def pkg_files(repo):
    return sorted((repo / PKG).glob("*.py"))


def rel(repo, p):
    return p.relative_to(repo).as_posix()


def parse(p):
    return ast.parse(p.read_text())  # a missing source is an OSError, which run() refuses


def scoped(tree):
    """Like walk, but a def/class node's children see the def's dotted name."""
    def go(node, q):
        for c in ast.iter_child_nodes(node):
            yield c, q
            if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                yield from go(c, c.name if q == "<module>" else f"{q}.{c.name}")
            else:
                yield from go(c, q)
    yield from go(tree, "<module>")


def fname(call):
    f = call.func
    return f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""


def const_assign(tree, name):
    """The value node of a module-level `name = ...` / `name: T = ...`, or None."""
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets):
            return n.value
        if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.target.id == name and n.value:
            return n.value


def d16(repo, cells=False, **_):
    out = []
    for p in pkg_files(repo):
        tree = parse(p)
        calls = {id(n.func): n for n in ast.walk(tree) if isinstance(n, ast.Call)}
        for n, q in scoped(tree):
            if isinstance(n, ast.Attribute) and n.attr == "async_call" and isinstance(n.value, ast.Attribute) and n.value.attr == "services":
                # a reference handed on uncalled is a writer too: its domain is whatever the receiver passes
                c = calls.get(id(n))
                arg = c and (c.args[0] if c.args else next((k.value for k in c.keywords if k.arg == "domain"), None))
                dom = arg.value if isinstance(arg, ast.Constant) and isinstance(arg.value, str) else "?"
                if dom not in READ_ONLY_DOMAINS:
                    out.append(f"write {rel(repo, p)}:{n.lineno} {q} domain={dom}")
            if isinstance(n, ast.Call) and fname(n) == "log_held":
                out.append(f"hold {rel(repo, p)}:{n.lineno} {q}")
    if cells:
        v = const_assign(parse(repo / PKG / "const.py"), "PUMP_DUTY_MODES")
        modes, named = {e.value for e in getattr(v, "elts", []) if isinstance(e, ast.Constant)}, {d for _, d in STATES}
        if modes != named:
            raise Refuse(f"const.py PUMP_DUTY_MODES {sorted(modes)} are not the duty modes STATES names {sorted(named)}: "
                         "a duty mode with no plan state is unrowed, and a state under no duty mode cannot run")
        out = [f"{s} | {name}" for s in out for name, _ in STATES]
    return out


def d17(repo, kind=None, **_):
    out, base = [], repo / PKG
    out += [f"service {m}" for m in re.findall(r"^([a-z_]+):", (base / "services.yaml").read_text(), re.M)]
    s = json.loads((base / "strings.json").read_text())
    for sec, kstep, kfield in (("config", "config-step", "config-field"), ("options", "options-step", "option")):
        for step, body in s.get(sec, {}).get("step", {}).items():
            out.append(f"{kstep} {step}")
            out += [f"{kfield} {step}.{k}" for k in (body.get("data") or {})]
    ent = s.get("entity", {})
    out += [f"entity {pl}.{k}" for pl in USER_PLATFORMS for k in ent.get(pl, {})]
    out += [f"blueprint {b}" for b in sorted(tracked(repo)) if b.startswith("blueprints/")]
    stray = sorted({l.split(" ", 1)[0] for l in out} - set(KINDS))
    if stray:
        raise Refuse(f"d17-features prints a prefix KINDS does not name: {stray}")
    return [l for l in out if not kind or l.split(" ", 1)[0] == kind]


def d14(repo, status=None, **_):
    p = repo / "dev/audit/config/bugclasses.json"
    return [f"{v['status']} {v.get('kind', '?')} {k}" for k, v in json.loads(p.read_text()).items()
            if isinstance(v, dict) and "status" in v and status in (None, v["status"])]


def d0grid(repo, plane=None, **_):
    tree = parse(repo / "tests/profiles.py")
    lits = {}
    for fn in ("prices", "weather"):
        lits[fn] = sorted({c.value for f in ast.walk(tree) if isinstance(f, ast.FunctionDef) and f.name == fn
                           for n in ast.walk(f) if isinstance(n, ast.Compare) and isinstance(n.left, ast.Name)
                           and n.left.id == "profile" for c in n.comparators if isinstance(c, ast.Constant)})
    pw = [f"{a}/{b}" for a in lits["prices"] for b in lits["weather"]]
    if plane == "price-weather":
        return pw
    return [f"{x}/{t}/{d}/{pl}/{h}h" for x in pw for t in TOPOLOGY for d in DHW for pl in PLANT for h in HORIZON_H]


def imports(path, base):
    out = set()
    for n in ast.walk(parse(path)):
        names = []
        if isinstance(n, ast.ImportFrom):
            if n.level == 1 and n.module:
                names = [n.module.split(".")[0]]
            elif n.level == 1:
                names = [a.name for a in n.names]
            elif n.level == 0 and n.module and n.module.startswith(PKG.replace("/", ".")):
                tail = n.module[len(PKG):].lstrip(".")
                names = [tail.split(".")[0]] if tail else [a.name for a in n.names]
        elif isinstance(n, ast.Import):
            names = [a.name[len(PKG) + 1:].split(".")[0] for a in n.names if a.name.startswith(PKG.replace("/", ".") + ".")]
        out |= {x for x in names if (base / f"{x}.py").is_file()}
    return out


def d0modules(repo, **_):
    base = repo / PKG
    seen, todo = set(), ["optimizer", "dhw_planner"]
    while todo:
        m = todo.pop()
        if m not in seen:
            seen.add(m)
            todo += sorted(imports(base / f"{m}.py", base))
    if not (base / "coordinator.py").is_file():
        raise Refuse(f"missing source {base / 'coordinator.py'}")
    return [f"{PKG}/{m}.py" for m in seen | {"coordinator"}]


def d1stores(repo, **_):
    out = []
    st = parse(repo / PKG / "store.py")
    d = const_assign(st, "DOMAINS")
    if not isinstance(d, ast.Dict):
        raise Refuse("no DOMAINS dict literal in store.py")
    for k in d.keys:
        if isinstance(k, ast.Constant):
            out.append(f"store {k.value}")
        elif isinstance(k, ast.Name):
            v = const_assign(st, k.id)
            out.append(f"store {v.value if isinstance(v, ast.Constant) else k.id}")
    for p in pkg_files(repo):
        r = rel(repo, p)
        for n in parse(p).body:
            tg = n.targets[0] if isinstance(n, ast.Assign) and len(n.targets) == 1 else getattr(n, "target", None)
            if isinstance(n, (ast.Assign, ast.AnnAssign)) and isinstance(tg, ast.Name) and isinstance(n.value, ast.Constant) \
                    and type(n.value.value) is int and (tg.id.endswith("STORE_VERSION") or (tg.id == "CONFIG_ENTRY_VERSION" and p.name == "const.py")):
                v = n.value.value
                out += [f"upgrade {r}:{tg.id} v{k}->{v}" for k in range(1, v)] or [f"upgrade {r}:{tg.id} v{v} (no earlier version)"]
    return out


def d1excepts(repo, **_):
    out = []
    for p in pkg_files(repo):
        for n, q in scoped(parse(p)):
            if isinstance(n, ast.ExceptHandler):
                ts = n.type.elts if isinstance(n.type, ast.Tuple) else [n.type]
                broad = n.type is None or any(isinstance(t, ast.Name) and t.id in ("Exception", "BaseException") for t in ts)
                out.append(f"{rel(repo, p)}:{n.lineno} {'broad' if broad else 'narrow'} {q}")
    return out


def d1life(repo, **_):
    out = []
    for p in pkg_files(repo):
        t = parse(p)
        for n, q in scoped(t):
            if isinstance(n, ast.Call):
                k = fname(n)
                if k.startswith("async_track_") or k in LIFE_CALLS:
                    out.append(f"{k} {rel(repo, p)}:{n.lineno} {q}")
        if p.name == "__init__.py":
            out += [f"entry {n.name}" for n in t.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in ENTRY_FNS]
    return out


def d3(repo, state=None, by_file=False, ast_only=False, **_):
    rows = []  # (file, "file:line kind", state)
    if ast_only:
        for p in pkg_files(repo):
            for n, _q in scoped(parse(p)):
                k = ("if" if isinstance(n, ast.If) else "ifexp" if isinstance(n, ast.IfExp) else "except" if isinstance(n, ast.ExceptHandler)
                     else "minmax" if isinstance(n, ast.Call) and fname(n) in ("min", "max", "clip") else None)
                if k:
                    rows.append((rel(repo, p), f"{rel(repo, p)}:{n.lineno} {k}", None))
    else:
        mt = repo / "tests/mutation_table.py"
        if not mt.is_file():
            raise Refuse(f"missing source {mt} (use --ast for the ledger-free fallback)")
        sys.path.append(str(repo / "tests"))
        with contextlib.redirect_stdout(sys.stderr):
            import mutation_table as m
            b, inv = m.load_budgets(), m.inventory()
        kb, tr = b.get("killed_by", {}), b.get("survivor_triage", {})
        for s in inv:
            a = s["anchor"]
            st = "killed" if m.disposition_matches(kb.get(a), s) else "triaged" if m.disposition_matches(tr.get(a), s) else "unrecorded"
            if state in (None, st):
                rows.append((s["file"], f"{s['file']}:{s['line']} {s['kind']}", st))
    if by_file:
        c = collections.Counter(f for f, _l, _s in rows)
        if ast_only:
            return [f"{f} {c[f]}" for f in c]
        return [f"{f} {c[f]} " + " ".join(str(sum(1 for r in rows if r[0] == f and r[2] == s)) for s in ("killed", "triaged", "unrecorded")) for f in c]
    return [f"{l} {s}" if s else l for _f, l, s in rows]



def flow_slots(repo):
    """The keys config_flow.py's `_F` rows offer through an entity selector: a row whose widget is a
    call of EntitySelector or of a def returning one, its key a name or a comprehension's loop name
    over a tuple of names. An entity selector in no such row is refused: the census would be short."""
    t = parse(repo / PKG / "config_flow.py")
    defs = [d for d in ast.walk(t) if isinstance(d, (ast.FunctionDef, ast.AsyncFunctionDef))]
    fac = {d.name for d in defs if any(isinstance(r, ast.Return) and isinstance(r.value, ast.Call)
                                       and fname(r.value) == "EntitySelector" for r in ast.walk(d))}
    inside = {id(n) for d in defs if d.name in fac for n in ast.walk(d)}
    loops = {}  # id(an _F call) -> {loop name: [the tuple's names]}
    for c in ast.walk(t):
        if isinstance(c, (ast.GeneratorExp, ast.ListComp, ast.SetComp)):
            b = {g.target.id: [e.id for e in g.iter.elts] for g in c.generators if isinstance(g.target, ast.Name)
                 and isinstance(g.iter, (ast.Tuple, ast.List)) and all(isinstance(e, ast.Name) for e in g.iter.elts)}
            loops.update({id(n): b for n in ast.walk(c.elt)})
    keys, rows = [], set()
    for n in ast.walk(t):
        if isinstance(n, ast.Call) and fname(n) == "_F":
            a = {**dict(zip(("step", "key", "default", "widget"), n.args)), **{k.arg: k.value for k in n.keywords}}
            w, k = a.get("widget"), a.get("key")
            if isinstance(w, ast.Call) and (fname(w) in fac or fname(w) == "EntitySelector"):
                rows.add(id(w))
                if not isinstance(k, ast.Name):
                    raise Refuse(f"config_flow.py:{n.lineno}: an entity selector row whose key is no name")
                keys += loops.get(id(n), {}).get(k.id) or [k.id]
    for n in ast.walk(t):
        if isinstance(n, ast.Call) and id(n) not in inside and id(n) not in rows and (fname(n) in fac or fname(n) == "EntitySelector"):
            raise Refuse(f"config_flow.py:{n.lineno}: an entity selector outside an `_F` row is in no census")
    return keys


def wiring_slots(repo):
    """The keys entry_config.py's FACTORY_KEPT keeps for the reason its one comprehension gives (an
    entity assignment): the const.py names that comprehension's startswith/endswith tests select,
    and the dict entries FACTORY_KEPT spreads that give the same reason. Another test is refused."""
    t = parse(repo / PKG / "entry_config.py")
    fk = const_assign(t, "FACTORY_KEPT")
    comps = [c for c in ast.walk(fk) if isinstance(c, ast.DictComp)] if fk else []
    if len(comps) != 1 or not isinstance(comps[0].value, ast.Constant) or not isinstance(comps[0].generators[0].target, ast.Tuple):
        raise Refuse("entry_config.py: no FACTORY_KEPT holding one comprehension over (name, key): re-read the entity rule")
    c = comps[0]
    reason, (nv, kv) = c.value.value, [e.id for e in c.generators[0].target.elts]
    tests = []
    for e in [x for i in c.generators[0].ifs for x in (i.values if isinstance(i, ast.BoolOp) else [i])]:
        if isinstance(e, ast.Call) and fname(e) == "isinstance" and getattr(e.args[0], "id", None) == kv:
            continue
        if not (isinstance(e, ast.Call) and fname(e) in ("startswith", "endswith") and isinstance(e.func.value, ast.Name)
                and e.func.value.id in (nv, kv) and len(e.args) == 1 and isinstance(e.args[0], ast.Constant)):
            raise Refuse(f"entry_config.py:{e.lineno}: FACTORY_KEPT's entity rule holds a test this census cannot read")
        tests.append((e.func.value.id == nv, fname(e), e.args[0].value))
    keys = []
    for n in parse(repo / PKG / "const.py").body:
        tg = n.targets[0] if isinstance(n, ast.Assign) and len(n.targets) == 1 else getattr(n, "target", None)
        v = getattr(n, "value", None)
        if isinstance(tg, ast.Name) and isinstance(v, ast.Constant) and isinstance(v.value, str) \
                and all(getattr(tg.id if on_name else v.value, how)(arg) for on_name, how, arg in tests):
            keys.append(tg.id)
    for d in [x for x in ast.walk(fk) if isinstance(x, ast.Dict)]:
        for k, v in zip(d.keys, d.values):
            src = const_assign(t, v.id) if k is None and isinstance(v, ast.Name) else None
            pairs = zip(src.keys, src.values) if isinstance(src, ast.Dict) else [(k, v)] if k is not None else []
            keys += [kk.attr if isinstance(kk, ast.Attribute) else kk.id for kk, vv in pairs
                     if isinstance(kk, (ast.Attribute, ast.Name)) and isinstance(vv, ast.Constant) and vv.value == reason]
    return keys


def d1inputs(repo, **_):
    """Step 3's inputs: every configured entity slot, by what the code treats as one: a key the
    options flow offers through an entity selector, or one a factory reset keeps as an entity
    assignment. A key in both prints once."""
    return [f"input {k}" for k in sorted(set(flow_slots(repo)) | set(wiring_slots(repo)))]


def d1solve(repo, **_):
    """Step 4's reads: every `self.<attr>` the solve-thread entry functions touch."""
    out, found = set(), set()
    for n, _q in scoped(parse(repo / PKG / "coordinator.py")):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in SOLVE_FNS:
            found.add(n.name)
            out |= {f"{n.name} self.{a.attr}" for a in ast.walk(n)
                    if isinstance(a, ast.Attribute) and isinstance(a.value, ast.Name) and a.value.id == "self"}
    if set(SOLVE_FNS) - found:
        raise Refuse(f"coordinator.py lacks {sorted(set(SOLVE_FNS) - found)}: the solve-thread entry moved, re-point SOLVE_FNS")
    return sorted(out)


def d1parsers(repo, **_):
    """Step 6's parsers: a def whose name holds `parse`, and each json.loads / .json() / async_subscribe site."""
    out = []
    for p in pkg_files(repo):
        for n, q in scoped(parse(p)):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and "parse" in n.name:
                out.append(f"def {rel(repo, p)}:{n.lineno} {n.name}")
            if isinstance(n, ast.Call):
                f, k = n.func, fname(n)
                if k == "loads" and isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id == "json":
                    out.append(f"json {rel(repo, p)}:{n.lineno} {q}")
                elif k == "json" and isinstance(f, ast.Attribute) and not n.args:
                    out.append(f"response {rel(repo, p)}:{n.lineno} {q}")
                elif k == "async_subscribe":
                    out.append(f"subscribe {rel(repo, p)}:{n.lineno} {q}")
    return out


def tracked(repo):
    r = subprocess.run(["git", "ls-files"], cwd=repo, capture_output=True, text=True)
    fs = r.stdout.split("\n") if r.returncode == 0 and (repo / ".git").exists() else []
    return {f for f in fs if f} or {rel(repo, Path(d) / f) for d, _, names in os.walk(repo) for f in names}


def population_axes(repo):
    """{axis: [levels]} as `check_scopes.py --population` reads them, by its own reader, and the
    two totals it prints; a binary axis key is its own axis with levels present and absent. An
    axis it prints NO-READ is an axis all the same once its row declares `levels` (the continuous
    ones: no source holds them), and both totals are raised by what those levels add."""
    obj = repo / OBJECTIVE
    sys.path.append(str(Path(__file__).resolve().parent))
    import check_scopes
    spec = json.loads(obj.read_text()).get("population", [])
    lines, ok = check_scopes.population(spec, tracked(repo), lambda f: (repo / f).read_text())
    if not ok:
        raise Refuse("the population is unreadable: " + "; ".join(l for l in lines if l.startswith("UNREADABLE")))
    declared = {a.get("axis"): [str(k) for k in a["levels"]] for a in spec if a.get("levels")}
    axes, totals, added = {}, {}, []
    for l in lines:
        if "\t" not in l:
            k, _, v = l.partition(": ")
            totals[k] = int(v)
            continue
        name, _, rest = l.partition("\t")
        n, _, lv = rest.partition("\t")
        if n == "NO-READ" and name in declared:
            axes[name] = declared[name]
            added.append(len(declared[name]))
            print(f"NO-READ axis {name}: its cells are the levels {OBJECTIVE} declares, which no reader compares with their source", file=sys.stderr)
        elif n == "NO-READ":
            print(f"NO-READ axis {name}: no cell until {OBJECTIVE} declares its levels", file=sys.stderr)
        elif n.endswith("binary axes"):
            axes.update({k: ["absent", "present"] for k in lv.split(",")})
        else:
            axes[name] = lv.split(",")
    totals["PAIRS"] += totals["LEVELS"] * sum(added) + (sum(added) ** 2 - sum(n * n for n in added)) // 2
    totals["LEVELS"] += sum(added)
    return axes, totals


def golden_scenarios(repo):
    v = const_assign(parse(repo / "tests/golden.py"), "SCENARIOS")
    return [k.value for k in getattr(v, "keys", []) if isinstance(k, ast.Constant)]


def d2(repo, cells=False, **_):
    """The identity register, one line per identity, or under --cells one per identity and
    grid cell. A grid axis is a population axis by name, `golden` (tests/golden.py SCENARIOS),
    or an inline {"axis", "levels"} the register states because no source holds it."""
    p = repo / IDENTITIES
    rows, out, pop = json.loads(p.read_text()).get("identities", []), [], None
    for r in rows:
        if not (re.fullmatch(r"M\d+", str(r.get("step"))) and r.get("id") and r.get("identity") and r.get("grid")):
            raise Refuse(f"{IDENTITIES}: an identity needs step, id, identity and a non-empty grid: {r}")
        grid = []
        for g in r["grid"]:
            if isinstance(g, dict):
                name, lv = g.get("axis"), g.get("levels")
            elif g == "golden":
                name, lv = g, golden_scenarios(repo)
            else:
                pop = pop or population_axes(repo)[0]
                name, lv = g, pop.get(g)
            if not lv:
                raise Refuse(f"{IDENTITIES}: identity {r['id']} names grid axis {name!r}, which has no level")
            grid.append((name, lv))
        if not cells:
            out.append(f"{r['step']} {r['id']} grid=" + "x".join(n for n, _ in grid))
            continue
        combos = [[]]
        for name, lv in grid:
            combos = [c + [f"{name}={x}"] for c in combos for x in lv]
        out += [f"{r['step']} {r['id']} | " + " ".join(c) for c in combos]
    return out


def d8(repo, **_):
    """Entity by state by language: every name, state, attribute and attribute state strings.json
    declares under `entity`, once per translation file (a file lacking the key is still a cell)."""
    sj, tr = repo / PKG / "strings.json", repo / PKG / "translations"
    langs = sorted(f.stem for f in tr.glob("*.json"))  # no translation file is no cell, which run() refuses
    facets = []
    for pl, ents in json.loads(sj.read_text()).get("entity", {}).items():
        for k, body in ents.items():
            facets.append(f"{pl}.{k} name")
            facets += [f"{pl}.{k} state={s}" for s in body.get("state", {})]
            for a, ab in body.get("state_attributes", {}).items():
                facets.append(f"{pl}.{k} attr={a}")
                facets += [f"{pl}.{k} attr={a}:state={s}" for s in (ab.get("state", {}) if isinstance(ab, dict) else {})]
    return [f"{lang} {f}" for f in facets for lang in langs]


def d9collections(repo, **_):
    """Every `self.<attr>` of a coordinator.py class bound to a container literal, comprehension
    or constructor, once per class and attribute, at its first binding."""
    first = {}
    for n, q in scoped(parse(repo / PKG / "coordinator.py")):
        tg = n.targets if isinstance(n, ast.Assign) else [n.target] if isinstance(n, ast.AnnAssign) and n.value else []
        v = getattr(n, "value", None)
        kind = ({ast.Dict: "dict", ast.List: "list", ast.Set: "set", ast.DictComp: "dict", ast.ListComp: "list", ast.SetComp: "set"}.get(type(v))
                or (fname(v) if isinstance(v, ast.Call) and fname(v) in CONTAINERS else None))
        for t in tg:
            if kind and isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == "self" and "." in q:
                first.setdefault(f"{q.split('.')[0]}.{t.attr}", f"{kind} {PKG}/coordinator.py:{n.lineno}")
    return [f"{k} {v}" for k, v in first.items()]


def d9attributes(repo, **_):
    """Every class that publishes attributes: one defining or assigning `extra_state_attributes`."""
    out = []
    for p in pkg_files(repo):
        for c in ast.walk(parse(p)):
            if isinstance(c, ast.ClassDef) and any(
                    (isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name == "extra_state_attributes")
                    or (isinstance(m, (ast.Assign, ast.AnnAssign)) and any(isinstance(t, ast.Name) and t.id == "_attr_extra_state_attributes"
                                                                          for t in (m.targets if isinstance(m, ast.Assign) else [m.target])))
                    for m in c.body):
                out.append(f"{rel(repo, p)}:{c.lineno} {c.name}")
    return out


def d9solves(repo, **_):
    """The solve paths: each call of SOLVER_ENTRY, then each call of, or bare reference to (a
    function handed to an executor is never called by name), a function that holds one, upward
    by name inside the solver's own module; a site in another module is an entry into the
    solver, printed and not climbed (a name shared with an unrelated function stops there)."""
    sites, home = [], None
    for p in pkg_files(repo):
        t = parse(p)
        if any(isinstance(n, ast.FunctionDef) and n.name == SOLVER_ENTRY for n in t.body):
            home = rel(repo, p)
        called = {id(n.func) for n in ast.walk(t) if isinstance(n, ast.Call)}
        for n, q in scoped(t):
            if isinstance(n, ast.Call) and fname(n):
                sites.append((fname(n), "", rel(repo, p), n.lineno, q))
            elif isinstance(n, (ast.Name, ast.Attribute)) and isinstance(n.ctx, ast.Load) and id(n) not in called:
                sites.append((n.id if isinstance(n, ast.Name) else n.attr, " (ref)", rel(repo, p), n.lineno, q))
    names, grown = {SOLVER_ENTRY}, set()
    while names != grown:
        grown = set(names)
        names |= {q.split(".")[-1] for callee, _how, f, _line, q in sites if callee in grown and f == home and q != "<module>"}
    return [f"{'solve' if callee == SOLVER_ENTRY else 'path'} {callee} <- {f}:{line} {q}{how}" for callee, how, f, line, q in sites if callee in names]


def d12(repo, pairs=False, **_):
    """The generality cells: every level `--population` reads, the card and each blueprint,
    and under --pairs every pair of levels from two axes. The level and pair counts are asserted
    against the command's own."""
    axes, totals = population_axes(repo)
    cells = [f"level {a}={x}" for a, lv in axes.items() for x in lv]
    if len(cells) != totals.get("LEVELS"):
        raise Refuse(f"{len(cells)} level cells against the population's LEVELS: {totals.get('LEVELS')}")
    names = sorted(axes)
    if pairs:
        pc = [f"pair {a}={x} & {b}={y}" for i, a in enumerate(names) for b in names[i + 1:] for x in axes[a] for y in axes[b]]
        if len(pc) != totals.get("PAIRS"):
            raise Refuse(f"{len(pc)} pair cells against the population's PAIRS: {totals.get('PAIRS')}")
        cells += pc
    surf = [f"surface card {f}" for f in sorted(tracked(repo)) if f.startswith(f"{PKG}/www/") and f.endswith(".js")]
    surf += [f"surface blueprint {f}" for f in sorted(tracked(repo)) if f.startswith("blueprints/")]
    if not surf:
        raise Refuse("no card and no blueprint is tracked")
    return cells + surf


def d15(repo, **_):
    """The installs that sent a bundle, one line per bundle: its date, the round that read it and
    the steps run on it. A round's examined count is its own lines; the universe is every line."""
    p = repo / BUNDLES
    out = []
    for b in json.loads(p.read_text()).get("bundles", []):
        if not (b.get("install") and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(b.get("date"))) and isinstance(b.get("round"), int)
                and isinstance(b.get("steps"), list) and b.get("evidence")):
            raise Refuse(f"{BUNDLES}: a bundle needs install, date (YYYY-MM-DD), round, steps and evidence: {b}")
        if not (repo / b["evidence"]).exists():
            raise Refuse(f"{BUNDLES}: evidence {b['evidence']} of {b['install']} {b['date']} is not in the tree")
        out.append(f"{b['install']} {b['date']} round={b['round']} steps={','.join(b['steps']) or 'none'}")
    return out


UNIVERSES = {"d16-writes": d16, "d17-features": d17, "d14-classes": d14, "d0-grid": d0grid, "d0-modules": d0modules,
             "d1-stores": d1stores, "d1-excepts": d1excepts, "d1-lifecycle": d1life, "d1-inputs": d1inputs,
             "d1-solve-state": d1solve, "d1-parsers": d1parsers, "d2-identities": d2, "d3-sites": d3, "d8-cells": d8,
             "d9-collections": d9collections, "d9-attributes": d9attributes, "d9-solves": d9solves,
             "d12-cells": d12, "d15-installs": d15}


def joined(name, items, ledger):
    """Each item beside its ledger row, or `not run`: the census with the test that drives each
    line. A row is item and asserting test, tab-separated; a generality cell also names, between
    them, which of decision 0018's four sources examined it, and prints `not run` with no ledger."""
    cell = name == "d12-cells"
    if not ledger and not cell:
        return items
    rows = {}
    for i, l in enumerate(Path(ledger).read_text().splitlines() if ledger else (), 1):
        c = [x.strip() for x in l.split("\t")]
        if not l.strip() or l.startswith("#"):
            continue
        if len(c) != 2 + cell or not c[-1] or (cell and c[1] not in SOURCES):
            raise Refuse(f"{ledger}:{i}: a row is the item, " + (f"its source ({', '.join(SOURCES)}), " if cell else "")
                         + "and its asserting test, tab-separated; a run that asserts nothing examines nothing")
        if c[0] not in items:
            raise Refuse(f"{ledger}:{i}: {c[0]!r} is no item of this universe as printed (check its options)")
        rows[c[0]] = "\t".join(c[1:])
    return [f"{x}\t{rows.get(x, 'not run')}" for x in items]


def run(name, repo, ledger=None, **kw):
    try:
        lines = joined(name, sorted(_dedupe(UNIVERSES[name](Path(repo), **kw))), ledger)
    except OSError as e:
        raise Refuse(f"missing or unreadable source: {e}")
    if not lines:
        raise Refuse(f"{name} yields zero items: an empty universe is a refusal")
    return lines


def _dedupe(lines):
    seen = collections.Counter()
    for l in lines:
        seen[l] += 1
        yield l if seen[l] == 1 else f"{l} #{seen[l]}"


def briefs(repo):
    """One `ok` line per (brief, cited command); Refuse on a citation that names no universe,
    one whose universe refuses, or a tree whose briefs cite none."""
    out, bad = [], []
    for f in sorted((repo / "dev/governance/dimensions").glob("D*.md")):
        text = re.sub(r"\s+", " ", f.read_text())
        for u, flags in sorted(set(re.findall(r"enumerate\.py (d\d+-[a-z-]+)((?: --(?:cells|pairs))*)", text))):
            opt = {k: True for k in re.findall(r"--(cells|pairs)", flags)}
            try:
                if u not in UNIVERSES:
                    raise Refuse("no such universe")
                with contextlib.redirect_stderr(io.StringIO()):
                    run(u, repo, **opt)
                out.append(f"ok {f.stem} {u}{flags}")
            except Refuse as e:
                bad.append(f"{f.stem} cites `enumerate.py {u}{flags}`: {e}")
    if bad or not out:
        raise Refuse("; ".join(bad) or "no dimension brief cites a universe")
    return out


def plant(root):
    P = root / PKG
    for d in ("tests", "dev/audit/config", "blueprints/automation", f"{PKG}/translations", f"{PKG}/www"):
        (root / d).mkdir(parents=True)
    w = lambda p, t: (root / p).write_text(t)
    w(f"{PKG}/x.py", "def f(hass):\n" + "    hass.services.async_call('a', 'b')\n" * 2 + "    log_held('x')\n"
      "    try:\n        pass\n    except Exception:\n        pass\n    except ValueError:\n        pass\n"
      "    async_track_time_interval(1)\n    hass.async_create_task(1)\n    hass.helpers.async_call('c')\n"
      "    y = min(1, 2) if hass else 0\n    if y:\n        pass\n")
    w(f"{PKG}/p.py", "import json\ndef parse_a(x):\n    return json.loads(x)\nasync def g(r, m):\n    await r.json()\n    r.json('k')\n"
      "    await m.async_subscribe('t')\n")
    w(f"{PKG}/e.py", "class E:\n    @property\n    def extra_state_attributes(self):\n        return {}\nclass F:\n    _attr_extra_state_attributes = {}\nclass G:\n    pass\ndef use(c):\n    return c.cycle()\n")
    w(f"{PKG}/const.py", "PUMP_DUTY_MODES: Final = ('off', 'observe', 'control')\nCONFIG_ENTRY_VERSION: Final = 3\n"
      "CONF_A_ENTITY = 'a_entity'\nCONF_B_ENTITY: Final = 'b_entity'\nCONF_F_SENSOR = 'f_sensor'\nCONF_H1 = 'h1'\nCONF_H2 = 'h2'\n"
      "CONF_W_SENSOR = 'w_sensor'\nCONF_NAME = 'n'\nX_ENTITY = 'x_entity'\nMODES = ('m1', 'm2')\n")
    w(f"{PKG}/config_flow.py", "def _entity_of(d):\n    return selector.EntitySelector(d)\ndef _text():\n    return selector.TextSelector()\n"
      "ROWS = (\n    _F('s', CONF_A_ENTITY, '', _entity_of('sensor')),\n    _F('s', CONF_F_SENSOR, '', widget=_entity_of('sensor')),\n"
      "    *(_F('s', key, '', _entity_of('number')) for key in (CONF_H1, CONF_H2)),\n    _F('s', CONF_NAME, '', _text()),\n)\n")
    w(f"{PKG}/entry_config.py", "_WIRING: dict = {const.CONF_W_SENSOR: 'an entity assignment', const.CONF_NAME: 'the name'}\n"
      "FACTORY_KEPT = MappingProxyType({**{key: 'an entity assignment' for name, key in vars(const).items()\n"
      "    if name.startswith('CONF_') and isinstance(key, str) and key.endswith('_entity')}, **_WIRING})\n")
    w(f"{PKG}/store.py", "K = 'b'\nDOMAINS = {'a': {}, K: {}}\nLEDGER_STORE_VERSION = 2\nMAP_STORE_VERSION: Final = 1\n")
    w(f"{PKG}/__init__.py", "".join(f"async def {f}(h, e):\n    pass\n" for f in ENTRY) + "def helper():\n    pass\n")
    w(f"{PKG}/optimizer.py", "from .y import z\nfrom . import w\ndef _multi_start_minimize():\n    pass\ndef go(c):\n    return _multi_start_minimize() or go(c)\n")
    w(f"{PKG}/y.py", "from custom_components.heatpump_optimizer.v import q\nimport custom_components.heatpump_optimizer.u\n"
      "from custom_components.heatpump_optimizer import t\n")
    w(f"{PKG}/coordinator.py", "class C:\n    def __init__(self):\n        self.a = {}\n        self.b = deque(maxlen=3)\n        self.c = 0\n        self.a = {}\n"
      "    def _solve_record(self):\n        return self.a, self.c\n    def _solve_hubs(self):\n        return self.b\n    def cycle(self):\n        return go(self)\n    def held(self):\n        return submit(go)\n"
      "def helper(self):\n    self.z = {}\n")
    for n in ("w", "v", "u", "t", "dhw_planner"):
        w(f"{PKG}/{n}.py", "")
    w(f"{PKG}/services.yaml", "set_a:\n  fields: {}\nset_b:\n")
    w(f"{PKG}/strings.json", json.dumps({"config": {"step": {"user": {"data": {"f1": "", "f2": ""}}}},
                                         "options": {"step": {"init": {"data": {"o1": ""}}}},
                                         "entity": {"switch": {"s1": {}}, "sensor": {"z": {"state": {"on": "", "off": ""}, "state_attributes": {"k": {"state": {"u": ""}}}}}}}))
    w(f"{PKG}/translations/en.json", "{}"), w(f"{PKG}/translations/sv.json", "{}"), w(f"{PKG}/www/card.js", "")
    w("blueprints/automation/b.yaml", "")
    w("tests/profiles.py", "def prices(profile, s):\n    if profile == 'p1':\n        pass\n    elif profile == 'p2':\n        pass\n"
      "def weather(profile, s):\n    if profile == 'w1':\n        pass\n")
    w("tests/golden.py", "SCENARIOS: dict = {'g1': dict(), 'g2': dict()}\n")
    w("dev/audit/config/bugclasses.json", json.dumps({"_note": "x", "A": {"status": "open", "kind": "production"},
                                                       "B": {"status": "barriered", "kind": "instrument"}}))
    w(OBJECTIVE, json.dumps({"population": [{"axis": "mode", "kind": "tuple", "file": f"{PKG}/const.py", "symbol": "MODES"},
                                            {"axis": "price_shape", "kind": "compare", "file": "tests/profiles.py", "function": "prices", "argument": "profile"},
                                            {"axis": "size", "kind": None, "no_read": "r", "builder": "G"}]}))
    w(IDENTITIES, json.dumps({"identities": [{"step": "M1", "id": "i1", "identity": "x", "grid": ["mode"]},
                                             {"step": "M3", "id": "i2", "identity": "y", "grid": ["golden", {"axis": "noise", "levels": ["a", "b", "c"]}]}]}))
    plant_bundles(root)


def plant_bundles(root):
    (root / BUNDLES).write_text(json.dumps({"bundles": [{"install": f"i{k}", "date": "2026-01-02", "round": 1, "steps": ["M1"], "evidence": "tests/profiles.py"} for k in (1, 2)]}))


def cut(path, old, new=""):
    """An edit of the planted repo that refuses to match nothing."""
    def go(root):
        t = (root / path).read_text()
        if old not in t:
            raise AssertionError(f"self-test edit of {path} matched nothing: {old!r}")
        (root / path).write_text(t.replace(old, new, 1))
    return go


def put(path, text):
    return lambda root: (root / path).write_text(text)


def rm(*paths):
    return lambda root: [(root / p).unlink() for p in paths]


def both(*fs):
    return lambda root: [f(root) for f in fs]


def edit_json(path, fn):
    def go(root):
        d = json.loads((root / path).read_text())
        fn(d)
        (root / path).write_text(json.dumps(d))
    return go


X, CO, CF = f"{PKG}/x.py", f"{PKG}/coordinator.py", f"{PKG}/config_flow.py"
DUTY = "PUMP_DUTY_MODES: Final = ('off', 'observe', 'control')\n"
# the entry points the planted __init__.py defines, typed apart from ENTRY_FNS so a dropped one shows
ENTRY = ("async_setup", "async_setup_entry", "async_unload_entry", "async_remove_entry", "async_migrate_entry", "async_update_options")
# universe, options, the planted count, the edit deleting one item, the count after it, the edit emptying the source
PLANTED = [
    ("d0-grid", {}, 2 * 1 * 2 * 2 * 5 * 3, cut("tests/profiles.py", "    elif profile == 'p2':\n        pass\n"), 60,
     put("tests/profiles.py", "def prices(profile, s):\n    pass\ndef weather(profile, s):\n    pass\n")),
    ("d0-modules", {}, 8, cut(f"{PKG}/y.py", "import custom_components.heatpump_optimizer.u\n"), 7, rm(f"{PKG}/optimizer.py")),
    ("d1-lifecycle", {}, 2 + len(ENTRY), cut(X, "    async_track_time_interval(1)\n"), 1 + len(ENTRY), both(put(X, ""), put(f"{PKG}/__init__.py", ""))),
    ("d1-stores", {}, 6, cut(f"{PKG}/store.py", ", K: {}"), 5, put(f"{PKG}/store.py", "")),
    ("d1-inputs", {}, 6, cut(CF, "    _F('s', CONF_F_SENSOR, '', widget=_entity_of('sensor')),\n"), 5,
     both(put(CF, ""), put(f"{PKG}/entry_config.py", "FACTORY_KEPT = {}\n"))),
    ("d1-solve-state", {}, 3, cut(CO, "return self.a, self.c", "return self.a"), 2, put(CO, "")),
    ("d1-excepts", {}, 2, cut(X, "    except ValueError:\n        pass\n"), 1, put(X, "")),
    ("d1-parsers", {}, 4, cut(f"{PKG}/p.py", "    await m.async_subscribe('t')\n"), 3, put(f"{PKG}/p.py", "")),
    ("d2-identities", {}, 2, edit_json(IDENTITIES, lambda d: d["identities"].pop()), 1, edit_json(IDENTITIES, lambda d: d["identities"].clear())),
    ("d2-identities", {"cells": True}, 2 + 2 * 3, cut("tests/golden.py", ", 'g2': dict()"), 2 + 1 * 3, put("tests/golden.py", "SCENARIOS = {}\n")),
    ("d3-sites", {"ast_only": True}, 5, cut(X, "    except ValueError:\n        pass\n"), 4, put(X, "")),
    ("d8-cells", {}, 6 * 2, rm(f"{PKG}/translations/sv.json"), 6, rm(f"{PKG}/translations/sv.json", f"{PKG}/translations/en.json")),
    ("d9-collections", {}, 2, cut(CO, "self.b = deque(maxlen=3)", "self.b = None"), 1, put(CO, "")),
    ("d9-attributes", {}, 2, cut(f"{PKG}/e.py", "    _attr_extra_state_attributes = {}", "    pass"), 1, put(f"{PKG}/e.py", "")),
    ("d9-solves", {}, 4, cut(CO, "return submit(go)", "return None"), 3, cut(f"{PKG}/optimizer.py", "return _multi_start_minimize() or go(c)", "return None")),
    ("d12-cells", {}, 4 + 2, rm("blueprints/automation/b.yaml"), 5, rm(OBJECTIVE)),
    ("d12-cells", {"pairs": True}, 4 + 4 + 2, cut(f"{PKG}/const.py", "MODES = ('m1', 'm2')", "MODES = ('m1',)"), 3 + 2 + 2,
     rm("blueprints/automation/b.yaml", f"{PKG}/www/card.js")),
    ("d14-classes", {}, 2, edit_json("dev/audit/config/bugclasses.json", lambda d: d.pop("B")), 1, put("dev/audit/config/bugclasses.json", "{}")),
    ("d15-installs", {}, 2, edit_json(BUNDLES, lambda d: d["bundles"].pop()), 1, edit_json(BUNDLES, lambda d: d["bundles"].clear())),
    ("d16-writes", {}, 3, cut(X, "    hass.services.async_call('a', 'b')\n"), 2, put(X, "")),
    ("d16-writes", {"cells": True}, 3 * len(STATES), cut(X, "    log_held('x')\n"), 2 * len(STATES), cut(f"{PKG}/const.py", DUTY)),
    ("d17-features", {}, 9, cut(f"{PKG}/services.yaml", "set_b:\n"), 8,
     both(put(f"{PKG}/services.yaml", ""), put(f"{PKG}/strings.json", "{}"), rm("blueprints/automation/b.yaml"))),
]


def self_test():
    arms, fails = 0, []

    def arm(name, got, want):
        nonlocal arms
        arms += 1
        if got != want:
            fails.append(f"{name}: got {got!r}, want {want!r}")

    def count(u, t, **opt):
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                return len(run(u, t, **opt))
        except Refuse:
            return "Refuse"

    live = Path(".")
    for u in UNIVERSES:
        for opt in ({}, *[o for n, o, *_ in PLANTED if n == u and o and "ast_only" not in o], *([{"plane": "price-weather"}] if u == "d0-grid" else [])):
            try:
                with contextlib.redirect_stderr(io.StringIO()):
                    ls = run(u, live, **opt)
            except Refuse as e:
                ls = []
                fails.append(f"live {u} {opt}: {e}")
            arm(f"live {u} {opt}", (len(ls) >= 1, ls == sorted(ls), len(ls) == len(set(ls))), (True, True, True))
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            d3_all = run("d3-sites", live)
            by_state = {st: run("d3-sites", live, state=st) for st in ("killed", "triaged", "unrecorded") if any(l.split(" #")[0].endswith(" " + st) for l in d3_all)}
            by_file = [l.split() for l in run("d3-sites", live, by_file=True)]
        arm("live d3-sites: the --state filters partition the universe", sorted(l for ls in by_state.values() for l in ls), d3_all)
        arm("live d3-sites: each --state filter holds only its state", all(l.split(" #")[0].endswith(" " + st) for st, ls in by_state.items() for l in ls), True)
        arm("live d3-sites --by-file: each file's three state counts sum to its total, and the totals to the universe",
            (all(int(r[1]) == sum(map(int, r[2:5])) for r in by_file), sum(int(r[1]) for r in by_file)), (True, len(d3_all)))
    except Refuse as e:
        fails.append(f"live d3-sites options: {e}")
    try:
        arm("live briefs", len(briefs(live)) >= 1, True)
    except Refuse as e:
        fails.append(f"live briefs: {e}")
    arm("every universe has a planted arm", sorted({n for n, *_ in PLANTED}), sorted(UNIVERSES))
    for u, opt, n, delete, after, empty in PLANTED:
        for label, edit, want in (("planted", None, n), ("one item deleted", delete, after), ("source emptied", empty, "Refuse")):
            t = Path(tempfile.mkdtemp())
            try:
                plant(t)
                if edit:
                    edit(t)
                arm(f"{u} {opt or ''} {label}", count(u, t, **opt), want)
            finally:
                shutil.rmtree(t, ignore_errors=True)
    t = Path(tempfile.mkdtemp())
    try:
        plant(t)
        arm("d0-grid plane", run("d0-grid", t, plane="price-weather"), ["p1/w1", "p2/w1"])
        arm("d14 open", run("d14-classes", t, status="open"), ["open production A"])
        arm("d1-stores lines: DOMAINS keys, each earlier step of CONFIG_ENTRY_VERSION and of a *_STORE_VERSION, a v1 store once",
            run("d1-stores", t), ["store a", "store b", f"upgrade {PKG}/const.py:CONFIG_ENTRY_VERSION v1->3", f"upgrade {PKG}/const.py:CONFIG_ENTRY_VERSION v2->3",
                                  f"upgrade {PKG}/store.py:LEDGER_STORE_VERSION v1->2", f"upgrade {PKG}/store.py:MAP_STORE_VERSION v1 (no earlier version)"])
        arm("d1-inputs lines: a flow key behind an entity selector (one outside the CONF_*_ENTITY shape, two a loop binds), "
            "and a key the reset keeps as an entity assignment by the wiring's rule or its literal entry",
            run("d1-inputs", t), [f"input {k}" for k in ("CONF_A_ENTITY", "CONF_B_ENTITY", "CONF_F_SENSOR", "CONF_H1", "CONF_H2", "CONF_W_SENSOR")])
        for label, edit in (("an entity selector outside an `_F` row", cut(CF, "ROWS = (", "LOOSE = _entity_of('x')\nROWS = (")),
                            ("an entity selector row whose key is no name", cut(CF, "_F('s', CONF_A_ENTITY,", "_F('s', 'a_entity',")),
                            ("a wiring rule holding a test the census cannot read", cut(f"{PKG}/entry_config.py", "key.endswith('_entity')", "key[-7:] == '_entity'")),
                            ("a FACTORY_KEPT holding a second comprehension", cut(f"{PKG}/entry_config.py", "**_WIRING})", "**_WIRING, **{k: 'other' for k in ()}})")),
                            ("an isinstance test on the loop's name, not its value", cut(f"{PKG}/entry_config.py", "isinstance(key, str)", "isinstance(name, str)"))):
            g = Path(tempfile.mkdtemp())
            try:
                plant(g)
                edit(g)
                arm(f"d1-inputs {label} is refused", count("d1-inputs", g), "Refuse")
            finally:
                shutil.rmtree(g, ignore_errors=True)
        arm("d1-excepts lines carry broad or narrow", [l.split()[1] for l in run("d1-excepts", t)], ["broad", "narrow"])
        arm("d1-lifecycle lines: an async_track_* call, a LIFE_CALLS call and every entry point",
            run("d1-lifecycle", t), sorted([f"async_create_task {X}:12 f", f"async_track_time_interval {X}:11 f", *[f"entry {f}" for f in ENTRY]]))
        arm("d16-writes lines: the .services.async_call sites and log_held, not an async_call on another receiver",
            run("d16-writes", t), [f"hold {X}:4 f", f"write {X}:2 f domain=a", f"write {X}:3 f domain=a"])
        arm("d1-parsers lines: a parse def, json.loads, a bare .json() and async_subscribe, not a .json(x) with an argument",
            run("d1-parsers", t), [f"def {PKG}/p.py:2 parse_a", f"json {PKG}/p.py:3 parse_a", f"response {PKG}/p.py:5 g", f"subscribe {PKG}/p.py:7 g"])
        arm("d0-modules follows `from <package> import <module>`", f"{PKG}/t.py" in run("d0-modules", t), True)
        arm("d9-collections a module-level function's self is no class's collection", [l for l in run("d9-collections", t) if l.startswith("helper.")], [])
        arm("d9-solves lines: the solver's call, the recursive call inside its module, the coordinator's call and its bare reference",
            [(l.split(" <- ")[0], l.rsplit(" ", 1)[-1]) for l in run("d9-solves", t)],
            [("path go", "C.cycle"), ("path go", "(ref)"), ("path go", "go"), ("solve _multi_start_minimize", "go")])
        # D16's site rule and its one axis; D17's kinds. Each edit is of a fresh plant.
        def planted(*edits, u="d16-writes", **opt):
            d = Path(tempfile.mkdtemp())
            try:
                plant(d)
                for e in edits:
                    e(d)
                with contextlib.redirect_stderr(io.StringIO()):
                    return run(u, d, **opt)
            except Refuse:
                return "Refuse"
            finally:
                shutil.rmtree(d, ignore_errors=True)
        CALL, more = "    hass.services.async_call('a', 'b')\n", lambda line: cut(X, "    log_held('x')\n", "    log_held('x')\n" + line)
        writes = lambda ls: sorted(l.split(" ", 2)[2] for l in ls if l.startswith("write "))
        arm("d16 a write line names its literal domain", writes(planted()), ["f domain=a", "f domain=a"])
        arm("d16 a call on a read-only domain is no write (the count stays)", len(planted(more("    hass.services.async_call('weather', 'get_forecasts')\n"))), 3)
        arm("d16 null control: the same call on another domain is a write", len(planted(more("    hass.services.async_call('number', 'set_value')\n"))), 4)
        arm("d16 a reference handed on uncalled is a write with no literal domain", writes(planted(more("    g = hass.services.async_call\n"))), ["f domain=?", "f domain=a", "f domain=a"])
        arm("d16 a call whose domain is no literal is a cell, never dropped", writes(planted(cut(X, CALL, "    hass.services.async_call(*svc(e), {})\n"))), ["f domain=?", "f domain=a"])
        arm("d16 a domain passed by keyword is read", writes(planted(cut(X, CALL, "    hass.services.async_call(domain='weather', service='s')\n"))), ["f domain=a"])
        real_states = STATES
        try:
            globals()["STATES"] = tuple(st for st in real_states if st[0] != "idle")
            arm("d16 --cells is sites x states: one state cut drops one cell per site", len(planted(cells=True)), 3 * (len(real_states) - 1))
        finally:
            globals()["STATES"] = real_states
        arm("d16 --cells each site carries every state once", sorted({l.rsplit(" | ", 1)[1] for l in planted(cells=True)}), sorted(n for n, _ in STATES))
        arm("d16 --cells a duty mode added in production and rowed by no state is refused",
            planted(cut(f"{PKG}/const.py", "('off', 'observe', 'control')", "('off', 'observe', 'control', 'eco')"), cells=True), "Refuse")
        arm("d16 --cells a duty mode a state names and production dropped is refused",
            planted(cut(f"{PKG}/const.py", "('off', 'observe', 'control')", "('off', 'control')"), cells=True), "Refuse")
        arm("d17 --kind prints one prefix's lines", planted(u="d17-features", kind="service"), ["service set_a", "service set_b"])
        def cli(*argv):
            d = Path(tempfile.mkdtemp())
            try:
                plant(d)
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
                    rc = main([*argv, "--repo", str(d)])
                return rc, buf.getvalue().splitlines()
            finally:
                shutil.rmtree(d, ignore_errors=True)
        arm("d17 the command line's --kind reaches the filter", cli("d17-features", "--kind", "service"), (0, ["service set_a", "service set_b"]))
        arm("d17 the kinds partition the universe", sorted(l for k in KINDS for l in (lambda r: [] if r == "Refuse" else r)(planted(u="d17-features", kind=k))), planted(u="d17-features"))
        real_kinds = KINDS
        try:
            globals()["KINDS"] = tuple(k for k in real_kinds if k != "blueprint")
            arm("d17 a printed prefix KINDS does not name is refused", planted(u="d17-features"), "Refuse")
        finally:
            globals()["KINDS"] = real_kinds
        arm("d0-modules follows an absolute import of the package", f"{PKG}/u.py" in run("d0-modules", t), True)
        arm("d3-sites --ast --by-file counts the sites per file", run("d3-sites", t, ast_only=True, by_file=True), [f"{X} 5"])
        quiet = contextlib.redirect_stderr(io.StringIO())
        cells = run("d0-grid", t)
        arm("d0-grid a cell names D0.md step 4's axis levels", [sorted({c.split("/")[k] for c in cells}) for k in (2, 3, 4, 5)],
            [sorted(TOPOLOGY), sorted(DHW), sorted(PLANT), ["24h", "48h", "6h"]])
        arm("d0-grid the two plants round 10's escapes name are levels", {"manual-valve-buffer", "flow-setpoint-behind-valve"} <= set(PLANT), True)
        arm("d3-sites with no ledger source and no --ast is refused", count("d3-sites", t), "Refuse")
        rm(CO)(t)
        arm("d0-modules with no coordinator.py is refused", count("d0-modules", t), "Refuse")
        shutil.rmtree(t)
        t.mkdir()
        plant(t)
        arm("d9-solves a caller outside the solver's module is printed and not climbed", [l for l in run("d9-solves", t) if "cycle <-" in l], [])
        with quiet:
            arm("d12 a cell with no ledger row is not run", {l.split("\t", 1)[1] for l in run("d12-cells", t)}, {"not run"})
        led = t / "ledger.tsv"
        for label, text, want in (("a ledger row is joined", "level mode=m1\tsimulation\ttests/x.py::t\n", 6),
                                  ("an unknown source is refused", "level mode=m1\thearsay\ttests/x.py::t\n", "Refuse"),
                                  ("a row asserting nothing is refused", "level mode=m1\tsimulation\t \n", "Refuse"),
                                  ("a row naming no cell is refused", "level mode=m9\tsimulation\ttests/x.py::t\n", "Refuse"),
                                  ("a pair row without --pairs is refused", "pair mode=m1 & price_shape=p1\tbundle\ttests/x.py::t\n", "Refuse")):
            led.write_text(text)
            arm(f"d12 ledger: {label}", count("d12-cells", t, ledger=str(led)), want)
        led.write_text("level mode=m1\tsimulation\ttests/x.py::t\n")
        with contextlib.redirect_stderr(io.StringIO()):
            arm("d12 ledger: the joined row prints its source and test", [l for l in run("d12-cells", t, ledger=str(led)) if "not run" not in l],
                ["level mode=m1\tsimulation\ttests/x.py::t"])
        led.write_text("# a comment\nlevel mode=m9\tsimulation\ttests/x.py::t\n")
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                run("d12-cells", t, ledger=str(led))
            msg = "passed"
        except Refuse as e:
            msg = str(e)
        arm("a ledger refusal names the row's line", f"{led}:2:" in msg, True)
        arm("d12 a missing ledger is refused", count("d12-cells", t, ledger=str(t / "none.tsv")), "Refuse")
        edit_json(OBJECTIVE, lambda d: d["population"][2].update(levels={"min": 1, "max": 9}))(t)
        with contextlib.redirect_stderr(io.StringIO()):
            arm("d12 a NO-READ axis whose levels are declared is one cell per level", [l for l in run("d12-cells", t) if "size" in l],
                ["level size=max\tnot run", "level size=min\tnot run"])
        arm("d12 a declared level pairs with every level of another axis", count("d12-cells", t, pairs=True), (4 + 2) + (4 + 4 * 2) + 2)
        led.write_text("level size=min\tsimulation\ttests/x.py::t\n")
        arm("d12 ledger: a declared level's row is joined", count("d12-cells", t, ledger=str(led)), 4 + 2 + 2)
        edit_json(OBJECTIVE, lambda d: d["population"].append({"axis": "area", "kind": None, "levels": {"lo": 1, "hi": 2}, "no_read": "r", "builder": "G"}))(t)
        arm("d12 two declared axes pair with each other once", count("d12-cells", t, pairs=True), (4 + 4) + (4 + 4 * 4 + 2 * 2) + 2)
        edit_json(OBJECTIVE, lambda d: (d["population"].pop(), d["population"][2].update(levels={})))(t)
        arm("d12 a NO-READ axis declaring no level is no cell", count("d12-cells", t), 4 + 2)
        arm("with no ledger a census prints its items alone", run("d1-inputs", t)[:2], ["input CONF_A_ENTITY", "input CONF_B_ENTITY"])
        for label, text, want in (("a census line is joined to its driving test, the rest not run", "# c\n\ninput CONF_A_ENTITY\ttests/x.py::t\n",
                                   ["input CONF_A_ENTITY\ttests/x.py::t"] + [f"input {k}\tnot run" for k in ("CONF_B_ENTITY", "CONF_F_SENSOR", "CONF_H1", "CONF_H2", "CONF_W_SENSOR")]),
                                  ("a census row naming no test is refused", "input CONF_A_ENTITY\t\n", "Refuse"),
                                  ("a census row with a source column is refused", "input CONF_A_ENTITY\tsimulation\ttests/x.py::t\n", "Refuse"),
                                  ("a census row naming no item is refused", "input CONF_Z_ENTITY\ttests/x.py::t\n", "Refuse")):
            led.write_text(text)
            try:
                got = run("d1-inputs", t, ledger=str(led))
            except Refuse:
                got = "Refuse"
            arm(f"ledger: {label}", got, want)
        bd = t / "dev/governance/dimensions"
        bd.mkdir(parents=True)

        def cited(text):
            (bd / "D1.md").write_text(text)
            try:
                return briefs(t)
            except Refuse:
                return "Refuse"
        arm("briefs: a cited universe that prints is ok, across a line wrap", cited("1. Per line of `python3 tools/audit/enumerate.py\n   d2-identities --cells`.\n"), ["ok D1 d2-identities --cells"])
        arm("briefs: a citation of no universe is refused", cited("1. `enumerate.py d1-nothing`\n"), "Refuse")
        arm("briefs: a tree whose briefs cite none is refused", cited("1. Enumerate by hand.\n"), "Refuse")
        arm("briefs: one refused citation beside a good one refuses the tree", cited("1. `enumerate.py d1-inputs` and `enumerate.py d1-nothing`\n"), "Refuse")
        arm("briefs: a citation's options are run as cited", (cut(f"{PKG}/const.py", DUTY)(t), cited("1. `enumerate.py d16-writes --cells`\n"))[1], "Refuse")
        (t / BUNDLES).write_text('{"bundles": []}')
        arm("briefs: a cited universe that is empty is refused", cited("1. `enumerate.py d15-installs`\n"), "Refuse")
        plant_bundles(t)
        edit_json(BUNDLES, lambda d: d["bundles"][0].update(evidence="tests/gone.py"))(t)
        arm("d15 a bundle whose evidence is not in the tree is refused", count("d15-installs", t), "Refuse")
        cut(CO, "    def _solve_hubs(self):\n        return self.b\n")(t)
        arm("d1-solve-state a solve-thread entry that moved is refused, not read short", count("d1-solve-state", t), "Refuse")
        edit_json(IDENTITIES, lambda d: d["identities"][0].update(grid=["no_such_axis"]))(t)
        arm("d2 a grid axis with no level is refused", count("d2-identities", t), "Refuse")
        edit_json(IDENTITIES, lambda d: d["identities"][0].update(grid=["mode"], id=""))(t)
        arm("d2 an identity with no id is refused", count("d2-identities", t), "Refuse")
        edit_json(IDENTITIES, lambda d: d["identities"][0].update(id="i1", step="S1"))(t)
        arm("d2 an identity whose step is not M<n> is refused", count("d2-identities", t), "Refuse")
        edit_json(BUNDLES, lambda d: d["bundles"][0].update(evidence="tests/profiles.py", date="yesterday"))(t)
        arm("d15 a bundle with no date is refused", count("d15-installs", t), "Refuse")
        for total in ("LEVELS", "PAIRS"):
            real = population_axes
            try:
                globals()["population_axes"] = lambda repo: (real(repo)[0], {**real(repo)[1], total: 0})
                arm(f"d12 a cell count that disagrees with the population's {total} is refused", count("d12-cells", t, pairs=True), "Refuse")
            finally:
                globals()["population_axes"] = real
        edit_json(OBJECTIVE, lambda d: d["population"][0].update(symbol="NO_SUCH_TUPLE"))(t)
        arm("d12 an unreadable population axis is refused", count("d12-cells", t), "Refuse")
        g = Path(tempfile.mkdtemp())
        try:
            plant(g)
            (g / "blueprints/automation/untracked.yaml").write_text("")
            sys.path.append(str(Path(__file__).resolve().parents[2] / "tests"))
            from throwaway_git import throwaway_git_init
            env = throwaway_git_init(g, "-q")
            for a in (["add", "-A", ":!blueprints/automation/untracked.yaml"], ["commit", "-q", "-m", "plant"]):
                subprocess.run(["git", *a], cwd=g, env=env, capture_output=True, check=True)
            arm("in a git checkout an untracked file is in no universe", [l for l in run("d17-features", g) if "blueprint" in l], ["blueprint blueprints/automation/b.yaml"])
        finally:
            shutil.rmtree(g, ignore_errors=True)
    finally:
        shutil.rmtree(t, ignore_errors=True)
    if fails:
        print("SELF-TEST FAILED: " + "; ".join(fails), file=sys.stderr)
        return 1
    print(f"SELF-TEST passed ({arms} arms)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("universe", nargs="?", choices=sorted(UNIVERSES))
    ap.add_argument("--repo", default=".")
    ap.add_argument("--cells", action="store_true")
    ap.add_argument("--pairs", action="store_true")
    ap.add_argument("--kind", choices=KINDS)
    ap.add_argument("--ledger")
    ap.add_argument("--status")
    ap.add_argument("--plane", choices=("price-weather",))
    ap.add_argument("--state", choices=("killed", "triaged", "unrecorded"))
    ap.add_argument("--by-file", action="store_true")
    ap.add_argument("--ast", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--briefs", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.universe and not a.briefs:
        ap.error("universe required")
    try:
        ls = briefs(Path(a.repo)) if a.briefs else run(a.universe, a.repo, cells=a.cells, pairs=a.pairs, kind=a.kind, ledger=a.ledger, status=a.status, plane=a.plane,
                 state=a.state, by_file=a.by_file, ast_only=a.ast)
    except (Refuse, SyntaxError, json.JSONDecodeError) as e:
        print(f"REFUSE: {e}", file=sys.stderr)
        return 2
    print("\n".join(ls))
    return 0


if __name__ == "__main__":
    sys.exit(main())
