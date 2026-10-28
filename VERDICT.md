Fix review: blocked 1a13f2b3b97a2164d32308f12c5f6816e6a67bf2 metric-gamed: tests/structure.py class_excess_loc: 14 of 8005c528's 21 lines are line-joins that improve nothing

Round: delta review (round 2 on #2745) of d2cd24dcdfee19518416e299b8ac3207b92bc8b3..1a13f2b3b97a2164d32308f12c5f6816e6a67bf2. Measured head 1a13f2b3b97a2164d32308f12c5f6816e6a67bf2, which was still the head (ls-remote refs/pull/2745/head) when I posted.

## Blocking

`8005c528` ("ledger: pay the merge's MonthlyLedger growth in its own formatting") pays 21 lines of `class_excess_loc` (18096 -> 18075, re-recorded 18076 -> 18075). Null control (fix-review step 14): I took the commit's own ledger.py change and re-expanded only the pure line-joins, keeping the guard collapse.

- RESULT class_excess_loc=18096 with the commit's ledger.py change reverted
- RESULT class_excess_loc=18089 with the guard collapse only (`baseline_kw is None or not all(np.isfinite(...))`)
- RESULT class_excess_loc=18075 at the head

So the guard collapse is a real simplification and earns 7 lines. The other 14 come from joining the two `self.add(...)` calls, the `add_savings_settlement(...)` keyword call and `line()`'s return dict onto fewer lines. No code changes there. `fixer.md` step 17 says "Never move a metric by a change that does not improve the code". `tests/structure.py`'s definition of `class_excess_loc` says "only lines that go -- copies merged, dead code deleted -- lower it". The same move works on any class over the limit, so the diff's change is that move.

Owed: pay the remaining 14 lines with a change that improves the code (a simplification, removed duplication or dead code in any class over the limit), or take the raise path (`CLAUDE.md` rule 2, the owner's confirmation before the push). Then re-pin the mutants the pay moves, as `82e51032` did.

## Verified (these survive a re-cut of 8005c528 that leaves the rest of the delta alone)

- **Held-cost semantics survive #2834.** Merge `aef1a2595` resolved the coordinator conflict to #2834's `**price_tiles.monthly_deltas(...)`. In `price_tiles.monthly_deltas` it changed main's `sim.baseline_cost - live.baseline_cost` to `sim.held_cost - live.held_cost`. That matches the branch's pre-merge coordinator formula `simulated.held_cost - result.held_cost` at d2cd24dc. On this branch `baseline_cost` became the comfort-matched reference (#2492). `held_cost` keeps main's old `baseline_cost` meaning: optimizer.py:4611 `held_cost = float(energy_cost_of(baseline_power))` is taken before the reference is re-targeted, and 4898 is the same on the other path. So the key's meaning on main is preserved. `price_tiles.py:141`'s key selection is unchanged. Evidence: `ev/resolution_aef1a2595.diff`.
- **The payment changes no behaviour.** `all(np.isfinite(v) for v in ...)` short-circuits in the same order as the `and` chain, and `None` is still checked first. The other hunks only re-wrap code.
- **Claim files.** The `claimed_drift.txt` resolution keeps this branch's R10-SAV-COMFORT claims and main's coord_* R10-ADVISOR-RESIDUE claims. It drops the stale R10-CARD-VOICE coord_* lines. `claims-for: 7.0.4` equals `VERSION` 7.0.4.
- **Release files untouched.** The three-dot diff touches neither `VERSION` nor `RELEASE_NOTES.md` nor `manifest.json`.
- **Merges cleanly.** `git merge-tree --write-tree origin/main 1a13f2b3` (main 3b4180dc) exits 0.
- **Structure gate.** `python3 tests/structure.py` at the head exits 0, `ok class_excess_loc 18075 <= 18075`. Output in `ev/structure_head.txt`.

## Not verified

- **env_drift.** I did not run `env_drift.py --all`, because the block above does not depend on it. A re-cut head owes it.
- **The fixer's 4 local gate reds.** I did not reproduce them on main: stress shoulder, entities heartbeat, the card.mjs OOM, and optimality winter_narrow|shoulder. This needs re-checking at the re-cut head.
- **Mutation pins.** I did not re-run `82e51032`'s pins (ledger.py:225 GUARD_OFF, :265 RETURN_DEL). Re-cutting 8005c528 re-keys these sites, so they are owed again anyway.
- **CI and the body's root-cause answers.** I did not read the CI check-runs or the PR body's red-check answers at this head.

bus-nonce: 8cd35a44bf2eb1e4bb4de7b5758e53c6
