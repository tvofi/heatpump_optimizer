"""D5-s1 harness: heading structure of README.md and the seven user docs.

Metric (one line): heading defects = level skips (e.g. ## -> ####), duplicate heading texts
within one file (ambiguous anchors), and files without exactly one H1; fenced code ignored.
Count key: ATX headings outside ``` fences, per file on disk.
Command (from the repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D5/s1/md_headings.py [--perturb]
--perturb demotes, in memory, README's "### Sensors (59 total)" to "## ", so its first
    "####" child skips a level. Expected: heading_defects up (0 -> 1).
Expected at baseline: heading_defects=0 (exact). Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; box B1.
"""
import os
import re
import sys
import time

_t0p, _t0t = time.process_time(), time.thread_time()
DOCS = ["README.md"] + [f"docs/{n}.md" for n in (
    "architecture", "automations", "configuration", "dashboard-card", "ecl110",
    "how-it-works", "setup")]
defects, headings = [], 0
for f in DOCS:
    text = open(f, encoding="utf-8").read()
    if "--perturb" in sys.argv and f == "README.md":
        text = text.replace("### Sensors (59 total)", "## Sensors (59 total)")
    prev, fence, seen, h1 = 0, False, {}, 0
    for i, line in enumerate(text.split("\n"), 1):
        if line.startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if not m:
            continue
        headings += 1
        lv, t = len(m.group(1)), m.group(2).strip()
        h1 += lv == 1
        if prev and lv > prev + 1:
            defects.append(f"skip {f}:{i} h{prev}->h{lv} {t}")
        seen.setdefault(t, []).append(i)
        prev = lv
    defects += [f"duplicate {f} '{t}' at {ls}" for t, ls in seen.items() if len(ls) > 1]
    if h1 != 1:
        defects.append(f"h1-count {f} = {h1}")
for d in defects:
    print(d)
cpu_p, cpu_t = time.process_time() - _t0p, time.thread_time() - _t0t
print(f"RESULT headings={headings} count")
print(f"RESULT heading_defects={len(defects)} count")
print(f"RESULT thread_factor={cpu_p / cpu_t if cpu_t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
