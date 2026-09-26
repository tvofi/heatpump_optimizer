"""D6-s2 harness: every link in the seat's docs resolves.

Metric: count of markdown links in the seat's seven docs whose target does not resolve:
a relative file that does not exist, an #anchor no heading of the target file produces
(GitHub slug rule: lowercase, strip punctuation except '-' and ' ', spaces to '-'), or an
external URL whose HEAD (then GET) request does not return < 400. External requests go
through the environment's proxy; a transport error is counted separately as
'unreachable' (not as broken), so a sandbox without egress cannot inflate the count.
Symbol: the docs themselves (no production symbol; this is a link check, D6.M2 'links
with a HEAD request').

Command (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/s2/links.py [--offline]
Perturbation: --perturb appends a link to a missing anchor in memory; links_broken up by 1.
Expected: see REPORT.md (exact for local links; external depends on egress).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud container, 4 CPU, Linux.
Root rule: ROOT = Path.cwd().
"""

import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path.cwd()
_t0p, _t0t = time.process_time(), time.thread_time()
DOCS = ["docs/architecture.md", "docs/automations.md", "docs/configuration.md",
        "docs/dashboard-card.md", "docs/ecl110.md", "docs/how-it-works.md", "docs/setup.md"]


def slug(h):
    h = re.sub(r"[`*_]", "", h.strip().lower())
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


def anchors(path):
    out, seen = set(), {}
    in_code = False
    for line in path.read_text().splitlines():
        if line.startswith("```"):
            in_code = not in_code
        if in_code:
            continue
        m = re.match(r"^#{1,6}\s+(.*)$", line)
        if m:
            s = slug(m.group(1))
            n = seen.get(s, 0)
            out.add(s if n == 0 else f"{s}-{n}")
            seen[s] = n + 1
    return out


def main():
    offline = "--offline" in sys.argv
    broken, unreachable, local, external = [], [], 0, 0
    cache = {}
    for d in DOCS:
        p = ROOT / d
        text = p.read_text()
        if "--perturb" in sys.argv and d.endswith("setup.md"):
            text += "\n[x](#no-such-anchor-d6)\n"
        in_code = False
        for n, line in enumerate(text.splitlines(), 1):
            if line.startswith("```"):
                in_code = not in_code
            if in_code:
                continue
            for m in re.finditer(r"\]\(([^)\s]+)\)", line):
                tgt = m.group(1)
                if tgt.startswith(("http://", "https://")):
                    external += 1
                    if offline:
                        continue
                    if tgt not in cache:
                        try:
                            req = urllib.request.Request(tgt, method="HEAD", headers={"User-Agent": "d6-audit"})
                            code = urllib.request.urlopen(req, timeout=15).status
                        except urllib.error.HTTPError as e:
                            code = e.code
                            if code in (403, 405):
                                try:
                                    code = urllib.request.urlopen(urllib.request.Request(tgt, headers={"User-Agent": "d6-audit"}), timeout=15).status
                                except urllib.error.HTTPError as e2:
                                    code = e2.code
                                except Exception as e2:
                                    code = f"err {type(e2).__name__}"
                        except Exception as e:
                            code = f"err {type(e).__name__}"
                        cache[tgt] = code
                    code = cache[tgt]
                    if isinstance(code, str):
                        unreachable.append((f"{d}:{n}", tgt, code))
                    elif code >= 400:
                        broken.append((f"{d}:{n}", tgt, code))
                    continue
                if tgt.startswith("mailto:"):
                    continue
                local += 1
                file_part, _, anchor = tgt.partition("#")
                target = (p.parent / file_part).resolve() if file_part else p
                if not target.exists():
                    broken.append((f"{d}:{n}", tgt, "missing file"))
                    continue
                if anchor and target.suffix == ".md" and anchor not in anchors(target):
                    broken.append((f"{d}:{n}", tgt, "missing anchor"))
    for b in broken:
        print("BROKEN", *b)
    for u in unreachable:
        print("UNREACHABLE", *u)
    print(f"RESULT links_local={local} count")
    print(f"RESULT links_external={external} count")
    print(f"RESULT links_broken={len(broken)} count")
    print(f"RESULT links_unreachable={len(unreachable)} count")
    tp, tt = time.process_time() - _t0p, time.thread_time() - _t0t
    print(f"RESULT thread_factor={tp / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "na"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
