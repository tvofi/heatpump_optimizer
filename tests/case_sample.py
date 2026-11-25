"""Seeded case sampling for the long flat test scripts (#3885).

``tests/features.py`` and ``tests/entities.py`` are flat modules: their cases
are the ``R.section(...)`` blocks, run top to bottom in one namespace. On a
pull request CI runs a deterministic subset of them; everywhere else every
section runs. Each script's second statement after its imports is::

    if case_sample.engage(__file__, "features"):
        raise SystemExit  # unreachable: engage() exits with the sampled run's status

Unit: a SECTION, the statements from one top-level ``R.section(...)`` to the
next. Everything before the first section (the header) and the closing
``sys.exit(R.close(...))`` always run.

Only an INDEPENDENT section is ever dropped (``independent`` below). A section
is order-dependent, and always runs, when a later section or the tail could
see what it did:

* a name it binds at module scope (an assignment, def, class, import, loop or
  ``with`` target, or a ``global`` inside one of its functions) is read
  anywhere later, so dropping it would leave a later case a ``NameError`` or a
  stale value; or
* it stores into an object it did not create itself (an attribute or item
  assignment, ``del``, or augmented assignment at module scope whose root name
  it does not bind), so dropping it would change state a later case reads; or
* it calls ``exec``, ``eval``, ``globals``, ``vars``, ``locals`` or
  ``setattr`` at module scope, whose effects no name analysis can see.

When sampling is on, each independent section is kept when the first 8 hex of
sha256(seed + title + ordinal) fall under the fraction, so the same head
repeats the same subset and a different head draws a different one.

The knobs (read only from the environment):

* ``HPO_CASE_SAMPLE`` -- the fraction of independent sections to run, in
  (0, 1). Unset, empty, ``1`` or anything unparseable: the full set.
* ``HPO_CASE_SAMPLE_SEED`` -- the seed; CI passes the head SHA. Unset: the
  full set (a sample with no recorded seed could not be repeated).
* ``GATE_SCOPE=full`` forces the full set whatever the others say.

Every run prints exactly one line, so a reader never takes a sampled run for
a full one::

    CASE-SAMPLE: <script> ran k/n (seed <sha8>)   -- sampled; n sections, k ran
    CASE-SAMPLE: <script> FULL n/n                 -- every section ran

``python3 tests/case_sample.py --self-test`` runs this module's own checks;
``python3 tests/case_sample.py --plan <script>`` prints each section's
verdict (independent or the reason it is not) without running anything.
"""
from __future__ import annotations

import ast
import hashlib
import os
import sys

# Set while engage() executes a sampled body, so the body's own engage() call
# runs nothing and returns False instead of sampling again.
_INNER = False

_OPAQUE = frozenset({"exec", "eval", "globals", "vars", "locals", "setattr", "delattr"})


def fraction(env=None) -> float | None:
    """The sampling fraction in force, or None for the full set."""
    env = os.environ if env is None else env
    if env.get("GATE_SCOPE", "") == "full":
        return None
    if not env.get("HPO_CASE_SAMPLE_SEED", ""):
        return None
    try:
        f = float(env.get("HPO_CASE_SAMPLE", "") or "1")
    except ValueError:
        return None
    if not 0.0 < f < 1.0:
        return None
    return f


def _is_section(stmt: ast.stmt) -> bool:
    return (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)
            and isinstance(stmt.value.func, ast.Attribute)
            and stmt.value.func.attr == "section"
            and isinstance(stmt.value.func.value, ast.Name)
            and stmt.value.func.value.id == "R")


def _title(stmt: ast.stmt) -> str:
    args = stmt.value.args  # type: ignore[attr-defined]
    if args and isinstance(args[0], ast.Constant) and isinstance(args[0].value, str):
        return args[0].value
    return ast.unparse(args[0]) if args else ""


def split(tree: ast.Module) -> tuple[list[ast.stmt], list[list[ast.stmt]], list[ast.stmt]]:
    """(header, sections, tail): the tail is the closing statement alone."""
    body = list(tree.body)
    tail = body[-1:] if body else []
    body = body[:-1]
    starts = [i for i, s in enumerate(body) if _is_section(s)]
    if not starts:
        return body, [], tail
    header = body[: starts[0]]
    sections = [body[a:b] for a, b in zip(starts, starts[1:] + [len(body)])]
    return header, sections, tail


