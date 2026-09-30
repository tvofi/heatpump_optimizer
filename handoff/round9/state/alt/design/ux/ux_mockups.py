"""Lane UX mockups in the dusk identity (design of record for R9-UX-1..7).

Built on the lane-UI tokens (../overlay.js), the palette of record (../check_palette.py) and the concept-A chart
(../concept_chart.py). Plan values come from the repository fixture ../plandata.json (tests/plan_view.py); anything the
fixture cannot supply (advisor money, learned parameters, measured history, receipts) is an EXAMPLE and says so on the
mockup.   python3 ux_mockups.py   -> out/*.html and, via render_ux.mjs, out/*.png
"""
import json, math, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
_HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(_HERE + '/..')  # concept_chart reads plandata.json relative to the design folder
import concept_chart as cc
os.chdir(_HERE)
from color import contrast

P = json.load(open('../plandata.json'))
SP, DP = P['space_plan']['forecast'], P['dhw_plan']['forecast']
N = len(SP)
T = {
    'light': dict(page='#fafafa', card='#ffffff', text='#212121', text2='#727272', surface2='#f7f9fb', line='#e3e7eb',
                  accent='#026aa8', heat='#d2601f', ok='#1c7350', okbg='#e8f1ed', warn='#8a5a00', warnbg='#fbf1de',
                  crit='#b3261e', critbg='#fbe9e7', chip='#f3f6f9', btn='#026aa8', btntext='#ffffff', house='#008300',
                  tip='#ffffff', tipline='#d6dde4'),
    'dark': dict(page='#111111', card='#1c1c1c', text='#e1e1e1', text2='#9b9b9b', surface2='#242a30', line='#34383c',
                 accent='#4fb3f0', heat='#f08a3c', ok='#1fad6b', okbg='#1c3027', warn='#e3b25a', warnbg='#352c1a',
                 crit='#f28b82', critbg='#3b2322', chip='#262b30', btn='#4fb3f0', btntext='#0f2233', house='#1f9d1f',
                 tip='#262b30', tipline='#3a4148'),
}
MARK = ('<svg class="mk" viewBox="0 0 48 48" aria-hidden="true"><path d="M20 22 V26 H27 V35 H36 V22 Z" fill="#d2601f"/>'
        '<path d="M6 12 H13 V19 H20 V26 H27 V35 H36 V13 H42" fill="none" stroke="var(--accent)" stroke-width="3.6" '
        'stroke-linecap="round" stroke-linejoin="round"/></svg>')


