"""Reviewer's own probe: every path token (any extension) in any carry's remeasure/brief/control
field, spelled where the move map says the file no longer lives."""
import json, re, sys, glob
from pathlib import Path
sys.path.insert(0, "tests")
from layout import locate
rx = re.compile(r"(?<![\w./-])((?:\.?[\w-]+/)+[\w.*-]+\.[A-Za-z]{1,5})(?![\w])")
def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items(): yield from walk(v, path + "/" + k)
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from walk(v, f"{path}/{i}")
    elif isinstance(o, str): yield path, o
n = 0
for f in sorted(glob.glob("dev/programme/carries/*.json")):
    for p, s in walk(json.load(open(f))):
        for m in rx.finditer(s):
            w = m.group(1)
            if "*" in w: continue
            l = locate(w)
            if l != w and not Path(w).exists() and Path(l).exists():
                n += 1; print(f"{f}{p}\t{w}\t-> {l}")
print("RESULT moved_spellings_any_field_any_ext", n)
