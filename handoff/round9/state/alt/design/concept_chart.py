"""Two chart concepts drawn from the same fixture plan the real card renders (plandata.json):
A  stacked panels, one y-axis each (dataviz recommendation)
B  one chart, all four y-axes, made legible: shared gridlines, one mark type per axis, direct labels."""
import json, math
P = json.load(open('plandata.json'))
S, Dh = P['space_plan']['forecast'], P['dhw_plan']['forecast']
N = len(S)
price = [r['price'] for r in S]; outdoor = [r['outdoor'] for r in S]; house = [r['room'] for r in S]
space = [r['space_power'] for r in S]; dhw = [r['dhw_power'] for r in Dh]
tank = [r['dhw_temp'] for r in Dh]; tlo = [r.get('dhw_temp_lo', r['dhw_temp']) for r in Dh]; thi = [r.get('dhw_temp_hi', r['dhw_temp']) for r in Dh]
solar = [max(0, 400 * math.sin(i / N * math.pi)) for i in range(N)]
PAL = {
 'light': dict(bg='#ffffff', ink='#212121', ink2='#5e5e5e', grid='#e3e7eb', price='#4a3aa7', solar='#d4561f', dhw='#d2403f', space='#2a78d6', outdoor='#3b7dd8', actioned='#008a70', tank='#c2477a', house='#008300', now='#026aa8'),
 'dark': dict(bg='#1c1c1c', ink='#e1e1e1', ink2='#a8a8a8', grid='#34383c', price='#9085e9', solar='#d95926', dhw='#e66767', space='#3987e5', outdoor='#4b95e8', actioned='#22a383', tank='#d55181', house='#1f9d1f', now='#4fb3f0'),
}
FONT = "font-family:Roboto,-apple-system,'Segoe UI',sans-serif"

def nice_hi(hi, n):
    raw = hi / (n - 1); mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if m * mag >= raw: return m * mag * (n - 1)

def ticks(lo, hi, n=5):
    return [lo + (hi - lo) * i / (n - 1) for i in range(n)]

def fmt(v):
    return f'{v:.0f}' if abs(v) >= 10 or v == int(v) else f'{v:.1f}'

def xs(x0, w):
    return [x0 + w * i / N for i in range(N + 1)]

def step_path(vals, X, y):
    d = f'M{X[0]:.1f} {y(vals[0]):.1f}'
    for i, v in enumerate(vals):
        d += f' V{y(v):.1f} H{X[i+1]:.1f}'
    return d

def line_path(vals, X, y):
    return 'M' + ' L'.join(f'{(X[i]+X[i+1])/2:.1f} {y(v):.1f}' for i, v in enumerate(vals))

def bars(vals, X, y, base, col, gap=1.0):
    out = []
    for i, v in enumerate(vals):
        if v <= 0.05: continue
        x = X[i] + gap / 2; w = X[i+1] - X[i] - gap; top = y(v)
        out.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{max(w,0.6):.1f}" height="{base-top:.1f}" rx="1" fill="{col}"/>')
    return ''.join(out)

def xaxis(X, y0, c, fs, every=4 * 4):
    out = []
    for i in range(0, N + 1, every):
        hh = i // 4
        out.append(f'<text x="{X[i]:.1f}" y="{y0+fs+6}" font-size="{fs}" fill="{c["ink2"]}" text-anchor="middle">{hh:02d}:00</text>')
    return ''.join(out)

def label(x, y, txt, col, fs, anchor='start', ink=None):
    return (f'<circle cx="{x-6 if anchor=="start" else x+6}" cy="{y-fs*0.35:.1f}" r="3.5" fill="{col}"/>'
            f'<text x="{x+2 if anchor=="start" else x-2}" y="{y:.1f}" font-size="{fs}" fill="{ink or col}" text-anchor="{anchor}">{txt}</text>')

