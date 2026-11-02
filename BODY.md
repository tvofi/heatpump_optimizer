Triage batch 113 records one ruling, P371, the countermeasure from the root-cause record for the base-copy grader bootstrap: a pull request that teaches a pinned grader is graded by the base's copy, so no edit inside it can pass. Four instances in round 10 (R10-DEPS-ACTIONS-BUMP, R10-MACHINERY-RATCHETS, R10-BASH-KILL-HOOK, R10-AGREEMENT-BOOTSTRAP #3166) cost a measured 20 h 43 m, 62% of it BLOCKED returns waiting for the same split ruling. It is a root-cause countermeasure, so it keeps its own route and the owner's LOG rule does not apply.

- **P371 (a), (b), (c): ACCEPT, as one carry on R10-FLY-CIPREDICT-RESTORING** (`queued`, no pull request; its brief widens the same graders arm).
  - **(a)** `fixer.md` lets the fixer split itself (p1 grader hunks, p2 the rest) or move the registration to unpinned data, instead of returning BLOCKED.
  - **(b)** `designer.md` and `design-review.md` require a named p1/p2 split when a pinned grader must learn the change.
  - **(c)** `tools/pr/ci_predict.py`'s graders arm prints a BOOTSTRAP remedy when the refusing program is in the line's own changed-path list, and stops saying "repair before the handoff" for it (line 1107). Controls: 3 of 3 per-PR instances fire; an unchanged-grader refusal and a clean tree stay silent.
  - **Cost.** About 0 s per run for (c). About 120 tokens of role text for (a) and (b), against files at their caps: `fixer.md` 314/315 lines and 5216/5216 words, `designer.md` 60/60 and 878/878, `design-review.md` 53/53 and 778/778, fixer role 67 tokens of headroom. The builder pays by moving text; no raise is granted. (a) and (b) are policy.
- **P371 (d): DEFERRED to the owner.** Moving grader registries to unpinned data behind a pinned superset check reopens the #1403 boundary that decision 0013 drew ("Don't reopen the 1558 CI trust holes"). Additions are not monotone-safe (a "declares none" entry or a corpus exclusion shrinks grading), so it would need a design per registry. It changes on the owner's ruling, then a designer's note per registry naming its exempting kinds.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`. One roster op is queued held (`append-carry R10-FLY-CIPREDICT-RESTORING`), released when this file is on main.

## Head

`c3fde2648fc777aa6bc6a42e9cd2fd64de19245d`; the file is the whole diff against `dfb4ce2b5`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P371 as `ACCEPT`, and the queued carry text citing `s6-batch113.md#P371` passes: refusal `None`.
- With the verdict flipped to DEFER, the same text is refused: `is not an ACCEPT ruling (DEFER)`.
- P372 reads `None`: no such entry.

## Null control

- With the file absent from the roster branch and origin/main, `roster_edit.py append-carry` refuses the carry: `triage gate: the triage ruling dev/programme/triage/s6-batch113.md is not on the roster branch or origin/main; nothing written`.
- With it visible, the dry-run takes R10-FLY-CIPREDICT-RESTORING from 2 to 3 carries, and `brief_lint` reports `TOTAL: 0 error(s)`.

## Figures

- Seat ledger lines 3772, 3840, 3884 and 3890: one split ruling per instance; line 3521: the machinery freeze after v10.0.0.
- `node tools/policy/policy_lint.mjs --budgets` at `dfb4ce2b5`: the rows quoted above.
- `git grep -n "reopen the 1558" origin/main`: decision 0013, line 58.
- No capped file is touched; the diff is one markdown file.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
