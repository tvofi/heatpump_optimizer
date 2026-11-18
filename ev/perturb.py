"""Apply the p2 data half to a tree: argv[1]."""
import json, sys, pathlib
T = pathlib.Path(sys.argv[1])
(T/'dev/governance/dimensions/DX0.md').write_text('# DX0 - scratch fixture\n\nRead `COMMON.md` first.\n\n## Owner-only\n\n1. Step one.\n2. Step two.\n3. Step three.\n4. Step four.\n5. Step five.\n')
f = T/'.claude/workflows/audit-find.js'; s = f.read_text(); s = s.replace("'D17']", "'D17', 'DX0']", 1); f.write_text(s)
f = T/'.claude/workflows/audit-verify.js'; s = f.read_text(); s = s.replace("const OWNER_ONLY = new Set([])", "const OWNER_ONLY = new Set(['DX0'])", 1); f.write_text(s)
f = T/'dev/audit/config/scopes.json'; d = json.loads(f.read_text())
d['DX0'] = {'mode': 'cells', 'universe': [], 'steps': [f'M{i}' for i in range(1, 6)], 'owner_only': True,
            'seats': {f's{i}': [{'files': ['**'], 'steps': [f'M{i}']}] for i in range(1, 6)}}
f.write_text(json.dumps(d, indent=2) + '\n')
f = T/'dev/audit/config/finding.schema.json'; s = f.read_text(); s = s.replace('D(1[0-7]|[0-9])', 'D(1[0-7]|[0-9]|X0)'); f.write_text(s)
f = T/'dev/audit/config/rotation.json'; d = json.loads(f.read_text())
d['DX0'] = {'steps': [f'M{i}' for i in range(1, 6)], 'rounds': {}}
f.write_text(json.dumps(d, indent=2) + '\n')
f = T/'.claude/workflows/audit-find.js'; s = f.read_text(); f.write_text(s.replace('D(1[0-7]|[0-9])', 'D(1[0-7]|[0-9]|X0)'))
