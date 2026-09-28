#!/usr/bin/env python3
"""Re-derive classes_v2.json counts from register_rows.tsv and reconcile against
main's register v1 (tools/audit/bugclasses.json).

  python3 derive.py            check classes_v2.json counts, print reconciliation (rc 1 on a count mismatch)
  python3 derive.py --write    rewrite the count fields of classes_v2.json, then print the same

v1 is read with `git -C $REPO show $V1REF:tools/audit/bugclasses.json`
(REPO default /home/user/heatpump_optimizer, V1REF default 3490cb16), falling back
to src/bugclasses_main.json beside this file.

Counting rule (defect-root-cause.md:88-89): judged survivors plus counted
instances beyond them (kind=sweep). A row's note may start `FLAG-><class>`:
a proposed move not applied; the "flags applied" column shows its effect.
"""
import csv, json, os, re, subprocess, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROUNDS = [f'R{i}' for i in range(1, 10)]


def load_v1():
    repo = os.environ.get('REPO', '/home/user/heatpump_optimizer')
    ref = os.environ.get('V1REF', '3490cb16')
    try:
        txt = subprocess.run(['git', '-C', repo, 'show', f'{ref}:tools/audit/bugclasses.json'],
                             capture_output=True, text=True, check=True).stdout
        return json.loads(txt), f'{ref}:tools/audit/bugclasses.json'
    except Exception:
        p = os.path.join(HERE, 'src', 'bugclasses_main.json')
        return json.load(open(p)), p


def v1_members(entry):
    """-> (set of 'Rn id', list of non-round instances)."""
    ids, other = set(), []
    for i in entry['instances']:
        m = re.match(r'^(R\d) (\S+)$', i)
        if m:
            ids.add(i)
        elif re.match(r'^D\d+-s\d+-\d+$', i):  # P11 carries round-9 ids without a prefix
            ids.add('R9 ' + i)
        else:
            other.append(i)
    return ids, other


rows = list(csv.DictReader(open(os.path.join(HERE, 'register_rows.tsv')), delimiter='\t'))
classes = json.load(open(os.path.join(HERE, 'classes_v2.json')))
v1, v1src = load_v1()

# ---- derive
inst = defaultdict(lambda: defaultdict(list))
split = defaultdict(lambda: defaultdict(lambda: [0, 0]))  # class -> round -> [judged, sweep]
strict = defaultdict(lambda: defaultdict(int))  # sweep rows found by a sweep seat only
flagged = defaultdict(lambda: defaultdict(int))  # counts with FLAG moves applied
bad = []
for r in rows:
    c, rnd, fid = r['class_id'], r['round'], r['finding_id']
    if c not in classes:
        bad.append(f'row {rnd} {fid}: class {c} not in classes_v2.json')
        continue
    inst[c][rnd].append(fid)
    split[c][rnd][0 if r['kind'] == 'judged' else 1] += 1
    fb = re.match(r'found_by=(\S+?);', r['note'])
    if r['kind'] == 'judged' or (fb and fb.group(1).startswith('S')):
        strict[c][rnd] += 1
    m = re.match(r'FLAG->(\S+)', r['note'])
    tgt = m.group(1) if m else c
    flagged[tgt][rnd] += 1

derived = {}
for c in classes:
    if c.startswith('_'):
        continue
    per = {rnd: sorted(inst[c][rnd]) for rnd in ROUNDS if inst[c][rnd]}
    derived[c] = {'instances': per, 'total': sum(len(v) for v in per.values()),
                  'max_per_round': max((len(v) for v in per.values()), default=0),
                  'rounds': [int(k[1:]) for k in per],
                  'per_round_judged_sweep': {k: split[c][k] for k in per}}

write = '--write' in sys.argv
mismatch = []
for c, d in derived.items():
    for k, v in d.items():
        if classes[c].get(k) != v:
            mismatch.append(f'{c}.{k}')
            if write:
                classes[c][k] = v
if write:
    with open(os.path.join(HERE, 'classes_v2.json'), 'w') as fh:
        json.dump(classes, fh, indent=2, ensure_ascii=False)
        fh.write('\n')
    print(f'wrote counts for {len(derived)} classes ({len(mismatch)} fields changed)')
elif mismatch:
    print('COUNT MISMATCH (run with --write):', ', '.join(mismatch))

for b in bad:
    print('ERROR', b)

# ---- per round
print('\n== rows per round (judged + sweep)')
per_round = defaultdict(lambda: [0, 0])
for r in rows:
    per_round[r['round']][0 if r['kind'] == 'judged' else 1] += 1
for rnd in ROUNDS:
    j, s = per_round[rnd]
    print(f'{rnd}: {j + s:4d}  (judged {j}, sweep/counted-beyond {s})')