def css(m):
    t = T[m]
    v = ';'.join(f'--{k}:{c}' for k, c in t.items())
    return f'''<style>:root{{{v}}}
*{{box-sizing:border-box}} body{{margin:0;padding:16px;background:var(--page);font:14px/1.45 Roboto,-apple-system,"Segoe UI",sans-serif;color:var(--text)}}
#m{{max-width:932px}} .card{{background:var(--card);border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,.18);overflow:hidden}}
.hdr{{display:flex;align-items:center;gap:12px;padding:12px 16px}} .mk{{width:28px;height:28px;flex:none}}
.ttl{{font-size:18px;font-weight:600}} .pill{{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:500;padding:3px 10px 3px 8px;border-radius:999px;white-space:nowrap}}
.pill::before{{content:"";width:7px;height:7px;border-radius:50%;background:currentColor}}
.ok{{color:var(--ok);background:var(--okbg)}} .warn{{color:var(--warn);background:var(--warnbg)}} .crit{{color:var(--crit);background:var(--critbg)}}
.tabs{{display:flex;gap:4px;padding:0 12px;border-bottom:1px solid var(--line);overflow-x:auto}} .tab{{padding:10px 12px;color:var(--text2);font-weight:500;white-space:nowrap;border-bottom:2px solid transparent;min-height:44px}}
.tab.on{{color:var(--accent);border-bottom-color:var(--accent)}} .body{{padding:16px;display:grid;gap:16px}}
h3{{margin:0;font-size:15px;font-weight:600}} .sub{{color:var(--text2);font-size:13px}} .ex{{font-size:12px;color:var(--text2);border:1px dashed var(--line);border-radius:6px;padding:2px 8px;justify-self:start}}
.rows{{display:grid;gap:8px}} .row{{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:12px;align-items:center;background:var(--surface2);border-radius:12px;padding:10px 12px}}
.row .t{{font-weight:500}} .row .d{{color:var(--text2);font-size:13px}} .val{{font-variant-numeric:tabular-nums;font-weight:600;white-space:nowrap;text-align:right}}
.btn{{font:inherit;font-weight:600;font-size:13px;border-radius:8px;padding:6px 12px;min-height:32px;border:1px solid var(--btn);white-space:nowrap}}
.btn.p{{background:var(--btn);color:var(--btntext)}} .btn.s{{background:transparent;color:var(--accent)}}
table{{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}} td,th{{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left}} th{{color:var(--text2);font-weight:500;font-size:12px}} td.n,th.n{{text-align:right}}
.grid2{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,380px),1fr));gap:16px;align-items:start}}
.big{{font-size:28px;font-weight:600;font-variant-numeric:tabular-nums}} .chk{{display:inline-grid;place-items:center;width:20px;height:20px;border-radius:50%;font-size:12px;font-weight:700}}
.chk.y{{background:var(--okbg);color:var(--ok)}} .chk.n{{border:1.5px solid var(--text2);color:var(--text2)}}
@media (max-width:600px){{.row{{grid-template-columns:minmax(0,1fr) auto}} .row .btn{{grid-column:1/-1;justify-self:start}}}}
</style>'''


def shell(m, active, body, pill=('ok', 'Heating now')):
    tabs = ''.join(f'<div class="tab{" on" if x == active else ""}">{x}</div>' for x in ('Plan', 'Setup', 'Savings', 'Advisor', 'Health'))
    return (f'<!doctype html><html><head><meta charset="utf-8">{css(m)}</head><body><div id="m"><div class="card">'
            f'<div class="hdr">{MARK}<span class="ttl">Heat pump plan</span><span class="pill {pill[0]}">{pill[1]}</span></div>'
            f'<div class="tabs">{tabs}</div><div class="body">{body}</div></div></div></body></html>')


def hhmm(i):
    return f'{(i * 15) // 60:02d}:{(i * 15) % 60:02d}'


# ---------- UX-1: why now, why not ----------
def runs(key, plan):
    out, s = [], None
    for i, p in enumerate(plan + [{key: 0}]):
        on = (p.get(key) or 0) > 0.05
        if on and s is None: s = i
        if not on and s is not None: out.append((s, i)); s = None
    return out


def narrative_lines():
    E = {'cheap_price': '{kwh} kWh in the cheapest hours for {cost} kr', 'terminal_value': 'leaving the house warm past the horizon: {kwh} kWh ({cost} kr)',
         'dhw_preheat': 'charging the tank while electricity is cheap: {kwh} kWh ({cost} kr)', 'dhw_window': 'hot water needed now: {kwh} kWh ({cost} kr)',
         'dhw_ready': 'getting the tank ready for a demand window: {kwh} kWh ({cost} kr)', 'comfort_floor': 'holding the minimum temperature took {kwh} kWh ({cost} kr)',
         'scheduled': 'keeping the house at target took {kwh} kWh ({cost} kr)', 'legionella': 'the anti-legionella cycle takes {kwh} kWh ({cost} kr)'}
    agg = {}
    for plan, key in ((SP, 'space_power'), (DP, 'dhw_power')):
        for p in plan:
            kw = p.get(key) or 0
            if kw > 0.05 and p.get('reason') in E:
                a = agg.setdefault(p['reason'], [0.0, 0.0]); a[0] += kw * .25; a[1] += kw * .25 * p['price']
    lines = [E[r].format(kwh=f'{k:.1f}', cost=f'{c:.2f}') for r, (k, c) in sorted(agg.items(), key=lambda x: -x[1][1])]
    idle_h = sum(1 for p in SP if (p.get('space_power') or 0) <= 0.05) / 4
    return lines + [f'space heating idle for {idle_h:g} h']


