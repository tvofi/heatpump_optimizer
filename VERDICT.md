Fix review: merge 94ce0fe6b3ae94766e9262fe2cc7695a44281a59

bus-nonce: 0fe2220a8c232f60d0fe9d2b414aecf7
Round: 2. Round 1 blocked 957c9cd0 on B1, B2 and B3.
Measured head: 94ce0fe6b3ae94766e9262fe2cc7695a44281a59, in a fresh detached worktree at /Users/timmalmstrom/hpo-seats/orch-r9c/review-2029-r2. Fixer code e052636a, then a main merge. Merge base 8d7903e6. The three-dot diff is still the same 7 files: no row file, and no `docs/delivery/` path.
Live head re-read at posting: it equals the measured head.
Evidence dir: /Users/timmalmstrom/hpo-seats/orch-r9c/review-2029-r2-evidence

## Round-1 blockers, re-attacked

- **B1, non-canonical paths: fixed.** The guard now requires `path == row_path(int(m.group(1)))`. I re-ran my `path_attack.py` (`path_attack.out`). Arabic-Indic digits, fullwidth digits, a leading zero, a trailing newline and another directory each refuse alone. One PR rowed at two paths refuses on the non-canonical file. The canonical control passes.
  - The fixer's note is correct. My round-1 fixture carried no `base` field, so under the new merged-into-main arm my canonical control refuses for that reason alone (`path_attack_r1fixture.out`). With `base: {ref: main}` added, the control passes and every attack still refuses.
  - The self-test now carries all six cases. Removing the canonical-path arm fails 5 named checks (`mutations.out`).
- **B2 and B3, auto-merge re-pinning and the post-queue push: fixed by removing auto-merge.**
  - The beat now merges itself with REST `PUT /pulls/N/merge`, `{"sha": HEAD}`. GitHub refuses that merge when the live head is not `sha`, so no later head can ride the merge.
  - The merge runs only after `guard --require-green` passes at that same head. `automerge_check` refuses a head other than `--head` before it reads any file. That pin now has a test: a stand-in `_api` checks the refusal and the call list, with a null control. The mutation that removes the pin fails it.
  - A push after approval is judged afresh on the next beat. It is refused, which dismisses the bot approvals, or it passes as row-only. Either way nothing is merged that the guard did not read at the merged SHA.
  - Refusal now dismisses every `hpo-approver[bot]` APPROVED review, so a stale bot approval can no longer back a hand merge of refused content.
  - `GITHUB_TOKEN` is never used. The author App merges and dismisses, and the approver App only approves.
- **Token revocation: fixed.** A new `if: always()` step revokes both installation tokens on every path, including beats where the approve step never runs.
- **Merged-into-main facts: fixed.** A cited PR must have `base.ref == "main"`. There is a fixture, and removing the arm fails it.

## The body's two original gaps
Both are moot now that auto-merge is gone. `expectedHeadOid` is no longer used. `dismiss_stale_reviews_on_push: false` remains, but no unattended merge relies on it, because the merge is SHA-pinned and re-judged.

## Re-verified
- **Self-test:** `python3 tools/audit/seat/record_row.py --self-test` prints `all checks passed`, rc 0 (`selftest.out`).
- **Mutations, singly with a byte-identical restore** (`mutations.out`). Each of these fails its named check:
  - canonical path
  - base.ref
  - `_latest` re-run ordering
  - `not_green` treating `None` as passed
  - `not_green` dropping missing contexts
  - the head pin
- **Two survivors, non-blocking:**
  - Disabling the `--require-green` wiring inside `automerge_check` (`if green and not why`).
  - Collapsing the CLI's exit-3/exit-1 split.
  
  In the first case the PUT would be attempted early, and the ruleset's required checks refuse it (HTTP 405, then `skip-merge-refused`). In the second, a second-guard refusal reads as `approved-pending` and skips the dismissal. GitHub stays the backstop for the merge. Worth a fixture later; it does not block this merge.
- **Replay #1989–#2002 with the base arm** (`replay.out`). #1989, #1991, #1992, #1998, #2000, #2001 and #2002 give OK, rc 0. #1993, #1994, #1995, #1997 and #1999 refuse, rc 1, on branch.
- **Residual TOCTOU, theoretical:** the guard reads `/pulls/N` and then `/files`. A writer would have to force-push between those reads, then force-push back before the PUT, and do it twice, because the guard runs twice. The PUT `sha` pin still requires the merged SHA to be the one whose head was read. Closing it fully would mean re-reading the head after `/files` and comparing. That is optional.
- **Unverified in production:** whether the author App's installation token may dismiss reviews. Failure there only warns, and the merge stays SHA-pinned regardless.
- **Policy sentence:** it now reads "merges with no review seat where `record_row.py --automerge-check` passes at its head; else it is reviewed". That is accurate.
  - `policy_lint --budgets`: `delivery-status-tracking.md` is at 25/26 lines and 603/606 tokens, under its cap with no raise. `rules_sync --check` is ok.
- **VERSION, manifest and notes heading:** untouched (`pr-contract` "no version edit").
- **entities.py pins:** these are CI's, because the local interpreters lack 3.12+ syntax or `yaml`. The `fast (3.14)` check-run is success.

## CI at 94ce0fe6 (check-runs API, `checkruns.tsv`)
19 success, 11 skipped, 2 failure, 1 cancelled, and 2 still in progress when posted.
- **Success:** `pr-contract` (both runs), `fast (3.14)`, `mutation`, `policy-docs`, `briefs`, `closure-scope` and `wave-script`.
- **Failure:** `delivery-status` and `nightly-status`. They grade main, and the body answers both.
- **Cancelled:** `budget-raise-gate`. Re-run the twin.
- **Still running:** `coverage` and `closures`. Both are required. The merge train's CI gate must see them green; this verdict does not cover them.
