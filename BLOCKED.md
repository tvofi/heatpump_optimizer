# BLOCKED: r10-process-slim (#3245) at b2381acd5004e85a8b85a4643bc0939d25a3bf75

## The question (owner or orchestrator)

Card C5 deletes nightly.yml's `record-autofix` beat and stops `handoff_push.sh`
writing the delivery row. tools/release/stamp.py (code-owned, `/tools/release/ @tvofi`)
is unchanged by this diff, and two of its rules still depend on that beat:

- **The flush (rules 3-4).** `flush_before_tag` dispatches nightly.yml so the
  record beat merges a record PR. This dates from 6b1aa629f (#2836, 2026-10-26),
  an ancestor of the branch's first commit 96dde9309. After C5 the dispatch
  still succeeds, but nothing in nightly.yml writes a record. So every stamp
  waits up to FLUSH_TIMEOUT_S (7200 s), or until FLUSH_MAX_DISPATCHES full
  nightly runs have been dispatched, and lands no merge.
- **Rule 5 (rows).** `tests/delivery_status.py --require-rows` refuses any
  merged PR whose row is not rowed. After C5, the only row a merged PR has is
  the `**open**` row from `open_pr.sh`/`update_pr.sh` (`delivery_row.sh`), which
  reads as pending. So every window refuses unless the stamp is run with
  `--allow-rowless`.

Which ruling applies?

- (a) C5 extends to the stamp: retire the flush and the train hold
  (`hold_bound_s`, `train_hold`, `record_flush`, their self-test arms), and
  retire or redefine rule 5. This changes the stamp's refusal rules, which is
  policy (CLAUDE.md rule 4).
- (b) A delivery row is still written at merge by something else, for example
  postmerge.py. That reverses part of C5.
- (c) The stamp gap ships as is, as a recorded forward-carry.

My recommendation is (a). It deletes machinery whose only producer C5 deletes.
It is outside the owner-approved cards and the fixer's scope, so I made no
code change.

## STEP 1: which reds this diff caused

Check-runs at b2381acd, filter=all, 104 runs across all pages.

- **Caused by the diff (main merged with this head):** `tests / fast (3.14)`
  (128481970498), via `tests/entities.py`'s "stamp.py's --self-test passes"
  check, and `governance / instrument-self-tests` (128481970080), at the step
  that runs `stamp.py --self-test`. Both fail on the same check: `FAIL hold:
  the bound is nightly.yml's own HOLD_MAX_AGE_S by source read`. Main's #3280
  (aaaec2128) added that check after the merge base 4b5d771b, and C5 deletes
  the line it reads.
  - Null control, run in this seat: `python3 -I tools/release/stamp.py
    --self-test` printed `RESULT stamp_self_test=pass` at origin/main 8a1358e84
    and `RESULT stamp_self_test=fail` on 8a1358e84 merged with b2381acd (that
    merge also conflicts in `tools/audit/seat/sweep_template.md`).
- **Follows from the red above:** `pr-contract / pr-contract` (128493151057)
  refuses because the body does not name `tests / fast (3.14)`. The last
  `gate` (128493523507) reads `FAIL tests / fast (3.14): failure (this run)`.
- **Not caused by the diff:**
  - `tests / graders-head-copy` (128477498053) and `tests / lane-proofs`
    (128477500774) were cancelled when attempt 1 of run 42396905388 was
    cancelled at 17:39:11Z. In attempt 2 they concluded success (128491618847,
    128492036996).
  - The other gates: 128476564557 read fast(3.14) as cancelled in attempt 1.
    128481472549 (edit run 42398106138) reads `run(s) [42396905388] at this
    head are still being judged`, which is the edit/code deferral race.
  - `tests / nightly-status`: it graded main's cancelled dispatch 42369836867.
    Main's next dispatch, 42382408131, concluded success, so this red is
    inherited from main.
  - `budget-raise-gate`: the cap removal for the deleted proposal-triage.md
    waits on the owner's review.
- **Confirmed cleared:** the 6289321a block. `ref_privacy self-test: 113
  checks, 0 failed` in attempt 2's instrument-self-tests log.

## A concurrent seat on this topic

handoff-wip/r10-process-slim was at 86c6ff57c (2026-11-07 19:11Z). It carries
747e9065b, which moves `HOLD_MAX_AGE_S` into merge_train.py so that the stamp
self-test reads it there. That makes the check green, but it keeps the hold
alive for a beat that no longer exists, and it leaves the flush and rule 5 as
described above. This seat therefore pushes no code and no handoff or body,
so that it does not race that seat or pre-empt the ruling. This file is the
only commit on top of 86c6ff57c; delete it when you resume.
