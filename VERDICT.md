Fix review: merge ffec33d8db7221a473096d955bd1a9ffc10b475c

bus-nonce: 0e52a9c7e2de18cb54d9da6cba6e04a1

Round 1. Measured head ffec33d8db7221a473096d955bd1a9ffc10b475c (authored code head d1afdcf87; the head adds only dev/programme/delivery/3059.md). Detached worktrees at the head and at the base a7dd7f50d.

## Findings

- The mutation-ledger-push job runs only when `needs.mutation-ledger.result == 'success'`. With `fail-fast: false` and four matrix legs, one failed or cancelled shard (including a runner loss) skips the push, so the other three shards' kills are uploaded as artifacts but never pushed that night. The old single job had the same all-or-nothing rule, but one failure now costs up to four times the measured work. Not exercised until the cron fires. Carry: R10-FLY-LEDGER-SAMPLE
- Only shard 1 saves the pool-seconds cache, so the next night's `--pool-seconds` bound is seeded from shard 1's timings (merged over the prior seed) and not from all four. This is a bound cover rather than a verdict, so the effect is a looser bound. Carry: R10-FLY-LEDGER-SAMPLE
- The PR changes `dev/governance/rules/ci-autofix.md` (policy) and its generated copies. It needs the owner's approving review at the head or a mandate in force; the body says approval is owed and not given. I note it and do not decide it. Carry: dismissed: owner approval is owed on the PR itself (CLAUDE.md, 0009 step 6) and is outside a fix reviewer's verdict

## Evidence

- ev/HEAD.txt holds the head reviewed. CI: `merge_train.py classify ffec33d8db7221a473096d955bd1a9ffc10b475c` printed GREEN (pending: none, red: none).
- Merge with main: `git merge-tree --write-tree origin/main ffec33d8db7221a473096d955bd1a9ffc10b475c` exits 0 with no conflict (ev/mergetree.txt).
- Entity suite: `PYTHONPATH=tests/hastub python3 tests/entities.py` prints ALL 2497 ENTITY CHECKS PASSED at the head and ALL 2493 at the base (ev/entities-head.txt, ev/entities-base.txt). The body's "1 of 2497 FAILED (template arm, rc=1)" does not reproduce here: the head is green and the base is green, so that red was not this diff's. The mutant runs below also show no template-arm failure.
- Mutation proof, each in its own worktree at the head, suite rerun (ev/mutant-m*.txt): all killed, each run ends "N of 2497 ENTITY CHECKS FAILED".
  - m1, `cap *= shard[1]` deleted from drain_pool: 1 failed, "--drain --shard K/N: the shards are disjoint whole-anchor slices whose union is the unsharded slice ..." no longer passes.
  - m2, survivor union replaced by the last shard's list in merge_pin_shards: 2 failed, that check and "the survivors are written by each pin shard, merged as a union ...".
  - m3, closure.AUTOFIX_SURVIVOR_GRADED emptied: 2 failed, "mutation-autofix is red on an applied measurement that left a site alive ..." and the pin-shard survivors check.
  - m4, my own: drain_pool's shard k also returns shard 1's anchors (overlap): 1 failed, the same disjoint-slices check kills it.
  The `hb:positive_control` lines that differ between runs are timing noise, not the diff's.
- Null control (the body's): the unsharded drain_pool at the same total cap is covered by the disjoint/union check, which passes at the head.
- Survivor path, read from code: survivor_sites keys on `UNPINNED <key> -- lives` only. A budget-cut, cut-tail or timed-out site prints another verdict and does not redden, so "left unpinned" stays green. A hand-mutant that is an in-table site and lives goes red, as designed, and the report names it. A `tools/` hand-mutant outside the table is never driven, so it stays out of reach, as the body's refusal for #2579 and #2820 says. `skip-head-moved` and `skip-not-allowed` stay quiet through AUTOFIX_SURVIVOR_GRADED.
- Check names: the nightly's `mutation-ledger` job runs only on main and not on push or PR, and `mutation-ledger-push` keeps its id. Neither is a PR check, and the ruleset query returned no required contexts for these jobs. No required-context name is created or renamed. Matrix legs show as `mutation-ledger (1..4)` only in the nightly.
- Push race: there is one push job, downloading `mutation-ledger-*` and merging through merge_pin_shards. There are not four writers, so no race exists.
- Policy: `node tools/policy/policy_lint.mjs --budgets` shows ci-autofix.md at 91 lines (cap 96) and 1466 tokens (cap 1469), so 3 tokens of headroom. `rules_sync.mjs --check` prints RULES-SYNC ok, so the .claude and .cursor copies match. `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED.
- Claim files byte-identical in the three-dot diff; VERSION untouched; the delivery row dev/programme/delivery/3059.md is in the three-dot diff. The packet's FIGURES line: 5 resolved, 0 not verified. carry_audit: 3 routed, 0 unrouted.
- Forward-carry: R10-FLY-LEDGER-SAMPLE in handoff/audit-r10-roster (dev/programme/rosters/wave-r10-groups.json) names run 40054585693 as the baseline and the step rules (clip -> --max 70; timeouts -> --jobs 3 --max 65; kills under a quarter three nights -> one shard). The controls are recorded and not dropped.
- R10-PIN-DRIVE-INCONCLUSIVE: I judged "stale: not reproduced" by reading main(): `return verdicts.stop` (tests/mutation_table.py:4179-4180) precedes pin_results, so an INCONCLUSIVE drive prints no PIN KILLED summary. I did not rerun the scratch-worktree drive at the base and head, and I did not mutate the new ordering check. This is a limit of my review and not a failure.
- Not measurable before the cron fires: the matrix leg timings against the 240-minute budget, `--jobs 4` CPU contention, artifact download of `mutation-ledger-*` patterns, and the shard-count/step rules.
- Round 1 of this review. No mutant survived.
