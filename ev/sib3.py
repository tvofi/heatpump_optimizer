# reviewer round 3: new sibling plants against the round-3 repair (_chain leaves, starred _bound)
import ast, sys
sys.path.insert(0, sys.argv[1] + "/tools/audit")
from archscore.metrics import footprint
n = lambda s: footprint.logic_stmts(ast.parse(s))
cases = [
 ("ifexp body-arm 3 deep", "a = ((f(x+1) if r else k(w+1)) if q else g(y+1)) if p else h(z+1)",
  "if p:\n    if q:\n        if r:\n            a = f(x+1)\n        else:\n            a = k(w+1)\n    else:\n        a = g(y+1)\nelse:\n    a = h(z+1)"),
 ("ifexp body-arm as expr stmt", "(f(x+1) if q else g(y+1)) if p else h(z+1)", "if p:\n    if q:\n        f(x+1)\n    else:\n        g(y+1)\nelse:\n    h(z+1)"),
 ("ifexp body-arm in return", "def k():\n    return (f(x+1) if q else g(y+1)) if p else h(z+1)", "def k():\n    if p:\n        if q:\n            return f(x+1)\n        else:\n            return g(y+1)\n    else:\n        return h(z+1)"),
 ("ifexp tree inside call arg", "a = s((f(x+1) if q else g(y+1)) if p else h(z+1))", "if p:\n    if q:\n        a = s(f(x+1))\n    else:\n        a = s(g(y+1))\nelse:\n    a = s(h(z+1))"),
 ("ifexp tree inside tuple value", "a, b = ((f(x+1) if q else g(y+1)) if p else h(z+1)), k(w+1)", "if p:\n    if q:\n        a = f(x+1)\n    else:\n        a = g(y+1)\nelse:\n    a = h(z+1)\nb = k(w+1)"),
 ("ifexp in test arm (lone each)", "a = f(x+1) if (q if p else r) else g(y+1)", "t = q if p else r\na = f(x+1) if t else g(y+1)"),
 ("two separate chains in one stmt", "a = s(f(x+1) if p else g(y+1) if q else h(z+1), f(x+2) if p else g(y+2) if q else h(z+2))", None),
 ("ifexp tree in walrus", "if (a := (f(x+1) if q else g(y+1)) if p else h(z+1)):\n    pass", None),
 ("ifexp tree in lambda", "k = lambda: (f(x+1) if q else g(y+1)) if p else h(z+1)", "def k():\n    if p:\n        if q:\n            return f(x+1)\n        else:\n            return g(y+1)\n    else:\n        return h(z+1)"),
 ("ifexp tree in comprehension", "r = [(f(v) if q else g(v)) if p else h(v) for v in vs]", "r = []\nfor v in vs:\n    if p:\n        if q:\n            r.append(f(v))\n        else:\n            r.append(g(v))\n    else:\n        r.append(h(v))"),
 ("starred middle", "a, *b, c = f(x+1), g(y+1), h(z+1), k(w+1)", "a = f(x+1)\nb = [g(y+1), h(z+1)]\nc = k(w+1)"),
 ("starred value side", "a, b, c = f(x+1), *g(y+1)", "a = f(x+1)\nb, c = g(y+1)"),
 ("starred against generator", "a, *b = (f(v) for v in vs)", "a = f(vs[0])\nb = [f(v) for v in vs[1:]]"),
 ("starred nested target", "a, (b, *c) = f(x+1), (g(y+1), h(z+1), k(w+1))", "a = f(x+1)\nb = g(y+1)\nc = [h(z+1), k(w+1)]"),
 ("starred plumbing", "a, *b = x.p, x.q, x.r", "a = x.p\nb = [x.q, x.r]"),
 ("starred in for over literal", "for a, *b in [(f(x+1), g(y+1), h(z+1))]:\n    pass", "a = f(x+1)\nb = [g(y+1), h(z+1)]\npass"),
 ("boolop chain control", "a = p and f(x+1) or q and g(y+1) or h(z+1)", "if p:\n    a = f(x+1)\nelif q:\n    a = g(y+1)\nelse:\n    a = h(z+1)"),
 ("boolop lone control", "a = p and f(x+1) or g(y+1)", "if p:\n    a = f(x+1)\nelse:\n    a = g(y+1)"),
 ("ctrl lone ifexp", "a = f(x+1) if p else g(y+1)", None),
 ("ctrl display one target", "x = [1, 2, 3]", None),
 ("ctrl or default", "a = b or c", None),
]
for name, pk, pl in cases:
    a = n(pk); b = n(pl) if pl else None
    print(f"RESULT {name!r:38} packed={a} plain={b} {'' if pl is None else ('SAME' if a==b else 'DIFF')}")
