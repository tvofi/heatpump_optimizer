"""Shared, deterministic edit helpers for the perturbation scripts.

Every helper asserts its anchor exists exactly once, so a script run against
a tree that is not baseline 7952d8f9 fails loudly instead of editing the
wrong place. Scripts are invoked as ``python3 <script> <worktree>``.
"""
from __future__ import annotations

import ast
import json
import sys
import textwrap
from pathlib import Path

PKG = "custom_components/heatpump_optimizer"
COORD = f"{PKG}/coordinator.py"
COORD_CLASS = "HeatPumpOptimizerCoordinator"


def wt() -> Path:
    return Path(sys.argv[1]).resolve()


def read(rel: str) -> str:
    return (wt() / rel).read_text()


def write(rel: str, text: str) -> None:
    (wt() / rel).write_text(text)


def replace_once(text: str, old: str, new: str) -> str:
    n = text.count(old)
    assert n == 1, f"anchor found {n} times: {old[:80]!r}"
    return text.replace(old, new)


def edit(rel: str, old: str, new: str) -> None:
    write(rel, replace_once(read(rel), old, new))


# -- seam map -----------------------------------------------------------------

def seam_set(name: str, seam: str) -> None:
    p = wt() / "tests/seam_map.json"
    d = json.loads(p.read_text())
    d["seams"][name] = seam
    d["seams"] = dict(sorted(d["seams"].items()))
    p.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")


def seam_drop(*names: str) -> None:
    p = wt() / "tests/seam_map.json"
    d = json.loads(p.read_text())
    for n in names:
        del d["seams"][n]
    p.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")


# -- AST addressing -------------------------------------------------------------

def find_class(tree: ast.AST, cls: str) -> ast.ClassDef:
    hits = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == cls]
    assert len(hits) == 1, (cls, len(hits))
    return hits[0]


def find_method(src: str, cls: str | None, name: str):
    tree = ast.parse(src)
    body = find_class(tree, cls).body if cls else tree.body
    hits = [n for n in body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name]
    assert len(hits) == 1, (cls, name, len(hits))
    return hits[0]


def def_start(node) -> int:
    return min([d.lineno for d in node.decorator_list] + [node.lineno])


def method_text(src: str, cls: str | None, name: str) -> str:
    n = find_method(src, cls, name)
    lines = src.splitlines(keepends=True)
    return "".join(lines[def_start(n) - 1:n.end_lineno])


def remove_method(src: str, cls: str | None, name: str) -> str:
    n = find_method(src, cls, name)
    lines = src.splitlines(keepends=True)
    return "".join(lines[:def_start(n) - 1] + lines[n.end_lineno:])


def insert_after_method(src: str, cls: str | None, name: str, text: str) -> str:
    n = find_method(src, cls, name)
    lines = src.splitlines(keepends=True)
    return "".join(lines[:n.end_lineno] + ["\n", text if text.endswith("\n") else text + "\n"] + lines[n.end_lineno:])


# -- tail extraction (the pass-through chain of B3) ----------------------------

_SCOPES = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp, ast.Lambda,
           ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def _walk_scope(node):
    """ast.walk that does not descend into nested scopes (their names are theirs)."""
    todo = [node]
    while todo:
        n = todo.pop()
        yield n
        if n is not node and isinstance(n, _SCOPES):
            continue
        todo.extend(ast.iter_child_nodes(n))


def _bound_names(stmts) -> set[str]:
    out: set[str] = set()
    for s in stmts:
        for n in _walk_scope(s):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                out.add(n.id)
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                out.add(n.name)
            elif isinstance(n, ast.ExceptHandler) and n.name:
                out.add(n.name)
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                for a in n.names:
                    out.add((a.asname or a.name).split(".")[0])
    return out


