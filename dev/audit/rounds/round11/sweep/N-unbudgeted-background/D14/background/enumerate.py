"""D14 sweep, class N-unbudgeted-background: list every background-work submit seam.

A seam is a call site in custom_components/heatpump_optimizer/**/*.py, inside a
function, of a primitive that runs work off the event loop or starts a solve:
    _await_optimize, _await_process, _await_off_loop      (the solve worker / executor)
    async_simulate                                        (a full what-if solve, 1-3 jobs)
    async_add_executor_job, run_in_executor               (HA / asyncio executor)
The infrastructure that implements those primitives (their own bodies) is
excluded.  For each seam it reports:
  enclosing   the function the call sits in
  roots       the package functions that (transitively, by name) reach it, cut
              at known trigger roots: the cycle (_async_update_data /
              async_run_optimization), services, setup, the debugger
  guard       tokens in the enclosing function or any caller on the path that
              bound in-flight work or a budget: `_running`, `.done()`, `Lock`,
              `in_flight`/`inflight`, `budget`, `limited_answer`, `last_at`,
              `semaphore`, a `return` under an `if` reading one of them
              (a heuristic, printed for the disposition, not a verdict)
Run:  python3 dev/audit/rounds/round11/D14/background/enumerate.py [--root DIR] [--json]
"""
import ast
import json
import os
import re
import sys

args = sys.argv[1:]
ROOT = args[args.index("--root") + 1] if "--root" in args else "custom_components/heatpump_optimizer"
PRIMS = {"_await_optimize", "_await_process", "_await_off_loop", "async_simulate",
         "async_add_executor_job", "run_in_executor"}
INFRA = {"_await_optimize", "_await_process", "_await_off_loop", "_run_in_process"}
GUARD = re.compile(r"_running\b|\.done\(\)|Lock\(|_lock\b|in_?flight|budget|limited_answer|last_at|[Ss]emaphore|_pending_task|_task is not None")
ROOTS = re.compile(r"^(_async_update_data|async_run_optimization|async_setup.*|_async_setup.*|handle_.*|_handle_.*|async_handle.*|.*_service.*)$")


def callee(n):
    f = n.func
    return f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else None


def code_only(n):
    """The function's code with comments and docstrings dropped, so a guard
    token must be code (a comment saying 'budget' is not a budget)."""
    import copy
    m = copy.deepcopy(n)
    for x in ast.walk(m):
        b = getattr(x, "body", None)
        if isinstance(b, list) and b and isinstance(b[0], ast.Expr) and isinstance(getattr(b[0], "value", None), ast.Constant) \
                and isinstance(b[0].value.value, str):
            x.body = b[1:] or [ast.Pass()]
    return ast.unparse(m)


def collect():
    funcs = {}  # (file, name) -> (node, src)
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = sorted(d for d in dn if d not in ("www", "translations", "__pycache__"))
        for f in sorted(fn):
            if not f.endswith(".py"):
                continue
            p = os.path.join(dp, f)
            text = open(p, encoding="utf-8").read()
            for n in ast.walk(ast.parse(text)):
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    funcs.setdefault((p, n.name), (n, code_only(n)))
    return funcs


def direct_calls(node):
    """Calls in this function body, not inside nested defs (those are their own functions)."""
    out = []
    stack = list(ast.iter_child_nodes(node))
    while stack:
        x = stack.pop()
        if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)) and x is not node:
            if isinstance(x, ast.Lambda):
                stack.extend(ast.iter_child_nodes(x))
            continue
        if isinstance(x, ast.Call):
            out.append(x)
        stack.extend(ast.iter_child_nodes(x))
    return out


def seams():
    funcs = collect()
    callers = {}
    for (p, name), (node, _) in funcs.items():
        for c in direct_calls(node):
            nm = callee(c)
            if nm:
                callers.setdefault(nm, set()).add((p, name))
        # functools.partial(self._x, ...) / references passed as values count as calls
        for x in ast.walk(node):
            if isinstance(x, ast.Attribute) and isinstance(x.ctx, ast.Load) and x.attr.startswith(("_maybe", "_async", "async_")):
                callers.setdefault(x.attr, set()).add((p, name))

    def path_up(name, seen=None, depth=0):
        seen = seen if seen is not None else set()
        if depth > 8 or name in seen:
            return set(), set()
        seen.add(name)
        if ROOTS.match(name):
            return {name}, set()
        roots, guards = set(), set()
        for (p, caller) in callers.get(name, ()):
            src = funcs[(p, caller)][1]
            g = set(GUARD.findall(src))
            r, gg = path_up(caller, seen, depth + 1)
            roots |= r or {caller + "(no root)"}
            guards |= {f"{caller}:{t}" for t in g} | gg
        return roots, guards

    out = []
    for (p, name), (node, src) in sorted(funcs.items()):
        if name in INFRA:
            continue
        for c in direct_calls(node):
            nm = callee(c)
            if nm in PRIMS:
                arg0 = ""
                if c.args:
                    a = c.args[-1] if nm in ("_await_process", "_await_off_loop", "async_add_executor_job") and len(c.args) >= 2 else c.args[0]
                    a = c.args[1] if nm in ("_await_process", "_await_off_loop", "async_add_executor_job", "run_in_executor") and len(c.args) >= 2 else a
                    arg0 = ast.unparse(a)[:60]
                own = sorted(set(GUARD.findall(src)))
                roots, guards = path_up(name)
                out.append({"file": p, "line": c.lineno, "enclosing": name, "primitive": nm, "job": arg0,
                            "own_guard": own, "path_guards": sorted(guards)[:6], "roots": sorted(roots)[:6]})
    return out


if __name__ == "__main__":
    s = seams()
    if "--json" in args:
        print(json.dumps(s, indent=1))
    else:
        for x in s:
            print(f"{x['file']}:{x['line']}  {x['enclosing']} -> {x['primitive']}({x['job']})  own_guard={x['own_guard']}  roots={x['roots']}  path_guards={x['path_guards']}")
        print(f"RESULT seams={len(s)} count")
        print(f"RESULT unguarded={sum(not x['own_guard'] for x in s)} count")
