Fix review: blocked 1019d18de448a9569c65a704410c331046cbe868 carry-missing: not carried to #2428 #2436 #2437 #2429 #2438 (no owner, carry_audit BAD-DEST)

Round: first review of this head. Group: none (topic r10-rca-harness-friction; no group entry matched), so this was reviewed against the PR body. Measured at 1019d18de448a9569c65a704410c331046cbe868 (ev/HEAD.txt), from a detached worktree at that head.

RESULT step0 roles-current: git diff merge-base...origin/main -- dev/governance/roles/ is empty
RESULT step13 merge-tree origin/main(289426c1f) 1019d18de448a9569c65a704410c331046cbe868: rc=0, clean (ev/merge_tree.txt)
RESULT step10 carry: BLOCK. python3 -I tools/audit/carry_audit.py check --body <PR body> gives rc=1: "12 finding item(s): 6 routed, 0 unrouted, 6 bad destination(s)". The ## Forward-carry items routed to #2428, #2436, #2437 (twice), #2429 and #2438 all fail with "has no owner: no live roster group lists it and there is no dev/programme/carries/carry-N.json". I got the same result at the head and at origin/main 289426c1f (ev/carry_audit.txt). These carries are not written into any stage that owns them, so step 10 blocks.
RESULT step11 CI: pr-contract is red on both runs (119209550896, 119209802161). Its job log fails at the carry_audit step with the BAD-DEST lines above. The body's "## Red checks" says "none" because it was written before the PR existed. env-matrix, instrument-self-tests, policy-docs, mutation, closure-scope, briefs and nightly-status were still running when I read CI (ev/check_runs.txt). Step 11 gates a root-cause-unanswered verdict on all of them finishing, so I am not blocking on that here. The carry block above stands on its own.
RESULT step1 mutation: the claims hold. M1 (step 6 put back to "harness: class-open <seam>"): rc=1, FAIL "teaches class-open as a reason under another class". M2 (shadowed returns null): rc=1, negative control FAIL. M3 ("mutation-vacous"): rc=1, taught-word arm FAIL. M5 (detector loop line deleted, with M1 applied): rc=0, so that loop is the line that kills M1. The tree was clean after each mutant (ev/mutants.txt). At the head: 202 passed, 0 failed.
RESULT step5 VERSION, manifest version, notes heading and tests/golden: untouched (empty three-dot diff)
RESULT cheap checks at head: policy_lint TOTAL 0 errors across 41 files. fix-review.md 140/140 lines and 2443/2451 tokens; orchestrator.md 318/319 and 4511/4513, as the body says. fold_ledger 0 violations. rules_sync --check rc=0 (ev/cheap_checks.txt).
RESULT step8 not re-derived: the window statistics (policy_lint --stats 234/116, rounds.py 102 blocked, class-open 26/15, and the minutes figures) need a 229-PR API sweep. I did not re-take them, so they are unverified, not confirmed.
RESULT step2/6: the finding has no finder harness apart from the detector and the census. The detector's seam (step 6) is closed in the diff. I did not re-run the census.
RESULT step7: the body names 1019d18de448a9569c65a704410c331046cbe868 as the head. The PR API head is the same.

To clear the block, the fixer can route each of those six carries to a live owner: a roster group that lists the issue, or dev/programme/carries/carry-N.json. Otherwise, use a destination that carry_audit accepts, then re-run pr-contract.

bus-nonce: 886cfba8620475ae99447f6d9eef5cb3