def _definitely_bound(fn, stmts) -> set[str]:
    """Params plus names bound by a top-level simple statement (not inside if/for/try)."""
    out = {a.arg for a in fn.args.args + fn.args.kwonlyargs + fn.args.posonlyargs}
    if fn.args.vararg:
        out.add(fn.args.vararg.arg)
    if fn.args.kwarg:
        out.add(fn.args.kwarg.arg)
    for s in stmts:
        if isinstance(s, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Expr, ast.With, ast.AsyncWith,
                          ast.FunctionDef, ast.AsyncFunctionDef, ast.Import, ast.ImportFrom)):
            if isinstance(s, ast.AnnAssign) and s.value is None:
                continue
            out |= _bound_names([s])
    return out


def _loaded(stmts) -> set[str]:
    return {n.id for s in stmts for n in ast.walk(s) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}


def tail_cut_ok(fn, k: int) -> tuple[bool, list[str]]:
    body = fn.body
    prefix, tail = body[:k], body[k:]
    if any(isinstance(n, (ast.Global, ast.Nonlocal, ast.Yield, ast.YieldFrom)) for s in body for n in ast.walk(s)):
        return False, []
    if any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "super" for s in tail for n in ast.walk(s)):
        return False, []
    params_all = {a.arg for a in fn.args.args + fn.args.kwonlyargs + fn.args.posonlyargs}
    local_before = _bound_names(prefix) | params_all
    needed = sorted((_loaded(tail) & local_before))
    # closures defined in the prefix must not read names the tail rebinds
    rebound = _bound_names(tail)
    for s in prefix:
        for n in ast.walk(s):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)) and _loaded([n]) & rebound:
                return False, needed
    if not set(needed) <= _definitely_bound(fn, prefix):
        return False, needed
    return True, needed


def tail_extract(src: str, cls: str, name: str, k: int, new_name: str) -> tuple[str, str]:
    """Move statements body[k:] of ``cls.name`` into a new method ``new_name``.

    The original ends in ``return [await] self.new_name(<live locals>)``. Pure
    tail extraction: early returns inside the tail stay correct, nothing flows
    back. Returns (new_src, the new method's name)."""
    fn = find_method(src, cls, name)
    ok, needed = tail_cut_ok(fn, k)
    assert ok, (name, k, needed)
    needed = [n for n in needed if n != "self"]
    lines = src.splitlines(keepends=True)
    tail_start = fn.body[k].lineno
    # comments directly above the first tail statement travel with it
    while lines[tail_start - 2].strip().startswith("#"):
        tail_start -= 1
    tail_end = fn.end_lineno
    tail_lines = lines[tail_start - 1:tail_end]
    indent = " " * fn.body[0].col_offset
    has_await = any(isinstance(n, (ast.Await, ast.AsyncFor, ast.AsyncWith)) for s in fn.body[k:] for n in ast.walk(s))
    is_async = has_await
    call = f"self.{new_name}({', '.join(needed)})"
    ret = f"{indent}return {'await ' if is_async else ''}{call}\n"
    def_indent = " " * fn.col_offset
    header = f"{def_indent}{'async ' if is_async else ''}def {new_name}(self{''.join(', ' + n for n in needed)}):  # type: ignore[no-untyped-def]\n"
    new_fn = [header] + tail_lines
    out = lines[:tail_start - 1] + [ret] + lines[tail_end:]
    # insert the new method right after the (now shortened) original
    shortened_end = tail_start - 1 + 1
    out = out[:shortened_end] + ["\n"] + new_fn + out[shortened_end:]
    return "".join(out), new_name


def pick_cuts(src: str, cls: str, name: str, fractions=(0.25, 0.5, 0.75)) -> list[int]:
    """Top-level statement indices nearest each line fraction where a tail cut is legal."""
    fn = find_method(src, cls, name)
    n = len(fn.body)
    span = fn.end_lineno - fn.lineno
    cuts = []
    for f in fractions:
        target = fn.lineno + f * span
        cands = sorted(range(1, n), key=lambda i: abs(fn.body[i].lineno - target))
        for i in cands:
            if tail_cut_ok(fn, i)[0] and i not in cuts:
                cuts.append(i)
                break
    return sorted(cuts)


def dedent_block(text: str, levels: int = 1) -> str:
    return textwrap.dedent(text) if levels else text
