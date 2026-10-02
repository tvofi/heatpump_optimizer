Fix review: blocked 8b523cc690ac170acc2b039a2b01afdefb70432b class-open: the revocation is fail-open on any near-miss spelling, and a tvofi comment that someone else edits before the review counts as a mandate

Round 1. Reviewed at the head 8b523cc690ac170acc2b039a2b01afdefb70432b, a detached worktree. The authored code head is d741a894, and the merge base is 492d8401. I re-read the live head before writing this verdict and it had not moved. My contract copy is current: `git diff <mb>...origin/main -- tools/audit/briefs/` is empty. This is a policy PR, so tvofi approves the merge. This verdict covers the authored work only.

## Blocking findings (my own probe, `probe.py`, output `probe_head.txt`)

**B1. A revocation with any near-miss spelling is silently ignored.** `MANDATE_REVOKED.fullmatch` is applied to the first line only, so it accepts exactly `MANDATE REVOKED <id>` and nothing else. Each revocation below was posted by the pinned owner account (login, id and type) and cites the right id. Each one leaves the mandate in force, so `approved=True`:
- `MANDATE REVOKED <id>.` (a trailing period)
- `MANDATE REVOKED #<id>`
- `MANDATE REVOKED: <id>`
- `Mandate revoked <id>`
- `Ending it now.\nMANDATE REVOKED <id>` (the revocation on a second line)

The grant must be strict, and it is. The kill switch must be lenient, because over-matching a revocation fails safe while under-matching fails open. As written, tvofi can believe a mandate is revoked while the gate still passes agent approvals under it, and nothing reports the near miss. Suggested repair: any tvofi comment on #201, with a line matching something like `(?i)\brevok\w*\b.*?#?<id>\b`, revokes `<id>`. Add tests for the five forms above.

**B2. Someone other than tvofi can turn an existing tvofi comment into a mandate by editing it.** `mandate_check` refuses an edit only when `updated_at > review.submitted_at`. An edit made *before* the review passes. Because `start = max(from, created_at)` and an old comment has an early `created_at`, the rewritten text governs. My probe case "EDITED BEFORE review" sets created 2026-09-01, updated 2026-10-02T06:30Z and a review at 07:00Z, and it returns `approved=True`. GitHub lets anyone with write access edit other users' issue comments. The collaborator list, read live, shows `tvofi-seat-author  User  write`. That account is retired by decision 0011 but still holds write access. An App with issues:write may also be able to edit, but I did not test that because it would be a write. The comment's `user` stays tvofi, so `_is_owner` passes. The gate never reads who made the edit. Suggested repair: refuse any mandate whose `updated_at != created_at`. An edited mandate would then grant nothing, and tvofi posts a fresh one. The alternative is to read the editor through GraphQL `userContentEdits`, which is heavier. Add a test where the edit happens before the review.

Both findings are seams of the class the PR set out to close: a refusal predicate that the harness's configurations reach and the tests never exercised. Hence `class-open`.

## Residual for tvofi (not blocking, and the PR cannot fix it)

- The seats run `gh` authenticated as **tvofi**. This machine's `gh auth status` shows the active account is tvofi, via keyring. Any seat holding that token can post a `MANDATE:` comment on #201 that passes every check in `mandate_check`, because author login, id and type are all genuinely tvofi's. Forging an undeclared approval already needed this same token, so the mandate adds no new forgery capability. It does make a forged grant look exactly like a real one. The forward-carry text says tvofi posts the first MANDATE comment. That only holds if no seat ever posts one, even when told to in a chat. tvofi should decide whether to accept this or require the mandate through a channel the seats' token cannot reach.
- An agent's mandated APPROVED review overrides tvofi's own **earlier** CHANGES_REQUESTED (probe case `approved=True`). Only a *later* CHANGES_REQUESTED from tvofi is pinned to override. This may be intended, since a mandate lets the agent approve as tvofi. It is still tvofi's call, and the amendment text does not say it.

