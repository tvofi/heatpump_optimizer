"""Mark geometry on a 48-unit lattice (2-unit steps). Three concepts; light and dark colourways."""
PAL = {
    'light': dict(line='#026aa8', heat='#d2601f', ink='#0f2233'),
    'dark': dict(line='#4fb3f0', heat='#d2601f', ink='#f3f8fc'),
}
SW = 3.6  # stroke width in lattice units

def valley(mode, tile=False):
    c = dict(PAL[mode])
    if tile:
        c = dict(line='#f3f8fc', heat='#f08a3c', ink='#f3f8fc')
    # the price profile: a stair down into the cheap hours and back up (every vertex on the 2u lattice)
    line = 'M7 14 H15 V23 H21 V34 H33 V18 H41'
    # the pool: heat settled to one calm level, taking the shape of the stairs it fills (drawn under the line)
    pool = 'M15 20.5 V23 H21 V34 H33 V20.5 Z'
    bg = ''
    if tile:
        bg = f'<rect x="0" y="0" width="48" height="48" rx="11" fill="{"#026aa8" if mode == "light" else "#0f2233"}"/>'
    return (bg + f'<path d="{pool}" fill="{c["heat"]}"/>'
            f'<path d="{line}" fill="none" stroke="{c["line"]}" stroke-width="{SW}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')

def _old_valley(mode):
    c = PAL[mode]
    # price profile: high, stepping down into a valley, back up
    line = 'M5 13 H14 V21 H20 V35 H31 V25 H37 V15 H43'
    # the warm pool: fills the lowest step up to a gently waved surface, 1.2u clear of the stroke
    g = SW / 2 + 1.2
    x0, x1, yb, lvl = 20 + g, 31 - g, 35 - g, 27.0
    mid = (x0 + x1) / 2
    pool = (f'M{x0:.2f} {yb:.2f} V{lvl+0.6:.2f} '
            f'Q{(x0+mid)/2:.2f} {lvl-1.4:.2f} {mid:.2f} {lvl:.2f} '
            f'T{x1:.2f} {lvl-0.6:.2f} V{yb:.2f} Z')
    return (f'<path d="{pool}" fill="{c["heat"]}"/>'
            f'<path d="{line}" fill="none" stroke="{c["line"]}" stroke-width="{SW}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')

def house(mode):
    c = PAL[mode]
    roof = 'M7 22 L24 8 L41 22'
    walls = 'M11 19 V40 M37 19 V40'
    floor = 'M11 40 H17 V33 H31 V40 H37'  # the floor is a schedule: a cheap block lifted
    heat = f'<rect x="19.6" y="35.4" width="8.8" height="4.6" rx="1.2" fill="{c["heat"]}"/>'
    s = f'fill="none" stroke="{c["line"]}" stroke-width="{SW}" stroke-linecap="round" stroke-linejoin="round"'
    return f'<path d="{roof} {walls} {floor}" {s}/>' + heat.replace('y="35.4"', 'y="23.6"').replace('height="4.6"', 'height="6.4"')

def bars(mode):
    c = PAL[mode]
    # a 6-slot plan: bar heights are price; the two cheapest slots carry heat
    xs = [6, 13, 20, 27, 34, 41]
    hs = [22, 16, 8, 6, 14, 24]
    out = []
    for x, hgt in zip(xs, hs):
        cheap = hgt <= 8
        out.append(f'<rect x="{x-2.6:.1f}" y="{42-hgt}" width="5.2" height="{hgt}" rx="1.6" '
                   f'fill="{c["heat"] if cheap else c["line"]}"/>')
    return ''.join(out)

CONCEPTS = {'valley': valley, 'valley_tile': lambda m: valley(m, True), 'house': house, 'bars': bars}

def svg(concept, mode, size=None):
    sz = f' width="{size}" height="{size}"' if size else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"{sz}>{CONCEPTS[concept](mode)}</svg>'
