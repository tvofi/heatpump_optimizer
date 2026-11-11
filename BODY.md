Triage batch 180 rules queue line 278, 2026-11-11. It holds one ruling.

- **P599, REJECT: MUTATION-VACUOUS-DIFF-PASS-REFUSE.**
  - Arm (a), measured over the last 20 fixer handoff bodies: 2/20 ran `mutant_run.py --diff`, 7/20 hand-built `--spec` mutants, 11/20 carry no mutant evidence, and `MUTANT_CMD` is set in 0/20.
  - Arm (b) is refused on reach. Over 24 h the class blocked 7 PRs (10 head-blocks, 17 named sites). The generator reaches 2-3 of the 17 sites, because 9 are shell, YAML or `tests/`. It would have prevented 1 of the 7 blocks, which is 3% of the 33 reviewed PRs, against the claimed 35%.
  - The step would cost 40-160 s per handoff at cap 40, at about 6% precision (47 survivors against 3 real sites, from P577).
  - This repeats P577 with two new heads, 3423 and 3448, and neither is reachable.

The diff is one file against the merge base: `dev/programme/triage/s6-batch180.md`, the ruling. No product behaviour changes.

## Head

`f6e8c00eb98a47fc2f99671f08c4c1292d2ab6be`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads P599 as REJECT.
- A citation of P599 is refused as "not an ACCEPT ruling (REJECT)", so no carry can cite it.

## Null control

- P600 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat cbd23f1c8b...f6e8c00eb98a47fc2f99671f08c4c1292d2ab6be`: 1 file, 1 commit.
- The figures come from three sources:
  - `review_strength.py --by class` over the window 2026-11-10T09:00Z..2026-11-11T09:30Z;
  - the `origin/verdict/*` subjects;
  - grep counts on the 20 newest `origin/handoff-body/r10-*` BODY.md files.

  Each is cited beside its command in the ruling.

## Red checks

none

## Forward-carry

none

## Friction

none
