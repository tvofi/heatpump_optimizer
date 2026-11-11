"""For each attempt whose every stale job was really success (a false red): the run's later attempts and outcome."""
import json,subprocess,re,sys
R="tvofi/heatpump_optimizer"
rows=[json.loads(x) for x in open(sys.argv[1] if len(sys.argv) > 1 else 'reasons.jsonl')]
seen=set()
for r in sorted((x for x in rows if 'why' in x),key=lambda r:r['read_at'] or ''):
    w=r['why']
    if not w or not all(re.match(r'(FAIL )?.+: (PENDING|ABSENT) \(this run\)$',x) or x=='FAIL prelude: None' for x in w): continue
    false_red=all(v['conclusion']=='success' for v in r['lags'].values())
    j=(r['run'],r['attempt'])
    if j in seen: continue
    seen.add(j)
    p=subprocess.run(['gh','api',f"repos/{R}/actions/runs/{r['run']}/jobs?filter=all&per_page=100",'--paginate','--jq','.jobs[]|select(.name=="gate")|[.run_attempt,.conclusion,.completed_at]|@tsv'],capture_output=True,text=True)
    atts=[l.split('\t') for l in p.stdout.splitlines()]
    atts.sort(key=lambda a:int(a[0]))
    print(r['run'],'a%s'%r['attempt'],r['event'],r['read_at'],'FALSE' if false_red else 'TRUE-RED',' '.join(f"a{a[0]}={a[1]}@{a[2][11:19]}" for a in atts))
