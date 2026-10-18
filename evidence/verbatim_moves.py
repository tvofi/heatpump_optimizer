import ast,sys,subprocess
def src(ref,p): return subprocess.run(["git","-C","wt","show",f"{ref}:custom_components/heatpump_optimizer/{p}"],capture_output=True,text=True,check=True).stdout
MB,H=sys.argv[1],"HEAD"
def fn(s,name):
    t=ast.parse(s)
    for n in t.body:
        if isinstance(n,ast.FunctionDef) and n.name==name:
            return "\n".join(s.splitlines()[n.lineno-1:n.end_lineno])
a=fn(src(MB,"optimizer.py"),"_utc_step_starts"); b=fn(src(H,"drift.py"),"utc_step_starts")
print("RESULT clock_body_identical_modulo_name=", a.replace("def _utc_step_starts","def utc_step_starts")==b)
def consts(s):
    t=ast.parse(s); out={}
    for n in t.body:
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id.startswith("REASON_"):
            out[n.targets[0].id]=ast.literal_eval(n.value)
    return out
base=consts(src(MB,"optimizer.py")); head_p=consts(src(H,"payload.py")); head_o=consts(src(H,"optimizer.py"))
print("RESULT reason_codes_base_optimizer=",len(base)," head_payload=",len(head_p)," head_optimizer_assigns=",len(head_o))
print("RESULT reason_values_identical=", base==head_p)
print("RESULT payload_base_reasons=",len(consts(src(MB,"payload.py"))))
