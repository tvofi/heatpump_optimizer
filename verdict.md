Fix review: merge 903c0ed1bf439a5f1548388dc30aaa20c31578f0

bus-nonce: cdcac2f26339f3a978e025a465238b18
pending-ci: gate

## Summary

Round 1 (first review, full scope). Reviewed at head 903c0ed1bf439a5f1548388dc30aaa20c31578f0, merge base 38bf516bdd73f926ee9639ffda7b9ca5163fd50e. `OptimizationConfig.start_price` returns `CLAMPED_DEFAULT_START_PRICE` (0.1) for a clamped install configured at zero and the configured `cycling_cost` otherwise. Every optimizer reader now reads it. The mutation proof, the finder's harness at both ends, the null controls and every figure in the body re-derive at this head.

## Evidence

- RESULT mutation proof: I deleted the two `start_price` lines (optimizer.py 2754-2755) in a separate worktree and ran the body's `features_block.py` command. It printed `2 of 54 FEATURES BLOCK FAILED`, both on the named checks; the restored head printed `ALL 54 FEATURES BLOCK PASSED`. Files: ev/mutant-start_price-deleted.txt, ev/block-head.txt.
- RESULT targeted mutant: CMP_BOUND on 2754 (`not self.cycling_cost >= 0`) fails the same 2 of 54. File: ev/mutant-2754-CMP_BOUND.txt.
- RESULT finder's harness, both ends: I ran `dev/audit/harnesses/r11_honest_starts_runs.py` (sha1 02db0c09c2a54545f840c23d8a7a4de69275aecf, the head's file, copied onto the base tree) in modes `grid` and `defaults`, at the current merge base 38bf516bdd and at the head.
  - `grid`, clamped unpriced row: base `edges 5, energy_kwh 2.93, objective 7.6826`; head `edges 2, energy_kwh 2.75, objective 7.8664`.
  - `grid`, priced clamped null row (0.25): `edges 2, energy_kwh 2.75, objective 8.1664` at both ends.
  - `grid`, unpriced duty-cycle cells that entered the stage: 0 at both ends.
  - All of these match the body. Files: ev/harness-{base,head}-grid.txt.
- RESULT `defaults`: the ladder is identical at both ends (diff empty apart from timing).
  - Row 0.0: grid 5 / 2.93 / 1.4128 / 20.19, everything_on 5 / 69.57 / 63.2857 / 17.91, cycling_cost 7 / 42.04 / 32.0354 / 16.87.
  - Row 0.1: grid 2 / 2.75 / 1.3980 / 20.22, everything_on 4 / 69.94 / 63.4567 / 17.97, cycling_cost unchanged.
  - Null pairs: all six array-equal at default 0 against 10.0, `null pairs that differ 0`, rc 0 at both ends. Every number matches the body's tables.
  - At the head the nulls run through the tree's own rule: the harness patches `om.CLAMPED_DEFAULT_START_PRICE`. Files: ev/harness-{base,head}-defaults.txt.
- RESULT class rule: the body's rule (`git grep -n "\.cycling_cost\b\|cycling_cost=" -- custom_components/`) returns the 3 sites it names: coordinator.py:6239, the writer, and optimizer.py:2754 and 2756, the property.
  - A broader `git grep cycling_cost` over custom_components finds only the option plumbing upstream of the property: const.py, config_flow.py:1869, entry_config.py:158 and coordinator `_effective_cycling_cost`. No other solve-side reader exists, so the class is closed.
  - `tests/features.py` pins it through the `inspect.getsource` check.
- RESULT the deleted `_commit_runs` early return is unreachable at the head. It needed an engaged solve with `start_price` not above 0, but `_engaged` is `start_price > 0 or clamp`, and a clamp now implies `start_price` 0.1. Only a test-patched default of 0 reaches the old state, and the two re-anchored fixtures do exactly that.
- RESULT attack, other price profiles and houses (reviewer-built, not the finder's instrument: ev/attack-price-scale.py, output ev/attack-price-scale.txt). Setup: the harness's `_grid_solve` clamped at configured 0, default 0 against 0.1, on four cells (p_min 1.1 and 0.53; loss 0.4 and 1.0; outdoor means 8, 2 and -5), with prices scaled x0.1, x0.25, x1 and x3.
  - In 16 of 16 rows the default never adds a start.
  - It removes starts in 4 rows.
  - The largest drop in the lowest room temperature is 0.19 K (p_min 1.1, x0.25: 20.40 to 20.21, energy cost 0.6240 to 0.4436). That is the objective trading slack comfort for a cheaper plan, not a breach.
- RESULT VERSION, manifest, RELEASE_NOTES.md, both claim files, `*_budgets.json` and tests/closures.json are untouched. The three-dot diff over them is empty.
- RESULT goldens: no golden scenario sets `clamp_planned_levels` (grep of tests/golden.py and tests/golden/ is empty), so the change cannot move a golden. This agrees with the body's `env_drift.py --all` pass; I did not re-run it.
- RESULT merge: `git merge-tree --write-tree origin/main 903c0ed1bf` exits 0 against origin/main 4ecca4cc58; no conflict.
- RESULT role contract: `git diff <merge-base>...origin/main -- dev/governance/roles/` touches only architect-planner.md, so fix-review.md is current.
- RESULT body head: the body names 903c0ed1bf as head; I measured that head.
- RESULT ten deleted mutation pins: each anchors a line whose text this diff rewrote (`cycling_cost` to `start_price`) or deleted. They are stale pins, not lost kills. The body declares the 11 resulting unpinned sites under `## Unpinned sites`, and `tests / mutation`'s red is answered under `## Red checks`.
- RESULT step 16: the diff adds no refusal on an actuator write, so no release is owed.
- RESULT CI: `merge_train.py classify 903c0ed1bf --pr 3697` printed `WAIT 903c0ed1bf439a5f1548388dc30aaa20c31578f0 pending: gate red: none` on every run, polled about every 90 s from roughly 03:52Z to 04:21Z; hence `pending-ci: gate`.
  - Live check runs at 03:5xZ: `tests / mutation` was red, the 11 declared unpinned sites, answered in the body's `## Red checks`; mutation-autofix owes the pins.
  - `tests / nightly-status` was red, inherited from main.
  - The superseded `gate` runs were red; classify reports gate red: none.
  - fast, replay, coverage, typing, closures, browser and mutation-pins were still running or queued.

## Notes

- Note: figure: the body's `## Head` also quotes 1b76f567ea and merge base b425502da8. I re-took the figures at the current merge base 38bf516bdd; they are identical.
- Note: figure: the body's quoted ruling says "the lowest room unchanged" for 0.1. Measured, the lowest room rises: grid 20.19 to 20.22, everything_on 17.91 to 17.97. That is consistent with "not lowered".
