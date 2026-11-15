#!/usr/bin/env python3
"""NOT APPLIED. Rewrite bare citations of doomed refs to their archive tags, in place, token for token.

    python3 retarget.py --dry-output DRY.txt FILE [FILE ...]      # print counts, write nothing
    python3 retarget.py --dry-output DRY.txt --write FILE [FILE ...]

DRY.txt is the output of `closeout.py ... --verbose-less dry plan` (lines `  - <ref> is cited bare by <path>; retarget it to archive/<ref>`):
the doomed set is exactly what closeout itself names, so the rewrite and the refusal cannot disagree. Uses closeout's own CITED_RE
(its lookbehind `(?<![\\w./-])` is why `archive/handoff/x` is no longer read as the bare `handoff/x`), only rewrites tokens in the
doomed set, never touches a token already under archive/, and for a .json file proves the result parses and (for a roster) that
roster_edit.dump(json.loads(out)) reproduces the bytes (the file's own formatting). Idempotent: a second run changes nothing.
"""
import argparse, json, re, sys
sys.path.insert(0, 'tools/audit/seat')
import closeout
ap = argparse.ArgumentParser()
ap.add_argument('--dry-output', required=True)
ap.add_argument('--write', action='store_true')
ap.add_argument('files', nargs='+')
a = ap.parse_args()
doomed = set(re.findall(r'^\s+- (\S+) is cited bare by ', open(a.dry_output).read(), re.M))
print(f'{len(doomed)} doomed refs named by closeout')
rc = 0
for f in a.files:
    s = open(f, encoding='utf-8').read()
    n = 0
    def sub(m):
        global n
        if m.group(1) in doomed:
            n += 1
            return 'archive/' + m.group(1)
        return m.group(0)
    out = closeout.CITED_RE.sub(sub, s)
    ok = ''
    if f.endswith('.json'):
        try:
            json.loads(out)
            ok = 'json parses'
            if 'rosters/wave-r' in f:
                import roster_edit
                ok += '; dump round-trip ' + ('identical' if roster_edit.dump(json.loads(out)) == out else 'DIFFERS')
                if 'DIFFERS' in ok: rc = 1
        except ValueError as e:
            ok = f'INVALID JSON: {e}'; rc = 1
    print(f'{f}: {n} token(s) rewritten; {ok}')
    if a.write and out != s:
        open(f, 'w', encoding='utf-8').write(out)
sys.exit(rc)
