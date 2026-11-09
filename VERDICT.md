Fix review: blocked 06a3478fdbf386278952d741985e5da5ee28bd5c root-cause-unanswered: governance / delivery-status is red, the diff touches governance.yml, and ## Red checks says none

bus-nonce: a7782a528fcc250a2837a2db690e08fe

## Block

- `governance / delivery-status` concluded failure at this head (check 128955414223). Its grader exempts a body only while the diff touches none of what the check reads (defect-root-cause.md, Enforcement). This diff edits `.github/workflows/governance.yml` (the survivor-list self-test step), which that rule names. The body's `## Red checks` reads "none. CI has not run on this head", so the trigger is unanswered. CI says the same: `pr-contract` (job 128967170153) failed with "check `governance / delivery-status` is red and `## Red checks` does not name it", and the required `gate` follows it.
- To repair: name `governance / delivery-status` in `## Red checks`, with the cheaper detector and its standing cost, or the finding that none exists. If the red belongs to main, say so with evidence. Edit the body only; no code push is needed.

## Evidence

- Merge resolution delta (06a3478fd is the merge of 49b9fe55c into the previously merged 41a196a24): the resolved `dev/governance/roles/fix-review.md` step 13 holds both sides. It has the branch's inlined `git merge-tree --write-tree origin/main <head>` form and `MERGE-CLAIM: resolved|refused` compaction, and main's "Block on main only on one, never on a head behind main that merges cleanly (tvofi 11-07). A conflict off the two claim files is yours." The old retained sentence ("A conflict on any path other than ... yours to block on") is gone. `git diff origin/main HEAD` on the file equals the three-dot PR diff, so main's role-file text is intact and the resolution adds nothing else.
- `git merge-tree --write-tree origin/main 06a3478fdbf386278952d741985e5da5ee28bd5c`: rc 0 (LEDGER-MERGE resolved tests/closures.json). origin/main's role files are unchanged since the merge base.
- Mutation proof, re-run here (ev/mutants.txt): five mutants of `survivor_list.py`, each killed by its `--self-test` (rc 1): class gate inverted, left-boundary lookbehind removed, only the first survivor returned, triaged sites not dropped. The sixth, deleting the `survivor_list.py check` call from `bus.sh push-verdict`, fails `bus.sh --self-test` on the arm "push-verdict refuses a mutation-vacuous verdict naming one of two survivors". No survivors.
- Figures re-taken at this head: `survivor_list.py --self-test` is 20 checks, 0 failed. `tests/doc_claims.py` prints ALL 296 checks PASSED and `tests/entities.py` prints ALL 2668 ENTITY CHECKS PASSED. `tests/structure.py` prints STRUCTURE RATCHET PASSED. `policy_lint.mjs --budgets` gives fix-review.md 133 of 140 lines, 2450 of 2451 tokens. `selftest_wiring.py --check` gives 125 self-testing, 125 wired, 0 unwired. I did not re-run `bus.sh --self-test` in full (the 162-check figure is not re-derived); I ran only its push-verdict arm via mutant 6. The body's `closure.py` --diff versus --files scope discrepancy is as disclosed there; I did not trace it.
- Step 5: no VERSION, manifest or notes edit (pr-contract's version-edit step: "moves none").
- `carry_audit.py`: 0 finding items. `review_carry.py 41a196a2 HEAD` prints FRESH-REVIEW (the head is a hand-resolved merge), so this is a fresh review, not a carry.
- CI at this head: `classify` is WAIT. `gate` was re-queued after `pr-contract` failed, `tests/closures` and `codeql / python` had been in progress earlier, and `governance / delivery-status` is red. The only red attributable to this PR is the unanswered `delivery-status`.
- This is round 2 or later of this PR's review; the fourth round would owe a re-cut (fixer.md).
