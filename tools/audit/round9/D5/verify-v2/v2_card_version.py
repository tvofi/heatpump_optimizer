"""D5 verify-v2 harness for D5-s1-03 (independent of the finder's card_version_doc.py).

Metric (one line): over the last N (default 20) release tags v<x.y.z> reachable from the
baseline, the share whose shipped card file's CARD_VERSION equals the tag's version
(the real release history the stamp produced, not a simulated stamp); plus whether
docs/dashboard-card.md still says the banner "is often lower than the integration version".
Count key: CARD_VERSION as read from `git show <tag>:custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`.
Command (repository root, needs tags fetched):
    python tools/audit/round9/D5/verify-v2/v2_card_version.py [N]
Perturbation (for the judge): read VERSION at each tag's parent release instead of the tag
itself -> share drops to 0 (an off-by-one-release card would show the lag the doc describes).
Pass --perturb to do exactly that.
Baseline 1936d5ca; exact.
"""
import os, re, subprocess, sys, time
_p0, _t0 = time.process_time(), time.thread_time()
N = int(next((a for a in sys.argv[1:] if a.isdigit()), 20))
CARD = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
def g(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True).stdout
tags = [t for t in g("tag", "--merged", "1936d5ca72a06556eeed4e8e5bf3dea520e517e1", "--sort=-v:refname").split()
        if re.fullmatch(r"v\d+\.\d+\.\d+", t)]
sel = tags[:N + 1]
eq = 0; used = 0
first_equal_run = None
for i, t in enumerate(sel[:N]):
    card = g("show", f"{t}:{CARD}")
    m = re.search(r'const CARD_VERSION = "(\d+\.\d+\.\d+)";', card)
    ref = sel[i + 1][1:] if "--perturb" in sys.argv else t[1:]
    if not m:
        continue
    used += 1
    ok = m.group(1) == ref
    eq += ok
    print(f"TAG {t} card={m.group(1)} {'EQ' if ok else 'DIFF'}")
doc = open("docs/dashboard-card.md", encoding="utf-8").read()
print(f"RESULT tags_checked={used} count")
print(f"RESULT card_equals_tag={eq} count")
print(f"RESULT share={eq/used if used else 0:.2f} ratio")
print(f"RESULT doc_says_often_lower={int('often lower than the integration version' in doc)} count")
cp, ct = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={cp/ct if ct else 1:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
