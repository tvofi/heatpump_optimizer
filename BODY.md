Part 2 of 2 of R11-SEAM-store (the persisted store seam), roster group R11-SEAM-store-p2. Refs #3744, #3757, #3758 (left open). Part 1 merged as #3875.

The previous seat's BLOCKED.md (handoff-wip/r11-seam-store 34cb956da2) asked whether carries 0-1 were a second part or part 1's. The recommended option was taken: they are dispatched as this second part, and part 1 merged without them.

Carry 0 (P1 sweep, six store loaders admitting a stored boolean as a number) is built here, once, at the store's load boundary. `QuarantiningStore.async_load` walks each document against its `DOMAINS` trie (`store._unflag_numbers`) and reads a `bool` at a `real`/`int` declaration as `None`, the absent value every loader already defaults. No loader is patched. `in_domain` already refuses a flag at a numeric declaration, so writers and loaders now agree with the one schema at load as well as in the Arm 6 census.

Carry 1 (P2 sweep, three DHW weekday/weekend window readers) is already implemented on main, by R11-SEAM-entity-service (865dff33d6, dbaf42a411). All three readers resolve the day through `dhw_schedule.windows_in_force`, the registered owner of `tests/entities.py`'s P2 fact `dhw_window_in_force`, and `tests/features.py`'s D17-s3-51 block pins them. This PR adds no P2 code. Its evidence is under `## Figures`.

