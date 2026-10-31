Fix review: merge f51d1e5d663de8c832c881c2ef663d740db830cd

bus-nonce: 4d62faff4010f404893f13f84b3b8e86

Round 1. Record PR (triage s8 batch 89, P326 REJECT). Diff vs merge base: dev/programme/delivery/3036.md (1 line) and dev/programme/triage/s6-batch89.md (new). No production code, no budget, claim, VERSION or closure file touched (ev/diff-files.txt).

## Evidence

- Ground (a), verified. dev/governance/rules/ci-autofix.md line 84 reads "Do not automate survivor triage, golden drift, structure budgets, `no-copies`, orphan -> `INERT`, or briefs lint"; CLAUDE.md rule 2 says "re-record deliberately with the reason in the commit message". The record quotes both correctly.
- Ground (b), verified. Re-derived with `git show <sha>:tests/structure_budgets.json` (ev/merge-chain.txt), class_excess_loc: 4665c0c91 ours 17671 theirs 17659 merged 17658, merge-base 17672; 958b4af8e ours 17658 theirs 17670 merged 17657, base 17671; 76d96ac77 ours 17657 theirs 17658 merged 17656, base 17659; 9033a5958 ours 17656 theirs 17656 merged 17656, base 17658. Every row of the table matches, and rows 1-3 equal base + both deltas. The "Measured 17654" for 9033a5958 I did not re-derive by building that tree; it is the record's own measurement (structure.py on that tree), and I took it from the record rather than re-running it.
- Ground (c), verified. tools/merge/ledger_merge.py merge3 line 242 is `if ours == theirs: return ours` (also line 267 after rekeying) (ev/ledger_merge_rule.txt). That the rule is what keeps 17656 follows from row 4: both sides equal, so the base-plus-deltas sum (17654) is never reached. The double-count argument for a re-cut handoff merged by tools/audit/seat/update_pr.sh (which merges handoff tips into the PR branch) is reasoning, not something I ran; it is sound because two sides carrying one shared reduction are indistinguishable from two coincident independent ones by text.
- Ground (d), verified. 41 first-parent commits since 2026-10-17 touch tests/structure_budgets.json on origin/main, matching the record's "41". One instance, re-open trigger stated (3 or more in one round). At current main, tests/structure.py prints STRUCTURE RATCHET PASSED.
- Merge with origin/main: git merge-tree --write-tree exits 0, no conflict (ev/merge-tree.txt).
- Review packet at this head: no refusals, no advisories, CARRY-AUDIT 0 findings, FIGURES 2 resolved, 0 not verified.
- CI at this head: merge_train.py classify exited 3 (WAIT, pending, gate red: none) on every run over roughly three hours. All concluded checks are success or skipped (pr-contract-relevant: delivery-status, policy-docs, briefs, closure-scope, fast, mutation, arch-score, budget-raise-gate, nightly-status all success). Two checks, governance / instrument-self-tests and tests / coverage, stayed in_progress throughout. I could not obtain GREEN; this verdict rests on the content review and is not a statement that those two passed. The merge train classifies CI itself before merging.
- Mutation, null control and both-ends steps do not apply: the PR writes no production line.
- Root-cause (step 11): no check went red at this head, so nothing is owed.
- VERSION, manifest version and RELEASE_NOTES heading untouched.
- The filename s6-batch89.md against the title "session s8" follows the directory's existing s6-batchN naming; not a defect.
