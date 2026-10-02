<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: `budget-raise-gate` dropped every review under tvofi's account whose body declared an agent gave it, so a mandated agent approval could pass only if the agent hid its authorship.

After: an agent's approval counts when it stays declared as an agent's and cites a MANDATE comment that tvofi recorded on #201, which covers budget raises and was in force when the review was submitted. The verdict line names the mandate it used.

This amends decision 0013's `budget-raise-gate` (the 2026-09-24 amendment) and its D11-s1-04 refusal; the amendment section is in `docs/decisions/0013-verdicts-post-as-the-approver-app.md`. It is policy, so it merges on tvofi's own approving review.

How: `mandate_check` in `.claude/workflows/budget_raise_gate.py` reads the cited comment by id and #201's comments since it was posted, from the API at run time. It refuses a mandate that is expired, revoked by tvofi, not written by tvofi (login, id and type), not on #201, scoped `code-owned`, or not in the grammar. The approval must still be on the head. The workflow gains `issues: read`. `tests/entities.py` pins that permission and now keys its issue-trigger check inside `on:`, because the new top-level `issues: read` matched the old unanchored pattern.

## Head

d741a894 (code; merge base 492d8401, measured 2026-10-02T09:12Z)

## Mutation proof

Each mutant disables one refusal predicate (`False and ...`); evidence `mutants.txt`, runner `mutants.py`.
- M1 expired (`at >= end`): 2 checks fail, "a review submitted after `until` fails" and the at-`until` boundary.
- M2 revoked (the `MANDATE REVOKED` match): 2 fail, "a mandate tvofi revoked fails" and the named revocation.
- M3 not tvofi's (`_is_owner(comment.user)`): 3 fail, another account, a same-login other id, and the approver App.
- M4 scope (`scope not in MANDATE_COVERS_RAISE`): 1 fails, "scope code-owned does not cover a raise".
- M5 non-head (`last.commit_id != head`): 4 fail, including "a mandated approval on a non-head commit fails".
- M6 `_mandate` reads no thread: 2 end-to-end checks fail, the read order and the revocation exit.
- M0 restored: 0 failed, byte-identical to the committed file (`cmp`).

Failing test first: at 870f47a6's parent with the tests alone, `--self-test` exits 1 (`NameError: MANDATE_ISSUE`); evidence `selftest_tests_only.txt`.

## Null control

- No raise reads no mandate (`calls == []`).
- An agent approval citing no mandate id still fails.
- A revocation by another account, or of another mandate id, revokes nothing.
- The issue-trigger pattern still matches an `on:` block with `issues:` and does not match a `permissions:` block's `issues: read` (`issue_trigger_probe.txt`).

## Figures

- `python3 .claude/workflows/budget_raise_gate.py --self-test`: all checks pass; count from that command's last line.
- `PYTHONPATH=tests/hastub python3.13 tests/entities.py`: ALL ENTITY CHECKS PASSED (`entities.log`).
- `PYTHONPATH=tests/hastub python3.13 tests/harness_headers.py`: ALL HARNESS HEADER CHECKS PASSED.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Scope: `tests/closure.py select` at the merge base, MODE: SCOPED, running `tests/entities.py` and `tests/harness_headers.py`.

## Red checks

None known at handoff. The gate grades this PR with the base's copy, which is unchanged in effect because this diff raises no budget.

## Forward-carry

`docs/decisions/0013-verdicts-post-as-the-approver-app.md` (the 2026-10-02 amendment, in this diff): after merge, the approval seat cites the mandate comment id in each approval body ("mandate <id>"), and tvofi posts the first MANDATE comment on #201.

## Friction

none
