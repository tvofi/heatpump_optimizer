#!/usr/bin/env python3
"""Print one audit universe, one item per line, so a finder can report `universe=N examined=n`.

Usage: python3 -I tools/audit/enumerate.py <universe> [--repo DIR] [options]
  d16-writes [--cells]   actuator `services.async_call` and `log_held` sites; --cells crosses each
                         with the PUMP_DUTY_MODES parsed from const.py and the four lifecycle conditions
  d17-features           services.yaml keys, strings.json steps/fields/entities, blueprints
  d14-classes [--status open]   dev/audit/config/bugclasses.json entries that carry a status
  d0-grid [--plane price-weather]   tests/profiles.py price x weather x topology x dhw x plant x horizon
  d0-modules             package-internal import closure of optimizer.py + dhw_planner.py, plus coordinator.py
  d1-stores              store.py DOMAINS keys, and one `upgrade` line per earlier *_STORE_VERSION /
                         CONFIG_ENTRY_VERSION step
  d1-excepts             every except handler, broad or narrow
  d1-lifecycle           async_track_* / async_call_later / listener / task registrations and the entry points
  d3-sites [--state S] [--by-file] [--ast]   the mutation universe, `<file>:<line> <kind> <state>`, joined
                         to the ledger through tests/mutation_table.py's own `inventory` and
                         `disposition_matches`; --ast is the ledger-free fallback (if/ifexp/minmax/except)
Stdout is the universe only (deterministic, sorted; `wc -l` is its size); a second identical item on
one line gets a ` #2` suffix so no two lines are equal. Diagnostics go to stderr.
Exit 0 on success. Exit 2 with a message on stderr when a source is missing or yields zero items: an
empty universe is a refusal, never a pass.
Null control: --self-test runs every universe on the live tree (>=1 line, sorted, no duplicates) and
plants a tiny fake repo (--repo) per parser family: two async_call and one log_held give 3 lines, and
2 after one call is deleted; one open and one barriered class give 1 under --status open; a fake
strings.json/services.yaml/blueprint give the expected d17 lines; 2 price x 1 weather profiles give
2x1x2x2x3x3 grid lines; an empty source exits 2. It prints `SELF-TEST passed (N arms)` or names the
failing arm and exits 1.
"""
import argparse, ast, collections, contextlib, io, json, os, re, subprocess, sys, tempfile
from pathlib import Path

PKG = "custom_components/heatpump_optimizer"
# the conditions dev/governance/dimensions/D16.md step 2 drives
CONDITIONS = ("running", "restart", "upgrade", "unavailable")
# D0.md step 4's axes
TOPOLOGY, DHW, PLANT, HORIZON_H = ("single-zone", "two-zone"), ("dhw", "no-dhw"), ("plain", "valve-storage", "wood"), (6, 24, 48)
USER_PLATFORMS = ("switch", "button", "climate", "datetime", "number", "select")
LIFE_CALLS = {"async_call_later", "async_on_unload", "async_create_task", "async_create_background_task",
              "async_add_executor_job", "async_listen", "async_listen_once", "add_update_listener"}
ENTRY_FNS = ("async_setup", "async_setup_entry", "async_unload_entry", "async_remove_entry",
             "async_migrate_entry", "async_update_options")


class Refuse(Exception):
    pass


def pkg_files(repo):
    fs = sorted((repo / PKG).glob("*.py"))
    if not fs:
        raise Refuse(f"no {PKG}/*.py under {repo}")
    return fs


def rel(repo, p):
    return p.relative_to(repo).as_posix()


def parse(p):
    if not p.is_file():
        raise Refuse(f"missing source {p}")
    return ast.parse(p.read_text())


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
    return None


def d16(repo, cells=False, **_):
    out = []
    for p in pkg_files(repo):
        for n, q in scoped(parse(p)):
            if isinstance(n, ast.Call):
                f = n.func
                if isinstance(f, ast.Attribute) and f.attr == "async_call" and isinstance(f.value, ast.Attribute) and f.value.attr == "services":
                    out.append(f"write {rel(repo, p)}:{n.lineno} {q}")
                if fname(n) == "log_held":
                    out.append(f"hold {rel(repo, p)}:{n.lineno} {q}")
    if cells:
        v = const_assign(parse(repo / PKG / "const.py"), "PUMP_DUTY_MODES")
        modes = [e.value for e in getattr(v, "elts", []) if isinstance(e, ast.Constant)]
        if not modes:
            raise Refuse("PUMP_DUTY_MODES not found in const.py")
        out = [f"{s} | duty={m} | {c}" for s in out for m in modes for c in CONDITIONS]
    return out


