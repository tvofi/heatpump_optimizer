"""Detail: clean draws not passing at a tree, and 1.5x/2x plants surviving among
clean-PASSING draws only (a plant on a clean draw already red is not a survivor)."""
import re, sys
from collections import defaultdict
lines = open(sys.argv[1]).read().splitlines()
rows = [l for l in lines if l.startswith("  1") and "->" in l]
surv = defaultdict(list)
print("CLEAN NOT PASSING:")
for l in rows:
    head, plants = l.split(" | ", 1)
    verdict = head.split("-> ", 1)[1]
    if verdict != "pass":
        print("  " + head.strip()[:230])
        continue
    for tok in plants.split():
        k, v = tok.rsplit(":", 1)
        if v == "PASS":
            m = re.search(r"ref_ms\s+([\d.]+)\s+loop_ref\s+([\d.]+)\s+(\S+)\s+cpu ([\d.]+) loop ([\d.]+)", head)
            surv[k].append(f"{m.group(3)}@{m.group(1)} cpu {m.group(4)} loop {m.group(5)} ({head.split()[2]})")
print("PLANTS SURVIVING ON CLEAN-PASSING DRAWS:")
for k in sorted(surv):
    print(f"  {k}: {len(surv[k])}")
    for s in surv[k]:
        print(f"     {s}")
