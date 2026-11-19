Fix review: blocked ee9bfa8ac5c2c5cc5454f3c636cb627bcb29d565 mutation-vacuous: custom_components/heatpump_optimizer/plan_slots.py:89 lives: M1 (dict.fromkeys back to set) passes the D1-s1-51 tie check under some hash seeds, so the check's "whatever the hash seed" is not what it tests

bus-nonce: 660d8f04cbd4468a25be894b27de8a28

## Block

- M1, `plan_slots.py:89` `max(dict.fromkeys(codes), key=codes.count)` back to `max(set(codes), key=codes.count)`, run in a worktree at the head against the PR's features block (`features_block.py`, marker `# --- R11-SEAM-solver: the start set brackets`): ALL 9 FEATURES BLOCK PASSED under a random hash seed, rc=0 (ev/block-mutant-M1.log). Under fixed seeds: PYTHONHASHSEED=0 rc=1 (killed), 23 rc=0, 76 rc=0 (ev/M1-seeds.txt). The unmutated head passes at 23 and 76 too.
- The cause: for a two-element set the iteration order is insertion order when both strings land in the same table slot, which happens under some seeds. In that case `set` also returns the slot's first code for both spellings of the tie, so the check cannot tell the mutant from the fix. Over seeds 16-120, `max(set(...))` returned the first code for both orders at seeds 23, 24, 76 and 84. The body's M1 "FAIL" was one draw.
- Repair: make the check independent of the process's seed. For example, run the two tie spellings in subprocesses over a fixed seed list that includes a colliding seed (23) and a non-colliding one (0). Or check the order-preserving property directly, with a tie whose set order disagrees with its first code under the running seed. Re-run M1 at seeds 0, 23 and 76.
- The production fix is sound: `dict.fromkeys` keeps first-seen order, so a tie goes to the slot's first code under every seed. This block is on the pin only.

## Previous findings

- At bdf09624 the block was tests/doc_claims.py (2 of 411). Resolved: at this head `tests/doc_claims.py` reads ALL 439 checks PASSED (ev/local-doc_claims.log), and 61f2f4bbb2 rewords how-it-works.md to the five starts.
- Owed from the previous round, the other mutants (M1, M3-M6) and the other three `tests / fast` failures. The mutants are re-run here (ev/mutants.txt). M3, M4, M5 and M6 are killed; M1 is above. The fast failures are named in the body (`env_drift.py` confidence_margins, claimed at db6f2a664b, and `stress.py`), and `tests / fast (3.14)` is green at this head.

## Delta reviewed

`git diff bdf09624...ee9bfa8ac5`. The branch's own commits since bdf09624 are 61f2f4bbb2, 320c063489, bc33f25c50, d1e3701d13, 6a09ed087a, d63daa072e, f769d50c7f, a2236e189f and db6f2a664b. The rest are main merges (a7f9c27aee: the one `tests/features.py` end-of-file conflict, both blocks kept).

- Production delta, `optimizer.py` `_space_only_starts` (d1e3701d13, f769d50c7f). Byte-identical starts are kept once, first occurrence first. The reference-energy seeds are drawn unconditionally.
  - For covered == 0.0, `reference_power * (1.0 - 0.0)` is exact, so `energy == reference_kwh` bitwise and the filter drops the copies. The removed guard was dead.
  - `_wood_covered_share` returns a value in [0, 1], so no negative share adds a non-duplicate set.
  - Mutants: M7 (filter removed) is killed by `a space-only solve no wood covers hands the multi-start no duplicate start` [7 starts, 5 distinct]. M5 (reference-energy extend deleted) is killed by the whole-cover check.
  - Widened to `_space_only_starts`' callers only; nothing else in the delta touches the solve.
- `tests/stress.py` simulate allowance, with `tests/stress_budgets.json` `simulate_allowance` and the ratio 2.2 -> 7.46 (6a09ed087a, d63daa072e). The allowance applies to one scenario on one channel and expires once the baseline reads at or above 68093. `budget_table_problems` validates it. It carries four self-checks, whose mutants MA-MD the body reports (not re-run here). The body's `## Raise justification` names six payments and an `Architecture score:` line. `budget-raise-gate` is green at this head.
- `tests/features.py`, 320c063489 and bc33f25c50: the commit-stage checks now read candidate 1 as the descent's plan. Test only.
- Mutation pins (a2236e189f): three RETURN_DEL sites, killed per the ledger. Two ledger files are deleted for sites the diff removed. CI `tests / mutation` is green.

## Evidence

- Head: ee9bfa8ac5c2c5cc5454f3c636cb627bcb29d565 (ev/HEAD.txt). The live PR head was re-read before posting and is the same.
- Round: second (delta over bdf09624).
- `merge_train.py classify --pr 3736 ee9bfa8ac5`: `GREEN ... pending: none red: none` (ev/classify.txt). The packet's digest reads every required check success.
- `git merge-tree --write-tree origin/main ee9bfa8ac5` at origin/main e4a6cc6041: rc=0, no conflict (ev/merge-tree.txt).
- VERSION, manifest.json and RELEASE_NOTES.md: untouched in the three-dot diff.
- Local at the head: doc_claims.py ALL 439 PASSED; `env_drift.py --claims-only` rc=0; structure.py rc=0; the PR block ALL 9 PASSED.
- Finder's harness, D0-s2-01 `wood_seeds.py --race` over the finding's 7 cells from the plan/r11 export 819aa2e3 (sha1 1b03dd54), per-tree copies, on this arm64 host (numpy on Accelerate, not OpenBLAS). Summer_cool gap_abs, base cb8edb65 vs head:
  - winter_narrow 2.0292 -> 0.0022
  - winter_extreme 1.6782 -> 0.1210
  - winter_typical 1.6310 -> 0.0093
  - winter_moderate 1.3572 -> 0.0000
  - flat 1.6782 -> 0.1292

  At the head every summer_cool cell ships 3.0-3.8 kWh instead of 0, so the seed collapse is closed (ev/race-base.log, ev/race-head.log).

Note: figures-not-reproduced: the body's head race figures (0.0000, 0.0000, 0.0004, 0.0077, 0.0000) and its base shoulder figures (winter_typical 1.7251, flat 0.0001) do not reproduce on this host. Here winter_typical/shoulder reads 1.9945 at base and 1.7870 at head; flat/shoulder 1.3426 at base and 0.0002 at head.
  - A two-cell rerun at the head read flat/summer_cool 0.0043 where the seven-cell run read 0.1292 (ev/race-head-rerun.log). The race is order-dependent within one process, so its sub-0.13 residues are not a stable measurement on this host.
  - The previous head bdf09624 reads 0.1210 and 0.1292 on those two cells (ev/race-prev-bdf09624.log).
  - Bearing on the raise: the body rejects variant A for leaving 0.1287 and 0.1292 on winter_extreme and flat. This head reads 0.1210 and 0.1292 on those cells in one ordering here. The rejection rests on the fixer's host's figures, which this seat could not re-derive. Not re-derived: variant A itself, the stress counts (54/38 evaluations, 122592 simulate steps), MA-MD, and the `start_below_band` four-kernel claim.

Note: harness-unnamed: the review packet reports `Finder's harness: none named`. The body names the finder's scripts only through `$EXPORT` paths, which figure_lint cannot resolve.

## Red checks

None at this head: the classify read is GREEN, and every check in the packet digest is success or skipped. The body's `## Red checks` answers the reds at earlier heads and the cancelled jobs at this head, which have since been rerun green.

## Carry

Carry: dismissed: evidence, not a finding
