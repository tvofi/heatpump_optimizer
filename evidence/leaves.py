"""Reviewer's probe: capture HEAD's scenarios, diff leaves against the cached merge-base capture, classify leaf names."""
import json, os, sys, tempfile, subprocess, re, collections
wt = sys.argv[1]; cache = sys.argv[2]
sys.path.insert(0, os.path.join(wt, 'tests'))
import env_drift
d = tempfile.mkdtemp(); out = os.path.join(d, 'cap.json')
subprocess.run([sys.executable, os.path.join(wt, 'tests/env_drift.py'), '--capture', wt, out, '--all'], check=True, env={**os.environ, 'PYTHONPATH': os.path.join(wt, 'tests/hastub')})
head = json.load(open(out)); base = json.loads(json.load(open(cache))['capture_json'])
leafkinds = collections.Counter(); scen = 0
for name in sorted(set(head) | set(base)):
    diffs = []
    env_drift._diff_leaves(base.get(name), head.get(name), name, diffs)
    if diffs: scen += 1
    for l in diffs:
        m = re.search(r'(space_reasons|dhw_reasons)', l)
        leafkinds['reasons' if m else 'OTHER'] += 1
        if not m: print('OTHER', l[:200])
print(f"RESULT leaves scenarios_moved={scen} reasons_leaves={leafkinds['reasons']} other_leaves={leafkinds['OTHER']}")
