# Reviewer's round-2 re-bucketing of ALL 75 entries from the full differing-file list,
# independent of hm3/hm4: M = carry@t yes or own patch same/row-only; G = all files registry; S = else.
import subprocess,re,statistics,collections
REG=re.compile(r'^(tests/(features\.py|closures\.json|structure_budgets\.json|golden/(card_)?claimed_drift\.txt|mutation_ledger/.*|guard_pins\.py)|dev/programme/rosters/.*|dev/audit/harnesses/r10_.*_mutants\.py|dev/programme/delivery/\d+\.md)$')
def g(*a): return subprocess.run(['git',*a],capture_output=True,text=True).stdout
def own(h,m):
    mb=g('merge-base',h,m).strip(); fa={};cur=None
    for x in g('diff','-U0','--no-color',mb,h).splitlines():
        if x.startswith(('@@','index ')): continue
        if x.startswith('diff --git'): cur=x.split(' b/')[-1]; fa[cur]=[]
        elif cur: fa[cur].append(x)
    return fa
D='dev/audit/rca/headmoved/'
hm4={}
for l in open(D+'hm4_out.tsv'):
    if l.startswith('#'): f=l.split('\t'); hm4[(f[0],f[1])]=f[2]
agg=collections.defaultdict(list); mism=0
for l in open(D+'hm2_out.tsv'):
    if not l.startswith('#'): continue
    f=l.rstrip('\n').split('\t'); pr,t1,pair,k1,at,lag,side=f[0],f[1],f[2],f[3],f[6],int(f[7]),f[8]
    h0,h1=[g('rev-parse',x).strip() for x in pair.split('->')]
    m=g('rev-list','-1','--first-parent',f'--before={t1}','origin/main').strip()
    a,c=own(h0,m),own(h1,m)
    fs=sorted(k for k in set(a)|set(c) if a.get(k)!=c.get(k))
    rowonly=bool(fs) and all(re.match(rf'dev/programme/delivery/{pr[1:]}\.md$',x) for x in fs)
    if at=='carry@t=yes' or not fs or rowonly: b='M'
    elif all(REG.match(x) for x in fs): b='G'
    else: b='S'
    if hm4[(pr,t1[:16])]!=b: mism+=1; print('MISMATCH',pr,t1[:16],'hm4='+hm4[(pr,t1[:16])],'mine='+b)
    agg[b].append((side,k1,lag))
for b in 'MGS':
    v=agg[b]; print('RESULT bucket',b,'n',len(v),'after',sum(s=='after' for s,_,_ in v),'blocked',sum(k=='blocked' for _,k,_ in v),'lag_median',statistics.median([x for *_,x in v]),'lag_sum',sum(x for *_,x in v))
print('RESULT mismatches_vs_hm4',mism)