Carries 2-4 (D3 wave fold, class I1, #3755) were re-derived at the merge base with `d3_fnstate.py` on `D3-FOLD.json` (both at e8aefbb452):
- D3-g03 (`_async_load_energy_totals`, BOOLOP on the `since` guard): pinned.
- D3-g12 (`_storable_sample_count`, CMP_BOUND at both ends of `0 <= count <= 2**31`): pinned.
- D3-g11 (`_learned_pair`, `value > 0` to `>= 0`): the patch is already killed at the merge base by `tests/finite_boundary.py`'s "a stored fold with a zero or negative value is dropped and the least positive one is kept" (part 1), and the ledger already holds `_learned_pair.CMP_BOUND.26881a60`. It is a non-finding for the judge, not a pin.

Alternatives considered for carry 0:
- **Patch each of the six loaders' `isinstance(x, (int, float))`.** This is the brief's refused per-loader patch. It leaves every later numeric loader to repeat the exclusion.
- **Route each loader through `store.admitted`.** `dhw_draws.py` and `tariff.py` are model modules. `store.py` imports model modules and Home Assistant, so importing it there adds a cycle and an HA import to a model module (fixer.md step 17). `_tries()` is also uncached, so a per-element `admitted` call rebuilds the trie for every stored draw event.
- **Rule at the boundary (taken).** One rule, already fed by `DOMAINS`. It covers every store, the snapshot ring's aliased learner payloads included, and costs one walk per load.

## Head

a0b598938dd0579445b4992b4b3be8ee15f60f71, merge base 7194ff84c09dd9d54a99f8208c906136981fd9dc (origin/main at 2026-11-27).

## Mutation proof

Each mutant was run with `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py "# R11-SEAM-store-p2 (round-11 sweep P1"`, and the line was restored afterwards:
- Delete `data = _unflag_numbers(data, node)` in `QuarantiningStore.async_load`: 2 of 4 fail, "a stored true where a number is declared loads as absent at each of the six loaders the P1 sweep named; ..." and "every numeric declaration in store.DOMAINS loads a stored true as absent, every flag one as true; ...".
- D3-g03 patch `isinstance(since, str) and since` to `or`: 1 of 4 fails, "a stored energy-totals start that is empty or not text is no start; an ISO day is (D3-g03)", reading `{'empty': '', 'number': 20260101, ...}`.
- D3-g12 patch `count <= 2**31` to `<`: 1 of 4 fails, "a stored sample count of 0 or exactly 2**31 is kept; -1 and 2**31 + 1 are refused (D3-g12)".
- D3-g12 patch `0 <= count` to `0 < count` (the line's second CMP_BOUND mutant, which shares the ledger key `713016cb`): the same check fails, reading `['refused', 2147483648, 'refused', 'refused']`.
- D3-g11 patch `value > 0` to `>= 0`: `tests/finite_boundary.py` at the merge base reads `1 of 122 FINITE BOUNDARY CHECKS FAILED` (the check named above).

Ledger rows added under `tests/mutation_ledger/killed_by/coordinator.py/`: `HeatPumpOptimizerCoordinator._async_load_energy_totals.BOOLOP.aa0e01fc.json` and `_storable_sample_count.CMP_BOUND.713016cb.json`. `tests/mutation_table.py --list BOOLOP|CMP_BOUND` now reads `pinned` at coordinator.py 8340 (BOOLOP) and at both line-471 CMP_BOUND mutants.

Rows for the five mutants of the new `store._unflag_numbers` (GUARD_OFF at its dict and list tests, BOOLOP at `numeric` and at its return, RETURN_DEL), each driven against the block above and red under it: `tests/mutation_ledger/killed_by/store.py/_unflag_numbers.{GUARD_OFF.710abac2,GUARD_OFF.c8d051b9,BOOLOP.adb1a211,BOOLOP.ed392b3b,RETURN_DEL.ed392b3b}.json`; `tests/mutation_table.py --list` reads all five `pinned`.

Diff mutants: MUTANT_CMD=`python3 tools/audit/seat/features_block.py "# R11-SEAM-store-p2 (round-11 sweep P1"`; prepr's line, verbatim: `ok       diff mutants           [14s] no survivor among the diff's first 40 mutant(s) under: python3 tools/audit/seat/features_block.py "# R11-SEAM-store-p2 (round-11 sweep P1"` (at e8aaf72e00; the later commit adds ledger rows only).

## Null control

- The features block's six-loader check loads the numbers stored beside each `true` as stored: `dhw_energy_kwh` 4.0, off_restore `c` 20.5, reservoir 2.0, peak 3.0.
- The census drives every `flag` declaration with `true` and requires it to load as `true`.
- The D3 pins pass on the unpatched tree.
- The P2 companion's `--perturb` (weekly windows unset, every reader on the flat union) reads 3 of 3 failed.

## Figures

- P1 end-to-end companion, six loaders through their own `QuarantiningStore` loads with a stored `true`: `PYTHONPATH=tests/hastub python3 $EXPORT/p1_e2e.py` (sha1 d909bdfa07d900189a5e4bbf00226602a64a5eaf). It reads `RESULT stored_true_read_as_one=6 of 6` at 7194ff84c0 and `0 of 6` at the head.
- In-tree finder harness: `PYTHONPATH=tests/hastub:. python3 dev/audit/rounds/round11/sweep/P1/D14/sweep-P1/p1_probes.py` reads `store_bool_admitted_as_number=6 of 7` at both ends. Its store arm calls each loader with a hand-built payload, past the store load where the fix sits, so it measures what the fix rightly leaves alone. The companion above and the features block apply the tree's own load to the same inputs.
- Likewise, `python3 dev/audit/rounds/round11/sweep/P1/D14/sweep-P1/p1_seams.py` (family bool-number) still lists the six loaders as FLAG. Its rule reads a function's own `isinstance(x, bool)` test, not the boundary upstream of it.
- The enumeration rule for carry 0's class is the census in the features block: every `DOMAINS` pattern whose declaration is `real` or `int`, one stored `true` each, through a `QuarantiningStore` load. It returns every numeric declaration of every store, and each loads as absent. Its check asserts it drove a numeric declaration of each of the six loaders' stores (dhw_draws, accuracy, energy, ledger, off_restore, dhw_legionella).
- Census residue, by category:
  - a map key (`~`): JSON text, never a flag;
  - an alias pattern: it mirrors a store whose own patterns are driven;
  - a payload a writer of this package builds in-process and never stores: no writer stores a flag where it declares a number, which Arm 6 of `tests/finite_boundary.py` checks against the writers.
- The P1 enumerator's other 16 bool-number FLAG sites are not store loaders (config flow, diagnostics, payload readers) and are outside carry 0.
- P2 companion, the three production readers at Saturday 07:00 on "weekdays 06:00-08:30, weekend 08:00-09:30": `PYTHONPATH=tests/hastub python3 $EXPORT/p2_companion.py [--perturb]` (sha1 9f4877fd4f444bb182e71fd729209fc054f84a62). It reads `RESULT companion_failed=0 of 3` at 7194ff84c0 and the head, and `3 of 3 (--perturb)`.
- The SW8 harness (`probes_p2.py` from 872510cd3e, sha1 5058a46432166867f8e75a5d4846acea20d0b752, run from a scratch root) reads `probes_failed=3 of 6` at 7194ff84c0. Its boost arm passes. Its VVC arm re-implements the pre-865dff33d6 call (`vvc_should_run(hour, list(p.dhw_windows))`), its label arm calls `window_label` on the flat set itself, and its `probe_zone` needs a module (`rig`) outside both trees. None of those three drives production.
- D3 re-derivation: `python3 -I d3_fnstate.py D3-FOLD.json HEAD --group R11-SEAM-store-p2 --ids` (files at e8aefbb452) reads `same 2 changed 1 gone 0 module 0`, with `_learned_pair` changed (part 1's `least` parameter).
- Scoped gate: `python3 tests/closure.py select --diff 7194ff84c0` reads `MODE: SCOPED -- 23 script(s) run, 11 scoped out`. Each named script was run with `PYTHONPATH=tests/hastub`, golden under `GOLDEN_MODE=drift` against the merge base: all 23 rc=0.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Architecture score: `python3 tools/audit/archscore/score.py --diff 7194ff84c09dd9d54a99f8208c906136981fd9dc` reads `Architecture score: dS +0.0000 NULL`.

## Red checks

none

## Unpinned sites

none: the five sites `ci_predict.py` named at e8aaf72e00 are pinned by the rows under `## Mutation proof`.

## Forward-carry

- D3-g11 (`_learned_pair` CMP_BOUND, `value > 0` to `>= 0`) is already killed at the merge base, so it returns to the judge as a non-finding (ADR-011 decision 4). Carry: dismissed: killed at the merge base by tests/finite_boundary.py, ledger row _learned_pair.CMP_BOUND.26881a60
- The in-tree P1 harness's store arm (`p1_probes.py` `arm_store_bool`) calls loaders past the store load, so a re-run reads 6 of 7 at this head too. The features block is the rerunnable measurement. Carry: dismissed: a round's harness records its round; the features block re-measures the class

## Friction

none
