#!/usr/bin/env python3
"""R10-FLOW-YIELD-PROBE: every one-node mutant of review_strength.py against its self-test.

    python3 dev/audit/harnesses/r10_review_strength_mutants.py [--jobs N] [--list] [--show-killed]

THE RULE (the enumeration, so a sibling cannot be missed). The file is parsed
with `ast`; every node of every module-level statement is visited except the
docstring, the imports, `ROOT`, `self_test` and its `_self_test_main`, type annotations
and the `__main__` guard, and each
operator class below yields one mutant per site and per replacement:

    ordering    `sorted(...)` -> `list(...)`; `max` <-> `min`; `any` <-> `all`;
                a slice's lone bound moved to the other side (`[-n:]` -> `[:-n]`);
                a unary minus dropped (`[-n:]` -> `[n:]`)
    comparison  `<` -> `<=`,`>`;  `<=` -> `<`,`>=`;  `>` -> `>=`,`<`;  `>=` -> `>`,`<=`;
                `==` <-> `!=`;  `in` <-> `not in`;  `is` <-> `is not`
    branch      every arm of an `and`/`or` dropped, and `and` <-> `or`; `not` dropped;
                every `if`/`while`/conditional-expression test forced True and
                forced False; every comprehension `if` dropped
    threshold   every int literal n -> n-1 and n+1; every float f -> f/2 and 2f
    class words every string literal -> "" (bar the human text: `help=`,
                `metavar=`, `description=`, and the arguments of `print`,
                `.error` and `SystemExit`); every element of a tuple, list or
                set literal dropped (so each REAL_CATCH word and each product
                prefix is its own mutant)
    arithmetic  `+` <-> `-`, `*` <-> `/`, `**` -> `*`, and the same in `+=` / `-=`
    statements  every statement in a body replaced by `pass`; every keyword
                argument of a call dropped (bar `help=`/`metavar=`/`description=`)

Each mutant is the whole module re-emitted by `ast.unparse` with that one node
changed, written into its own scratch root beside a copy of
tests/throwaway_git.py (what the self-test imports), and run as
`review_strength.py --self-test`. KILLED means a non-zero exit (or a 120 s
timeout); SURVIVED means exit 0. A mutant whose emitted module is
byte-identical to the unmutated emission is not a mutant and is not counted.
M0 is the unmutated emission, which must pass first, or nothing is run.

DISPOSED below names every survivor this harness accepts, keyed on the
function, the original node and its replacement, each with the reason the
self-test cannot or need not see it. Prints one line per survivor (and per
killed mutant with --show-killed), then
`RESULT mutants=<n> killed=<k> survived=<s> disposed=<d> undisposed=<u> stale=<x>`;
exit 1 when M0 fails, any survivor is undisposed, or a DISPOSED key matched
no survivor (stale -- a disposition that outlives its mutant blinds nothing,
but it hides that the file moved under it).
"""
from __future__ import annotations

import argparse
import ast
import copy
import os
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
TARGET = "tools/audit/seat/review_strength.py"
COPY = ("tests/throwaway_git.py", "dev/audit/rounds/round10/D13/yield-probe.md")
SKIP_DEFS = {"self_test", "_self_test_main"}
SKIP_ASSIGN = {"ROOT"}
TEXT_KW = {"help", "metavar", "description"}
TEXT_CALLS = {"print", "error", "SystemExit"}
CMP = {ast.Lt: (ast.LtE, ast.Gt), ast.LtE: (ast.Lt, ast.GtE), ast.Gt: (ast.GtE, ast.Lt),
       ast.GtE: (ast.Gt, ast.LtE), ast.Eq: (ast.NotEq,), ast.NotEq: (ast.Eq,),
       ast.In: (ast.NotIn,), ast.NotIn: (ast.In,), ast.Is: (ast.IsNot,), ast.IsNot: (ast.Is,)}
BIN = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.Div, ast.Div: ast.Mult, ast.Pow: ast.Mult}
SWAP_CALL = {"max": "min", "min": "max", "any": "all", "all": "any", "sorted": "list"}

