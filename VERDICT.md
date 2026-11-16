Fix review: merge c155f81fa7eee55adc1de4d4211bba76f72bb20e

bus-nonce: cdbf23cbfb6e65bed3ff2f2ea5c11be9

## Summary

The diff is decision 0017's text plus the #3653 delivery row: two files, 14 lines added and 3 removed (three-dot from 6aa7ddc712). It changes no production code, test or claim file. It is a policy change, so the owner's approving review is still required before it merges. That gate is separate from this verdict.

## Evidence

- Head: the PR body and the review packet both name c155f81fa7eee55adc1de4d4211bba76f72bb20e, and that is the head reviewed (ev/HEAD.txt). It merges cleanly with origin/main: `git merge-tree --write-tree origin/main <head>` gives tree d82b97f478 with rc 0.
- CI: `merge_train.py classify` printed `GREEN c155f81fa7eee55adc1de4d4211bba76f72bb20e pending: none red: none` with rc 0 (ev/classify.txt). There are no reds, so no `## Red checks` answer is owed.
- Mutation proof: n/a. No production or test line changes, so there is no mutant to run.
- Null control, item 7, `[OUTSIDE]` stops: `git grep -n "cls=OUTSIDE" tools/audit/seat/merge_train.py` at the head returns 7 sites (ev/claims.txt), at lines 2698, 2720, 2751, 2765, 3157, 3183 and 3189. They are, in order: the unread head repository and branch, the stale contract copy, the contract's refusal, `no_fork_post`, the fork head that could not be checked out, the merge conflict, and `REMERGE FAILED ... at push`. Each one maps to a clause of the new item 7 text, and the text names nothing else.
- Null control, item 7, merge mechanism: `remerge_main.sh`'s `--head-repo` arm calls `PUT .../pulls/$PR/update-branch` with `expected_head_sha`, using the minted App token. It then reads the result back: the new head must have parents (old, a first-parent commit of main), exactly two of them, and a tree equal to `merge-tree old p2`. That matches "read back as the automatic two-parent merge". That arm has no `git push`, and every failure prints `REMERGE FAILED $PR at push (fork ...)`, which the train parks as `[OUTSIDE]`.
- Null control, item 6, fetch only: `merge_train.py:3154` fetches `+refs/pull/<pr>/head:refs/remotes/pull/<pr>/head` and adds the worktree with `--detach`, as the new text says. Every non-fixture `refs/pull/` use in tools/.github/.claude is a fetch into a local ref. The pushes are self-test fixtures to a local remote (`bus.sh:2456`, `app_approve.sh` `setpr`/`forkpr`, `app_comment.sh:339`).
- Forward-carry check: decision 0017's `## Before the first allowlist entry` already lists the three owner-held checks (the fork-head merge, the live check, and the account behind `CLOSURES_PUSH_TOKEN`) as owed before any entry is added. The body's dismissal of Carry 0 holds.
- `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden` are unchanged three-dot. The roles diff from merge base to main is empty, so the contract is current.
- Figures were re-run at the head in a detached worktree. The results are in the ev/*.log files; see `## Figures re-run` below.
- Finder's harness: none. This is a documentation carry with no finding harness; the null-control greps above stand in for it and are the reviewer's own.
- Note: body-figure: the body's list of `refs/pull/` readers leaves out two more fetch-only readers, `tools/pr/merge_main_bot.py:258` (into `refs/merge-main/<n>`, and it returns `skip-fork` for fork heads) and `tools/pr/outside.py` (into `refs/hpo-outside/<pr>`). Neither pushes, so the claim stands; only the enumeration is incomplete. Carry: dismissed: evidence, not a finding

## Findings

- Carry 0, the three live checks on a test fork, is not run at this head. It needs the owner's credential and a fork, and decision 0017 already records it as owed before the first allowlist entry. Carry: dismissed: owner-held checks, recorded as owed in decision 0017 before the first allowlist entry

## Figures re-run

- `python3 -I tools/audit/seat/merge_train.py --self-test` ended `merge_train self-test: 825 checks, 0 failed`, matching the body (ev/merge_train_selftest.log).
- `bash tools/audit/seat/merge_pr.sh --self-test` ended `merge_pr self-test: 50 checks, 0 failed`, matching the body (ev/merge_pr_selftest.log).
- `python3 -I tools/pr/outside.py --self-test` ended `outside self-test: 266 checks, 0 failed`, matching the body (ev/outside_selftest.log).
- `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`, matching the body (ev/structure.log).
- `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` was not re-derived by this seat. figure_lint lists it as unverified; the gate check is green at this head.
