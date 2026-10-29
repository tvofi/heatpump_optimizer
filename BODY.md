R10-ADVISOR-WHATIF, the follow-on sub-PR that #2834's Forward-carry owed. Part of #2257. This body does not close the issue: item (1) below needs the owner's decision, and this seat cannot obtain it.

The brief has two items.

**(1) The Plan page's what-if panel. Not done; the owner must decide.** The panel prints `WhatIf.summary`'s money line from `monthly_cost_delta` alone (`heatpump-optimizer-card.js`, `summary`): "N less per month" or "N more per month than the current plan". The panel shows no caveat except the rate-limit note. That figure is the plan's own single-solve spend. It moves with where the house starts: the `whatif` arm reads `plan_moves_by_start 24` of 24 rows, and its held control reads 0 (Figures). `docs/dashboard-card.md` discloses the one-off in one place only, the Advisor's **Try in what-if** paragraph: "that panel prices the plan from the house as it is now, so its figure includes the one-off coast or heat-up a change starts with".

The brief allows two outcomes, and this seat can produce neither:
- **An estimator.** None of the three figures `price_tiles.monthly_deltas` already computes is sound for a draft:
  - the plan figure moves with the start;
  - the settled figure has the wrong sign across two schedules (`varying 00:00 target_minus_1 … settled +24.6`, `target_plus_1 … settled -25.5`, Figures);
  - the held figure is the thermostat baseline, which prices only the comfort part of a draft. A draft can also move hot-water windows, quiet hours and wood.

  A sound figure needs a new solve shape: both plans solved from a start held at each one's own schedule. That roughly doubles the what-if's solves on a Raspberry-Pi-class host and changes `async_simulate`'s contract. That is an L design for `designer.md`, not this size-S group with no architect note. Fixer step 17 says such a fix stops and asks the orchestrator, so this seat built none.
- **The owner's acceptance of the disclosed copy.** Only the owner can give it, and no live owner reached this seat.

  If the owner accepts it, one question remains: is the docs paragraph disclosure enough, or should the panel itself say so? Today the panel carries no caveat next to the figure.

  So #2257 stays open on item (1). Forward-carry routes it.

**(2) P141: the plan-slot summary builder leaves the coordinator.** Done.
- `HeatPumpOptimizerCoordinator._plan_slots` was a `@staticmethod` that read no coordinator state. It is now `plan_slots.plan_slots`, a pure module function, with its body moved verbatim (dedented, renamed). Its four call sites (`_build_plan_views`'s space and hot-water slots, `async_simulate`'s two slot counts) call it unchanged.
- It does not sit beside `PlanSlot` in `payload.py`, where the ruling first suggests. The function merges steps on `channel_heating_steps`. `payload.py` holds the payload's shapes on the standard library alone, and the optimizer imports it, so placing the function there would give the type module a runtime import of the model. The ruling's alternative, a small plan-view module, is what archscore reads as sounder.
- **A second move came with it.** With `channel_heating_steps` imported from `optimizer.py`, the new pure module reached the solver (scipy) and, through `tariff -> accuracy`, Home Assistant. Archscore read `layer_violations 13 -> 15`, `dS -0.1757 WORSENS (inadmissible)`. So `channel_heating_steps` and its threshold `CHANNEL_ACTIVE_KW` move from `optimizer.py` to `thermal_model.py`, beside `planned_draws_run`, the running rule they refine. `thermal_model` is rank 0 with a clean closure. The optimizer re-imports both names, so `optimizer.channel_heating_steps` still resolves for every caller. The coordinator now imports it from its owner.

Alternatives considered:
- **Into `payload.py` with a function-scope import of `channel_heating_steps`.** archscore counts a function-scope import as an edge (`layering.py`, `ALL_SCOPES = True`), so `payload` would join the violations and hide a cycle with `optimizer`.
- **A module-level function in `coordinator.py`.** This would drop the footprint too, but the ruling moves the function out of the file, and the coordinator still owns no part of this concern.
- **Pass the two heating masks in.** Every caller would compute them, which adds four call-site lines to the coordinator for a concern it does not own.

