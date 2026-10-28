# Reviewer's re-bucketing of hm4's S entries with the FULL differing-file list (hm4 tests the
# 160-char-truncated hm3 column, and `len(files)<160` sends every truncated list to S).
import subprocess,re,sys
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
b4={}
for l in open(D+'hm4_out.tsv'):
    if l.startswith('#'): f=l.split('\t'); b4[(f[0],f[1])]=(f[2],f[3])
blk={}
for l in open(D+'hm2_out.tsv'):
    if l.startswith('#'): f=l.split('\t'); blk[(f[0],f[1][:16])]=f[3]
n=0;moved=0
for l in open(D+'hm3_out.tsv'):
    if not l.startswith('#'): continue
    f=l.rstrip('\n').split('\t'); pr,t1,pair=f[0],f[1],f[2]
    b,side=b4[(pr,t1[:16])]
    if b!='S': continue
    n+=1
    h0,h1=[g('rev-parse',x).strip() for x in pair.split('->')]
    m=g('rev-list','-1','--first-parent',f'--before={t1}','origin/main').strip()
    a,c=own(h0,m),own(h1,m)
    fs=sorted(k for k in set(a)|set(c) if a.get(k)!=c.get(k))
    non=[x for x in fs if not REG.match(x)]
    nb='S' if non else 'G'
    if nb!=b: moved+=1
    print(pr,t1[:16],side,blk[(pr,t1[:16])],'hm4='+b,'full='+nb,len(fs),','.join(non)[:120],sep='\t')
print('RESULT S_entries',n,'rebucketed_to_G',moved)
