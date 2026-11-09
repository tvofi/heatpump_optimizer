import sys, re, ast
src=open("tests/features.py").read()
lines=src.split("\n")
s=next(i for i,l in enumerate(lines) if l.startswith("# R10-COMBI-TANK-STORE (#3225"))
e=next(i for i,l in enumerate(lines) if l.startswith("# R10-BUFFER-STORE review 1: the savings reference"))
# top-level imports, defs, classes before the block (no statements)
pre=ast.parse("\n".join(lines[:s]))
keep=[n for n in pre.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef,ast.ClassDef))]
extra=[l for l in sys.argv[1:]]
first=[n for n in pre.body if n.end_lineno<=217]
ns={"__name__":"__blk__"}
import io,contextlib
for n in first+[n for n in keep if n.lineno>217]:
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(ast.Module(body=[n],type_ignores=[]),"pre","exec"),ns)
    except Exception as x: pass
R0=ns["R"]; R0.failures=0; R0.checks=0
for x in extra: exec(x,ns)
try:
    exec(compile("\n".join(lines[s:e]),"blk","exec"),ns)
except Exception as x:
    print("EXC",type(x).__name__,x); sys.exit(3)
sys.exit(ns["R"].close("COMBI BLOCK"))
