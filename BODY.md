Triage batch 204 rules P634 and P635 (queue line 312 and its P631 datum), 2026-11-11. It holds two rulings.

- **P634, ACCEPT narrowed, as a carry on R10-TICK-RESIDUE-P3: verdict_audit.py drops every `FIRED <utc>` fire-ledger line.**
  - `recent_lines` matches its stamp at column 0, while 71 of the last 300 ledger lines lead with `FIRED`.
  - The beat now prints a false `UNHELD #3464` beside a 12:48Z reviewer fire.
  - Promoting the local RED-UNOWNED arm is DEFERRED until its true positives are counted.
- **P635, DEFER, narrowed: the P631 orphans' launcher is identified.**
  - The launcher is `r10_roster_ops_mutants.target_self_test`, which has no `timeout=`, run from a copy-tree harness.
  - If a second instance comes, the countermeasure is one bound at that call site.

The diff is one file against the merge base: `dev/programme/triage/s6-batch204.md`, the rulings. No product behaviour changes.

## Head

`bde6e63e84d587212a86c93e82569d28ad36d08f`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P634 as ACCEPT, and a citation of it passes (`None`).
- A citation of P635 is refused as "not an ACCEPT ruling (DEFER)".
- With P634's verdict text flipped, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P636 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat` over the merge base: 1 file, 1 commit.
- The figures come from:
  - the fire ledger named by the beat's `sweep-overlay.json`;
  - the beat's verdict-audit output at 14:45Z;
  - `git grep` at origin/main.

## Red checks

none

## Forward-carry

none

## Friction

none
