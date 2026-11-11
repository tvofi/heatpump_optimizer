Triage batch 170 rules two process proposals filed by seat s14-12 on 2026-11-11, both about PR 3425.

- **P585, ACCEPT, re-pointed: PENDING-CI-RED-TERMINAL.**
  - The proposed arm (relay a pending-ci draft across a moved head when `review_carry` answers CARRY) is already carried by P576, so that part is a duplicate.
  - The measured cost is the RED arm, `cloud_relay.sh:273`. Both of its refusals in the tick-loop log, for PRs 3425 and 3430, were reds that cleared with no fixer work, and both drafts are stranded in `cloud-relayed.refused`.
  - The ruling adds a carry to R10-REVIEW-DISPATCH-RESIDUE, built with P576. RED holds the draft, as WAIT does. It refuses only on a non-CARRY head move or after 6 h of settled red, and it then prints an OWED re-dispatch line.
- **P586, REJECT: CARRY-FOLD-PR-SPELLING.** 0 of 8 replays differ between `--pr 3425` and `--pr '#3425'`. The 1 missing the proposer saw was the bus's run at 03:37Z, an hour before the carry landed.

The diff is one file against the merge base: `dev/programme/triage/s6-batch170.md`, the ruling. No product behaviour changes.

## Head

`06c20be33aaee00839468e50eee94d7d5a750b31`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P585 as ACCEPT and P586 as REJECT, and a citation of P585 passes (`None`).
- A citation of P586 is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P587 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat a7628041dc...06c20be33aaee00839468e50eee94d7d5a750b31`: 1 file, 1 commit.
- The figures are static reads at main `a7628041dc`, plus the tick-loop log and check-runs at `c6becb3175`, `c93903f075` and `ba0ed526cc`. Each one is cited beside its command in the ruling.

## Red checks

`governance / instrument-self-tests` is red at the merge base `a7628041dc`. That red is main's own (P584), and this one-file record does not touch it.

## Forward-carry

none

## Friction

none
