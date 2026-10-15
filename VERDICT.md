Fix review: merge 5f47b7911e138ec564b53774f9f8e1fea4519b5d
bus-nonce: 8b042abb6975b177eaabfcf6c24090f3

Round 2: the resolution delta from my blocked verdict at 6285ed67c (comment 6195054813). It contains the repair d5998794b, two automatic merges of main (0bc62f48e, 5f47b7911) and the body fix for the orchestrator.md line. Measured from a detached worktree at 5f47b7911e138ec564b53774f9f8e1fea4519b5d.

RESULT head_unmutated passed=186 failed=0
RESULT mutation_M4_reviewer_prompt_reverted_to_base_wording failed=2 (184 passed) -- killed by the two new group-11b assertions; survived in round 1
RESULT mutation_M5_detectable_and_unrecorded_definitions_swapped failed=2 (184 passed) -- killed; survived in round 1
RESULT mutation_M1_vocabulary_line_deleted failed=4 (182 passed)
RESULT mutation_M2_ROOT_CAUSE_CLASSES_reverted failed=2 (184 passed)
RESULT merges: merge-tree of each merge's parents equals the merge's tree (no hand resolution); three-dot diff vs origin/main = web-fix-wave.js, check-wave-script.mjs, dev/programme/delivery/2275.md
RESULT enumerate.mjs head, window.json sha1 8c4de8e2: seams=13 instances=1 engineering_max=23, root-cause-unanswered=37 -- flat, as at the base
RESULT blocks_friction.mjs head, window.json: blocked_verdicts=124, block_class[root-cause-unanswered]=37, blocked_outside_grammar=0 -- flat
RESULT planted companion (sha1 907f6b3b0638, my own): head root-cause-detectable=1, root-cause-unrecorded=1, untaught:root-cause-invented=1 (base: all three untaught)
RESULT gate: both words in ROOT_CAUSE_CLASSES; each blocks and dispatches the root-cause seat, never a repair
RESULT forward-carry: on origin/main via #2287 (9b1320d37), R10-BRIEFS-FOLD's brief text carries the GATE-YIELD item as a "Forward-carried precondition" with its control (blocks_friction.mjs files the words under orchestration until placed); its files list names dev/governance/roles/fix-review.md and both D13/D14 harness files
RESULT CI at 5f47b7911e138ec564b53774f9f8e1fea4519b5d: 30 success, 15 skipped, 0 failure, 0 cancelled (check-runs API); pr-contract green
RESULT VERSION / manifest / notes heading: untouched

Code-owned: .claude/workflows/web-fix-wave.js -- the merge train approves it under mandate 6175172275.
