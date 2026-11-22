Root-cause record `dev/audit/rca/R11-RCA-MODEX.md` beside #3735 (R11-SEAM-ratchet-raise). It lands the record alone, no code and no policy file. The record's cause: `tests/structure.py` `ratchet()` compares each measure with the table's absolute value, so a branch carrying a row that main's table does not carry (here `module_excess_loc`) is judged against a record taken at an older main. Each bot merge of main carries main's own movement of the measure into the PR (21549 to 21779 over four days, none of it #3735's), and each instance costs a seat-authored `--record --allow-regression` commit that moves the head again. Process state (d): the process was sound and its precondition, that every row in a branch's table is a row main enforces, changed underneath it. Cost: 6 occurrences in 10 days on one PR, 7.18 PR-hours red, 12 red `CI code` runs, about 7.1 runner-hours per occurrence; the class's third reported instance (#3736, #3616, #3737 with #3728). Countermeasure: a local overlay prototype, `r11/proto/RCA-MODEX`, that judges a PR-local row by the PR's own delta against the merge base, plus proposal P-R11-99 for round-end triage, since the tooling freeze holds. The cost test passes by more than 40x on runner time. Closes: none.

## Head

`2ff2f066e811e3eb5c7651ec099a7a0614497d96` is the code head: two commits adding `dev/audit/rca/R11-RCA-MODEX.md` on `origin/main` `e4c929bd1c`. The record was measured on 2026-11-22 against `origin/main` `4ebd430fbf` and `e4c929bd1c`.

## Mutation proof

n/a: a record adds no production or check code, so there is nothing to mutate. The prototype's own mutation run is run B in the record (section 6): the PR's own ten added module-level lines turn the overlay red where `own_delta=+10`, so the detector still detects.

## Null control

n/a: nothing is measured by this change. The record's own null controls are runs C, D and E (section 6): no PR-local row, PR-local rows main did not move, and an unmeasurable base, which fails rather than passes.

## Figures

none

## Red checks

none

## Forward-carry

The record's open questions are proposal P-R11-99 for round-end triage and land in `dev/programme/rosters/wave-r11-groups.json`, group `R11-CLOSEOUT-CLEANUP`, as a carry: whether the other budget-table checkers compare absolutely, and how many of the 14 merges that introduced new budget keys since 2026-10-01 suffered the class. The brief line to land a new ratchet row in its own pull request ahead of any raise is a plan change, proposed there too. Carry: R11-CLOSEOUT-CLEANUP

## Friction

none