# Survivors the self-test cannot or need not see, keyed "<function>: <node> -> <mutant>".
# Every entry says which of the two it is.
DISPOSED = {
    "load @ out.append(dict(pr=int(m[1]), t=when(t), kind=m[2], head=...: drop or arm ''":
        "equivalent: cls None and cls '' read alike everywhere: stratum's `or` and the REAL_CATCH membership test",
    "pr_facts @ for ln in git(repo, 'diff', '--numstat', mb, head, check=...: test mb -> True":
        "equivalent: with no merge base the size is '?' and product reads `files`, which a failed `git diff` leaves empty either way",
    "pr_facts @ a, d, f = ln.split('\\t', 2): 2 -> 3":
        'equivalent: `git diff --numstat` quotes any path holding a tab, so a line holds exactly two tabs',
    'pr_facts @ grp = groups.get(g[1]) if g else None: 1 -> 0':
        "equivalent: GROUP_RE's one group is its whole match, so g[0] == g[1]",
    "pr_facts @ for ln in git(repo, 'diff', '--numstat', mb, head, check=...: drop keyword check= of git":
        'equivalent: the diff runs only with a merge base, so both commits exist and it cannot exit non-zero',
    'guardrail @ return f"GUARDRAIL last {n} PRs (first verdict {first[las...: cdf < ALPHA [op 0: Lt -> LtE]':
        "equivalent: no binomial CDF lands exactly on 0.05 in floating point (none for N <= 5 on a 1e-5 p0 grid); strict 'below 0.05' is R13's wording",
    "main @ ap.add_argument('--repo', default=str(ROOT)): drop keyword default= of ap.add_argument":
        'unpinned: the default is the checkout the tool runs from; the fixture must pass --repo to be the repository read',
    "main @ ap.add_argument('--tree', default='origin/main'): drop keyword default= of ap.add_argument":
        "unpinned: the default is the real remote's main; the fixture has none and passes --tree",
    "main @ ap.add_argument('--window', action='append', default=[], ...: drop keyword default= of ap.add_argument":
        "equivalent: argparse's append default is None without it, and `not a.window` refuses None and [] alike",
    "main @ ap.add_argument('--tree', default='origin/main'): 'origin/main' -> ''":
        "unpinned: the default is the real remote's main; the fixture has none and passes --tree",
    "main @ name, span = w.split('=', 1): 1 -> 2":
        "equivalent: a window spec holds one '=' (names and ISO stamps hold none)",
    "main @ f, u = span.split('..', 1): 1 -> 2":
        "equivalent: an ISO stamp holds no '..', so a span holds one",
}


def _call_name(node: ast.Call) -> str:
    f = node.func
    return f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""


def _text_ids(tree: ast.AST) -> set[int]:
    """ids of string constants that are human text (help, error messages, prints, docstrings)."""
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if _call_name(node) in TEXT_CALLS:
                for sub in node.args:
                    out.update(id(x) for x in ast.walk(sub))
            for kw in node.keywords:
                if kw.arg in TEXT_KW:
                    out.update(id(x) for x in ast.walk(kw.value))
        if isinstance(node, (ast.FunctionDef, ast.Module)) and node.body and isinstance(node.body[0], ast.Expr) \
                and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
            out.add(id(node.body[0].value))
        if isinstance(node, ast.JoinedStr):
            out.update(id(v) for v in node.values if isinstance(v, ast.Constant))
    return out


def _annotation_ids(tree: ast.AST) -> set[int]:
    """ids of every node inside a type annotation (inert under `from __future__ import annotations`)."""
    out = set()
    for node in ast.walk(tree):
        ann = []
        if isinstance(node, ast.FunctionDef):
            ann.append(node.returns)
            ann.extend(a.annotation for a in (*node.args.args, *node.args.kwonlyargs, *node.args.posonlyargs))
        elif isinstance(node, ast.AnnAssign):
            ann.append(node.annotation)
        for a in ann:
            if a is not None:
                out.update(id(x) for x in ast.walk(a))
    return out


def _in_scope(stmt: ast.stmt) -> bool:
    if isinstance(stmt, (ast.Import, ast.ImportFrom)):
        return False
    if isinstance(stmt, ast.FunctionDef):
        return stmt.name not in SKIP_DEFS
    if isinstance(stmt, ast.Assign):
        return not any(isinstance(t, ast.Name) and t.id in SKIP_ASSIGN for t in stmt.targets)
    if isinstance(stmt, ast.If):  # the __main__ guard
        return False
    return not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant))


