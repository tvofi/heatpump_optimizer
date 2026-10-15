Fix review: blocked 48d926c1c991774540afbe24b04992d0066a2477 other: docs-code-mismatch: two comments still state the old definition of the head-moved row, and this PR exists to give that row one definition. policy_lint.mjs 2743-2755 (rows stop partitioning; blocked head-moved already in the row by the word) and friction_issues.mjs 22-29 (rework counted under head-moved, files "recurring friction: head-moved")
bus-nonce: 5edbc89f9ae9588f3a86050aa0328f31

Round 1. Measured at 47f766f04b442e33bc6e193e2ee37e8d4fbb7f92. The head moved during the review to 48d926c1c991774540afbe24b04992d0066a2477, a github-actions `ci: merge main` whose delta touches no measured file (`git diff --quiet 47f766f04 48d926c1c -- tools/policy dev/audit/rounds tests/entities.py` is clean). So every number below holds at 48d926c, and both stale comments are byte-identical there. This is not `head-moved` against the fixer. Evidence: /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/rev-pls/evidence

## The block

1. `tools/policy/policy_lint.mjs` 2743-2748 at head: "So the rows stop partitioning the window's verdicts: the same round is one `merge` entry AND one `head-moved` entry". Lines 2753-2755: "only the first enters this row; a reviewer who wrote `blocked <sha> head-moved` on that round is already in it by the word". Both describe the deleted bump. The new paragraph at 2762-2768 says the opposite (the verdict map partitions; the rework row is `rounds.reverify`, word-independent). They sit in one block above `REWORK_CLASS`, so the source now gives the row two definitions, which is the defect this PR closes.
2. `tools/policy/friction_issues.mjs` 22-29 is the consumer of this output. It says the rework "is counted under the wave's `head-moved`" and that this lane "opens `[policy] recurring friction: head-moved`" on it. After this diff the rework files as `head-moved (rework)`, and `head-moved` is the blocked-verdict row. The body's Forward-carry discusses the title change but not this file. The self-test fixture at line 774 quotes the old message text. It is a parse fixture, so it can stay, but the header prose is a claim about behaviour.

Repair: rewrite both comments to the new definition. No code change is owed.

## RESULT lines (finder's harnesses, base 586455741 vs measured head 47f766f04)

- blocks_friction.mjs (sha1 fce9a961) over window.json (sha1 8c4de8e2, 185 PRs):
  - base: PROD verdict_row[head-moved] prs=71 entries=133; block_class[head-moved]=4.
  - head: prs=4 entries=4 = block_class[head-moved]=4; blocked_verdicts=124.
  - friction_prod_key_is_budget_file 66 -> 67; DISAGREE rows 2 -> 2 (budgets, fixer). This matches the body.
- friction_key_split.mjs (sha1 e1a54186):
  - base: split_keys=34 of moved_corpus_files=34; --perturb gives split_keys_perturbed=0 (plumbing_only 34).
  - head: split_keys=0. Its --perturb throws "perturbation anchor not found" at head, because the fix is byte-for-byte the finder's perturbation.
- sweep-I4/enumerate.py:
  - base: SEAMS 29 hist_mixed 2 canon_unguarded 25.
  - head: SEAMS 30 hist_mixed 0 canon_unguarded 21.
  - The set diff matches the body's dispositions: 2 MIXED -> single, 6 POLICY_KEY_INDEX -> guarded, 2 new entities _FK_MOVED rows, +39 line shift.
- r10_stats_window.mjs (the fixer's harness, disclosed as theirs; run by me at both ends):
  - base: verdict_head_moved=133, verdict_total=563 vs parsable_total=434, rework absent.
  - head: verdict_head_moved=4 = blocked_head_moved=4, verdict_total=434 = parsable_total=434, rework_entries=130 = reverify_entries=130.
  - The class line matches the body: record 16 of 32, fix 2 of 66, closure 1 of 2, docs 1 of 14, policy 1 of 6, test 1 of 6 = 22.
- Mutation proof (my mutants, tests/entities.py, venv 3.14):
  - M1 restore the bump: 3 of 2325 FAILED.
  - M2 drop canon in frictionKey: 1 of 2325 FAILED. My first M2 substitution did not match, which is recorded in mut.log; it was re-run as M2b.
  - M3 constant class: 2 of 2325 FAILED.
  - M4 empty rework row: 5 of 2325 FAILED.
  - These match the body.

## Other checks

- Version, claims: VERSION, the manifest and both claim files are untouched.
- Conflicts: `git merge-tree origin/main 48d926c1c` exits 0.
- Checks: all 17 required checks are success at 47f766f04. At 12aa30386 every non-green run is `cancelled` by the superseding push, and CodeQL is neutral (SARIF). None went red, so the body's "Red checks: none" holds. CI is re-running at 48d926c after the bot merge.
- Filer: the key change from head-moved to head-moved (rework) defeats no disposition. `disposedHere` keys on the window, so the closed #1990 suppressed nothing in a new window anyway.
