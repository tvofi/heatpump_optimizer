Fix review: merge bc75120cb7337969c46afa33efc05c9bd186b262

bus-nonce: 47acbb4b5a7d1dd515bc446a24ea0bf9

## Scope

Round 1 review of PR #2794 (record: delivery rows for #2790, #2791, autofix), head `bc75120cb7337969c46afa33efc05c9bd186b262`, merge base `21a1e04a7e838545f43a6f9a8545f4bb2bc0548f` (= origin/main). Role contract fix-review.md read from main; `git diff $(merge-base)...origin/main -- dev/governance/roles/` empty.

## Findings

none

## Evidence

- Diff (three-dot, ev/diff.txt): only `dev/programme/delivery/2790.md`, `2791.md` (open -> merged) and new `2794.md` (self row, open); each one line anchoring its own PR number. No production, test, check, budget, claim or closure file touched; mutation proof and null control correctly n/a (step 1, 3, 14 have nothing to act on).
- Merge SHAs re-derived: `ab3aade49` is "Merge pull request #2790", `21a1e04a7` is "Merge pull request #2791"; #2791's own rows (#2787, #2789) present on main, matching the row text.
- Step 5: `VERSION`, manifest and `RELEASE_NOTES.md` untouched.
- Step 4: no golden/claim files in diff; nothing to claim.
- Step 7: body `## Head` names `bc75120cb7337969c46afa33efc05c9bd186b262`, the head measured; re-read via ls-remote before return, still the head; main still `21a1e04`.
- Step 13: `git merge-tree --write-tree origin/main bc75120cb7337969c46afa33efc05c9bd186b262` rc=0, no conflict (ev/merge_tree.txt).
- RESULT delivery_status: `python3 tests/delivery_status.py` at head -> `DELIVERY STATUS OK — 143 rowed, 0 pending, 0 overdue`, rc=0 (ev/delivery_status.txt). This re-derives the body's one figure.
- RESULT policy_lint --record --since 21a1e04: 0 errors, rc=0 (ev/policy_lint_record.txt).
- RESULT record_row.py --automerge-check --head bc75120cb7337969c46afa33efc05c9bd186b262: `AUTOMERGE OK #2794`, rc=0 (ev/automerge_check.txt).
- Step 11, CI on this head (check-runs API, 56 runs): no run concluded failure; pr-contract success, delivery-status success, nightly-status success, mutation success (record-only diff draws no mutant). The body's Red-checks section pre-answers record/nightly-status/delivery-status, none of which is red on this head. At read time `gate`, a second `arch-score` and one `prelude` were still in_progress; those are not concluded and are not judged here.
- Step 6/9/10: record-class diff, single seam, no harness owed; Forward-carry "none" is consistent with a record beat.
