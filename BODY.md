Triage batch 148 rules queue lines 241 and 242, both of which arrived after batch 147. It holds two rulings: P557, ACCEPT, and P558, DEFER.

- **P557, ACCEPT, a repair of an observed wrong behaviour: S14-BODY-PUSH-LANDED-MAIN-ONLY.** `body_push.sh`'s carry-landing check says "main's roster or the round's branch" (CARRY 11, P287), but it runs `carry_audit.py --roster-ref origin/main`, and `bus.sh` does the same. A carry already on the round branch is refused, and the relay's fold cannot clear it. `carry_audit.py landed` will accept either ref, the round branch being the one `roster_lib.default_roster_ref` names, and both callers drop the hard-coded ref. The fix is one carry to R10-PREPR-RESIDUE.
- **P558, DEFER: S14-CLOUD-PREPR-ENV-FAULTS.** One cloud fixer reported two `prepr.sh` faults. It is unverified by a second seat, and other cloud fixers that hour got past `prepr.sh`. A cloud probe running `prepr.sh` at origin/main that reproduces either fault would change it. The owning group is R10-SUITE-ENV.

The diff is one file against the merge base: `dev/programme/triage/s6-batch148.md`, the ruling. No product behaviour changes.

## Head

`7220463e18f9f9cf10fdfe5c9f9e24636a61233b`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- A citation of P557 passes `triage_refusal`.
- A citation of P558 is refused as "not an ACCEPT ruling (DEFER)".
- With P557's verdict flipped to REJECT, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P559 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat d08ed31049...7220463e18f9f9cf10fdfe5c9f9e24636a61233b`: 1 file.
- The blocked-fixer counts and the cloud faults are the sources' own figures, marked as such. The line numbers come from origin/main `d08ed31049`.

## Red checks

`none`. The merge base is main `d08ed31049`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
