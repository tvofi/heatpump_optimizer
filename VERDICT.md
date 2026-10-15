Fix review: merge e6f3837585f0aa83952eb4828c4576587fd50c07
bus-nonce: 961bfb58890bbc8e6226155ceba6828e

Round 2. This verdict reviews the repair of my round-1 block (comment 6200939369, at 48d926c1c).
Evidence: /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/rev-pls/evidence2

## The repair delta

The repair delta is c5079e654 (parent 48d926c1c). It touches only tools/policy/policy_lint.mjs and tools/policy/friction_issues.mjs, and its only non-comment line is one self-test sample string (`git diff -U0`, non-comment lines filtered).

1. policy_lint.mjs, the REWORK_CLASS block: the "rows stop partitioning" and "already in it by the word" sentences are gone. One paragraph now defines both rows. The verdict `head-moved` row holds the blocked verdicts carrying that word, and the rework row is `rounds.reverify`, whatever the word. This matches the code.
2. friction_issues.mjs 22-31: the rework row is named `head-moved (rework)`, and the bare `head-moved` is the verdict-class row. This matches the code.
3. friction_issues.mjs ~776, the self-test sample I did not list: `grep -cF` finds its tail verbatim in policy_lint's `not opened:` message with REWORK_KEY substituted (count 1). That is the property its own comment claims. `friction_issues.mjs --self-test` prints 102 passed, 0 failed.

## The main merges

230113434 and e6f383758 merged cleanly. `git diff 48d926c1c e6f383758 -- tools/policy/policy_lint.mjs tools/policy/friction_issues.mjs` is exactly the repair delta, so main brought nothing into either file. `git merge-tree origin/main e6f383758` exits 0.

## Finder's harnesses, re-run at e6f383758

- blocks_friction.mjs: PROD verdict_row[head-moved] prs=4 entries=4 = block_class[head-moved]=4.
- friction_key_split.mjs: split_keys=0.
- enumerate.py: SEAMS 30 hist_mixed 0 canon_unguarded 21.
- r10_stats_window.mjs: verdict_head_moved=4, blocked_head_moved=4, rework_entries=130 = reverify_entries=130, verdict_total=434 = parsable_total=434.

The base-end figures and the mutation proof are from round 1 (copied here, M1 3 / M2b 1 / M3 2 / M4 5 failures). The production code they mutate is unchanged since then.

## Other checks

- Lint: `policy_lint.mjs` prints TOTAL: 0 error(s) and FIXTURE ok.
- Version, claims: VERSION, the manifest and the claim files are untouched.
- Checks: the 17 required checks of ruleset 23698884 are green at e6f383758, read from the check-runs API.
