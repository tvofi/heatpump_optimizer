#!/usr/bin/env python3
"""Reviewer's instrument (not the finder's): is blind_classify_readers total?
Axis 1: closed busy expressions (no free name: nothing can carry runtime state). Each is
eval'd; classify reads busy by truthiness only, so a falsy closed expression is a blind read
and a truthy one a constant always-deferral read. LEAK = closed and the census reads {}.
Axis 2: call shapes that reach merge_train.classify with no busy.
Usage: python3 -I reviewer_totality.py <tree>"""
import builtins, itertools, sys
sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import merge_train as m

def census(call):
    return m.blind_classify_readers("def f():\n    return %s\n" % call)

atoms = ["None", "()", "[]", "{}", "''", "0", "False", "b''", "0.0", "set()", "frozenset()", "dict()"]
# every builtin callable with no argument that returns a falsy value
noarg = []
for n in sorted(dir(builtins)):
    o = getattr(builtins, n)
    if isinstance(o, type) and not issubclass(o, BaseException):
        try:
            if not o():
                noarg.append(n + "()")
        except Exception:
            pass
forms = list(noarg)
for a in atoms:
    forms += [f"tuple({a})" if a in ("()", "[]", "{}", "''", "set()", "frozenset()", "dict()", "b''") else f"bool({a})"]
for a, b in itertools.product(["None", "()", "[]", "{}", "''", "0", "False", "set()"], repeat=2):
    forms += [f"{a} or {b}", f"{a} and {b}", f"{a} if {b} else {a}"]
forms += ["()[0:0]", "[][:]", "''[:]", "[()][0]", "{0: ()}[0]", "(None, ())[1]",
          "list(())", "set(())", "frozenset(())", "dict(())", "dict({})", "str('')", "bytes(b'')", "sorted(())",
          "tuple([])", "list([])", "bool()", "bool(0)", "int(0)", "len(())", "any(())", "sum(())",
          "type(())()", "().__class__()", "[].copy()", "''.join(())", "dict.fromkeys(())", "{}.keys()",
          "[x for x in ()]", "{x for x in ()}", "{x: x for x in ()}", "not True", "-0", "0 + 0", "() + ()", "1 > 2",
          "(lambda: ())()", "(b := ())", "f''", "[*()]", "{**{}}", "not ()" ]
seen, leaks, truthy_leaks, closed_blind = set(), [], [], 0
for e in forms:
    if e in seen: continue
    seen.add(e)
    try: v = eval(e, {})
    except Exception as x:
        print(f"SKIP {e!r}: {type(x).__name__}"); continue
    for call in (f"classify(l, r, {e})", f"classify(l, r, busy={e})"):
        got = census(call)
        if got == {}:
            (truthy_leaks if v else leaks).append(call)
        else:
            closed_blind += 1
print(f"RESULT closed_expressions={len(seen)} census_blind={closed_blind} falsy_read_as_a_read={len(leaks)} truthy_constant_read_as_a_read={len(truthy_leaks)}")
for c in leaks: print("LEAK falsy  ", c)
for c in truthy_leaks: print("LEAK truthy ", c)
print("--- axis 2: call shapes (each reaches classify with no busy, or with one that reads nothing)")
shapes = ["classify(l, r)", "classify(*(l, r))", "classify(*a)", "classify(l, *(r,))", "classify(l, r, *())", "classify(*a, **k)",
          "classify(l, r, **{})", "classify(l, r, **k)", "classify(latest=l, required=r)", "mt.classify(l, r)",
          "merge_train.classify(*a)", "(classify)(l, r)", "getattr(mt, 'classify')(l, r)", "functools.partial(classify, l, r)()",
          "(c := classify)(l, r)", "[classify][0](l, r)", "(mt.classify if 1 else 0)(l, r)", "classify.__call__(l, r)"]
n2 = 0
for s in shapes:
    got = census(s); n2 += got == {}
    print(("MISS " if got == {} else "seen ") + s, got)
alias = m.blind_classify_readers("from merge_train import classify as cl\nc2 = cl\ndef f():\n    return cl(l, r)\ndef g():\n    k = mt.classify\n    return k(l, r)\n")
print("MISS alias/import-as/local binding" if alias == {} else "seen alias", alias)
ex = m.blind_classify_readers("def gate_self_test_reading():\n    return classify(l, r)\nclass X_self_test:\n    def prod(self):\n        return classify(l, r)\n")
print("EXEMPT a production function whose name (or class) merely contains 'self_test'" if ex == {} else "seen", ex)
print(f"RESULT call_shapes_missed={n2 + (alias == {})} of {len(shapes) + 1} self_test_substring_exempts={ex == {}}")
# the reviewer's candidate total rule on axis 1: blind iff no Name/Attribute in the busy subtree other than a builtin-callable func
import ast
def closed(e):
    t = ast.parse(e, mode="eval")
    funcs = {id(n.func) for n in ast.walk(t) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and hasattr(builtins, n.func.id)}
    bound = {n.id for n in ast.walk(t) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
    for c in ast.walk(t):
        if isinstance(c, ast.comprehension):
            bound |= {n.id for n in ast.walk(c.target) if isinstance(n, ast.Name)}
        if isinstance(c, ast.Lambda):
            bound |= {a.arg for a in c.args.args}
    return not any((isinstance(n, ast.Name) and id(n) not in funcs and n.id not in bound and not hasattr(builtins, n.id))
                   for n in ast.walk(t))
miss = [e for e in seen if not closed(e)]
reads_ok = [e for e in ("b", "self.b", "x[0]", "h(r)", "frozenset(r)", "[b]", "{'a': b}", "self._gate_busy(h, runs)", "busy or ()", "b if c else ()") if closed(e)]
print(f"RESULT free_name_rule: closed_expressions_it_reads_as_a_read={len(miss)} {miss} runtime_reads_it_calls_blind={len(reads_ok)} {reads_ok}")
