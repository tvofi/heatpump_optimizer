"""Palette of record for chart concept A: per-panel validation with the repo's gates (color.py, ported from
tests/card.mjs) and the dataviz skill's validator (OKLab, protan/deutan/tritan, all pairs). Writes PALETTE-CHECKS.txt."""
import itertools, subprocess, sys
from color import contrast, deut_dE
V = sys.argv[1]
PANELS = {
 'price':  {'price': ('#4a3aa7', '#9085e9'), 'solar': ('#d4561f', '#d95926')},
 'power':  {'space': ('#2a78d6', '#3987e5'), 'dhw': ('#d2403f', '#e66767'), 'actioned': ('#008a70', '#22a383')},
 'temps':  {'tank': ('#c2477a', '#d55181'), 'house': ('#008300', '#1f9d1f'), 'outdoor': ('#3b7dd8', '#4b95e8')},
}
TODAY = {'price': '#a86b00', 'dhw_slots': '#e0544e', 'space_slots': '#4a90e2', 'actioned': '#00838f',
         'outdoor': '#7d8794', 'dhw_temp': '#c264d0', 'house_temp': '#1a7a52', 'solar': '#ed6900'}
out = []
def val(cols, mode, surface):
    r = subprocess.run(['node', V, ','.join(cols), '--mode', mode, '--surface', surface, '--pairs', 'all'], capture_output=True, text=True)
    return [l.rstrip() for l in r.stdout.splitlines() if l.strip().startswith(('[', '→'))]
out.append('# today (SERIES_DEFS, one plot), light, all pairs')
out += val(list(TODAY.values()), 'light', '#ffffff')
ok = True
for panel, ser in PANELS.items():
    for mi, (mode, bg) in enumerate((('light', '#ffffff'), ('dark', '#1c1c1c'))):
        cols = {k: v[mi] for k, v in ser.items()}
        out.append(f'\n# panel {panel}, {mode} (surface {bg})')
        for k, c in cols.items():
            cr = contrast(c, bg); out.append(f'  repo gate  {k:9} {c}  contrast {cr:.2f} (>= 3)'); ok &= cr >= 3
        for (a, ca), (b, cb) in itertools.combinations(cols.items(), 2):
            d = deut_dE(ca, cb); out.append(f'  repo gate  {a}/{b} deuteranope dE {d:.1f} (>= 10; dash if < 20)'); ok &= d >= 10
        v = val(list(cols.values()), mode, bg); out += ['  ' + l for l in v]; ok &= any('ALL CHECKS PASS' in l for l in v)
out.append(f'\nRESULT: {"every panel passes both" if ok else "FAIL"}')
open('PALETTE-CHECKS.txt', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out[-12:])); sys.exit(0 if ok else 1)