def concept_a(mode, W=900, phone=False):
    c = PAL[mode]; fs = 11 if not phone else 10
    L, R = (46, 18) if not phone else (38, 12)
    pw = W - L - R; X = xs(L, pw)
    panels = [('Price', 'SEK/kWh', 70), ('Heating power', 'kW', 92), ('Temperatures', '°C', 110)]
    y = 10; g = []
    now_x = X[8]
    for title, unit, h in panels:
        g.append(f'<text x="{L}" y="{y+fs+2}" font-size="{fs+1}" font-weight="600" fill="{c["ink"]}">{title}</text>'
                 f'<text x="{L+pw}" y="{y+fs+2}" font-size="{fs}" fill="{c["ink2"]}" text-anchor="end">{unit}</text>')
        leg_y = y + 2 * fs + 8 if phone else y + fs + 2
        top = (leg_y + 12) if phone else (y + fs + 12); bot = top + h
        if title == 'Price':
            lo, hi = 0, nice_hi(max(price), 4)
            yy = lambda v, lo=lo, hi=hi, top=top, bot=bot: bot - (v - lo) / (hi - lo) * (bot - top)
            for t in ticks(lo, hi, 4):
                g.append(f'<line x1="{L}" x2="{L+pw}" y1="{yy(t):.1f}" y2="{yy(t):.1f}" stroke="{c["grid"]}"/><text x="{L-6}" y="{yy(t)+3.5:.1f}" font-size="{fs}" fill="{c["ink2"]}" text-anchor="end">{fmt(t)}</text>')
            sy = lambda v: bot - v / 450 * (bot - top) * 0.55
            g.append(f'<path d="{step_path(solar, X, sy)} V{bot} H{X[0]} Z" fill="{c["solar"]}" fill-opacity=".14"/>')
            g.append(f'<path d="{step_path(solar, X, sy)}" fill="none" stroke="{c["solar"]}" stroke-width="1.5" stroke-dasharray="4 3"/>')
            g.append(f'<path d="{step_path(price, X, yy)}" fill="none" stroke="{c["price"]}" stroke-width="2" stroke-linejoin="round"/>')
            leg = [('Electricity price', 'price'), ('Solar (relative)', 'solar')]
        elif title == 'Heating power':
            lo, hi = 0, 6
            yy = lambda v, lo=lo, hi=hi, top=top, bot=bot: bot - (v - lo) / (hi - lo) * (bot - top)
            for t in ticks(lo, hi, 4):
                g.append(f'<line x1="{L}" x2="{L+pw}" y1="{yy(t):.1f}" y2="{yy(t):.1f}" stroke="{c["grid"]}"/><text x="{L-6}" y="{yy(t)+3.5:.1f}" font-size="{fs}" fill="{c["ink2"]}" text-anchor="end">{fmt(t)}</text>')
            g.append(bars(space, X, yy, bot, c['space']))
            g.append(bars(dhw, X, yy, bot, c['dhw']))
            leg = [('Space heating', 'space'), ('Hot water', 'dhw')]
        else:
            lo, hi = -20, 60
            yy = lambda v, lo=lo, hi=hi, top=top, bot=bot: bot - (v - lo) / (hi - lo) * (bot - top)
            for t in ticks(lo, hi, 5):
                g.append(f'<line x1="{L}" x2="{L+pw}" y1="{yy(t):.1f}" y2="{yy(t):.1f}" stroke="{c["grid"]}"/><text x="{L-6}" y="{yy(t)+3.5:.1f}" font-size="{fs}" fill="{c["ink2"]}" text-anchor="end">{fmt(t)}</text>')
            band = line_path(thi, X, yy) + ' L' + ' L'.join(f'{(X[i]+X[i+1])/2:.1f} {yy(v):.1f}' for i, v in reversed(list(enumerate(tlo)))) + ' Z'
            g.append(f'<path d="{band}" fill="{c["tank"]}" fill-opacity=".16"/>')
            for key, vals, dash in (('tank', tank, ''), ('house', house, ''), ('outdoor', outdoor, ' stroke-dasharray="5 3"')):
                g.append(f'<path d="{line_path(vals, X, yy)}" fill="none" stroke="{c[key]}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"{dash}/>')
            leg = [('Hot-water tank', 'tank'), ('House', 'house'), ('Outdoor', 'outdoor')]
        g.append(f'<line x1="{now_x:.1f}" x2="{now_x:.1f}" y1="{top}" y2="{bot}" stroke="{c["now"]}" stroke-width="1.5" stroke-dasharray="3 3"/>')
        lx = L + 4 if phone else L + 120
        for k, (name, key) in enumerate(leg):
            g.append(label(lx + 10 + k * (118 if not phone else 104), leg_y, name, c[key], fs, ink=c['ink2']))
        y = bot + 8
    g.append(xaxis(X, y - 8, c, fs))
    Ht = y + fs + 12
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {Ht}" width="{W}" height="{Ht}" style="{FONT};background:{c["bg"]}">{"".join(g)}</svg>'

