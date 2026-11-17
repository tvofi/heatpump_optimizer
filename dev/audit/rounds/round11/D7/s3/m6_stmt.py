#!/usr/bin/env python3
"""D7.M6 (round 11, seat D7-s3), third census: statements that cannot matter.

Metric (one line): per function body of the package, the statements that are dead by the AST
alone -- a store overwritten in the same block before any load (`dead_store`), an expression
statement with no effect (`no_effect`), a constant condition (`const_condition`), a literal
dict's repeated key (`dup_key`), an if/elif repeating a test or an if/else with identical
arms (`same_test`, `same_arms`), an operator applied to two identical operands
(`self_operand`), a self-assignment (`self_assign`), and an `else` arm no member of the
enumeration its chain tests can reach (`exhausted_else`: the if/elif arms compare one subject
with package constants that together cover every value of a module-level tuple of constants,
and the else arm is more than a raise, a return of a constant or a log line).

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m6_stmt.py --list   # the universe
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m6_stmt.py          # the census
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m6_stmt.py --perturb

Instrumented symbols: every function body in `custom_components/heatpump_optimizer/*.py`
(static counts, no timing). Count key: (file, function, line, kind).
Perturbation (`--perturb`): one planted statement of each kind in an in-memory copy must raise
its kind's count by exactly 1 (up).
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, Darwin arm64 / Python 3.14; exact.
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")

import argparse
import ast
import glob
import sys
import time

PKG = os.path.join("custom_components", "heatpump_optimizer")
KINDS = ("dead_store", "no_effect", "const_condition", "dup_key", "same_test", "same_arms",
         "self_operand", "self_assign", "exhausted_else")


def constants(sources):
    """Module-level string constants and tuples of them, by bare name, resolved through
    aliases (`DEFAULT_X = X_AUTO`); a name bound to different values in two modules is dropped."""
    raw, tuples = {}, {}
    for rel, text in sources.items():
        for st in ast.parse(text).body:
            tgt = val = None
            if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name):
                tgt, val = st.targets[0].id, st.value
            elif isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name) and st.value is not None:
                tgt, val = st.target.id, st.value
            if tgt is None:
                continue
            raw.setdefault(tgt, []).append(val)
    resolved = {}

    def value_of(node, depth=0):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        name = node.id if isinstance(node, ast.Name) else node.attr if isinstance(node, ast.Attribute) else None
        if name is None or depth > 6 or name not in raw:
            return None
        vals = {value_of(v, depth + 1) for v in raw[name]}
        return vals.pop() if len(vals) == 1 else None

    for name, nodes in raw.items():
        v = {value_of(n) for n in nodes}
        if len(v) == 1 and None not in v:
            resolved[name] = v.pop()
        for n in nodes:
            if isinstance(n, ast.Tuple) and len(n.elts) >= 2:
                vals = [value_of(e) for e in n.elts]
                if all(isinstance(x, str) for x in vals):
                    tuples[name] = frozenset(vals)
    return value_of, tuples


def _trivial_else(body):
    for b in body:
        if isinstance(b, (ast.Raise, ast.Pass, ast.Continue, ast.Break)):
            continue
        if isinstance(b, ast.Return) and (b.value is None or isinstance(b.value, (ast.Constant, ast.Name))):
            continue
        if isinstance(b, ast.Expr) and isinstance(b.value, ast.Call) and "LOGGER" in ast.dump(b.value.func):
            continue
        return False
    return True


def exhausted_else(rel, fn, value_of, tuples):
    rows = []
    for st in ast.walk(fn):
        if not isinstance(st, ast.If):
            continue
        subject, seen, cur, else_body = None, set(), st, None
        ok = True
        while True:
            t = cur.test
            if not (isinstance(t, ast.Compare) and len(t.ops) == 1):
                ok = False
                break
            subj = ast.dump(t.left)
            if subject is None:
                subject = subj
            if subj != subject:
                ok = False
                break
            comp = t.comparators[0]
            if isinstance(t.ops[0], ast.Eq):
                vals = [value_of(comp)]
            elif isinstance(t.ops[0], ast.In) and isinstance(comp, (ast.Tuple, ast.Set, ast.List)):
                vals = [value_of(e) for e in comp.elts]
            else:
                ok = False
                break
            if any(v is None for v in vals):
                ok = False
                break
            seen.update(vals)
            if len(cur.orelse) == 1 and isinstance(cur.orelse[0], ast.If):
                cur = cur.orelse[0]
                continue
            else_body = cur.orelse
            break
        if not ok or not else_body or len(seen) < 2 or _trivial_else(else_body):
            continue
        covered = sorted(name for name, vals in tuples.items() if vals <= seen)
        if covered:
            rows.append((rel, fn.name, else_body[0].lineno, "exhausted_else",
                         "every value of %s is taken by an earlier arm (%s)" % (covered[0], ", ".join(sorted(seen)))))
    return rows


def load_sources(root):
    return {os.path.basename(f): open(f, encoding="utf-8").read()
            for f in sorted(glob.glob(os.path.join(root, PKG, "*.py")))}


def _loads(node):
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Load, ast.Del)):
            out.add(n.id)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            pass
    return out


def _pure(e):
    """An expression whose evaluation calls nothing."""
    return not any(isinstance(n, (ast.Call, ast.Await, ast.Yield, ast.YieldFrom, ast.NamedExpr))
                   for n in ast.walk(e))


def _blocks(fn):
    for n in ast.walk(fn):
        for field in ("body", "orelse", "finalbody"):
            seq = getattr(n, field, None)
            if isinstance(seq, list) and seq and isinstance(seq[0], ast.stmt):
                yield seq
        for h in getattr(n, "handlers", []) or []:
            yield h.body
        for c in getattr(n, "cases", []) or []:
            yield c.body


def census(sources):
    rows, universe = [], []
    value_of, tuples = constants(sources)
    for rel, text in sources.items():
        tree = ast.parse(text)
        funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for fn in funcs:
            universe.append("%s:%s:%d [body]" % (rel, fn.name, fn.lineno))
            rows.extend(exhausted_else(rel, fn, value_of, tuples))
            nonlocal_names = set()
            for n in ast.walk(fn):
                if isinstance(n, (ast.Global, ast.Nonlocal)):
                    nonlocal_names.update(n.names)
            # names an inner function reads are read at any time
            closure_reads = set()
            for n in ast.walk(fn):
                if n is not fn and isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                    closure_reads |= _loads(n)
            for seq in _blocks(fn):
                for i, st in enumerate(seq):
                    # dead store: a plain `x = <expr>` re-stored later in this block, no load between
                    if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name):
                        name = st.targets[0].id
                        if name in nonlocal_names or name in closure_reads or name == "_":
                            pass
                        else:
                            for later in seq[i + 1:]:
                                if name in _loads(later):
                                    break
                                if isinstance(later, (ast.Try, ast.With, ast.AsyncWith, ast.For, ast.AsyncFor,
                                                      ast.While, ast.If, ast.Match, ast.Return, ast.Raise,
                                                      ast.Break, ast.Continue)):
                                    break  # control flow: do not reason past it
                                if (isinstance(later, ast.Assign) and len(later.targets) == 1
                                        and isinstance(later.targets[0], ast.Name)
                                        and later.targets[0].id == name):
                                    if not (isinstance(st.value, ast.Constant)):
                                        rows.append((rel, fn.name, st.lineno, "dead_store", name))
                                    break
                            else:
                                pass
                        if isinstance(st.value, ast.Name) and st.value.id == name:
                            rows.append((rel, fn.name, st.lineno, "self_assign", name))
                    if isinstance(st, ast.Expr):
                        v = st.value
                        if not isinstance(v, (ast.Call, ast.Await, ast.Yield, ast.YieldFrom)) and not (
                                isinstance(v, ast.Constant) and (isinstance(v.value, str) or v.value is Ellipsis)):
                            if _pure(v):
                                rows.append((rel, fn.name, st.lineno, "no_effect", ast.unparse(v)[:60]))
                    if isinstance(st, ast.If):
                        tests, cur = [], st
                        while True:
                            tests.append(ast.dump(cur.test))
                            if len(cur.orelse) == 1 and isinstance(cur.orelse[0], ast.If):
                                cur = cur.orelse[0]
                            else:
                                break
                        if len(set(tests)) < len(tests) and _pure(st.test):
                            rows.append((rel, fn.name, st.lineno, "same_test", ""))
                        if st.orelse and [ast.dump(x) for x in st.body] == [ast.dump(x) for x in st.orelse]:
                            rows.append((rel, fn.name, st.lineno, "same_arms", ""))
            for n in ast.walk(fn):
                if isinstance(n, (ast.If, ast.While, ast.IfExp)) and isinstance(n.test, ast.Constant):
                    if not (isinstance(n, ast.While) and n.test.value is True):
                        rows.append((rel, fn.name, n.lineno, "const_condition", repr(n.test.value)))
                elif isinstance(n, ast.Dict):
                    keys = [ast.dump(k) for k in n.keys if isinstance(k, ast.Constant)]
                    if len(set(keys)) < len(keys):
                        rows.append((rel, fn.name, n.lineno, "dup_key", ""))
                elif isinstance(n, ast.Compare) and len(n.ops) == 1 and _pure(n):
                    if ast.dump(n.left) == ast.dump(n.comparators[0]) and not isinstance(n.left, ast.Constant):
                        # `x != x` is the NaN test; anything else is a comparison that cannot vary
                        if not isinstance(n.ops[0], (ast.NotEq, ast.Eq)):
                            rows.append((rel, fn.name, n.lineno, "self_operand", ast.unparse(n)[:60]))
                        else:
                            rows.append((rel, fn.name, n.lineno, "self_operand", ast.unparse(n)[:60]))
                elif isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Sub, ast.Div, ast.FloorDiv, ast.Mod)) and _pure(n):
                    if ast.dump(n.left) == ast.dump(n.right) and not isinstance(n.left, ast.Constant):
                        rows.append((rel, fn.name, n.lineno, "self_operand", ast.unparse(n)[:60]))
                elif isinstance(n, ast.BoolOp) and _pure(n):
                    ds = [ast.dump(v) for v in n.values]
                    if len(set(ds)) < len(ds):
                        rows.append((rel, fn.name, n.lineno, "self_operand", ast.unparse(n)[:60]))
    # nested functions are walked by their parents too: one row per site
    rows = sorted(set(rows))
    return rows, universe


PLANTS = {
    "dead_store": "def _p(a):\n    x = a + 1\n    x = a + 2\n    return x\n",
    "no_effect": "def _p(a):\n    a == 2\n    return a\n",
    "const_condition": "def _p(a):\n    if False:\n        return 1\n    return a\n",
    "dup_key": "def _p(a):\n    return {'k': a, 'k': 2}\n",
    "same_test": "def _p(a):\n    if a > 1:\n        return 1\n    elif a > 1:\n        return 2\n    return 3\n",
    "same_arms": "def _p(a):\n    if a:\n        return 1\n    else:\n        return 1\n",
    "self_operand": "def _p(a):\n    return a - a\n",
    "self_assign": "def _p(a):\n    b = a\n    b = b\n    return b\n",
    "exhausted_else": ("_P_A = 'pa'\n_P_B = 'pb'\n_P_ALL = (_P_A, _P_B)\n_P_DEFAULT = _P_A\n"
                       "def _p(a, cfg):\n    if a in (_P_B, _P_DEFAULT):\n        return 1\n    elif a == _P_A:\n        return 2\n"
                       "    else:\n        return any(k in cfg for k in ('x', 'y'))\n"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()
    sources = load_sources(a.root)
    rows, universe = census(sources)
    if a.list:
        print("\n".join(universe))
        return 0
    counts = dict.fromkeys(KINDS, 0)
    for rel, fn, line, kind, what in rows:
        counts[kind] += 1
        print("ROW %s %s:%d %s %s" % (kind, rel, line, fn, what))
    print("RESULT universe=%d function bodies" % len(universe))
    for k in KINDS:
        print("RESULT %s=%d statements" % (k, counts[k]))
    if a.perturb:
        for k in KINDS:
            planted = dict(sources)
            planted["wear.py"] += "\n\n" + PLANTS[k]
            r2, _u = census(planted)
            c2 = sum(1 for r in r2 if r[3] == k)
            print("RESULT planted_%s_delta=%d statements" % (k, c2 - counts[k]))
    tf = (time.process_time() - t0p) / max(time.thread_time() - t0t, 1e-9)
    print("RESULT thread_factor=%.3f ratio" % tf)
    print("RESULT load1=%.2f load" % os.getloadavg()[0])
    try:
        import resource
        print("RESULT swapins=%d count" % resource.getrusage(resource.RUSAGE_SELF).ru_nswap)
    except Exception:
        print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
