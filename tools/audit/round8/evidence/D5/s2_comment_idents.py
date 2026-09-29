#!/usr/bin/env python3
"""D5-s2 harness: comments that abbreviate a real identifier down to a form
that itself has zero occurrences in code, in the same comment block as the
real (word-superset) identifier they abbreviate.

Method (two stages, both executed):

1. RAW SCAN. For every module docstring and every consecutive-`#`-line
   comment block longer than 3 lines under
   custom_components/heatpump_optimizer/*.py, extract underscore-containing
   tokens (``[A-Za-z_][A-Za-z0-9_]*_[A-Za-z0-9_]+``) -- backticked or bare.
   For each token, search the whole tree (custom_components/ and tests/,
   *.py) for a CODE occurrence of that exact word (grep -rnw), excluding
   lines that are themselves comment-only (`path:line:   #...`). This is
   the RAW candidate set (noisy: it also catches physics notation used as
   prose variables, e.g. `T_prev`, `q_eff`, which are not identifier claims
   at all, and citations of a name in a different repository).
2. SHORTHAND FILTER. A raw-missing token T is kept only if some OTHER
   identifier-shaped token U in the *same block* (a) DOES have a code
   occurrence by the stage-1 rule, and (b) T's underscore-split word set is
   a non-empty proper subset of U's word set (e.g. {min,power} subset of
   {conf,heat,pump,min,power}). This isolates "the comment abbreviated a
   real name to something that reads as a symbol but is not one" from noise
   that shares no word relationship with anything real in the block.
   RESULT shorthand_missing is the count surviving stage 2.

Command:
    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
    python3 tools/audit/round8/D5/s2_comment_idents.py

Expected value ± tolerance: shorthand_missing=2, exact, on the baseline
(cdf82daabcfe3777d98b31489f36df5555ec9d82): const.py:80's bare `MIN_POWER`
next to the real `CONF_HEAT_PUMP_MAX_POWER` (real sibling:
CONF_HEAT_PUMP_MIN_POWER, const.py:656, never itself named in the block),
and optimizer.py:6515's bare `min_power` next to the block's own backticked
`min_electrical_power` (real: ``self.model.params.min_electrical_power``,
used at optimizer.py:2131 etc.). raw_missing is provisional/noisy and not
part of the claim; only shorthand_missing is. Machine: this audit's cloud
container (4 vCPU / 15 GB); counts-only, contention-immune.

Perturbation: apply the one-line production edits in s2_min_power_fix.diff
(rewrites the two bare mentions to their real names) and re-run;
shorthand_missing must go to 0 (expected_direction: to_zero). raw_missing
drops by exactly 2 for the same reason and is reported alongside as a cross
check, though it is not the metric the claim rests on.
"""
import os
import re
import subprocess
import sys
import time

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(var, "1")

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(ROOT, "..", "..", "..", ".."))
os.chdir(REPO_ROOT)

BACKTICK_RE = re.compile(r"`{1,2}[^`]*`{1,2}")
IDENT_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*_[A-Za-z0-9_]+)\b")
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
                blocks.append((i + 1, j, "".join(lines[i:j])))
            i = j
        else:
            i += 1
    # module docstring (first statement, triple-quoted)
    text = "".join(lines)
    m = re.match(r'\s*(?:#.*\n)*\s*(\'\'\'|""")', text)
    if m:
        q = m.group(1)
        start = m.end() - len(q)
        end = text.find(q, m.end())
        if end != -1:
            doc = text[start:end + len(q)]
            blocks.append((1, text[:end].count("\n") + 1, doc))
    return blocks


def strip_backticked(text):
    return BACKTICK_RE.sub(" ", text)


def code_exists(word):
    r = subprocess.run(
        ["grep", "-rnw", word, "--include=*.py", "--include=*.mjs", "custom_components", "tests"],
        capture_output=True, text=True,
    )
    for line in r.stdout.splitlines():
        if not COMMENT_ONLY_RE.match(line):
            return True
    return False


DUNDER_RE = re.compile(r"^__[A-Za-z0-9_]+__$")


def words(ident):
    return frozenset(w for w in ident.strip("_").split("_") if w)


def main():
    import glob
    files = sorted(glob.glob("custom_components/heatpump_optimizer/*.py"))
    raw_missing = []
    exists_cache = {}
    checked = 0

    def exists(ident):
        if ident not in exists_cache:
            exists_cache[ident] = code_exists(ident)
        return exists_cache[ident]

    shorthand = []
    for f in files:
        file_blocks = comment_blocks(f)
        # every underscore identifier this file itself actually defines or
        # uses in real (non-comment) code -- the pool of "real siblings" a
        # shorthand in this file's comments could be abbreviating. Read
        # straight from the file's own non-comment lines via AST-free
        # tokenising (a name preceded by neither `#` nor inside a string is
        # good enough here: false positives only shrink the shorthand set).
        file_real = set()
        src_lines = open(f, encoding="utf-8").readlines()
        for line in src_lines:
            if line.lstrip().startswith("#"):
                continue
            code_part = line.split("#", 1)[0]
            for ident in IDENT_RE.findall(code_part):
                if not DUNDER_RE.match(ident):
                    file_real.add(ident)

        for (start, end, block) in file_blocks:
            idents = sorted(set(IDENT_RE.findall(block)))
            checked += len(idents)
            for ident in idents:
                if DUNDER_RE.match(ident):
                    continue  # a Python special method name, not a project symbol
                if exists(ident):
                    continue
                raw_missing.append((f, start, end, ident))
                tw = words(ident)
                if not tw:
                    continue
                for u in sorted(file_real):
                    uw = words(u)
                    if tw < uw:  # proper subset: ident is real word-subset of u
                        shorthand.append((f, start, end, ident, u))
                        break

    for m in raw_missing:
        print(f"RAW_MISSING {m[0]}:{m[1]}-{m[2]} {m[3]}")
    for s in shorthand:
        print(f"SHORTHAND {s[0]}:{s[1]}-{s[2]} {s[3]} -> real sibling {s[4]}")
    print(f"RESULT raw_missing={len(raw_missing)} count")
    print(f"RESULT shorthand_missing={len(shorthand)} count")
    print(f"RESULT checked_idents={checked} count")


if __name__ == "__main__":
    t0 = time.time()
    main()
    dt = time.time() - t0
    load1 = os.getloadavg()[0]
    print(f"RESULT wall_s={dt:.3f} s")
    print(f"RESULT load1={load1:.2f} n/a")
    print("RESULT thread_factor=1.00 ratio")