## Mutation proof (my own mutants, `mutate.py`, output `mutants_reviewer.txt`)

Each mutant disables one predicate in an out-of-tree copy. Control `mutant_none_outoftree.txt`: the unmutated copy gives exactly 2 environment failures (`git rev-parse` in the copy's directory), so any failure beyond those 2 is the mutant's.
- expired +2, not-yet +1, revoked +3, revoker-must-be-owner +1, author +3, author-id +2, issue +1, scope +1, edited-after +1, two-cites +1, agent-state +1: each is killed by a named check.
- **grammar (`if not m` → `if False`): survives the self-test (+0).** The next line, `m.group`, raises. `decide` catches the exception and refuses ("could not be read"), so the gate still fails closed. The refusal therefore has no distinguishing test: the unit test that claims to pin the grammar arm would pass without it. This is minor, and fixing it with B1/B2 means asserting the refusal text ("first line is not the mandate grammar").
- I did not re-run the fixer's `mutants.py`. These are my own.

## Null controls (re-run, `probe_head.txt`)

- An agent approval that cites no mandate: refused.
- A revocation by another account: revokes nothing, so the mandate stays in force.
- An undeclared approval from the owner: unchanged (passes as before).
- The approver App's own approval: refused.
- `self-test`: 184 checks, 0 failed (head, python 3.14). I did not re-run the e2e "no raise reads no mandate" check separately. It is inside that count.

## Other probes

- **Wrong-author login, id and type; wrong issue; scope code-owned; non-head approval; review after `until` and before `from`; a mandate quoted (`> `) or on the second line; trailing text; edited after the review:** all refused (`probe_head.txt`).
- **#201 in another repository:** `mandate_check`'s `endswith("/issues/201")` check accepts it (probe `approved=True`), but no live call can reach that path. `GET repos/tvofi/heatpump_optimizer/issues/comments/<foreign id 539473254 from cli/cli>` answers 404, so `_mandate` returns None. This is defence-in-depth only. Comparing the full `repos/<repo>/issues/201` suffix would make the check robust, but it is not blocking.
- **The issue-trigger regex in tests/entities.py:** the old pattern matched only `budget-raise-gate.yml`, and only because of the new `permissions: issues: read`. The new pattern matches nothing. No workflow is issue-triggered at either end, so the protected check runs over an empty set, both at the base and at the head. Synthetic controls: an `on:` block with `issues:` or `issue_comment:` (including indented and comment lines in between) matches. `permissions:\n  issues: read` does not. `on: [issues]` and `"on":` match under neither the old nor the new pattern, so this is not a regression (`issue_trigger_sets.txt`).
- **Conflict:** `git merge-tree --write-tree origin/main <head>` exits 0.
- **VERSION, the manifest and the notes heading:** untouched. The diff is 5 files.

## CI at the head (check-runs API, `check_runs_head.txt`, read 2026-10-02)

- **Green:** budget-raise-gate, pr-contract, policy-docs, instrument-self-tests, wave-script, delivery-status, env-matrix, hassfest, validate-hacs, Analyze (actions/js-ts).
- **Cancelled:** one each of budget-raise-gate and pr-contract. These are superseded duplicate runs; the same names also concluded success.
- **Still running or not started:** CodeQL python. The **Tests workflow (run 36996228877) is `pending`**, so no fast/closures/mutation result exists at this head yet. I did not run the gate. I key on no MODE line because I ran no scoped gate.

## Evidence

All on branch `review/1843`: `probe.py`, `probe_head.txt`, `mutate.py`, `mutants_reviewer.txt`, `mutant_none_outoftree.txt`, `issue_trigger_sets.txt`, `check_runs_head.txt`. All harnesses are the reviewer's own, not the fixer's.

Publication note: the contract names `bus.sh push-verdict`. This seat's dispatch forbade any GitHub write other than this branch push, so the verdict was not posted to the PR.