def ux1(m):
    i = 64  # 16:00, an idle space step in the fixture
    p = SP[i]; prices = [q['price'] for q in SP]
    dearer = sum(1 for q in prices if q >= p['price']) / N
    cheapest = min(prices); prev = [r for r in runs('space_power', SP) if r[1] <= i][-1]; nxt = [r for r in runs('space_power', SP) if r[0] > i][0]
    svg = cc.concept_a(m, 900)
    L, R = 46, 18; pw = 900 - L - R; x = L + pw * (i + .5) / N
    tip = (f'<div class="tip" style="left:{(x + 14) if x < 560 else (x - 314):.0f}px"><div class="tt">{hhmm(i)}–{hhmm(i + 1)} · Space heating off</div>'
           f'<div class="lk">Likely because</div><ul>'
           f'<li><b>{p["price"]:.2f} SEK/kWh</b> is among the dearest {math.ceil(dearer * 100)} % of the next 24 h (cheapest {cheapest:.2f})</li>'
           f'<li>The house is coasting on heat stored {hhmm(prev[0])}–{hhmm(prev[1])}</li>'
           f'<li>Next run {hhmm(nxt[0])} at {SP[nxt[0]]["price"]:.2f} SEK/kWh</li></ul>'
           f'<div class="ft">House {p["room"]:.1f} °C · outdoor {p["outdoor"]:.0f} °C</div></div>')
    nl = narrative_lines()
    body = (f'<div><h3>Today\'s plan</h3><ul class="nar">' + ''.join(f'<li>{s[0].upper() + s[1:]}</li>' for s in nl) + '</ul></div>'
            f'<div class="chart" style="position:relative;width:900px;max-width:100%">{svg}'
            f'<div class="xh" style="left:{x:.1f}px"></div>{tip}</div>')
    extra = '''<style>.nar{margin:6px 0 0;padding-left:18px;color:var(--text)} .nar li{margin:2px 0}
    .xh{position:absolute;top:0;bottom:24px;width:0;border-left:1px solid var(--text2)}
    .tip{position:absolute;top:150px;width:300px;background:var(--tip);border:1px solid var(--tipline);border-radius:12px;padding:10px 12px;box-shadow:0 4px 14px rgba(0,0,0,.18);font-size:13px}
    .tip .tt{font-weight:600} .tip .lk{color:var(--text2);margin-top:4px} .tip ul{margin:4px 0;padding-left:16px} .tip li{margin:2px 0} .tip .ft{color:var(--text2);border-top:1px solid var(--tipline);padding-top:6px;margin-top:6px}</style>'''
    return shell(m, 'Plan', body).replace('</head>', extra + '</head>'), dict(step=hhmm(i), price=p['price'], dearer_pct=math.ceil(dearer * 100), lines=nl)


# ---------- UX-2: advisor inbox ----------
def ux2(m):
    rows = [('Lower the hot-water setpoint to 48 °C', 'Still covers your heaviest day (Tuesdays, 9.8 kWh)', '≈ 35 kr/month', ('p', 'Apply')),
            ('Add a thermometer in the upstairs hall', 'The room forecast would tighten by about ±0.4 °C', '≈ 18 kr/month', ('s', 'Assign sensor')),
            ('Set the mixing valve target to 38 °C', 'At today\'s prices throttling costs more than it saves', '≈ 9 kr/month', ('p', 'Apply')),
            ('What one degree costs', '1 °C warmer ≈ +28 kr/month · 1 °C cooler ≈ −25 kr/month', '', ('s', 'Try in what-if'))]
    opt = [('Wood-stove timing', 'Turn on the wood furnace in Setup to see which evenings a fire beats the heat pump'),
           ('Fuse size', 'Turn on the peak tariff to see whether a smaller main fuse would pay'),
           ('Compressor frequency', 'Connect the compressor-frequency entity to see a recommended cap')]
    r = ''.join(f'<div class="row"><div><div class="t">{t}</div><div class="d">{d}</div></div><div class="val">{v}</div>'
                f'<button class="btn {b[0]}">{b[1]}</button></div>' for t, d, v, b in rows)
    o = ''.join(f'<div class="row"><div><div class="t">{t}</div><div class="d">{d}</div></div><div></div>'
                f'<button class="btn s">Open settings</button></div>' for t, d in opt)
    body = (f'<span class="ex">Example values</span><div><h3>Worth doing</h3><div class="sub">Ranked by what it saves; every figure is the integration\'s own estimate.</div></div>'
            f'<div class="rows">{r}</div><div><h3>More advice, once turned on</h3></div><div class="rows">{o}</div>')
    return shell(m, 'Advisor', body)


