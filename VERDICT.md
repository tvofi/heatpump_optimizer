Fix review: merge 1d3b792575aa15072dd0614c23d2c184d8ffdf0b

bus-nonce: cdb182f2648538e5f6c6236b1b8f7fc2
pending-ci: gate

## Summary

Round 2: the delta after my round-1 block at 8ca95413 (`blocked mutation-vacuous`, probe/rev-3869-8ba22bbd 7c308abb). I reviewed the delta (tvofi 2026-11-09). That is `git diff 8ca95413 1d3b7925` restricted to this branch's own commits. The rest of the range is main merges and the `mutation-autofix` pin commit 1aa635d2.

- Production delta: one line, 8630bbf58c. It adds `entry_config._leg_minutes` to `_DEFAULTED_NUMBERS`. `_leg_minutes` returns the default for a non-finite value and for one outside 0..PLAN_STEP_MINUTES, so it is a defaulted parse like `_interval_minutes`. The `_MIG_NUMERIC_PARSES` census line in tests/entities.py matches it.
- Test delta: T6b, T6c, T6d and T6e in tests/features.py, each with a null control. ff7aa67a is comment-only.
- Every repair the block asked for is built. (1) A heating leg at the plan's end is kept: T6b(a). (2) Idle steps join the pump's hot-water leg: T6c. (3) A space-first short heating leg is kept: T6b(b).

## Findings

- `custom_components/heatpump_optimizer/duty_switch.py:592` survives when `current == wanted` is dropped (M17). It is equivalent on every input: both later branches return `current`, which equals `wanted`. The site is on the body's Unpinned sites list, so `mutation-autofix` triages it. Carry: dismissed: equivalent mutant; the PR's own mutation lane records its disposition

## Evidence

- Head reviewed: 1d3b792575aa15072dd0614c23d2c184d8ffdf0b (`ev/HEAD.txt`). Its tree, 7ad3a1d6, is identical to 39b182d75f's, the SHA the body measured at. Merge base b18edd59. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.
- `git merge-tree --write-tree origin/main <head>` at origin/main f52e700d: rc 0. `LEDGER-MERGE: resolved` structure_budgets.json and closures.json (`ev/merge_tree.txt`).
- RESULT round-1 block resolved (step 1). I ran my round-1 driver (`ev/mutant_driver.py`, mutant texts unchanged from 7c308abb) over the R11-OWNER-MODE-LEGS block, `# --- R11-OWNER-MODE-LEGS (#3859)` to `# --- R10-CEILING-PROBE (#2498`. Baseline: `ALL 19 FEATURES BLOCK PASSED` (`ev/ml_block_at_head.txt`). Results are in `ev/mutants_mode_legs_block.txt`:
  - M09, R2's left side dropped: killed by T6b.
  - M10, R2's right side dropped: killed by T6b.
  - M12, forward fill `before` -> `IDLE`: killed by T6c.
  - M08, `leg_minimum` clamp dropped, a round-1 survivor I had read as equivalent: now killed by T6e.
  - M01, M11, M20 and M24 were re-run as controls: all killed.
  - M17 (`duty_switch.py:592` `current == wanted` dropped) survives. It is equivalent: with current == wanted, both later branches return `current`, which is `wanted`.
- The duty-switch block baseline at the head reads `ALL 90 FEATURES BLOCK PASSED` (`ev/ds_block_at_head.txt`), equal to the body's 90. I stopped a full 24-mutant re-run over that block after M01 and M02 (both killed, `ev/mutants_duty_switch_block_partial.txt`). The production code it covers is unchanged since round 1, where the same driver killed 19 of 24.
- The one production line, 8630bbf58c (`ev/entry_config_mutant.txt`). At the head, `number_repairs` on stored `"abc"` and `None` for the two leg keys returns repairs for both. With `_leg_minutes` removed from `_DEFAULTED_NUMBERS` in memory, it returns `{}`, so the line carries the migration repair. The body's entities.py half-application figures (`1 of 2761` per half) were not re-run.
- Step 14: `python3 tests/structure.py` at the head prints `module_excess_loc 21768 <= 21768`, `STRUCTURE RATCHET PASSED` (`ev/structure.txt`). Main's budget reads 21775, so the branch lowers it by 7, as the body states (21779 -> 21772 at 8ef4). I judged that move earned in round 1, and the delta adds no production line counted against it.
- Step 5: `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (three-dot). The claim file adds `config_flow` only, unchanged since round 1.
- Step 10: the forward-carries to R11-OWNER-FAULT-HOLD and R11-OWNER-FROST-HOLD are on `handoff/audit-r11-roster` f19b546a. The FAULT-HOLD carry now names its own pin, "the fault hold wins with a young leg latched", which resolves my round-1 follow-up. carry_audit at the head: `3 routed, 0 unrouted`.
- Step 16: `_kept_leg`'s hold is bounded by the minimum (0..15 min). Its release is pinned by T2, as in round 1. The delta adds no actuator path.
- Step 2: there is no finder's harness, because the issue is an owner feature. The fixer's `dev/audit/harnesses/mode_legs.py` figures were re-derived in round 1, and the delta does not touch the harness or the code it measures.
- Step 11, owed reds. `tests / mutation` is red at this head with `MUTATION TABLE REFUSED -- 1904 unpinned site(s) against 1860 ..., 45 of them added by this diff`. The body's `## Red checks` answers it: `mutation-autofix` pins the new sites, which is the ci-autofix path, and `tests / mutation-pins` shards were running. The `gate` failures read `FAIL run(s) [45554090363] at this head are still being judged`. `nightly-ha` and `nightly-status` are not in the owed-reds set. CI state: `ev/classify_poll.log`.
- CI wait: `merge_train.py classify` read `WAIT 1d3b7925... pending: gate red: none` on every poll from 07:13Z to 07:44Z (`ev/classify_poll.log`), with `tests / mutation-pins` shards still queued or running. The `pending-ci: gate` line hands the post to the relay.
