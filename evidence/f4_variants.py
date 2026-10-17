import json, re, sys
from pathlib import Path
sys.path.insert(0, "tests")
from layout import locate
d = json.loads(Path("dev/programme/carries/carry-201.json").read_text())
FIELDS = ("from", "control", "brief")
def collect(node, keys=None, allstr=False, out=None):
    out = [] if out is None else out
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str) and (allstr or k in FIELDS): out.append(v)
            else: collect(v, keys, allstr, out)
    elif isinstance(node, list):
        for v in node: collect(v, keys, allstr, out)
    return out
def count(texts, rx):
    n = 0
    for t in texts:
        for m in rx.finditer(t):
            w = m.group(1); p = locate(w)
            if p != w and not Path(w).is_file() and Path(p).is_file(): n += 1
    return n
EXE = re.compile(r"(?<![\w./-])((?:[\w.-]+/)+[\w.-]+\.(?:py|mjs|js|sh))(?![\w.])")
ANYEXT = re.compile(r"(?<![\w./-])((?:[\w.-]+/)+[\w.-]+\.[A-Za-z0-9]+)(?![\w.])")
ANYPATH = re.compile(r"(?<![\w./-])((?:[\w.-]+/)+[\w.-]+)/?(?![\w.])")
sets = {
 "V1 from/control/brief, executable ext": (collect(d, allstr=False), EXE),
 "V2 from/control/brief, any extension": (collect(d, allstr=False), ANYEXT),
 "V3 all string fields, executable ext": (collect(d, allstr=True), EXE),
 "V4 all string fields, any extension": (collect(d, allstr=True), ANYEXT),
 "V5 all string fields, any path token": (collect(d, allstr=True), ANYPATH),
}
for k, (t, rx) in sets.items():
    print("%-42s %d" % (k, count(t, rx)))
