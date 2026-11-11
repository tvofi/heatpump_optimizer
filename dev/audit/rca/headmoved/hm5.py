"""orchestrator.md section 11's whole carry predicate at the time of each re-verification:
app_approve.sh --carry (script of main@t) says CARRY: yes, AND `git diff --name-only h0 h1` misses the
branch's own diff (merge-base(h1, main@t)..h1), AND both claim files at h1 equal main@t's."""
import subprocess,collections
def g(*a): return subprocess.run(['git','-C','wt',*a],capture_output=True,text=True).stdout
CL=['tests/golden/claimed_drift.txt','tests/golden/card_claimed_drift.txt']
b4={}
for l in open('hm4_out.tsv'):
    if l.startswith('#'): f=l.split('\t'); b4[(f[0],f[1])]=f[2:5]
c=collections.Counter()
for l in open('hm3_out.tsv'):
    if not l.startswith('#'): continue
    pr,t1,pair,kind,at,same,side=l.rstrip('\n').split('\t')[:7]
    h0,h1=[g('rev-parse',x).strip() for x in pair.split('->')]
    m=g('rev-list','-1','--first-parent',f'--before={t1}','origin/main').strip()
    moved=set(g('diff','--name-only',h0,h1).split())
    own=set(g('diff','--name-only',g('merge-base',h1,m).strip(),h1).split())
    claims=all(g('rev-parse',f'{h1}:{p}')==g('rev-parse',f'{m}:{p}') for p in CL)
    p11 = at=='carry@t=yes' and not (moved & own) and claims
    why = 'P11' if p11 else ('carry-no' if at!='carry@t=yes' else ('overlap' if moved&own else 'claims'))
    b=b4[(pr,t1[:16])][0]
    c[(b,side,why)]+=1
    print(pr,t1[:16],b,side,why,','.join(sorted(moved&own))[:100],sep='\t')
for k in sorted(c): print('SUM',k,c[k])