def _module_scope(stmts):
    """Every node at module scope: into compound statements, never into a def, class or lambda body."""
    stack = list(stmts)
    while stack:
        node = stack.pop()
        yield node
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                yield child  # its name and decorators bind and run here; its body does not
                stack.extend(child.decorator_list)
                continue
            if isinstance(child, ast.Lambda):
                continue
            if isinstance(child, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                # Its targets are its own; only a walrus inside binds out here.
                stack.extend(n for n in ast.walk(child) if isinstance(n, ast.NamedExpr))
                continue
            stack.append(child)


def _target_names(target) -> set[str]:
    out = set()
    for n in ast.walk(target):
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            out.add(n.id)
    return out


def _root(node):
    while isinstance(node, (ast.Attribute, ast.Subscript, ast.Starred)):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def bound(stmts) -> set[str]:
    """Names the statements bind at module scope, ``global`` declarations in their functions included."""
    out: set[str] = set()
    for node in _module_scope(stmts):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(node.name)
            for inner in ast.walk(node):
                if isinstance(inner, ast.Global):
                    out.update(inner.names)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for a in node.names:
                out.add((a.asname or a.name).split(".")[0])
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            out.add(node.id)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            out.add(node.name)
        elif isinstance(node, ast.NamedExpr):
            out.update(_target_names(node.target))
    return out


_COMPS = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
_SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef) + _COMPS


def _local_names(fn) -> set[str]:
    """A function's (or lambda's) own locals: its parameters and every name its body stores, less its globals."""
    a = fn.args
    out = {x.arg for x in a.posonlyargs + a.args + a.kwonlyargs}
    out |= {x.arg for x in (a.vararg, a.kwarg) if x is not None}
    if isinstance(fn, ast.Lambda):
        return out
    declared: set[str] = set()
    stack = list(fn.body)
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.Global, ast.Nonlocal)):
            declared.update(node.names)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(node.name)
            continue
        elif isinstance(node, (ast.Lambda,) + _COMPS):
            continue
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            out.add(node.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            out.update((x.asname or x.name).split(".")[0] for x in node.names)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            out.add(node.name)
        stack.extend(ast.iter_child_nodes(node))
    return out - declared


def _reads(node, shadow: frozenset, out: set) -> None:
    """Add to ``out`` every module-level name ``node`` reads, scope by scope.

    ``shadow`` is the set of enclosing function or comprehension locals, which
    a read of the same name means instead. A class body is read with its
    enclosing shadow only, never its own names, so a method's read of a
    module name is never hidden: the conservative side.
    """
    if isinstance(node, ast.Name):
        if isinstance(node.ctx, ast.Load) and node.id not in shadow:
            out.add(node.id)
        return
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        for d in node.decorator_list:
            _reads(d, shadow, out)
        for d in node.args.defaults + [x for x in node.args.kw_defaults if x is not None]:
            _reads(d, shadow, out)
        inner = shadow | _local_names(node)
        for s in node.body:
            _reads(s, inner, out)
        return
    if isinstance(node, ast.Lambda):
        for d in node.args.defaults + [x for x in node.args.kw_defaults if x is not None]:
            _reads(d, shadow, out)
        _reads(node.body, shadow | _local_names(node), out)
        return
    if isinstance(node, _COMPS):
        inner = set(shadow)
        for g in node.generators:
            _reads(g.iter, frozenset(inner), out)
            inner |= _target_names(g.target)
            for cond in g.ifs:
                _reads(cond, frozenset(inner), out)
        elts = [node.key, node.value] if isinstance(node, ast.DictComp) else [node.elt]
        for e in elts:
            _reads(e, frozenset(inner), out)
        return
    for child in ast.iter_child_nodes(node):
        _reads(child, shadow, out)


def loads(stmts) -> set[str]:
    """Every module-level name the statements read, inside their functions too (scope-aware)."""
    out: set[str] = set()
    for s in stmts:
        _reads(s, frozenset(), out)
    return out


def _effects(stmts) -> tuple[set[str], str | None]:
    """(roots of the objects the statements store into, the first opaque effect or None).

    A store is an attribute or item assignment, ``del`` or augmented
    assignment at module scope, and an augmented assignment to a bare name;
    the root is the name the stored-into object hangs off. An opaque effect is
    a call of ``exec``, ``eval``, ``globals``, ``vars``, ``locals``,
    ``setattr`` or ``delattr`` at module scope, whose reach no name analysis
    can see.
    """
    roots: set[str] = set()
    for node in _module_scope(stmts):
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
            targets = [node.target]
        elif isinstance(node, ast.Delete):
            targets = node.targets
        for t in targets:
            for n in ast.walk(t):
                if isinstance(n, (ast.Attribute, ast.Subscript)):
                    roots.add(_root(n) or "")
        if isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name):
            roots.add(node.target.id)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _OPAQUE:
            return roots, f"calls {node.func.id}() at line {node.lineno}"
    return roots, None


