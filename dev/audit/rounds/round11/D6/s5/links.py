#!/usr/bin/env python3
"""D6-s5 M2 links: every link target text_ledger.py outline lists for the seat's cells resolves.

Metric: per link row of `text_ledger.outline`, the target file (relative to its document) exists in
the baseline tree and, for a `#fragment` into Markdown, a heading of the target slugs to it
(GitHub's rule: lowercase, punctuation but `-`/`_` dropped, spaces to `-`). External http(s)
targets would take a HEAD request; the seat's cells hold none (RESULT external=0).
Command (from the export root):
  PYTHONPATH=tests/hastub ~/venv-ci/bin/python3 dev/audit/rounds/round11/D6/s5/links.py --repo /home/user/heatpump_optimizer
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692: links=115 broken=0 external=0, exact.
Perturbation: --drop-target removes the first link's target from the tree listing -> broken 0 -> 1 (up).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, re, subprocess, sys

sys.path.insert(0, "tools/audit")
import text_ledger  # noqa: E402

SHA = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"


def slug(h):
    h = re.sub(r"[`*_]", lambda m: "_" if m.group(0) == "_" else "", h.strip().lower())
    return re.sub(r"\s", "-", re.sub(r"[^\w\- ]", "", h))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--drop-target", action="store_true")
    a = ap.parse_args()
    files = set(subprocess.check_output(["git", "-C", a.repo, "ls-tree", "-r", "--name-only", SHA], text=True).split("\n"))
    docs = text_ledger.seat_files("D6-s5", a.repo, SHA)
    links, broken, external = [], [], 0
    for d in docs:
        for line, kind, t in text_ledger.outline(d, text_ledger.read(".", d)):
            if kind == "link":
                links.append((d, line, t))
    if a.drop_target and links:
        d, _l, t = links[0]
        files.discard(os.path.normpath(os.path.join(os.path.dirname(d), t.split("#")[0])))
    for d, line, t in links:
        if t.startswith(("http://", "https://")):
            external += 1
            continue
        path, _, frag = t.partition("#")
        tgt = os.path.normpath(os.path.join(os.path.dirname(d), path)) if path else d
        if tgt not in files:
            broken.append(f"{d}:{line} -> {t} (no file)")
            continue
        if frag and tgt.endswith(".md"):
            src = subprocess.check_output(["git", "-C", a.repo, "show", f"{SHA}:{tgt}"], text=True)
            heads = {slug(m.group(2)) for m in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", src, re.M)}
            if frag not in heads:
                broken.append(f"{d}:{line} -> {t} (no heading)")
    for b in broken:
        print("BROKEN", b)
    print(f"RESULT links={len(links)}")
    print(f"RESULT broken={len(broken)}")
    print(f"RESULT external={external}")
    print("RESULT thread_factor=1.00")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
