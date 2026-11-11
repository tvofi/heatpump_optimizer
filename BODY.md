Triage batch 157 rules queue line 252. It holds one ruling: P569, DEFER on (a) and (c), with (b) a standing 600 s tick interval REJECTED.

- **P569, DEFER: S14-API-BUDGET-EXHAUSTED.**
  - The core bucket read 5000 used, 0 remaining, at 03:01Z, with the reset at 03:24:36Z.
  - The per-caller split the line asks for cannot be taken. The P284 `gh` shim is not installed in the seat bin directory, so there is no call log after 2026-11-09.
  - The `rate_limit` samples fit the baseline-plus-tick model up to 02:40Z: about 960 calls predicted, 979 read. After that they show at least about 2880 calls in 18 minutes that neither the baseline nor the tick explains.
  - The 120 s tick interval accounts for at most about 290 calls, so it was not the cause.
  - (a) the budget guard and (c) a second credential are deferred until one attributed window exists. (b) the tick returns to 300 s after the reset.
  - It adds no carry. The shim install is owed to the orchestrator as a local step.

The diff is one file against the merge base: `dev/programme/triage/s6-batch157.md`, the ruling. No product behaviour changes.

## Head

`43de04863de85700c0318f5036ad447b4a391fb0`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- A citation of P569 is refused as "not an ACCEPT ruling (DEFER)".
- With P569's verdict flipped to ACCEPT, the same citation passes `triage_refusal`.

## Null control

- P570 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat 444cf62fab...43de04863de85700c0318f5036ad447b4a391fb0`: 1 file, 1 commit.
- The bucket readings come from `gh api rate_limit`, which costs nothing against the bucket, and from the batch 155 sampler's 20 s log.
- The pass starts come from the `tick-loop.log` TICK-RELAY lines, and the job counts from the `beatd/journal.log` PASS lines.
- The line numbers come from origin/main `444cf62fab`.

## Red checks

`none`. The merge base is main `444cf62fab`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
