#!/usr/bin/env python3
"""Review driver: extract the stale-path arm's functions and constants VERBATIM
from tests/entities.py (via ast) and run them against the block's claims.

This is the reviewer's own instrument (fix-review.md step 9/14): it runs the
tree's actual code, not a paraphrase, so the numbers below are the tree's.
"""
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

WANT_FUNCS = {
    "_sp_bind_names", "_sp_scope_map", "_sp_args", "_sp_bindings",
    "_sp_reach", "_sp_path_literal", "_sp_attr_bound", "_sp_literals",
    "_sp_opens", "_sp_path_join",
}
WANT_CONSTS = {
    "_SP_SCOPE_NODES", "_SP_FN_SCOPES", "_SP_TOPS", "_SP_OPENS",
    "_SP_READS", "_SP_JOIN_MODULES",
}

ENTITIES = Path("tests/entities.py")


def extract(entities_path):
    tree = ast.parse(entities_path.read_text())
    stmts = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in WANT_FUNCS:
                stmts.append(node)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if (len(targets) == 1 and isinstance(targets[0], ast.Name)
                    and targets[0].id in WANT_CONSTS):
                stmts.append(node)
    mod = ast.Module(body=stmts, type_ignores=[])
    ast.fix_missing_locations(mod)
    return mod


def main():
    sys.path.insert(0, "tests")
    from layout import canon as _layout_canon, locate as _layout_locate

    mod = extract(ENTITIES)
    ns = {
        "ast": ast, "re": re, "Path": Path, "subprocess": subprocess,
        "sys": sys, "json": json, "os": __import__("os"),
        "_layout_canon": _layout_canon, "_layout_locate": _layout_locate,
    }
    code = compile(mod, "tests/entities.py", "exec")
    exec(code, ns)

    # The planted stale literal, same predicate as the tree.
    layout = json.loads(Path("tests/layout.json").read_text())
    sp_old = next(r["old"] for r in layout["retired"]
                  if r["new"] and not r["old"].endswith("/") and Path(r["new"]).is_file())
    ns["_sp_old"] = sp_old
    print(f"RESULT sp_old={sp_old!r}")

    probe = "\nimport os\nfrom pathlib import Path\n"
    opens = ns["_sp_opens"]
    literals = ns["_sp_literals"]
    attr_bound = ns["_sp_attr_bound"]

    def opened(src):
        return opens(src, sp_old)

    # 1. Minimal global / nonlocal sources from the PR body.
    global_src = f"_G = None\ndef load():\n    global _G\n    _G = {sp_old!r}\n_X = open(_G)\n"
    nonlocal_src = (f"def _outer():\n    _P = ''\n    def _inner():\n"
                    f"        nonlocal _P\n        _P = {sp_old!r}\n    _X = open(_P)\n")
    print(f"RESULT minimal-global-resolves={opened(global_src)}")
    print(f"RESULT minimal-nonlocal-resolves={opened(nonlocal_src)}")

    # 2. Enumerator: 25 escape shapes all read as opens; 3 held read as no-open.
    escapes = {
        "two-hop alias": f"_A = {sp_old!r}\n_B = _A\n_X = open(_B)\n",
        "two-hop alias via join": f"_A = {sp_old!r}\n_B = _A\n_X = os.path.join('.', _B)\n",
        "pathlib / then read_text": f"_X = (Path('.') / {sp_old!r}).read_text()\n",
        "pathlib / via a name then read_text": f"_P = Path('.') / {sp_old!r}\n_X = _P.read_text()\n",
        "pathlib / then open": f"_X = (Path('.') / {sp_old!r}).open()\n",
        "pathlib / via a name then open": f"_P = Path('.') / {sp_old!r}\n_X = _P.open()\n",
        "f-string root prefix": f"_X = open(f\"{{os.getcwd()}}/{sp_old}\")\n",
        "dict value then subscript": f"_C = {{'k': {sp_old!r}}}\n_X = open(_C['k'])\n",
        "tuple-unpack assign": f"_A, _B = {sp_old!r}, 'x'\n_X = open(_A)\n",
        "annotated assign": f"_A: str = {sp_old!r}\n_X = open(_A)\n",
        "for target": f"for _P in ({sp_old!r},):\n    _X = open(_P)\n",
        "walrus": f"if (_P := {sp_old!r}):\n    _X = open(_P)\n",
        "augmented assign": f"_P = ''\n_P += {sp_old!r}\n_X = open(_P)\n",
        "parameter default": f"def _f(_p={sp_old!r}):\n    return open(_p)\n_X = _f()\n",
        "with ... as": f"with Path('.') / {sp_old!r} as _P:\n    _X = _P.read_text()\n",
        "self attribute": f"class _C:\n    def m(self):\n        self._P = {sp_old!r}\n"
                          f"        _X = open(self._P)\n",
        "list element then subscript": f"_L = [{sp_old!r}]\n_X = open(_L[0])\n",
        "nested dict subscript": f"_C = {{'a': {{'b': {sp_old!r}}}}}\n_X = open(_C['a']['b'])\n",
        "for tuple target": f"for _A, _B in (({sp_old!r}, 'x'),):\n    _X = open(_A)\n",
        "for over a list": f"for _P in [{sp_old!r}]:\n    _X = open(_P)\n",
        "kwonly default": f"def _f(*, _p={sp_old!r}):\n    return open(_p)\n_X = _f()\n",
        "lambda default": f"_f = lambda _p={sp_old!r}: open(_p)\n",
        "joinpath then read_text": f"_X = Path('.').joinpath({sp_old!r}).read_text()\n",
        "global binding": f"_G = None\ndef _load():\n    global _G\n"
                          f"    _G = {sp_old!r}\n_X = open(_G)\n",
        "nonlocal binding": f"def _outer():\n    _P = ''\n    def _inner():\n"
                            f"        nonlocal _P\n        _P = {sp_old!r}\n    _X = open(_P)\n",
    }
    held = {
        "held tuple": f"_X = ({sp_old!r},)\n",
        "held set": f"_S = {{{sp_old!r}}}\n",
        "held comparison": f"_X = ('x' == {sp_old!r})\n",
    }
    missed = sorted(k for k, p in escapes.items() if not opened(p))
    held_open = sorted(k for k, p in held.items() if opened(p))
    print(f"RESULT escapes-count={len(escapes)} missed={missed}")
    print(f"RESULT held-count={len(held)} held-open={held_open}")

    # 3. Census: planted pair fires; attr_bound returns [] over cited corpus.
    planted = (attr_bound("class _C:\n    def __init__(self):\n"
                          f"        self._p = {sp_old!r}\n"
                          "    def m(self):\n        return open(self._p)\n")
               + attr_bound(f"class C:\n    P = {sp_old!r}\n_X = open(C.P)\n"))
    benign = attr_bound("class _C:\n    def __init__(self):\n"
                        f"        self._x = 'not-a-path'\n"
                        "    def m(self):\n        return open(self._x)\n")
    print(f"RESULT census-planted={len(planted)} planted={planted}")
    print(f"RESULT census-benign={len(benign)}")

    # Store the namespace for mutation use.
    ns["_probe"] = probe
    ns["_escapes"] = escapes
    ns["_held"] = held
    ns["_sp_old"] = sp_old
    return ns


if __name__ == "__main__":
    main()
