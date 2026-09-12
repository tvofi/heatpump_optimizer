#!/usr/bin/env python3
"""D5 options-placement harness.

METRIC: agreement between `docs/configuration.md` -- the reference a user
configuring the integration reads -- and the options UI the integration actually
ships in `custom_components/heatpump_optimizer/strings.json`.

  sections_matched      `###` sections under "Changing settings later" whose
                        heading equals an options step's title
  sections_orphan       such a section whose heading matches no options step
  steps_undocumented    options steps with fields but no section of their own
  rows_total            setting-table rows in the matched sections
  rows_misplaced        a row whose label matches NO field label of the step the
                        section is about (it may exist on some other page: that
                        is still a dead end, because the reader opens the named
                        page and the setting is not on it)
  fields_undocumented   fields of a matched step with no row in that section
  fields_elsewhere      of those, the ones a setting row SOMEWHERE ELSE in
                        docs/configuration.md does describe (the "Initial setup"
                        walkthrough, or another page's table): a cross-reference,
                        not a gap
  fields_nowhere        of those, the ones no setting row anywhere in
                        docs/configuration.md describes -- the reader cannot find
                        the field, its default or its range at all
  fields_total          fields of all matched steps

  labels_absent_distinct / labels_absent_occurrences
                        EXACT arm, no fuzzy matching at all: an options field
                        label whose text does not occur, case-folded and
                        whitespace-normalised, anywhere in README.md or any
                        docs/*.md, after stripping one trailing parenthetical
                        ("(optional)", "(kW/°C)") which is a UI convention
                        rather than part of the name. The reader cannot find the
                        control by the name the UI gives it. Occurrences counts
                        it once per page it ships on.

Matching is deliberately generous -- case-folded, punctuation-stripped, either
string containing the other -- so the count is a floor on the real divergence.

RUN (from the export root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D5/options_placement.py
  ... --list      every misplaced row and undocumented field
  ... --selftest  positive control: the step->section mapping is rotated by one,
                  which must drive rows_misplaced to near rows_total

EXPECTED at baseline 7dd68dd (Apple M1, 8 core, macOS 25.6): see RESULT lines.
Counts over strings.json and docs/configuration.md; contention-immune.
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
SETTING_HDR = ("setting", "option", "field")


def fold(s):
    s = re.sub(r"`([^`]*)`", r"\1", s)
    s = s.replace("**", "").replace("*", "")
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def hit(a, b):
    fa, fb = fold(a), fold(b)
    if not fa or not fb:
        return False
    return fa == fb or fa in fb or fb in fa


def all_row_labels():
    """Every setting-table row label anywhere in docs/configuration.md."""
    lines = DOC.read_text(encoding="utf-8").splitlines()
    out, in_tbl, in_fence = [], False, False
    for i, line in enumerate(lines, 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        mr = ROW.match(line)
        if not mr:
            in_tbl = False
            continue
        cells = [c.strip() for c in mr.group(1).split("|")]
        first = cells[0] if cells else ""
        if first and set(first.replace(" ", "")) <= set("-:"):
            continue
        if fold(first) in SETTING_HDR:
            in_tbl = True
            continue
        if not first:
            in_tbl = False
            continue
        if in_tbl:
            out.append((i, first))
    return out


def doc_sections():
    """-> [(title, [(lineno, row_label)])] for each ### under PARENT."""
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
                cur = (title, [])
                out.append(cur)
                in_tbl = False
                continue
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
        if fold(first) in SETTING_HDR:
            in_tbl = True
            continue
        if not first:
            in_tbl = False
            continue
        if in_tbl:
            cur[1].append((i, first))
    return out


READER_DOCS = ["README.md"] + [f"docs/{n}" for n in
               ("architecture.md", "automations.md", "configuration.md",
                "dashboard-card.md", "ecl110.md", "how-it-works.md")]


def doc_haystack():
    t = []
    for d in READER_DOCS:
        p2 = ROOT / d
        if p2.exists():
            t.append(p2.read_text(encoding="utf-8", errors="replace"))
    h = "\n".join(t)
    h = re.sub(r"[^a-z0-9]+", " ", h.lower())
    return re.sub(r"\s+", " ", h)


