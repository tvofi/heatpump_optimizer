#!/usr/bin/env python3
"""Plan rev 3.1 section 4.6: every open issue and the open group that closes it.

    python3 gen_coverage_rev31.py ROSTER.json OPEN_ISSUES.json > coverage.md

OPEN_ISSUES.json: [[number, title], ...] as listed on GitHub (tracking issue #201 excluded).
"""
import json, sys

R = json.load(open(sys.argv[1]))
issues = json.load(open(sys.argv[2]))
openg = [g for g in R['groups'] if g['resume'].get('stage') not in ('done', 'rca-done')]
rows, miss = [], []
for n, title in issues:
    closers = [g['group'].replace('R9-', '') for g in openg if n in (g.get('fixes') or [])]
    parts = [g['group'].replace('R9-', '') for g in openg if n in (g.get('issues') or []) and n not in (g.get('fixes') or [])]
    if not closers and not parts:
        miss.append(n)
    t = title.replace('|', '/')
    rows.append(f'| #{n} | {t[:90]} | {", ".join(closers) or "—"} | {", ".join(parts) or "—"} |')
print('| issue | title | closed by | also part of |\n|---|---|---|---|')
print('\n'.join(rows))
print(f'{len(issues)} open issues; uncovered: {miss}', file=sys.stderr)
