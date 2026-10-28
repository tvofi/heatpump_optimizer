"""Bucket hm3_out.tsv: M = mechanical (carry@t yes, or the branch's own patch unchanged); G = the own
patch moved only in shared registries; S = the own patch moved in anything else (real rework).
Also reads each verdict's text to see whether the reviewer's turn was itself a carry."""
import subprocess,collections,re,datetime as dt
REG=re.compile(r'^(tests/(features\.py|closures\.json|structure_budgets\.json|golden/(card_)?claimed_drift\.txt|mutation_ledger/.*|guard_pins\.py)|dev/programme/rosters/.*|dev/audit/harnesses/r10_.*_mutants\.py|dev/programme/delivery/\d+\.md)$')
def g(*a): return subprocess.run(['git','-C','wt',*a],capture_output=True,text=True).stdout
# verdict text per (pr, head)
vt={}
for ref in g('for-each-ref','--format=%(refname)','refs/remotes/origin/verdict/','refs/remotes/origin/review/').split():
    for c in g('log','--format=%H',ref,'--','VERDICT.md').split():
        t=g('show',f'{c}:VERDICT.md'); m=re.match(r'Fix review:\s+\w+\s+([0-9a-f]{40})',t)
        if m: vt.setdefault(m.group(1)[:8],t)
c=collections.Counter(); P=lambda s:dt.datetime.fromisoformat(s)
lag={l.split('\t')[2]:int(l.split('\t')[7]) for l in open('hm2_out.tsv') if l.startswith('#')}
L=collections.Counter()
for l in open('hm3_out.tsv'):
    if not l.startswith('#'): continue
    pr,t1,pair,kind,at,same,side,files=(l.rstrip('\n').split('\t')+[''])[:8]
    fl=[f for f in files.split(',') if f]
    b='M' if at=='carry@t=yes' or same in('same','row-only') else ('G' if fl and all(REG.match(f) for f in fl) else 'S')
    h1=pair.split('->')[1]; txt=vt.get(h1,'')
    rc='carry-turn' if re.search(r'\bcarr(y|ied|ies)\b',txt[:1500],re.I) else 'full-turn'
    c[(b,side)]+=1; c[(b,side,rc)]+=1; L[(b,side)]+=lag[pair]
    print(pr,t1[:16],b,side,rc,kind,files[:80],sep='\t')
for k in sorted(c,key=str): print('SUM',k,c[k])
for k in sorted(L): print('LAG',k,L[k])