def definite(stmts) -> set[str]:
    """Names a section binds unconditionally: its own top-level statements, never one inside an if, loop or try."""
    out: set[str] = set()
    for s in stmts:
        if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(s.name)
        elif isinstance(s, (ast.Import, ast.ImportFrom)):
            out.update((a.asname or a.name).split(".")[0] for a in s.names)
        elif isinstance(s, ast.Assign):
            for t in s.targets:
                out.update(_target_names(t))
        elif isinstance(s, ast.AnnAssign) and s.value is not None:
            out.update(_target_names(s.target))
        elif isinstance(s, (ast.With, ast.AsyncWith)):
            for item in s.items:
                if item.optional_vars is not None:
                    out.update(_target_names(item.optional_vars))
    return out


def free(stmts) -> set[str]:
    """Names a section reads before it binds them itself, in statement order.

    A read inside a function the section defines counts unless the section
    bound the name unconditionally before that definition.
    """
    return _free_block(stmts, frozenset())[0]


def _free_block(stmts, have: frozenset) -> tuple[set[str], frozenset]:
    """(free reads, names bound by the end) of a block entered with ``have`` bound.

    A loop or ``with`` target and an ``except ... as`` name are bound for the
    body they head; after a loop, an if or a try nothing new counts as bound,
    since the body may not have run.
    """
    out: set[str] = set()
    for s in stmts:
        if isinstance(s, (ast.For, ast.AsyncFor)):
            out |= loads([s.iter]) - have
            out |= _free_block(s.body, have | _target_names(s.target))[0]
            out |= _free_block(s.orelse, have)[0]
        elif isinstance(s, ast.While):
            out |= loads([s.test]) - have
            out |= _free_block(s.body, have)[0] | _free_block(s.orelse, have)[0]
        elif isinstance(s, ast.If):
            out |= loads([s.test]) - have
            out |= _free_block(s.body, have)[0] | _free_block(s.orelse, have)[0]
        elif isinstance(s, (ast.Try, getattr(ast, "TryStar", ast.Try))):
            out |= _free_block(s.body, have)[0]
            for h in s.handlers:
                if h.type is not None:
                    out |= loads([h.type]) - have
                out |= _free_block(h.body, have | ({h.name} if h.name else set()))[0]
            out |= _free_block(s.orelse, have)[0] | _free_block(s.finalbody, have)[0]
        elif isinstance(s, (ast.With, ast.AsyncWith)):
            inner = set(have)
            for item in s.items:
                out |= loads([item.context_expr]) - inner
                if item.optional_vars is not None:
                    inner |= _target_names(item.optional_vars)
            got, end = _free_block(s.body, frozenset(inner))
            out |= got
            have = end
        else:
            out |= loads([s]) - have
            have = have | definite([s])
    return out, have


class Section:
    """One section's facts, read once: what it binds, reads first and stores into."""

    def __init__(self, stmts):
        self.stmts = stmts
        self.title = _title(stmts[0])
        self.line = stmts[0].lineno
        self.size = stmts[-1].end_lineno - stmts[0].lineno + 1
        self.binds = bound(stmts)
        self.sure = definite(stmts)
        self.free = free(stmts)
        self.roots, self.opaque = _effects(stmts)


def plan(source: str, path: str = "<script>"):
    """(tree, header, sections, tail): sections as ``Section`` records."""
    tree = ast.parse(source, path)
    header, sections, tail = split(tree)
    return tree, header, [Section(sec) for sec in sections], tail


