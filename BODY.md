Fixes the empty replay section on the v7.1.1 diagnostics export: `replay_doc.seal` refused the whole replay with "entity id(s) not masked to a role or a hashed id".

Class that escapes the mask (derived shape only): an entity id configured under an entry key that `sanitise` later drops, namely a key absent from `conf_keys` or one matching `SECRET_KEY`. A second seam of the same mismatch is an id inside an `*_entities` list that also holds a non-id item, where the index shifts once the sanitiser filters the list. `mask_ids` gave such an id a role from the unsanitised entry, and the id still appears as a `states` key. `_unmasked` then re-derived roles from the sanitised entry, found no key claiming that role, and read the masked id as unmasked. I could not read the live export, so I identified the class by construction, not by matching its content.

Fix at the owner (`replay_doc.py`): `entity_roles`, through the new `_role_claims`, takes an optional `conf` and then claims roles only from the keys `sanitise` keeps, with a list counting only its ids. `document` and `mask_ids` pass it through, and both writers (`debugger.py`, `tools/replay/export.py`) pass their `conf`. An id with no surviving key falls to the hash. The refusal itself is unchanged, and `conf=None` keeps the old behaviour.

Entity-id sources the replay writes: `entry.data` and `entry.options` values (single and list), `price_series_entity`, `inputs`, `published`, `states` keys, any dict key or list item at any depth (attributes keyed by id). `mask_ids` renames every one through one mapping, and `_unmasked` checks every one.

## Head

a242409874d5b1571966c6e0c4e5797f19640fcd (base origin/main 783d8dc72811, unmoved since prepr).

## Mutation proof

Mutant 1, the `conf` key guard in `_role_claims` replaced with `if False:`: `mask:id_under_key_off_the_allowlist_seals_masked` goes red. Mutant 2, the list filter condition replaced with `if False else value`: `mask:id_under_list_beside_a_non_id_seals_masked` goes red. Both were restored and the checks go green again. Run: `PYTHONPATH=tests/hastub python3` calling `replay.mask_checks()`.

## Null control

At the merge base, `document(...)` then `seal(...)` on an entry with `legacy_probe_entity` set to a states-key id raised `Refused: 1 entity id(s) not masked to a role or a hashed id`. At the head it seals with a non-empty `states`. A planted unmasked id (`mask:planted_unmasked_id_still_refused`) still refuses, and a clean export seals non-empty (`mask:clean_export_writes_a_non_empty_replay`).

## Figures

Instrument: `tests/replay.py` (`mask_checks`), the four new `mask:` checks listed above all true at the head. `python3 tests/replay.py` reports one failing check, `synthetic-dhw-only.json: cycle_cost`, a runner-class timing band (`runner class unknown: ref_ms lies in no band`), environmental. The merge base fails the same check and two siblings on this container. CI is the authority. Toolchain: numpy 2.5.4 and scipy 1.18.1 match tests/requirements-ci.txt.

## Unpinned sites

- custom_components/heatpump_optimizer/replay_doc.py:533 BOOLOP: value check, killed by `mask:id_under_key_off_the_allowlist_seals_masked` (mutant 1 above); the pin is left to `mutation-autofix`.
- custom_components/heatpump_optimizer/replay_doc.py:533 GUARD_OFF: killed by the same check; pinned by `mutation-autofix`.
- custom_components/heatpump_optimizer/replay_doc.py:536 GUARD_OFF: the `isinstance(value, list)` guard moved from `entity_roles`, whose stale ledger pin I deleted; pinned by `mutation-autofix`.
- custom_components/heatpump_optimizer/replay_doc.py:539 GUARD_OFF: killed by `mask:id_under_list_beside_a_non_id_seals_masked` (mutant 2 above); pinned by `mutation-autofix`.
- custom_components/heatpump_optimizer/replay_doc.py:540 BOOLOP: value check on the same list filter; pinned by `mutation-autofix`.

## Red checks

`mutation` is predicted red by `prepr.sh` step 6d solely because of the five unpinned sites above. The cheaper detector is `mutation-autofix` (`mutation_table.apply_pins`), which pins killed mutants after the PR exists. Its standing cost is one bot commit. A local run would mean per-mutant `stress.py`, which the fixer contract bars.

## Forward-carry

none

## Friction

none