def _sites(tree: ast.Module):
    """Yield (node, key, edit) for every mutant; `edit(node)` returns the replacement node."""
    text = _text_ids(tree)
    inert = _annotation_ids(tree)
    for top in tree.body:
        if not _in_scope(top):
            continue
        owner = top.name if isinstance(top, ast.FunctionDef) else (
            top.targets[0].id if isinstance(top, ast.Assign) and isinstance(top.targets[0], ast.Name) else "module")
        parent = {id(c): n for n in ast.walk(top) for c in ast.iter_child_nodes(n)}
        for node in ast.walk(top):
            if id(node) in inert:
                continue
            stmt = node
            while not isinstance(stmt, ast.stmt):
                stmt = parent[id(stmt)]
            for site, label, edit in _node_mutants(node, text):
                where = _short(stmt if site is not stmt else parent.get(id(stmt), stmt), 60)
                yield site, f"{owner} @ {where}: {label}", edit


def _node_mutants(node, text):
    """(site, label, edit) per mutant of `node`; `edit` works on a copy's node and returns its replacement."""
    if isinstance(node, ast.Compare):
        for i, op in enumerate(node.ops):
            for new in CMP.get(type(op), ()):
                def f(n, i=i, new=new):
                    n.ops[i] = new()
                    return n
                yield node, f"{_short(node, 50)} [op {i}: {type(op).__name__} -> {new.__name__}]", f
    elif isinstance(node, ast.BoolOp):
        for j, arm in enumerate(node.values):
            def f(n, j=j):
                n.values.pop(j)
                return n if len(n.values) > 1 else n.values[0]
            yield node, f"drop {type(node.op).__name__.lower()} arm {_short(arm, 50)}", f

        def sw(n):
            n.op = ast.Or() if isinstance(n.op, ast.And) else ast.And()
            return n
        yield node, f"{_short(node, 50)} [and <-> or]", sw
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.Not, ast.USub)):
        yield node, f"drop {'not' if isinstance(node.op, ast.Not) else 'minus'} of {_short(node.operand, 50)}", \
            lambda n: n.operand
    elif isinstance(node, ast.Constant) and id(node) not in text:
        v = node.value
        if isinstance(v, bool) or v is None:
            pass
        elif isinstance(v, int):
            for d in (-1, 1):
                yield node, f"{v} -> {v + d}", lambda n, d=d: ast.Constant(n.value + d)
        elif isinstance(v, float):
            for k in (0.5, 2.0):
                yield node, f"{v} -> {v * k}", lambda n, k=k: ast.Constant(n.value * k)
        elif isinstance(v, str) and v:
            yield node, f"{_short(node, 50)} -> ''", lambda n: ast.Constant("")
    elif isinstance(node, (ast.Tuple, ast.List, ast.Set)) and isinstance(getattr(node, "ctx", ast.Load()), ast.Load) \
            and len(node.elts) >= 2:
        for j, elt in enumerate(node.elts):
            def f(n, j=j):
                n.elts.pop(j)
                return n
            yield node, f"drop element {_short(elt, 50)}", f
    elif isinstance(node, ast.BinOp) and type(node.op) in BIN:
        yield node, f"{_short(node, 50)} [{type(node.op).__name__} -> {BIN[type(node.op)].__name__}]", \
            lambda n: ast.BinOp(n.left, BIN[type(n.op)](), n.right)
    elif isinstance(node, ast.AugAssign) and type(node.op) in BIN:
        yield node, f"{_short(node, 50)} [{type(node.op).__name__} -> {BIN[type(node.op)].__name__}]", \
            lambda n: ast.AugAssign(n.target, BIN[type(n.op)](), n.value)
    elif isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Slice):
        s = node.slice
        if (s.lower is None) != (s.upper is None) and s.step is None:
            def f(n):
                n.slice = ast.Slice(lower=n.slice.upper, upper=n.slice.lower)
                return n
            yield node, f"{_short(node, 50)} [slice bound to the other side]", f
    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in SWAP_CALL:
            def f(n):
                n.func = ast.Name(SWAP_CALL[n.func.id], ast.Load())
                if n.func.id == "list":
                    n.keywords = []
                return n
            yield node, f"{node.func.id} -> {SWAP_CALL[node.func.id]} in {_short(node, 50)}", f
        for j, kw in enumerate(node.keywords):
            if kw.arg not in TEXT_KW:
                def f(n, j=j):
                    n.keywords.pop(j)
                    return n
                yield node, f"drop keyword {kw.arg or '**'}= of {_short(node.func, 40)}", f
    if isinstance(node, (ast.If, ast.While, ast.IfExp)):
        for val in (True, False):
            def f(n, val=val):
                n.test = ast.Constant(val)
                return n
            yield node, f"test {_short(node.test, 50)} -> {val}", f
    if isinstance(node, ast.comprehension):
        for j, cond in enumerate(node.ifs):
            def f(n, j=j):
                n.ifs.pop(j)
                return n
            yield node, f"drop comprehension if {_short(cond, 50)}", f
    for field in ("body", "orelse", "finalbody"):
        body = getattr(node, field, None)
        if not isinstance(body, list):
            continue
        for j, st in enumerate(body):
            if isinstance(st, (ast.FunctionDef, ast.Pass)) or (
                    j == 0 and isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant)):
                continue
            yield st, f"statement {_short(st, 60)} -> pass", lambda n: ast.Pass()