# ---------- UX-3 + UX-7: health ----------
def health(m, learned=False):
    inputs = [('Electricity prices', 'Tibber · updated 12 min ago', ('ok', 'Fresh')), ('Weather forecast', 'weather.home · 25 min ago', ('ok', 'Fresh')),
              ('Indoor temperature', '3 min ago', ('ok', 'Fresh')), ('Outdoor temperature', '2 h 10 min ago · limit 1 h · the plan uses the forecast instead', ('warn', 'Stale')),
              ('Hot-water tank', '4 min ago', ('ok', 'Fresh')), ('Heat pump power', '1 min ago', ('ok', 'Fresh'))]
    ir = ''.join(f'<div class="row"><div><div class="t">{t}</div><div class="d">{d}</div></div><span class="pill {s[0]}">{s[1]}</span><span></span></div>' for t, d, s in inputs)
    checks = [(True, 'Price source connected'), (True, 'Weather forecast with hourly steps'), (True, 'Indoor temperature sensor'),
              (True, 'Heat pump control answered a test write'), (False, 'Power meter on the heat pump: makes savings measured instead of modelled', 'Assign'),
              (False, '5 insight sensors are off by default: receipts, peak, fuse advice, compressor starts, wood', 'Show')]
    cr = ''.join(f'<div class="row"><div style="display:flex;gap:10px;align-items:center"><span class="chk {"y" if c[0] else "n"}">{"✓" if c[0] else ""}</span><span>{c[1]}</span></div><span></span>'
                 + (f'<button class="btn s">{c[2]}</button>' if len(c) > 2 else '<span></span>') + '</div>' for c in checks)
    wait = [('Savings this month', 'Waiting for the first full month, 1 Nov'), ('Prediction accuracy', '4 of 7 days collected'),
            ('Heavy-day hot-water demand', 'Needs about 2 more weeks of use')]
    wr = ''.join(f'<div class="row"><div><div class="t">{t}</div><div class="d">{d}</div></div><span class="pill warn" style="visibility:hidden">x</span><span></span></div>' for t, d in wait)
    body = ('<span class="ex">Example values</span><div class="grid2"><div style="display:grid;gap:8px"><h3>Inputs</h3>' + ir + '</div>'
            '<div style="display:grid;gap:8px"><h3>Plan</h3><div class="row"><div><div class="t">Solved 12 min ago</div><div class="d">Next solve in 18 min · 96 steps · 1.4 s</div></div><span class="pill ok">Fresh</span><span></span></div>'
            '<h3 style="margin-top:8px">Still learning</h3>' + wr + '</div></div>')
    if learned:
        L = [('House heat loss', '142 W/K', 21, 21, 'Learned from 21 days, ±6 %. The house loses heat 8 % faster than the questionnaire estimated.'),
             ('Solar gain', '3.1 m² effective window', 6, 14, 'Learning: 6 of about 14 sunny days'),
             ('Lower floor', '38 % of the upper floor\'s loss', 14, 14, 'Learned from 14 days'),
             ('Hot-water tank cooling', '0.9 °C per hour', 30, 30, 'Learned from 30 days'),
             ('Heat pump efficiency', 'Normal (COP scale 0.97)', 30, 30, 'No sign of degradation')]
        lr = ''.join(f'<div class="row"><div><div class="t">{t}</div><div class="d">{d}</div></div><div class="val">{v}</div>'
                     f'<div class="meter" title="{a} of {b}"><i style="width:{100 * a / b:.0f}%"></i></div></div>' for t, v, a, b, d in L)
        gains = [0.15, 0.12, 0.1, 0.1, 0.1, 0.12, 0.25, 0.4, 0.3, 0.2, 0.2, 0.22, 0.3, 0.25, 0.22, 0.25, 0.35, 0.5, 0.6, 0.55, 0.45, 0.35, 0.25, 0.18]
        W, H, B = 336, 64, 14; bw = W / 24
        bars = ''.join(f'<rect x="{k * bw + 1:.1f}" y="{H - B - g / 0.6 * (H - B - 4):.1f}" width="{bw - 2:.1f}" height="{g / 0.6 * (H - B - 4):.1f}" rx="2" fill="var(--accent)"/>' for k, g in enumerate(gains))
        axis = ''.join(f'<text x="{k * bw:.0f}" y="{H - 2}" font-size="10" fill="var(--text2)">{k:02d}</text>' for k in (0, 6, 12, 18))
        spark = f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Internal gains by hour, peaking at 0.6 kW around 18:00">{bars}{axis}</svg>'
        body += ('<div style="display:grid;gap:8px"><h3>What the model has learned</h3>' + lr +
                 f'<div class="row"><div><div class="t">Internal gains by hour</div><div class="d">People, cooking and appliances add up to 0.6 kW around 18:00</div></div><div>{spark}</div><span></span></div></div>')
    body += '<div class="row"><div><div class="t">Something looks wrong?</div><div class="d">The diagnostics file holds the last diagnosis, input states and the current plan, with tokens, names and locations removed.</div></div><span></span><button class="btn p">Download diagnostics</button></div>'
    body += '<div><h3>First-plan checklist</h3></div><div class="rows">' + cr + '</div>'
    extra = '<style>.meter{width:72px;height:6px;border-radius:3px;background:var(--line);overflow:hidden} .meter i{display:block;height:100%;background:var(--accent)}</style>'
    return shell(m, 'Health', body, pill=('warn', '1 input stale')).replace('</head>', extra + '</head>')