def choose(header, sections, tail, seed: str | None, frac: float) -> list[str | None]:
    """Which sections run: ``None`` for one the draw dropped, else why it runs.

    A backward pass. ``live`` holds every name a section that RUNS later, or
    the closing statement, reads before binding it itself. Section i is
    order-dependent, and runs whatever the draw, when it binds a live name,
    when it stores into an object hung off a live name or off one the header
    binds or no section binds (a module, a builtin), or when it makes an
    opaque call. Any other section is drawn: kept when ``keep`` says so. A
    dropped section leaves ``live`` as it was, so the sections a dropped
    reader alone needed become free to drop in turn; a kept one adds its own
    reads. ``seed=None`` keeps every section the draw would see (the plan
    view: which ones are free to be drawn at all).
    """
    header_binds = bound(header)
    any_binds = set().union(*(x.binds for x in sections)) if sections else set()
    live = loads(tail)
    out: list[str | None] = [None] * len(sections)
    for i in range(len(sections) - 1, -1, -1):
        x = sections[i]
        held = sorted(x.binds & live)
        stuck = sorted(r for r in x.roots if r in live or r in header_binds or r not in any_binds)
        if x.opaque:
            out[i] = x.opaque
        elif held:
            out[i] = "binds " + ", ".join(held[:3]) + (" ..." if len(held) > 3 else "") + ", which a later section reads"
        elif stuck:
            out[i] = f"stores into an object hung off {stuck[0] or 'an expression'}, which a later section or the header holds"
        elif seed is None or keep(seed, x.title, i, frac):
            out[i] = "drawn" if seed is not None else "free to draw"
        if out[i] is not None:
            live = x.free | (live - x.sure)
    return out


def keep(seed: str, title: str, ordinal: int, frac: float) -> bool:
    h = hashlib.sha256(f"{seed}\0{title}\0{ordinal}".encode()).hexdigest()
    return int(h[:8], 16) < frac * 0x100000000


def engage(path: str, name: str) -> bool:
    """Print the CASE-SAMPLE line; under a sample run the sampled body here and exit with its status.

    Returns False when the full set runs (the caller simply carries on), and
    inside the sampled body itself.
    """
    global _INNER
    if _INNER:
        return False
    frac = fraction()
    source = open(path, encoding="utf-8").read()
    if frac is None:
        # The count alone: one parse, no dependency analysis on a full run.
        n = len(split(ast.parse(source, path))[1])
        print(f"CASE-SAMPLE: {name} FULL {n}/{n}", flush=True)
        return False
    tree, header, sections, tail = plan(source, path)
    n = len(sections)
    seed = os.environ["HPO_CASE_SAMPLE_SEED"]
    runs = choose(header, sections, tail, seed, frac)
    kept = [x.stmts for x, why in zip(sections, runs) if why is not None]
    print(f"CASE-SAMPLE: {name} ran {len(kept)}/{n} (seed {seed[:8]})", flush=True)
    body = header + [s for sec in kept for s in sec] + tail
    module = ast.Module(body=body, type_ignores=[])
    ns = {"__file__": os.path.abspath(path), "__name__": "__main__", "__builtins__": __builtins__}
    _INNER = True
    try:
        exec(compile(module, path, "exec"), ns)
    finally:
        _INNER = False
    raise SystemExit(0)


# --- self-test ---------------------------------------------------------------

_FIXTURE = '''
import sys
R = Results("fixture")
R.section("alpha")
shared = 1
R.check("alpha", True)
R.section("beta")
local_b = 2
R.check("beta", local_b == 2)
R.section("gamma")
R.check("gamma", shared == 1)
R.section("delta")
mod.attr = 3
R.section("eps")
def helper():
    global counter
    counter = 1
R.section("zeta")
R.check("zeta", "counter" not in dir() or counter == 1)
counter = 0
R.section("eta")
local_b = 5
R.check("eta", local_b == 5)
R.section("iota")
i = 9
a = 8
R.section("kappa")
R.check("kappa", [i for i in range(2)] == [0, 1])
def kf(a):
    return a
R.check("kappa f", kf(1) == 1 and (lambda a: a)(2) == 2)
R.section("lam")
box = {}
box["k"] = 1
for item in range(2):
    R.check("lam", item in (0, 1))
sys.exit(R.close("FIXTURE"))
'''

_TITLES = ["alpha", "beta", "gamma", "delta", "eps", "zeta", "eta", "iota", "kappa", "lam"]


def _ran(stdout: str) -> list[str]:
    return stdout.split("SECTIONS ")[-1].split()[0].split(",") if "SECTIONS " in stdout else []


