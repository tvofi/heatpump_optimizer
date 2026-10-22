import ast,subprocess,sys
P="dev/audit/harnesses/r10_seat_selftests_mutants.py"
def ids(rev):
    t=ast.parse(subprocess.check_output(["git","show",f"{rev}:{P}"]))
    for n in t.body:
        if isinstance(n,ast.Assign) and any(getattr(x,'id','')=="MUTANTS" for x in n.targets):
            return [e.elts[0].value for e in n.value.elts]
m,b,h=(ids(r) for r in sys.argv[1:4])
u=set(m)|set(b)
print(f"main={len(m)} branch={len(b)} head={len(h)} union={len(u)} missing_from_head={sorted(u-set(h))} extra_in_head={sorted(set(h)-u)} order_tail={h[-10:]}")
sys.exit(1 if u-set(h) else 0)
