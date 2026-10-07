"""Reviewer's own scan (r9c-rev-2025): attribute reads on config holders that EntryConfig does not
declare, string-literal key reads on them, and module-level undefined names."""
import ast, sys, pathlib, builtins, dataclasses
root = pathlib.Path(sys.argv[1]) / "custom_components/heatpump_optimizer"
sys.path.insert(0, str(root.parent)); sys.path.insert(0, str(pathlib.Path(sys.argv[1]) / "tests/hastub"))
from heatpump_optimizer.entry_config import EntryConfig
from heatpump_optimizer import const
FIELDS = {f.name for f in dataclasses.fields(EntryConfig)}
MAP = {"get","keys","items","values","raw","from_mapping","__getitem__"}
CONFVALS = {v for k,v in vars(const).items() if k.startswith("CONF_") and isinstance(v,str)}
HOLDERS = {"_config","effective_config","entry_config"}
MIGR = ["coordinator.py","__init__.py","binary_sensor.py","optimizer.py","climate.py","disinfection.py","legionella.py","pump_arbiter.py","pump_signals.py","sensor.py","setpoint_check.py","silent_mode.py"]
def holder(n):
    return (isinstance(n,ast.Name) and n.id in HOLDERS) or (isinstance(n,ast.Attribute) and n.attr in HOLDERS)
bad_attr, lit = [], []
for m in MIGR:
    t = ast.parse((root/m).read_text())
    for n in ast.walk(t):
        if isinstance(n,ast.Attribute) and holder(n.value) and n.attr not in FIELDS|MAP and not n.attr.startswith("__"):
            bad_attr.append((m,n.lineno,n.attr))
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=="get" and holder(n.func.value):
            lit.append((m,n.lineno,ast.unparse(n)[:90]))
        if isinstance(n,ast.Subscript) and holder(n.value) and isinstance(n.ctx,ast.Load):
            lit.append((m,n.lineno,ast.unparse(n)[:90]))
        if False:
            lit.append((m,n.lineno,"literal "+repr(n.value)))
print("ATTR-NOT-A-FIELD", len(bad_attr)); [print(" ",x) for x in bad_attr]
print("HOLDER-MAPPING-READS", len(lit)); [print(" ",x) for x in lit]
# undefined module-level names
und = {}
for p in sorted(root.glob("*.py")):
    t = ast.parse(p.read_text()); defined=set(dir(builtins))|{"__file__","__name__"}
    for n in ast.walk(t):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)): defined.add(n.name)
        elif isinstance(n,(ast.Import,ast.ImportFrom)):
            for a in n.names: defined.add((a.asname or a.name).split(".")[0])
        elif isinstance(n,ast.Name) and isinstance(n.ctx,(ast.Store,ast.Del)): defined.add(n.id)
        elif isinstance(n,ast.arg): defined.add(n.arg)
        elif isinstance(n,ast.ExceptHandler) and n.name: defined.add(n.name)
        elif isinstance(n, ast.alias): pass
    if any(isinstance(n,ast.ImportFrom) and any(a.name=="*" for a in n.names) for n in ast.walk(t)): continue
    loads = {n.id for n in ast.walk(t) if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Load)}
    u = sorted(loads-defined)
    if u: und[p.name]=u
print("UNDEFINED", und)
