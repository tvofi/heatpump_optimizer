R10-REVIEW-DISPATCH-RESIDUE part 6. Carry 25: the handoff's brief-carries check demands only the indexes the dispatch PROMPT's part line assigns. Carry 24: a later-round design reviewer is given the round, the last verdict and the diff range. Carry 10: review_strength reads a string roster model as the fixer model.

## Head

1fe252f0d6e8590df6356163c1bdd93c8b9c58d0

## Mutation proof

Hand mutants, each applied to one file in place and restored, run against the file's own self-test at the head:

- Carry 25 drop part scope (`assigned or found or None` -> `found or None`): KILLED
- Carry 25 run end exclusive: KILLED
- Carry 25 run join (`+` runs not unioned): KILLED
- Carry 25 base text in the refusal dropped: KILLED
- Carry 25 NULL (replacement identical to the original): SURVIVED
- Carry 24 round context removed from the render: KILLED
- Carry 24 round count off by one: KILLED
- Carry 24 previous design sha read from the wrong token: KILLED
- Carry 24 verdict read narrowed back to the designer: KILLED
- Carry 10 string-model guard removed: KILLED
- Carry 10 dict key read broken: KILLED

## Null control

Red at the merge base (the arms present, the fix lines reverted), then green at the head:

- `python3 tools/audit/seat/review_packet.py --self-test`: 3 `FAIL P593 brief-carries` lines without the fix; `128 checks, 0 failed` with it. Null arm: no part line demands the prompt's whole `Carry N:` set, no prompt demands the live count.
- `python3 -I tools/audit/seat/cloud_dispatch.py --self-test`: 2 FAIL (round 2 and round 3 arms) without the fix; `172 checks, 0 failed` with it. Null arm: a first round (no design-verdict ref) renders no `This is round` text and no verdict commit.
- `python3 tools/audit/seat/review_strength.py --self-test`: NameError on `fixer_of` without the fix; `117 checks, 0 failed` with it. Null arm: the dict shape reads its fixer key, an empty dict and no group read `none`.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none

## Design notes

Carry 25 extends `prompt_carries` (the existing seam) with `part_carries`, which reads both part-line spellings: the hand `This part: Carries <list> (0-based roster indexes` and the generated `Part k of N: build carries <runs>`. I did not build the roster-at-dispatch-time base (`rev-list -1 --before`): the dispatch PROMPT already holds the carries the part was dispatched with, so a carry appended later cannot be demanded; the refusal names its base as the dispatch PROMPT's part line.
Carry 24 widens the existing verdict read in `dispatch_group` to the design reviewer and adds `round_context`; no flag, no new git read beyond `rev-list --count`.
Carry 10 extracts `fixer_of` from `pr_facts` so the guard is testable.
No role or policy file is edited.
