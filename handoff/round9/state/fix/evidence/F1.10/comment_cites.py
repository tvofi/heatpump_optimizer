"""Companion to D5/s2/comment_numbers.py (which hard-codes each cited number,
so it reads flat when only the comment text changes). This one READS the
comment block above each symbol in the tree it runs in, extracts every number
word or numeral it cites, and counts a citation that is not the value the
same harness measures (0.55 derate floor, 30-minute default cadence, 10-minute
selector minimum). Run from a tree root."""
import re
P = "custom_components/heatpump_optimizer/"
WORDS = {"half": 0.5, "third": 1 / 3, "quarter": 0.25}
SITES = [  # (file, symbol line prefix, measured, unit regex)
    ("defrost.py", "DERATE_MIN =", 0.55, r"(half|third|quarter|\d+(?:\.\d+)?\s*%)"),
    ("const.py", "MIXING_VALVE_WRITE_EPSILON", 30.0, r"(\d+)\s*-?\s*minute"),
    ("coordinator.py", "PLAN_STALE_INTERVALS =", 10.0, r"(\d+)\s*-?\s*minute(?! *s? so)"),
]
bad = 0
for f, sym, measured, rx in SITES:
    lines = open(P + f).read().splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith(sym))
    j = i
    while j > 0 and lines[j - 1].lstrip().startswith("#"):
        j -= 1
    block = " ".join(l.strip("# ") for l in lines[j:i])
    cites = []
    for m in re.finditer(rx, block):
        t = m.group(1)
        v = WORDS.get(t) if t in WORDS else float(t.rstrip("% ")) / (100 if "%" in t else 1)
        cites.append(v)
    # the stale floor block also cites its own 90-minute floor, which holds
    wrong = [c for c in cites if abs(c - measured) > 1e-9 and c != 90.0]
    bad += len(wrong)
    print(f"ROW {f}:{sym.split()[0]} cites={cites} measured={measured} wrong={wrong}")
print(f"RESULT comment_citations_wrong={bad}")
