Triage batch 189 rules P611 (queue line 289, cloud fixers stopping between a code handoff and a pushed body), 2026-11-11. It holds one ruling, and records that P610's text reached the seat in its brief, not the queue file.

- **P611, ACCEPT narrowed: CLOUD-STOP-BEFORE-BODY, as a new group R10-RELAY-NOBODY-STALL** (S, `cloud_relay.sh`, after R10-RELAY-ARM-ORDER).
  - Over 2026-11-04 to 11-11, 124 of 628 fixer fires (19.7%) returned code without a body. 113 of them were re-fired, a median 174-196 min after the stalled fire.
  - (a) The fold arm already exists (`67a823c2e7`). Its column-0 regex (`:819`) missed 3 of the 8 CARRY-LANDED blocks, r10-standing-contracts-p2 among them. Fix: accept indented refusal lines.
  - (b) The owed line triggers at 60 min, not 25. Healthy fires take a median of 10 min from the last code commit to the body, p75 28 and p90 48.
  - (c) is rejected: it duplicates (a), and it would make a cloud fixer a roster writer.
  - The class owes a root-cause seat. 3 of today's 4 stops left no BLOCKED.md.

The diff is one file against the merge base: `dev/programme/triage/s6-batch189.md`, the ruling. No product behaviour changes.

## Head

`f31dd067657d3730b2696c69ad0a970f15359343`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P611 as ACCEPT, and a citation of it passes (`None`).
- With the verdict flipped to REJECT in the file text, the P611 citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P612 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat ee64358be7...f31dd067657d3730b2696c69ad0a970f15359343`: 1 file, 1 commit.
- The figures come from the `dispatch/fixer-*`, `handoff/*`, `handoff-body/*` and `handoff-wip/*` refs fetched at 11:37Z, the relay's `tick-loop.log` and `cloud-folded`, and `cloud_relay.sh` and `ledger.py` at `ee64358be7`, as cited in P611.

## Red checks

none

## Forward-carry

none

## Friction

none
