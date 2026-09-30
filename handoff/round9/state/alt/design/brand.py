"""Build the identity's SVG masters (outlined type) and the Home Assistant brand PNG set."""
import os, subprocess, json
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from PIL import Image

FONTS = '/root/.claude/skills/synced/c7dd3f1e-c571-4ca2-a0de-fcecc6fb749a_a98e53c1-333f-4779-a652-b12285f4d3ce/canvas-design/canvas-fonts'
OUT = 'out'
os.makedirs(OUT, exist_ok=True)
SW = 3.6
LINE = 'M6 12 H13 V19 H20 V26 H27 V35 H36 V13 H42'
POOL = 'M20 22 V26 H27 V35 H36 V22 Z'
COL = {
    'light': dict(line='#026aa8', heat='#d2601f', ink='#0f2233', sub='#5b6b7a'),
    'dark': dict(line='#4fb3f0', heat='#d2601f', ink='#f3f8fc', sub='#9fb3c4'),
    'tile_light': dict(line='#f3f8fc', heat='#f08a3c', bg='#026aa8'),
    'tile_dark': dict(line='#f3f8fc', heat='#f08a3c', bg='#0f2233'),
}

def mark(mode, tx=0, ty=0, s=1.0):
    c = COL[mode]
    bg = f'<rect width="48" height="48" rx="11" fill="{c["bg"]}"/>' if 'bg' in c else ''
    return (f'<g transform="translate({tx} {ty}) scale({s})">{bg}<path d="{POOL}" fill="{c["heat"]}"/>'
            f'<path d="{LINE}" fill="none" stroke="{c["line"]}" stroke-width="{SW}" stroke-linecap="round" stroke-linejoin="round"/></g>')

def text_path(text, font, size, x, y, tracking=0.0):
    f = TTFont(os.path.join(FONTS, font)); gs = f.getGlyphSet(); cmap = f.getBestCmap()
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

def svgdoc(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}" width="{w:.1f}" height="{h:.1f}">{body}</svg>'

def lockup(mode, stacked=True):
    c = COL[mode]
    if stacked:
        p1, w1 = text_path('Heat Pump', 'Outfit-Bold.ttf', 30, 60, 26, 0.0)
        p2, w2 = text_path('Cost Optimizer', 'Outfit-Regular.ttf', 22, 61, 50, 0.02)
        w = 60 + max(w1, w2) + 2
        body = mark(mode, -7.5, -3.5, 1.36) + f'<path d="{p1}" fill="{c["ink"]}"/><path d="{p2}" fill="{c["sub"]}"/>'
        return svgdoc(w, 56, body)
    p1, w1 = text_path('Heat Pump ', 'Outfit-Bold.ttf', 28, 58, 33)
    p2, w2 = text_path('Cost Optimizer', 'Outfit-Regular.ttf', 28, 58 + w1, 33)
    return svgdoc(58 + w1 + w2 + 2, 48, mark(mode, -3, -3.6, 1.14) + f'<path d="{p1}" fill="{c["ink"]}"/><path d="{p2}" fill="{c["sub"]}"/>')

def icon(mode):
    return svgdoc(48, 48, mark(mode))

def render(svg_text, png, w, h, scale=1):
    src = png.replace('.png', '.svg')
    open(src, 'w').write(svg_text)
    html = src.replace('.svg', '.html')
    open(html, 'w').write(f'<html><body style="margin:0;background:transparent">'
                          f'<img src="{os.path.basename(src)}" style="width:{w}px;height:{h}px;display:block"></body></html>')
    subprocess.run(['node', 'render.mjs', html, png, str(w), str(h), str(scale), '1'], check=True)
    os.remove(html)

def trim(png, pad=0, square=False):
    im = Image.open(png).convert('RGBA'); bb = im.getbbox(); im = im.crop(bb)
    if square:
        s = max(im.size) + 2 * pad; can = Image.new('RGBA', (s, s), (0, 0, 0, 0))
        can.paste(im, ((s - im.width) // 2, (s - im.height) // 2)); im = can
    im.save(png)

if __name__ == '__main__':
    import shutil
    for mode in ('light', 'dark'):
        # masters
        open(f'{OUT}/mark-{mode}.svg', 'w').write(icon(mode))
        open(f'{OUT}/lockup-stacked-{mode}.svg', 'w').write(lockup(mode, True))
        open(f'{OUT}/lockup-inline-{mode}.svg', 'w').write(lockup(mode, False))
        open(f'{OUT}/tile-{mode}.svg', 'w').write(icon('tile_' + mode))
    # HA brand set (brand/): icon 256 + @2x 512, dark_ variants; logo landscape, shortest side 128 (@2x 256)
    B = f'{OUT}/brand'; os.makedirs(B, exist_ok=True)
    for mode, pre in (('light', ''), ('dark', 'dark_')):
        for size, suf in ((256, ''), (512, '@2x')):
            p = f'{B}/{pre}icon{suf}.png'
            render(icon(mode), p, size, size)
            trim(p, pad=int(size * 0.04), square=True)
            Image.open(p).resize((size, size), Image.LANCZOS).save(p)
        lk = lockup(mode, True)
        vb = [float(v) for v in lk.split('viewBox="')[1].split('"')[0].split()]
        for h, suf in ((146, ''), (292, '@2x')):
            w = round(vb[2] * h / vb[3])
            p = f'{B}/{pre}logo{suf}.png'
            render(lk, p, w, h)
            trim(p)
    for f in os.listdir(B):
        if f.endswith('.svg'): os.remove(os.path.join(B, f))
    print(json.dumps({f: Image.open(os.path.join(B, f)).size for f in sorted(os.listdir(B))}))
