R10-COP-GATE part 6: leads 20 and 21 of the group's brief (its `carry` list on `handoff/audit-r10-roster` b1e9fe0bda6cad7e9f8a066a427c7afdec32231a, 21 entries, cited 1-based), measured and confirmed, then fixed at the attribution owner #3005 uses. Part of #2262 (the group's roster `fixes` list is empty).

A meter reading taken at an interval's close stood for that interval's space figure even where the pump's mode dwell had run hot water inside it. Two readers did this:

- **Lead 20, `_interval_space_power`** (the power the house learners replay). It split the reading by the plan's commanded split. On a switch-back window (0.45 h hot water, then 0.05 h space, under a space-only plan), it booked the whole 2.2 kW reading as space power for the interval. Without a power entity it booked the 2.2 kW ask the same way.
- **Lead 21, `_record_accuracy` into `draw_range.fold`.** The running-space filter judged the cycle by the pending plan split. The same window, and one that ran hot water up to the close, folded one sample each into the space draw range. That range is what `follows_ask` reads, so the COP eligibility read it as well.

The fix adds `heat_energy.ran_hot_water(a)`, which is `a.observed and a.dhw > 0.0` on the interval's `Attribution`. Both sites read it through `heat_energy.meter_of(...).attribution(split)`, the owner of the dwell-or-plan choice that `_fold_flow_lift`, `_cop_reference_curve` and `_interval_measured_heat_kw` already use.
- `_interval_space_power` returns `None` (skip the sample) on both its metered and unmetered paths.
- `_record_accuracy` folds neither a running nor an idle reading, because a hot-water run is neither.

An unobserved interval (no mode entity, a combination mode, a stale read) keeps each site's plan rule unchanged. No threshold moved: `COP_BASELINE_MIN_SAMPLES`, `COP_TRACKING_ERROR_GATE`, `_COP_CURVE_SHARE` and the draw range's floors are untouched.

Alternatives (fixer.md step 17):
- **Prorate the reading by the dwell's space hours.** Lost: the reading is a point sample at the close, and `heat_energy.space_heat_kw` already rules that a point reading is the interval's only where it served space alone. Prorating would be a second rule beside that owner.
- **Reuse `_fold_flow_lift`'s `dhw_share > _COP_CURVE_SHARE` gate.** Lost: that share is the curve's blend tolerance for a supply temperature. A metered kW has no such tolerance, and a 0.15 h hot-water run would still book its hours as space.
- **Pass the dwell into `draw_range.fold` as a new flag.** Lost: it would widen a pure module's signature to say what the coordinator can decide by not calling it.

## Head

`f40be9c9756ba7cc84ba7a5daa77e1ba449b0b05`, four commits on merge base `be7584c4904e243ffb48c166be39221623d81415`:
- `b3faa54d1` the fix and its checks;
- `2c7f05d8a` the structure payment (condensed comments);
- `9c601202f` the `tests/structure.py --record` of the two improved rows;
- `f40be9c97` the mutation ledger: five `killed_by` pins and the removal of the stale `_record_accuracy` GUARD_OFF pin `b36c07ff`.

`f40be9c97` touches only `tests/mutation_ledger/` JSON. The figures taken at `9c601202f` therefore describe this head's code and checks: `git diff --stat 9c601202f f40be9c97` lists only five ledger paths (git pairs the removed `b36c07ff` pin with the new `fe5030a3` one as a rename), and the closure selection at both SHAs prints the same `scope.run`.

`git merge-tree --write-tree origin/main HEAD` exited 0 against origin/main `4822c8f9b7f7ca6201cea05a9c80f7797e5f56a6` (taken 2026-10-31). Main was not merged in (fixer.md step 6).

## Mutation proof

Driver: a fresh `git worktree add --detach` of `9c601202f` per mutant, so `.git` is present. Each mutant is one exact replacement asserted to match once, then `PYTHONPATH=tests/hastub python3 tests/features.py` in that worktree. The driver is a seat-scratch script, not in the tree.

