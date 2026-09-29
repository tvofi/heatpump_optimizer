import json, re, subprocess
D='/tmp/claude-0/-home-user-heatpump-optimizer/1b5fa08f-9bd8-59e8-b197-ffb291fc579e/scratchpad/archscore/status/'
R='/home/user/heatpump_optimizer'
def git(*a): return subprocess.run(['git','-C',R,*a],capture_output=True,text=True).stdout.strip()
a=json.load(open(D+'src/main-prestudy-ALT-ROSTER.json')); b=json.load(open(D+'src/fixplan-wave-r9-groups.json'))
A={g['group']:g for g in a['groups']}; B={g['group']:g for g in b['groups']}
# merges on main
merges={}
for line in git('log','--first-parent','--format=%H %s','origin/main').splitlines():
    h,s=line.split(' ',1); m=re.match(r'Merge pull request #(\d+) from (\S+)',s)
    if m: merges[int(m.group(1))]=(h,m.group(2))
since=set(int(x) for x in re.findall(r'#(\d+)',git('log','--first-parent','--format=%s','5a2a62ff..origin/main')))
OPEN_PR={1767:('handoff/r9-f1-coordinator-6','929e5aa0fa81760339b56a24bcdb03f101358ee6')}
C201_NEW='https://github.com/tvofi/heatpump_optimizer/issues/201#issuecomment-5899374096'
C201_BATCH='https://github.com/tvofi/heatpump_optimizer/issues/201#issuecomment-5896576410'
PRURL='https://github.com/tvofi/heatpump_optimizer/pull/%d'
out={}
for gid in [g['group'] for g in a['groups']]:
    ga,gb=A[gid],B[gid]; ra,rb=ga['resume'] or {},gb['resume'] or {}
    rev2=ra.get('stage'); roster=rb.get('stage')
    pr=None
    for s in (rb.get('last_step') or '', ra.get('last_step') or ''):
        m=re.search(r'(?:as|PR) #(\d+)',s)
        if m: pr=int(m.group(1)); break
    rec={'rev2':rev2,'live_roster_stage':roster,'live_roster_commit':rb.get('commit') or None,
         'lane':ga.get('lane'),'after':ga.get('after'),'owner_gate':ga.get('owner_gate'),'blocked_on':ga.get('blocked_on'),
         'issues':ga.get('issues'),'fixes':ga.get('fixes'),'pr':None,'sha':None,'live':None,'evidence':[],'disagreement':[]}
    if pr and pr in merges:
        h,br=merges[pr]
        rec.update(pr=pr,sha=h,live='merged')
        rec['evidence'].append(f'git: {h[:8]} "Merge pull request #{pr} from {br}" is first-parent on origin/main 4d33b25c')
        rec['evidence'].append(PRURL%pr)
        if rb.get('commit') and not h.startswith(rb['commit'][:8]):
            rec['disagreement'].append(f'live roster commit {rb["commit"][:8]} != merge sha {h[:8]}')
        if pr in since: rec['evidence'].append('merged after 5a2a62ff; listed in #201 state batch '+C201_BATCH)
    elif pr and pr in OPEN_PR:
        rec.update(pr=pr,sha=OPEN_PR[pr][1],live='in-review')
    out[gid]=rec
    if roster!=rev2: rec['evidence'].append(f'live roster (handoff/audit-r9-fixplan c5af8f3a) resume.stage={roster}: {rb.get("last_step")}')
# F1.6 special: roster has no PR
f=out['R9-F1.6']
f.update(pr=1767,sha='929e5aa0fa81760339b56a24bcdb03f101358ee6',live='in-review (round 2)')
f['evidence']+=[PRURL%1767+' open, draft, author hpo-author[bot], head handoff/r9-f1-coordinator-6 @929e5aa0 (pushed 2026-09-29 23:18 +0200); branch absorbed main at 7952d8f9 (c9a403fa), not 4d33b25c',
  'PR #1767 check-runs at 929e5aa0 (read 2026-09-29): 34 runs, 0 failure; mutation still in_progress; no GitHub reviews posted',
  'RESUME.md (handoff/audit-r9-plan 4c613d8c) 2026-09-29T21Z: review round 1 BLOCKED (harness + one real seam _fabricated_forecast); round 2 pushed at 929e5aa0, awaiting re-review',
  '#201 newest comment '+C201_NEW+': "In flight: F1.6 round 2 (#1767) -- its merge opens F2.4 || F9.3 || EG-B10"']
