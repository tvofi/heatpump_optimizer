#!/usr/bin/env python3
"""Two roster ops roster_edit.py lacks, run through its own flow (same JSON
load/dump, branch worktree, brief_lint gate, --push) by rebinding the op it
dispatches to for 'append-carry' and 'edit-brief':

  drop-carry <group> <unique-prefix>     append-carry slot: removes the ONE carry entry that
                                         starts with <prefix>; refuses 0 or >1 matches
  set-owner-gate <group> <text | @file>  edit-brief slot: sets group.owner_gate

Usage: ci_prep_edit.py drop-carry|set-owner-gate <roster_edit args as for append-carry/edit-brief>
"""
import sys
from pathlib import Path
SEAT = "/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat"
sys.path.insert(0, SEAT)
import roster_edit as R  # noqa: E402


def drop_carry(roster, group, prefix):
    g = R._need(roster, group)
    hit = [i for i, c in enumerate(g.get("carry") or []) if c.startswith(prefix)]
    if len(hit) != 1:
        raise R.Refuse(f"{group}: prefix matches {len(hit)} carry entries (need exactly 1): {prefix[:60]!r}")
    print(f"dropping {group} carry[{hit[0]}]: {g['carry'][hit[0]][:80]!r}")
    del g["carry"][hit[0]]


def set_owner_gate(roster, group, text):
    R._need(roster, group)["owner_gate"] = R._text(text)


def main():
    op, rest = sys.argv[1], sys.argv[2:]
    if op == "drop-carry":
        R.op_append_carry = drop_carry
        rest = ["append-carry"] + rest
    elif op == "set-owner-gate":
        R.op_edit_brief = set_owner_gate
        rest = ["edit-brief"] + rest
    else:
        raise SystemExit("op is drop-carry or set-owner-gate")
    sys.exit(R.main(rest))


main()
