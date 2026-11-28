#!/usr/bin/env python3
"""Case-level test units inside the long flat scripts (R11-CI-CASE-SELECT, part P1).

    python3 tests/case_select.py split <script>                   print the spans, one line each
    python3 tests/case_select.py run <script> [--plan FILE]       run the script span by span
    python3 tests/case_select.py plan <script> [--seed S] [--base REF] [--files F]   a pull request's plan
    python3 tests/case_select.py run <script> --sample [--seed S] [--base REF] [--files F]   plan, then run it
    python3 tests/case_select.py record <script> [--union] [--table T]
    python3 tests/case_select.py stats <script>                   selectivity figures from the table
    python3 tests/case_select.py scripts                          the scripts recorded per span
    python3 tests/case_select.py --self-test

`tests/features.py` and `tests/entities.py` have no callable cases. Each is a
flat module whose cases are the spans between top-level `R.section(<literal>)`
statements, all sharing one namespace. This module cuts those spans from the
AST, runs a script span by span in one namespace, and records per span what it
reads, into `tests/case_closures.json`:

- `files`: the repository units the span opened and the files of the code it
  started (`sys.monitoring` PY_START). They also include the files its started
  code and its own names reach through a module-level import (one hop further
  through that module's own imports), and the repository paths on its
  subprocess command lines;
- `needs`: the earlier spans it depends on. A span needs an earlier one that
  binds a name it reads. Binding means an assignment, def, class, import or
  `global`, an attribute or item store on the name, an in-place method call on
  it, or a call of a function whose body does one of these. It also needs an
  earlier span that moved a module-level value or a repository module's
  attribute it can see, recorded by fingerprints taken at each span boundary.
  And it needs an earlier span that moved shared process state: the RNG, the
  environment, `sys.path`, the logging root, the warning filters or the
  locale. Every span that draws both reads and moves `@random`, so each
  drawing span needs the previous one.

On a pull request under `GATE_SCOPE=auto`, `tests/run.sh` runs the two
scripts through `run --sample` (#3885 item 2): `plan` keeps every span the
diff reaches and draws `FRACTION` of the rest, seeded by `HPO_CASE_SEED`
(`<PR number>-<head sha>`); the same seed, base and table give the same plan
on any machine. Any other event, or any fail-safe in `plan`, runs every span.
`record` on Darwin only unions into an existing entry (`--union`); a full
re-derivation replaces entries and runs on Linux (`tests/derive_closures.sh --cases`).
"""
from __future__ import annotations

import __future__ as _future
import ast
import builtins
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "tests" / "case_closures.json"
VERSION = 1
SCRIPTS = ("tests/features.py", "tests/entities.py")
_TOOL_ID = 4  # a sys.monitoring tool slot no debugger, profiler or coverage tool claims

# In-place methods that change their receiver (design 25fa1f76, section 3).
INPLACE = frozenset({
    "append", "extend", "update", "insert", "pop", "popitem", "clear", "setdefault",
    "add", "remove", "discard", "sort", "reverse",
    "difference_update", "intersection_update", "symmetric_difference_update",
    "__setitem__", "__delitem__",
})
# The shared process state a span can move without binding a name.
RNG_MODULES = ("random", "numpy.random")
STATE_SETTERS = {
    "@environ": ("os.environ", "os.putenv", "os.unsetenv", "time.tzset"),
    "@syspath": ("sys.path", "sys.modules"),
    "@logging": ("logging.basicConfig", "logging.disable", "logging.root", "logging.getLogger"),
    "@warnings": ("warnings.filterwarnings", "warnings.simplefilter", "warnings.resetwarnings",
                  "warnings.filters"),
    "@locale": ("locale.setlocale",),
}


# ---------------------------------------------------------------- the splitter

class Span:
    """One case: a top-level `R.section(<literal>)` statement up to the next one."""

    def __init__(self, sid: str, title: str, stmts: list, first: int, last: int, text: str):
        self.id, self.title, self.stmts = sid, title, stmts
        self.first, self.last = first, last  # 1-based source lines, inclusive
        self.hash = hashlib.sha1(text.encode()).hexdigest()


def _title(node: ast.stmt) -> str | None:
    """The literal title when `node` is a top-level `R.section("...")` statement."""
    if not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)):
        return None
    f, args = node.value.func, node.value.args
    if (isinstance(f, ast.Attribute) and f.attr == "section" and isinstance(f.value, ast.Name)
            and f.value.id == "R" and len(args) == 1 and isinstance(args[0], ast.Constant)
            and isinstance(args[0].value, str)):
        return args[0].value
    return None


def _is_close(node: ast.stmt) -> bool:
    """The script's closing `sys.exit(R.close(...))`."""
    return (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
            and ast.unparse(node.value.func) == "sys.exit" and len(node.value.args) == 1
            and isinstance(node.value.args[0], ast.Call)
            and ast.unparse(node.value.args[0].func) == "R.close")


def split(source: str, tree: ast.Module | None = None):
    """(header statements, header hash, spans, tail statements) of a flat script.

    A `section` call inside a function, loop or branch is no boundary. A repeated
    title gets `#2`, `#3` and so on, in order. The tail is the closing
    `sys.exit(R.close(...))` when the script ends with one, else empty.
    """
    tree = tree or ast.parse(source)
    lines = source.splitlines(keepends=True)
    body = list(tree.body)
    tail = [body.pop()] if body and _is_close(body[-1]) else []
    cuts = [i for i, n in enumerate(body) if _title(n) is not None]
    first_line = (lambda n: min([n.lineno] + [d.lineno for d in getattr(n, "decorator_list", [])]))
    head_end = first_line(body[cuts[0]]) - 1 if cuts else (first_line(tail[0]) - 1 if tail else len(lines))
    header = body[:cuts[0]] if cuts else body
    header_hash = hashlib.sha1("".join(lines[:head_end]).encode()).hexdigest()
    spans, seen = [], {}
    stop = first_line(tail[0]) - 1 if tail else len(lines)
    for k, i in enumerate(cuts):
        j = cuts[k + 1] if k + 1 < len(cuts) else len(body)
        title = _title(body[i])
        seen[title] = seen.get(title, 0) + 1
        sid = title if seen[title] == 1 else f"{title}#{seen[title]}"
        lo = first_line(body[i])
        hi = first_line(body[j]) - 1 if j < len(body) else stop
        spans.append(Span(sid, title, body[i:j], lo, hi, "".join(lines[lo - 1:hi])))
    return header, header_hash, spans, tail


# ------------------------------------------------------------- static needs

def _root(e: ast.AST) -> str | None:
    while isinstance(e, (ast.Attribute, ast.Subscript, ast.Call)):
        e = e.func if isinstance(e, ast.Call) else e.value
    return e.id if isinstance(e, ast.Name) else None


def _dotted(e: ast.AST) -> str | None:
    parts = []
    while isinstance(e, ast.Attribute):
        parts.append(e.attr)
        e = e.value
    if not isinstance(e, ast.Name):
        return None
    return ".".join([e.id, *reversed(parts)])


def _aliases(tree: ast.Module) -> dict[str, str]:
    """Every name an import anywhere in the script binds, to the module path it names."""
    out: dict[str, str] = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                out[a.asname or a.name.split(".")[0]] = a.name if a.asname else a.name.split(".")[0]
        elif isinstance(n, ast.ImportFrom) and n.module and not n.level:
            for a in n.names:
                out[a.asname or a.name] = f"{n.module}.{a.name}"
    return out


def _resolve(e: ast.AST, aliases: dict[str, str]) -> str | None:
    d = _dotted(e)
    if d is None:
        return None
    head, _, rest = d.partition(".")
    base = aliases.get(head, head)
    return f"{base}.{rest}" if rest else base


