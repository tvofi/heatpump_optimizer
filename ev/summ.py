import json,sys
t=open(sys.argv[1]).read(); d=json.loads(t[t.index('{'):])
aw=[o for o in d['away'] if o.get('commanded_return')]
print('cycles',d['cycles'],'counts',d['counts'])
print('away offenders', d['results'].get('away'))
print('commanded', len(aw), 'views', sorted({(o['active'],o['override'],o['recovery'],o['floor'],o['target']) for o in aw}))
print('space_kwh', min(o['space_kwh'] for o in aw) if aw else None, max(o['space_kwh'] for o in aw) if aw else None)
print('cycle_cost', d['results'].get('cycle_cost'))
json.dump([{k:o[k] for k in ('t','active','override','recovery','floor','target','commanded_return')} for o in d['away']], open(sys.argv[1]+'.views','w'))
