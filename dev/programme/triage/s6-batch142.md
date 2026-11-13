# Proposal triage, session s14, batch 142 (P546 to P547)

This batch rules `s7/triage-queue-s7.txt` lines 230 and 231. They arrived after batch 141.

The bar is batch 141's, at origin/main `d08ed31049`:
- **The rulings in force:** the owner's rulings of 2026-11-08, and P434's reading of severity.
- **The denominators**, all from batch 136: 29876 runner-min/day for CI time, 170.42 h for
  completion, and 55 PRs/day for right-first-time.

## P546: S14-DISPOSE-WIP-GAP, dead blocked-stop lines that no disposition clears

Verdict: ACCEPT, on the class-barrier route. Batch 141's P529 (BLOCKED-STOP-LANDED) was a REJECT
on 2 instances. Its premise no longer holds.

Source: queue line 230 (2026-11-11T00:19:39Z, the s14 handoff-drain seat).

Instances:
- **The refusal.** `cloud_relay.sh` `dispose()` (line 319 at main) refuses every ref outside
  `probe/`, `handoff/`, `handoff-body/` and `review/`. A `handoff-wip/` blocked-stop can therefore
  never be disposed.
- **The arms that follow from it.** The carry-fold arm reads no disposition. `bus.sh orphans` reads
  none either.
- **The count: 9 lines in all.**
  - 2 are from queue line 208 (P529): r10-rca-ci-critpath-3 and r10-round-playbook.
  - 7 are from this line: 7 of 9 stops whose work was already landed or superseded. They stood owed
    for 9 to 34 h.
  - That is past the third instance, so the class owes a barrier.
- **The cost of the gap.** Each dead line is an owed line that a sweep must act on every turn
  ("never ignore waiting work"), so dead lines dilute the board.

Cost:
- `dispose()` accepts `refs/heads/handoff-wip/` at a sha.
- The carry-fold arm and `bus.sh orphans` skip a tip disposed at that sha, and re-raise it when the
  tip moves, as `dispose` does today.
- Self-test arms, a null control (an undisposed `handoff-wip` stop still owes) and a mutant per
  reader.

Binding: one carry, R10-REVIEW-DISPATCH-RESIDUE (`cloud_relay.sh` and `bus.sh` are in its files),
from the file `b142-P546.txt`.

## P547: S14-OVERLAY-KEYS, the sweep renderer refuses the beat's overlay keys

Verdict: REJECT.

Source: queue line 231 (2026-11-11T00:26:14Z, the s14 orchestrator).

Instances:
- **The refusal.** `sweep_render.py` lines 16 to 21 refuse an overlay key that the template's
  `## Placeholders` table does not declare ("unknown").
- **The undeclared keys.** `beat_jobs.py` reads `train_log` (lines 423 and 618) and
  `plan_coordinator_cap`, and neither is declared.
- **The count.** 1 instance, worked around by rendering from a filtered copy of the overlay. It
  recurs at most once per sweep render at a session start, at a cost of minutes.

Binding: the measured cost is one filtered copy per session start, which is under 1 % on every
measure, against >20 %. Not built. The workaround, rendering from a copy without the beat-only keys,
stands.
