"""README graphics: banner, "how it works" figure (light and dark) and the social preview.

Every glyph is outlined (fontTools), so the SVGs are byte-stable and need no font at view time.
Needs: Python with fontTools; Node with Playwright and Chromium for the PNGs.

    HPO_FONTS=/path/to/fonts python3 make_readme_figures.py            # SVG + PNG beside this file
    HPO_FONTS=/path/to/fonts python3 make_readme_figures.py --live     # SVGs with live text, to inspect

HPO_FONTS holds Outfit-Bold/Regular.ttf, InstrumentSans-Bold/Regular.ttf and JetBrainsMono-Regular.ttf (all SIL OFL).
The social preview (social-preview.svg/.png) is written to $HPO_SOCIAL_OUT (default: a temp dir); it is uploaded by the
owner under the repository settings and is not tracked.
"""
import os, subprocess, sys, tempfile
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.environ.get('HPO_FONTS', '')
OUT = HERE
SOCIAL_OUT = os.environ.get('HPO_SOCIAL_OUT') or tempfile.mkdtemp(prefix='hpo-social-')
SW = 3.6
LINE = 'M6 12 H13 V19 H20 V26 H27 V35 H36 V13 H42'
POOL = 'M20 22 V26 H27 V35 H36 V22 Z'
_MARK = dict(line='#4fb3f0', heat='#d2601f')


def mark(mode, tx=0, ty=0, s=1.0):
    """The dusk mark (dark-background colours; only 'dark' is used here)."""
    c = _MARK
    return (f'<g transform="translate({tx} {ty}) scale({s})"><path d="{POOL}" fill="{c["heat"]}"/>'
            f'<path d="{LINE}" fill="none" stroke="{c["line"]}" stroke-width="{SW}" stroke-linecap="round" '
            f'stroke-linejoin="round"/></g>')


_FONT_CACHE = {}


def text_path(text, font, size, x, y, tracking=0.0):
    if font not in _FONT_CACHE:
        _FONT_CACHE[font] = TTFont(os.path.join(FONTS, font))
    f = _FONT_CACHE[font]; gs = f.getGlyphSet(); cmap = f.getBestCmap()
    upm = f['head'].unitsPerEm; k = size / upm; hmtx = f['hmtx']
    d = []; cx = x
    for ch in text:
        g = cmap.get(ord(ch))
        if g is None: continue
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (k, 0, 0, -k, cx, y)))
        d.append(pen.getCommands())
        cx += hmtx[g][0] * k + tracking * size
    return ' '.join(d), cx - x

INK, FROST, FJORD, GLACIER, EMBER, SLATE, MIST = '#0f2233', '#f3f8fc', '#026aa8', '#4fb3f0', '#d2601f', '#5b6b7a', '#9fb3c4'

import math
LIVE = False
FAM = {'Outfit-Bold.ttf': ('Outfit', 700), 'Outfit-Regular.ttf': ('Outfit', 400), 'InstrumentSans-Regular.ttf': ('Inter', 400),
       'InstrumentSans-Bold.ttf': ('Inter', 700), 'JetBrainsMono-Regular.ttf': ('Roboto Mono', 400)}

def T(text, x, y, size, fill, font='InstrumentSans-Regular.ttf', anchor='start', tracking=0.0):
    if LIVE:
        fam, wt = FAM[font]
        return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-weight="{wt}" font-size="{size}" fill="{fill}" '
                f'text-anchor="{anchor}">{text.replace("&", "&amp;")}</text>')
    _, w = text_path(text, font, size, 0, 0, tracking)
    x0 = x - w if anchor == 'end' else x - w / 2 if anchor == 'middle' else x
    d, _ = text_path(text, font, size, x0, y, tracking)
    return f'<path d="{d}" fill="{fill}"/>'

def step_field(x, y, w, h, n, seed_prices, cheap_q=0.25, col=GLACIER, heat=EMBER, sw=2.2, fill_op=0.9):
    """A day of prices as a step profile; the cheapest slots carry heat bars (the plan)."""
    ps = seed_prices; lo, hi = min(ps), max(ps); cw = w / n
    thr = sorted(ps)[int(len(ps) * cheap_q)]
    bars, d = [], []
    for i, p in enumerate(ps):
        yy = y + h - (p - lo) / (hi - lo) * h * 0.78 - h * 0.1
        xa, xb = x + i * cw, x + (i + 1) * cw
        d.append(f'{"M" if i == 0 else "V"}{yy:.1f} ' if i else f'M{xa:.1f} {yy:.1f} ')
        d.append(f'H{xb:.1f} ')
        if p <= thr:
            bh = min(h * 0.26, y + h - yy - 7)
            bars.append(f'<rect x="{xa + cw*0.18:.1f}" y="{y + h - bh:.1f}" width="{cw*0.64:.1f}" height="{bh:.1f}" rx="2.5" fill="{heat}" fill-opacity="{fill_op}"/>')
    path = ''.join(d)
    return ''.join(bars) + f'<path d="{path}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"/>'