def d17(repo, **_):
    out, base = [], repo / PKG
    sy = base / "services.yaml"
    if not sy.is_file():
        raise Refuse(f"missing source {sy}")
    out += [f"service {m}" for m in re.findall(r"^([a-z_]+):", sy.read_text(), re.M)]
    sj = base / "strings.json"
    if not sj.is_file():
        raise Refuse(f"missing source {sj}")
    s = json.loads(sj.read_text())
    for sec, kstep, kfield in (("config", "config-step", "config-field"), ("options", "options-step", "option")):
        for step, body in s.get(sec, {}).get("step", {}).items():
            out.append(f"{kstep} {step}")
            out += [f"{kfield} {step}.{k}" for k in (body.get("data") or {})]
    ent = s.get("entity", {})
    out += [f"entity {pl}.{k}" for pl in USER_PLATFORMS for k in ent.get(pl, {})]
    r = subprocess.run(["git", "ls-files", "blueprints"], cwd=repo, capture_output=True, text=True)
    bp = r.stdout.split() if r.returncode == 0 else []
    if not bp and (repo / "blueprints").is_dir():
        bp = [rel(repo, Path(d) / f) for d, _, fs in os.walk(repo / "blueprints") for f in fs]
    return out + [f"blueprint {b}" for b in bp]


def d14(repo, status=None, **_):
    p = repo / "dev/audit/config/bugclasses.json"
    if not p.is_file():
        raise Refuse(f"missing source {p}")
    return [f"{v['status']} {v.get('kind', '?')} {k}" for k, v in json.loads(p.read_text()).items()
            if isinstance(v, dict) and "status" in v and status in (None, v["status"])]


