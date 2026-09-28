import ast,sys
src=open(sys.argv[1]).read();t=ast.parse(src)
# map node->enclosing function
def funcs(t):
    for f in ast.walk(t):
        if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef)):
            yield f
consts=set()
for n in t.body:
    if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str):
        for tg in n.targets:
            if isinstance(tg,ast.Name): consts.add(tg.id)
for f in funcs(t):
    for n in ast.walk(f):
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in('Optional','Required') and isinstance(n.func.value,ast.Name) and n.func.value.id=='vol' and n.args:
            a=n.args[0]
            if isinstance(a,ast.Constant): continue
            if isinstance(a,ast.Name) and (a.id in consts or a.id.isupper()): continue
            if isinstance(a,ast.Attribute) and a.attr.isupper(): continue
            print(f.name, n.lineno, ast.unparse(a))
