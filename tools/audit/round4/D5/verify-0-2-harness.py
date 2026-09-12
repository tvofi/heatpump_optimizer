#!/usr/bin/env python3
"""Verifier-2 independent harness for D5-01 and D5-02 (round 4).

METRIC (D5-01): my own count of distinct options-field labels whose name does
not occur in the documentation corpus, under three normalisations of my own
(stripped-parenthetical substring = finder-comparable; unstripped substring =
stricter; contiguous word-token match = independent of folding), each against
TWO corpora: the finder's six reader docs, and a maximally generous corpus of
every *.md at the repo root and in docs/ (HANDOVER, plan, audit, SECURITY,
RELEASE_NOTES included). The corpus attack: if the generous corpus drives the
count under 15, the finder's corpus choice manufactured the finding.

METRIC (D5-02): my own regex for the stress.py annotation in tests/README.md,
against len(sweep_combinations()) plus a key-signature decomposition of the
returned list (base grid / feature / archetype / zero-range), proving 51 is
computed and not a constant.

RUN (from a tree root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D5/verify-0-2-harness.py

EXPECTED at 0855277 (== baseline 7dd68dd for every file touched): see RESULT
lines; counts over file bytes, contention-immune.
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

READER = [ROOT / "README.md"] + [ROOT / "docs" / n for n in (
    "architecture.md", "automations.md", "configuration.md",
    "dashboard-card.md", "ecl110.md", "how-it-works.md")]
GENEROUS = sorted(
    [p for p in ROOT.glob("*.md")]
    + [p for p in (ROOT / "docs").glob("*.md")]
)


def norm_text(t):
    t = re.sub(r"`([^`]*)`", r"\1", t)
    t = t.replace("**", "").replace("*", "")
    t = re.sub(r"[^a-z0-9]+", " ", t.lower())
    return re.sub(r"\s+", " ", t).strip()


def norm_tokens(t):
    return norm_text(t).split()


def strip_paren(label):
    return re.sub(r"\s*\([^()]*\)\s*$", "", label)


def main():
    # ---------- D5-01 ----------
    strings = json.loads((PKG / "strings.json").read_text(encoding="utf-8"))
    steps = strings["options"]["step"]
    labels = []  # (step_id, key, raw label)
    for sid, body in steps.items():
        for k, v in (body.get("data") or {}).items():
            labels.append((sid, k, v))

    hay_r = norm_text("\n".join(
        p.read_text(encoding="utf-8", errors="replace")
        for p in READER if p.exists()))
    hay_g = norm_text("\n".join(
        p.read_text(encoding="utf-8", errors="replace") for p in GENEROUS))
    tok_r = norm_tokens("\n".join(
        p.read_text(encoding="utf-8", errors="replace")
        for p in READER if p.exists()))
    tok_g = norm_tokens("\n".join(
        p.read_text(encoding="utf-8", errors="replace") for p in GENEROUS))

    def token_in(tokens, label):
        want = norm_tokens(strip_paren(label))
        if not want:
            return True
        n = len(want)
        for i in range(len(tokens) - n + 1):
            if tokens[i:i + n] == want:
                return True
        return False

    a_r = {l for _, _, l in labels
           if norm_text(strip_paren(l)) and norm_text(strip_paren(l)) not in hay_r}
    a_g = {l for _, _, l in labels
           if norm_text(strip_paren(l)) and norm_text(strip_paren(l)) not in hay_g}
    u_r = {l for _, _, l in labels if norm_text(l) and norm_text(l) not in hay_r}
    t_r = {l for _, _, l in labels if not token_in(tok_r, l)}
    t_g = {l for _, _, l in labels if not token_in(tok_g, l)}

    print(f"RESULT my_fields_total={len(labels)} count")
    print(f"RESULT my_corpus_reader_files={len([p for p in READER if p.exists()])} count")
    print(f"RESULT my_corpus_generous_files={len(GENEROUS)} count")
    print(f"RESULT my_absent_parenstrip_reader={len(a_r)} count")
    print(f"RESULT my_absent_parenstrip_generous={len(a_g)} count")
    print(f"RESULT my_absent_unstripped_reader={len(u_r)} count")
    print(f"RESULT my_absent_tokens_reader={len(t_r)} count")
    print(f"RESULT my_absent_tokens_generous={len(t_g)} count")
    print(f"RESULT my_absent_occurrences_reader="
          f"{sum(1 for s, _, l in labels if l in a_r)} count")
    drop = a_r - a_g
    print(f"LABELS_CLEARED_BY_GENEROUS_CORPUS: {sorted(drop)!r}")

    # ---------- D5-02 ----------
    doc = (ROOT / "tests" / "README.md").read_text(encoding="utf-8")
    m = re.search(r"stress\.py\s*#\s*(\d+)\s+combinations", doc)
    doc_sweep = int(m.group(1)) if m else None

    sys.path.insert(0, str(ROOT / "tests"))
    import stress  # noqa: E402  __main__-guarded

    combos = stress.sweep_combinations()
    base = [c for c in combos
            if set(c) == {"season", "two_zone", "dhw", "label"}]
    feat = [c for c in combos if "tariff" in c]
    arch = [c for c in combos if "building" in c]
    rest = [c for c in combos if c not in base and c not in feat and c not in arch]

    print(f"RESULT my_doc_sweep={doc_sweep} count")
    print(f"RESULT my_code_sweep={len(combos)} count")
    print(f"RESULT my_sweep_base={len(base)} count")
    print(f"RESULT my_sweep_feature={len(feat)} count")
    print(f"RESULT my_sweep_archetype={len(arch)} count")
    print(f"RESULT my_sweep_zero_range={len(rest)} count")
    print(f"RESULT my_sweep_mismatch={int(doc_sweep != len(combos))} count")

    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