- **The fix removed** (`coordinator.py` restored to the merge base, which drops both sites): `3 of 4642 FEATURE CHECKS FAILED`, the three new checks:
  - `FAIL a switch-back interval gives the house learners no space power; an all-space dwell books the reading and an unobserved one the plan's subtraction, as before (nulls)  [{'switch-back': 2.2, ...`
  - `FAIL without a power entity a switch-back interval books no commanded space power; an all-space dwell books the ask (null)  [{'switch-back': 2.2, 'all-space': 2.2}]`
  - `FAIL a hot-water dwell under a space plan folds no running-draw sample; an all-space dwell and an unobserved interval fold one each (nulls)  [{'switch-back': 1, 'hot water to the close': 1, ...`
- **Site 1** (the `if heat_energy.ran_hot_water(...): return None` lines in `_interval_space_power` deleted): `2 of 4642 FEATURE CHECKS FAILED`, the first two checks above.
- **Site 2** (`and not heat_energy.ran_hot_water(...)` dropped from `_record_accuracy`'s fold condition): `1 of 4642 FEATURE CHECKS FAILED`, the third check above.
- **`ran_hot_water`, `and` to `or`** (BOOLOP): `features.py` dies with `TypeError: unsupported operand type(s) for -: 'NoneType' and 'float'` after `FAIL without a power entity the commanded space figure is all there is`. That is an existing check; an unobserved plan split now refuses its sample.
- **`ran_hot_water`, `a.dhw > 0.0` to `a.dhw >= 0.0`** (CMP_BOUND): `3 of 4642 FEATURE CHECKS FAILED`, the three new checks; the all-space nulls refuse (`'all-space': None`, `'all-space': 0`).
- **`ran_hot_water`, `a.observed and` removed** (an unobserved plan split with hot water then refuses): the same `TypeError` and `FAIL without a power entity the commanded space figure is all there is`; in the fast driver, the first new check failed on its `no dwell, planned hot water` arm.
- **The head itself**: `ALL 4642 FEATURE CHECKS PASSED`.

## Null control

- In every new check, the all-space dwell (0.5 h space) books its 2.2 kW reading, books the 2.2 kW ask without a power entity, and folds one draw sample, at the base and at the head. An interval with no dwell (`Segment(..., None)`, unobserved) also keeps the plan's rule at both ends: with a planned 1.0 kW hot-water share and a 3.2 kW reading, `_interval_space_power` returns 2.2, and a space plan folds one draw sample.
- Carry 1 (an install whose draw follows the plan still reaches a COP model): companion harness `dev/audit/harnesses/r10_cop_gate.py` (sha1 d03dd93508936796fba5ec07ce387d393c9d8b60), `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_cop_gate.py`, at the merge base `be7584c49` and at head `b3faa54d1`. Both print `RESULT synthetic.follows.folded=12/12 refusal=None observability=draw_follows_plan` and `RESULT synthetic.selfset.folded=0/12 refusal=draw_off_ask observability=not_measurable`. The readings are flat because its fixtures carry no mode dwell, which this diff needs before it acts.

## Figures

- The leads, measured before any code. A seat-scratch probe (sha1 f9c5a98a3bb5a0c0d3af0a409e75dc7f0e631729, not in the tree; the three new `tests/features.py` checks carry the same arms) builds the coordinator with a power entity, sets the meter's `cycle` and `dwell.segments` directly, and calls `_interval_space_power()` and `_record_accuracy()`. At the merge base `be7584c49`:
  - switch-back (0.45 h hot water, 0.05 h space): `space_kw=2.2`, `draw samples folded=1`;
  - hot water to the close (0.05 h space, 0.45 h hot water): `2.2`, `1`;
  - all-space 0.5 h: `2.2`, `1`;
  - no dwell: `2.2`, `1`.

  At `b3faa54d1`: `None`, `0` for both hot-water arms, and `2.2`, `1` for both nulls. Both leads were confirmed, so both were fixed (each lead's text: "Only if confirmed").
- The finder's harness, `dev/audit/rounds/round10/study-ident/owner_rows.py`, is not run at either end. It reads the owner's private diagnostics bundle by path, and that bundle is not available to this seat (the seat brief forbids reading it). It measures gate pass shares on the owner's accuracy rows, which carry no mode dwell, so this diff would leave it flat. Its companion `r10_cop_gate.py` is under `## Null control`, and it is flat at both ends.
- `PYTHONPATH=tests/hastub python3 tests/features.py` at `9c601202f`: `ALL 4642 FEATURE CHECKS PASSED`, three of them new.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` at `9c601202f`: `MODE: SCOPED -- 22 script(s) run, 11 scoped out.` Then `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` at `9c601202f`: 20 of the 22 scripts exited 0, among them `ALL 4642 FEATURE CHECKS PASSED`, `NO UNCLAIMED DRIFT` and `NO STALE FIXTURE` (56 each, so no golden fixture moved and both claim files stay byte-identical to the merge base), `STRUCTURE RATCHET PASSED`, `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED` and `ALL 112 HARNESS HEADER CHECKS PASSED`. Two failed on this host, and this diff reaches neither: (1) `node tests/card.mjs` aborted on V8's `OOMErrorHandler` (out of heap). Re-run alone with `NODE_OPTIONS=--max-old-space-size=8192 node tests/card.mjs`, it printed `ALL CARD CHECKS PASSED`, exit 0. (2) `tests/entities.py` raised `PermissionError: Cannot get task port` at module level in `_hb_stdlib_reads`. That is the CPython 3.14 `_remote_debugging` sampler, which macOS refuses without the `com.apple.system-task-ports` entitlement, the host failure #3005 recorded. Re-run with that module marked absent (`sys.modules['_remote_debugging'] = None`, from a seat-local driver kept out of the tree), it printed `ALL 2490 ENTITY CHECKS PASSED`, exit 0. CI's Linux `tests` lanes are the authority for both.
- `PYTHONPATH=tests/hastub python3 tests/structure.py` at `2c7f05d8a`: `class_excess_loc 17655 (budget 17656, -1)` and `max_class_loc 8060 (budget 8061, -1)`, `2 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED`. Before the payment, at `b3faa54d1`, it printed `FAIL class_excess_loc 17661 > 17656 (+5)` and `FAIL max_class_loc 8066 > 8061 (+5)`. That was paid in `2c7f05d8a`, which condenses the v5.3.0 comment in `_interval_space_power`, the pairing comment in `_record_accuracy` and the new docstring sentence. `9c601202f` records both rows, and the commit message names them. At `9c601202f`: `STRUCTURE RATCHET PASSED`.
- `bash tools/pr/prepr.sh body.md` at `f40be9c97`, without the closures skip, ended `PRE-PR: f40be9c9756ba7cc84ba7a5daa77e1ba449b0b05 ... rc=0`. It printed `CI PREDICT: no closures, fast, governance or instrument red predicted against be7584c4904e`, `CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s), at origin/handoff/audit-r10-roster b1e9fe0bd`, `claim files: byte-identical to origin/main` and `self-test 429 passed, 0 failed`. The closures step is left to CI on this non-Linux seat, as prepr itself prints.
- Class enumeration (fixer.md step 8). Rule: `grep -n "_commanded_split()" custom_components/heatpump_optimizer/coordinator.py`, plus `grep -n 'pending\["split"\]\|pending.get("split")' custom_components/heatpump_optimizer/*.py` for the split the pending prediction carries. At the head the first returns 8 sites:
  - `_fold_flow_lift` (`:883`), `_interval_measured_heat_kw` (`:916`) and `_fold_measured_cop` / `_cop_reference_curve` (`:4975`): already attributed through `heat_energy` (#3005, #2854).
  - `_async_learn_heat_span` / `close_span` (`:1088`): the meter splits by its own dwell.
  - `_commanded_power` (`:4695`): the total, not a duty split.
  - `_interval_space_power` (`:4717`): closed in this diff.
  - The pending prediction's `split` (`:9846`), read only by `_record_accuracy`'s fold (`:9751-9752`, the second grep's two hits): closed in this diff.
  - `_propagated_slab`'s `draw_range.space_draw_kw(...)` (`:1013`): the same plan-against-dwell shape on the slab estimate. It is gated on the live mode only, and its rule for a hot-water-only mode is a confident 0 kW, not a skip, so the dwell-aware rule there is a choice (prorate or plan fallback), not this diff's predicate. It is not measured here and is named under `## Forward-carry`.

## Architecture score

- `coord_footprint` 2380 -> 2382: `python3 tools/audit/archscore/score.py --diff be7584c4904e243ffb48c166be39221623d81415` at `9c601202f` prints `Architecture score: dS -0.0012 WORSENS (inadmissible: coord_footprint 2380->2382)`. The two statements are the new `if ... ran_hot_water(...)` and its `return None` in `_interval_space_power`. The predicate itself lives in `heat_energy`, the attribution's owner. The coordinator method is where the house learners' sample is refused, beside its other refusals, and no existing statement there can absorb an early return that both the metered and the unmetered path need. The second site adds a term to an existing condition and no statement.

## Unpinned sites

- `custom_components/heatpump_optimizer/coordinator.py:4718 GUARD_OFF`: killed and pinned in this diff (`tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.cd19f403.json`, killed by `tests/features.py`).
- `custom_components/heatpump_optimizer/coordinator.py:9751 GUARD_OFF`: killed and pinned in this diff (`..._record_accuracy.GUARD_OFF.fe5030a3.json`). It replaces pin `b36c07ff`, whose line this diff extends.
- `custom_components/heatpump_optimizer/heat_energy.py:252 BOOLOP`, `CMP_BOUND` and `RETURN_DEL`: killed and pinned in this diff (`tests/mutation_ledger/killed_by/heat_energy.py/ran_hot_water.{BOOLOP,CMP_BOUND,RETURN_DEL}.39172521.json`).
- All five were driven by `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base be7584c4904e243ffb48c166be39221623d81415 --jobs 3 --scripts tests/features.py` at `9c601202f`, with the stale pin removed. It printed:
  - `baseline tests/features.py: rc=0 failed=0`;
  - `null control custom_components/heatpump_optimizer/coordinator.py:370 NULL_COMMENT survived tests/features.py`;
  - `PIN KILLED: 5 pinned, 0 left unpinned`, rc=0.
- The first drive, before the stale pin was removed, refused with `MUTATION TABLE REFUSED -- the ledger disagrees with the deterministic inventory` on `b36c07ff`. That is the ledger red `prepr.sh`'s CI-predict step named (`STALE PIN ... _record_accuracy GUARD_OFF b36c07ff`), and it is repaired before the handoff.

## Red checks

none

## Forward-carry

- B, the heat-pump grade's drivers (carries 6, 7, 14 and 17 of R10-COP-GATE's `carry` list): `compose_scores` publishes `envelope_drivers` only, and the card's `scoreDrivers` already reads `machine_drivers` once it exists. Not started here: it is a separate surface (score composition, card renderer and hover strings) from this diff's attribution seam. It already stands in the group's brief. Carry: R10-COP-GATE
- D, the learned top's consumer (carry 12): `DrawRange.planned` returns `None` unless `engaged`, by design. Letting a learned top reach the plan changes what it books, which is against the architect note's "no threshold change", so it needs a designer's ruling (designer.md) before a fixer, as #3005 recorded. It already stands in the group's brief. Carry: R10-COP-GATE
- New, from this diff's step-8 enumeration: `_propagated_slab` (`coordinator.py`) advances the unsensed slab by `draw_range.space_draw_kw(..., coord._commanded_split(), space_served=signals.space_heat or not signals.mode_observed)`. That is the running draw apportioned by the plan's split and gated on the live mode only, so a switch-back interval advances the slab by a hot-water run's kW as space heat. Unmeasured. MEASURE FIRST on a switch-back dwell, with the all-space dwell as the null. If confirmed, the rule is a design choice: the slab's own rule books a hot-water-only mode as a confident 0 kW, so prorating by the dwell's space hours competes with falling back to the plan's trajectory. Route it through `heat_energy.meter_of(coord).attribution(...)` (`ran_hot_water` for the skip). Destination: a new carry in R10-COP-GATE's `carry` list in `dev/programme/rosters/wave-r10-groups.json` on `handoff/audit-r10-roster`. Carry: R10-COP-GATE

## Friction

none
