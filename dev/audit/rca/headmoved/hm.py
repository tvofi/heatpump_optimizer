"""R10-RCA-HEADMOVED: every re-verification after a `merge` verdict, and what moved the head.

Usage: python3 hm.py <since ISO> [--carry]  (run in a checkout with the verdict/*,
review/* bus refs and refs/remotes/pr/* fetched). Reads each bus ref's VERDICT.md
history; a PR's verdicts are ordered by commit time; an entry is a verdict whose
predecessor was `merge` at a different head (policy_lint's rework arm). For the
delta prev..cur it lists the first-parent commits and classifies each:
  main   a merge whose second parent is on origin/main
  bot    authored by a bot account
  row    a branch commit touching only dev/programme/delivery/<N>.md
  own    any other branch commit
With --carry it also runs tools/pr/app_approve.sh --carry prev cur origin/main.
Prints one TSV line per entry, then totals.
"""
import subprocess, sys, re, collections
def g(*a, ok=False):
    r = subprocess.run(['git', *a], capture_output=True, text=True)
    if r.returncode and not ok: return None
    return r.stdout
since = sys.argv[1]; carry = '--carry' in sys.argv
rx = re.compile(r'^Fix review:\s+(merge|blocked)\s+([0-9a-f]{40})')
refs = g('for-each-ref', '--format=%(refname)', 'refs/remotes/origin/verdict/', 'refs/remotes/origin/review/').split()
seen = {}; per = collections.defaultdict(list)
for ref in refs:
    m = re.match(r'(\d+)', ref.split('/', 4)[-1])
    if not m: continue
    pr = m.group(1)
    for line in (g('log', '--format=%H %cI', ref, '--', 'VERDICT.md') or '').splitlines():
        c, t = line.split()
        first = (g('show', f'{c}:VERDICT.md', ok=True) or '').split('\n', 1)[0].strip()
        v = rx.match(first)
        if not v: continue
        key = (pr, v.group(1), v.group(2), first)
        if key in seen: continue
        seen[key] = 1; per[pr].append((t, v.group(1), v.group(2), c))
tot = collections.Counter(); out = []
for pr, vs in per.items():
    vs.sort()
    for (t0, k0, h0, _), (t1, k1, h1, c1) in zip(vs, vs[1:]):
        if k0 != 'merge' or h0 == h1 or t1 < since: continue
        cls = collections.Counter(); bad = ''
        log = g('log', '--first-parent', '--format=%H%x09%P%x09%an%x09%s', f'{h0}..{h1}')
        if log is None: bad = 'missing'
        for l in (log or '').splitlines():
            h, parents, an, s = l.split('\t', 3); ps = parents.split()
            if len(ps) > 1 and subprocess.run(['git', 'merge-base', '--is-ancestor', ps[1], 'origin/main']).returncode == 0:
                cls['main'] += 1
            elif 'bot' in an.lower() or an == 'github-actions':
                cls['bot'] += 1
            else:
                files = (g('diff-tree', '--no-commit-id', '--name-only', '-r', h) or '').split()
                cls['row' if files and all(f == f'dev/programme/delivery/{pr}.md' for f in files) else 'own'] += 1
        kind = bad or ('own' if cls['own'] else 'row' if cls['row'] else 'bot' if cls['bot'] else 'main' if cls['main'] else 'empty')
        cr = ''
        if carry and not bad:
            r = subprocess.run(['bash', 'tools/pr/app_approve.sh', '--carry', h0, h1, 'origin/main'], capture_output=True, text=True)
            cr = 'yes' if 'CARRY: yes' in r.stdout else (r.stdout + r.stderr).strip().splitlines()[-1][:90] if (r.stdout + r.stderr).strip() else f'rc={r.returncode}'
        tot[kind] += 1
        out.append(f'#{pr}\t{t1}\t{h0[:8]}->{h1[:8]}\t{k1}\t{kind}\t{dict(cls)}\t{cr}')
for l in sorted(out, key=lambda s: s.split('\t')[1]): print(l)
print('TOTAL', sum(tot.values()), dict(tot))
