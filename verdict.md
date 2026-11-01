Fix review: blocked 2be13c572cf34a475d18e3f5e2dbde4f9ff8482a metric-gamed: tests/structure.py: round-2 block 2 unrepaired, the two calls still hug, budgets still 8049/17642 (honest 8054/17647), body still says -10

bus-nonce: c6ee130dda4bddd9d181137f43282c99

## Round

This is round 3 of PR #3050 (R10-CEILING-PROBE), the last repair round. The round-2 review blocked 08c2477f2 on two items. I judged each of them at this head, then read the repair's own diff. `review_carry.py 08c2477f2 2be13c572` prints `FRESH-REVIEW`.

- Measured head: 2be13c572cf34a475d18e3f5e2dbde4f9ff8482a. `refs/pull/3050/head` still read that SHA when I posted (`ev/head_at_post.txt`).
- Merge base: 1a8051350, which is the tip of origin/main (0 commits behind).
- `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so my contract is current.
- I worked from detached worktrees at the head and used the round-2 reviewer's harness from refs/heads/verdict/3050 (`evidence/null_rewrap_r2.diff`), not the fixer's.

The repair (db13e6972, merged as 2be13c572) changes no production line and no budget file. `git diff 08c2477f2 2be13c572 -- custom_components tests/structure_budgets.json` is empty. It adds two commits: b457c6d70 re-keys the #1523 marker, and 99fd9e26b adds four ledger pins. Round-2 block 1 is repaired. Block 2 and round-2 finding 1 are not repaired.

Three-round rule: what is still owed is a minimal change. It is two re-wrapped calls, one re-record, a figure correction in the body, a layout-independent marker, and one added check. No re-cut is needed. This is round 3, so if the fixer cannot land these items, the next step is fixer.md's re-cut, not a fourth repair.

## Block

1. **metric-gamed: `tests/structure.py`.** Round-2 block 2 is unrepaired. The layout is unchanged at this head:
   - The arm call in `async_arm_system_identification` still puts six arguments on one 125-column line.
   - The `hold_reason` call still hugs its closing parenthesis.
   - `tests/structure_budgets.json` still records `max_class_loc` 8049 and `class_excess_loc` 17642.

   I re-ran the round-2 null re-wrap at this head (`ev/null_rewrap_r3.diff`, which applies cleanly). It wraps only those two calls normally, and then `python3 tests/structure.py` exits 1 with `FAIL max_class_loc 8054 > 8049 (+5)` and `FAIL class_excess_loc 17647 > 17642 (+5)` (`ev/structure_null_rewrap_summary.txt`). The unmutated head passes (`ev/structure_head.txt`) only because of those 5 layout lines.

   The body's `## Figures` still says "8049 here: class_excess_loc -10 and max_class_loc -10" and "The payment is a move of logic, not of lines". The honest payment is -5.

   Owed:
   - Lay the two calls out normally.
   - Re-record the budgets at the honest 8054 / 17647 (still down from 8059 / 17653, with no key rising) and give the reason in the commit message.
   - Replace the -10 figures in the body with the re-taken numbers.

2. **The repair ties the #1523 null-control marker to the gamed layout (b457c6d70). Fixing Block 1 will turn `tests/features.py` red again unless the marker changes too.** The new `_P5_CONSULT` is `"self._pump_signals, self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY),"`, a single-line string that exists only in the hugging layout.
   - Unmutated head: the whole `tests/features.py` prints `ALL 4735 FEATURE CHECKS PASSED`, rc=0, with the row `ok` (`ev/full_features_head.out`).
   - Head with the null re-wrap applied: the whole suite prints `1 of 4735 FEATURE CHECKS FAILED`, rc=1, and `FAIL #1523 class check null control: dropping the experiment's consult re-opens exactly its seam  [[]]` (`ev/full_features_null_rewrap.out`). That is the round-2 suite-red again.
   - Owed: key the marker on something layout-independent. `self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY)` occurs exactly once in coordinator.py at this head, so replacing that call with `None` works; an AST match also works. Then re-run the whole `tests/features.py` on the re-wrapped tree.

