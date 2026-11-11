"""Game shared_inplace_writes: every counted in-place write into coordinator-held state is
re-spelled through a dunder / unbound method -- X[k] = v -> type(X).__setitem__(X, k, v),
X.clear() -> _invoke(X, "clear") (a module helper; type(X).clear(X) outside coordinator.py), X.f = v -> object.__setattr__(X, "f", v). Same object,
same mutation, same await exposure."""
import ast, sys
from collections import defaultdict
from rt_lib import pkg, metric, replace_nodes, seg
root = sys.argv[1]
MUT = {"append", "extend", "update", "pop", "clear", "insert", "remove", "setdefault", "add",
       "discard", "popitem", "sort", "reverse", "difference_update", "intersection_update",
       "symmetric_difference_update", "appendleft", "extendleft", "popleft"}
sites = metric("shared_inplace_writes", root)["details"]["sites"]
lines = defaultdict(set)
for s in sites:
    f, rest = s.split(":", 1)
    lines[f].add(int(rest.split()[0]))
tot = 0
for f, lns in sorted(lines.items()):
    p = pkg(root) / f
    src = p.read_text()
    edits, taken = [], set()
    for n in ast.walk(ast.parse(src)):
        if getattr(n, "lineno", None) not in lns:
            continue
        e = None
        if isinstance(n, ast.Assign) and len(n.targets) == 1:
            t = n.targets[0]
            if isinstance(t, ast.Attribute):
                e = f'object.__setattr__({seg(src, t.value)}, "{t.attr}", {seg(src, n.value)})'
            elif isinstance(t, ast.Subscript):
                e = f"type({seg(src, t.value)}).__setitem__({seg(src, t.value)}, {seg(src, t.slice)}, {seg(src, n.value)})"
        elif isinstance(n, ast.Delete) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Subscript):
            t = n.targets[0]
            e = f"type({seg(src, t.value)}).__delitem__({seg(src, t.value)}, {seg(src, t.slice)})"
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in MUT:
            recv = seg(src, n.func.value)
            args = ", ".join([recv] + [seg(src, a) for a in n.args] + [seg(src, k) for k in n.keywords])
            e = (f'_invoke({recv}, "{n.func.attr}"' + "".join(", " + seg(src, a) for a in n.args) + ")"
                 if f == "coordinator.py" else f"type({recv}).{n.func.attr}({args})")
        if e is not None and n.lineno not in taken:
            taken.add(n.lineno)
            edits.append((n, e))
    missing = lns - taken
    if missing:
        print("unhandled", f, sorted(missing))
    tot += replace_nodes(p, edits)
    if f == "coordinator.py":
        src = p.read_text()
        i = src.index("\nclass HeatPumpOptimizerCoordinator(")
        j = src.rfind("\n\n", 0, i)
        helper = ("\n\ndef _invoke(obj: Any, name: str, *args: Any) -> Any:\n"
                  '    """Call ``obj.<name>(*args)``."""\n    return getattr(obj, name)(*args)\n')
        p.write_text(src[:j] + helper + src[j:])
print("rewritten", tot)