Follow-on edits that keep the tree's claims true:
- `docs/architecture.md` maps the new module and counts 84 modules, 55 of them free of Home Assistant.
- The P2 `channel_active_kw` fact's owner in `tests/entities.py` is `thermal_model.py::channel_heating_steps`.
- `tests/seam_map.json` drops `_plan_slots`. The class has no new method, so no new entry is needed.
- The round-4 D6 claims harness header reads 84 (its regenerated `claims.json` and `claims.md` are committed).
- The `tests/deployment_shape.py` note reads 102 files.
- Comments naming the old locations are corrected in `sensor.py`, `pump_schedule.py`, `tests/entities.py` and `tests/features.py`.
- `tests/plan_view.py`'s fake no longer binds `_plan_slots`.
- The callers in `tests/features.py` and `dev/audit/harnesses/r10_channel_running_rule.py` import the new function.
- Eleven mutation pins keyed on the moved functions' old scopes were STALE PINs (`ci_predict.py`) and are deleted. See Unpinned sites.
- `plan_slots.py` joins the measured closures of the 22 scripts whose closures read `coordinator.py`. These were recorded on Linux with `tests/derive_closures.sh --scripts-from … --record-only`, then merged with `closure.py merge --partial`. Two of the 22 had read the red tree, so `tests/entities.py` and `tests/harness_headers.py` were re-recorded with `--single` on the passing tree.

## Head

`badd0b11480cd08f04235d565767300323062b8a` (branch `handoff/r10-advisor-whatif`), cut from origin/main `88c6ad5bbec69bfe157e04597a74d0c9c3e4775c`, which is also the merge base. The gate ran at `eaac9d6b7`. The head adds one commit after it, the 19 ledger pins (`git diff eaac9d6b7 badd0b114 --stat` touches `tests/mutation_ledger/` only), and `tests/entities.py`, `tests/structure.py`, `ci_predict.py` and archscore were re-run at the head. At handoff (2026-10-29T18:12Z, `date -u`) origin/main is `ce5940c0d`, and `git merge-tree --write-tree origin/main HEAD` returns rc 0.

## Mutation proof

The ruling's mutant replaces `slot["shared_kwh"] = round(shared, 3)` with `pass` in `plan_slots.plan_slots` (the moved function). It ran in a detached worktree of `86e9f8d53`, where the moved function is byte-identical to the head's (`git diff 86e9f8d53 HEAD -- custom_components/heatpump_optimizer/plan_slots.py` is empty).
- `PYTHONPATH=tests/hastub python tests/features.py` -> `2 of 4574 FEATURE CHECKS FAILED`:
  - `a slot names the other channel's energy in its shared steps, by hand`
  - `a plan slot counts shared energy and reasons only where the shorter series reach`
- The capture comparison (below) fails too. The mutant's `space_plan.slots` carry 0 `shared_kwh` keys against 1 at the base, and its `dhw_plan.slots` carry 0 against 4, so neither list is identical.

The tree is restored (the mutant lived only in that scratch worktree).

**The moved sites, driven.** `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/features.py` ran on the tree:
- Baseline `rc=0 failed=0`; its null control (`thermal_model.py:127 NULL_COMMENT`) survived.
- 18 sites pinned, each `killed by tests/features.py`: plan_slots.py:59 CMP_BOUND, :72 GUARD_OFF, :74 BOOLOP, :74 CMP_BOUND, :76 GUARD_OFF, :78 GUARD_OFF, :82 BOOLOP, :82 CMP_BOUND, :84 GUARD_OFF, :92, :93, :95 and :98 GUARD_OFF, :100 RETURN_DEL; thermal_model.py:1237 CONST, :1252 GUARD_OFF, :1256 BOOLOP and :1256 RETURN_DEL.
- `thermal_model.py:1256 CMP_BOUND` survived `features.py`. The same run with `--scripts tests/guard_pins.py` pinned it (`killed by tests/guard_pins.py`). That is the script its pre-move pin, `optimizer.py:channel_heating_steps CMP_BOUND d964e804`, named.

## Null control

