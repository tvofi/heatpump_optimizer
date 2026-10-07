Fix review: merge 0dfb63a8c64950f062b047b4a8a49565a1c64f5f

bus-nonce: 07a8e4662a62c316e1301277df33f110

Reviewer seat r9c-rev-2025, round 3. I reviewed from a fresh detached worktree, /Users/timmalmstrom/hpo-seats/r9c-rev-2025-r3, at 0dfb63a8. Its parents are 984334b5 (the fixer's merge d15fc0ae on top of e0f87d5b) and c327da7f (main). The live head was re-read at posting and had not moved. `git merge-tree --write-tree origin/main(e7479ad1) 0dfb63a8` exits 0.

## The merge resolution (d15fc0ae, merging main 09ba95d0)

- `git diff --name-only $(git merge-tree --write-tree e0f87d5b 09ba95d0) d15fc0ae` lists only `dev/audit/rounds/round4/D6/claims.json`, `dev/audit/rounds/round4/D6/claims.md` and `tools/audit/round4/D6/claims.md`, the old copy, deleted. That matches the body.
- Against 09ba95d0, the two regenerated files differ only in the module-count results, 71 -> 72.
- Re-running `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` at the head leaves the tree byte-clean.
- The moved claims.py carries the branch's EntryConfig `_ecl_topic` and the counts of 72.
- 0dfb63a8 (update_pr's merge of c327da7f) has an empty remerge-diff.
- The branch's changed lines are identical to round 2's (e0f87d5b vs e0f0b6fb, and 0dfb63a8 vs c327da7f), compared line by line. That covers custom_components, tests/harness.py, tests/structure_budgets.json, tests/mutation_ledger, tests/entities.py and tests/features.py. So round 2's local judgement carries: the live quiet apply equals main (reloaded=0, 2 off steps), quiet_windows.py is byte-identical to main, M1/M7/M9 are killed, and the deleted pins have stale anchors.
- tests/closures.json after the ledger merge: entry_config.py is in 26 closures, including all 20 that contain coordinator.py (missing=[]).

## CI at 0dfb63a8 (run 37663843895, via the commit check-runs API; `checkruns_head.tsv`)

- **typing: success** (job 112937895741). "errors did not grow", "ALL 9 typing-ruler checks PASSED". mypy is 0, from 9 at a390f589. I did not run mypy locally because none is installed here; this result is CI's.
- **closures: success** (job 112938013797). No UNDER-SCOPED. closures-autofix was skipped.
- **fast (3.14): success** (job 112937895765). `MODE: SCOPED -- 28 script(s) run, 4 scoped out`. It ran entities, features, golden and stress, among others:
  - ALL 3823 FEATURE CHECKS PASSED, so R9-F2.1 P3 is green on Linux.
  - ALL 2210 ENTITY CHECKS PASSED.
  - ALL 106 STRESS CHECKS PASSED.
  - golden runs in drift mode through `env_drift.py --all e7479ad1`: ok (445 s), and the fixtures are byte-identical to the base.
  - Also: manual plan ALL 128, typing-ruler source ALL 11, optimality ALL 84, finite boundary ALL 83.
- **coverage: success.**
- **mutation: failure** (job 112937895475) and **mutation-autofix: failure** (job 112940895162). "MUTATION TABLE REFUSED -- 4735 unpinned site(s) against 4693 at the ratchet base e7479ad1, 56 of them added by this diff", then "nothing was measured: 0 mutant(s) timed out, 56 not started for --budget-minutes". The autofix reports `skip-no-measurement`. This is the same unmeasured-lane red as at a390f589. The body's `## Red checks` names it, and the Mutation proof section dispositions it, leaving it to CI's chain. The trigger is answered, per fix-review.md step 11.

  Not verified: the 56 sites, and the features.py re-kills of the six rewritten lines whose pins were deleted. Nothing measured them at any head of this PR, and the per-PR budget does not reach them. Their pins come only from a later chain run (mutation-nightly or a dispatched drive), not from this merge.
- Not this PR's: `delivery-status` (UNCHECKED, 0 overdue, unread main merges such as 618d014), `nightly-status` (main's nightly), and `budget-raise-gate` (cancelled twin; its sibling succeeded). The diff raises no budget leaf. The merge may need the cancelled twin re-run (memory note: a cancelled budget gate blocks a merge).
- pr-contract: success twice. The PR author is hpo-author[bot]. Commit-author "Tvofi2" is not read by pr-contract (round 2).

## Notes, non-blocking

- `## Head` carries a stray second paragraph naming `6fa6f2aa4034044d30107b899f75b91562fa81d4`, which is not this head. The body does name 0dfb63a8 correctly (step 7), and pr-contract passed. The stray paragraph is a body-hygiene leftover for the next body re-take.
- The design choice is the orchestrator's, under the mandate. The live quiet apply replaces `self._ctx` with a copy whose EntryConfig is re-parsed. Objects that captured the old config at construction, such as the disinfection switch, keep the old object. None of them reads quiet keys, so this is judgement, not a measurement.
- VERSION, the manifest version and the RELEASE_NOTES heading are untouched. The structure budgets only go down (max_class_loc 8877, seam_cut_total 760). No budget raise.

Evidence: /Users/timmalmstrom/hpo-seats/r9c-rev-2025-ev3 (HEAD.txt, checkruns_head.tsv, joblog_112937895765.txt (fast), joblog_112938013797.txt (closures), joblog_112937895741.txt (typing), joblog_112937895475.txt / joblog_112940895162.txt (mutation chain), joblog_112937894446.txt (delivery-status), d15fc0ae_remerge.diff, resolution_paths.txt, closures_cover.txt, merge_tree_main.txt, claims_regen.txt, pr-body.md). Rounds 1 and 2: /Users/timmalmstrom/hpo-seats/r9c-rev-2025-ev and -ev2.