f['disagreement'].append('live roster on handoff/audit-r9-fixplan still says stage=not-started with empty commit/last_step, while PR #1767 has been open since 2026-09-29T14:45Z (dispatched 05:23Z per RESUME.md) and #201 newest comment says round 2 in flight')
f['disagreement'].append('rev-2 roster (and its copy on main, tools/audit/round9/prestudy/ALT-ROSTER.json) says not-started')
# EG-B0
e=out['R9-EG-B0']; e['live']='rca-done (no PR; RCA-1736 posted on #1736 comment 5877263448)'; e['evidence'].append('roster last_step unchanged since rev 2; its obligations carried into R9-EG-B1')
# groups merged since rev2: note rev2 disagreement
for gid,r in out.items():
    if r['live']=='merged' and r['rev2']!='done':
        r['disagreement'].append(f'rev-2 roster (and main copy tools/audit/round9/prestudy/ALT-ROSTER.json, landed by #1771) says {r["rev2"]}; merged as #{r["pr"]} {r["sha"][:8]}')
    if r['live']=='merged' and r['live_roster_stage']!='done':
        r['disagreement'].append(f'live roster stage={r["live_roster_stage"]} but merged')
    if r['live'] is None:
        r['live']='not started' if r['live_roster_stage']=='not-started' else r['live_roster_stage']
        br=r and (B[gid]['resume'] or {}).get('branch')
        exists=git('ls-remote','--heads','origin',br) if br else ''
        r['evidence'].append(f'live roster stage=not-started; no open PR; branch {br} '+('EXISTS on origin' if exists else 'absent on origin'))
        if exists: r['disagreement'].append(f'branch {br} exists on origin though roster says not-started')
# open-issue check of fixes[]
open_issues={1759,1758,1757,1756,1755,1754,1748,1747,1745,1744,1743,1742,1741,1740,1739,1738,1737,1736,1687,1686,1664,1663,1661,1660,1659,1658,1657,1656,1655,1654,1653,1652,1651,1650,1649,1647,1646,1645,1644}
for gid,r in out.items():
    fx=r['fixes'] or []
    if r['live']=='merged':
        still=[i for i in fx if i in open_issues]
        if still: r['evidence'].append(f'fixes[] still open on GitHub: {still}')
        else: r['evidence'].append(f'fixes[] {fx} all closed on GitHub' if fx else 'fixes[] empty')
    else:
        closed=[i for i in fx if i not in open_issues]
        if closed: r['disagreement'].append(f'fixes[] {closed} already CLOSED on GitHub though group not merged')
# readiness
done={g for g,r in out.items() if r['live']=='merged'}|{'R9-EG-B0'}
for gid,r in out.items():
    if r['live']=='not started':
        openedges=[x for x in r['after'] if x not in done]
        r['open_after']=openedges
        r['ready']= 'READY now' if not openedges else ('ready when F1.6 merges' if openedges==['R9-F1.6'] else 'waits')
for gid in ['R9-F4.2']:
    out[gid]['evidence'].append('#1655 in fixes[] deliberately left open (free-heat half carried to F1 lane) -- recorded in roster last_step, not a disagreement')
json.dump(out,open(D+'live_status.json','w'),indent=1)
from collections import Counter
print(Counter(r['live'] for r in out.values()))
for g,r in out.items():
    if r.get('ready') and r['ready']!='waits': print(g,r['ready'],r['open_after'],'gate' if r['owner_gate'] else '', r['blocked_on'] and 'BLOCKED')
for g,r in out.items():
    if r['disagreement']: print(g, r['disagreement'])
