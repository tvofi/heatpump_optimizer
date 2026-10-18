Fix review: blocked 03f1681a3e684854b5b934020ec5d44612b2ffd2 root-cause-unanswered: wave-script went red, unanswered (and delivery-status; pr-contract 117779459209 refuses the body; both reds are main's, so the repair is a body edit only)

bus-nonce: 48c96e8c8b8abf2fbe5a786c671575d6
Round: fourth review of #2404. Round 1 blocked 5cf5786b9 (the item-ref over-fire). Round 2 blocked 354c84a96 (mutation-vacuous: the paren form and the segment scope were each unpinned). Round 3 blocked 312f31923 (mutation-vacuous: the line-end cut and the next-`Carry:` cut were each unpinned). This round judges the delta 312f31923..03f1681a3: authored commits 8c666c644 and 6f20f78a3, the main merges f08104f74, 7c0383bc8 and 03f1681a3, and the re-cut body.
Reviewed head: 03f1681a3e684854b5b934020ec5d44612b2ffd2. It was still the PR head at 20:53 UTC, after every check run on it had concluded. Merge base 07a09406a. Role contract current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
Evidence: ev/ (this probe ref)

## Block

The code is sound. Every claim I re-derived holds; see Verified. The block is step 11, and the repair is a body edit only.

The head carries three red check runs (ev/check-runs.tsv: 48 runs, 30 success, 15 skipped, 3 failure):
- wave-script 117778707693: `pair merge-subject-pr: ... 2 divergent` on "Merge pull request #2401 (R10-ARCHSCORE-COVERAGE p5)" and "#2379 (R10-SENSOR-PAYLOAD)". These are the same two DIVERGENT subjects as main's own wave-script red at 07a09406a (job 117765552837). `diff ev/wave-script-main.txt ev/wave-script-head.txt` differs only in the item count, 808 against 809. This is main's red (the 5756f2b1 merge-subject divergence, in flight as R10-MERGE-SUBJECT), not this PR's.
- delivery-status 117778707734: `DELIVERY STATUS OVERDUE`, on main's autofix rows #2413, #2412 and #2407. The diff's governance.yml hunk is in instrument-self-tests, not in the delivery-status job, and touches no delivery row except its own 2404.md. By fix-review.md step 11 this red is not this PR's.
- pr-contract 117779459209 started at 20:19:50, after both reds concluded (20:16:49 and 20:16:51). It refused the body: `check \`delivery-status\` is red and \`## Red checks\` does not name it` and `check \`wave-script\` is red and \`## Red checks\` does not name it` (ev/pr-contract-117779459209.log, around line 1578). Every workflow on the head has since concluded, so the step-11 posting condition holds.

Repair: add two bullets to the body's `## Red checks`. Each names its check, says it is main's red with the evidence above, and states the cheaper-detector answer. For wave-script, the R10-MERGE-SUBJECT fix is in flight on main. Then pr-contract re-runs on the body edit. No code change is owed, and none of my numbers below depend on the body.

## Verified

RESULT drive sites=152 unmapped=0 mutants=190 survived=0 (python3 dev/audit/harnesses/r10_carry_parser_mutants.py at head; 191 RESULT lines: M0 baseline, S-span-lo equivalent, the rest killed; git status clean after)
RESULT carry_audit_selftest=144 failed=0; queue_pre_flight_selftest=37 failed=0; merge_train_selftest=180 failed=0
RESULT own_mutants_segment (hand-planted, my script ev/m2.py; Dests mutants ev/mut.py, not the drive): M15b line-cut=killed (1: "a segment ends at its line"), M16 next-cut=killed (1: "a segment ends at the next `Carry:`"), span-skip removed=killed (4), ITEM_REF bare=killed (3), segment scope dropped=killed (3). Round 3's two survivors and round 2's two are now each killed alone.
RESULT own_mutants_dests (hand-planted on Dests.check, load_dests, seg_dests and audit; 13 mutants): 11 killed, 2 survived (see notes)
RESULT rows39 rows_caught=33 of=33; last20 rows_caught=34 of=35, last20_hits=76 on_a_row=46 on_no_row=30
RESULT sweep --issues ISSUE-UNOWNED=2 (#2409, #2410); roster-drift 64b1f82a3/b29cd8d23=6, same ref twice=0
RESULT codeowners_gap uncovered_files=0; field_coverage ok; agreement divergent=0 unregistered=0; policy_lint TOTAL 0 errors across 41 files; rules_sync ok; structure PASSED
RESULT closure select MODE: SCOPED -- 3 script(s) run (entities, harness_headers, layout), as the body says
RESULT body_check="5 routed, 0 unrouted, 0 bad" (live body, carry_audit at head)
RESULT merge_tree_vs_origin_main=clean (exit 0, origin/main 07a09406a)
RESULT resolution_delta: 03f1681a3 and 7c0383bc8 each have exactly the tree `git merge-tree --write-tree` of their parents gives (automatic, no hand resolution)
RESULT version_manifest_notes=untouched
RESULT CI head: fast (3.14), coverage, instrument-self-tests, mutation, typing, closure-scope, arch-score and budget-raise-gate all success

- Step 1 and step 14: the null controls were not re-run row by row (the M16 and M15b rows deleted, the census UNMAPPED counts). My hand mutants kill on exactly the rows the body names, which corroborates them. The `tests/closures.json` move is the two harnesses' `inert_reads` rows, and `tests/layout.json` adds carry_audit.py to the tools glob. No budget moves.
- Step 6 (class): round 3's class was the segment's boundaries. Paren, segment start, next marker, line end and code span are each now killed alone. The drive's census (152 sites, 0 unmapped) is the enumeration rule, and it returns no unmapped seam.
- Step 9: r10_carry_sweep_rows.py and r10_carry_parser_mutants.py are the fixer's own instruments, disclosed as such. The round-10 sweep has no committed finder harness, as rounds 1 to 3 recorded. My mutant scripts are my own.
- Step 10: the Forward-carry items name R10-TICK-DRIVERS (live in wave-r10-groups.json) and O10-policy-fixer-md (out of tree, UNVERIFIED, as the PR says).
- Step 12: the head is unchanged since dispatch.
- Note, not a block: two of my own mutants survive outside the drive's declared scope, which is the parser. The drive's census covers parser sites, not Dests.
  - D1: `dismissed:` with a reason of 1 word or more, against the docstring's "two words or more". It fails open, so "Carry: dismissed: nah" would pass. The rule itself only says `dismissed: <reason>`.
  - D13: load_dests no longer reads a carry file's `issue`. It fails closed. The self-test builds Dests directly and never runs load_dests's carry-file read.

  Neither needs a block. Each can take a self-test row in a later pass. Carry: O10-policy-fixer-md
