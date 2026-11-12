#!/usr/bin/env python3
"""scorecard.py --runs main_ci_runs.json --jobs DIR --verdicts verdicts.json --merges merges.tsv --train train.log --roster roster.json
The convergence scorecard, report-only. Read-only on every input; makes no GitHub call (the inputs are refreshed by the
commands in REVIEW.md appendix A). One line per signal: value, n, rule, and the null control it must satisfy.

A_gate  share of the last 20 CONCLUDED main `CI` push runs whose job named `gate` concluded success. This is what
        tools/release/stamp.py rule 2 reads. Runs with no cached job listing are reported as `unread`, never guessed.
        NULL: a run whose only failed job is governance / instrument-self-tests counts GREEN here and red in A_run.
A_run   share of the same 20 runs whose RUN conclusion is success (the machinery-inclusive status).
Y_rev   over the last 50 distinct PRs by first review verdict (verdicts de-duplicated on pr, head, kind, class word):
        share whose first verdict is `merge`; and M_first, the share whose first verdict is a block in a machinery
        family (carry, body, CI state, merge state, root-cause form, ruling/roster -- the study's FAMILY map).
        NULL: a bus holding only merge verdicts prints 100% and 0%.
Y_train over the last 50 PRs the merge train named and merged: share never on a SKIP or PARK line.
        NULL: a log with no SKIP/PARK line prints 100%. Reported only over train-named PRs (exposure-normalised).
H       hotfix merges among the last 50 code merges (branch token `hotfix`; a naming measure, see REVIEW.md 9.6 caveat).
S       not computed here: `tools/audit/machinery_ratchet.py --measure --head origin/main` and the study's tree_size.sh.
E       product escapes: roster groups with source == outside, plus HOTFIX/bug groups whose files include the product.
"""
import argparse,json,csv,re,glob,os,collections
ap=argparse.ArgumentParser(); [ap.add_argument('--'+k,required=True) for k in('runs','jobs','verdicts','merges','train','roster')]
a=ap.parse_args()
W='<state>/study/work/'
src=open(W+'yield.py').read(); FAM=eval(src[src.index("FAMILY = ["):src.index("def fam(")].split("=",1)[1])
def fam(c):
    for n,rx in FAM:
        if re.match(rx,c): return n
    return "unmapped"
MACH={"carry-bookkeeping","body-bookkeeping","ci-state","merge-state","root-cause-form","ruling-or-roster"}
runs=[r for r in sorted(json.load(open(a.runs)),key=lambda r:r['t']) if r['c'] in('success','failure')][-20:]
gate={}
for f in glob.glob(os.path.join(a.jobs,'jobs_*.json')):
    try: d=json.load(open(f))
    except Exception: continue
    for j in d.get('jobs',[]):
        if j['name']=='gate': gate[int(os.path.basename(f).split('_')[1].split('.')[0])]=j['conclusion']
g=[('success' if r['c']=='success' else gate.get(r['id'],'unread')) for r in runs]
c=collections.Counter(g); read=c['success']+c['failure']
print(f"A_gate  {c['success']}/{read} read = {100*c['success']/max(1,read):.0f}%  (unread {c['unread']} of {len(runs)}; window {runs[0]['t']} .. {runs[-1]['t']})")
print(f"A_run   {sum(r['c']=='success' for r in runs)}/{len(runs)} = {100*sum(r['c']=='success' for r in runs)/len(runs):.0f}%")
V=json.load(open(a.verdicts))["verdicts"]; seen=set(); by=collections.OrderedDict()
for v in V:
    k=(v["pr"],v["head"],v["kind"],v["cls"])
    if k in seen: continue
    seen.add(k); by.setdefault(v["pr"],[]).append(v)
last=sorted(by.items(),key=lambda kv:kv[1][0]["t"])[-50:]
fp=sum(vs[0]["kind"]=="merge" for _,vs in last); mf=sum(vs[0]["kind"]=="blocked" and fam(vs[0]["cls"]) in MACH for _,vs in last)
print(f"Y_rev   first verdict merge {fp}/{len(last)} = {100*fp/len(last):.0f}%   M_first {mf}/{len(last)} = {100*mf/len(last):.0f}%   (first verdicts {last[0][1][0]['t'][:16]} .. {last[-1][1][0]['t'][:16]})")
M=sorted(csv.DictReader(open(a.merges),delimiter="\t"),key=lambda r:int(r["ct"])); merged=[r["pr"] for r in M if r["pr"]]
sk=set(); named=set()
for l in open(a.train,errors="replace"):
    m=re.match(r"SKIP #(\d+)",l)
    if m: sk.add(m[1])
    if l.startswith("PARK"): sk|=set(re.findall(r"#(\d{4})",l)[:1])
    if re.match(r"(BATCH|SKIP|PARK|MERGED|ADMIT|ALREADY)",l): named|=set(re.findall(r"#(\d{4})",l))
tn=[p for p in merged if p in named][-50:]
print(f"Y_train never skipped or parked {sum(p not in sk for p in tn)}/{len(tn)} = {100*sum(p not in sk for p in tn)/max(1,len(tn)):.0f}%  (last 50 train-named merged PRs)")
code=[r for r in M if r["class"] in("production","instrument")][-50:]
print(f"H       hotfix-token merges {sum('hotfix' in r['tokens'] for r in code)}/{len(code)} of the last 50 code merges; production merges among them {sum(r['class']=='production' for r in code)}")
G=json.load(open(a.roster))["groups"]
out=[x for x in G if x.get("source")=="outside"]; ph=[x for x in G if ('HOTFIX' in x["group"] or x.get("kind") in("bug","hotfix")) and any(f.startswith("custom_components/") for f in (x.get("files") or []))]
print(f"E       roster groups from outside reports {len(out)}; hotfix or bug groups touching the product {len(ph)}; open among both {sum((x.get('resume') or {}).get('stage')!='done' for x in out+ph)}")
