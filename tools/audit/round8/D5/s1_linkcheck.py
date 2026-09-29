#!/usr/bin/env python3
"""s1_linkcheck.py

Metric: count of internal markdown links/anchors in README.md and docs/*.md
(excluding docs/delivery/, docs/decisions/, docs/superpowers/, which are
process record, not reader-facing docs) that point at a file that does not
exist or a `#anchor` that does not match any heading-derived slug in the
target file (or same file when no file is given).

Command: PYTHONPATH=tests/hastub python3 tools/audit/round8/D5/s1_linkcheck.py
Expected: RESULT broken_links=<n> (baseline cdf82daabcfe3777d98b31489f36df5555ec9d82: 2) +/- 0
Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
Machine: 4-vCPU cloud container (see BASELINE.md); this harness does no
timing/CPU work, so no thread_factor/load1 are meaningful, but they are
printed for contract compliance.

Perturbation: pass --break-one, which appends a bogus `[x](docs/does-not-exist.md)`
link to README.md (restored in a finally block) -- broken_links must increase
by exactly 1 under it.
"""
import os
import re
import sys
import time

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(ROOT, "..", "..", "..", ".."))

READER_FACING = [
    "README.md",
    "docs/how-it-works.md",
    "docs/configuration.md",
    "docs/setup.md",
    "docs/dashboard-card.md",
    "docs/automations.md",
    "docs/architecture.md",
    "docs/ecl110.md",
    "docs/HANDOVER.md",
    "DISCLAIMER.md",
]

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.M)


def slugify(text):
    text = re.sub(r"[`*_]", "", text)
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    # GitHub's own slugger replaces each whitespace run char-for-char with a
    # hyphen and does NOT collapse repeats, so "a  b" -> "a--b" not "a-b".
    text = re.sub(r"\s", "-", text)
    return text


def heading_slugs(path):
    if not os.path.exists(path):
        return set()
    text = open(path, encoding="utf-8").read()
    slugs = set()
    counts = {}
    for m in HEADING_RE.finditer(text):
        base = slugify(m.group(2))
        n = counts.get(base, 0)
        counts[base] = n + 1
        slugs.add(base if n == 0 else f"{base}-{n}")
    return slugs


def check_file(relpath):
    path = os.path.join(REPO, relpath)
    if not os.path.exists(path):
        return []
    text = open(path, encoding="utf-8").read()
    # Strip fenced code blocks so example links inside code are not counted.
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    own_slugs = heading_slugs(path)
    broken = []
    for m in LINK_RE.finditer(text):
        target = m.group(2)
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        if target.startswith("#"):
            anchor = target[1:]
            if anchor and anchor not in own_slugs:
                broken.append((relpath, target, "anchor-in-self", None))
            continue
        file_part, _, anchor = target.partition("#")
        target_path = os.path.normpath(os.path.join(os.path.dirname(path), file_part))
        rel_target = os.path.relpath(target_path, REPO)
        if not os.path.exists(target_path):
            broken.append((relpath, target, "missing-file", rel_target))
            continue
        if anchor:
            tslugs = heading_slugs(target_path)
            if anchor not in tslugs:
                broken.append((relpath, target, "anchor-in-target", rel_target))
    return broken


# Deliberately stripped from every seat's export per BASELINE.md / COMMON.md:
# docs/audit-*.md and docs/backlog.md do not exist here even though README and
# docs/how-it-works.md link them in the real repository. Not findings.
KNOWN_EXPORT_GAP = {"docs/audit-2026-08.md", "docs/audit-2026-09.md", "docs/backlog.md"}


def run():
    total = []
    for rel in READER_FACING:
        for entry in check_file(rel):
            rel_target = entry[3]
            if rel_target in KNOWN_EXPORT_GAP:
                continue
            total.append(entry)
    return total


def main():
    break_one = "--break-one" in sys.argv
    readme = os.path.join(REPO, "README.md")
    original = open(readme, encoding="utf-8").read()
    try:
        if break_one:
            with open(readme, "a", encoding="utf-8") as f:
                f.write("\n[bogus](docs/does-not-exist.md)\n")
        t0 = time.process_time()
        broken = run()
        t1 = time.process_time()
        for relpath, target, kind, _rel_target in broken:
            print(f"  {relpath} -> {target}  [{kind}]")
        print(f"RESULT broken_links={len(broken)} count")
        print(f"RESULT thread_factor=1.00 ratio")
        try:
            load1 = os.getloadavg()[0]
        except OSError:
            load1 = -1
        print(f"RESULT load1={load1} load")
        print(f"RESULT swapins=0 count")
    finally:
        if break_one:
            with open(readme, "w", encoding="utf-8") as f:
                f.write(original)


if __name__ == "__main__":
    main()
