Fix review: merge 229f638cb285db895771f825d4ce634e84fe5fa6
bus-nonce: 9156439357764341de3da888be2a07de

Round 2. Reviewed at PR head 229f638cb285db895771f825d4ce634e84fe5fa6 from a fresh detached worktree. That head is code head 459d05c3 merged into round 1's head 8b523cc6, which carried only `docs/delivery/1843.md`. Merge base 492d8401. I read the live head again just before publishing and it had not moved. My contract copy is current: `git diff <mb>...origin/main -- tools/audit/briefs/` is empty. This is a policy PR, so tvofi's own approving review is still needed to merge it.

## Round-1 blockers, re-measured with the reviewer's own harness

`probe.py` is round 1's probe. Its two unjudged cases are now expected to refuse, and I added 10 cases of my own for round 2.
- At 229f638c: **0 of 36** RESULT lines are UNEXPECTED (`probe_head.txt`).
- The same probe at round-1 head 8b523cc6 shows **11 UNEXPECTED** (`probe_round1head_8b523cc6.txt`). So the harness moves on the fix, and every null-control case (expect=True) holds at both ends.
- **B1 (revocation fail-open): closed.** All five near-miss forms now revoke: trailing period, `#id`, `: id`, lower case, and a second line. An `issuecomment-<id>` URL beside "revoking" also revokes. The over-revoke controls hold: a longer number containing the id, the same login with another id, and the mandate comment itself in the thread all revoke nothing.
- **B2 (edit before review): closed.** `updated_at != created_at` refuses, including an edit 1 second after creation and a missing `updated_at`.
- **Earlier CHANGES_REQUESTED: now refused.** This includes a CHANGES_REQUESTED on an older commit and a later one. tvofi's own DISMISSED and tvofi's own approval on an older commit still let a mandated approval at the head pass.
- **Another repository's #201: refused** (full `/repos/tvofi/heatpump_optimizer/issues/201` suffix).
- `--self-test`: 200 checks, 0 failed (`selftest_head.txt`).

## Mutation proof (reviewer's own mutants, `mutate.py`, `mutants_reviewer.txt`)

The copies run out of tree. The unmutated copy (`none`) fails exactly 2 environment checks; every other count below is in addition to those.
- revocation off: 9 checks fail.
- revoker-must-be-owner dropped: 1.
- whole-number boundary dropped: 1.
- "revok" word requirement dropped: 1.
- revocation reverted to round 1's strict grammar: 3.
- edit refusal off: 3.
- edit refusal reverted to round 1's `updated > at`: 2.
- CHANGES_REQUESTED override off: 1 (2 checks).
- issue URL reverted to `/issues/201`: 1.
- grammar refusal off: 1. **Round 1's surviving mutant is now killed.**

Every mutant is killed by a named check.

## The fixer's edit-rate figure, re-derived

The figure is "7 of 285 tvofi comments since 2026-09-15 were edited". I read all of #201's comments, 1329 in 14 pages. tvofi wrote 1185 of them, and 16 of those are edited across all time. Restricted to `updated_at >= 2026-09-15`, which is how the API's `since=` filters, it is **285 tvofi comments, 7 edited**, matching the body exactly (`edit_rate_201.txt`).

**Choosing not to treat an edited tvofi comment as a revocation:** tvofi decided this (relayed by the orchestrator), so it is not judged here. Factually, an edit-as-revocation rule would not close the deletion path either. The amendment already records that a write-access account can edit or delete a revocation, and that the mandate's `until` bounds that.

## Seams (class rule in the body: every field of a GitHub object the gate reads)

The rule names the mandate body, the revocation body, `issue_url` and the review body. Each is closed in this diff or dispositioned in the body and the amendment. I found no seam outside that list.

## Advisory, non-blocking

- **The `until` bound.** The amendment says `until` is "the bound that no such edit can remove". With `until programme-end`, that bound is the end of the programme. A finite `until` keeps the residual window of a deleted or edited revocation short.
- **Seats hold tvofi's token** (carried from round 1). `gh` on this machine is signed in as tvofi, so any seat can post a comment on #201 that passes the mandate checks. The mandate adds no forgery capability that the token did not already give. Seats must never post a `MANDATE:` line.
- **Status comments can revoke a mandate.** Any comment a seat posts on #201 as tvofi that names a mandate id near any form of "revoke" revokes that mandate, wherever the word appears. This fails safe, but the orchestrator should know that a status comment discussing revocation will trigger it.

## CI at 229f638c (check-runs API, `check_runs_head.txt`, read after the Tests run completed)

- 24 success, 9 skipped, 2 cancelled, 0 failure.
- Both cancelled runs (budget-raise-gate, pr-contract) are superseded duplicates. The same names concluded success at this head.
- Tests run 36998454762 concluded **success**: fast (3.14), closures, closure-scope, coverage, mutation, typing, briefs, browser, nightly-status, delivery-status, env-matrix and the rest.
- There is no red, so step 11 owes nothing.
- I did not run the gate myself, so I key on no MODE line. Locally, `tests/entities.py` cannot import numpy in my venv, so CI's `fast` is the cited evidence.
- `git merge-tree --write-tree origin/main <head>` exits 0.
- VERSION, the manifest and the notes heading are untouched. The diff touches 5 files.

## Evidence (this directory)

- `HEAD_MEASURED.txt` (names the head)
- `probe.py`, `probe_head.txt`, `probe_round1head_8b523cc6.txt`
- `mutate.py`, `mutants_reviewer.txt`
- `selftest_head.txt`
- `edit_rate_201.txt`
- `check_runs_head.txt`, `workflow_runs_head.txt`
- `pr_body.txt`

All harnesses are the reviewer's own.
