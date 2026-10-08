"""Reviewer harness: C9a twin case + C9b key multiplicity + fuzz, old vs new."""
import importlib.util, random, sys, tempfile, pathlib
sys.path[:0]=["tests","tests/hastub"]
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
O=load("mt_old","../rp/tests/mutation_table.py"); N=load("mt_new","tests/mutation_table.py")
def site(f,scope,old,kind,line): return {"file":f,"kind":kind,"old":old,"line":line,"anchor":f"{f}:{scope} {kind}"}
base=[site("p/o.py","_seed","    return out","RETURN_DEL",40)]
for order in (0,1):
    head=[site("p/o.py","_padded","    return out","RETURN_DEL",10), site("p/o.py","_seed","    return out","RETURN_DEL",41)]
    if order: head.reverse()
    for M in (O,N):
        print(f"RESULT C9a order={order} {M.__name__} added={[ (s['anchor'].split(' ')[0], s['line']) for s in M.added_unpinned(head,[dict(b) for b in base])]}")
# re-indent null
for M in (O,N): print(f"RESULT C9a-null {M.__name__} added={M.added_unpinned([site('p/o.py','_seed','        return out','RETURN_DEL',40)],[dict(base[0])])}")
d=tempfile.mkdtemp(); p=pathlib.Path(d)/"chain.py"; p.write_text("def f(x, y):\n    if 0 < x < 9 < y:\n        return 1\n    return 0\n")
c=[s for s in N.candidates(p) if s["kind"]=="CMP_BOUND"]
print(f"RESULT C9b n={len(c)} old_keys={[O.triage_key(s) for s in c]} new_keys={[k for k,_ in N.added_keys(c)]}")
# fuzz: added count invariant, and new never charges a same-scope twin when a cross-scope one exists
random.seed(7); diff=0; cnt_mismatch=0
for _ in range(20000):
    scopes=["a","b","c"]; texts=["return x","return y"]
    mk=lambda: site("p/f.py",random.choice(scopes),random.choice(texts),"RETURN_DEL",random.randint(1,99))
    b=[mk() for _ in range(random.randint(0,5))]; h=[mk() for _ in range(random.randint(0,6))]
    sides=random.choice([(set(),set()),({"p/f.py"},{"p/f.py"})])
    o=O.added_unpinned([dict(x) for x in h],[dict(x) for x in b],sides); n=N.added_unpinned([dict(x) for x in h],[dict(x) for x in b],sides)
    if len(o)!=len(n): cnt_mismatch+=1
    if sorted((x['line'],x['anchor']) for x in o)!=sorted((x['line'],x['anchor']) for x in n): diff+=1
print(f"RESULT fuzz 20000 count-mismatch={cnt_mismatch} identity-differs={diff}")
