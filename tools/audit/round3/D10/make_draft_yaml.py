#!/usr/bin/env python3
"""Emit tools/audit/round3/D10/quality_scale.draft.yaml from rule_table.tsv.

    python3 tools/audit/round3/D10/make_draft_yaml.py

Run qs_register.py first (it writes rule_table.tsv). Every comment in the
output is the evidence string the corresponding check returned, so the draft
carries its own provenance and nothing in it is asserted by hand.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = ROOT / "tools/audit/round3/D10"
rows = [l.split("\t") for l in
        (HERE / "rule_table.tsv").read_text(encoding="utf-8").splitlines()[1:]]

HEAD = """# Home Assistant integration quality scale -- rule-by-rule register.
# DRAFT produced by audit round 3, dimension D10, at baseline
# ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1. Every status below is the verdict
# of an executed check in tools/audit/round3/D10/, and every comment is that
# check's own evidence string, not prose. Regenerate with:
#   PYTHONPATH=tests/hastub python3 tools/audit/round3/D10/qs_register.py
#   python3 tools/audit/round3/D10/make_draft_yaml.py
#
# The checklist is the 54 rules fetched 2026-09-10 from
# https://developers.home-assistant.io/docs/core/integration-quality-scale/checklist
# (20 Bronze, 10 Silver, 21 Gold, 3 Platinum).
#
# hassfest skips this file for custom integrations, so nothing here is
# machine-enforced, and nothing under tests/ reads it either. qs_register.py
# is what re-derives it: it prints `register_divergences` and a `<-- DIVERGES`
# row for every status the tree contradicts. Wiring that number into the gate
# is what would stop this file going stale again; today nothing does.
rules:
"""

TIER_TITLE = {"bronze": "Bronze", "silver": "Silver", "gold": "Gold",
              "platinum": "Platinum"}


def wrap(text: str, width: int = 72) -> list[str]:
    words, line, out = text.split(), "", []
    for w in words:
        if len(line) + len(w) + 1 > width:
            out.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    if line:
        out.append(line)
    return out


def main() -> int:
    body, seen = [], set()
    for rule, tier, claimed, measured, evidence in rows:
        if tier not in seen:
            body.append(f"  # {TIER_TITLE[tier]}")
            seen.add(tier)
        note = evidence
        if claimed != measured and measured != "unmeasured":
            note += f" [the shipped register says `{claimed}`]"
        lines = wrap(note)
        if len(lines) == 1 and len(lines[0]) < 60 and measured == "done" and claimed == measured:
            body.append(f"  {rule}: {measured}")
        else:
            body.append(f"  {rule}:")
            body.append(f"    status: {measured}")
            body.append("    comment: >-")
            body.extend(f"      {l}" for l in lines)
    out = HEAD + "\n".join(body) + "\n"
    (HERE / "quality_scale.draft.yaml").write_text(out, encoding="utf-8")
    counts = {}
    for _, _, _, measured, _ in rows:
        counts[measured] = counts.get(measured, 0) + 1
    print("RESULT draft_rules=%d count" % len(rows))
    for k in sorted(counts):
        print(f"RESULT draft_{k}={counts[k]} count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
