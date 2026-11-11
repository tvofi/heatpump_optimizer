Triage batch 156 rules queue line 251, which arrived after batch 155. It holds one ruling: P568, ACCEPT.

- **P568, ACCEPT, a repair of an observed wrong behaviour: S14-PACKET-REFUSES-DEFERRAL-RED.**
  - `merge_train.py classify` reads WAIT at PR 3404's and PR 3429's heads beside concluded-red edit-run gates. The review packet still refused both dispatches as `red-unanswered`, and 14 dispatch outputs hold that refusal on `gate`.
  - The packet already gathers that classify answer (line 602), and its `required-red` arm defers to it. The `red-unanswered` arm (lines 542-543) does not.
  - The fix: a required red that the gathered read calls WAIT or GREEN gets its existing advisory and no `red-unanswered` refusal. It adds no second classify read.
  - It is one carry to R10-REVIEW-DISPATCH-RESIDUE.

The diff is one file against the merge base: `dev/programme/triage/s6-batch156.md`, the ruling. No product behaviour changes.

## Head

`5385d9866add4b145b83be5261f6d2e363fcfc04`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- A citation of P568 passes `triage_refusal`.
- With P568's verdict flipped to REJECT, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P569 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat 444cf62fab...5385d9866add4b145b83be5261f6d2e363fcfc04`: 1 file.
- The classify readings come from `merge_train.py classify <head> --pr <n>`.
- The refusal count comes from `grep -rlF` over the state directory.
- The line numbers come from origin/main `444cf62fab`; `review_packet.py` is unchanged from `63bcdcaad8`.

## Red checks

`none`. The merge base is main `444cf62fab`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
