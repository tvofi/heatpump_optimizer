Triage batch 62 rules the orchestrator's triage-queue line of 2026-10-29T22:30Z (claim-file merges void every merge verdict) as P290. It is the next rolling batch under V182, after batch 61 (#2970). **Urgent:** critical-path #2917 is blocked on this defect now, so this batch opens with one ruling.
- **P290 (a merge verdict never carries across a claim-file merge): ACCEPT, option (a) only, as a new fly-in R10-FLY-CARRY-CLAIM-DRIVER; option (b), a train hold, is REJECTED.**
  - `tools/pr/app_approve.sh`'s carry walk requires each `merge=claimnotes` file in a merge commit to equal the union of its parents. `review_carry.py` asks `app_approve.sh --carry` for this predicate, so both tools share it.
  - `tests/env_drift.py`'s `merge_claim_file` deliberately takes the claim list from whichever side changed it, never the union. So git's own driver resolution is refused.
  - The live train log holds 5 such refusals, all #2917 (4 `SKIP`, 1 `ADD REFUSED`).
  - Replaying the driver on (merge base, first parent, second parent) for the 4 refused merges gives the head's file exactly in all 4. The union of the parents matches none of them.
  - The fix: a claim file also passes when it equals main's driver output on the parents. A driver refusal leaves today's union rule deciding.
  - One held roster op (`append-group R10-FLY-CARRY-CLAIM-DRIVER`), released once this file is on main.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`944396c67a3131b28631d0f3530721503e815f05`; the file is the whole diff against `2fde526340bdb1da17fa7a5cd8bff283cff2757c`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P290 as `ACCEPT`. `triage_refusal` passes the new group's brief and resume note (it returns None).
- With `Verdict: ACCEPT` changed to `Verdict: REJECT`, the same texts are refused: `dev/programme/triage/s6-batch62.md#P290 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the same texts return `the triage ruling dev/programme/triage/s6-batch62.md is not on the roster branch or origin/main`.

## Figures

- `grep 'resolves tests/golden/'` over the live `merge_train/train.log`, then `grep -oE '^(SKIP|ADD REFUSED) #[0-9]+' | sort | uniq -c`, gives `4 SKIP #2917` and `1 ADD REFUSED #2917`.
- The replay: for each merge `H`, `git log -1 --format=%P H` gives the parents, and `git merge-base` gives the base. The file at those three commits went to scratch copies, and `python3 tests/env_drift.py --merge-claim-file O A B` was run on them (rc 0 each). `cmp` of the driver output against `git show H:tests/golden/claimed_drift.txt` was EQUAL for all 4. The sorted unique non-blank union of the parents' lines differed for all 4.
- The group was linted on a copy of the roster at the `handoff/audit-r10-roster` tip. The only error is its citation of this not-yet-merged file, which clears on merge.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
