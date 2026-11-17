"""V2 (D17-v1) for D17-s1-01: independent count of options-flow fields absent
from `tools/audit/enumerate.py d17-features --kind option`.

Metric: |S - P| where S = every (step, key) in strings.json
options.step.<step>.data plus options.step.<step>.sections.<sec>.data, and P =
the (step, key) pairs parsed from the enumerator's printed option lines (any
line mentioning '<step>.<key>' or '<step>' and '<key>' tokens).
Also: of the fields whose key contains 'weekend' or 'holiday', how many are printed.
Run from the export root: python3 $HOME/vout/D17-v1/harness/v2_s1_01_enum.py
"""
import json, subprocess, sys, re

s = json.load(open("custom_components/heatpump_optimizer/strings.json"))
S = set()
nested = set()
for step, body in s["options"]["step"].items():
    for k in (body.get("data") or {}):
        S.add((step, k))
    for sec, sb in (body.get("sections") or {}).items():
        for k in (sb.get("data") or {}):
            S.add((step, k)); nested.add((step, k))
out = subprocess.run([sys.executable, "tools/audit/enumerate.py", "d17-features", "--kind", "option"],
                     capture_output=True, text=True).stdout
lines = [l for l in out.splitlines() if l.strip()]
toks = set()
for l in lines:
    for m in re.finditer(r"([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)", l):
        toks.add((m.group(1), m.group(2)))
missing = S - toks
wh = {x for x in S if re.search("weekend|holiday", x[1])}
print(f"RESULT printed_lines={len(lines)}")
print(f"RESULT declared={len(S)} nested={len(nested)}")
print(f"RESULT missing={len(missing)} missing_and_nested={len(missing & nested)} missing_flat={len(missing - nested)}")
print(f"RESULT weekend_holiday_declared={len(wh)} printed={len(wh - missing)}")
pages = {}
for st, k in missing:
    pages[st] = pages.get(st, 0) + 1
print("RESULT missing_by_page", dict(sorted(pages.items())))
print("SAMPLE_LINE", lines[0] if lines else None)
