Fix review: merge df70cb6bca69c7b1717abcc317233ff1bc994df3

Re-issue of verdict comment 6320657454 at this same head, routing its two observations; that verdict's findings and its merge call stand unchanged. Fresh re-check: the PR head is still df70cb6bca69c7b1717abcc317233ff1bc994df3 (ev/HEAD.txt). `git merge-tree --write-tree origin/main df70cb6bca69c7b1717abcc317233ff1bc994df3` with origin/main f2fb1b0e950e exits 0 (ev/merge_tree.out). All 17 required check contexts of ruleset main-protect-checks are success on the head (ev/required_checks.txt, ev/required_on_head.txt). Of 48 check runs, the only red one is nightly-status. It is not required, it grades main, and this diff touches nothing it reads, per defect-root-cause.md "nightly-status and delivery-status grade main". The body already answers it (ev/checkruns.txt, ev/nightly.out). carry_audit on the earlier verdict listed two unrouted items, 3df82198 and 3d8a556c (ev/carry_prior.out, ev/carry_pr_before.out). Each is routed below.

Carry: dismissed: rechain-decision.md section 4 rules "R10-SCORES: unchanged", so the note's stale `next:` text stays as the ruling left it. The train reads the after lists, which are correct (R10-CONFIG-NOTICES after = [], ev/after_lists.out) (item 3df82198)
Carry: dismissed: the HEAT-METER after THERMAL-POWER-OPTION edge is already enforced in R10-HEAT-METER's after list (ev/after_lists.out). rechain-decision.md section 3 left it to the orchestrator and requires no note text on THERMAL-POWER-OPTION (item 3d8a556c)

bus-nonce: 71d2e101ef8e59ecfb4f697cd84adb00
