# independent: verdict coverage and block classes from the s1 raw cache
import json,glob,re,os,collections,sys
C=os.environ['TMPDIR'].rstrip('/')+'/d13s1-cache-1913f0dd7'
RE=re.compile(r'^Fix review:\s+(merge|blocked)\s+([0-9a-f]{40})(?:\s+([a-z][a-z0-9-]*)\s*:)?')
prs=[int(x) for x in open('winprs.txt').read().split()]
nov=[];cls=collections.Counter();blocked=0;maxlen=0
for n in prs:
    pr=json.load(open(f'{C}/_repos_tvofi_heatpump_optimizer_pulls_{n}.json'))
    items=[]
    for g in glob.glob(f'{C}/_repos_tvofi_heatpump_optimizer_issues_{n}_comments*')+glob.glob(f'{C}/_repos_tvofi_heatpump_optimizer_pulls_{n}_reviews*'):
        d=json.load(open(g)); maxlen=max(maxlen,len(d)); items+=d
    vs=[m for i in items if (m:=RE.match((i.get('body') or '').strip().split('\n')[0]))]
    if not vs: nov.append((n,pr['title'][:30]))
    for m in vs:
        if m.group(1)=='blocked': blocked+=1; cls[m.group(3) or 'bare']+=1
print('prs',len(prs),'no_verdict',len(nov),'max_page_len',maxlen)
for x in nov: print(' ',x)
print('blocked',blocked,cls.most_common(6),'head-moved',cls['head-moved'])