PRICES = [0.62,0.58,0.55,0.53,0.52,0.56,0.71,0.95,1.18,1.12,0.98,0.86,0.80,0.78,0.83,0.97,1.21,1.34,1.29,1.10,0.92,0.81,0.74,0.69]

def banner(w=1280, h=320):
    b = [f'<rect width="{w}" height="{h}" rx="18" fill="{INK}"/>']
    # the measured field: faint lattice + one day of prices, cheap hours carrying heat
    for gx in range(640, w - 40, 30):
        b.append(f'<line x1="{gx}" y1="56" x2="{gx}" y2="{h-56}" stroke="{MIST}" stroke-opacity=".08"/>')
    b.append(step_field(640, 60, w - 700, h - 120, 24, PRICES))
    b.append(T('00', 640, h - 34, 13, MIST, 'JetBrainsMono-Regular.ttf'))
    b.append(T('12', 640 + (w - 700) / 2, h - 34, 13, MIST, 'JetBrainsMono-Regular.ttf', 'middle'))
    b.append(T('24 h', w - 60, h - 34, 13, MIST, 'JetBrainsMono-Regular.ttf', 'end'))
    # lockup
    b.append(f'<g transform="translate(64 86)">{mark("dark", 0, 0, 1.9)}</g>')
    b.append(T('Heat Pump', 170, 136, 46, FROST, 'Outfit-Bold.ttf'))
    b.append(T('Cost Optimizer', 172, 180, 34, MIST, 'Outfit-Regular.ttf', tracking=0.01))
    b.append(T('Model-predictive heating control for Home Assistant', 68, 244, 17, FROST, 'InstrumentSans-Regular.ttf'))
    b.append(T('Heating and hot water planned 24 h ahead against prices', 68, 270, 15, MIST))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{"".join(b)}</svg>'

def social(w=1280, h=640):
    b = [f'<rect width="{w}" height="{h}" fill="{INK}"/>']
    for gy in range(120, h - 60, 32):
        b.append(f'<line x1="80" y1="{gy}" x2="{w-80}" y2="{gy}" stroke="{MIST}" stroke-opacity=".06"/>')
    b.append(step_field(80, 330, w - 160, 230, 24, PRICES, sw=3))
    b.append(f'<g transform="translate(80 92)">{mark("dark", 0, 0, 2.6)}</g>')
    b.append(T('Heat Pump Cost Optimizer', 222, 170, 58, FROST, 'Outfit-Bold.ttf'))
    b.append(T('Heating and hot water planned 24 hours ahead against electricity prices', 224, 222, 24, MIST))
    b.append(T('for Home Assistant', 224, 258, 24, MIST))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{"".join(b)}</svg>'

def box(x, y, w, h, title, sub, fg, bg, stroke, hi=False):
    s = EMBER if hi else stroke
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{bg}" stroke="{s}" stroke-width="{2 if hi else 1.2}"/>',
           T(title, x + w / 2, y + 30, 16, fg, 'InstrumentSans-Bold.ttf', 'middle')]
    for i, line in enumerate(sub):
        out.append(T(line, x + w / 2, y + 54 + i * 19, 13, MIST if bg in (INK, '#16304a') else SLATE, anchor='middle'))
    return ''.join(out)

def arrow(x1, y1, x2, y2, label, col, lx=None, ly=None, dash=False, anchor='middle', tcol=None):
    da = ' stroke-dasharray="6 5"' if dash else ''
    lx = (x1 + x2) / 2 if lx is None else lx; ly = (y1 + y2) / 2 - 8 if ly is None else ly
    ang = math.atan2(y2 - y1, x2 - x1); a1, a2 = ang + 2.7, ang - 2.7
    head = f'<polygon points="{x2},{y2} {x2 + 9*math.cos(a1):.1f},{y2 + 9*math.sin(a1):.1f} {x2 + 9*math.cos(a2):.1f},{y2 + 9*math.sin(a2):.1f}" fill="{col}"/>'
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2 - 7*math.cos(ang):.1f}" y2="{y2 - 7*math.sin(ang):.1f}" stroke="{col}" stroke-width="1.6"{da}/>' + head +
            (T(label, lx, ly, 12, tcol or col, anchor=anchor) if label else ''))