# ---------- UX-4: events + blueprint ----------
def ux4(m):
    ev = [(True, 'Monthly receipt', 'When a month closes'), (True, 'Comfort at risk', 'When the plan expects the house below your minimum'),
          (True, 'Input stale', 'When a required input has been stale for 1 h'), (False, 'Plan stale', 'When no plan has been solved for 90 min'),
          (True, 'Manual plan released', 'When your plan was released to protect comfort or hot water')]
    evr = ''.join(f'<div class="row"><div style="display:flex;gap:10px;align-items:center"><span class="chk {"y" if c else "n"}">{"✓" if c else ""}</span><div><div class="t">{t}</div><div class="d">{d}</div></div></div><span></span><span></span></div>' for c, t, d in ev)
    form = ('<div style="display:grid;gap:8px"><h3>Blueprint: Heat pump optimizer notifications</h3>'
            '<div class="row"><div><div class="t">Notify</div><div class="d">notify.mobile_app_phone</div></div><span></span><span></span></div>'
            + evr + '<div class="row"><div><div class="t">Quiet hours</div><div class="d">22:00–07:00, comfort alerts still come through</div></div><span></span><span></span></div></div>')
    nt = [('Monthly receipt: September', 'Heating and hot water cost 612 kr, 148 kr (19 %) less than a plain thermostat would have. Tap for the itemised receipt.'),
          ('Comfort at risk tonight', 'The plan expects 18.6 °C at 06:00, below your 19.0 °C minimum: the fuse limit caps heating 02:00–05:00. Tap to see the plan.')]
    ntr = ''.join(f'<div class="note"><div class="nh">{MARK}<span>Heat Pump Optimizer · now</span></div><div class="t">{t}</div><div class="d">{d}</div></div>' for t, d in nt)
    body = f'<span class="ex">Example values</span><div class="grid2">{form}<div style="display:grid;gap:10px"><h3>On the phone</h3>{ntr}</div></div>'
    extra = '<style>.note{background:var(--surface2);border-radius:16px;padding:12px 14px;display:grid;gap:4px} .note .nh{display:flex;gap:8px;align-items:center;font-size:12px;color:var(--text2)} .note .mk{width:18px;height:18px} .note .t{font-weight:600} .note .d{font-size:13px}</style>'
    return shell(m, 'Health', body).replace('</head>', extra + '</head>')


