Fix review: blocked 95b083063f3ebce013d38726bd329c729438bc7c root-cause-unanswered: mutation red at the head (5 added sites unpinned, one a live survivor); body stale

bus-nonce: 8288ef41ee345977760afb92049ada42

Reviewer seat review-2025-r6, round 6 of PR #2025 (R9-EG-B11, #1745). This is a delta review from 0662bd8e, run from the detached worktree /Users/timmalmstrom/hpo-seats/review-2025-r6/wt. The dispatch named 883eed10. The head then moved by the bot's `ci: pin killed mutants` commit (95b08306, ledger only, 58 added pins), and this verdict is at that head under the coordinator's re-issued nonce. `fix-review.md` is unchanged on main since the merge base.

**This is not a body-only block.** The mutation lane is still red at 95b08306 on 5 added sites. One of them is a live survivor. `mutation-pins` is skipped at this head (the `ci:` loop guard), so no second bot commit is coming. The fixer owes ledger or test work: `ci-autofix.md` says to run `--pin-killed` yourself when the autofix leaves sites, and to triage a survivor by hand, never by automation.

## What holds (no re-review owed next round)

### (a) Main merges
- **37ac4d84 and 883eed10:** `git merge-tree --write-tree` reproduces each tree exactly, and the remerge-diff is empty for both. On 883eed10 the stderr reads `LEDGER-MERGE: resolved tests/closures.json`, which is the driver.
- **b29e4ee4 (main 6b91e238) was resolved by hand.** merge-tree exits 1. The remerge-diff is 124 lines:
  - the `pump_arbiter.py` conflict (`_entities` silent slot), plus a hand edit of `_silent_target` to read `cfg.quiet_silent_windows` and `cfg.quiet_off_windows`;
  - `features.py` stand-ins moved from item writes to `with_config`.
  The body discloses all of these.
- **The b29e4ee4 resolution is equivalent.** I judged it with my own harness, `resolution_equiv.py`. It compares raw values against parsed fields for `silent_control_usable`, `_silent_rows` and `_inside_silent` (49 now-points over a week), plus the `from_mapping` fields. Result: `RESULT resolution_equiv comparisons=2702 mismatches=0`.
  - Perturbation (`_spec` maps blank to a real window): `mismatches=202`, so the harness moves.
  - No `CONF_` read is left in `pump_arbiter.py`. Every mapping read on main (lines 291-1056) maps to a parsed field.

### (b) Survivor kills
I applied each mutant in place, ran `PYTHONPATH=tests/hastub python3 tests/entities.py` (venv-ci 3.14.7), then restored with `git checkout`. The tree was clean after each.
- **Baseline at 883eed10:** `ALL 2225 ENTITY CHECKS PASSED`.
- **All 9 mutants KILLED.** Each fails exactly 1 of 2225 checks, the gate check, on the arm the body names:

| Mutant | Moved arm |
|---|---|
| M1 coordinator.py:5051 GUARD_OFF | (1, 1) |
| M2 :5462 BOOLOP | ((1.0,), (1.0,)) |
| M3 :6840 GUARD_OFF | (2.0, 2.0) |
| M4 :6840 BOOLOP | (0.5714, 0.5714) |
| M5 :8901 GUARD_OFF | ((False, 1), (True, 1)) |
| M6 :8934 GUARD_OFF | ((True, 0), (True, 1)) |
| M7 :10776 GUARD_OFF | (9.0, 9.0) |
| M8 entry_config.py:256 GUARD_OFF | (False, True) |
| M9 silent_mode.py:104 GUARD_OFF | ('TypeError', True) |

- **The tests pin behaviour, not formulas.** Each arm drives the real coordinator or `silent_mode` and compares produced values against literals. None re-implements a formula, and the on arm is the null control.
- **Dropping `_optional_number`'s `== ""` guard is equivalent.** All 4 call sites default to None, and `float("")` raises, which falls to that same default. Nothing outside `entry_config.py` uses it.
- **b21ed75e's two dropped pins are correct.** Their `old` text appears 0 times at the head. The rewritten sites (coordinator.py:9809 GUARD_OFF, pump_arbiter.py:572 RETURN_DEL) are listed in the body.

### Other checks
- `tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`.
- Against the merge base, `structure_budgets.json` only falls (max_class_loc 9048 to 8817, seam_cut_total 766 to 760).
- VERSION, the manifest, RELEASE_NOTES.md and both claim files are untouched.
- CI at 883eed10: fast (3.14), closures, coverage, typing, env-matrix and all ten mutation-pins shards are success.
  - `delivery-status` failure is main's window (`UNCHECKED -- 9 merge commits ...`), not this PR's diff.

## Blocking: mutation at 95b08306 (job 113224598923)

The job reads: `MUTATION TABLE REFUSED -- 4657 unpinned site(s) against 4670 at the ratchet base 0c25836e, 5 of them added by this diff`. The shard logs at 883eed10 give each site's status:
- `coordinator.py:6840 CMP_BOUND` (`snow_array > 0.0`): **lives**. This is a surviving mutant. The gate check's rain arm uses 1 cm of snow, so it never reaches the zero boundary. The fixer owes a kill, or a `survivor_triage` entry with the equivalence evidence.
- `entry_config.py:272 CMP_BOUND`, `entry_config.py:282 RETURN_DEL`, `legionella.py:194 GUARD_OFF`, `pump_arbiter.py:572 RETURN_DEL`: **skip-budget**. They were not started and never measured. Run `python3 tests/mutation_table.py --pin-killed --base origin/main` for these (CI's lane, or locally per ci-autofix.md). My round-5 R2 kill (the `amps > 0` guard dropped) suggests 272 is killable. 282 is the `__reduce__` restore, which the round-4 deepcopy check kills.

## Body changes (one pass)
1. **Head:** name 95b083063f3ebce013d38726bd329c729438bc7c (the bot pin commit over 883eed10), and whatever head the fix above produces.
2. **Red checks:** add `mutation` at 883eed10 (job 113187473136, REFUSED, 63 added unpinned) and at 95b08306 (job 113224598923, 5 added unpinned), each with its answer. The section currently names only bfaf5486's run.
3. **Unpinned sites:** 58 sites are now pinned by 95b08306. The 5 above are still listed as "pinned by mutation-autofix", which is false at this head. Give each its real disposition (killed and pinned, or triaged).
4. **Figures:** the entities count is 2218 at b21ed75e and 2225 at the main-merged head. Say which head each figure is for.

Evidence: /Users/timmalmstrom/hpo-seats/review-2025-r6/ev. It holds:
- HEAD.txt and mutate_r6.py
- run_mutants.sh, ent_M*.txt and mutants_summary.txt
- entities_R0_head.txt
- resolution_equiv*.py and resolution_equiv*.txt (run against `git archive 883eed10 custom_components tests/hastub`, kept outside evidence at /Users/timmalmstrom/hpo-seats/review-2025-r6/head_tree)
- remerge_*.diff and mt_*.err
- structure_head.txt
- checkruns_head.tsv, cr_poll*.tsv and cr_new_head.tsv
- joblog_mutation_*.txt, shard_*.txt and residual_unpinned.txt
- pr-body.md
