import json,os
m4=json.load(open('state/u1d-m4.json'))
for k in open('state/keys-D3-u1d-surv.txt').read().split():
    p=f'state/results/complete/{k}.json'
    if not os.path.exists(p): continue
    r=json.load(open(p))
    if r['verdict']!='SURVIVED' or k in m4: continue
    m=r['mutant']; f=m['file'].split('/')[-1]
    print(k, f, m['line'], m['anchor'].split(':')[1].split(' ')[0], m['kind'], repr(m['old'].strip()),'->',repr(m['new'].strip()))