- **The move is behaviour-identical.**
  - `tests/plan_view.py` builds the published `space_plan` and `dhw_plan` from a real solve. It ran at the base and at the head, and both payloads it wrote were compared as sorted JSON: `space_plan` 2 slots and `dhw_plan` 9 slots at both ends, each list carrying `shared_kwh`; `identical True` for both lists and for the whole payload.
  - The fixture captures the ruling names publish no plan slots at all. In the five `coord_*` scenarios, `data.space_plan` and `data.dhw_plan` are `{}`, so a slot comparison over them is vacuous. The `plan_view.py` payload is the capture that carries slots, and the mutant above shows that it reads the field.
  - `env_drift` reads `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56 committed fixture(s)` against the merge base (Figures). The branch claims nothing, so both claim files are byte-identical to main.
- **The archscore null:** a whitespace-only move of `_plan_slots` inside `coordinator.py`, made in a detached worktree of the base (two blank lines before the method and two after it, `git diff -w` showing no non-whitespace change), reads `Architecture score: dS +0.0000 NULL`. So the footprint fall below comes from the method leaving the class, not from moving lines.
- **The harness, at both ends:** `r10_advisor_residue.py whatif` (sha1 `ffb5f71b132ed9547aeb05f7dd7429d366bf412c` at both ends) prints byte-identical output at the base and at the head (`cmp` exit 0). This diff leaves the what-if seam where it was, by design (item 1).

## Figures

