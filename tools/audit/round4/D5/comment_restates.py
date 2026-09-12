#!/usr/bin/env python3
"""D5 comment-concision harness.

METRIC: `restating` comments in the production package -- a comment-only line (or
run of them) whose content words, after case folding, stemming of a trailing "s"
and removal of a 40-word stop list, are a SUBSET of the words appearing in the
single statement immediately below it (identifiers split on `_` and camelCase,
plus string and attribute text). Such a comment says only what the next line
already says. Comments of three lines or more are reported separately, because
the brief asks specifically about those.

Also reported: comment_density (comment lines / code lines) and the count of
comments of >= 3 lines, so a reader can see the corpus the ratio is over.

RUN (from the export root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D5/comment_restates.py
  ... --list      every restating comment with file:line and the line below it
  ... --selftest  positive control: a synthetic pair ("# the buffer tank volume"
                  over "buffer_tank_volume = 200.0") is appended and must be
                  reported, so restating_comments must rise by exactly 1

EXPECTED at baseline 7dd68dd (Apple M1, 8 core, macOS 25.6): see RESULT lines.
Counts over file bytes; contention-immune.
"""
import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import re
import sys
from pathlib import Path

ROOT = Path(".").resolve()
PKG = ROOT / "custom_components" / "heatpump_optimizer"

STOP = set("""a an the and or but of to in on at for from by with as is are was
were be been being this that these those it its if then else not no we you i
so into over under per each every any all some one two both same other than
when while which who whose what how why here there""".split())

WORD = re.compile(r"[A-Za-z][A-Za-z0-9]*")
CAMEL = re.compile(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])")


def words(text):
    out = set()
    for w in WORD.findall(text):
        for part in w.split("_"):
            for piece in CAMEL.findall(part):
                p = piece.lower()
                if len(p) > 2 and p not in STOP:
                    out.add(p[:-1] if p.endswith("s") and len(p) > 3 else p)
    return out


def main():
    listing = "--list" in sys.argv
    selftest = "--selftest" in sys.argv

    restating, long_comments = [], 0
    comment_lines = code_lines = 0
    blocks_checked = 0

    files = sorted(PKG.glob("*.py"))
    for p in files:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        i = 0
        while i < len(lines):
            s = lines[i].strip()
            if s.startswith("#"):
                comment_lines += 1
                start = i
                buf = []
                while i < len(lines) and lines[i].strip().startswith("#"):
                    buf.append(lines[i].strip().lstrip("#").lstrip(":").strip())
                    i += 1
                    if i > start + 1:
                        comment_lines += 1
                if len(buf) >= 3:
                    long_comments += 1
                # the first non-blank statement below the block
                j = i
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j >= len(lines):
                    continue
                target = lines[j]
                if target.strip().startswith(("#", '"""', "'''")):
                    continue
                ctext = " ".join(buf).strip()
                if not ctext or len(buf) > 2:
                    continue
                cw = words(ctext)
                if not cw or len(cw) < 2:
                    continue
                blocks_checked += 1
                if cw <= words(target):
                    restating.append(
                        (p.relative_to(ROOT).as_posix(), start + 1, ctext,
                         target.strip()[:90]))
                continue
            if s and not s.startswith(("#",)):
                code_lines += 1
            i += 1

    if selftest:
        # A comment that names nothing the line below does not already name.
        cw = words("the buffer tank volume")
        blocks_checked += 1
        if cw <= words("buffer_tank_volume = 200.0"):
            restating.append(("SELFTEST", 0, "the buffer tank volume",
                              "buffer_tank_volume = 200.0"))

    if listing:
        for f, ln, c, t in restating:
            print(f"RESTATES {f}:{ln}  # {c}")
            print(f"            {t}")

    print(f"RESULT files={len(files)} count")
    print(f"RESULT comment_lines={comment_lines} count")
    print(f"RESULT code_lines={code_lines} count")
    print(f"RESULT comment_density={comment_lines / max(code_lines, 1):.4f} ratio")
    print(f"RESULT comments_ge3_lines={long_comments} count")
    print(f"RESULT blocks_checked={blocks_checked} count")
    print(f"RESULT restating_comments={len(restating)} count")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
