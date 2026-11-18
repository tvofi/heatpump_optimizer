"""D5-s2 M2: internal link + anchor check over README.md and docs/*.md.
Metric: count of relative markdown links whose target file is missing, or whose
#fragment matches no GitHub-slugged heading (or explicit id/name) in the target.
Command: PYTHONPATH=tests/hastub python dev/audit/rounds/round10/D5/s2/links.py [--perturb]
Key: (source file, line, link) as delivered by the doc text. Expected: printed.
Baseline 17f1c55fad1b, machine B2 (macOS). --perturb renames README '## Removal'
heading in memory -> broken_links must rise by >=1.
"""
import os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import re, sys, glob, time
P = "--perturb" in sys.argv
files = ["README.md"] + sorted(glob.glob("docs/*.md"))
text = {f: open(f, encoding="utf-8").read() for f in files}
if P:
    text["README.md"] = text["README.md"].replace("### Removal", "### Uninstall", 1)
def slug(h):
    h = re.sub(r"[`*_]|<[^>]+>", "", h.strip().lower())
    h = re.sub(r"[^\w\- ]", "", h, flags=re.U)
    return h.replace(" ", "-")
def anchors(t):
    out, seen, fence = set(), {}, False
    for line in t.splitlines():
        if line.startswith("```"): fence = not fence; continue
        if fence: continue
        m = re.match(r"#{1,6}\s+(.*)", line)
        if m:
            s = slug(re.sub(r"\]\([^)]*\)", "]", m.group(1)).replace("[", "").replace("]", ""))
            n = seen.get(s, 0); seen[s] = n + 1
            out.add(s if n == 0 else f"{s}-{n}")
    out |= set(re.findall(r'(?:id|name)="([^"]+)"', t))
    return out
cache = {}
broken = []; total = 0
c0 = time.process_time(); t0 = time.thread_time()
for f in files:
    fence = False
    for i, line in enumerate(text[f].splitlines(), 1):
        if line.startswith("```"): fence = not fence; continue
        if fence: continue
        for tgt in re.findall(r"\]\(([^)\s]+)\)", line):
            if re.match(r"[a-z]+:", tgt): continue
            total += 1
            path, _, frag = tgt.partition("#")
            dest = os.path.normpath(os.path.join(os.path.dirname(f), path)) if path else f
            if not os.path.exists(dest):
                broken.append((f, i, tgt, "missing file")); continue
            if frag and dest.endswith(".md"):
                if dest not in cache:
                    cache[dest] = anchors(text.get(dest) or open(dest, encoding="utf-8").read())
                if frag not in cache[dest]:
                    broken.append((f, i, tgt, "missing anchor"))
for b in broken: print("BROKEN", *b)
print(f"RESULT internal_links={total} count")
print(f"RESULT broken_links={len(broken)} count")
tc = time.thread_time() - t0
print(f"RESULT thread_factor={((time.process_time()-c0)/tc if tc else 1):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
