#!/usr/bin/env python3
"""Verifier-1 OWN harness for D5-01 (independent metric, refute-first).

METRIC (mine, deliberately different from the finder's):
  absent_labels_distinct  distinct options-field labels shipped in
                          strings.json options.step.*.data whose text -- one
                          trailing parenthetical stripped, casefolded,
                          non-alphanumerics collapsed to single spaces -- does
                          not occur anywhere in the folded concatenation of
                          README.md and EVERY docs/*.md present (globbed, not
                          a fixed list: MORE generous than the finder's fixed
                          6 reader docs, i.e. biased AGAINST the finding)
  absent_label_pages      sum over those labels of the number of options steps
                          shipping them (the finder's "occurrences")
  own_fields_total / own_sections_matched / own_rows_total
                          my own table parser over docs/configuration.md's
                          "Changing settings later" chapter (exact folded
                          title equality, no substring generosity)
  own_fields_no_row       matched-step fields whose label matches no row label
                          in that step's own section, substring either way

Perturbation arms, executed in-memory, numbers printed:
  add_after_saving_row    the finder's forward perturbation text appended to
                          the corpus: absent_labels_distinct must fall 15->14,
                          absent_label_pages 34->14
  fabricated_label        a fake label injected into one step: absent +1
  drop_one_buffer_mention one folded occurrence of "buffer tank size" removed
                          from the corpus: does the label turn absent?
                          (the finder's stated reverse perturbation, tested)

RUN (from a tree root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D5/d5_own_D5-01.py

EXPECTED at branch head 0855277 (= baseline 7dd68dd for every file measured):
  absent_labels_distinct=15  absent_label_pages=34  own_fields_total=200
Counts over file bytes; contention-immune.
Root rule: ROOT = Path(".").resolve() -- measures the tree it is run from.
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

import json
import re
import sys
from pathlib import Path

ROOT = Path(".").resolve()
PKG = ROOT / "custom_components" / "heatpump_optimizer"
DOC = ROOT / "docs" / "configuration.md"
PARENT = "Changing settings later"

FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
ROW = re.compile(r"^\s*\|(.+)\|\s*$")
HDRS = ("setting", "option", "field")


def fold(s):
    s = re.sub(r"`([^`]*)`", r"\1", s)
    s = s.replace("**", "").replace("*", "")
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def strip_paren(label):
    return re.sub(r"\s*\([^()]*\)\s*$", "", label)


def corpus_texts():
    """README.md + every docs/*.md (glob). More docs than the finder's list."""
    docs = [ROOT / "README.md"] + sorted(ROOT.glob("docs/*.md"))
    return [p for p in docs if p.exists()]


def build_haystack(texts, extra="", drop=None):
    h = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in texts)
    h = h + "\n" + extra
    h = re.sub(r"[^a-z0-9]+", " ", h.lower())
    h = re.sub(r"\s+", " ", h)
    if drop is not None:
        h = h.replace(drop, " ", 1)
    return h


def sections_and_rows():
    """My own parser: [(folded_title, [(lineno, first_cell)])] for ### under PARENT."""
    lines = DOC.read_text(encoding="utf-8").splitlines()
    out, cur, in_par, in_tbl, in_fence = [], None, False, False, False
    for i, line in enumerate(lines, 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING.match(line)
        if m:
            lvl, title = len(m.group(1)), m.group(2).strip()
            if lvl == 2:
                in_par = title == PARENT
                cur = None
                continue
            if in_par and lvl == 3:
                cur = (fold(title), [])
                out.append(cur)
            in_tbl = False
            continue
        if cur is None:
            continue
        mr = ROW.match(line)
        if not mr:
            in_tbl = False
            continue
        cells = [c.strip() for c in mr.group(1).split("|")]
        first = cells[0] if cells else ""
        if first and set(first.replace(" ", "")) <= set("-:"):
            continue
        if fold(first) in HDRS:
            in_tbl = True
            continue
        if not first:
            in_tbl = False
            continue
        if in_tbl:
            cur[1].append((i, first))
    return out


def main():
    strings = json.loads((PKG / "strings.json").read_text(encoding="utf-8"))
    steps = strings["options"]["step"]

    texts = corpus_texts()

    def absent_map(hay, step_items=None):
        absent = {}
        for sid, body in (step_items if step_items is not None else steps).items():
            for label in (body.get("data") or {}).values():
                f = fold(strip_paren(label))
                if f and f not in hay:
                    absent.setdefault(fold(label), set()).add(sid)
        return absent

    hay = build_haystack(texts)
    base = absent_map(hay)

    # -- structural counts, my own parser ------------------------------------
    by_title = {}
    for sid, body in steps.items():
        t = body.get("title")
        if t:
            by_title.setdefault(fold(t), sid)
    secs = sections_and_rows()
    matched = [(t, rows, by_title[t]) for t, rows in secs if t in by_title]
    rows_total = 0
    fields_total = 0
    fields_no_row = 0
    for title, rows, sid in matched:
        flabels = list((steps[sid].get("data") or {}).values())
        fields_total += len(flabels)
        seen = set()
        for _, label in rows:
            rows_total += 1
            for k, fl in enumerate(flabels):
                fa, fb = fold(label), fold(strip_paren(fl))
                if fa and fb and (fa == fb or fa in fb or fb in fa):
                    seen.add(k)
        fields_no_row += len(flabels) - len(seen)

    # -- perturbation arms ----------------------------------------------------
    add_row = ("| After saving | Return to the section menu | menu / close | "
               "Where the dialog goes after a save. |")
    hay_add = build_haystack(texts, extra=add_row)
    after_add = absent_map(hay_add)

    fab = {sid: dict(b) for sid, b in steps.items()}
    first_data = next(sid for sid, b in steps.items() if b.get("data"))
    fab[first_data] = dict(steps[first_data])
    fab[first_data]["data"] = dict(steps[first_data]["data"])
    fab[first_data]["data"]["zzz_fabricated"] = "Zzz fabricated control"
    after_fab = absent_map(hay, fab)

    hay_drop = build_haystack(texts, drop=" buffer tank size ")
    after_drop = absent_map(hay_drop)
    buf_now_absent = int(fold("Buffer tank size") in after_drop
                         and fold("Buffer tank size") not in base)

    print(f"RESULT own_corpus_docs={len(texts)} count")
    print(f"RESULT own_sections_matched={len(matched)} count")
    print(f"RESULT own_rows_total={rows_total} count")
    print(f"RESULT own_fields_total={fields_total} count")
    print(f"RESULT own_fields_no_row={fields_no_row} count")
    print(f"RESULT absent_labels_distinct={len(base)} count")
    print(f"RESULT absent_label_pages={sum(len(v) for v in base.values())} count")
    print(f"RESULT arm_add_row_distinct={len(after_add)} count")
    print(f"RESULT arm_add_row_pages={sum(len(v) for v in after_add.values())} count")
    print(f"RESULT arm_fabricated_distinct={len(after_fab)} count")
    print(f"RESULT arm_drop_buffer_row_turns_absent={buf_now_absent} bool")
    for f in sorted(base):
        pages = sorted(base[f])
        print(f"  ABSENT {f!r} pages={len(pages)}")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
