Triage batch 53 rules V178, the orchestrator's friction filing at 2026-10-28T18:43:14Z, as P264: ACCEPT narrowed, into R10-FLY-CARRY-DOC-CONTEXT. It is its own batch because batch 52 (#2924) was already merge-verdicted and queued in the train when it arrived.

- **The friction.** On #2912, the CI bot's `ci: pin killed mutants` commit (`4fc6a4c51`) moved the head after a merge verdict at `cc0510ee2`. `app_approve.sh --carry` answers `CARRY: yes`, yet the verdict could not be posted, so the PR costs a re-review round.
- **The refusal is in the poster.** `tools/pr/app_comment.sh:68-69` (`check_pr`) refuses any merge verdict whose head differs from the live head. The train's own carry admission (`merge_train.py` `admit_verdict`, lines 2045-2048) is therefore never reached, and the train reports "confirmed and not posted" (line 2076).
- **The carry.** `check_pr` runs the same `app_approve.sh --carry` predicate before refusing. It posts with a carry line on `CARRY: yes` and refuses as today otherwise. `bus.sh` and `train.sh` are unchanged.
- **Measured.** 16 of 284 PRs merged since 2026-10-21 carry a pin commit. 6 had a merge verdict at the pre-pin head, and in 3 the pin precedes the verdict (#2612, #2775, #2745). With #2912 that is 4 instances in 7 days.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`e7c001083fa9de3e25f949389b3964e85e19fda8`; the file is the whole diff against `beb570c817c4efcae0d5f6f4bba52f3383baf8db`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate.
- On the committed file, `ruling_verdict` reads P264 as `ACCEPT`, and the queued carry text citing `#P264` passes.
- Mutant (the verdict rewritten to `REJECT` in a copy): the carry is refused, `#P264 is not an ACCEPT ruling (REJECT)`, so the gate reads this line.

## Null control

With the file absent, the same call returns `the triage ruling dev/programme/triage/s6-batch53.md is not on the roster branch or origin/main`.

## Figures

- `app_comment.sh:69`: "head moved: the merge verdict names $3, the live head of #$2 is $head". `merge_train.py:2076`: "is confirmed and not posted".
- 16 of 284 first-parent merges since 2026-10-21 carry `ci: pin killed mutants` (`git log --grep` over each `^1..^2`).
- Merge verdicts per affected PR (`git log origin/verdict/<n> | grep -c 'Fix review: merge'`): #2745 14, #2819 3, #2824 2, #2817 2, #2775 5, #2612 2.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

- P264 ACCEPT narrowed (V178): `app_comment.sh`'s `check_pr` posts a merge verdict whose head carries (`app_approve.sh --carry`: yes) with a carry line, and refuses otherwise. Carry: R10-FLY-CARRY-DOC-CONTEXT

## Friction

none
