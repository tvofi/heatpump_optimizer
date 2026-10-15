#!/usr/bin/env python3
"""D6-web harness: claims table for docs/index.html (the product page).
RUN (repo root): PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D6/web/web_claims.py [--live] [--perturb-dims]
Key: RESULT lines count (a) declared-vs-actual image pixel dims read from the PNG
bytes (metric img_dim_mismatch), (b) per-claim verdicts. --live fetches the live
page and links (network). --perturb-dims rewrites the declared dims from the PNG
headers in memory (the one-line fix) and the mismatch count must go to 0.
Instrumented symbol: docs/index.html (the published artifact) vs const.py / strings.json.
"""
import json, os, re, struct, sys, urllib.request
ROOT = os.getcwd(); C = "custom_components/heatpump_optimizer"
page = open("docs/index.html").read()
readme = open("README.md").read()
rows = []
def claim(src, text, check, ok, note="", verdict=None):
    rows.append((len(rows)+1, src, text, check, verdict or ("true" if ok else "false"), note))
def rd(p): return open(p).read()
const = rd(f"{C}/const.py"); strings = json.load(open(f"{C}/strings.json"))
js = rd(f"{C}/www/heatpump-optimizer-card.js")

# tiles
claim("tile", "30 min between solves by default", "const DEFAULT_OPTIMIZATION_INTERVAL", bool(re.search(r"DEFAULT_OPTIMIZATION_INTERVAL: Final = 30\b", const)))
claim("tile", "20 h of pinnable run slots", "const MANUAL_PLAN_WINDOW_HOURS", "MANUAL_PLAN_WINDOW_HOURS: Final = 20" in const)
claim("tile", "EN/SV entity names", "translations dir", sorted(os.listdir(f"{C}/translations"))==["en.json","sv.json"])
claim("tile", "24 h plan", "const.py states horizon 24 h", "horizon is 24 h" in const)
snap = rd(f"{C}/snapshots.py")
claim("feat", "weekly snapshots, last eight kept", "snapshots.RING_SIZE", "RING_SIZE = 8" in snap)
claim("feat", "90th percentile heavy-day target", "dhw_draws.quantile default q", "q: float = 0.9" in rd(f"{C}/dhw_draws.py"))
claim("feat", "card type custom:heatpump-optimizer-card", "frontend.py/js registers", "heatpump-optimizer-card" in rd(f"{C}/frontend.py") or "heatpump-optimizer-card" in js)
claim("feat", "Apply this plan button", "card js string", '"Apply this plan"' in js)
claim("feat", "Advisor: Worth doing / More advice sections", "card js strings", '"Worth doing"' in js and "More advice" in js)
q = strings["config"]["step"]["quick_setup"]["data"]
claim("alt", "Quick setup: five toggles, two wood sensor pickers", "strings quick_setup fields", [k for k in q if k in("two_zone","buffer_tank","dhw_tank","wood_furnace","wood_buffer_tank")].__len__()==5 and sum("wood_tank_" in k for k in q)==2)
m = strings["config"]["step"]
menu = [v for st in m.values() for v in st.get("menu_options",{}).values()]
claim("alt", "Finish-setup menu: Quick setup (recommended), Continue setup, Finish setup now", "strings menu_options", all(x in menu for x in("Quick setup (recommended)","Continue setup","Finish setup now")))
claim("alt", "Customize by weekday switch", "strings dhw_windows_by_day", '"dhw_windows_by_day": "Customize by weekday"' in open(f"{C}/strings.json").read())
claim("feat", "Prices only Tibber or an entity", "const PRICE_SOURCES", "PRICE_SOURCES: Final = (PRICE_SOURCE_TIBBER, PRICE_SOURCE_ENTITY)" in const)
claim("req", "HA 2025.2.0 floor", "hacs.json", json.load(open("hacs.json"))["homeassistant"]=="2025.2.0")
claim("req", "Python 3.13 or newer / numpy scipy threadpoolctl from manifest", "manifest requirements", [r.split(">")[0] for r in json.load(open(f"{C}/manifest.json"))["requirements"]]==["numpy","scipy","threadpoolctl"] and "Python 3.13 or newer" in readme)
claim("text", "fork of strutsfarm/heatpump_optimizer 2.2.0", "README acknowledgement", "strutsfarm/heatpump_optimizer" in readme and "2.2.0" in readme)
claim("version", "page carries no version/feature-count figure", "regex over visible text", not re.search(r"\bv?\d+\.\d+\.\d+\b", re.sub(r"<(style|script|svg).*?</\1>","",page,flags=re.S).replace("2025.2.0","").replace("2.2.0","").replace("3.13","")))
claim("version", "VERSION==manifest==7.0.0", "VERSION/manifest", rd("VERSION").strip()==json.load(open(f"{C}/manifest.json"))["version"])
for dq in re.findall(r'data-q="([^"]+)"', page):
    claim("tile-q", dq, "substring in README (case-insens)", dq.lower() in re.sub(r"\s+"," ",readme.lower()))

