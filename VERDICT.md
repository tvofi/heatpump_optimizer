Fix review: merge 22eab552c61d34943b7d314f964c2959ab36b4ef

bus-nonce: bfa854c448faf2e873a2d584cc2284fa
Reviewer: r9c-rev-2014, round 4. This is a delta review of 1d494f01..22eab552; the round-3 merge verdict at 1d494f01 stands for the code. Fresh detached worktree /Users/timmalmstrom/hpo-seats/r9c-rev-2014-r4; I re-read the live head at posting time and it is the same SHA. Evidence: /Users/timmalmstrom/hpo-seats/r9c-rev-2014-evidence/r4

## Resolution delta (a main merge, so it is judged as its resolution only)
- dfe2bb79 merges main 8d7903e6 into the round-3 head 1d494f01, and 22eab552 merges dfe2bb79 into 1d494f01. No authored code change.
- Simulation: `git merge-tree --write-tree 1d494f01 8d7903e6` gives rc=1, conflicting only on dev/audit/config/bugclasses.json (merge_tree_sim.txt). The head's tree differs from the simulated tree only in that file, by the removed conflict markers (`4 +---`).
- Semantic check: the head's bugclasses.json equals main's file plus the PR's own changes (merge base c327da7f), key for key. That is 133 keys, equal=True, with no extra or lost entry. Both R9-RCA-2004 (PR) and R9-RCA-stress-recording (main) are kept.
- `fold_ledger.py check`: 0 violation(s). `git merge-tree` against origin/main: rc=0.
- Spot re-checks at the head: `friction_issues.mjs --self-test` 102/0; FR-3 consumer rc=0.

## Body corrections asked for in round 3
- `## Red checks` now says the diff does edit governance.yml at lines 220 and 602. Done.
- The body now records #2012 as merged at 14:21Z. Done. The in-tree RCA (dev/audit/rca/R9-RCA-2004.md:129) still reads "Owned by open PR #2012". That was true when the document was written, so it is not blocking; a later RO-9 or record pass can update it.
- Small inaccuracy: the body's `## Head` says 22eab552 "merges the authored code head dfe2bb79 and then merges origin/main 8d7903e6". In fact dfe2bb79 is the main merge into 1d494f01, and 22eab552 merges it into 1d494f01. No authored commit is in the delta. Not blocking.

## CI (check-runs at 22eab552, checkruns_head.tsv, 34 runs)
- Red: nightly-status and delivery-status only, both main's and answered in the body.
- budget-raise-gate has one **success** (run 37675921397) and one **cancelled** twin (run 37675921045). The cancelled one needs a rerun before the merge train; I did not rerun it, because seats make no GitHub writes.
- Still in progress at review time: pr-contract (queued), closures, browser, fast (3.14), coverage, env-matrix, instrument-self-tests, CodeQL (js and python). The merge is conditional on these finishing green; I did not watch them.
- Round-3 head 1d494f01 finished with only delivery-status and nightly-status failed, so its closures, coverage, fast, browser and env-matrix concluded green. dfe2bb79 has no failed runs.
