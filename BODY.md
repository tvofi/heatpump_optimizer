Triage batch 199 rules P623-P625 (queue lines 300, 301 and 303), 2026-11-11. It holds three rulings.

- **P623, REJECT (superseded): R10-FLY-CLOUD-FRUGAL-OFF.**
  - The owner directive of 2026-11-06 ("Drop the frugal change. Instead, have the seats use subagents as required", P398) is later than the 2026-11-04 ruling ("Turn it off in the cloud") and reverses it.
  - The roster already records the group as `refused`.
  - The owner applies no settings edit. The group's leftover refs are cleared by `prune_refs.py --topic`.
- **P624, REJECT widening `cloud_relay.sh dispose`; narrowed to the existing instrument.**
  - `carry_fold_arm` never reads `disposed`, so widening the case alone would not silence the line.
  - A dry `prune_refs.py --topic` run clears 3 of the 5 stale handoff-wip topics today.
  - It refuses the other 2 because their code refs carry content that is not on main. Those 2 keep the 12-hour ack until R10-CLOSEOUT-CLEANUP.
- **P625, ACCEPT narrowed (a): a carry onto R10-GH-READ-RESIDUE-P3.**
  - (a): route the ruleset reads (235 per hour from 120 processes, 4.7% of the bucket) through P3's conditional-read helper, built in `gh_read.py`.
  - (b) is DEFERRED to R10-GH-READ-RESIDUE's drain attribution.
  - (c) is REJECTED: it costs latency, and P3 item 1 already cuts the same tick reads.

The diff is one file against the merge base: `dev/programme/triage/s6-batch199.md`, the rulings. No product behaviour changes.

## Head

`44a99110761d0746165b0c3ba022044043b45681`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P625 as ACCEPT, and a citation of it passes (`None`).
- It reads P623 and P624 as REJECT, so a roster citation of either is refused.
- With P624's verdict text flipped, the citation stays refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P626 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat 60413046e3...44a99110761d0746165b0c3ba022044043b45681`: 1 file, 147 insertions, 1 commit. `tests/layout.py --guard`: 0 refusals.
- The figures come from:
  - the roster at `334095b9b6`;
  - dry `prune_refs.py --topic` runs over a 6791-ref ls-remote;
  - the shim call log for 12:25:00Z-13:25:30Z, 1557 lines.

## Red checks

none

## Forward-carry

none

## Friction

none
