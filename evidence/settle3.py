import json,sys
rs=json.load(open(sys.argv[1]))['check_runs']
if not rs or any(r['status']!='completed' for r in rs): sys.exit(1)
other=[r for r in rs if r['name']!='pr-contract']
redr=[r for r in other if r['conclusion'] in ('failure','timed_out','cancelled')]
red=[r['name'] for r in redr]
suites={r['check_suite']['id'] for r in redr}
last=max([r['completed_at'] for r in other if r['check_suite']['id'] in suites] or [''])
pc=max(r['started_at'] for r in rs if r['name']=='pr-contract')
print('last-completion',last,'newest-contract-start',pc,'red',red)
sys.exit(0 if (not red or pc>last) else 1)
