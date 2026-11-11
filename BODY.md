Triage batch 150 rules queue line 244, which arrived after batch 149. It holds one ruling: P561, ACCEPT.

- **P561, ACCEPT, a repair of an observed wrong behaviour: S14-TRAIN-ADD-NO-CARRY-AFTER-SKIP.**
  - The live train skipped PR 3386 red at `7628bb71`. A pure main merge (`b874260809`) then repaired it.
  - Neither `add` can bring it back. At the old verdict, `already_held` answers ALREADY, because a skip is keyed on the verdict alone. At the new head, `add_verdict` refuses because the posted verdict names `7628bb71`.
  - Both refusals were reproduced on the live `queue.seen.json`.
  - The proposal's fix site was `admit_add`, but that already carries an old verdict to a new head. The ruling moves the fix to `already_held`: a skip records its head, and a skip at the same verdict whose head has moved is admitted, for `admit_add`'s carry rule to decide.
  - It is one carry to R10-TRAIN-RESIDUE, as PART 2.

The diff is one file against the merge base: `dev/programme/triage/s6-batch150.md`, the ruling. No product behaviour changes.

## Head

`6ee00655b115120b14cd2fc0fc3873cc457e1fe2`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- A citation of P561 passes `triage_refusal`.
- With P561's verdict flipped to REJECT, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P562 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat 63bcdcaad8...6ee00655b115120b14cd2fc0fc3873cc457e1fe2`: 1 file.
- The skip and the seen record come from the live train's `train.log` line 19436 and its `queue.seen.json`.
- The line numbers come from origin/main `63bcdcaad8`.

## Red checks

`none`. The merge base is main `63bcdcaad8`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