def concept_b(mode, W=900, phone=False):
    """One chart, four y-axes. The fixes: one shared set of gridlines that every axis ticks on; each axis owns one mark type;
    axis titles carry the swatch of what they measure; line series are labelled at their ends."""
    c = PAL[mode]; fs = 11 if not phone else 9.5
    L, R = (96, 104) if not phone else (66, 70)
    top, bot = 52, (310 if not phone else 260)
    pw = W - L - R; X = xs(L, pw); n = 5
    frac = lambda i: bot - (bot - top) * i / (n - 1)
    axes = {'°C': (-20, 60, ['tank', 'house', 'outdoor']), 'kW': (0, 6, ['space', 'dhw']), 'SEK/kWh': (0, nice_hi(max(price), 5), ['price']), 'W/m²': (0, 400, ['solar'])}
    def ymap(ax):
        lo, hi, _ = axes[ax]; return lambda v: bot - (v - lo) / (hi - lo) * (bot - top)
    g = []
    for i in range(n):
        g.append(f'<line x1="{L}" x2="{L+pw}" y1="{frac(i):.1f}" y2="{frac(i):.1f}" stroke="{c["grid"]}"/>')
    pos = {'°C': L - 8, 'kW': L - (52 if not phone else 38), 'SEK/kWh': L + pw + 8, 'W/m²': L + pw + (60 if not phone else 42)}
    row = {'kW': top - 34, 'W/m²': top - 34, '°C': top - 14, 'SEK/kWh': top - 14}
    for ax, (lo, hi, keys) in axes.items():
        right = ax in ('SEK/kWh', 'W/m²'); x = pos[ax]; anc = 'start' if right else 'end'
        for i, t in enumerate(ticks(lo, hi, n)):
            g.append(f'<text x="{x}" y="{frac(i)+3.5:.1f}" font-size="{fs}" fill="{c["ink2"]}" text-anchor="{anc}" style="font-variant-numeric:tabular-nums">{fmt(t)}' if ax == 'SEK/kWh' else f'<text x="{x}" y="{frac(i)+3.5:.1f}" font-size="{fs}" fill="{c["ink2"]}" text-anchor="{anc}">{fmt(t)}')
            g[-1] += '</text>'
        sw = ''.join(f'<rect x="{(x + (0 if right else -10)) + k*0:.1f}" y="{top-24+k*0}" width="0" height="0"/>' for k in range(0))
        # axis title with the swatches of what it measures
        tx = x
        ry = row[ax]
        if ax == 'kW':      # outer left: text from the card's left edge, swatches after it
            tw = len(ax) * fs * 0.62
            g.append(f'<text x="4" y="{ry}" font-size="{fs}" font-weight="600" fill="{c["ink"]}">{ax}</text>' +
                     ''.join(f'<rect x="{8 + tw + 9*k:.1f}" y="{ry-7}" width="7" height="7" rx="1.5" fill="{c[kk]}"/>' for k, kk in enumerate(keys)))
        elif ax == 'W/m²':  # outer right: swatches, then text ending at the card's right edge
            tw = len(ax) * fs * 0.66
            g.append(''.join(f'<rect x="{W - 8 - tw - 9*(k+1):.1f}" y="{ry-7}" width="7" height="7" rx="1.5" fill="{c[kk]}"/>' for k, kk in enumerate(keys)) +
                     f'<text x="{W-4}" y="{ry}" font-size="{fs}" font-weight="600" fill="{c["ink"]}" text-anchor="end">{ax}</text>')
        else:
            sws = ''.join(f'<rect x="{(tx + 1 + 9*k) if right else (tx - 8 - 9*k):.1f}" y="{ry-7}" width="7" height="7" rx="1.5" fill="{c[kk]}"/>' for k, kk in enumerate(keys))
            g.append(sws + f'<text x="{(tx + 4 + 9*len(keys)) if right else (tx - 12 - 9*len(keys))}" y="{ry}" font-size="{fs}" font-weight="600" fill="{c["ink"]}" text-anchor="{anc}">{ax}</text>')
    yC, yK, yP, yS = ymap('°C'), ymap('kW'), ymap('SEK/kWh'), ymap('W/m²')
    g.append(f'<path d="{step_path(solar, X, yS)} V{bot} H{X[0]} Z" fill="{c["solar"]}" fill-opacity=".10"/>')
    g.append(f'<path d="{step_path(solar, X, yS)}" fill="none" stroke="{c["solar"]}" stroke-width="1.2" stroke-dasharray="4 3"/>')
    g.append('<g opacity=".85">' + bars(space, X, yK, bot, c['space']) + bars(dhw, X, yK, bot, c['dhw']) + '</g>')
    band = line_path(thi, X, yC) + ' L' + ' L'.join(f'{(X[i]+X[i+1])/2:.1f} {yC(v):.1f}' for i, v in reversed(list(enumerate(tlo)))) + ' Z'
    g.append(f'<path d="{band}" fill="{c["tank"]}" fill-opacity=".14"/>')
    for key, vals, dash in (('tank', tank, ''), ('house', house, ''), ('outdoor', outdoor, ' stroke-dasharray="5 3"')):
        g.append(f'<path d="{line_path(vals, X, yC)}" fill="none" stroke="{c[key]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"{dash}/>')
    g.append(f'<path d="{step_path(price, X, yP)}" fill="none" stroke="{c["price"]}" stroke-width="2.2" stroke-linejoin="round"/>')
    now_x = X[8]
    g.append(f'<line x1="{now_x:.1f}" x2="{now_x:.1f}" y1="{top}" y2="{bot}" stroke="{c["now"]}" stroke-width="1.5" stroke-dasharray="3 3"/><text x="{now_x+4:.1f}" y="{bot-6}" font-size="{fs}" fill="{c["now"]}" paint-order="stroke" stroke="{c["bg"]}" stroke-width="3">now</text>')
    # direct end labels for the lines (<= 4 labelled), nudged apart so none overlap
    ends = sorted([(yC(tank[-1]), 'Tank', 'tank'), (yC(house[-1]), 'House', 'house'), (yC(outdoor[-1]), 'Outdoor', 'outdoor'), (yP(price[-1]), 'Price', 'price')])
    last = -99; ex = L + pw - 4
    for yv, name, key in ends:
        yv = max(yv, last + fs + 3); last = yv
        g.append(f'<text x="{ex}" y="{yv - 4:.1f}" font-size="{fs}" font-weight="600" fill="{c[key]}" text-anchor="end" paint-order="stroke" stroke="{c["bg"]}" stroke-width="3">{name}</text>')
    g.append(xaxis(X, bot, c, fs, every=16 if not phone else 24))
    Ht = bot + fs + 16
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {Ht}" width="{W}" height="{Ht}" style="{FONT};background:{c["bg"]}">{"".join(g)}</svg>'

if __name__ == '__main__':
    import os, subprocess
    os.makedirs('out/card', exist_ok=True)
    for mode in ('light', 'dark'):
        for W, phone in ((900, False), (375, True)):
            for name, fn in (('A-panels', concept_a), ('B-single', concept_b)):
                svg = fn(mode, W, phone); base = f'out/card/{name}-{mode}-{W}'
                open(base + '.svg', 'w').write(svg)
                h = float(svg.split('viewBox="0 0 ')[1].split('"')[0].split()[1])
                open(base + '.html', 'w').write(f'<html><body style="margin:0;background:{PAL[mode]["bg"]}">{svg}</body></html>')
                subprocess.run(['node', 'render.mjs', base + '.html', base + '.png', str(W), str(int(h)), '2'], check=True)
                os.remove(base + '.html')
    print(sorted(f for f in os.listdir('out/card') if f.endswith('.png')))
