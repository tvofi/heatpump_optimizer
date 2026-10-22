#!/usr/bin/env python3
"""R10-FLOW-YIELD-PROBE: every one-node mutant of review_strength.py against its self-test.

    python3 dev/audit/harnesses/r10_review_strength_mutants.py [--jobs N] [--list] [--show-killed]

THE RULE (the enumeration, so a sibling cannot be missed). The file is parsed
with `ast`; every node of every module-level statement is visited except the
docstring, the imports, `ROOT`, `self_test` and its `_self_test_main` and `_self_test_seams`, type annotations
and the `__main__` guard, and each
operator class below yields one mutant per site and per replacement:

    ordering    `sorted(...)` -> `list(...)`; `max` <-> `min`; `any` <-> `all`;
                `reverse=True` added to a `sorted`/`.sort`;
                a slice's lone bound moved to the other side (`[-n:]` -> `[:-n]`);
                a unary minus dropped (`[-n:]` -> `[n:]`)
    comparison  `<` -> `<=`,`>`;  `<=` -> `<`,`>=`;  `>` -> `>=`,`<`;  `>=` -> `>`,`<=`;
                `==` <-> `!=`;  `in` <-> `not in`;  `is` <-> `is not`
    branch      every arm of an `and`/`or` dropped, and `and` <-> `or`; `not` dropped;
                every `if`/`while`/conditional-expression test forced True and
                forced False; every comprehension `if` dropped; `True` <-> `False`
    threshold   every int literal n -> n-1 and n+1; every float f -> f/2 and 2f
    literals    every string literal, f-string part and format spec (so every path
                prefix, ref pattern, regex and class word) -> '', its first or last
                character dropped, cut before and after each separator (`/-_:. =`)
                keeping either side, and each numeral in it moved by one; every
                element of a tuple, list or set literal dropped (so each REAL_CATCH
                word and each product prefix is its own mutant). Human text is
                skipped: the docstrings and everything under `help=`, `metavar=`,
                `description=`, `.error(...)` and `SystemExit(...)`
    calls       `startswith` <-> `endswith`, `removesuffix` <-> `removeprefix`,
                `search` <-> `match`, and `split` <-> `rsplit` where a maxsplit is
                given (without one the two are the same function); every positional
                argument of a call holding two or more dropped; every keyword
                argument dropped (bar the human-text keywords)
    arithmetic  `+` <-> `-`, `*` <-> `/`, `**` -> `*`, and the same in `+=` / `-=`
    statements  every statement in a body replaced by `pass`; the one or two
                statements before an `if`/`for`/`while`/`with`/`try` moved into the
                head of its body; a block's first or last one or two statements
                moved out before or after it; every adjacent pair swapped where the
                two depend on each other (`_depends`: one writes what the other
                reads or writes, or one exits where the other's effect outlives it).
                A pair that commutes is the same program either way, so it is not
                generated; the dependency read is conservative (a computed key or a
                method call counts as touching the whole object), so it can only
                over-generate. What it cannot see is a call that mutates an
                argument it is passed (not its receiver) or a module global; no
                function in review_strength.py does either. A call to one of the
                module's functions that prints writes stdout, as a `print` does.

BOUNDS. The rule is this list and no more. It does not rename variables, swap
two different names, insert statements, move a statement more than one block
or two positions, or replace a literal with an unrelated one; a mutant of
those shapes is outside it, and a reviewer who finds one moving a figure has
found a class this rule does not close.

Each mutant is the whole module re-emitted by `ast.unparse`, one top-level statement
at a time, with that one node changed, written into its own scratch root beside a copy of
tests/throwaway_git.py (what the self-test imports), and run as
`review_strength.py --self-test`. KILLED means a non-zero exit (or a 120 s
timeout); SURVIVED means exit 0. A mutant whose emitted module is
byte-identical to the unmutated emission is not a mutant and is not counted.
M0 is the unmutated emission, which must pass first, or nothing is run.

DISPOSED below names every survivor this harness accepts, keyed on the
function, the statement and the mutant, each an equivalent mutant with the
reason it changes nothing. Prints one line per survivor (and per
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
import re
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
SKIP_DEFS = {"self_test", "_self_test_main", "_self_test_seams"}
SKIP_ASSIGN = {"ROOT"}
TEXT_KW = {"help", "metavar", "description"}
TEXT_CALLS = {"error", "SystemExit"}
SEPS = "/-_:. ="
SWAP_ATTR = {"startswith": "endswith", "endswith": "startswith", "removesuffix": "removeprefix",
             "removeprefix": "removesuffix", "split": "rsplit", "search": "match", "match": "search"}
CMP = {ast.Lt: (ast.LtE, ast.Gt), ast.LtE: (ast.Lt, ast.GtE), ast.Gt: (ast.GtE, ast.Lt),
       ast.GtE: (ast.Gt, ast.LtE), ast.Eq: (ast.NotEq,), ast.NotEq: (ast.Eq,),
       ast.In: (ast.NotIn,), ast.NotIn: (ast.In,), ast.Is: (ast.IsNot,), ast.IsNot: (ast.Is,)}
BIN = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.Div, ast.Div: ast.Mult, ast.Pow: ast.Mult}
PRINTERS: set[str] = set()  # filled per parse by `_sites`
SWAP_CALL = {"max": "min", "min": "max", "any": "all", "all": "any", "sorted": "list"}

# Survivors the self-test cannot see because they change nothing, keyed "<function> @ <statement>: <mutant>".
# Every entry is an equivalent mutant and says why.
DISPOSED = {
    "NONCE_RE @ NONCE_RE = re.compile('^bus-nonce:\\\\s*([0-9a-f]{32})', re.M): '^bus-nonce:\\\\s*([0-9a-f]{32})' -> '^bus-nonce:\\\\s*([0-9a-f]{31})'":
        'equivalent: only nonce[:8] is ever read, and a 32-hex nonce matches {31} at the same start',
    "when @ return datetime.fromisoformat(s.replace('Z', '+00:00')).a...: '+00:00' -> '+00'":
        'equivalent: datetime.fromisoformat reads +00 and +00:00 alike (3.11+)',
    "load @ for r in refs(repo, f'refs/remotes/{remote}/review/'):: swap if not m: with the next statement":
        'equivalent: the swapped `body = git(show ...)` is a read whose result only the lines after the `continue` use',
    "load @ for r in refs(repo, f'refs/remotes/{remote}/probe/') + re...: 'refs/tags/archive/probe/' -> 'refs/tags/archive/probe'":
        "equivalent: for-each-ref matches a pattern without its trailing '/' only at a whole path component, so archive/probe-x is not read either way",
    "load @ for r in refs(repo, f'refs/remotes/{remote}/verdict/'):: '/verdict/' -> '/verdict'":
        "equivalent: for-each-ref matches refs/remotes/<r>/verdict at a whole component, as with the '/'",
    "load @ for r in refs(repo, f'refs/remotes/{remote}/review/'):: '/review/' -> '/review'":
        "equivalent: for-each-ref matches refs/remotes/<r>/review at a whole component, as with the '/'",
    "load @ for r in refs(repo, f'refs/remotes/{remote}/probe/') + re...: '/probe/' -> '/probe'":
        "equivalent: for-each-ref matches refs/remotes/<r>/probe at a whole component, as with the '/'",
    "load @ out.append(dict(pr=int(m[1]), t=when(t), kind=m[2], head=...: drop or arm ''":
        "equivalent: cls None and cls '' read alike everywhere: stratum's `or` and the REAL_CATCH membership test",
    'pr_facts @ for pr, head in last.items():: swap files.append(f) with the next statement':
        'equivalent: `files` feeds only product, whose prefixes no delivery row matches, so where its append sits beside the delivery test moves nothing',
    "pr_facts @ for pr, head in last.items():: move 1 statement(s) before into if not f.startswith('dev/programme/de...":
        'equivalent: `files` feeds only product, whose prefixes no delivery row matches',
    "pr_facts @ for ln in git(repo, 'diff', '--numstat', mb, head, check=...: test mb -> True":
        "equivalent: with no merge base the size is '?' and product reads `files`, which a failed `git diff` leaves empty either way",
    "pr_facts @ a, d, f = ln.split('\\t', 2): split -> rsplit in ln.split('\\t', 2)":
        'equivalent: `git diff --numstat` quotes any path holding a tab, so a line holds exactly two tabs',
    "pr_facts @ a, d, f = ln.split('\\t', 2): drop argument 1 2 of ln.split":
        'equivalent: `git diff --numstat` quotes any path holding a tab, so a line holds exactly two tabs',
    "pr_facts @ a, d, f = ln.split('\\t', 2): 2 -> 3":
        'equivalent: `git diff --numstat` quotes any path holding a tab, so a line holds exactly two tabs',
    'pr_facts @ grp = groups.get(g[1]) if g else None: 1 -> 0':
        "equivalent: GROUP_RE's one group is its whole match, so g[0] == g[1]",
    "pr_facts @ base, head, branch = (merges[pr][0] + '^1', merges[pr][1]...: '^1' -> '^'":
        'equivalent: git reads <rev>^ as <rev>^1',
    "pr_facts @ for ln in git(repo, 'diff', '--numstat', mb, head, check=...: drop keyword check= of git":
        'equivalent: the diff runs only with a merge base, so both commits exist and it cannot exit non-zero',
    "pr_facts @ for ln in git(repo, 'diff', '--numstat', mb, head, check=...: False -> True":
        'equivalent: the diff runs only with a merge base, so both commits exist and it cannot exit non-zero',
    "stratum @ def stratum(by: str, v: dict, facts: dict[int, dict]) -> ...: swap if '+' in by: with the next statement":
        "equivalent: the four tests ('+' in by, == 'all', == 'kind', == 'class') are disjoint, so their order picks nothing",
    "stratum @ def stratum(by: str, v: dict, facts: dict[int, dict]) -> ...: swap if by == 'all': with the next statement":
        "equivalent: the four tests ('+' in by, == 'all', == 'kind', == 'class') are disjoint, so their order picks nothing",
    "stratum @ def stratum(by: str, v: dict, facts: dict[int, dict]) -> ...: swap if by == 'kind': with the next statement":
        "equivalent: the four tests ('+' in by, == 'all', == 'kind', == 'class') are disjoint, so their order picks nothing",
    "stratum @ def stratum(by: str, v: dict, facts: dict[int, dict]) -> ...: swap if by == 'class': with the next statement":
        "equivalent: the four tests ('+' in by, == 'all', == 'kind', == 'class') are disjoint, so their order picks nothing",
    "tally @ for v in verdicts:: swap o['verdicts'] += 1 with the next statement":
        'equivalent: the counter and the real/book counters are different keys of o; the swap is generated only because the latter key is computed',
    "tally @ for v in verdicts:: move last 1 statement(s) of if v['kind'] == 'blocked': after it":
        'equivalent: load sets real only on a blocked verdict',
    "tally @ if a <= v['t'] < b:: swap o['real' if v['real'] else ... with the next statement":
        "equivalent: o['real'|'book'] and o['caught'] are different keys; the swap is generated only because the former key is computed",
    'guardrail @ return f"GUARDRAIL last {n} PRs (first verdict {first[las...: cdf < ALPHA [op 0: Lt -> LtE]':
        "equivalent: no binomial CDF lands exactly on 0.05 in floating point (none for N <= 5 on a 1e-5 p0 grid); strict 'below 0.05' is R13's wording",
    "parser @ def parser() -> argparse.ArgumentParser:: swap ap.add_argument('--repo', d... with the next statement":
        'equivalent: argparse registration order of optionals orders only the --help listing (human text)',
    "parser @ def parser() -> argparse.ArgumentParser:: swap ap.add_argument('--remote',... with the next statement":
        'equivalent: argparse registration order of optionals orders only the --help listing (human text)',
    "parser @ def parser() -> argparse.ArgumentParser:: swap ap.add_argument('--tree', d... with the next statement":
        'equivalent: argparse registration order of optionals orders only the --help listing (human text)',
    "parser @ def parser() -> argparse.ArgumentParser:: swap ap.add_argument('--fetch', ... with the next statement":
        'equivalent: argparse registration order of optionals orders only the --help listing (human text)',
    "parser @ def parser() -> argparse.ArgumentParser:: swap ap.add_argument('--window',... with the next statement":
        'equivalent: argparse registration order of optionals orders only the --help listing (human text)',
    "parser @ def parser() -> argparse.ArgumentParser:: swap ap.add_argument('--by', act... with the next statement":
        'equivalent: argparse registration order of optionals orders only the --help listing (human text)',
    "parser @ def parser() -> argparse.ArgumentParser:: swap ap.add_argument('--roster',... with the next statement":
        'equivalent: argparse registration order of optionals orders only the --help listing (human text)',
    "parser @ def parser() -> argparse.ArgumentParser:: swap ap.add_argument('--as-of', ... with the next statement":
        'equivalent: argparse registration order of optionals orders only the --help listing (human text)',
    "parser @ def parser() -> argparse.ArgumentParser:: swap ap.add_argument('--guardrai... with the next statement":
        'equivalent: argparse registration order of optionals orders only the --help listing (human text)',
    "parser @ def parser() -> argparse.ArgumentParser:: swap ap.add_argument('--p0', typ... with the next statement":
        'equivalent: argparse registration order of optionals orders only the --help listing (human text)',
    "parser @ def parser() -> argparse.ArgumentParser:: swap ap.add_argument('--real-ext... with the next statement":
        'equivalent: argparse registration order of optionals orders only the --help listing (human text)',
    "parser @ ap.add_argument('--window', action='append', default=[], ...: drop keyword default= of ap.add_argument":
        "equivalent: argparse's append default is None without it, and `not a.window` refuses None and [] alike",
    'main @ def main(argv: list[str]) -> int:: swap if a.fetch: with the next statement':
        'equivalent: the swapped `extra = ...` only reads a.real_extra; the dependency is generated because a method call on a.real_extra counts as writing a',
    "main @ git(repo, 'fetch', '-q', '--tags', a.remote, *(f'+refs/he...: drop argument 2 '-q' of git":
        "equivalent: git() captures the fetch's output, and -q changes only that",
    "main @ name, span = w.split('=', 1): split -> rsplit in w.split('=', 1)":
        "equivalent: a window spec holds one '=' (names and ISO stamps hold none)",
    "main @ name, span = w.split('=', 1): drop argument 1 1 of w.split":
        "equivalent: a window spec holds one '=' (names and ISO stamps hold none)",
    "main @ f, u = span.split('..', 1): split -> rsplit in span.split('..', 1)":
        "equivalent: an ISO stamp holds no '..', so a span holds one",
    "main @ f, u = span.split('..', 1): drop argument 1 1 of span.split":
        "equivalent: an ISO stamp holds no '..', so a span holds one",
    "main @ git(repo, 'fetch', '-q', '--tags', a.remote, *(f'+refs/he...: '--tags' -> '--tag'":
        'equivalent: git accepts an unambiguous prefix of a long option, so --tag is --tags',
    "main @ name, span = w.split('=', 1): 1 -> 2":
        "equivalent: a window spec holds one '=' (names and ISO stamps hold none)",
    "main @ f, u = span.split('..', 1): 1 -> 2":
        "equivalent: an ISO stamp holds no '..', so a span holds one",
}


def _call_name(node: ast.Call) -> str:
    f = node.func
    return f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""


def _text_ids(tree: ast.AST) -> set[int]:
    """ids of the nodes that are human text: help, refusal messages, docstrings."""
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
                and _is_str(node.body[0].value):
            out.add(id(node.body[0].value))
    return out


def _is_str(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and isinstance(node.value, str)


def _str_edits(v: str) -> list[str]:
    """Every edit of the literal class rule: '', each end character dropped, each prefix and suffix
    cut at a separator (with and without it), and each numeral moved by one."""
    out = ["", v[1:], v[:-1]]
    for i, ch in enumerate(v):
        if ch in SEPS and 0 < i < len(v) - 1:
            out += [v[:i], v[:i + 1], v[i:], v[i + 1:]]
    for m in re.finditer(r"\d+", v):
        for d in (-1, 1):
            if int(m[0]) + d >= 0:
                out.append(v[:m.start()] + str(int(m[0]) + d) + v[m.end():])
    return list(dict.fromkeys(x for x in out if x != v))


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
    """Yield (top, node, key, edit) for every mutant; `edit(node)` returns the replacement node."""
    PRINTERS.clear()
    PRINTERS.update(_printers(tree))
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
                yield top, site, f"{owner} @ {where}: {label}", edit


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
        if v is None:
            pass
        elif isinstance(v, bool):
            yield node, f"{v} -> {not v}", lambda n: ast.Constant(not n.value)
        elif isinstance(v, int):
            for d in (-1, 1):
                yield node, f"{v} -> {v + d}", lambda n, d=d: ast.Constant(n.value + d)
        elif isinstance(v, float):
            for k in (0.5, 2.0):
                yield node, f"{v} -> {v * k}", lambda n, k=k: ast.Constant(n.value * k)
        elif isinstance(v, str) and v:
            for e in _str_edits(v):
                yield node, f"{_short(node, 50)} -> {e!r}", lambda n, e=e: ast.Constant(e)
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
        if isinstance(node.func, ast.Attribute) and node.func.attr in SWAP_ATTR and (
                node.func.attr not in ("split", "rsplit") or len(node.args) == 2 or node.keywords):
            def f(n):
                n.func = ast.Attribute(n.func.value, SWAP_ATTR[n.func.attr], ast.Load())
                return n
            yield node, f"{node.func.attr} -> {SWAP_ATTR[node.func.attr]} in {_short(node, 50)}", f
        if _call_name(node) in ("sorted", "sort") and not any(k.arg == "reverse" for k in node.keywords):
            def f(n):
                n.keywords.append(ast.keyword("reverse", ast.Constant(True)))
                return n
            yield node, f"reverse=True in {_short(node, 50)}", f
        if len(node.args) >= 2 and _call_name(node) not in TEXT_CALLS:
            for j, arg in enumerate(node.args):
                if not isinstance(arg, ast.Starred):
                    def f(n, j=j):
                        n.args.pop(j)
                        return n
                    yield node, f"drop argument {j} {_short(arg, 30)} of {_short(node.func, 40)}", f
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
        yield from _moves(node, field, body)


COMPOUND = (ast.If, ast.For, ast.While, ast.With, ast.Try)


def _moves(node, field, body):
    """Statement moves in one body: the one or two statements before a block moved into its head,
    a block's first or last one or two moved out before or after it, and adjacent statements swapped."""
    def mk(label, how):
        def f(n):
            setattr(n, field, how(list(getattr(n, field))))
            return n
        return node, label, f
    for j, st in enumerate(body):
        if isinstance(st, COMPOUND):
            head = _short(st, 40)
            for k in (1, 2):
                if j - k >= 0 and not any(isinstance(x, (ast.FunctionDef, ast.Return)) for x in body[j - k:j]):
                    def into(b, j=j, k=k):
                        blk = copy.copy(b[j])
                        blk.body = b[j - k:j] + blk.body
                        return b[:j - k] + [blk] + b[j + 1:]
                    yield mk(f"move {k} statement(s) before into {head}", into)
                if len(st.body) > k:
                    def out_first(b, j=j, k=k):
                        blk = copy.copy(b[j])
                        blk.body = b[j].body[k:]
                        return b[:j] + b[j].body[:k] + [blk] + b[j + 1:]

                    def out_last(b, j=j, k=k):
                        blk = copy.copy(b[j])
                        blk.body = b[j].body[:-k]
                        return b[:j] + [blk] + b[j].body[-k:] + b[j + 1:]
                    yield mk(f"move first {k} statement(s) of {head} before it", out_first)
                    yield mk(f"move last {k} statement(s) of {head} after it", out_last)
        if j + 1 < len(body) and not isinstance(body[j + 1], ast.Return) and not _docstring(body, j) \
                and _depends(st, body[j + 1]):
            def swap(b, j=j):
                return b[:j] + [b[j + 1], b[j]] + b[j + 2:]
            yield mk(f"swap {_short(st, 30)} with the next statement", swap)


