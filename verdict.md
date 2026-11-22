Design review: approve ee6bb4da3329dcf1ba16e6a40fd63ef80cdba289

Reviewed design/R11-OWNER-EXTHEAT-OVERRIDE design.md at ee6bb4da3329 (revision 3). I read the delta from 0a6dfc18, checked it against verdict 9be15750a3 (revise 0a6dfc18 harness), and checked every cited site at the note's base, origin/main 8ef450936a. The card side was read at design/R11-OWNER-CARD-EXTERNAL-HEAT 6ed233f99c, which is still that ref's tip. I swept the open design/* refs for statusPill, ExternalHeatBinarySensor and binary_sensor.py:244: only R11-OWNER-CARD-EXTERNAL-HEAT and this note match, and the orchestrator's merge-gated `after` edge orders the two.

## Prior findings

- R1 resolved. design.md:121-128 keeps the cached value at coordinator.py:6225 (`self._external_heat_active and not self._external_heat.ignore_effective(...)`). At base, :6225 reads `external_heat_active=self._external_heat_active`.
  - tests/features.py:73051 and dev/audit/harnesses/solve_inputs_parity.py:157 still set the cache, so they still reach the solve with the switch off. No harness port is needed.
  - The 73160 null control is evidence test 3n (design.md:234).
  - The 6225 mutation targets are listed at design.md:246-249: the `ignore_effective` term dropped, and `and not` flipped to `and`. The 3n switch-off arm kills the flip.
  - Alternative 7 (design.md:210-214) records why the revision-2 shape was rejected.
- Carry r9egb1-burn-null resolved. design.md:322 carries it, with evidence 3n and the parity run at base and at head.
- Carry woodfuel-view resolved. The residue now names the raw gate at wood_fuel.py:629 (design.md:58-62; at base, :629 is `if result is not None and det.suppressing:`), and evidence 4b measures it.
- Carry view-import resolved. design.md:132-135 extends external_heat.py:37 and keeps coordinator.py:65's import. At base, the name's only other use in coordinator.py is the :8085 annotation, so keeping it is correct.

## Orchestrator binding (card reconciliation): carried

- Hot files (design.md:255-262): www/heatpump-optimizer-card.js (`statusPill`'s external-heat branch only), tests/card.mjs and docs/dashboard-card.md. All three exist at base, and `statusPill` is at card.js:9758.
- Serial position (design.md:267-271): `after` R11-OWNER-CARD-EXTERNAL-HEAT, merge-gated. The clause moves with whatever shape the card group lands.
- Rule (design.md:151-166): the pill takes `external_heat` only when the twin is on and `attributes.block_ignored !== true`. Otherwise it falls through to the heating/idle state that the plan earns. No new string.
  - Source chain: `view` passes `ignore_effective(...)` only when the switch is on, else None (design.md:111-116). The binary sensor adds the attribute only when the key is present (design.md:145-149). With the switch off, the attribute is absent and the card group's markup is unchanged.
- Evidence and check: test 6c (design.md:240) pins `heating`/`idle` under `block_ignored: true`. Its null is the card group's own case, unchanged. The mutation targets add the `!== true` clause and the binary sensor's key-presence guard. Carry card-reconcile is at design.md:325.

## Owner decisions

The note records Q1-Q9 as the designer's defaults (design.md:299-311). Verdict 9be15750a3 named Q6 "yes" and Q3 "a timeout" as the only answers that would move the shape. The owner answered "learners stay frozen" and "no timeout", so the shape stands.

## Revise points

None.

## Notes for the fixer

- Carry: R11-OWNER-EXTHEAT-OVERRIDE (item 3n-inert-fixture) -- evidence 3n's switch-on arm ("switch on ⇒ False", design.md:234) runs on `_r9egb1_coord`, which is built on `_solve_coord` (tests/features.py:31190). That fixture's entry data has no wood-furnace keys, so `wood_furnace_on` is False and `_external_heat_config()` (coordinator.py:5047) gives `enabled=False`. By the note's own Q4 rule, `ignore_effective(True)` is then False, and the solve state stays `external_heat_active is True` with the switch on. As written, that arm goes red. Keep the switch-on/disabled result (True) as a Q4 null, and kill the 6225 `ignore_effective` drop on an arm that enables detection: CONF_WOOD_FURNACE_ENABLED and detection enabled via `with_config`, then `coord._external_heat.config = coord._external_heat_config()`. Alternatively, rely on evidence 3's DHW fixture, provided its detector config is enabled; state which.
- Carry: R11-OWNER-EXTHEAT-OVERRIDE (item card-twin-shape) -- the card group's design folds `inputProblemState`'s lookup into `planBinaryTwin(plan, suffix)` (its design.md:36, :105). Read `block_ignored` from the state object that the merged helper already resolves, not from a second id derivation, as design.md:159-162 allows. Re-check after the rebase that the card group's own external_heat case in tests/card.mjs passes byte-for-byte with no `block_ignored` attribute.
