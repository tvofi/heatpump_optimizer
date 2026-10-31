import sys, subprocess, importlib.util, re
def load(p, name):
    s=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
head=load(sys.argv[1]+'/tools/audit/carry_audit.py','h')
refs=subprocess.run(['git','for-each-ref','--format=%(refname:short)','refs/remotes/origin/handoff-body/'],capture_output=True,text=True).stdout.split()
# unstripped variant
def unstripped(t): return bool(head.OWED_CARRY.search(t))
flip_s={}; flip_u={}; nbodies=0
for r in refs:
    b=subprocess.run(['git','show',r+':BODY.md'],capture_output=True,text=True)
    if b.returncode: continue
    nbodies+=1
    rows=head.items(b.stdout, False)
    s=[x for x in rows if x['why']=='owed carry']
    if s: flip_s[r]=len(s)
    # unstripped: monkeypatch
    orig=head.owed_carry
    head.owed_carry=lambda t: bool(head.OWED_CARRY.search(t))
    u=[x for x in head.items(b.stdout, False) if x['why']=='owed carry']
    head.owed_carry=orig
    if u: flip_u[r]=len(u)
print('bodies',nbodies)
print('stripped: bodies',len(flip_s),'items',sum(flip_s.values()))
for r,n in sorted(flip_s.items()): print('  S',r,n)
print('unstripped: bodies',len(flip_u),'items',sum(flip_u.values()))
for r in sorted(set(flip_u)-set(flip_s)): print('  U-only',r,flip_u[r])
for r in sorted(flip_u):
    if flip_u[r]!=flip_s.get(r): print('  diff',r,flip_s.get(r),flip_u[r])