def d0grid(repo, plane=None, **_):
    tree = parse(repo / "tests/profiles.py")
    lits = {}
    for fn in ("prices", "weather"):
        f = next((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == fn), None)
        if f is None:
            raise Refuse(f"no function {fn} in tests/profiles.py")
        lits[fn] = sorted({c.value for n in ast.walk(f) if isinstance(n, ast.Compare) and isinstance(n.left, ast.Name)
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
    for m in todo:
        if not (base / f"{m}.py").is_file():
            raise Refuse(f"missing source {base / (m + '.py')}")
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
        sys.path.insert(0, str(repo / "tests"))
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


UNIVERSES = {"d16-writes": d16, "d17-features": d17, "d14-classes": d14, "d0-grid": d0grid, "d0-modules": d0modules,
             "d1-stores": d1stores, "d1-excepts": d1excepts, "d1-lifecycle": d1life, "d3-sites": d3}


def run(name, repo, **kw):
    lines = UNIVERSES[name](Path(repo), **kw)
    seen = collections.Counter()
    out = []
    for l in lines:
        seen[l] += 1
        out.append(l if seen[l] == 1 else f"{l} #{seen[l]}")
    if not out:
        raise Refuse(f"{name} yields zero items: an empty universe is a refusal")
    return sorted(out)


def plant(root, calls=2):
    P = root / PKG
    (root / "tests").mkdir(parents=True), (root / "dev/audit/config").mkdir(parents=True), (root / "blueprints/automation").mkdir(parents=True), P.mkdir(parents=True)
    w = lambda p, t: (root / p).write_text(t)
    body = "def f(hass):\n" + "    hass.services.async_call('a', 'b')\n" * calls + "    log_held('x')\n"
    w(f"{PKG}/x.py", body + "    try:\n        pass\n    except Exception:\n        pass\n    except ValueError:\n        pass\n"
      "    async_track_time_interval(1)\n    y = min(1, 2) if hass else 0\n    if y:\n        pass\n")
    w(f"{PKG}/const.py", "PUMP_DUTY_MODES: Final = ('off', 'control')\nCONFIG_ENTRY_VERSION: Final = 3\n")
    w(f"{PKG}/store.py", "K = 'b'\nDOMAINS = {'a': {}, K: {}}\n")
    w(f"{PKG}/__init__.py", "async def async_setup_entry(h, e):\n    pass\ndef helper():\n    pass\n")
    w(f"{PKG}/optimizer.py", "from .y import z\nfrom . import w\n")
    w(f"{PKG}/y.py", "from custom_components.heatpump_optimizer.v import q\n")
    for n in ("w", "v", "dhw_planner", "coordinator"):
        w(f"{PKG}/{n}.py", "")
    w(f"{PKG}/services.yaml", "set_a:\n  fields: {}\nset_b:\n")
    w(f"{PKG}/strings.json", json.dumps({"config": {"step": {"user": {"data": {"f1": "", "f2": ""}}}},
                                         "options": {"step": {"init": {"data": {"o1": ""}}}},
                                         "entity": {"switch": {"s1": {}}, "sensor": {"z": {}}}}))
    w("blueprints/automation/b.yaml", "")
    w("tests/profiles.py", "def prices(profile, s):\n    if profile == 'p1':\n        pass\n    elif profile == 'p2':\n        pass\n"
      "def weather(profile, s):\n    if profile == 'w1':\n        pass\n")
    w("dev/audit/config/bugclasses.json", json.dumps({"_note": "x", "A": {"status": "open", "kind": "production"},
                                                       "B": {"status": "barriered", "kind": "instrument"}}))


def self_test():
    arms, fails = 0, []

    def arm(name, got, want):
        nonlocal arms
        arms += 1
        if got != want:
            fails.append(f"{name}: got {got!r}, want {want!r}")

    live = Path(".")
    for u in UNIVERSES:
        for opt in ({}, {"cells": True} if u == "d16-writes" else {"plane": "price-weather"} if u == "d0-grid" else {}):
            try:
                ls = run(u, live, **opt)
            except Refuse as e:
                ls = []
                fails.append(f"live {u} {opt}: {e}")
            arm(f"live {u} {opt}", (len(ls) >= 1, ls == sorted(ls), len(ls) == len(set(ls))), (True, True, True))
    t = Path(tempfile.mkdtemp())
    plant(t)
    try:
        arm("d16 planted", len(run("d16-writes", t)), 3)
        arm("d16 cells", len(run("d16-writes", t, cells=True)), 3 * 2 * 4)
        arm("d1-excepts", [l.split()[1] for l in run("d1-excepts", t)], ["broad", "narrow"])
        arm("d1-lifecycle", [l.split()[0] for l in run("d1-lifecycle", t)], ["async_track_time_interval", "entry"])
        arm("d17", len(run("d17-features", t)), 9)
        arm("d14 all", len(run("d14-classes", t)), 2)
        arm("d14 open", run("d14-classes", t, status="open"), ["open production A"])
        arm("d0-grid", len(run("d0-grid", t)), 2 * 1 * 2 * 2 * 3 * 3)
        arm("d0-grid plane", run("d0-grid", t, plane="price-weather"), ["p1/w1", "p2/w1"])
        arm("d0-modules", [l.rsplit("/", 1)[1] for l in run("d0-modules", t)],
            ["coordinator.py", "dhw_planner.py", "optimizer.py", "v.py", "w.py", "y.py"])
        arm("d1-stores", run("d1-stores", t), ["store a", "store b", f"upgrade {PKG}/const.py:CONFIG_ENTRY_VERSION v1->3",
                                               f"upgrade {PKG}/const.py:CONFIG_ENTRY_VERSION v2->3"])
        arm("d3 ast", len(run("d3-sites", t, ast_only=True)), 5)  # live ledger arm is the d3-sites live arm above
        (t / PKG / "x.py").write_text("def f(hass):\n    hass.services.async_call('a', 'b')\n    log_held('x')\n")
        arm("d16 after delete", len(run("d16-writes", t)), 2)
        (t / PKG / "x.py").write_text("")
        try:
            run("d16-writes", t)
            arm("d16 empty refused", "passed", "Refuse")
        except Refuse:
            arm("d16 empty refused", "Refuse", "Refuse")
    finally:
        import shutil
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
    ap.add_argument("--status")
    ap.add_argument("--plane", choices=("price-weather",))
    ap.add_argument("--state", choices=("killed", "triaged", "unrecorded"))
    ap.add_argument("--by-file", action="store_true")
    ap.add_argument("--ast", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.universe:
        ap.error("universe required")
    try:
        ls = run(a.universe, a.repo, cells=a.cells, status=a.status, plane=a.plane, state=a.state, by_file=a.by_file, ast_only=a.ast)
    except (Refuse, SyntaxError, json.JSONDecodeError) as e:
        print(f"REFUSE: {e}", file=sys.stderr)
        return 2
    print("\n".join(ls))
    return 0


if __name__ == "__main__":
    sys.exit(main())