- `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_advisor_residue.py whatif` (the finding's instrument, sha1 `ffb5f71b132ed9547aeb05f7dd7429d366bf412c`, unchanged by this diff). It ran at the head `eaac9d6b7` and at the base `88c6ad5bb` with identical output. A row moves when its three starts spread more than 1.0; the held figure counts any spread above 1e-9.
  - `RESULT whatif rows 24 plan_moves_by_start 24 held_moves_by_start 0`
  - `RESULT whatif caps rows 12 spread_by_start mean plan 45.7 settled 10.1; figures reading a saving (< -1) plan 18/36 settled 2/36`
  - `RESULT whatif null 00:00 target_plus_1   plan by start  +229.5   +84.8  +120.7 spread  144.7 | held  +51.5  +51.5  +51.5 spread 0.00`
  - `RESULT whatif varying 00:00 target_minus_1 … settled   +24.6   +24.7   +24.7`; `RESULT whatif varying 00:00 target_plus_1 … settled   -25.5   -21.7   -25.0`
  - `VERDICT whatif the plan figure moves with the start; the held figure does not`
  - Against #2834's figures the null spread reads 144.7 (was 132.0), the cap mean plan 45.7 (was 50.4) and settled savings 2/36 (was 1/36). Main moved between the two runs: both ends of this run read the same.
- `python3 tools/audit/archscore/score.py --diff origin/main` -> `Architecture score: dS +0.0169 IMPROVES`, `coord_footprint 2409 -> 2381`
- `PYTHONPATH=tests/hastub python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`. The re-record is in commit `86e9f8d53`'s message: `class_excess_loc` 17814 -> 17732, `max_class_loc` 8155 -> 8073 and `seam_cut_total` 423 -> 422.
- `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` -> `MODE: SCOPED -- 29 script(s) run, 4 scoped out.`
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=88c6ad5bbec69bfe157e04597a74d0c9c3e4775c ./tests/run.sh` at `eaac9d6b7` -> `31 TEST SCRIPT(S) PASSED; 3 SCOPED OUT AND NOT RUN`, rc 0. That includes:
  - `ALL 4574 FEATURE CHECKS PASSED`, `ALL 2470 ENTITY CHECKS PASSED`, `ALL CARD CHECKS PASSED`
  - `ALL 113 STRESS CHECKS PASSED`, `ALL 112 HARNESS HEADER CHECKS PASSED`, `ALL 84 OPTIMALITY CHECKS PASSED`
  - `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 88c6ad5bbec69bfe157e04597a74d0c9c3e4775c`, `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`, `STRUCTURE RATCHET PASSED`
- `PYTHONPATH=tests/hastub python3 tests/entities.py` at the base `88c6ad5bb` -> `ALL 2470 ENTITY CHECKS PASSED`. At `78dcf8eeb`, before the closure, doc-count and note repairs, it read `9 of 2470 ENTITY CHECKS FAILED`, and each of the nine named this diff's new module or moved owner. That is the control showing that the repairs above, not the environment, turned it green.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` -> `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 88c6ad5bbec6 (a data-file read is not seen)`. Before the repairs it predicted `13 predicted red(s) on ledger, tests / closures, tests / fast (3.14)`.
- **Class seams (fixer step 8).**
  - The P141 class is "a coordinator method that reads no coordinator state". The instrument that enumerates it is archscore's `coord_footprint` charge list, which counts the class's logic statements. This diff closes `_plan_slots` only. The other static members of the class are not this brief's, and no ruling routes them here.
  - The layer seam this move opened is enumerated by `layering.measure`'s violation list. It reads 13 at the base and 13 at the head (``Architecture score: dS +0.0169 IMPROVES`, `coord_footprint 2409 -> 2381``, no `layer_violations` row).

## Architecture score

`Architecture score: dS +0.0169`: IMPROVES, admissible.
- `coord_footprint 2409 -> 2381`: `_plan_slots`'s logic statements left the coordinator class. The whitespace null reads `dS +0.0000 NULL` (Null control).
- `layer_violations` stays 13. The first cut, with `channel_heating_steps` still in `optimizer.py`, read `layer_violations 13 -> 15` and `dS -0.1757 WORSENS (inadmissible)`. Moving the function beside `planned_draws_run` is the mechanism, and putting it back is its null.
- No `*_budgets.json` key rises. `tests/structure_budgets.json` re-records three improvements (commit `86e9f8d53`).

## Unpinned sites

`ci_predict.py` at the head lists no added unpinned site. Before the pins it listed 14. 19 sites are now pinned by `mutation_table.py --pin-killed` (Mutation proof).
- `plan_slots.py:69 CMP_BOUND` (`energy > 1e-9` -> `>=`) and `plan_slots.py:76 CMP_BOUND` (`shared > 1e-9` -> `>=`) survive `features.py` and `guard_pins.py`. `ci_predict.py` does not count either as added.
- Both are the moved lines of `_plan_slots.close`'s two `1e-9` guards. The base ledger holds one `_plan_slots.close CMP_BOUND` pin (`7b589d80`), so at most one of the two had a pin before the move.
- Neither is triaged here. An energy or shared total of exactly 1e-9 kWh is the only input that separates `>` from `>=`.

## Red checks

none. No PR exists yet. Locally, `ci_predict.py`'s predicted reds were each repaired before this handoff (Figures); CI has not run.

## Forward-carry

- **Item (1), the Plan page's what-if panel.** The panel prints the single-solve `monthly_cost_delta` with no caveat, and the figure moves with where the house starts (`whatif` arm, Figures). It needs one of two things: the owner's acceptance of the copy `docs/dashboard-card.md` already discloses (and whether the panel should carry that disclosure itself), or a designer seat for a steady-start estimator (both plans solved from a start held at each one's own schedule), which is size L. This PR is Part of #2257, so the issue stays open on this item. Carry: #2257

## Friction

- brief-citations: stale: P141's ruling (`dev/programme/triage/s6-batch27.md#P141`) and the group's brief name `payload.py` as the destination. A runtime import of `channel_heating_steps` there is a layer violation and a cycle with `optimizer.py`, and the ruling's own alternative (a small plan-view module) is what archscore admits. The same ruling cites the fixture captures' slot lists as the byte-identity control, but the five `coord_*` captures publish empty `space_plan` and `dhw_plan`, so that control is vacuous. `tests/plan_view.py`'s payload is the capture that carries slots. Carry: dismissed: recorded here; the ruling is satisfied by its alternative and a non-vacuous capture
- gate-scoping: cost: the brief names its toolchain as "on PATH from the environment", but the seat's `python3` (3.11) had neither numpy nor voluptuous, and `tests/requirements-ci.txt` does not install on 3.11 under `--require-hashes` (`typing_extensions>=4.4` unpinned). A preinstalled CI venv existed but was found only by a worker's search. Carry: dismissed: environment setup, not a rule of this tree