def _families(node: ast.AST, aliases: dict[str, str]) -> tuple[set[str], set[str]]:
    """(families read, families set) by one expression or statement tree."""
    reads, sets = set(), set()
    for n in ast.walk(node):
        if not isinstance(n, ast.Attribute):
            continue
        full = _resolve(n, aliases) or ""
        if any(full == m or full.startswith(m + ".") for m in RNG_MODULES):
            if not any(full.startswith(m + ".") and full[len(m) + 1:][:1].isupper() for m in RNG_MODULES):
                reads.add("@random")
                sets.add("@random")  # a draw moves the generator as a seed does (carry rng-consume)
        for fam, roots in STATE_SETTERS.items():
            if any(full == r or full.startswith(r + ".") for r in roots):
                reads.add(fam)
    for n in ast.walk(node):
        target = None
        if isinstance(n, ast.Call):
            full = _resolve(n.func, aliases) or ""
            meth = full.rpartition(".")
            if meth[2] in INPLACE or full in {r for rs in STATE_SETTERS.values() for r in rs}:
                target = meth[0] if meth[2] in INPLACE else full
        elif isinstance(n, (ast.Assign, ast.AugAssign, ast.Delete)):
            for t in (n.targets if isinstance(n, (ast.Assign, ast.Delete)) else [n.target]):
                if isinstance(t, (ast.Subscript, ast.Attribute)):
                    target = _resolve(t.value if isinstance(t, ast.Subscript) else t, aliases)
        if target:
            for fam, roots in STATE_SETTERS.items():
                if any(target == r or target.startswith(r + ".") for r in roots):
                    sets.add(fam)
    return reads, sets