def _self_test() -> int:
    fails = 0

    def check(label, cond, detail=""):
        nonlocal fails
        print(f"  {'ok  ' if cond else 'FAIL'} {label}" + (f"  [{detail}]" if detail and not cond else ""))
        fails += 0 if cond else 1

    _, header, sections, tail = plan(_FIXTURE)
    titles = [x.title for x in sections]
    check("the fixture splits into ten sections, a header and the closing tail",
          titles == _TITLES and len(tail) == 1 and len(header) == 2,
          f"{titles} tail={len(tail)} header={len(header)}")
    v = dict(zip(titles, choose(header, sections, tail, None, 0.3)))
    free_ = "free to draw"
    check("with every later section kept, one whose binding a later one reads is order-dependent",
          v["alpha"] is not None and "shared" in v["alpha"], str(v["alpha"]))
    check("a global declared in a function binds the name: read later, order-dependent",
          "counter" in str(v["eps"]), str(v["eps"]))
    check("a section binding only what nothing later reads is free to draw", v["beta"] == free_, str(v["beta"]))
    check("a store into an object no section binds (a module's, a builtin's) always runs",
          v["delta"] is not None and "mod" in v["delta"], str(v["delta"]))
    check("a store into an object the section built itself is free to draw", v["lam"] == free_, str(v["lam"]))
    check("a name a later section rebinds before it reads it does not hold the earlier binder",
          v["eta"] == free_ and v["beta"] == free_, f"{v['beta']} {v['eta']}")
    check("a comprehension's target and a function's or lambda's parameter are not reads of the module name",
          v["iota"] == free_, str(v["iota"]))
    t_h, t_s, t_t = plan('R = 1\nR.section("a")\nx = 1\nR.section("b")\ny = 2\nprint(x)\n')[1:]
    t_v = choose(t_h, t_s, t_t, None, 0.3)
    check("a section whose binding the closing statement reads always runs",
          t_v[0] is not None and "x" in t_v[0] and t_v[1] == free_, str(t_v))
    o_h, o_s, o_t = plan('R = 1\nR.section("a")\nsetattr(R, "x", 1)\nR.section("b")\nz = 1\n0\n')[1:]
    o_v = choose(o_h, o_s, o_t, None, 0.3)
    check("an opaque call (setattr, exec, globals ...) always runs", "setattr" in str(o_v[0]), str(o_v))
    h_h, h_s, h_t = plan('R = 1\nbox = {}\nR.section("a")\nbox["k"] = 1\nR.section("b")\nz = 1\n0\n')[1:]
    check("a store into an object the header binds always runs",
          "box" in str(choose(h_h, h_s, h_t, None, 0.3)[0]))

    env = {"HPO_CASE_SAMPLE": "0.3", "HPO_CASE_SAMPLE_SEED": "ab" * 20}
    check("0.3 with a seed is a sample", fraction(env) == 0.3)
    check("GATE_SCOPE=full forces the full set", fraction({**env, "GATE_SCOPE": "full"}) is None)
    check("no seed is the full set", fraction({"HPO_CASE_SAMPLE": "0.3"}) is None)
    bounds = all(fraction({**env, "HPO_CASE_SAMPLE": x}) is None for x in ("0", "1", "1.5", "-0.2", "x", ""))
    check("a fraction outside (0, 1), empty or unparseable is the full set", bounds)

    seed = "0123456789abcdef0123456789abcdef01234567"
    names = [f"case {i}" for i in range(2000)]
    a = [keep(seed, t, i, 0.3) for i, t in enumerate(names)]
    b = [keep(seed, t, i, 0.3) for i, t in enumerate(names)]
    c = [keep("f" + seed[1:], t, i, 0.3) for i, t in enumerate(names)]
    share = sum(a) / len(a)
    check("the same seed draws the same subset", a == b)
    check("another seed draws another subset", a != c)
    check("0.3 keeps about 30% of 2000 drawn sections", 0.26 < share < 0.34, f"{share:.3f}")
    check("a fraction near 0 keeps almost none and near 1 almost all",
          sum(keep(seed, t, i, 0.001) for i, t in enumerate(names)) < 20
          and sum(keep(seed, t, i, 0.999) for i, t in enumerate(names)) > 1980)

    # End to end through engage(): the sampled body runs the header, the kept
    # sections and the tail, and the CASE-SAMPLE line names k/n.
    import subprocess
    import tempfile
    stub = ('import sys\nsys.path.insert(0, %r)\nimport case_sample\n'
            'if case_sample.engage(__file__, "fx"):\n    raise SystemExit\n'
            'class Results:\n    def __init__(s, t): s.titles = []\n'
            '    def section(s, t): s.titles.append(t)\n'
            '    def check(s, *a): pass\n'
            '    def close(s, l): print("SECTIONS", ",".join(s.titles)); return 0\n'
            'mod = type("M", (), {})()\n' % os.path.dirname(os.path.abspath(__file__)))
    with tempfile.TemporaryDirectory() as d:
        script = os.path.join(d, "fx.py")
        open(script, "w").write(_FIXTURE.replace("import sys\n", stub, 1))
        base = {k: x for k, x in os.environ.items()
                if k not in ("HPO_CASE_SAMPLE", "HPO_CASE_SAMPLE_SEED", "GATE_SCOPE")}

        def go(**extra):
            return subprocess.run([sys.executable, script], capture_output=True, text=True, env={**base, **extra})

        full = go()
        check("a full run prints FULL n/n and runs every section",
              "CASE-SAMPLE: fx FULL 10/10" in full.stdout
              and "SECTIONS " + ",".join(_TITLES) in full.stdout and full.returncode == 0,
              full.stdout + full.stderr)
        r1 = go(HPO_CASE_SAMPLE="0.01", HPO_CASE_SAMPLE_SEED=seed)
        r2 = go(HPO_CASE_SAMPLE="0.01", HPO_CASE_SAMPLE_SEED=seed)
        ran = _ran(r1.stdout)
        check("a sampled run prints ran k/n with the seed's first 8 hex, keeps the order-dependent section "
              "and exits 0",
              f"(seed {seed[:8]})" in r1.stdout and f"CASE-SAMPLE: fx ran {len(ran)}/10" in r1.stdout
              and "delta" in ran and r1.returncode == 0, r1.stdout + r1.stderr)
        check("a rerun of the same seed repeats the same subset", r1.stdout == r2.stdout)
        held, released = True, False
        for k in range(40):
            r = go(HPO_CASE_SAMPLE="0.5", HPO_CASE_SAMPLE_SEED=f"{k:040x}")
            got = _ran(r.stdout)
            held &= (r.returncode == 0 and "delta" in got
                     and ("gamma" not in got or "alpha" in got) and ("zeta" not in got or "eps" in got))
            released |= "alpha" not in got and "gamma" not in got
        check("over 40 seeds every sampled run exits 0, keeps the order-dependent section, and never runs a "
              "reader without the section it reads", held)
        check("a binder whose only reader the draw dropped is drawn in turn (some seed drops both)", released)
        forced = go(HPO_CASE_SAMPLE="0.01", HPO_CASE_SAMPLE_SEED=seed, GATE_SCOPE="full")
        check("GATE_SCOPE=full runs the full set even with a sample asked for",
              "CASE-SAMPLE: fx FULL 10/10" in forced.stdout, forced.stdout)

    print(f"CASE-SAMPLE SELF-TEST: {'PASSED' if not fails else f'{fails} FAILED'}")
    return 1 if fails else 0


def _print_plan(path: str, frac: float = 0.3, seeds: int = 20) -> int:
    """Each section's verdict with every later one kept, then the measured share a draw drops."""
    _, header, sections, tail = plan(open(path, encoding="utf-8").read(), path)
    for x, why in zip(sections, choose(header, sections, tail, None, frac)):
        print(f"{x.line}\t{x.size}\t{why}\t{x.title}")
    total = sum(x.size for x in sections)
    dropped_lines, dropped_n = [], []
    for k in range(seeds):
        runs = choose(header, sections, tail, hashlib.sha256(str(k).encode()).hexdigest(), frac)
        dropped_lines.append(sum(x.size for x, why in zip(sections, runs) if why is None))
        dropped_n.append(sum(why is None for why in runs))
    print(f"PLAN: {path} fraction {frac}: over {seeds} seeds a draw drops {min(dropped_n)}-{max(dropped_n)} "
          f"of {len(sections)} sections, mean {sum(dropped_lines) / seeds / total:.1%} of {total} section lines")
    return 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        sys.exit(_self_test())
    if len(sys.argv) == 3 and sys.argv[1] == "--plan":
        sys.exit(_print_plan(sys.argv[2]))
    print(__doc__)
    sys.exit(2)
