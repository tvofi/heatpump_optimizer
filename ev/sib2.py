import ast, sys
sys.path.insert(0, sys.argv[1] + "/tools/audit")
from archscore.metrics import footprint
n = lambda s: footprint.logic_stmts(ast.parse(s))
cases = [
 # my own plants (reviewer round 2)
 ("walrus in list display assign", "r = [a := f(x+1), b := g(y+1)]", "a = f(x+1)\nb = g(y+1)\nr = [a, b]"),
 ("walrus in if header x2", "if (a := f(x+1)) and (b := g(y+1)):\n    pass", "a = f(x+1)\nb = g(y+1)\nif a and b:\n    pass"),
 ("walrus in return", "def k():\n    return (a := f(x+1)), (b := g(y+1))", "def k():\n    a = f(x+1)\n    b = g(y+1)\n    return a, b"),
 ("set display 3", "{f(x+1), g(y+1), h(z+1)}", "f(x+1)\ng(y+1)\nh(z+1)"),
 ("dict display values+keys", "{f(x+1): g(y+1)}", "f(x+1)\ng(y+1)"),
 ("list display expr", "[f(x+1), g(y+1)]", "f(x+1)\ng(y+1)"),
 ("ifexp chain 3", "a = f(x+1) if p else g(y+1) if q else h(z+1) if r else k(w+1)", "if p:\n    a = f(x+1)\nelif q:\n    a = g(y+1)\nelif r:\n    a = h(z+1)\nelse:\n    a = k(w+1)"),
 ("ifexp chain as expr stmt", "f(x+1) if p else g(y+1) if q else h(z+1)", "if p:\n    f(x+1)\nelif q:\n    g(y+1)\nelse:\n    h(z+1)"),
 ("ifexp chain in return", "def k():\n    return f(x+1) if p else g(y+1) if q else h(z+1)", "def k():\n    if p:\n        return f(x+1)\n    elif q:\n        return g(y+1)\n    else:\n        return h(z+1)"),
 ("ifexp chain nested in body side", "a = (f(x+1) if q else g(y+1)) if p else h(z+1)", "if p:\n    if q:\n        a = f(x+1)\n    else:\n        a = g(y+1)\nelse:\n    a = h(z+1)"),
 ("starred target", "a, *b = f(x+1), g(y+1), h(z+1)", "a = f(x+1)\nb = [g(y+1), h(z+1)]"),
 ("starred head", "*a, b = f(x+1), g(y+1), h(z+1)", "a = [f(x+1), g(y+1)]\nb = h(z+1)"),
 ("for two-element literal", "for a, b in [(f(x+1), g(y+1))]:\n    pass", "a = f(x+1)\nb = g(y+1)\npass"),
 ("for two-element literal tuple", "for a, b in ((f(x+1), g(y+1)),):\n    pass", "a = f(x+1)\nb = g(y+1)\npass"),
 ("for nested tuple target", "for (a, b), c in [((f(x+1), g(y+1)), h(z+1))]:\n    pass", "a = f(x+1)\nb = g(y+1)\nc = h(z+1)\npass"),
 ("for two-row literal", "for a, b in [(f(x+1), g(y+1)), (h(z+1), k(w+1))]:\n    s(a, b)", "s(f(x+1), g(y+1))\ns(h(z+1), k(w+1))"),
 ("async for literal", "async def q():\n    async for a, b in [(f(x+1), g(y+1))]:\n        pass", "async def q():\n    a = f(x+1)\n    b = g(y+1)"),
 ("comprehension for literal", "r = [s(a, b) for a, b in [(f(x+1), g(y+1))]]", "a = f(x+1)\nb = g(y+1)\nr = [s(a, b)]"),
 ("chain + tuple", "a = b, c = f(x+1), g(y+1)", "a = (f(x+1), g(y+1))\nb = a[0]\nc = a[1]"),
 ("annassign tuple value", "a: tuple = f(x+1), g(y+1)", "a: tuple = (f(x+1), g(y+1))"),
 ("lambda body tuple", "k = lambda: (f(x+1), g(y+1))", "def k():\n    return f(x+1), g(y+1)"),
 ("boolop expr", "p and f(x+1) or g(y+1)", "if p:\n    f(x+1)\nelse:\n    g(y+1)"),
 ("listcomp side effects", "[fn(x+1) for fn in (f, g)]", "f(x+1)\ng(x+1)"),
 ("semicolon", "a = f(x+1); b = g(y+1)", "a = f(x+1)\nb = g(y+1)"),
 # controls
 ("ctrl display one target", "x = [1, 2, 3]", None),
 ("ctrl attr display one target", "cur = (self.a, self.b, self.c, self.d)", None),
 ("ctrl lone ifexp", "a = f(x+1) if p else g(y+1)", None),
 ("ctrl for one target literal", "for x in (1, 2, 3):\n    pass", None),
]
for name, pk, pl in cases:
    a = n(pk); b = n(pl) if pl else None
    print(f"RESULT {name!r:36} packed={a} plain={b} {'' if pl is None else ('SAME' if a==b else 'DIFF')}")