def _module_scope(stmts):
    """Nodes evaluated at module scope: not inside def/class/lambda bodies or comprehensions."""
    stack = list(reversed(stmts))
    while stack:
        n = stack.pop()
        yield n
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            stack.extend(reversed(n.decorator_list + n.args.defaults + [d for d in n.args.kw_defaults if d]))
            continue
        if isinstance(n, ast.ClassDef):
            stack.extend(reversed(n.decorator_list + n.bases + [k.value for k in n.keywords]))
            continue
        if isinstance(n, (ast.Lambda, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            stack.extend(w.target for w in ast.walk(n) if isinstance(w, ast.NamedExpr))
            continue
        stack.extend(reversed(list(ast.iter_child_nodes(n))))


def _function_effects(fn: ast.AST, aliases) -> tuple[set[str], set[str], set[str]]:
    """(module-level names it mutates, names it reads, names it calls) for one def body."""
    local = {a.arg for a in ast.walk(fn.args) if isinstance(a, ast.arg)} if hasattr(fn, "args") else set()
    glob = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Global):
            glob |= set(n.names)
        elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
            local.add(n.id)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n is not fn:
            local.add(n.name)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            local |= {(a.asname or a.name).split(".")[0] for a in n.names}
    local -= glob
    muts, reads, calls = set(glob), set(), set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id not in local:
            reads.add(n.id)
        if isinstance(n, ast.Call):
            if isinstance(n.func, ast.Name) and n.func.id not in local:
                calls.add(n.func.id)
            if isinstance(n.func, ast.Attribute) and n.func.attr in INPLACE:
                r = _root(n.func.value)
                if r and r not in local:
                    muts.add(r)
            if isinstance(n.func, ast.Name) and n.func.id == "setattr" and n.args:
                r = _root(n.args[0])
                if r and r not in local:
                    muts.add(r)
        if isinstance(n, (ast.Assign, ast.AugAssign, ast.Delete, ast.AnnAssign)):
            ts = n.targets if isinstance(n, (ast.Assign, ast.Delete)) else [n.target]
            for t in ts:
                for x in ast.walk(t):
                    if isinstance(x, (ast.Attribute, ast.Subscript)):
                        r = _root(x)
                        if r and r not in local:
                            muts.add(r)
    fr, fs = _families(fn, aliases)
    return muts | fs, reads | fr, calls


def static_effects(stmts: list, aliases: dict[str, str], funcs: dict) -> tuple[set, set, set]:
    """(names bound definitely, names bound in place or conditionally, names read) by one span.

    `funcs` maps each module-level function name defined so far to its
    (mutates, reads, calls) and is updated with the span's own defs; a call of
    a known function adds that function's effects, transitively.
    """
    definite, muts, reads = set(), set(), set()
    for top in stmts:
        if isinstance(top, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            definite.add(top.name)
            if not isinstance(top, ast.ClassDef):
                funcs[top.name] = _function_effects(top, aliases)
        elif isinstance(top, (ast.Import, ast.ImportFrom)):
            definite |= {(a.asname or a.name).split(".")[0] for a in top.names}
        elif isinstance(top, (ast.Assign, ast.AnnAssign)) and getattr(top, "value", None) is not None:
            ts = top.targets if isinstance(top, ast.Assign) else [top.target]
            definite |= {t.id for t in ts if isinstance(t, ast.Name)}
    called: set[str] = set()
    for n in _module_scope(stmts):
        if isinstance(n, ast.Name):
            (reads if isinstance(n.ctx, ast.Load) else muts).add(n.id)
        elif isinstance(n, ast.Global):
            muts |= set(n.names)
        elif isinstance(n, ast.Call):
            if isinstance(n.func, ast.Name):
                called.add(n.func.id)
                if n.func.id == "setattr" and n.args and _root(n.args[0]):
                    muts.add(_root(n.args[0]))
            elif isinstance(n.func, ast.Attribute) and n.func.attr in INPLACE and _root(n.func.value):
                muts.add(_root(n.func.value))
        elif isinstance(n, (ast.Attribute, ast.Subscript)) and isinstance(n.ctx, (ast.Store, ast.Del)):
            if _root(n):
                muts.add(_root(n))
    # Every name loaded anywhere in the span, def bodies included: a function
    # the span defines and calls later reads these too.
    for top in stmts:
        for n in ast.walk(top):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                reads.add(n.id)
    for top in stmts:
        fr, fs = _families(top, aliases)
        reads |= fr
        muts |= fs
    todo, done = list(called), set()
    while todo:
        f = todo.pop()
        if f in done or f not in funcs:
            continue
        done.add(f)
        m, r, c = funcs[f]
        muts |= m
        reads |= r
        todo.extend(c)
    muts -= definite & muts if False else set()
    return definite, muts - definite, reads


def static_needs(spans: list[Span], header: list, aliases: dict[str, str]) -> dict[str, set[str]]:
    """Each span's earlier spans by the static rule: the binders of the names it reads.

    A definite top-level rebinding resets a name's binders; an in-place or
    conditional binding adds to them. The header binds nothing a span can
    need (it always runs).
    """
    funcs: dict = {}
    static_effects(header, aliases, funcs)
    binders: dict[str, list[str]] = {}
    out: dict[str, set[str]] = {}
    for s in spans:
        definite, muts, reads = static_effects(s.stmts, aliases, funcs)
        out[s.id] = {b for n in reads for b in binders.get(n, ())}
        for n in muts:
            binders.setdefault(n, []).append(s.id)
        for n in definite:
            binders[n] = [s.id]
    return out


# --------------------------------------------------------------- the runner

def _flags(header: list) -> int:
    flags = 0
    for n in header:
        if isinstance(n, ast.ImportFrom) and n.module == "__future__":
            for a in n.names:
                flags |= getattr(_future, a.name).compiler_flag
    return flags


def _code(stmts: list, path: str, flags: int):
    return compile(ast.Module(body=stmts, type_ignores=[]), path, "exec", flags=flags, dont_inherit=True)


def run(script: str, plan: set[str] | None = None, recorder: "Recorder | None" = None,
        note: str = "") -> int:
    """Run `script` span by span in one namespace, as `python3 <script>` would.

    The header runs, then each span in order (all of them without a plan,
    only those named in `plan` with one), then the closing statement. Returns
    the script's exit status. `note` is the plan's reason, printed in the
    `CASES:` line with the count of spans executed.
    """
    path = os.path.abspath(script)
    source = open(path, encoding="utf-8").read()
    tree = ast.parse(source)
    header, _, spans, tail = split(source, tree)
    flags = _flags(header)
    module = types.ModuleType("__main__")
    module.__file__ = path
    module.__builtins__ = builtins
    saved_main, saved_argv = sys.modules.get("__main__"), sys.argv[:]
    sys.modules["__main__"] = module
    sys.argv[0] = path
    sys.path.insert(0, os.path.dirname(path))
    ns = module.__dict__
    rel = os.path.relpath(os.path.realpath(path), ROOT)
    ran = [s for s in spans if plan is None or s.id in plan]
    try:
        try:
            if recorder:
                recorder.begin("header", header, ns)
            exec(_code(header, path, flags), ns)
            for s in ran:
                if recorder:
                    recorder.begin(s.id, s.stmts, ns)
                exec(_code(s.stmts, path, flags), ns)
            if recorder:
                recorder.end(ns)
            if note:
                print(f"CASES: {'FULL' if plan is None else 'SCOPED'} {rel} -- {len(ran)} of {len(spans)} spans ({note})")
            elif plan is None:
                print(f"CASES: FULL {rel} -- {'recording' if recorder else 'no plan'}, {len(spans)} spans")
            else:
                print(f"CASES: SCOPED {rel} -- {len(ran)} of {len(spans)} spans")
            sys.stdout.flush()
            exec(_code(tail, path, flags), ns)
        except SystemExit as e:
            return e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        except BaseException:  # noqa: BLE001 - a raising script exits 1, as under python3
            import traceback
            traceback.print_exc()
            return 1
        finally:
            if recorder:
                recorder.end(ns)
        return 0
    finally:
        sys.modules["__main__"] = saved_main
        sys.argv[:] = saved_argv


# ------------------------------------------------------------- the recorder

def _fp(v) -> object:
    """A cheap fingerprint: identity, plus length and member identities for a container."""
    t = type(v)
    try:
        if t is list:
            return (id(v), len(v), hash(tuple(map(id, v))))
        if t is dict:
            return (id(v), len(v), hash(tuple(map(id, v))), hash(tuple(map(id, v.values()))))
        if t is set:
            return (id(v), len(v), hash(frozenset(map(id, v))))
    except Exception:  # noqa: BLE001 - a dict mutated under us still has an identity
        pass
    return id(v)


def _repo_modules() -> dict[str, types.ModuleType]:
    from closure import _rel  # the recorder's one path rule, shared with the script level
    out = {}
    for name, m in list(sys.modules.items()):
        f = getattr(m, "__file__", None)
        if f and name not in ("__main__", "case_select", "closure"):
            r = _rel(f)
            if r:
                out[name] = m
    return out


def _state() -> dict[str, object]:
    """Fingerprints of the shared process state the families name."""
    import logging
    import warnings
    out = {"@environ": hash(tuple(sorted(os.environ.items()))),
           "@syspath": hash(tuple(sys.path)),
           "@logging": (logging.root.level, tuple(map(id, logging.root.handlers)), logging.root.manager.disable),
           "@warnings": hash(tuple(map(repr, warnings.filters)))}
    try:
        import locale
        out["@locale"] = locale.setlocale(locale.LC_ALL, None)
    except Exception:  # noqa: BLE001
        pass
    import random
    out["@random"] = hash(random.getstate())
    np = sys.modules.get("numpy")
    if np is not None:
        try:
            st = np.random.get_state()
            out["@random"] = (out["@random"], hash(st[1].tobytes()), st[2])
        except Exception:  # noqa: BLE001
            pass
    return out


class Recorder:
    """Per-span read sets and dynamic moves, for one run of one script."""

    def __init__(self, script: str, source: str):
        from closure import _rel, unit_of
        self._rel, self._unit = _rel, unit_of
        self.script = script
        self.aliases = _aliases(ast.parse(source))
        self.units: dict[str, dict] = {}
        self.cur: str | None = None
        self.opened: set[str] = set()
        self.argv: list[list[str]] = []
        self.codes: set = set()
        self._imports: dict[str, dict[str, str]] = {}
        sys.addaudithook(self._hook)
        mon = sys.monitoring
        mon.use_tool_id(_TOOL_ID, "case_select")
        mon.register_callback(_TOOL_ID, mon.events.PY_START, self._start)
        mon.set_events(_TOOL_ID, mon.events.PY_START)

    def _hook(self, event, args):  # noqa: ANN001 - audit hook signature
        if self.cur is None:
            return
        try:
            if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
                r = self._rel(os.fsdecode(args[0]))
                if r:
                    self.opened.add(r)
            elif event in ("subprocess.Popen", "os.exec", "os.posix_spawn"):
                self.argv.append([os.fsdecode(a) for a in args[1]])
        except Exception:  # noqa: BLE001
            pass

    def _start(self, code, offset):  # noqa: ANN001 - monitoring callback signature
        if self.cur is not None:
            self.codes.add(code)
        return sys.monitoring.DISABLE

    def _file_unit(self, f: str | None) -> str | None:
        return self._rel(f) if f else None

    def _module_imports(self, f: str) -> dict[str, str]:
        """A repository file's module-level import bindings: bound name -> file unit."""
        if f in self._imports:
            return self._imports[f]
        out: dict[str, str] = {}
        try:
            tree = ast.parse(open(ROOT / f, encoding="utf-8").read())
        except (OSError, SyntaxError, ValueError):
            self._imports[f] = out
            return out
        for n in tree.body:
            pairs = []
            if isinstance(n, ast.Import):
                pairs = [((a.asname or a.name.split(".")[0]), a.name if a.asname else a.name.split(".")[0])
                         for a in n.names]
            elif isinstance(n, ast.ImportFrom):
                base = n.module or ""
                if n.level:
                    pkg = Path(f).parent
                    for _ in range(n.level - 1):
                        pkg = pkg.parent
                    m = next((name for name, mod in list(sys.modules.items())
                              if getattr(mod, "__file__", None)
                              and self._rel(mod.__file__) in (str(pkg / "__init__.py"),)), None)
                    base = f"{m}.{base}".rstrip(".") if m else base
                pairs = [((a.asname or a.name), f"{base}.{a.name}") for a in n.names]
                pairs += [((a.asname or a.name), base) for a in n.names]
            for bound, modname in pairs:
                mod = sys.modules.get(modname)
                u = self._file_unit(getattr(mod, "__file__", None)) if mod else None
                if u and bound not in out:
                    out[bound] = u
        self._imports[f] = out
        return out

    def _static_files(self, stmts: list, ns: dict) -> set[str]:
        files: set[str] = set()
        reached: set[str] = set()
        # The span's own names: a module, or an object defined in one.
        for top in stmts:
            for n in ast.walk(top):
                if not isinstance(n, (ast.Name, ast.Attribute)):
                    continue
                d = _dotted(n)
                if not d:
                    continue
                parts = d.split(".")
                obj = ns.get(parts[0], getattr(builtins, parts[0], None))
                for p in [None, *parts[1:]]:
                    if p is not None:
                        obj = getattr(obj, p, None) if not isinstance(obj, dict) else None
                    if obj is None:
                        break
                    mod = obj if isinstance(obj, types.ModuleType) else sys.modules.get(
                        getattr(obj, "__module__", "") or "")
                    u = self._file_unit(getattr(mod, "__file__", None)) if mod else None
                    if u:
                        reached.add(u)
        # Started code: each name it references that its module binds by import.
        for code in list(self.codes):
            u = self._file_unit(code.co_filename)
            if not u:
                continue
            files.add(u)
            imp = self._module_imports(u)
            for name in code.co_names:
                if name in imp:
                    reached.add(imp[name])
        # One more hop: the module-level imports of every module reached.
        for u in list(reached):
            files.add(u)
            files |= set(self._module_imports(u).values())
        return files

    def _snapshot(self, ns: dict):
        glob = {k: _fp(v) for k, v in list(ns.items()) if not k.startswith("__")}
        mods = {}
        for name, m in _repo_modules().items():
            try:
                mods[name] = {k: _fp(v) for k, v in list(vars(m).items()) if not k.startswith("__")}
            except Exception:  # noqa: BLE001
                pass
        return glob, mods, _state()

    def begin(self, sid: str, stmts: list, ns: dict) -> None:
        self.end(ns)
        self.before = self._snapshot(ns)
        self.opened, self.argv, self.codes = set(), [], set()
        self.stmts = stmts
        sys.monitoring.restart_events()
        self.t0 = time.monotonic()
        self.cur = sid

    def end(self, ns: dict) -> None:
        if self.cur is None:
            return
        sid, self.cur = self.cur, None
        seconds = time.monotonic() - self.t0
        files = set(self.opened) | self._static_files(self.stmts, ns)
        for argv in self.argv:
            for a in argv:
                r = self._rel(a)
                if r and (ROOT / r).exists():
                    files.add(r)
        g0, m0, s0 = self.before
        g1, m1, s1 = self._snapshot(ns)
        moved_names = {k for k in set(g0) | set(g1) if g0.get(k) != g1.get(k)}
        moved_mods = set()
        for name in set(m0) & set(m1):
            if m0[name] != m1[name]:
                u = self._file_unit(getattr(sys.modules.get(name), "__file__", None))
                if u:
                    moved_mods.add(u)
        moved_state = {k for k in s1 if s0.get(k) != s1.get(k)}
        self.units[sid] = {"files": {self._unit(f) for f in files}, "names": moved_names,
                           "mods": moved_mods, "state": moved_state, "seconds": round(seconds, 2)}

    def close(self) -> None:
        sys.monitoring.set_events(_TOOL_ID, 0)
        sys.monitoring.register_callback(_TOOL_ID, sys.monitoring.events.PY_START, None)
        sys.monitoring.free_tool_id(_TOOL_ID)


def dynamic_needs(spans: list[Span], units: dict[str, dict], reads: dict[str, set[str]]) -> dict[str, set[str]]:
    """Each span's earlier spans by the recorded moves.

    A span needs every earlier span that moved a module-level name it reads, or
    a repository module in its `files`. A span that moved the RNG needs the
    last earlier span that moved it. Any other net move of shared process state
    is needed by every later span.
    """
    out: dict[str, set[str]] = {}
    name_movers: dict[str, list[str]] = {}
    mod_movers: dict[str, list[str]] = {}
    state_movers: list[str] = []
    last_rng = None
    for s in spans:
        u = units.get(s.id)
        if u is None:
            continue
        need = {b for n in reads.get(s.id, ()) for b in name_movers.get(n, ())}
        need |= {b for f in u["files"] for b in mod_movers.get(f, ())}
        need |= set(state_movers)
        if "@random" in u["state"] and last_rng:
            need.add(last_rng)
        out[s.id] = need
        for n in u["names"]:
            name_movers.setdefault(n, []).append(s.id)
        for f in u["mods"]:
            mod_movers.setdefault(f, []).append(s.id)
        if u["state"] - {"@random"}:
            state_movers.append(s.id)
        if "@random" in u["state"]:
            last_rng = s.id
    return out


# --------------------------------------------------------------- the table

def _git_blob(path: str) -> str:
    return subprocess.run(["git", "hash-object", path], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()


def _head() -> str:
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip()


def load(table: Path = TABLE) -> dict | None:
    """The table, or None when it is missing, unparseable or at another version."""
    try:
        d = json.loads(table.read_text())
    except (OSError, ValueError):
        return None
    return d if isinstance(d, dict) and d.get("version") == VERSION else None


def entry(table: dict, script: str) -> dict | None:
    """One script's entry with indices resolved to paths."""
    e = table.get("scripts", {}).get(script)
    if e is None:
        return None
    files = table["files"]
    return {"blob": e["blob"], "header_hash": e["header_hash"],
            "header": [files[i] for i in e["header"]],
            "spans": {k: {"hash": v["hash"], "files": [files[i] for i in v["files"]],
                          "needs": list(v["needs"]), "seconds": v["seconds"]}
                      for k, v in e["spans"].items()}}


def build_entry(script: str, spans: list[Span], header_hash: str, units: dict, needs: dict) -> dict:
    return {"blob": _git_blob(script), "header_hash": header_hash,
            "header": sorted(units.get("header", {}).get("files", ())),
            "spans": {s.id: {"hash": s.hash, "files": sorted(units.get(s.id, {}).get("files", ())),
                             "needs": sorted(needs.get(s.id, ())),
                             "seconds": units.get(s.id, {}).get("seconds", 0.0)} for s in spans}}


def union_entry(old: dict | None, new: dict) -> dict:
    """`new`, with each span whose text is unchanged keeping the old entry's files and needs too."""
    if not old:
        return new
    out = json.loads(json.dumps(new))
    if old.get("header_hash") == new["header_hash"]:
        out["header"] = sorted(set(old["header"]) | set(new["header"]))
    for sid, s in out["spans"].items():
        o = old["spans"].get(sid)
        if o and o["hash"] == s["hash"]:
            s["files"] = sorted(set(o["files"]) | set(s["files"]))
            s["needs"] = sorted(set(o["needs"]) | set(s["needs"]))
    return out


def dumps(entries: dict[str, dict], order: list[str] | None = None, recorded_at: str = "") -> str:
    """The table text: each path stored once, spans holding indices, one span per line.

    `order` is the previous table's path list. Its paths keep their indices
    and new paths are appended, so a re-recording moves only the lines of the
    spans it changed, and two branches that touch different spans merge as
    text. A path no entry uses is dropped only when `order` is None (a full
    re-derivation).
    """
    used = {f for e in entries.values()
            for f in e["header"] + [x for sp in e["spans"].values() for x in sp["files"]]}
    paths = list(order or [])
    paths += sorted(used - set(paths))
    ix = {q: n for n, q in enumerate(paths)}
    lines = ['{"version": %d,' % VERSION, ' "recorded_at": %s,' % json.dumps(recorded_at), ' "files": [']
    lines += ["  %s%s" % (json.dumps(q), "," if n < len(paths) - 1 else "") for n, q in enumerate(paths)]
    lines += [" ],", ' "scripts": {']
    for k, (script, e) in enumerate(sorted(entries.items())):
        lines.append("  %s: {" % json.dumps(script))
        lines.append('   "blob": %s, "header_hash": %s,' % (json.dumps(e["blob"]), json.dumps(e["header_hash"])))
        lines.append('   "header": %s,' % json.dumps(sorted(ix[f] for f in e["header"])))
        lines.append('   "spans": {')
        items = list(e["spans"].items())
        for n, (sid, sp) in enumerate(items):
            body = {"hash": sp["hash"], "files": sorted(ix[f] for f in sp["files"]),
                    "needs": sorted(sp["needs"]), "seconds": sp["seconds"]}
            lines.append("    %s: %s%s" % (json.dumps(sid), json.dumps(body, sort_keys=True),
                                         "," if n < len(items) - 1 else ""))
        lines.append("   }")
        lines.append("  }" + ("," if k < len(entries) - 1 else ""))
    lines += [" }", "}"]
    return "\n".join(lines) + "\n"


def save(entries: dict[str, dict], table: Path = TABLE, keep_order: bool = True) -> None:
    old = load(table) if keep_order else None
    table.write_text(dumps(entries, old["files"] if old else None, _head()))


def _entries(d: dict) -> dict[str, dict]:
    return {k: entry(d, k) for k in d.get("scripts", {})}


def merge_tables(base: str, ours: str, theirs: str) -> str:
    """Three-way merge of two table texts (the `ledgermerge` arm for this file).

    Per span: one side's entry when only that side changed it, and both sides'
    `files` and `needs` united when their text hashes agree. When both edited
    the span differently it takes ours, with `files` and `needs` united (the
    script itself conflicted and is re-recorded after). A span one side deleted
    while the other left it is gone. `blob` and `header_hash` follow the side
    that moved them, ours when both did: a blob that matches neither the merge
    base nor the head makes the script run whole until it is re-recorded.
    """
    parse = lambda t: _entries(json.loads(t)) if t.strip() else {}  # noqa: E731
    b, o, t = parse(base), parse(ours), parse(theirs)
    order = json.loads(ours)["files"] if ours.strip() else []
    out: dict[str, dict] = {}
    for script in sorted(set(o) | set(t)):
        bs, os_, ts = b.get(script), o.get(script), t.get(script)
        if os_ is None or ts is None:
            pick = os_ or ts
            if not (bs is not None and pick == bs):
                out[script] = pick
            continue
        bs = bs or {"blob": "", "header_hash": "", "header": [], "spans": {}}
        e = {}
        for key in ("blob", "header_hash"):
            e[key] = ts[key] if os_[key] == bs[key] else os_[key]
        e["header"] = sorted(set(os_["header"]) | set(ts["header"]))
        spans = {}
        for sid in list(os_["spans"]) + [x for x in ts["spans"] if x not in os_["spans"]]:
            bo, so, st = bs["spans"].get(sid), os_["spans"].get(sid), ts["spans"].get(sid)
            if so is None or st is None:
                one = so or st
                if bo is None or one != bo:
                    spans[sid] = one
                continue
            if so == bo:
                spans[sid] = st
            elif st == bo:
                spans[sid] = so
            else:
                spans[sid] = dict(so, files=sorted(set(so["files"]) | set(st["files"])),
                                  needs=sorted(set(so["needs"]) | set(st["needs"])),
                                  seconds=max(so["seconds"], st["seconds"]))
        e["spans"] = spans
        out[script] = e
    rec = max(json.loads(x).get("recorded_at", "") if x.strip() else "" for x in (ours, theirs))
    return dumps(out, order, rec)


def stats(script: str, table: Path = TABLE) -> int:
    """Print one script's selectivity figures from the table (the enumerator P2 plans from)."""
    import statistics
    d = load(table)
    rel = os.path.relpath(os.path.realpath(script), ROOT)
    e = entry(d, rel) if d else None
    if e is None:
        print(f"STATS: {rel} has no entry in {os.path.relpath(table, ROOT)}")
        return 1
    sp = e["spans"]
    files = [len(v["files"]) for v in sp.values()]
    needs = [len(v["needs"]) for v in sp.values()]
    cc = {f for v in sp.values() for f in v["files"] if f.startswith("custom_components/")}
    wide = sum(1 for v in sp.values()
               if sum(f.startswith("custom_components/") for f in v["files"]) > len(cc) / 2)
    print(f"STATS: {rel}: {len(sp)} spans; table {table.stat().st_size} bytes, {len(d['files'])} paths;"
          f" files/span median {statistics.median(files)} max {max(files)};"
          f" needs/span median {statistics.median(needs)} max {max(needs)};"
          f" {wide} spans read over half of the {len(cc)} custom_components files recorded;"
          f" span seconds {round(sum(v['seconds'] for v in sp.values()), 1)}")
    return 0


def record(script: str, union: bool, table: Path = TABLE) -> int:
    """Run `script` under the recorder and write its entry into the table."""
    rel = os.path.relpath(os.path.realpath(script), ROOT)
    source = open(script, encoding="utf-8").read()
    tree = ast.parse(source)
    header, header_hash, spans, _ = split(source, tree)
    rec = Recorder(rel, source)
    try:
        rc = run(script, None, rec)
    finally:
        rec.close()
    aliases = _aliases(tree)
    needs = static_needs(spans, header, aliases)
    funcs: dict = {}
    static_effects(header, aliases, funcs)
    reads = {s.id: static_effects(s.stmts, aliases, funcs)[2] for s in spans}
    for k, v in dynamic_needs(spans, rec.units, reads).items():
        needs.setdefault(k, set()).update(v)
    current = load(table) or {"version": VERSION, "files": [], "scripts": {}}
    entries = _entries(current)
    new = build_entry(rel, spans, header_hash, rec.units, needs)
    entries[rel] = union_entry(entries.get(rel), new) if union else new
    save(entries, table, keep_order=union)
    print(f"case_select: recorded {len(rec.units) - 1} span(s) of {rel} into "
          f"{os.path.relpath(table, ROOT)}{' (union)' if union else ''}; script exit {rc}")
    return rc


# ------------------------------------------------- the plan (#3885 item 2)

#: The share of the spans the diff cannot reach that a pull request runs.
FRACTION = 0.3
#: `<PR number>-<head sha>`, which tests.yml exports on a pull request only.
SEED_ENV = "HPO_CASE_SEED"
_SEED_SHAPE = re.compile(r"\A[1-9][0-9]*-[0-9a-f]{40}\Z")
#: What every span runs through: a change here can move any span's outcome.
RUNNER_FILES = ("tests/harness.py", "tests/hastub/")


def draw(ids, seed: str, fraction: float = FRACTION) -> set[str]:
    """The ids a seed picks: sha256(seed NUL id) below the fraction's share of 2**64.

    Keyed on the id, never the ordinal, so an inserted span moves no other draw.
    """
    cut = int(fraction * 2 ** 64)
    return {i for i in ids
            if int(hashlib.sha256(f"{seed}\0{i}".encode()).hexdigest()[:16], 16) < cut}


def _closure_star(start: set[str], edges: dict[str, set[str]]) -> set[str]:
    out, todo = set(start), list(start)
    while todo:
        for n in edges.get(todo.pop(), ()):
            if n not in out:
                out.add(n)
                todo.append(n)
    return out


def plan(script: str, changed: list[str], seed: str | None, fraction: float = FRACTION,
         table: Path = TABLE, scope: dict | None = None, closures: dict | None = None) -> dict:
    """Which spans of `script` a pull request runs, each with the rule that chose it.

    `{"mode": "full", "reason": ...}` when any fail-safe holds; else
    `{"mode": "scoped", "rules": {id: rule}, ...}` where
    run = back*(diff | edited | forward(diff | edited) | sample(rest)):
    `diff` a span whose recorded files meet a changed unit, `edited` a span
    the table lacks or whose text moved, `forward` a span needing one of
    those, `sample` the seeded draw over every other span, and `needed` the
    producers of anything selected. A span the diff reaches is never drawn.
    `scope` and `closures` default to `tests/closure.py`'s plan for `changed`
    and `tests/closures.json`'s read sets.
    """
    import closure  # noqa: PLC0415 - a sibling module, imported where the plan needs it

    rel = os.path.relpath(os.path.realpath(script), ROOT)
    full = lambda why: {"mode": "full", "reason": why, "script": rel}  # noqa: E731
    if not seed or not _SEED_SHAPE.match(seed):
        return full(f"no seed of shape <PR number>-<head sha> in {SEED_ENV}")
    src = open(script, encoding="utf-8").read()
    tree = ast.parse(src)
    header, header_hash, spans, _ = split(src, tree)
    if not spans:
        return full("the splitter finds no span")
    d = load(table)
    e = entry(d, rel) if d else None
    if e is None:
        return full(f"{os.path.relpath(table, ROOT)} has no entry for {rel} at version {VERSION}")
    if e["header_hash"] != header_hash:
        return full("the header's text differs from the table's header_hash")
    if not changed:
        return full("no changed files could be determined")
    units = {closure.unit_of(f) for f in changed}
    gate = sorted(f for f in changed if closure.is_gate_file(f)
                  or any(f == r or (r.endswith("/") and f.startswith(r)) for r in RUNNER_FILES))
    if gate:
        return full(f"{gate[0]} changes how every span runs")
    scope = closure.select(sorted(changed)) if scope is None else scope
    if scope.get("mode") != "scoped":
        return full(f"the script-level scope is FULL: {scope.get('reason')}")
    hit = sorted(units & set(e["header"]))
    if hit:
        return full(f"the header reads {hit[0]}, and a span may read what the header built from it")
    recorded = set(e["header"]) | {f for v in e["spans"].values() for f in v["files"]}
    if closures is None:
        closures = json.loads(closure.CLOSURES.read_text())["closures"]
    stray = sorted(units & set(closures.get(rel, ())) - recorded)
    if stray:
        return full(f"{stray[0]} is in the script's closure and in no span's recording")
    titles: dict[str, list[Span]] = {}
    for s in spans:
        titles.setdefault(s.title, []).append(s)
    for t, group in titles.items():
        moved = [s for s in group if s.id not in e["spans"] or e["spans"][s.id]["hash"] != s.hash]
        if len(group) > 1 and moved:
            return full(f"the repeated title {t!r} has a moved instance, so its ids may not match the table")
    ids = [s.id for s in spans]
    sn = static_needs(spans, header, _aliases(tree))
    needs = {s.id: (sn.get(s.id, set()) | set(e["spans"].get(s.id, {}).get("needs", ()))) & set(ids)
             for s in spans}
    feeds: dict[str, set[str]] = {}
    for k, v in needs.items():
        for n in v:
            feeds.setdefault(n, set()).add(k)
    rules: dict[str, str] = {}
    for s in spans:
        t = e["spans"].get(s.id)
        if t is None or t["hash"] != s.hash:
            rules[s.id] = "edited"
        elif units & set(t["files"]):
            rules[s.id] = "diff"
    for i in _closure_star(set(rules), feeds) - set(rules):
        rules[i] = "forward"
    for i in draw([i for i in ids if i not in rules], seed, fraction):
        rules[i] = "sample"
    for i in _closure_star(set(rules), needs) - set(rules):
        rules[i] = "needed"
    count = {r: sum(1 for v in rules.values() if v == r)
             for r in ("diff", "edited", "forward", "sample", "needed")}
    return {"mode": "scoped", "script": rel, "seed": seed, "fraction": fraction, "n": len(ids),
            "rules": {i: rules[i] for i in ids if i in rules}, "count": count}


def plan_lines(p: dict, base: str) -> list[str]:
    """The plan as the job log and its artifact carry it: the key line, then one line per span run."""
    if p["mode"] != "scoped":
        return [f"CASES: PLAN {p['script']} -- FULL ({p['reason']})"]
    c = p["count"]
    head = (f"CASES: PLAN {p['script']} -- {len(p['rules'])} of {p['n']} spans (seed {p['seed']}, "
            f"fraction {p['fraction']}, base {base}, {c['diff']} diff, {c['edited']} edited, "
            f"{c['forward']} forward, {c['sample']} sample, {c['needed']} needed)")
    return [head] + [f"  case {r:<7} {i}" for i, r in p["rules"].items()]


def _merge_base(ref: str) -> str:
    r = subprocess.run(["git", "merge-base", ref, "HEAD"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() or ref


def sampled(script: str, seed: str | None, base: str, files: list[str] | None = None) -> int:
    """Plan `script` against the diff from `base` and run it: the pull request's entry point."""
    import closure  # noqa: PLC0415 - a sibling module, imported where the plan needs it

    mb = _merge_base(base)
    p = plan(script, files if files is not None else closure.changed_files(base), seed)
    print("\n".join(plan_lines(p, mb)))
    sys.stdout.flush()
    if p["mode"] != "scoped":
        return run(script, None, note=p["reason"])
    c = p["count"]
    note = (f"seed {seed}, fraction {p['fraction']}, base {mb}, {c['diff']} diff, {c['edited']} edited, "
            f"{c['forward']} forward, {c['sample']} sample, {c['needed']} needed")
    return run(script, set(p["rules"]), note=note)


# -------------------------------------------------------------- self-test

_FIXTURE = '''\
"""A synthetic flat script."""
from __future__ import annotations
import os
import random as _random
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cs_mod as M
from harness_stub import Results
R = Results("fixture")
L = []

def helper():
    return 1

R.section("alpha")
x = 1
R.check("alpha one", x == 1)

def nested():
    R.section("not a boundary")
for _ in range(1):
    R.section("not a boundary either")

R.section("beta reads a constant of M")
R.check("beta", M.LIMIT == 3)

R.section("gamma rebinds M.f")
M.f = lambda: 2

R.section("delta reads M")
R.check("delta", M.f() == 2)

R.section("bump calls into M")
M.bump()

R.section("count reads M")
R.check("count", M.COUNT == 1)

R.section("eps appends")
L.append(1)

R.section("zeta reads L")
R.check("zeta", L == [1])

R.section("alpha")
R.check("alpha two", x == 1)

R.section("seed")
_random.seed(7)

R.section("draw one")
a = _random.random()

R.section("no rng")
b = 2

R.section("draw two")
c = _random.random()
sys.exit(R.close("FIXTURE"))
'''

_MOD = "LIMIT = 3\nCOUNT = 0\n\ndef f():\n    return 1\n\ndef bump():\n    global COUNT\n    COUNT += 1\n"
_HARNESS = ('class Results:\n    def __init__(self, t): self.bad = 0; self.n = 0\n'
            '    def section(self, name): print("--", name)\n'
            '    def check(self, name, ok):\n        self.n += 1; self.bad += not ok\n'
            '        print(("  ok   " if ok else "  FAIL ") + name)\n'
            '    def close(self, label): print(self.n, label, self.bad); return 1 if self.bad else 0\n')


def _plan_rows(check, spans: list[Span], hh: str) -> None:
    """The plan over the fixture, against a synthetic table: each rule, each fail-safe, the draw."""
    import tempfile
    seed = "7-" + "a" * 40
    ids = [s.id for s in spans]
    check("draw: the same seed draws the same ids", draw(ids, seed) == draw(list(reversed(ids)), seed))
    many = [f"case {k}" for k in range(4000)]
    share = len(draw(many, seed)) / len(many)
    check("draw: the drawn share of 4000 ids is within 0.03 of FRACTION", abs(share - FRACTION) < 0.03, share)
    check("draw: another seed draws another set", draw(many, seed) != draw(many, "8-" + "a" * 40))
    check("draw: an inserted id moves no other id's draw (keyed on the id, never the ordinal)",
          draw(many, seed) == draw(["inserted"] + many, seed) - {"inserted"})
    check("draw: fraction 0 draws nothing and fraction 1 draws every id",
          draw(many, seed, 0.0) == set() and draw(many, seed, 1.0) == set(many))
    tmp = os.path.realpath(tempfile.mkdtemp(prefix="case-plan-"))
    try:
        script = os.path.join(tmp, "fx.py")
        open(script, "w").write(_FIXTURE)
        rel = os.path.relpath(script, ROOT)
        files = {s.id: ["m.py"] if s.id == "beta reads a constant of M" else ["h.py"] for s in spans}
        table = {"version": VERSION, "files": [], "scripts": {}}

        def make(spans_, header_hash=hh, header=("hdr.py",)):
            e = {"blob": "b", "header_hash": header_hash, "header": list(header),
                 "spans": {s.id: {"hash": s.hash, "files": files.get(s.id, []), "needs": [], "seconds": 1.0}
                           for s in spans_}}
            save({rel: e}, Path(tmp) / "t.json", keep_order=False)
            return Path(tmp) / "t.json"

        t = make(spans)
        ok = {"mode": "scoped"}
        cl = {rel: ["m.py", "h.py", "hdr.py", "stray.py"]}
        P = lambda ch, sd=seed, tb=t, sc=ok, fr=FRACTION: plan(script, ch, sd, fr, tb, sc, cl)  # noqa: E731
        p = P(["m.py"], fr=0.0)
        check("rule (i): a span whose recorded files meet the diff runs as diff; at fraction 0 nothing else does",
              p["mode"] == "scoped" and p["rules"] == {"beta reads a constant of M": "diff"}, p)
        p = P(["m.py"], fr=1.0)
        check("rule (iv): at fraction 1 every other span is drawn, and the diff span stays diff",
              p["mode"] == "scoped" and p["rules"]["beta reads a constant of M"] == "diff"
              and len(p["rules"]) == len(ids), p.get("count"))
        p = P(["m.py"])
        check("a seeded plan is byte-stable: the same inputs print the same lines",
              plan_lines(p, "b") == plan_lines(P(["m.py"]), "b"))
        drawn = {i for i, r in p["rules"].items() if r == "sample"}
        check("rule (iv): the sample is exactly the draw over the spans the diff cannot reach",
              drawn == draw([i for i in ids if i != "beta reads a constant of M"], seed)
              and p["rules"]["beta reads a constant of M"] == "diff", (drawn, p["rules"]))
        src = _FIXTURE.replace("L.append(1)\n", "L.append(1)  # edited\n")
        open(script, "w").write(src)
        p = P(["m.py"], fr=0.0)
        check("rule (ii)+(iii): an edited span runs as edited and the span reading what it binds runs as forward",
              p["rules"].get("eps appends") == "edited" and p["rules"].get("zeta reads L") == "forward", p["rules"])
        open(script, "w").write(_FIXTURE)
        only = {s.id: ["h.py"] if s.id == "alpha#2" else ["z.py"] for s in spans}
        files.clear()
        files.update(only)
        t2 = make(spans)
        p = plan(script, ["h.py"], seed, 0.0, t2, ok, cl)
        check("rule (v): alpha#2 alone in the diff pulls in alpha as needed",
              p["rules"] == {"alpha": "needed", "alpha#2": "diff"}, p["rules"])
        full = lambda p_: p_["mode"] == "full"  # noqa: E731
        check("fail-safe: no seed, or a seed of another shape, runs every span",
              full(P(["m.py"], sd=None)) and full(P(["m.py"], sd="abc")) and full(P(["m.py"], sd="7-" + "a" * 39)))
        check("fail-safe: a header edit runs every span", full(plan(script, ["m.py"], seed, FRACTION,
                                                                     make(spans, header_hash="x"), ok, cl)))
        check("fail-safe: a missing table runs every span",
              full(plan(script, ["m.py"], seed, FRACTION, Path(tmp) / "none.json", ok, cl)))
        check("fail-safe: a changed gate or runner file runs every span",
              all(full(P([f])) for f in ("tests/harness.py", "tests/hastub/x.py", "tests/case_select.py",
                                         "tests/case_closures.json", "tests/run.sh")))
        check("fail-safe: a script-level FULL scope runs every span", full(P(["m.py"], sc={"mode": "full"})))
        check("fail-safe: a changed file the header reads runs every span", full(P(["hdr.py"])))
        check("fail-safe: a changed file in the script's closure and in no span's recording runs every span",
              full(P(["stray.py"])))
        check("fail-safe: no changed file runs every span", full(P([])))
        dup = _FIXTURE.replace('R.section("seed")', 'R.section("alpha")')
        open(script, "w").write(dup)
        dsp = split(dup)[2]
        p = plan(script, ["m.py"], seed, FRACTION, make(dsp[:9]), ok, cl)
        check("fail-safe: a repeated title with a moved instance runs every span", full(p), p)
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def _self_test() -> int:
    import shutil
    import tempfile
    results: list[bool] = []

    def check(name: str, ok: bool, detail: object = "") -> None:
        results.append(bool(ok))
        print(("  ok   " if ok else "  FAIL ") + name + (f"  [{detail}]" if detail and not ok else ""))

    header, hh, spans, tail = split(_FIXTURE)
    ids = [s.id for s in spans]
    check("the splitter cuts at each top-level R.section literal, nested calls cut nothing",
          ids == ["alpha", "beta reads a constant of M", "gamma rebinds M.f", "delta reads M", "bump calls into M", "count reads M", "eps appends",
                  "zeta reads L", "alpha#2", "seed", "draw one", "no rng", "draw two"], ids)
    check("the closing sys.exit(R.close(...)) is the tail, not part of the last span",
          len(tail) == 1 and spans[-1].stmts[-1].lineno < tail[0].lineno)
    check("the header ends before the first span", all(n.lineno < spans[0].first for n in header))
    edited = split(_FIXTURE.replace("x = 1\n", "x = 1  # edited\n"))[2]
    check("an edit moves only its own span's hash",
          [a.id for a, b in zip(spans, edited) if a.hash != b.hash] == ["alpha"])
    check("a header edit moves the header hash and no span hash",
          split(_FIXTURE.replace("L = []", "L = [ ]"))[1] != hh
          and [s.hash for s in split(_FIXTURE.replace("L = []", "L = [ ]"))[2]] == [s.hash for s in spans])
    for real in SCRIPTS:
        p = ROOT / real
        if p.exists():
            src = p.read_text(encoding="utf-8")
            n = sum(1 for line in src.splitlines() if line.startswith("R.section"))
            got = len(split(src)[2])
            check(f"{real}: span count equals the count of lines starting R.section", got == n, (got, n))
    aliases = _aliases(ast.parse(_FIXTURE))
    sn = static_needs(spans, header, aliases)
    check("static: a span reading a name an earlier span binds needs it (alpha#2 reads x)",
          "alpha" in sn["alpha#2"], sn["alpha#2"])
    check("static: an in-place L.append binds L for a later reader (zeta needs eps)",
          "eps appends" in sn["zeta reads L"], sn["zeta reads L"])
    check("static: an attribute store binds its root (delta needs gamma)",
          "gamma rebinds M.f" in sn["delta reads M"], sn["delta reads M"])
    check("static: every RNG draw binds @random, so a draw needs the previous draw and the seeder",
          "draw one" in sn["draw two"] and "seed" in sn["draw one"] and "no rng" not in sn["draw two"],
          (sn["draw one"], sn["draw two"]))
    check("static: a span reading nothing earlier spans bind needs none (beta)",
          sn["beta reads a constant of M"] == set(), sn["beta reads a constant of M"])
    tmp = os.path.realpath(tempfile.mkdtemp(prefix="case-select-"))
    try:
        os.makedirs(os.path.join(tmp, "tests"))
        script = os.path.join(tmp, "tests", "fx.py")
        open(script, "w").write(_FIXTURE)
        open(os.path.join(tmp, "tests", "cs_mod.py"), "w").write(_MOD)
        open(os.path.join(tmp, "tests", "harness_stub.py"), "w").write(_HARNESS)
        env = dict(os.environ, PYTHONPATH=str(ROOT / "tests"))
        direct = subprocess.run([sys.executable, script], capture_output=True, text=True, env=env)
        spanwise = subprocess.run([sys.executable, __file__, "run", script], capture_output=True,
                                  text=True, env=env)
        keep = lambda out: [ln for ln in out.splitlines() if not ln.startswith("CASES:")]  # noqa: E731
        check("runner equivalence: a full-plan run prints what python3 <script> prints, exit status included",
              keep(spanwise.stdout) == direct.stdout.splitlines() and spanwise.returncode == direct.returncode == 0,
              (spanwise.stdout[-300:], spanwise.stderr[-300:], direct.stdout[-200:]))
        check("the runner prints one CASES: line", spanwise.stdout.count("CASES: FULL") == 1, spanwise.stdout[-200:])
        plan_file = os.path.join(tmp, "plan")
        open(plan_file, "w").write("eps appends\n")
        one = subprocess.run([sys.executable, __file__, "run", script, "--plan", plan_file],
                             capture_output=True, text=True, env=env)
        dropped = [ln for ln in direct.stdout.splitlines() if ln not in one.stdout.splitlines()]
        check("null control: a plan naming eps alone drops zeta's section and check lines",
              "-- eps appends" in one.stdout and "-- zeta reads L" not in one.stdout
              and "  ok   zeta" in dropped and "CASES: SCOPED" in one.stdout, (one.stdout[-400:], one.stderr[-300:]))
        # The recorder, in a child so its audit hook and monitoring slot die with it.
        tab = os.path.join(tmp, "table.json")
        rec = subprocess.run([sys.executable, "-c", (
            "import sys, json; sys.path.insert(0, %r); import case_select as C\n"
            "from pathlib import Path\n"
            "C.ROOT = Path(%r).resolve(); import closure; closure.ROOT = C.ROOT\n"
            "C._git_blob = lambda p: 'blob'; C._head = lambda: 'head'\n"
            "rc = C.record(%r, False, Path(%r))\n"
            "e = C.entry(C.load(Path(%r)), 'tests/fx.py'); print('ENTRY', json.dumps(e))\n"
            "sys.exit(rc)") % (str(ROOT / "tests"), tmp, script, tab, tab)],
            capture_output=True, text=True, env=dict(env, HPO_CS_NO_STATIC=os.environ.get("HPO_CS_NO_STATIC", "")),
            cwd=tmp)
        line = next((ln for ln in rec.stdout.splitlines() if ln.startswith("ENTRY ")), None)
        e = json.loads(line[6:]) if line else None
        check("record writes an entry for every span", e is not None and set(e["spans"]) == set(ids),
              (rec.stdout[-500:], rec.stderr[-800:]))
        if e:
            sp = e["spans"]
            check("recorder (c): beta reads a constant of M and runs no M code, yet its files hold M",
                  "tests/cs_mod.py" in sp["beta reads a constant of M"]["files"], sp["beta reads a constant of M"])
            check("recorder: gamma's rebinding of M.f gives delta needs [gamma]",
                  "gamma rebinds M.f" in sp["delta reads M"]["needs"], sp["delta reads M"])
            check("recorder: a module global moved inside M's own code (no store the AST sees) gives count needs [bump]",
                  "bump calls into M" in sp["count reads M"]["needs"]
                  and "bump calls into M" not in sn["count reads M"], (sp["count reads M"], sn["count reads M"]))
            check("recorder: every span carries its seconds", all("seconds" in v for v in sp.values()))
        u = Recorder.__new__(Recorder)
        dyn = dynamic_needs(spans, {
            s.id: {"files": set(), "names": set(), "mods": ({"tests/cs_mod.py"} if s.id == "gamma rebinds M.f" else set()),
                   "state": ({"@random"} if s.id in ("seed", "draw one", "draw two") else set()), "seconds": 0}
            for s in spans} | {"delta reads M": {"files": {"tests/cs_mod.py"}, "names": set(), "mods": set(),
                                                 "state": set(), "seconds": 0}}, {})
        del u
        check("dynamic: a module moved by gamma is needed by a span whose files hold it",
              "gamma rebinds M.f" in dyn["delta reads M"], dyn["delta reads M"])
        check("dynamic: an RNG mover needs the previous mover, skipping spans that did not draw",
              dyn["draw two"] == {"draw one"} and dyn["draw one"] == {"seed"}, (dyn["draw one"], dyn["draw two"]))
        old = {"blob": "b", "header_hash": "h", "header": ["a"], "spans": {
            "s": {"hash": "1", "files": ["x"], "needs": ["p"], "seconds": 1}, "t": {"hash": "2", "files": ["y"], "needs": [], "seconds": 1}}}
        new = {"blob": "c", "header_hash": "h", "header": ["b"], "spans": {
            "s": {"hash": "1", "files": ["z"], "needs": [], "seconds": 2}, "t": {"hash": "3", "files": ["w"], "needs": [], "seconds": 2}}}
        un = union_entry(old, new)
        check("union keeps an unchanged span's old files and needs, and replaces an edited one",
              un["spans"]["s"]["files"] == ["x", "z"] and un["spans"]["s"]["needs"] == ["p"]
              and un["spans"]["t"]["files"] == ["w"] and un["header"] == ["a", "b"], un)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    _plan_rows(check, spans, hh)
    sp = lambda h, fs, ns=(): {"hash": h, "files": list(fs), "needs": list(ns), "seconds": 1.0}  # noqa: E731
    ent = lambda spans, blob="b0": {"tests/x.py": {"blob": blob, "header_hash": "h",  # noqa: E731
                                                   "header": ["a.py"], "spans": spans}}
    base_t = dumps(ent({"s": sp("1", ["a.py"]), "t": sp("2", ["b.py"]), "u": sp("3", ["a.py"])}))
    ours_t = dumps(ent({"s": sp("1", ["a.py", "c.py"]), "t": sp("2", ["b.py"]), "u": sp("3", ["a.py"])}),
                   json.loads(base_t)["files"])
    theirs_t = dumps(ent({"s": sp("1", ["a.py", "d.py"]), "t": sp("9", ["e.py"], ["s"]),
                          "u": sp("3", ["a.py"])}, blob="b1"), json.loads(base_t)["files"])
    m = _entries(json.loads(merge_tables(base_t, ours_t, theirs_t)))["tests/x.py"]
    check("ledger arm: a span both sides re-recorded unites its files; a span one side edited takes that side",
          m["spans"]["s"]["files"] == ["a.py", "c.py", "d.py"] and m["spans"]["t"]["hash"] == "9"
          and m["spans"]["t"]["needs"] == ["s"] and m["blob"] == "b1", m)
    check("the writer keeps the previous table's path indices and appends new paths",
          json.loads(ours_t)["files"][:2] == json.loads(base_t)["files"][:2]
          and json.loads(ours_t)["files"][-1] == "c.py", json.loads(ours_t)["files"])
    base_l, ours_l, theirs_l = (x.splitlines() for x in (base_t, ours_t, theirs_t))
    check("one span per line: an edit of span t moves t's line and no other span's",
          [x for x in base_l if x.lstrip().startswith('"u":')] == [y for y in theirs_l if y.lstrip().startswith('"u":')]
          and [x for x in base_l if x.lstrip().startswith('"t":')] != [y for y in theirs_l if y.lstrip().startswith('"t":')],
          theirs_t)
    import importlib.util
    spec = importlib.util.spec_from_file_location("_lm", ROOT / "tools/merge/ledger_merge.py")
    lm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lm)
    drv = tempfile.mkdtemp(prefix="case-select-drv-")
    try:
        paths = [os.path.join(drv, n) for n in ("base", "ours", "theirs")]
        for q, text in zip(paths, (base_t, ours_t, theirs_t)):
            open(q, "w").write(text)
        rc = lm.run_driver(*paths, "7", "tests/case_closures.json")
        got = open(paths[1]).read()
    finally:
        shutil.rmtree(drv, ignore_errors=True)
    check("the ledgermerge driver routes tests/case_closures.json to merge_tables",
          rc == 0 and got == merge_tables(base_t, ours_t, theirs_t), (rc, got[:300]))
    failed = results.count(False)
    print(f"CASE-SELECT SELF-TEST: {'PASSED' if not failed else f'{failed} FAILED'} ({len(results)} checks)")
    return 1 if failed else 0


def _main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return _self_test()
    if len(argv) >= 2 and argv[0] == "stats":
        return stats(argv[1], Path(argv[argv.index("--table") + 1]) if "--table" in argv else TABLE)
    if argv[:1] == ["scripts"]:
        print("\n".join(SCRIPTS))
        return 0
    if len(argv) >= 2 and argv[0] == "split":
        src = open(argv[1], encoding="utf-8").read()
        header, hh, spans, _ = split(src)
        print(f"header 1-{spans[0].first - 1 if spans else '?'} {hh[:12]}")
        for s in spans:
            print(f"{s.first}-{s.last} {s.hash[:12]} {s.id}")
        return 0
    opt = lambda k, d=None: argv[argv.index(k) + 1] if k in argv else d  # noqa: E731
    seed = opt("--seed", os.environ.get(SEED_ENV))
    base = opt("--base", os.environ.get("GATE_SCOPE_BASE") or "origin/main")
    files = opt("--files")
    files = [ln.strip() for ln in open(files, encoding="utf-8") if ln.strip()] if files else None
    if len(argv) >= 2 and argv[0] == "plan":
        import closure  # noqa: PLC0415 - a sibling module, imported where the plan needs it
        p = plan(argv[1], files if files is not None else closure.changed_files(base), seed)
        print("\n".join(plan_lines(p, _merge_base(base))))
        return 0
    if len(argv) >= 2 and argv[0] == "run" and "--sample" in argv:
        return sampled(argv[1], seed, base, files)
    if len(argv) >= 2 and argv[0] == "run":
        chosen = None
        if "--plan" in argv:
            chosen = {ln.rstrip("\n") for ln in open(argv[argv.index("--plan") + 1], encoding="utf-8") if ln.strip()}
        return run(argv[1], chosen)
    if len(argv) >= 2 and argv[0] == "record":
        table = Path(argv[argv.index("--table") + 1]) if "--table" in argv else TABLE
        return record(argv[1], "--union" in argv, table)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
