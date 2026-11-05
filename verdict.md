Fix review: blocked 140df0268a1065bf186d357ec75e8524a3c4b242 mutation-vacuous: the list filter in _role_claims (the body's mutant 2) survives, and filtering every list diverges from sanitise and refuses a replay the base wrote

bus-nonce: c62335c69205c7be518c19a43ec9f618

Round: first fix review of #3219, at head 140df0268a1065bf186d357ec75e8524a3c4b242 (merge base d91e464aafe8b9f3c763ecc495013e957a303d03). Roles diff against main is empty, so this contract is current.

## Block

- The body's mutant 2 does not die. At this head, replacing `value = [v for v in value if isinstance(v, str) and ENTITY_ID.match(v)]` in `_role_claims` with `pass` (the same as the body's `if False else value`) leaves `replay.mask_checks()` at 19/19 passing. `mask:id_under_list_beside_a_non_id_seals_masked` is not killed, though the body says it is. The cause is that the check's key, `room_sensor_entities`, is not in `conf`, and `conf` contains no key ending `_entities` at all. So the key guard (mutant 1) skips the list before the filter is reached, and the list filter is unreachable under the real allowlist. The body's "Mutation proof" and "Unpinned sites" entries for lines 539 and 540 do not hold.
- The filter is also the wrong shape. `sanitise` (`_entry_shape`) filters list items only under keys ending `_entities`, but `_role_claims` filters every list once `conf` is passed. Plant a list holding a non-id beside an id under any kept conf key (for example `after_save: ["abc", "sensor.zzz_probe"]`). The base seals it, and this head refuses with "1 entity id(s) not masked to a role or a hashed id": the empty-replay symptom on a new class (ev/plant.txt). Today the config flow writes no list-valued key (scout read of config_flow.py, const.py and entry_config.py), so this is latent, but it is a regression in the very refusal this PR fixes.
- To clear it: drop the list filter, which is dead under `conf`, or make it the same predicate as `_entry_shape` (only keys ending `_entities`). Then give it a check that reaches it (an `_entities` key inside `conf`) and a check for the planted non-`_entities` list above.

## Findings

- Follow-up: the body names the escaping class by construction ("I could not read the live export"). The brief asks for the class seen on the 2026-11-04 v7.1.1 export. The off-allowlist entity key is the only seam reachable under the real conf, which makes it the likely class, but no one has matched it against that export. The re-cut should state this, or derive the shape from the bundle. Carry: R10-FLY-REPLAY-MASK
- Follow-up: the regression and the dead filter described under Block. Carry: R10-FLY-REPLAY-MASK

## Evidence

- RESULT head mask_checks: 19 checks, 0 failed; the four new `mask:` checks are true (ev/mask_head.txt).
- RESULT mutants (ev/mutants.txt, run with PYTHONDONTWRITEBYTECODE=1): M1 key guard off kills 2; M2 list filter off kills 0 (survives); M3 `mask_ids` passes None kills 2; M5 `document` drops conf kills 2.
- RESULT null control (ev/plant.txt): at the base, `legacy_probe_entity` off-list refuses and `room_sensor_entities` off-list refuses; at the head, both seal 3 states with no id leaked. The planted unmasked id still refuses at the head (`mask:planted_unmasked_id_still_refused`).
- RESULT regression (ev/plant.txt): a list `["abc", <id>]` under the kept keys after_save, away_dhw_min_temperature and away_enabled seals at the base and refuses at the head; an ids-only list seals at both.
- Not covered by any check: deleting `conf=conf` in debugger.py or tools/replay/export.py fails nothing, because the checks call `document` directly. That should be added in the re-cut.
- Instrument note: my first mutant pass gave a false reading. M3 (`conf`→`None`) is the same byte size as the source, so the restored file kept a stale .pyc. I cleared the caches and re-ran everything with PYTHONDONTWRITEBYTECODE=1, and only those numbers are cited above.
- merge-tree with origin/main: rc=0, tree 95b1b5453536b059c697dab7e807aa115873da66, no conflicts (ev/merge-tree.txt).
- VERSION, manifest.json, RELEASE_NOTES.md and tests/golden are not touched by the three-dot diff.
- The diff, tests and body contain no real entity id; every id is synthetic (sensor.off_list, sensor.late, sensor.in, sensor.planted_unmasked).
- The body's Head section names 140df0268a1065bf186d357ec75e8524a3c4b242, the head measured, but it also names a242409874d5b1571966c6e0c4e5797f19640fcd with base 783d8dc72811, neither of which is this PR's head or base (d91e464a). The re-cut body should name one head.
- CI: `merge_train.py classify` read WAIT, "pending: gate red: none", at 00:11:54Z (ev/classify.txt). The head's runs had not concluded when this verdict was written, so step 11 (red checks) is unjudged. The block does not depend on CI.
- No finder's harness is named (packet: "Finder's harness: none named"). The instrument here is my own: ev/mc.py and ev/plant.py, run against the PR's `tests/replay.py` and the module API.