def main():
    listing = "--list" in sys.argv
    rotate = "--selftest" in sys.argv
    strings = json.loads((PKG / "strings.json").read_text(encoding="utf-8"))
    steps = strings["options"]["step"]
    by_title = {}
    for sid, body in steps.items():
        t = body.get("title")
        if t:
            by_title.setdefault(fold(t), (sid, body))

    secs = doc_sections()
    if rotate:
        ids = [s for s in steps if steps[s].get("data")]
        rot = {ids[i]: ids[(i + 1) % len(ids)] for i in range(len(ids))}
        by_title = {k: (rot.get(v[0], v[0]), steps[rot.get(v[0], v[0])])
                    for k, v in by_title.items()}

    matched, orphan = [], []
    for title, rows in secs:
        key = fold(title)
        if key in by_title:
            matched.append((title, rows, *by_title[key]))
        else:
            orphan.append(title)

    used_ids = {sid for _, _, sid, _ in matched}
    undocumented_steps = [
        sid for sid, b in steps.items() if b.get("data") and sid not in used_ids
    ]

    everywhere = all_row_labels()
    rows_total = rows_bad = fields_total = fields_bad = 0
    bad_rows, bad_fields = [], []
    for title, rows, sid, body in matched:
        flabels = list((body.get("data") or {}).values())
        fkeys = list((body.get("data") or {}).keys())
        fields_total += len(flabels)
        seen = set()
        for ln, label in rows:
            rows_total += 1
            # A single row may legitimately cover several fields ("Hot water
            # tank, buffer tank, floor return, lower floor sensors"), so every
            # field it matches counts as documented, not just the first.
            hits = [k for k, fl in enumerate(flabels)
                    if hit(label, fl) or hit(label, fkeys[k])]
            if not hits:
                rows_bad += 1
                bad_rows.append((title, sid, ln, label))
            else:
                seen.update(hits)
        for k, fl in enumerate(flabels):
            if k not in seen:
                fields_bad += 1
                anywhere = any(hit(lbl, fl) or hit(lbl, fkeys[k])
                               for _, lbl in everywhere)
                bad_fields.append((title, sid, fkeys[k], fl, anywhere))

    hay = doc_haystack()
    absent = {}
    for sid, body in steps.items():
        for key, label in (body.get("data") or {}).items():
            # A trailing parenthetical is a UI convention ("(optional)",
            # "(kW/°C)"), not part of the name a document would use, so it is
            # stripped before the exact test.
            f = fold(re.sub(r"\s*\([^()]*\)\s*$", "", label))
            if f and f not in hay:
                absent.setdefault(label, []).append(sid)

    if listing:
        print("== field labels that occur in no reader document ==")
        for label in sorted(absent):
            print(f"  LABEL-ABSENT {label!r}  on {len(absent[label])} page(s): "
                  f"{', '.join(absent[label])}")
        print("== sections with no options step of that title ==")
        for t in orphan:
            print(f"  ORPHAN-SECTION {t!r}")
        print("== options steps with fields and no section ==")
        for sid in undocumented_steps:
            print(f"  UNDOCUMENTED-STEP {sid} {steps[sid].get('title')!r} "
                  f"({len(steps[sid]['data'])} fields)")
        print("== rows not on the page the section is about ==")
        for title, sid, ln, label in bad_rows:
            print(f"  MISPLACED-ROW docs/configuration.md:{ln} [{title} -> {sid}] {label!r}")
        print("== shipped fields with no row in that section ==")
        for title, sid, key, fl, anywhere in sorted(bad_fields, key=lambda r: r[4]):
            tag = "ELSEWHERE" if anywhere else "NOWHERE"
            print(f"  UNDOCUMENTED-FIELD-{tag} [{title} -> {sid}] {key} = {fl!r}")

    print(f"RESULT sections_matched={len(matched)} count")
    print(f"RESULT sections_orphan={len(orphan)} count")
    print(f"RESULT steps_undocumented={len(undocumented_steps)} count")
    print(f"RESULT rows_total={rows_total} count")
    print(f"RESULT rows_misplaced={rows_bad} count")
    print(f"RESULT fields_total={fields_total} count")
    print(f"RESULT fields_undocumented={fields_bad} count")
    print(f"RESULT fields_elsewhere={sum(1 for r in bad_fields if r[4])} count")
    print(f"RESULT fields_nowhere={sum(1 for r in bad_fields if not r[4])} count")
    print(f"RESULT labels_absent_distinct={len(absent)} count")
    print(f"RESULT labels_absent_occurrences={sum(len(v) for v in absent.values())} count")
    print(f"RESULT labels_checked={sum(len(b.get('data') or {}) for b in steps.values())} count")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
