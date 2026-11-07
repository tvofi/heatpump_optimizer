Triage batch 135 rules on queue line 98, the owner's CLOUD-SEAT-CHANNEL ask: one ruling, P424.

- **P424, ACCEPT narrowed: a silent-seat detector, not a channel.** The fix is a new group, R10-CLOUD-SEAT-CHANNEL. It adds one arm to `cloud_relay.sh` that owes `seat-silent` for any role's dispatch with no newer return ref after 60 min, keyed on the dispatch sha so a re-fire re-arms. The owner's named instance, f-3264-conflict, was a masking defect: the session-local watcher keyed QUIET on the ref name without its sha, so a re-fire of a QUIET topic never re-emitted. Part (1)'s beat refs are REJECTED, part (2) is DEFERRED on an orchestrator probe, and part (3) is REJECTED as a duplicate of R10-TICK-LEVELS carry 14 (P382).

The diff is one file against the merge base: `dev/programme/triage/s6-batch135.md`, the ruling. No product behaviour changes.

## Head

`9059cce917c4e4efa516a65cc57dc532f0bf95da`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads ACCEPT for P424.
- The group brief in the ruling's `Binding:` passes `triage_refusal`.
- With P424's verdict flipped to REJECT, the brief is refused as "not an ACCEPT ruling (REJECT)".

## Null control

P425 reads `None`. With the file absent, the brief is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat dee8b413f...9059cce917c4e4efa516a65cc57dc532f0bf95da`: 1 file.
- Every ruling figure is printed by the command the ruling names beside it.

## Red checks

`none`. The merge base is main `dee8b413f`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