# anchors
ids = set(re.findall(r'\bid="([^"]+)"', page))
for a in sorted(set(re.findall(r'href="#([^"]*)"', page))):
    claim("anchor", "#"+a, "id present", a in ids or a=="top")
# images
mism = 0; imgs = []
def png(p):
    d = open(p,"rb").read(24); return struct.unpack(">II", d[16:24])
for tag in re.findall(r"<img[^>]*>", page):
    src = re.search(r'src="([^"]+)"', tag).group(1); wh = re.search(r'width="(\d+)" height="(\d+)"', tag)
    p = "docs/"+src; ex = os.path.exists(p)
    claim("img", src, "file exists", ex)
    if ex and wh:
        a = png(p); d = tuple(map(int, wh.groups()))
        if "--perturb-dims" in sys.argv: d = a
        if a != d:
            mism += 1; claim("img-dim", f"{src} declared {d[0]}x{d[1]}", "PNG header", False, f"actual {a[0]}x{a[1]}")
        else: claim("img-dim", src, "PNG header", True)
for s in re.findall(r'srcset="([^"]+)"', page):
    claim("img", s, "file exists", os.path.exists("docs/"+s))
# internal pages + external links
pages = {"readme","setup","how-it-works","configuration","dashboard-card","automations","architecture","ecl110","disclaimer"}
for h in sorted(set(re.findall(r'href="([a-z-]+)\.html', page))):
    claim("link", h+".html", "built page name known", h in pages)
if "--live" in sys.argv:
    def get(u, m="GET"):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, method=m, headers={"User-Agent":"d6web"}), timeout=20); return r.status, r.read()
        except Exception as e: return getattr(e,"code",str(e)), b""
    st, body = get("https://tvofi.github.io/heatpump_optimizer/")
    claim("live", "live page == docs/index.html at baseline", "byte compare", body.decode()==page, f"http {st}")
    for h in sorted(pages): claim("live", h+".html", "GET", get(f"https://tvofi.github.io/heatpump_optimizer/{h}.html")[0]==200)
    for u in ["https://github.com/tvofi/heatpump_optimizer","https://github.com/tvofi/heatpump_optimizer/blob/main/LICENSE"]:
        claim("link", u, "GET", get(u)[0]==200)
    for p in set(re.findall(r'(?:src|srcset)="(img/[^"]+)"', page)): claim("live", p, "GET", get("https://tvofi.github.io/heatpump_optimizer/"+p)[0]==200)

print("id|source|claim|check|verdict|note")
for r in rows: print("|".join(map(str,r)))
from collections import Counter
c = Counter(r[4] for r in rows)
print(f"RESULT claims extracted={len(rows)} checked={len(rows)-c['unverifiable']} false={c['false']} stale={c['stale']} unverifiable={c['unverifiable']}")
print(f"RESULT img_dim_mismatch={mism}")
