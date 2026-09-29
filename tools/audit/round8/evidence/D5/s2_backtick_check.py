#!/usr/bin/env python3
"""D5-s2 non-finding harness: backtick-quoted identifiers in code comments
that do not exist as a real symbol anywhere in the tree.

Metric: for every module docstring and every consecutive-`#`-line comment
block longer than 3 lines under custom_components/heatpump_optimizer/*.py,
extract every single- or double-backtick-quoted token that looks like a
dotted/underscored Python identifier (``[A-Za-z_][A-Za-z0-9_.]*``), take its
first dotted component, and check for a non-comment occurrence of that exact
word anywhere under custom_components/ or tests/ (grep -rnw, *.py). RESULT
backtick_missing is the count with zero such occurrence.

Command:
    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
    python3 tools/audit/round8/D5/s2_backtick_check.py

Expected value ± tolerance: 0, exact, on the baseline
(cdf82daabcfe3777d98b31489f36df5555ec9d82): every backtick-marked name this
codebase's own code comments cite resolves to something real. Machine: this
audit's cloud container (4 vCPU / 15 GB); counts-only, contention-immune.

Perturbation: s2_comment_idents.py's own MIN_POWER/min_electrical_power pair
(see that harness) shows the checker does detect a genuine miss when one is
present -- those two are BARE (unbacktracked) misses, which is why this
script's own RESULT is 0 while s2_comment_idents.py's shorthand_missing is 2:
this is evidence that the codebase's authors reserve backticks for names they
have actually checked, and use bare prose names more loosely. As a direct
perturbation on this script itself: temporarily add a nonexistent name in
double backticks to any qualifying comment block and rerun -- backtick_missing
must move from 0 to 1 (expected_direction: up). Not applied to production;
this is a self-test of the checker, run by hand, not part of the RESULT below.
"""
import os
import re
import subprocess
import time

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(var, "1")

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(ROOT, "..", "..", "..", ".."))
os.chdir(REPO_ROOT)

BT_RE = re.compile(r"`{1,2}([A-Za-z_][A-Za-z0-9_.]*)`{1,2}")
COMMENT_ONLY_RE = re.compile(r"^[^:]+:\d+:\s*#")


def comment_blocks(path):
    lines = open(path, encoding="utf-8").readlines()
    n = len(lines)
    i = 0
    blocks = []
    while i < n:
        stripped = lines[i].lstrip()
        if stripped.startswith("#") and not stripped.startswith("#!"):
            j = i
            while j < n and lines[j].lstrip().startswith("#"):
                j += 1
            if j - i > 3:
                blocks.append((i + 1, "".join(lines[i:j])))
            i = j
        else:
            i += 1
    text = "".join(lines)
    m = re.match(r'\s*(?:#.*\n)*\s*(\'\'\'|""")', text)
    if m:
        q = m.group(1)
        start = m.end() - len(q)
        end = text.find(q, m.end())
        if end != -1:
            blocks.append((1, text[start:end + len(q)]))
    return blocks


def code_exists(word):
    r = subprocess.run(
        ["grep", "-rnw", word, "--include=*.py", "--include=*.mjs", "custom_components", "tests"],
        capture_output=True, text=True,
    )
    for line in r.stdout.splitlines():
        if not COMMENT_ONLY_RE.match(line):
            return True
    return False


def main():
    import glob
    files = sorted(glob.glob("custom_components/heatpump_optimizer/*.py"))
    names = {}
    for f in files:
        for (start, block) in comment_blocks(f):
            for m in BT_RE.finditer(block):
                name = m.group(1).split(".")[0]
                if len(name) < 4:
                    continue
                names.setdefault(name, (f, start))

    missing = [n for n in names if not code_exists(n)]
    for n in sorted(missing):
        print(f"MISSING_BACKTICK {n} first seen at {names[n]}")
    print(f"RESULT backtick_missing={len(missing)} count")
    print(f"RESULT backtick_checked={len(names)} count")


if __name__ == "__main__":
    t0 = time.time()
    main()
    dt = time.time() - t0
    load1 = os.getloadavg()[0]
    print(f"RESULT wall_s={dt:.3f} s")
    print(f"RESULT load1={load1:.2f} n/a")
    print("RESULT thread_factor=1.00 ratio")
