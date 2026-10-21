"""Build the shadow roster: live round-10 roster + FLOW groups + folded carries."""
import json, subprocess, sys, copy
sys.path.insert(0, '.')
from flow_groups import GROUPS, CARRIES
REF = sys.argv[1] if len(sys.argv) > 1 else 'origin/handoff/audit-r10-roster'
REPO = __import__('os').environ.get('HPO_REPO', '.')  # a clone that has fetched the roster ref
raw = subprocess.run(['git', '-C', REPO, 'show', f'{REF}:dev/programme/rosters/wave-r10-groups.json'],
                     capture_output=True, text=True, check=True).stdout
d = json.loads(raw)
sha = subprocess.run(['git', '-C', REPO, 'rev-parse', REF], capture_output=True, text=True).stdout.strip()
names = {g['group'] for g in d['groups']}
for g in GROUPS:
    assert g['group'] not in names, g['group']
    for a in g['after']:
        assert a in names or a in {x['group'] for x in GROUPS}, (g['group'], a)
by = {g['group']: g for g in d['groups']}
for name, text in CARRIES:
    by[name].setdefault('carry', []).append(text)
d['groups'].extend(copy.deepcopy(GROUPS))
c = d.get('_comment')
note = (f"SHADOW: built from {REF} at {sha[:12]} plus {len(GROUPS)} FLOW groups and "
        f"{len(CARRIES)} folded carries (Lean flow study 2026-10-21). Not the live roster.")
d['_comment'] = ([note] + c) if isinstance(c, list) else [note, c]
json.dump(d, open('shadow-r10-groups.json', 'w'), indent=1, ensure_ascii=False)
open('shadow-r10-groups.json', 'a').write('\n')
print('groups', len(d['groups']), 'base', sha[:12])
