import json, re

SW = '/mnt/project-files/audit-r9/sweep/'
JU = '/mnt/project-files/audit-r9/judge/'

def load(path):
    d = json.load(open(path))
    if isinstance(d, dict) and 'classes' in d:
        return d['classes']
    if isinstance(d, dict) and 'class' in d:
        return [d]
    if isinstance(d, list):
        return d
    raise Exception('unknown shape ' + path)

sweep_by_class = {}
for i in range(1,8):
    for c in load(f'{SW}S{i}.json'):
        key = c.get('class')
        sweep_by_class[key] = c
        c['_source_file'] = f'S{i}.json'

judge = json.load(open(JU + 'CLASSES-DRAFT.json'))
judge_commit = judge['judge_commit']

judge_classes = judge['classes']
print(len(judge_classes), len(sweep_by_class))

# Map judge class to sweep class by id or name
def norm(s):
    return re.sub(r'\W+','', s.lower()) if s else s

sweep_norm = {norm(k): k for k in sweep_by_class}

pairs = []
for jc in judge_classes:
    jid = jc['id']
    jname = jc['name']
    skey = None
    if jid and jid in sweep_by_class:
        skey = jid
    elif norm(jname) in sweep_norm:
        skey = sweep_norm[norm(jname)]
    else:
        # try substring match
        for sk in sweep_by_class:
            if norm(jname) and norm(jname) in norm(sk) or norm(sk) in norm(jname or ''):
                skey = sk
                break
    pairs.append((jc, skey))

unmatched = [jc['name'] for jc,sk in pairs if sk is None]
print('unmatched:', unmatched)
for jc, sk in pairs:
    sc = sweep_by_class.get(sk)
    if sc is None: continue
    if jc['n'] != sc.get('N') or jc['rca'] != sc.get('rca'):
        print('CONFLICT', jc['id'], jc['name'][:50], 'judge n/rca=', jc['n'], jc['rca'], 'sweep N/rca=', sc.get('N'), sc.get('rca'), sc.get('_source_file'))
