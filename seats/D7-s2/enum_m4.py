"""D7.M4 enumerator (round 11, D7-s2): the implied-order and context-holder surface, one per line.

Three families, each by an AST rule over custom_components/heatpump_optimizer/*.py:
  solve_state:<attr>      an attribute HeatPumpOptimizer writes on ``self`` outside __init__
                          (per-solve state a later read inherits: last_buffer_trajectory's
                          descendants), plus any ``<x>._prev_shipped_plan`` written from outside;
  ctx_held:<file>:<func>  an async function that binds the coordinator context
                          (``_ctx_of(...)`` / ``getattr(..., "_ctx", ...)``) and reads the bound
                          name after an ``await``: a holder that may see a superseded context;
                          suffixed ``writes_back`` when it republishes from that binding after
                          the await (``<ctx>.publish(`` / ``replace(<ctx>`` / ``._ctx =``);
  ctx_inplace:<file>:<line>:<member>.<field>
                          an assignment into a field of a context member
                          (``._opt_config`` / ``._thermal_params`` / ``._current_state`` /
                          ``._config``): an edit every context sharing that member sees.

Run: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D7/s2/enum_m4.py
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692: 17 lines (7 solve_state, 8 ctx_held, 2 ctx_inplace).
"""
from __future__ import annotations

import ast
import glob

PKG = "custom_components/heatpump_optimizer"
MEMBERS = ("_opt_config", "_thermal_params", "_current_state", "_config")


def _is_ctx_bind(v: ast.AST) -> bool:
    if not isinstance(v, ast.Call):
        return False
    f = v.func
    if isinstance(f, ast.Name) and f.id == "_ctx_of":
        return True
    return (isinstance(f, ast.Name) and f.id == "getattr" and len(v.args) >= 2
            and isinstance(v.args[1], ast.Constant) and v.args[1].value == "_ctx")


def solve_state() -> list[str]:
    out = set()
    tree = ast.parse(open(f"{PKG}/optimizer.py").read())
    for cls in (n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "HeatPumpOptimizer"):
        for fn in cls.body:
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) or fn.name == "__init__":
                continue
            for n in ast.walk(fn):
                targets = n.targets if isinstance(n, ast.Assign) else (
                    [n.target] if isinstance(n, (ast.AugAssign, ast.AnnAssign)) else [])
                for t in targets:
                    for y in ast.walk(t):
                        if (isinstance(y, ast.Attribute) and isinstance(y.value, ast.Name)
                                and y.value.id == "self" and isinstance(y.ctx, ast.Store)):
                            out.add(y.attr)
    for path in glob.glob(f"{PKG}/*.py"):
        for n in ast.walk(ast.parse(open(path).read())):
            if isinstance(n, ast.Assign):
                for t in n.targets:
                    if isinstance(t, ast.Attribute) and t.attr == "_prev_shipped_plan":
                        out.add(t.attr)
    return [f"solve_state:{a}" for a in sorted(out)]


def ctx_held() -> list[str]:
    out = []
    for path in sorted(glob.glob(f"{PKG}/*.py")):
        tree = ast.parse(open(path).read())
        for fn in ast.walk(tree):
            if not isinstance(fn, ast.AsyncFunctionDef):
                continue
            events = []
            for n in ast.walk(fn):
                if isinstance(n, ast.Assign) and _is_ctx_bind(n.value):
                    for t in n.targets:
                        if isinstance(t, ast.Name):
                            events.append((n.lineno, 0, "bind", t.id))
                elif isinstance(n, (ast.Await, ast.AsyncFor, ast.AsyncWith)):
                    events.append((n.lineno, 1, "await", ""))
                elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                    events.append((n.lineno, 2, "use", n.id))
                elif isinstance(n, ast.Call):
                    f = n.func
                    if isinstance(f, ast.Attribute) and f.attr == "publish" and isinstance(f.value, ast.Name):
                        events.append((n.lineno, 3, "write", f.value.id))
                    if isinstance(f, ast.Name) and f.id == "replace" and n.args and isinstance(n.args[0], ast.Name):
                        events.append((n.lineno, 3, "write", n.args[0].id))
            events.sort()
            bound: dict[str, bool] = {}
            held, writes = set(), set()
            for _ln, _o, kind, name in events:
                if kind == "bind":
                    bound[name] = False
                elif kind == "await":
                    bound = {k: True for k in bound}
                elif kind == "use" and bound.get(name):
                    held.add(name)
                elif kind == "write" and bound.get(name):
                    writes.add(name)
            if held:
                tag = ":writes_back" if writes else ""
                out.append(f"ctx_held:{path.rsplit('/', 1)[1]}:{fn.name}{tag}")
    return out


def ctx_inplace() -> list[str]:
    out = []
    for path in sorted(glob.glob(f"{PKG}/*.py")):
        for n in ast.walk(ast.parse(open(path).read())):
            targets = n.targets if isinstance(n, ast.Assign) else (
                [n.target] if isinstance(n, ast.AugAssign) else [])
            for t in targets:
                if (isinstance(t, ast.Attribute) and isinstance(t.value, ast.Attribute)
                        and t.value.attr in MEMBERS):
                    out.append(f"ctx_inplace:{path.rsplit('/', 1)[1]}:{n.lineno}:{t.value.attr}.{t.attr}")
    return out


def universe() -> list[str]:
    return solve_state() + ctx_held() + ctx_inplace()


if __name__ == "__main__":
    print("\n".join(universe()))
