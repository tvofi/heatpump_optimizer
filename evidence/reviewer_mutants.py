"""Reviewer's own targeted mutants (round 4 of #2697): each narrows one use of a
shared part, which the fixer's table (R1-R26) mutates only as a whole."""
import pathlib, subprocess
p = pathlib.Path('tools/policy/agreement.mjs'); orig = p.read_text()
M = {
 'RV1 first gap (program->pr) narrowed to \\s+ (brief item 1)': ('${PROGRAM}${OPTIONS}${GAP}${word(\'pr\')}', '${PROGRAM}${OPTIONS}\\\\s+${word(\'pr\')}'),
 'RV2 second gap (pr->merge) narrowed to \\s+': ('${word(\'pr\')}${OPTIONS}${GAP}${word(\'merge\')}', '${word(\'pr\')}${OPTIONS}\\\\s+${word(\'merge\')}'),
 'RV3 quoted arm gap narrowed to ", "': ('`|${QUOTE}pr${QUOTE}${OPTIONS}${GAP}${QUOTE}merge${QUOTE}`', '`|${QUOTE}pr${QUOTE}${OPTIONS}, ${QUOTE}merge${QUOTE}`'),
 'RV4 OPTIONS before pr dropped': ('${PROGRAM}${OPTIONS}${GAP}', '${PROGRAM}${GAP}'),
 'RV5 OPTIONS between pr and merge dropped': ('${word(\'pr\')}${OPTIONS}${GAP}', '${word(\'pr\')}${GAP}'),
}
try:
    for k, (a, b) in M.items():
        if orig.count(a) != 1: print(k, 'NOT APPLIED', orig.count(a)); continue
        p.write_text(orig.replace(a, b))
        r = subprocess.run(['node', 'tools/policy/agreement.mjs', '--self-test'], capture_output=True, text=True)
        out = r.stdout + r.stderr
        fails = [l.strip() for l in out.splitlines() if l.strip().startswith('FAIL')]
        last = [l for l in out.splitlines() if 'SELF-TEST' in l]
        print(k, '|', last[-1] if last else 'no summary rc=%d' % r.returncode, '|', '; '.join(fails))
finally:
    p.write_text(orig)
