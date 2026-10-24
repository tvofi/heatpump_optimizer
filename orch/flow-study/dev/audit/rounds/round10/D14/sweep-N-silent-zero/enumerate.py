"""Class N-silent-zero, production arm: every ingress seam that stores a parsed
external result into coordinator state.

Seam: a function that reads an external source (HTTP session, a service call
with return_response, pull_prices, an Open-Meteo fetch) and assigns a non-constant
value to `self.<attr>`. The seam is GUARDED when the assignment sits under an
`if` whose test names the very value assigned (so an empty parse cannot replace
held data); otherwise UNGUARDED -- an empty parse is stored and the fetch reads
as success, the D1-s3-01 shape.

Usage: python3 enumerate.py [ROOT]            (default custom_components/heatpump_optimizer)
       python3 enumerate.py --null            (clean fixture: expect unguarded=0)
       python3 enumerate.py --perturb         (drops open_meteo's `if forecast:`; expect +1)
"""
import ast, pathlib, re, sys, tempfile, shutil

MARKERS = ("async_get_clientsession", "pull_prices", "_fenced", "return_response", ".json(")

def names_in(node):
    return {ast.unparse(n) for n in ast.walk(node) if isinstance(n, (ast.Name, ast.Attribute, ast.Call))}

def scan(root):
    seams = []
    for p in sorted(pathlib.Path(root).rglob("*.py")):
        src = p.read_text()
        tree = ast.parse(src)
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            body = ast.get_source_segment(src, fn) or ""
            if not any(m in body for m in MARKERS):
                continue
            def walk(stmts, guards):
                for s in stmts:
                    if isinstance(s, ast.Assign) and len(s.targets) == 1:
                        t = s.targets[0]
                        if (isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                                and t.value.id == "self" and not isinstance(s.value, (ast.Constant, ast.List, ast.Dict))
                                and not (isinstance(s.value, ast.Name) and s.value.id in ("None",))):
                            val = ast.unparse(s.value)
                            if isinstance(s.value, (ast.Name, ast.Call)) and val != "now" and not val.startswith(("dt_util", "OpenMeteoSolar", "_fabricated")):
                                ok = any(val in g for g in guards)
                                seams.append((str(p), fn.name, f"self.{t.attr} = {val}", s.lineno,
                                              "GUARDED" if ok else "UNGUARDED"))
                    for fld in ("body", "orelse", "handlers", "finalbody"):
                        sub = getattr(s, fld, None)
                        if isinstance(sub, list):
                            g = guards | ({ast.unparse(s.test)} if isinstance(s, ast.If) and fld == "body" else set())
                            walk(sub, g)
            walk(fn.body, frozenset())
    return seams

def report(root):
    seams = scan(root)
    for f, fn, a, ln, st in seams:
        print(f"SEAM {st} {f}:{ln} {fn} :: {a}")
    u = sum(1 for s in seams if s[4] == "UNGUARDED")
    print(f"RESULT seams={len(seams)} count")
    print(f"RESULT unguarded={u} count")
    return u

NULL_FIXTURE = '''
class C:
    async def _fetch(self, session):
        s = async_get_clientsession(self.hass)
        rows = await pull_prices(s)
        if rows:
            self._prices = rows
'''

if __name__ == "__main__":
    pkg = "custom_components/heatpump_optimizer"
    if "--null" in sys.argv:
        d = tempfile.mkdtemp(); pathlib.Path(d, "fx.py").write_text(NULL_FIXTURE); report(d); shutil.rmtree(d)
    elif "--perturb" in sys.argv:
        d = tempfile.mkdtemp(); shutil.copytree(pkg, d + "/pkg")
        om = pathlib.Path(d, "pkg/open_meteo.py"); s = om.read_text()
        s2 = s.replace("        if forecast:\n            self._forecast = forecast", "        self._forecast = forecast", 1)
        assert s2 != s; om.write_text(s2); report(d + "/pkg"); shutil.rmtree(d)
    else:
        report(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else pkg)
