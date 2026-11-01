Fix review: blocked d843403626ee923fe1fbde4428f3a0b2eb734b06 carry-over-wide: a branch's own commit that edits main's merge-driver files (budgets, closures, claim files) carries under L6

bus-nonce: fb5f8cf63b53cd1763c957550b7ae836

Round 1.

## Block

Under L6 a commit of the branch's own now carries when (a) the head's tree equals git's automatic merge of the reviewed head onto main and (b) the branch's own diff compares equal. Both checks pass `:(exclude)` for every file main's `.gitattributes` gives a merge driver: tests/structure_budgets.json, tests/mutation_budgets.json, tests/closures.json, dev/audit/config/bugclasses.json, and the two claim files. Before L6 a non-bot commit refused on sight, so that exclusion only ever applied to bot commits confined to their subject's paths. After L6 an ordinary `fix: ...` commit can change those files freely and still carry.

Reproduced at this head (ev/replay-budget-raise.txt, ev/replay-claimfile.txt): a commit `fix: tidy wording` that appends a digit to the first value in tests/structure_budgets.json gives `CARRY: yes d84340362 -> 4e3d100be`. A second commit appending a line to tests/golden/claimed_drift.txt also gives CARRY: yes. Neither the new budget nor the claim line was ever reviewed. The budget-raise-gate and env_drift run on the new head, but the reviewer's merge verdict, which the owner's gate treats as a review of the head, now stands over exactly those edits.

Fix: in the own-commit case, do not apply the driver-file exclusion (or exclude only the files a bot commit in the range wrote), so the tree check and the comparison cover the driver files too. A self-test needs both a budget-edit and a claim-file-edit twin that refuse.

## Findings

- The own-commit path above is the block. Carry: R10-FLY-CARRY-DOC-CONTEXT | #3077 | O1 | dismissed: blocked in this verdict, to be fixed in the PR.
- P123's residual (a tvofi-authored row commit naming another PR's number) is only exploitable for a file under dev/programme/delivery/. The path is bound to the subject's number, and the commit is confined to that one file and to tvofi's identity. I found no use beyond a row. Carry: R10-FLY-CARRY-DOC-CONTEXT | #3077 | O2 | dismissed: data file, one path, owner identity only.
- The .md context mask also covers CLAUDE.md, dev/governance/** and .claude/**, which seats load as instruction. A context-only rewrite by main beside the branch's lines can change a rule's meaning while the carry stays yes. That matches how code merges are already treated (main's content is main's reviewed content), but the head's own tree is never re-read for it. Not blocking, raised for the owner together with the beyond-brief "or keep its patch (L6)" clause in orchestrator.md section 11, which I note and do not decide. Carry: R10-FLY-CARRY-DOC-CONTEXT | #3077 | O3 | dismissed: owner decision, flagged here.

## Evidence

- Head measured: d843403626ee923fe1fbde4428f3a0b2eb734b06 (ev/HEAD.txt). Authored code head 7d81026f1; the head adds only dev/programme/delivery/3077.md.
- Self-tests at the head under env -u BASH_ENV: app_approve 296 checks 0 failed; app_comment 67 / 0; review_carry 29 / 0; app_push 204 / 0; bus 110 / 0; merge_train 381 / 0 (ev/st-*.log).
- Mutants applied, each run against the named self-test and restored: re-merge tree check off (5 fail lines), mask on every file (4), mask removed (1), row path binding dropped (4), app_comment without the carry call (3 failed of 67). app_push without the M arm: see ev/mut-pushnoM.log. All five finished mutants were killed.
- My own plant: the budget-edit and claim-file-edit own commits above. They survive the shipped self-test, so no test covers them.
- merge-tree of the head onto origin/main: exit 0, no conflict.
- policy_lint --budgets and rules_sync --check ran clean. I did not diff the self-test assertion sets base against head.
- Not done: replay of 3-5 real merged PRs through --carry, the patch-id --stable versus --verbatim measurement, the archscore run, and the claim-file and VERSION checks beyond a three-dot stat. CI on this head was still pending when I wrote this (merge_train classify exit 3, WAIT).
