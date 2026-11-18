"""N-log-flood enumerator (round 10, D14 steps 3-4).

Lists every WARNING/ERROR log call in a package and labels whether an
enclosing ``if`` (or the statement just before it) is a once-per-transition
latch: a test naming a latch flag (warned/logged/reported/latch/_failed/
_announced) or a ``not in`` membership test against a set that the same
function then ``.add``s to.  Unlatched sites are the class's seams.

    python3 enumerate.py [PKG_DIR] [--json]
"""
import ast, json, re, sys
from pathlib import Path

LATCH = re.compile(r"(warn|logged|report|latch|announc|_failed|notified|seen)", re.I)

def _latched(chain, fn):
    for node in chain:
        if isinstance(node, ast.If):
            src = ast.unparse(node.test)
            if LATCH.search(src):
                return src
            if isinstance(node.test, ast.Compare) and any(isinstance(o, ast.NotIn) for o in node.test.ops):
                body = ast.unparse(fn) if fn else ""
                tgt = ast.unparse(node.test.comparators[0])
                if f"{tgt}.add(" in body:
                    return src
    return None

def scan(pkg):
    out = []
    for p in sorted(Path(pkg).rglob("*.py")):
        tree = ast.parse(p.read_text())
        def walk(node, chain, fn):
            for ch in ast.iter_child_nodes(node):
                nfn = ch if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)) else fn
                if isinstance(ch, ast.Call) and isinstance(ch.func, ast.Attribute) \
                   and ch.func.attr in ("warning", "error") \
                   and ast.unparse(ch.func.value) == "_LOGGER":
                    out.append({"file": str(p), "line": ch.lineno, "level": ch.func.attr,
                                "symbol": fn.name if fn else "<module>",
                                "latch": _latched(chain, fn)})
                walk(ch, chain + [ch] if isinstance(ch, ast.If) else chain, nfn)
        walk(tree, [], None)
    return out

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    rows = scan(args[0] if args else "custom_components/heatpump_optimizer")
    seams = [r for r in rows if not r["latch"]]
    if "--json" in sys.argv:
        print(json.dumps(rows, indent=1))
    else:
        for r in rows:
            print(f"{'GUARD' if r['latch'] else 'SEAM '} {r['file']}:{r['line']} {r['symbol']} {r['latch'] or ''}")
    print(f"sites={len(rows)} latched={len(rows)-len(seams)} seams={len(seams)}", file=sys.stderr)
