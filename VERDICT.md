Fix review: merge 9bdd6af9bde7489cd2b0f05751b7f664ecd6a5a2

bus-nonce: d78802a581bcb881f61307497de5ca2e
pending-ci: tests / coverage, governance / instrument-self-tests

## Summary

Round 1, docs only (R10-USER-DOCS-VERIFY savings-valuation delta). Measured head 9bdd6af9bde7489cd2b0f05751b7f664ecd6a5a2 (the PR head and the body's `## Head`; the head commit adds only `dev/programme/delivery/3596.md` over authored code head 359e580ac4). Both changed sentences are true of the code at the head, neither overclaims, and the docs-claim checks pass.

## Evidence

- Diff (three-dot from merge base d7004eaa77): docs/architecture.md 1 line, docs/configuration.md 1 line, dev/programme/delivery/3596.md new. No custom_components/, tests/ or tools/ change; VERSION, manifest version and RELEASE_NOTES.md untouched (empty diff).
- docs/configuration.md, combi row, new tail "Each says so in its `dhw_split` attribute, and so does the climate entity." Verified: climate.py:281 `attrs.update(dhw_split_attributes(getattr(self.coordinator, "thermal_params", None)))` inside `extra_state_attributes` under `if self.coordinator.data:`, beside `dhw_heating_cost`. The three sensors: DHWHeatingCostSensor (sensor.py:1279), and `_AccumulatingSensor.extra_state_attributes` (sensor.py:1830) for `_ledger_line == "dhw"`, which only DHWEnergySensor (sensor.py:1855) and DHWCostSensor (sensor.py:1900) set. Gate `entity.dhw_split_attributes` returns the attribute only when `ThermalParameters.combi_tank_active` (thermal_model.py:317: option on, dhw on, buffer is store, no dhw coil), matching the row's "While it is on". No overclaim: the climate entity carries it only on a combi install, as the row's scope states.
- docs/architecture.md, "One payload read on the entity base": now names the combi store's `dhw_split` attribute as entity.py-owned, published by the hot-water cost and energy sensors and the climate entity from one function. Verified: `COMBI_DHW_SPLIT` entity.py:377 and `dhw_split_attributes` entity.py:383, imported by sensor.py:53 and climate.py:36; those four call sites (three sensors via two methods, plus climate) are the only users (`git grep dhw_split custom_components`).
- Body line cites re-derived at d7004eaa77: entity.py:377-380 (COMBI_DHW_SPLIT) exact; entity.py:386-392 for the builder is approximate (def at 383, return at 391); thermal_model.py:317 exact. No figure in the body moves a metric (`## Figures` none; figure_lint 0/0/0).
- #3587 claim (no user-facing wording changes): not independently re-derived beyond confirming no docs or strings change is owed by the body's account; the PR changes no sentence on it, so nothing here can overclaim it.
- RESULT doc_claims head: `ALL 410 checks PASSED` (ev/doc_claims_head.log).
- RESULT md_tables head: `doc_misrendered_lines=0` (ev/md_tables_head.log).
- Targeted mutant: renaming `dhw_split` to `dhw_splitz` in both changed sentences makes doc_claims fail 1 of 410 on "configuration.md's combi option names the three figures and their dhw_split (Carry 10)" (ev/doc_claims_mutant_dhw_splitz.log); the architecture.md sentence's identifier is not pinned.
- tests/entities.py and tests/features.py need Home Assistant, not installed here; cited from CI instead.
- Mutation proof: n/a per body (no production line); `tests / mutation` draws no mutant on a diff writing no code line.
- Merge with origin/main: `git merge-tree --write-tree` rc=0, tree 5f7f8c5196 (ev/merge-tree.txt).
- Roles drift since merge base: none.
- Finder's harness: none named; docs-verification seat, the harness is the enumeration grep the body lists, re-run for `dhw_split` over custom_components above.
- CI: classify polled 21:38-22:08 UTC, every run `WAIT 9bdd6af9bde7489cd2b0f05751b7f664ecd6a5a2 pending: gate red: none` (rc=3); in progress at 22:08: tests / coverage, governance / instrument-self-tests (ev/classify.txt). The two `gate` runs (jobs 132597220552, 132601680738) are red only with `FAIL run(s) [43642611250] at this head are still being judged; their gate decides`, a wait, not a finding. `tests / nightly-status` red is outside owed-reds. All other owed contexts completed green, including tests / mutation, tests / closures, tests / fast (3.14), tests / briefs, governance / policy-docs.

## Findings

- Follow-up: the new clause "and so does the climate entity" and the architecture.md `dhw_split` sentence are pinned by no check (the `dhw_splitz` mutant survives on architecture.md; doc_claims' Carry 10 check reads only the configuration.md identifier, not the climate clause). Hand-verified true at this head against climate.py:281. Carry: dismissed: docs-only correction verified against code; doc_claims pins prose only where a carry asked, and no check is owed for a one-clause doc fix