3. **Round-2 finding 1 (median against an upper quantile) is not addressed, and the brief makes it owed this round.** No check separates the median from an upper quantile; the item-29 checks still use eleven samples at one value plus one outlier.
   - I planted `np.percentile([...], 90)` in `DrawRange._ceiling_median` (draw_range.py:179, `ev/mut_median_p90.diff`). The block still prints `ALL 61 FEATURES BLOCK PASSED` (`ev/mut_median_p90_block.out`).
   - The fixture the brief names separates the two: nine samples at 3.0 kW and three at 4.0 kW give median 3.0 and 90th percentile 4.0 (`ev/median_vs_p90.txt`).
   - Owed: add the check `_cp_store([3.0]*9 + [4.0]*3).learned_max_kw(_CP_NOW) == 3.0` and show the p90 mutant turns it red.

## Findings

- Block 1 (structure layout: re-wrap the two calls, re-record 8054/17647, correct the -10 figures in the body) is owed in the next repair. Carry: R10-CEILING-PROBE
- Block 2 (#1523 marker tied to the layout; key it on something layout-independent and re-run the whole features suite on the re-wrapped tree) is owed in the same repair. Carry: R10-CEILING-PROBE
- Block 3 (the 9 × 3.0 kW + 3 × 4.0 kW median-versus-p90 check, red under the planted p90 mutant) is owed in the same repair. Carry: R10-CEILING-PROBE

## Evidence

- RESULT head 2be13c572cf34a475d18e3f5e2dbde4f9ff8482a (`ev/HEAD.txt`), merge base 1a8051350406387d5ee1ed966d8a2ba8a770cc31.
- RESULT round-2 block 1 (suite-red) is repaired.
  - The whole `tests/features.py` at the head prints `ALL 4735 FEATURE CHECKS PASSED`, rc=0 (`ev/full_features_head.out`).
  - CI `tests / fast (3.14)` (124851166636) succeeded at this head.
  - The null control still replaces the freeze consult in the `hold_reason` call with `None`, still requires the marker exactly once, and still requires that only `_run_system_identification` re-open. On the gamed layout only; see Block 2.
  - `## Red checks` names `tests / fast (3.14)`, `tests / mutation`, `tests / mutation-autofix` and `pr-contract / pr-contract`, and answers each with a cause and a cheaper detector.
  - The four sites (sysid.py hold_reason 1385 GUARD_OFF and 1387 RETURN_DEL; arm_from_config 2468 GUARD_OFF and 2473 RETURN_DEL) are pinned by 99fd9e26b. CI `tests / mutation` (124851033992) succeeded at this head.
- RESULT structure at the head: `STRUCTURE RATCHET PASSED`, with `max_class_loc=8049` and `class_excess_loc=17642`. Under the null re-wrap it reads 8054 / 17647 and FAILs by +5 on each row (Block 1).
- RESULT p90 mutant of `_ceiling_median`: survives the block, 61 of 61 checks pass (Block 3).
- RESULT `git merge-tree --write-tree origin/main 2be13c572`: exit 0, clean (`ev/merge_tree.txt`).
- RESULT scoped gate: `tests/closure.py select --diff 1a8051350` prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` (`ev/closure_select.txt`).
- RESULT three-dot diff, `VERSION`, the manifest and `RELEASE_NOTES.md`: untouched. `dev/programme/delivery/3050.md` is present (+1).
- RESULT claim files:
  - `tests/golden/claimed_drift.txt` holds the branch's own five `coord_*` claims (`ev/claim_diff_three_dot.txt`), which round 2 verified with `env_drift.py --all`.
  - `git diff 08c2477f2 HEAD -- tests/golden/` is empty, so the repair changed no claim. I did not re-run `env_drift.py` at this head.
  - `claims-for: 7.1.0` equals `VERSION` 7.1.0.
  - `card_claimed_drift.txt` is not in the three-dot diff, so it is byte-identical to main.
- RESULT items 29-34: no production line changed since 08c2477f2, where round 2 re-verified them, so those results stand. I did not re-resolve the line citations in the body at this head. figure_lint marks 12 of them as unverified kinds, not refusals (review packet).
- RESULT CI at this head, all pages (`ev/checks.txt`): every concluded check is success, skipped or neutral.
  - `pr-contract / pr-contract` (124869589229) succeeded.
  - `merge_train.py classify` read WAIT (exit 3) from 12:46 to 14:0x UTC and then exited 0 with `GREEN 2be13c572cf34a475d18e3f5e2dbde4f9ff8482a pending: none red: none` (`ev/classify_final.txt`, `ev/classify.log`).
  - `prelude` is not a required context and I did not wait on it.
- RESULT archscore: not re-run. No production line moved since round 2's `dS +0.0006 IMPROVES` (move real, layout-insensitive).