def _replace(tree: ast.AST, old: ast.AST, new: ast.AST) -> None:
    for parent in ast.walk(tree):
        for field, value in ast.iter_fields(parent):
            if value is old:
                setattr(parent, field, new)
                return
            if isinstance(value, list):
                for i, x in enumerate(value):
                    if x is old:
                        value[i] = new
                        return
    raise AssertionError("node not found")


def _short(node: ast.AST, width: int = 110) -> str:
    s = ast.unparse(node).splitlines()[0]
    return s if len(s) <= width else s[:width - 3] + "..."


def mutants(src: str) -> list[tuple[str, int, str]]:
    """(key, line, module source) for every distinct mutant, in visiting order."""
    orig = ast.parse(src)
    base = ast.unparse(orig)
    out, seen, keys = [], set(), Counter()
    for site, key, edit in list(_sites(orig)):
        memo = {}
        tree = copy.deepcopy(orig, memo)
        node = memo[id(site)]
        _replace(tree, node, edit(node))
        text = ast.unparse(ast.fix_missing_locations(tree))
        if text == base or text in seen:
            continue
        seen.add(text)
        keys[key] += 1
        if keys[key] > 1:
            key += f" #{keys[key]}"
        out.append((key, getattr(node, "lineno", 0), text))
    return out


def run(text: str) -> tuple[bool, str]:
    """(killed, last line) for one emitted module."""
    with tempfile.TemporaryDirectory() as d:
        dst = os.path.join(d, TARGET)
        os.makedirs(os.path.dirname(dst))
        for rel in COPY:
            os.makedirs(os.path.join(d, os.path.dirname(rel)), exist_ok=True)
            shutil.copy(ROOT / rel, os.path.join(d, rel))
        with open(dst, "w") as fh:
            fh.write(text)
        try:
            p = subprocess.run([sys.executable, dst, "--self-test"], capture_output=True, text=True,
                               timeout=120, cwd=d)
        except subprocess.TimeoutExpired:
            return True, "TIMEOUT"
        lines = (p.stdout + p.stderr).strip().splitlines()
        fails = [ln for ln in lines if ln.startswith("FAIL: ")]
        return p.returncode != 0, (fails[0] if fails else lines[-1] if lines else "")[:120]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--list", action="store_true", help="print the mutants, run nothing")
    ap.add_argument("--show-killed", action="store_true")
    a = ap.parse_args(argv)
    src = (ROOT / TARGET).read_text()
    ms = mutants(src)
    if a.list:
        for key, line, _ in ms:
            print(f"L{line:<4} {key}")
        print(f"RESULT mutants={len(ms)}")
        return 0
    m0, last = run(ast.unparse(ast.parse(src)))
    print(f"M0 (unmutated emission): {'FAILED' if m0 else 'passed'} -- {last}")
    if m0:
        print("RESULT m0=failed")
        return 1
    with ThreadPoolExecutor(a.jobs) as ex:
        results = list(ex.map(lambda m: run(m[2]), ms))
    survived, used = [], set()
    for (key, line, _), (killed, last) in zip(ms, results):
        if killed:
            if a.show_killed:
                print(f"KILLED   L{line:<4} {key}  [{last}]")
            continue
        survived.append(key)
        if key in DISPOSED:
            used.add(key)
            print(f"DISPOSED L{line:<4} {key}  [{DISPOSED[key]}]")
        else:
            print(f"SURVIVED L{line:<4} {key}")
    stale = sorted(set(DISPOSED) - used)
    for key in stale:
        print(f"STALE    {key}")
    undisposed = len(survived) - len(used)
    print(f"RESULT mutants={len(ms)} killed={len(ms) - len(survived)} survived={len(survived)} "
          f"disposed={len(used)} undisposed={undisposed} stale={len(stale)}")
    return 1 if undisposed or stale else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
