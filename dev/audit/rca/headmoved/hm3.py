"""For each re-verification in hm2_out.tsv: does the branch's own patch change between the two heads?
own(H) = `git diff -U0 merge-base(H, main@t)..H` with hunk headers and index lines dropped, so a
patch moved only by context compares equal. same = the move was mechanical; differs = new branch content."""
import subprocess,collections,re
def g(*a):
    return subprocess.run(['git','-C','wt',*a],capture_output=True,text=True).stdout
def own(h,m):
    mb=g('merge-base',h,m).strip()
    d=g('diff','-U0','--no-color',mb,h)
    return [x for x in d.splitlines() if not x.startswith(('@@','index '))]
c=collections.Counter(); out=[]
for l in open('hm2_out.tsv'):
    if not l.startswith('#'): continue
    f=l.rstrip('\n').split('\t'); pr,t1,pair,kind,at,side=f[0],f[1],f[2],f[4],f[6],f[8]
    h0,h1=pair.split('->'); m=g('rev-list','-1','--first-parent',f'--before={t1}','origin/main').strip()
    a,b=own(h0,m),own(h1,m)
    same='same' if a==b else 'differs'
    if same=='differs':
        # files whose own patch differs
        fa={};cur=None
        for x in a:
            if x.startswith('diff --git'): cur=x.split(' b/')[-1]; fa[cur]=[]
            elif cur: fa[cur].append(x)
        fb={};cur=None
        for x in b:
            if x.startswith('diff --git'): cur=x.split(' b/')[-1]; fb[cur]=[]
            elif cur: fb[cur].append(x)
        files=sorted(k for k in set(fa)|set(fb) if fa.get(k)!=fb.get(k))
        if files and all(re.match(rf'dev/programme/delivery/{pr[1:]}\.md$',k) for k in files): same='row-only'
    else: files=[]
    c[(kind,at,same,side)]+=1
    print('\t'.join([pr,t1,pair,kind,at,same,side,','.join(files)]))
for k in sorted(c): print('SUM',k,c[k])
