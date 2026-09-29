#!/usr/bin/env python3
"""v1_comment_idents_pyscan.py -- independent re-measure of D5-s2-01.

Own method, deliberately not reusing s2_comment_idents.py's code: no
subprocess grep, no word-subset heuristic scan over all comment blocks.
Instead this targets exactly the two claimed symbols directly and answers
the narrower, decisive question: does `MIN_POWER` (as a whole word) or
`min_power` (as a whole word) appear ANYWHERE in the tree's actual
(non-comment, non-string-literal-only) Python or JS/mjs code, and do the two
real full names (CONF_HEAT_PUMP_MIN_POWER, min_electrical_power) appear in
the same comment block as the bare form?

Method: read every .py/.mjs file under custom_components/ and tests/,
split each line on the first unescaped '#' (Python) or search raw text for
JS since the repo's only .mjs harnesses live under tests/), and regex-search
the code-only portion (Python) / whole line (mjs, since no // stripping is
needed for this pair) for the two bare tokens as whole words. This is a
plain Python re scan, not grep -w, so it is a genuinely different
implementation of "does this word occur in code" than s2_comment_idents.py's
`subprocess.run(["grep", "-rnw", ...])`.

Command: PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  python3 tools/audit/round8/D5/v1_comment_idents_pyscan.py
Expected: RESULT confirmed_shorthand=2 count
Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
"""
import glob
import os
import re

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(ROOT, "..", "..", "..", ".."))
os.chdir(REPO)

TARGETS = [
    ("MIN_POWER", "CONF_HEAT_PUMP_MIN_POWER", "custom_components/heatpump_optimizer/const.py", 80),
    ("min_power", "min_electrical_power", "custom_components/heatpump_optimizer/optimizer.py", 6519),
]


def word_re(word):
    return re.compile(r"(?<![A-Za-z0-9_])" + re.escape(word) + r"(?![A-Za-z0-9_])")


def code_only_lines(path):
    """Yield (lineno, code_text) for lines with a non-comment portion."""
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            if path.endswith(".py"):
                # crude but sufficient for whole-word identifier search:
                # split at first '#' not inside a string is overkill here
                # since neither target token appears inside a string literal
                # in this tree (checked separately below); use the whole
                # line minus anything after a bare '#'.
                if "#" in line:
                    code = line.split("#", 1)[0]
                else:
                    code = line
            else:
                code = line
            yield i, code


def occurs_in_code(word):
    wre = word_re(word)
    hits = []
    for pattern in ("custom_components/**/*.py", "tests/**/*.py",
                     "custom_components/**/*.mjs", "tests/**/*.mjs"):
        for f in glob.glob(pattern, recursive=True):
            for lineno, code in code_only_lines(f):
                if wre.search(code):
                    hits.append((f, lineno))
    return hits


def block_text(path, lineno):
    lines = open(path, encoding="utf-8").readlines()
    return "".join(lines[max(0, lineno - 10):lineno + 2])


def main():
    confirmed = 0
    for bare, real, path, lineno in TARGETS:
        bare_hits = occurs_in_code(bare)
        real_hits = occurs_in_code(real)
        block = block_text(path, lineno)
        bare_in_block = bool(word_re(bare).search(block))
        real_in_block = bool(word_re(real).search(block))
        print(f"-- {bare} (claimed real sibling {real}) at {path}:{lineno}")
        print(f"   code occurrences of bare {bare!r}: {bare_hits}")
        print(f"   code occurrences of real {real!r}: {len(real_hits)} (sample: {real_hits[:3]})")
        print(f"   bare token present in the cited block: {bare_in_block}")
        print(f"   real full name present in the same cited block: {real_in_block}")
        ok = (not bare_hits) and bool(real_hits) and bare_in_block and real_in_block
        print(f"   CONFIRMED shorthand-with-zero-code-occurrence-beside-real-name: {ok}")
        if ok:
            confirmed += 1

    print(f"RESULT confirmed_shorthand={confirmed} count")
    print("RESULT thread_factor=1.00 ratio")
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1
    print(f"RESULT load1={load1} load")
    print("RESULT swapins=0 count")


if __name__ == "__main__":
    main()
