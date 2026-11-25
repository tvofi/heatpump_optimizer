#!/usr/bin/env python3
"""D6-s1 round 11: the live Pages site against the tree's docs/index.html and the built sub-pages.

Metric: differing lines between the live product page and docs/index.html, and per live sub-page
(each page tools/site/build_docs.mjs builds) whether it answers 200 and how many internal anchors
fail to resolve (dev/audit/harnesses/d6_page_anchors.py over the live URL).
Key: the bytes the live site serves, against the tree's own file and build.

RUN (export root, no cd; network):
    PYTHONUTF8=1 PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D6/s1/live_page.py [--page FILE]
Expected (2026-11-16, baseline 92d38ecb export, box B1): live_vs_tree_diff_lines=0, live_subpages_ok=9 of 9,
  live_unresolved_anchors=0. Volatile: the live site moves with each deploy.
Perturbation: --page FILE compares a different local page (e.g. a copy with one tile's number edited):
  live_vs_tree_diff_lines goes up from 0.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, difflib, ssl, subprocess, sys, time, urllib.request
from pathlib import Path

LIVE = "https://tvofi.github.io/heatpump_optimizer/"
ap = argparse.ArgumentParser()
ap.add_argument("--page", default="docs/index.html")
a = ap.parse_args()
t0, h0 = time.process_time(), time.thread_time()
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if Path("/root/.ccr/ca-bundle.crt").exists() else None


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "doc-link-check"})
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""


st, live = get(LIVE)
tree = Path(a.page).read_text()
diff = [l for l in difflib.unified_diff(tree.splitlines(), live.splitlines(), lineterm="", n=0)
        if l[:1] in "+-" and not l.startswith(("+++", "---"))]
print(f"live {LIVE} -> {st}, {len(live)} chars; tree {a.page} {len(tree)} chars")
for l in diff[:20]:
    print("  DIFF", l[:160])
manifest = Path("docs")  # sub-page names are build_docs.mjs's: readme, and each Documentation row's stem
names = ["readme", "how-it-works", "configuration", "setup", "dashboard-card", "automations", "architecture", "ecl110", "disclaimer"]
ok = 0
unresolved = 0
for n in names:
    url = f"{LIVE}{n}.html"
    s, _ = get(url)
    an = subprocess.run([sys.executable, "dev/audit/harnesses/d6_page_anchors.py", url], capture_output=True, text=True)
    out = an.stdout.strip()
    bad = 0
    if "unresolved=" in out:
        bad = int(out.split("unresolved=")[1].split()[0])
    unresolved += bad
    ok += s == 200
    print(f"  SUB {url} -> {s}; {out[len(url)+2:] if out.startswith(url) else out}")
print(f"RESULT live_status={st} code")
print(f"RESULT live_vs_tree_diff_lines={len(diff)} count")
print(f"RESULT live_subpages_ok={ok} count of {len(names)}")
print(f"RESULT live_unresolved_anchors={unresolved} count")
c, h = time.process_time() - t0, time.thread_time() - h0
print(f"RESULT thread_factor={c / h if h else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=" + next((l.split()[1] for l in Path("/proc/vmstat").read_text().splitlines() if l.startswith("pswpin")), "0"))
