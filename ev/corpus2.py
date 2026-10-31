import sys, subprocess, importlib.util
def load(p, name):
    s=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
h=load(sys.argv[1]+'/tools/audit/carry_audit.py','h')
refs=subprocess.run(['git','for-each-ref','--format=%(refname:short)','refs/remotes/origin/handoff-body/'],capture_output=True,text=True).stdout.split()
def unrouted(rows): return [x for x in rows if x['why']=='owed carry' and not h.CARRY.search(x.get('text',''))]
print(sorted(h.items("Carry 1: not done in this pull request.\n",False)[0].keys()))
S={};U={}
orig=h.owed_carry
for r in refs:
    b=subprocess.run(['git','show',r+':BODY.md'],capture_output=True,text=True)
    if b.returncode: continue
    s=unrouted(h.items(b.stdout,False))
    h.owed_carry=lambda t: bool(h.OWED_CARRY.search(t))
    u=unrouted(h.items(b.stdout,False))
    h.owed_carry=orig
    if s: S[r]=s
    if u: U[r]=u
print('stripped unrouted: bodies',len(S),'items',sum(map(len,S.values())))
for r,v in sorted(S.items()): print(' S',r.split('/')[-1],len(v),[x.get('id') for x in v][:4])
print('unstripped unrouted: bodies',len(U),'items',sum(map(len,U.values())))
for r in sorted(U):
    if len(U[r])!=len(S.get(r,[])): print(' diff',r.split('/')[-1],len(S.get(r,[])),len(U[r]))
