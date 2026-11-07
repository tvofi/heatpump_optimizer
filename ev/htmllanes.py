import re, sys, json
W = sys.argv[1]
res = {}
for e in ("base", "rev"):
    h = open(f"{W}/ev/plan-{e}.html").read()
    bands = [(int(y), int(y) + int(ht)) for y, ht in re.findall(r'<rect x="0" y="(\d+)" width="\d+" height="(\d+)" class="lane"/>', h)]
    labs = [(int(y), n) for y, n in re.findall(r'<text x="10" y="(\d+)" class="lanelab">([^<]+)</text>', h)]
    def band_of(y):
        for lo, hi in bands:
            if lo <= y < hi:
                for ly, n in labs:
                    if lo <= ly < hi: return n
        return None
    plan = json.load(open(f"{W}/ev/plan-{e}.json"))["groups"]
    drawn = {}
    for name, y in re.findall(r'<g class="grp"[^>]*data-name="([^"]+)"[^>]*><title>[^<]*</title><rect x="[\d.]+" y="(\d+)"', h):
        drawn["R10-" + name] = band_of(int(y))
    mism = [n for n, l in drawn.items() if plan.get(n, {}).get("lane") != l]
    by = {}
    for l in drawn.values(): by[l] = by.get(l, 0) + 1
    print(e, "lanes", [n for _, n in sorted(labs)], "drawn bars", len(drawn), "by lane", by, "html!=json", len(mism), mism)
    res[e] = drawn
mv = sorted(n for n in res["rev"] if res["base"].get(n) != res["rev"][n])
print("drawn moved", len(mv))
for n in mv: print(" ", n, res["base"].get(n), "->", res["rev"][n])