print(f'all: {len(rows)}')

# ---- reconciliation vs v1
print(f'\n== reconciliation vs v1 ({v1src})')
print(f"{'class':20s} {'v1':>4s} {'v1R1-7':>6s} {'v2R1-7':>6s} {'d':>3s} {'v1R8':>4s} {'v2R8':>4s} {'v1R9':>4s} {'v2R9':>4s} {'v2tot':>5s} {'flagsR1-7':>9s}  explanation")
rows17 = {(r['round'], r['finding_id']): r for r in rows if r['round'] in ROUNDS[:7]}
all_ok = True
for c in sorted(set(derived) | {k for k in v1 if not k.startswith('_')}, key=lambda x: (x not in v1, x)):
    e = v1.get(c)
    ids1, other = v1_members(e) if e else (set(), [])
    v1_17 = {i for i in ids1 if i[:2] in ROUNDS[:7]}
    v1_8 = {i for i in ids1 if i.startswith('R8')}
    v1_9 = {i for i in ids1 if i.startswith('R9')}
    d = derived.get(c, {'instances': {}, 'total': 0})
    v2_17 = {f'{k} {i}' for k, l in d['instances'].items() if k in ROUNDS[:7] for i in l}
    v2_8 = {f'R8 {i}' for i in d['instances'].get('R8', [])}
    v2_9 = {f'R9 {i}' for i in d['instances'].get('R9', [])}
    fl17 = sum(flagged[c][k] for k in ROUNDS[:7])
    expl = []
    if v1_17 != v2_17:
        all_ok = False
        expl.append(f'R1-7 only in v1: {sorted(v1_17 - v2_17)}; only in v2: {sorted(v2_17 - v1_17)}')
    else:
        expl.append('R1-7 identical')
    if v1_9 - v2_9:
        expl.append(f'v1 R9 not in v2 {c}: {sorted(v1_9 - v2_9)}')
    if v2_9 - v1_9 and v1_9:
        expl.append(f'v2 R9 added: {len(v2_9 - v1_9)}')
    if other:
        expl.append(f'{len(other)} non-round v1 instance(s) kept aside (non_round_instances)')
    if fl17 != len(v2_17):
        expl.append(f'flags move R1-7 {len(v2_17)}->{fl17} (reclassifications.md)')
    print(f"{c:20s} {len(ids1) + len(other) if e else '-':>4} {len(v1_17) if e else '-':>6} {len(v2_17):6d} {len(v2_17) - len(v1_17):3d} "
          f"{len(v1_8):4d} {len(v2_8):4d} {len(v1_9):4d} {len(v2_9):4d} {d['total']:5d} {fl17:9d}  " + '; '.join(expl))
print('R1-7 membership identical to v1 for every class' if all_ok else 'R1-7 membership differs from v1 (see rows above)')

# ---- flags targeting ids with no v2 class yet
tgts = {t for t in flagged if t not in classes}
if tgts:
    print('flag targets that are not classes:', sorted(tgts), '(no class fits; see reclassifications.md)')

# ---- threshold views
print('\n== total >= 3 but max_per_round < 3 (never tripped the per-round RCA trigger)')
for c, d in sorted(derived.items(), key=lambda x: -x[1]['total']):
    if d['total'] >= 3 and d['max_per_round'] < 3:
        print(f"{c}: total {d['total']}, max/round {d['max_per_round']}, rounds {d['rounds']}")
print('\n== same view with every FLAG move applied (R1-9 flags; "none" = no class fits)')
for c in sorted(flagged, key=lambda x: -sum(flagged[x].values())):
    per = {k: v for k, v in flagged[c].items() if v}
    tot, mx = sum(per.values()), max(per.values(), default=0)
    if tot >= 3 and mx < 3:
        print(f"{c}: total {tot}, max/round {mx}, rounds {sorted(int(k[1:]) for k in per)}")
print('\n== per-round N >= 3 (judged + counted beyond); strict = judged + sweep-seat-found only')
for c, d in sorted(derived.items()):
    hits = [f"{k}={len(v)}(strict {strict[c][k]})" for k, v in d['instances'].items() if len(v) >= 3]
    if hits:
        print(f"{c}: {', '.join(hits)}")
print('\n== v1 entry lacks R8 / R9 members that v2 has')
for c, d in sorted(derived.items()):
    e = v1.get(c)
    ids1 = v1_members(e)[0] if e else set()
    miss = [k for k in ('R8', 'R9') if d['instances'].get(k) and not any(i.startswith(k) for i in ids1)]
    if miss:
        parts = ', '.join('%s (%d)' % (k, len(d['instances'][k])) for k in miss)
        print(f"{c}: {'new id' if not e else 'v1 has none for'} {parts}")
sys.exit(1 if (mismatch and not write) or bad else 0)
