"""List full-net survivors of this box's slice without a D3.md step-4 answer yet, with code context."""
import glob, json, os, sys
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")
ROOT = os.path.abspath(os.path.join(S, *[".."] * 7))
done = {}
for p in sorted(glob.glob(os.path.join(os.path.dirname(S), "m4_u1a_part*.json"))):
    done.update(json.load(open(p)))
for k in [l.strip() for l in open(os.path.join(S, "keys-D3-u1a-surv.txt")) if l.strip()]:
    p = os.path.join(S, "results", "complete", k + ".json")
    if not os.path.exists(p) or k in done:
        continue
    r = json.load(open(p))
    if r["verdict"] != "SURVIVED":
        continue
    m = r["mutant"]; f = os.path.join(ROOT, m["file"]); L = m["line"]
    src = open(f).read().splitlines()
    fn = next((s.strip() for s in reversed(src[:L]) if s.lstrip().startswith(("def ", "async def "))), "?")
    print(f"== {k} {os.path.basename(m['file'])}:{L} {m.get('kind')} in {fn[:80]}")
    print(f"   NEW: {m['new'].strip()[:150]}")
    for i in range(max(0, L - 4), min(len(src), L + 2)):
        print((">> " if i == L - 1 else "   ") + src[i][:150])
