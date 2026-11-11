"""Reclassify hm_out.tsv entries against origin/main as it stood at each verdict.
A first-parent commit of prev..cur is: main (merge, 2nd parent on main@t), bot (bot author),
code (merge of a non-main head: update_pr.sh merging an authored code head), row (own commit,
only dev/programme/delivery/<N>.md), own (other). Carry is run with the app_approve.sh of main@t."""
import subprocess,collections,datetime as dt,sys
def g(*a):
    r=subprocess.run(['git','-C','wt',*a],capture_output=True,text=True); return r.stdout.strip(), r.returncode
P=lambda s:dt.datetime.fromisoformat(s)
CUT=P('2026-10-25T07:38:00+00:00')
tot=collections.Counter(); after=collections.Counter(); lag=collections.Counter()
for l in open('hm_out.tsv'):
    if not l.startswith('#'): continue
    pr,t1,pair,k1=l.split('\t')[:4]; n=pr[1:]
    h0,h1=pair.split('->'); H0,_=g('rev-parse',h0); H1,_=g('rev-parse',h1)
    m,_=g('rev-list','-1','--first-parent',f'--before={t1}','origin/main')
    cls=collections.Counter()
    log,_=g('log','--first-parent','--format=%H%x09%P%x09%an',f'{H0}..{H1}')
    for x in log.splitlines():
        h,ps,an=x.split('\t'); ps=ps.split()
        if 'bot' in an.lower(): cls['bot']+=1; continue
        if len(ps)>1:
            on=subprocess.run(['git','-C','wt','merge-base','--is-ancestor',ps[1],m]).returncode==0
            if on: cls['main']+=1; continue
            fs,_=g('diff','--name-only',ps[0],h)  # what the merge brought relative to the branch
            # what the merged head itself authored, beyond main@t
            mb,_=g('merge-base',ps[1],m); own,_=g('diff','--name-only',f'{ps[0]}...{ps[1]}')
            cls['code-row' if own and all(f==f'dev/programme/delivery/{n}.md' for f in own.split()) else 'code']+=1; continue
        fs,_=g('diff-tree','--no-commit-id','--name-only','-r',h)
        cls['row' if fs and all(f==f'dev/programme/delivery/{n}.md' for f in fs.split()) else 'own']+=1
    kind=next((k for k in ('own','code','row','code-row','bot','main') if cls[k]),'empty')
    src,rc=g('show',f'{m}:tools/pr/app_approve.sh')
    if rc: src,_=g('show',f'{m}:tools/audit/app_approve.sh')
    open('aa_at.sh','w').write(src+'\n')
    r=subprocess.run(['bash','../aa_at.sh','--carry',H0,H1,m],cwd='wt',capture_output=True,text=True)
    at='yes' if 'CARRY: yes' in r.stdout else 'no'
    ct,_=g('log','-1','--format=%cI',H1); lg=round((P(t1)-P(ct)).total_seconds()/60)
    late=P(t1)>=CUT
    tot[(kind,at)]+=1; lag[(kind,at)]+=lg
    if late: after[(kind,at)]+=1
    print('\t'.join([pr,t1,pair,k1,kind,str(dict(cls)),'carry@t='+at,str(lg),'after' if late else 'before']))
for k in sorted(tot): print('SUM',k,'n',tot[k],'after',after[k],'lag_min',lag[k])