def figure(w=1200, h=440, dark=False):
    bg, card, fg, st, ac = (INK, '#16304a', FROST, '#3a5670', GLACIER) if dark else ('#ffffff', '#f7f9fb', INK, '#c9d6e2', FJORD)
    et = '#f08a3c' if dark else '#b4501a'  # ember as 12 px text: 6.48 / 5.12:1
    g = [f'<rect width="{w}" height="{h}" rx="16" fill="{bg}"/>',
         T('One optimization interval (default every 30 min)', 40, 44, 18, fg, 'InstrumentSans-Bold.ttf')]
    # inputs column
    ins = [('Prices', ['Tibber + learned prior']), ('Weather entity', ['forecast, irradiance']), ('Your sensors', ['temps, tanks, power'])]
    for i, (t, s) in enumerate(ins):
        y = 80 + i * 112
        g.append(box(40, y, 190, 84, t, s, fg, card, st))
        g.append(arrow(230, y + 42, 298, 214, '', ac))
    g.append(box(300, 170, 190, 88, 'Coordinator', ['staleness check,', 'learners freeze on bad input'], fg, card, st))
    g.append(arrow(490, 214, 598, 214, 'forecast arrays', ac, ly=196))
    g.append(T('(24 h)', 544, 238, 12, ac, anchor='middle'))
    g.append(box(600, 170, 170, 88, 'Thermal model', ['heat demand, COP,', 'solar gain, DHW draws'], fg, card, st))
    g.append(arrow(770, 214, 848, 214, 'predictions', ac, ly=196))
    g.append(box(850, 150, 310, 128, 'Optimizer (MPC)', ['minimise cost + comfort penalty', 'subject to comfort floor, tank limits,', 'fuse and peak caps'], fg, card, st, hi=True))
    g.append(arrow(930, 278, 850, 356, 'switch the heat pump', EMBER, lx=872, ly=312, anchor='end', tcol=et))
    g.append(arrow(1085, 278, 1085, 356, 'publish plan', EMBER, lx=1095, ly=322, anchor='start', tcol=et))
    g.append(box(700, 358, 190, 60, 'Heat pump', [], fg, card, st))
    g.append(box(960, 358, 200, 60, 'Plan sensors and card', [], fg, card, st))
    fb = SLATE if not dark else MIST
    g.append(f'<path d="M700 388 H672 Q662 388 662 378 V272 Q662 262 672 262 H684" fill="none" stroke="{fb}" stroke-width="1.6" stroke-dasharray="6 5"/>')
    g.append(f'<polygon points="690,262 681,257 681,267" fill="{fb}"/>')
    g.append(T('afterwards: prediction vs reality', 650, 316, 12, fb, anchor='end'))
    g.append(T('nudges the learners', 650, 334, 12, fb, anchor='end'))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="One optimization interval: prices, weather and sensors feed the coordinator, the thermal model predicts 24 hours, the optimizer solves for cost plus comfort, then the heat pump is switched and the plan is published; afterwards the learners compare prediction with reality.">{"".join(g)}</svg>'

def render(svg, name, w, h, out=OUT):
    p = f'{out}/{name}.svg'
    with open(p, 'w') as fh:
        fh.write(svg)
    html = f'{out}/{name}.html'
    with open(html, 'w') as fh:
        fh.write(f'<html><body style="margin:0"><img src="{name}.svg" style="display:block;width:{w}px;height:{h}px"></body></html>')
    subprocess.run(['node', os.path.join(HERE, 'render.mjs'), html, f'{out}/{name}.png', str(w), str(h), '2', '1'], check=True)
    os.remove(html)


if not FONTS:
    sys.exit('set HPO_FONTS to the directory holding the five .ttf files named in the module docstring')
if '--live' in sys.argv:
    LIVE = True
    for name, svg in (('banner', banner()), ('social-preview', social()), ('how-it-works', figure()), ('how-it-works-dark', figure(dark=True))):
        with open(f'{SOCIAL_OUT}/{name}.live.svg', 'w') as fh:
            fh.write(svg)
    print(SOCIAL_OUT); sys.exit(0)
render(banner(), 'banner', 1280, 320)
render(figure(), 'how-it-works', 1200, 440)
render(figure(dark=True), 'how-it-works-dark', 1200, 440)
render(social(), 'social-preview', 1280, 640, SOCIAL_OUT)
print('social preview (untracked):', SOCIAL_OUT)