def _printers(tree: ast.Module) -> set[str]:
    """The module's functions that print, directly or through another of them."""
    calls = {t.name: {_call_name(c) for c in ast.walk(t) if isinstance(c, ast.Call)}
             for t in tree.body if isinstance(t, ast.FunctionDef)}
    out = {f for f, cs in calls.items() if "print" in cs}
    while True:
        more = {f for f, cs in calls.items() if cs & out} - out
        if not more:
            return out
        out |= more


def _docstring(body, j) -> bool:
    return j == 0 and isinstance(body[0], ast.Expr) and _is_str(body[0].value)


def _effects(st: ast.stmt) -> tuple[set, set, set]:
    """(reads, writes, exits) of one statement, as (name, key) tokens; key None is the whole name,
    '*' an unknown part. A method call writes its receiver; a print or refusal writes '<out>'; a
    git call reads '<refs>' and a fetch writes it; a call to a module function that prints writes '<out>'. Exits are the return, raise, break or continue
    it holds, and a refusal (`.error`, `SystemExit`). A lambda's body is read when it is called, not here."""
    reads, writes, exits = set(), set(), set()

    def tok(node):
        if isinstance(node, ast.Name):
            return node.id, None
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
            sl = node.slice
            return node.value.id, sl.value if isinstance(sl, ast.Constant) else "*"
        if isinstance(node, ast.Attribute):
            return tok(node.value)
        return None

    skip, based = set(), set()
    for node in ast.walk(st):
        if isinstance(node, ast.Lambda) and isinstance(st, ast.Assign) and st.value is node:
            skip.update(id(x) for x in ast.walk(node.body))
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
            based.add(id(node.value))
            if isinstance(node.ctx, ast.Load):
                reads.add(tok(node))
    for node in ast.walk(st):
        if id(node) in skip:
            continue
        if isinstance(node, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
            exits.add(type(node).__name__)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and id(node) not in based:
            reads.add((node.id, None))
        if isinstance(node, (ast.Name, ast.Subscript, ast.Attribute)) and isinstance(node.ctx, (ast.Store, ast.Del)):
            t = tok(node)
            writes.add(t if t else ("<unknown>", None))
        if isinstance(node, ast.AugAssign):
            t = tok(node.target)
            writes.add(t if t else ("<unknown>", None))
        if isinstance(node, ast.Call):
            name = _call_name(node)
            if isinstance(node.func, ast.Attribute):
                t = tok(node.func.value)
                if t:
                    writes.add(t)
            if name in ("print", "error", "SystemExit") or name in PRINTERS:
                writes.add(("<out>", None))
            if name in ("error", "SystemExit"):
                exits.add("Raise")
            if name == "git":
                reads.add(("<refs>", None))
                if any(isinstance(x, ast.Constant) and x.value == "fetch" for x in node.args):
                    writes.add(("<refs>", None))
    return reads, writes, exits


def _clash(xs: set, ys: set) -> bool:
    return any(a == c and (b is None or d is None or "*" in (b, d) or b == d) for a, b in xs for c, d in ys)


def _depends(s1: ast.stmt, s2: ast.stmt) -> bool:
    """Whether swapping two adjacent statements can change anything: one writes what the other reads
    or writes, or one exits where the other's effect would outlive it (`_exit_clash`). Statements
    that commute are equivalent swaps by construction and are not generated."""
    r1, w1, x1 = _effects(s1)
    r2, w2, x2 = _effects(s2)
    return _clash(w1, r2 | w2) or _clash(w2, r1) or _exit_clash(x1, s2, w2, x2) or _exit_clash(x2, s1, w1, x1)


def _exit_clash(exits: set, other: ast.stmt, writes: set, other_exits: set) -> bool:
    """An exit beside another exit, or beside any write when it is a break or continue (the loop goes
    on); a return or raise only beside a write that outlives the call: anything but a plain local name."""
    if not exits:
        return False
    if other_exits or exits & {"Break", "Continue"}:
        return bool(other_exits or writes)
    local = {t.id for t in ast.walk(other) if isinstance(t, ast.Name) and isinstance(t.ctx, ast.Store)}
    return any(not (k is None and n in local) for n, k in writes)


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


def emit(tree: ast.Module) -> str:
    """The module re-emitted one top-level statement at a time, as every mutant is."""
    return "\n".join(ast.unparse(t) for t in tree.body)


def mutants(src: str) -> list[tuple[str, int, str]]:
    """(key, line, module source) for every distinct mutant, in visiting order."""
    orig = ast.parse(src)
    pieces = [ast.unparse(t) for t in orig.body]
    base = emit(orig)
    out, seen, keys = [], set(), Counter()
    for top, site, key, edit in list(_sites(orig)):
        memo = {}
        holder = ast.Module(body=[copy.deepcopy(top, memo)], type_ignores=[])
        node = memo[id(site)]
        _replace(holder, node, edit(node))
        i = orig.body.index(top)
        text = "\n".join([*pieces[:i], ast.unparse(ast.fix_missing_locations(holder)), *pieces[i + 1:]])
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
    m0, last = run(emit(ast.parse(src)))
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
