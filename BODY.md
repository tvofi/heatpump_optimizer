Triage batch 128 rules on one queue line, P399, `s12-fire-without-sources`.

**P399: ACCEPT narrowed**, to R10-POLICY-ROLE-PACK.

- **The incident:** 7 cloud fires after a compaction carried no `session_context.sources`. They lost 342.7 seat-minutes (5.7 h), each lost 15.2 to 86.8 min, and the measure is ledger refire time minus first fire time.
- **The rate:** they are 2.0 % of the 342 fires in the ledger since 10-31.
- **The renderer already exists:** `cloud_dispatch.py` already renders and self-tests the full body.
- **The form:** the check is a PreToolUse hook on `RemoteTrigger`, not a `cloud_fire.py` renderer that the orchestrator would have to remember to call.
- **Review:** the hook files are code-owned, so the fix PR needs the owner's review or a mandate.

The diff is one file against the merge base: `dev/programme/triage/s6-batch128.md`, the ruling. No product behaviour changes.

## Head

`17a48e8e8c1f0b0b086da7b455f1b4e29e87af56`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`. `ruling_verdict` reads P399 `ACCEPT`, and the Binding carry text passes `triage_refusal`. With the verdict flipped to REJECT, the same carry is refused as "not an ACCEPT ruling (REJECT)".

## Null control

P400 reads `None`, and a carry citing it is refused as "no such entry". With the file absent, the carry is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat f2a015142...17a48e8e8c1f0b0b086da7b455f1b4e29e87af56`: 1 file.
- Every ruling figure is printed by the ledger command the ruling names beside it.
- No capped file is touched.

## Red checks

`none`. The merge base is main `f2a015142`. This head's checks run after its push.

## Forward-carry

none

## Friction

none
