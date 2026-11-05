import ast, sys
sys.path.insert(0, sys.argv[1] + "/tools/audit")
from archscore.metrics import footprint
n = lambda s: footprint.logic_stmts(ast.parse(s))
cases = [
 ("for-target literal", "for a, b, c in [(f(x+1), g(y+1), h(z+1))]:\n    pass", "a = f(x+1)\nb = g(y+1)\nc = h(z+1)"),
 ("for-target gen", "for a, b in ((f(x+1), g(y+1)),):\n    pass", "a = f(x+1)\nb = g(y+1)"),
 ("set display expr", "{f(x+1), g(y+1)}", "f(x+1)\ng(y+1)"),
 ("dict display expr", "{1: f(x+1), 2: g(y+1)}", "f(x+1)\ng(y+1)"),
 ("walrus tuple expr", "(a := f(x+1), b := g(y+1))", "a = f(x+1)\nb = g(y+1)"),
 ("walrus in call", "h(a := f(x+1), b := g(y+1))", "a = f(x+1)\nb = g(y+1)\nh(a, b)"),
 ("walrus in assign", "c = (a := f(x+1)) + (b := g(y+1))", "a = f(x+1)\nb = g(y+1)\nc = a + b"),
 ("ifexp chain", "a = f(x+1) if p else g(y+1) if q else h(z+1)", "if p:\n    a = f(x+1)\nelif q:\n    a = g(y+1)\nelse:\n    a = h(z+1)"),
 ("boolop expr", "p and f(x+1) or g(y+1)", "if p:\n    f(x+1)\nelse:\n    g(y+1)"),
 ("starred value", "a, *b = f(x+1), g(y+1), h(z+1)", "a = f(x+1)\nb = [g(y+1), h(z+1)]"),
 ("listcomp side effects", "[fn(x+1) for fn in (f, g)]", "f(x+1)\ng(x+1)"),
 ("ann assign tuple", "a: int = 1", "a = 1"),
 ("aug assign", "a += f(x+1)", "a = a + f(x+1)"),
 ("nested tuple expr", "(f(x+1), (g(y+1), h(z+1)))", "f(x+1)\ng(y+1)\nh(z+1)"),
 ("tuple of tuples target", "(a, b), c = (f(x+1), g(y+1)), h(z+1)", "a = f(x+1)\nb = g(y+1)\nc = h(z+1)"),
 ("return tuple", "def k():\n    return f(x+1), g(y+1)", "def k():\n    a = f(x+1)\n    return a, g(y+1)"),
 ("with single", "with p() as a:\n    pass", "with p() as a:\n    pass"),
]
for name, pk, pl in cases:
    a, b = n(pk), n(pl)
    print(f"RESULT {name!r:28} packed={a} plain={b} {'SAME' if a==b else 'DIFF'}")
