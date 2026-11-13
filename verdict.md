Fix review: merge dc727c4d8fbf98a3fe9ef93feb16c428912eb78b

bus-nonce: bcf93034c8b3ae3874f786275181ac48
pending-ci: gate

Round 2, the delta review after `blocked 69078d59 class-open`. I measured at head dc727c4d8fbf98a3fe9ef93feb16c428912eb78b, which merges the authored head bace7b74 into e59e21fe. The round's own delta is 6f396cce..bace7b74 (six commits). The scope is that delta plus the prior block, per fix-review.md step 12.

## Evidence

- RESULT prior block closed. The capacity seam is now guarded: `_held_unreachable` has a pump bound at `max_electrical_power`, priced at `_reference_cop`, and the bisection runs on valved and unvalved installs alike.
  - The prior verdict's own instrument (`ev/cap.py`, unchanged) at the head reads: 4 kW unvalved, held room -1.577, power 4.000, dS +0.0000; 4 kW valved, held -0.928, power 4.000, dS +0.0000; 9 kW, held 21.000, dS +0.0000 (`ev/cap_head.txt`).
  - At the base e59e21fe the same instrument reads dS -1.0724 / -1.0762 (`ev/cap_base.txt`), so the instrument moves.
- RESULT breadth, my own probe (`ev/probe2.py`). It covers none/manual/smart_read/smart_write × both zonings × default/two_tank_4way × pumps of 3/4/6/9 kW × valve targets 25/40 × outdoor -30..5 C, 560 cases in all.
  - Head: bad 0, draws below -0.02 kWh_th 0, maximum sag 33.1 K, every held room in [outdoor, 21] (`ev/probe2_head.txt`).
  - Base: 204 draws, worst -1.8375 (`ev/probe2_base.txt`).
- RESULT wood tank and humidity, my own probe (`ev/wood.py`). It runs two_tank_4way with the wood tank at None/15/85 C, humidity None/95, and pumps of 4/9 kW at -25/-5 C: 144 of 144 cases ok, no draw (`ev/wood_head.txt`).
- RESULT the class enumeration. The body's rule is every cap, clip or derate on `_compute_baseline_power`'s path, each listed with its disposition, and the fixer's census `dev/audit/harnesses/r10_sav_held_capacity_census.py` covers it. At the head the census reads `cases 1728 of 1728, worst first-step dS +0.0000, over 0.02 kWh_th 0`, with controls matching the body (`ev/census_head.txt`). The census is the fixer's instrument and is disclosed as such in the body; my probes above are an independent check of it.
- RESULT mutation proof, my own driver over the group's block (`ev/mut2.py`, `ev/mutation_proof2.txt`; each mutant restored and the tree clean afterwards):
  - P1, pump bound to `return False`: 1 of 10 FAIL (the capacity check).
  - P2, valve bound off: 1 of 10 FAIL.
  - P3, entry `if False:`: 2 of 10 FAIL.
  - P4, bisection step: 2 of 10 FAIL.
  - P5, final assign dropped: 2 of 10 FAIL.
  - P6, COP to `cop_nominal_floored`: 1 of 10 FAIL.
  - P9, the span's `min()` dropped: 1 of 10 FAIL (the warm-day check).
  - NULL, a comment edit: `ALL 10 FEATURES BLOCK PASSED`.
  - P7 and P8 survive; see Findings and the line below.
- RESULT P8, the survivor where the pump bound reads `need_kw` in place of `made` (dropping the tank's standing loss): the block passes. Probe2 under P8 has no draw, and its worst dS is +0.0325 kWh_th, a charge rather than a draw (`ev/survivors.txt`). It is near-equivalent at the default parameters. Carry: dismissed: measured, its largest effect is 0.03 kWh_th per step of charge at a 3 kW pump at -30 C, and nothing is drawn
- RESULT the finder's harness `r10_sav_residual_attribution.py` at the head (`ev/harness_head_*.txt`).
  - Residual +6.84 % flat and +3.38 % `winter_typical`.
  - Reference stored +11.11 kWh_th; non-steady -6.83 / -7.46.
  - `plant steps seen 192 of 192`.
  - Every figure matches the body (measured there at 056abe4d). The base figures, -3.90 % / -8.02 %, were taken by the round 1 review.
- RESULT the forward-carry item, the apportion seam's +11.11 kWh_th, is confirmed by the harness above. The body routes it to R10-SAV-VALUATION-RESIDUE (parts 2 and 3). `carry_audit` at the head resolves all 3 routed items, as the packet shows.
- `git merge-tree --write-tree origin/main dc727c4d...`: exit 0 against origin/main e4ca2d94 (`ev/merge_tree.txt`).
- `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden/` are untouched by the three-dot diff (`ev/version_untouched.txt`).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` (`ev/structure.txt`).
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` at the head: `ALL 2709 ENTITY CHECKS PASSED`, rc=0 (`ev/entities.txt`; the FAIL lines in that log are its positive controls).
- The body's head SHA is dc727c4d, the head I measured; the authored head bace7b74 is named.
- Mutation ledger delta: the deleted rows key lines the rewrite removed. The two triage rows (CONST 40 -> 80, and the pump bound's `>=`) argue equivalence within the 2**-40 bracket, consistent with the bisection. I did not re-measure them.
- Figures I did not re-derive: the gate line `29 TEST SCRIPT(S) PASSED`, the scope line, `ci_predict.py`'s 7 unpinned sites, the split probe (scratch, not in the tree), the census at 69078d59, and the archscore `dS +0.0000`. CI's heavy runs are cited, not re-run.
- Red checks: the body answers `tests / mutation` (the `ADDED UNPINNED` sites, left to `mutation-autofix`), `gate` (derived), `pr-contract` at 11dc22c8 and `arch-score` (an outside 503). `nightly-status` is outside owed-reds. I checked that each trigger was answered, not the answer itself.
- CI at this head: `merge_train.py classify` prints `WAIT ... pending: gate red: none` (rc 3, `ev/classify.txt`), unchanged over about 30 minutes of polling from 02:55 to 03:25 UTC, so this returns `pending-ci: gate`.

## Findings

- P7, a non-equivalent surviving mutant on a line this PR added. Replacing `humidity = None if weather.humidity is None else float(weather.humidity[0])` with `humidity = None` passes the group's block (`ALL 10 FEATURES BLOCK PASSED`), yet it moves the held state. Setup: a learned defrost derate (0.6 at 2 C / 90 %), humidity 90, two-zone, unvalved, 1 kW pump, 2 C outdoor. Held room 16.976 at the head against 19.436 under P7; at 4 C, 16.939 against 21.000 (`ev/humid_compare.txt`). The booked reference does read humidity: `_compute_baseline_power` gives 1.0875 kW dry against 1.2834 kW at 90 % (`ev/humid_ref.txt`). So the head's code is right and the defrost bound the body lists as closed is unpinned. The body's "pin the step-0 humidity read" kills only the `humidity[1]` index swap. Owed: a capacity row with a learned humid derate and a humidity series, run as a failing-first check against this mutant. Carry: R10-SAV-VALUATION-RESIDUE