# ---------- UX-6: receipt + day-ahead replay ----------
def ux6(m):
    c = cc.PAL[m]; t = T[m]
    lines = [('Spot energy', '1 238 kWh', '498'), ('Grid energy fee', '1 238 kWh', '74'), ('Capacity charge', 'peak 5.8 kW', '40'), ('Compressor wear', '212 starts', 'not priced')]
    lr = ''.join(f'<tr><td>{a}</td><td class="n">{b}</td><td class="n">{v}{" kr" if v[0].isdigit() else ""}</td></tr>' for a, b, v in lines)
    reasons = [('In the cheapest hours', 312), ('Keeping the house at target', 96), ('Charging the tank while cheap', 58), ('Hot water needed now', 21), ('Anti-legionella cycle', 11)]
    mx = max(v for _, v in reasons); W = 380
    rb = ''.join(f'<div class="rb"><span>{n}</span><span class="bar"><i style="width:{v / mx * 100:.0f}%"></i></span><span class="val">{v} kr</span></div>' for n, v in reasons)
    receipt = (f'<div style="display:grid;gap:10px"><div class="sub">September 2026 · closed</div><div class="big">612 kr</div>'
               f'<div>Saved <b>148 kr</b> (19 %) against a plain thermostat</div><table><tr><th>Line</th><th class="n">Basis</th><th class="n">Cost</th></tr>{lr}'
               f'<tr><td><b>Total</b></td><td></td><td class="n"><b>612 kr</b></td></tr></table>'
               f'<div class="sub">Covers spot, the grid energy fee and the capacity charge. The savings figure compares spot cost only.</div></div>')
    byr = f'<div style="display:grid;gap:8px"><h3>Where the money went</h3>{rb}</div>'
    # replay: promised = the fixture plan; measured = an example deviation (labelled)
    prom = [q['room'] for q in SP]
    meas = [v + 0.18 * math.sin(k / 9) - 0.12 * max(0, math.sin((k - 20) / 12)) for k, v in enumerate(prom)]
    kw = [(SP[k].get('space_power') or 0) + (DP[k].get('dhw_power') or 0) for k in range(N)]
    cp, cm, a, b = [], [], 0.0, 0.0
    for k in range(N):
        a += kw[k] * .25 * SP[k]['price']; b += kw[k] * .25 * SP[k]['price'] * (1.0 + 0.06 * (k < 20)); cp.append(a); cm.append(b)
    Wc, L, R = 880, 44, 16; pw = Wc - L - R; X = [L + pw * (k + .5) / N for k in range(N)]
    def panel(y0, h, lo, hi, series, unit, title, fmt):
        y = lambda v: y0 + h - (v - lo) / (hi - lo) * h
        g = [f'<text x="{L}" y="{y0 - 8}" font-size="12" font-weight="600" fill="{t["text"]}">{title}</text><text x="{Wc - R}" y="{y0 - 8}" font-size="11" fill="{t["text2"]}" text-anchor="end">{unit}</text>']
        step = (hi - lo) / 3
        for k in range(4):
            v = lo + step * k
            g.append(f'<line x1="{L}" x2="{Wc - R}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="{c["grid"]}"/><text x="{L - 6}" y="{y(v) + 4:.1f}" font-size="11" fill="{t["text2"]}" text-anchor="end">{fmt(v)}</text>')
        for vals, col, dash, name in series:
            d = 'M' + ' L'.join(f'{X[k]:.1f} {y(vals[k]):.1f}' for k in range(N))
            g.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"{dash}/>')
        return ''.join(g)
    Ht = 330
    svg = (f'<svg viewBox="0 0 {Wc} {Ht}" width="{Wc}" style="max-width:100%;height:auto" role="img" aria-label="Yesterday: the plan\'s promised indoor temperature and cost against what was measured">'
           + panel(28, 110, 16, 22, [(prom, c['house'], ' stroke-dasharray="6 4"', 'Promised'), (meas, c['house'], '', 'Measured')], '°C', 'Indoor temperature', lambda v: f'{v:.0f}')
           + panel(182, 110, 0, math.ceil(max(cm) / 15) * 15, [(cp, c['price'], ' stroke-dasharray="6 4"', 'Promised'), (cm, c['price'], '', 'Measured')], 'kr, cumulative', 'Cost', lambda v: f'{v:.0f}')
           + ''.join(f'<text x="{L + pw * h / 24:.1f}" y="{Ht - 6}" font-size="11" fill="{t["text2"]}" text-anchor="{"start" if h == 0 else "end" if h == 24 else "middle"}">{h:02d}:00</text>' for h in (0, 6, 12, 18, 24))
           + '</svg>')
    dev = sum(abs(a - b) for a, b in zip(prom, meas)) / N
    leg = (f'<div class="leg"><span><svg width="26" height="8"><line x1="0" x2="26" y1="4" y2="4" stroke="{t["text2"]}" stroke-width="2" stroke-dasharray="6 4"/></svg>Promised by the plan at 00:00</span>'
           f'<span><svg width="26" height="8"><line x1="0" x2="26" y1="4" y2="4" stroke="{t["text2"]}" stroke-width="2"/></svg>Measured</span></div>')
    replay = (f'<div style="display:grid;gap:8px"><h3>Yesterday: the plan against reality</h3><div class="sub">Indoor stayed within {dev:.1f} °C of the promise on average; '
              f'cost ended {(cm[-1] / cp[-1] - 1) * 100:.0f} % above it, because the night was colder than forecast and the heating run drew more.</div>{leg}{svg}</div>')
    body = f'<span class="ex">Example values: receipt lines and the measured series are examples; the promised series is the repository plan fixture</span><div class="grid2">{receipt}{byr}</div>{replay}'
    extra = ('<style>.rb{display:grid;grid-template-columns:minmax(0,1fr) 140px 64px;gap:10px;align-items:center;font-size:13px} .bar{height:10px;background:var(--line);border-radius:5px;overflow:hidden}'
             ' .bar i{display:block;height:100%;background:var(--accent);border-radius:0 4px 4px 0} .leg{display:flex;gap:18px;flex-wrap:wrap;font-size:13px;color:var(--text2)} .leg span{display:inline-flex;gap:6px;align-items:center}</style>')
    return shell(m, 'Savings', body).replace('</head>', extra + '</head>'), dict(dev=round(dev, 2), cost_over=round((cm[-1] / cp[-1] - 1) * 100, 1))


if __name__ == '__main__':
    os.makedirs('out', exist_ok=True)
    meta = {}
    jobs = []
    for m in ('light', 'dark'):
        h1, meta['ux1'] = ux1(m); h6, meta['ux6'] = ux6(m)
        for name, html in (('UX-1-why', h1), ('UX-2-inbox', ux2(m)), ('UX-3-health', health(m)), ('UX-4-notify', ux4(m)),
                           ('UX-6-receipt-replay', h6), ('UX-7-model', health(m, True))):
            f = f'out/{name}-{m}.html'; open(f, 'w').write(html); jobs.append((f, 964))
            if m == 'light' and name in ('UX-2-inbox', 'UX-3-health', 'UX-6-receipt-replay'):
                f2 = f'out/{name}-{m}-phone.html'; open(f2, 'w').write(html); jobs.append((f2, 390))
    for f, w in jobs:
        subprocess.run(['node', 'render_ux.mjs', f, f.replace('.html', '.png'), str(w)], check=True)
    json.dump(meta, open('out/meta.json', 'w'), indent=1, ensure_ascii=False)
    print(len(jobs), 'renders'); print(json.dumps(meta, ensure_ascii=False)[:600])
