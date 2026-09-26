"""Class search: which ha_contract contracts reach no assert on this provider."""
import ast, inspect, sys, textwrap
sys.path.insert(0, sys.argv[1] + "/tests")
import ha_contract as hc
vac, total = [], 0
for symbol, name, cite, expect, fn in hc.CONTRACTS:
    if expect == "real":
        continue
    total += 1
    src, first = inspect.getsourcelines(fn)
    tree = ast.parse(textwrap.dedent("".join(src)))
    lines = {n.lineno + first - 1 for n in ast.walk(tree) if isinstance(n, ast.Assert)}
    hit = set()
    code = fn.__code__
    def tr(frame, ev, arg):
        if frame.f_code is code:
            if ev == "line" and frame.f_lineno in lines:
                hit.add(frame.f_lineno)
            return tr
        return None
    sys.settrace(tr)
    try:
        fn()
    except Exception as e:
        pass
    finally:
        sys.settrace(None)
    if not hit:
        vac.append((symbol, name, len(lines)))
print(f"contracts_run={total} vacuous={len(vac)}")
for v in vac: print("  VACUOUS", v)
