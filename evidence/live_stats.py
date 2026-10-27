import json, re, sys, os
WT = os.path.expanduser("~/hpo-seats/r10s6/review-2889b/wt-head")
sys.path.insert(0, WT + "/tools/audit/seat")
sys.path.insert(0, WT + "/tools/audit")
import roster_sync as R

d = json.load(open("/tmp/r10roster.json"))
groups = d["groups"]
dest = [g for g in groups if isinstance(g, dict) and g.get("group")]
carries = sum(len(g.get("carry") or []) for g in dest)
with_ruling = 0
naming_pr = re.compile(r"(?<![\w-])#\d+")
naming = 0
for g in dest:
    for c in (g.get("carry") or []):
        c = str(c)
        if R.rulings(c):
            with_ruling += 1
        if naming_pr.search(c):
            naming += 1
print("RESULT live_destinations:", len(dest))
print("RESULT live_carries:", carries)
print("RESULT live_carries_citing_ruling:", with_ruling)
print("RESULT live_carries_naming_pr:", naming)

# destinations holding >=2 carries that share a ruling but differ in normalised text
shared = []
for g in dest:
    cs = [str(x) for x in (g.get("carry") or [])]
    for i in range(len(cs)):
        for j in range(i+1, len(cs)):
            if R.rulings(cs[i]) & R.rulings(cs[j]) and R.finding_words(cs[i]) != R.finding_words(cs[j]):
                shared.append((g["group"], cs[i][:60], cs[j][:60]))
print("RESULT live_destinations_two_texts_one_ruling:", len(shared))
for s in shared:
    print("   shared:", s)

# how many destinations would a derived row citing a given ruling collide with?
