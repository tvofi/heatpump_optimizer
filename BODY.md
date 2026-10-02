<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: `budget-raise-gate` dropped every review under tvofi's account whose body declared an agent gave it, so a mandated agent approval could pass only if the agent hid its authorship.

After: an agent's approval counts when it stays declared as an agent's and cites a MANDATE comment that tvofi recorded on #201, which covers budget raises and was in force when the review was submitted. The verdict line names the mandate it used.

This amends decision 0013's `budget-raise-gate` (the 2026-09-24 amendment) and its D11-s1-04 refusal; the amendment section is in `docs/decisions/0013-verdicts-post-as-the-approver-app.md`. It is policy, so it merges on tvofi's own approving review.

How: `mandate_check` in `.claude/workflows/budget_raise_gate.py` reads the cited comment by id and #201's comments since it was posted, from the API at run time. It refuses a mandate that is expired, revoked by tvofi, not written by tvofi (login, id and type), not on this repository's #201, scoped `code-owned`, not in the grammar, or ever edited. The approval must still be on the head, and a mandated approval does not override tvofi's own latest CHANGES_REQUESTED. The workflow gains `issues: read`. `tests/entities.py` pins that permission and now keys its issue-trigger check inside `on:`, because the new top-level `issues: read` matched the old unanchored pattern.

Round 2 (fix review at 8b523cc6, blocked):
- B1: any tvofi comment on #201 that names the id beside any form of "revoke", on any line and in any case, now revokes. The grant stays strict and the kill switch is loose, because over-revoking fails safe.
- B2: a mandate comment whose `updated_at` differs from its `created_at` grants nothing, whenever the edit happened.
- Minor: the grammar refusal is now pinned by its own refusal text.
- The amendment now states that a mandated approval may not override tvofi's own CHANGES_REQUESTED, and the gate implements that.
- The reviewer's foreign-repository #201 probe is closed too: the issue URL must end in `/repos/tvofi/heatpump_optimizer/issues/201`.

## Head

459d05c3 (code; merge base 492d8401 = origin/main at 2026-10-02T10:48Z)

## Mutation proof

Runner `mut/mutate.py` (sha1 b779bb29), run from the committed head. It edits one predicate in place, runs `--self-test` and restores the file. `git diff --quiet` was clean after the run.
- M0, no mutation: 0 failed.
- M1, the revocation never matches: 9 fail. These are the 6 near-miss forms, the exact form, its named refusal, and the end-to-end revocation exit.
- M2, the "revoke" word requirement dropped: 1 fails, "tvofi's comment naming the id with no revocation word revokes nothing".
- M3, the id digit boundary dropped: 1 fails, "a revocation naming a longer id that contains this one revokes nothing".
- M4, the revoker owner check dropped: 1 fails, "a revocation by another account revokes nothing".
- M5, the edit refusal put back to round 1's `updated > at`: 2 fail, "a mandate edited before the review fails" and its refusal text.
- M6, `if not m` changed to `if False` (the grammar refusal): 1 fails, "a body that is not the grammar is refused as such, not as an unread mandate". In round 1 this mutant survived.
- M7, the override of tvofi's own CHANGES_REQUESTED dropped: 2 fail, the refusal and its text.
- M8, the issue-URL check put back to `/issues/201`: 1 fails, "a mandate comment on #201 of another repository fails".

Failing tests came first. At 22f1141b, which has the round-2 tests over d741a894's code, 10 checks fail: the 6 revocation forms, the 2 edited-mandate checks and the 2 CHANGES_REQUESTED checks. At 2d79eafd, the foreign-repository test over ae00f893's code, 1 check fails.

## Null control

- No raise reads no mandate (`calls == []`). The check is unchanged and passes.
- An agent approval citing no mandate id still fails.
- A revocation by another account, of another mandate id, or of a longer id that contains this one revokes nothing. tvofi's comment that names the id without a revocation word revokes nothing either.
- tvofi's own later APPROVED clears his earlier CHANGES_REQUESTED, as before. tvofi's own earlier DISMISSED blocks nothing.

## Figures

- `python3 .claude/workflows/budget_raise_gate.py --self-test` at 459d05c3: 0 failed. The count is on that command's last line.
- The reviewer's harness `probe.py` (sha1 2d580f35, from `review/1843`) was run against `budget_raise_gate.py` at both ends. At d741a894 it prints 6 `UNEXPECTED` lines: the 5 revocation forms and the foreign-repository #201. At 459d05c3 it prints 0 of 26 `RESULT` lines. The two cases the probe leaves unjudged (`expect=None`) changed from `approved=True` to `approved=False`: "EDITED BEFORE review" and "agent approval after owner's own CHANGES_REQUESTED". The rule is `grep -c UNEXPECTED`.
- Seams of the class, which is text the gate reads that an account other than tvofi can change. The enumeration rule: every field of a GitHub object that `approval` and `mandate_check` read.
  - The mandate body: closed in this diff (B2).
  - The revocation body: matched loosely in this diff. An account with write access can still edit away or delete a revocation, and the comments API shows neither. This is not closable here, so it is stated in the amendment as a residual bounded by the mandate's `until`.
  - The mandate's `issue_url`: closed in this diff.
  - The review body: its author is the account that submitted it, and this diff does not change that surface.
- `tests/closure.py select` at the merge base prints MODE: SCOPED and names `tests/entities.py` and `tests/harness_headers.py`. Neither ran on this seat, because no local interpreter has numpy: both exit 1 on `ModuleNotFoundError: No module named 'numpy'`. CI's `fast` job runs both. This round touches neither file nor anything they parse, other than the two files above.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- How often tvofi edits #201 comments, the cost basis for not counting an edited comment as a revocation: 7 of 285 tvofi comments since 2026-09-15 were edited (`updated_at != created_at`, read from `repos/tvofi/heatpump_optimizer/issues/201/comments?since=2026-09-15T00:00:00Z`).

## Red checks

None known at handoff. At 8b523cc6, two runs were cancelled as superseded duplicates (budget-raise-gate and pr-contract). They are not reds. The gate grades this PR with the base's copy, which is unchanged in effect because this diff raises no budget.

## Forward-carry

`docs/decisions/0013-verdicts-post-as-the-approver-app.md` (the 2026-10-02 amendment, in this diff): after merge, the approval seat cites the mandate comment id in each approval body ("mandate <id>"), and tvofi posts the first MANDATE comment on #201. Each later grant is a fresh, unedited comment. A revocation names the id and the word "revoke".

## Residual for tvofi

- The seats run `gh` as tvofi, so a seat could post a MANDATE comment that passes every check. Forging an undeclared approval already needed the same token, so the mandate adds no new forgery capability. It does make a forged grant look exactly like a real one. tvofi decides whether to accept this.
- An account with write access can delete or edit a revocation without leaving a trace in the comments API. The mandate's `until` bounds this.

## Friction

none
