Fix review: merge 06cb984bdc0172bdd8eceda1ba55de0e67b4830e

bus-nonce: 216ac0a43e0c81c08c580e26e4e800d9

Delta re-review, round 2 for this PR: the body edit and the delivery-row commit, judged against the earlier blocked verdict (comment 6388572020, body-head-stale). The verdict is on head 06cb984bdc0172bdd8eceda1ba55de0e67b4830e (still the live head of triage/s6-batch14 when written; PR updated_at 19:31:39Z, body unchanged since). Measured against origin/main a260e563086a and merge base 87ecf385b1d2. `dev/governance/roles/` has no change between the merge base and origin/main, so the contract used is current.

## Findings

none

## Evidence

- Block cleared. The body's `## Head` now names `06cb984bdc0172bdd8eceda1ba55de0e67b4830e`, described as the ruling commit c130c242 plus one commit that holds only `dev/programme/delivery/2755.md`. That matches `git show --name-only 06cb984bdc0172bdd8eceda1ba55de0e67b4830e` (ev/scope.txt).
- RESULT policy_lint (body contract, from this checkout): `policy_lint.mjs --pr-body` on the live body at --head 06cb984bdc0172bdd8eceda1ba55de0e67b4830e gives `PR-BODY: 0 error(s)`, red-history `record`, 3 commits, no failure conclusion across them (ev/policy_lint_local.txt).
- RESULT harness bites (the finder's check, perturbed): set `## Head` back to c130c242 and the same lint returns 1 error, "`## Head` does not name 06cb984". Empty `## Red checks` to `none` with --red pr-contract and gate, and it returns 2 errors, one per check (ev/body_mutants.txt). The real body names both checks, with job ids, and says why they went red. CI drops `pr-contract / pr-contract` and `gate` from `--red` by name (.github/workflows/pr-contract.yml, "List the red checks at this head"), so the CI run is the local call with no --red.
- RESULT CI (fix-review step 11): pr-contract job 120967331018 started at 19:35:19Z. That is after the last red (gate 120962222537, concluded 19:13:22Z), and it ran on the re-taken body. It ended success. gate 120967474550 (run 40125701658) and gate 120967611466 (re-run attempt of 40122938509) both ended success. No other check is red on this head (ev/check_runs_at_head.txt). One more row, job 120967612416 (pr-contract, failure), has timestamps 19:12:30Z-19:12:59Z. Those are attempt 1's timestamps, copied into the re-run attempt, so it is not a new run on this body. The gate that ran after it ended success.
- Red checks answered: pr-contract and gate are named and answered in the body, and the earlier verdict's block names the cheaper detector (a local `policy_lint.mjs --pr-body` at the final head), so the step-11 trigger has its answer. The other checks were green or skipped throughout.
- Delivery row: `dev/programme/delivery/2755.md` is in the three-dot diff `git diff 87ecf385b...06cb984bdc0172bdd8eceda1ba55de0e67b4830e` (ev/scope.txt). It is a single line naming #2755 as open, and it is this PR's own row.
- Code diff unchanged: the head is the SHA the earlier verdict measured. The three-dot diff is still exactly `dev/programme/triage/s6-batch14.md` (+14) and `dev/programme/delivery/2755.md` (+1), and VERSION, the manifest and RELEASE_NOTES.md are untouched (ev/scope.txt). The body edit does not contradict anything the earlier verdict checked (scope, ruling_verdict P83=REJECT and P99=None, the figure 1 REJECT, P55 citation, merge), so those results carry unchanged.
- Merge: `git merge-tree --write-tree origin/main 06cb984bdc0172bdd8eceda1ba55de0e67b4830e` with origin/main at a260e563086a exits 0, tree 7a180cc6db1c, no conflict, no claim-file driver call (ev/merge_tree.txt).
- Commits carry no Co-Authored-By or session trailer. Neither added file has a host or home path.
- mergeable_state `blocked` is GitHub's review requirement, not a check: every check on this head is green.
