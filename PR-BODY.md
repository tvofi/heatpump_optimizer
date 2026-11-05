R10-FLY-REPLAY-MASK repairs the empty-replay refusal (`seal` refusing "entity id(s) not masked to a role or a hashed id"). The mask now takes roles from the same entry keys and items that `sanitise` keeps, through the one predicate `_entry_shape`. Round 2 of the repair: the first review (blocked, mutation-vacuous) found that the list filter in `_role_claims` was dead under the real allowlist and, for lists under keys not ending `_entities`, diverged from `sanitise` and refused a replay the base sealed.

Closes #3219's finding R10-FLY-REPLAY-MASK.

## Head

`1e25dcd8059086c1c9e6973ffad5c4f6bbae7daa`, the fix commit merged with `origin/main` at `499162c89d0f4f8369e16e6e41fb3a620bc1ecb0` (merge base with main equals that tip, measured 2026-11-05). `prepr.sh` was run once, after that merge.

## What changed since the blocked head

- Dropped the ad-hoc list filter in `_role_claims` (`replay_doc.py`). With `conf`, each kept entry value now goes through `_entry_shape(key, value)`, the very function `sanitise` applies, and a `_DROP` result is skipped. One predicate, so the roles `entity_roles` hands out cannot disagree with what `_unmasked` re-derives from the sanitised entry. Alternatives: (a) delete the filter only: leaves `_entities` lists with non-id items refused (the allowlist holds no such key today, but `_entry_shape` drops them on the sanitise side); (b) a second hand-copied `endswith("_entities")` predicate: duplicates the concept and can drift again. Both lost to calling the shared function.
- New checks in `tests/replay.py` (`mask_seam_checks`, `_conf_reaches_writers_checks`):
  - `mask:id_in_list_under_a_kept_key_beside_a_non_id_seals_masked` (the planted class: `after_save: ["abc", <id>]`), red at the blocked head, green now.
  - `mask:id_in_list_under_an_entities_key_beside_a_non_id_seals_masked` reaches the `_entities` branch with a synthetic allowlist key, because the installed allowlist holds no key ending `_entities`.
  - `mask:build_export_passes_conf_to_document` drives `tools/replay/export.py` `build_export` over the synthetic install with a second, off-allowlist key naming the outdoor sensor.
  - `mask:debugger_replay_document_passes_conf_to_document` drives `debugger.replay_document` with the same entry shape.
  Design choice stated: the last two pin that `conf` reaches `document` at each production call site by behaviour, not by reading the source.

## Mutation proof

Harness: `replay.mask_checks()` (23 checks), each mutant a one-line predicate change, restored after. Null control is the unmodified tree, first.

- null (head): 23 checks, none failed.
- M1 key guard off (`if False and (key not in conf ...`): killed by `mask:id_under_key_off_the_allowlist_seals_masked`, `mask:id_under_list_beside_a_non_id_seals_masked`, `mask:build_export_passes_conf_to_document`, `mask:debugger_replay_document_passes_conf_to_document`.
- M2 shape predicate off (`value = _entry_shape(...)` replaced by `pass`): killed by `mask:id_in_list_under_an_entities_key_beside_a_non_id_seals_masked` (this is the reviewer's surviving mutant 2, now killed).
- M3 `mask_ids` passes `None` for `conf`: killed by five checks, among them both new `_passes_conf_to_document` ones.
- M5 `document` drops `conf` before `mask_ids`: killed by the same five.
- M6 `conf=conf` deleted in `debugger.py`: killed by `mask:debugger_replay_document_passes_conf_to_document` alone.
- M7 `conf=conf` deleted in `tools/replay/export.py`: killed by `mask:build_export_passes_conf_to_document` alone.

Also red-first: `mask:id_in_list_under_a_kept_key_beside_a_non_id_seals_masked` failed ("1 entity id(s) not masked to a role or a hashed id") before the `_role_claims` change, which is the reviewer's regression reproduced.

## Null control

The base (merge base) refuses `legacy_probe_entity` and `room_sensor_entities` configured off the allowlist (reviewer's plant, `ev/plant.txt`); the unmodified blocked head refuses the kept-key list `after_save: ["abc", <id>]` the base sealed; this head seals both, and `mask:planted_unmasked_id_still_refused` still refuses a planted unmasked id, so the fix did not loosen the refusal.

## Escaped class on the live export of 2026-11-04

I cannot read the owner's live export of 2026-11-04 (v7.1.1) and did not. The class below is the reachable one by reasoning, not measured: an entity id configured under an entry key that is off the installed allowlist (a key `sanitise` drops, whose value is an id also or only sitting in the states). `entity_roles` gave that id a role from the dropped key, `seal` re-derived roles from the sanitised entry, found a different role (or the hash), and refused the whole replay. Under the real allowlist this is the only seam that reaches the mask; the list shape is latent (the config flow writes no list-valued key). No id is quoted anywhere in this diff, tests or body.

## Figures

- `PYTHONDONTWRITEBYTECODE=1 python3 -c "import sys; sys.path[:0]=['tests','tests/hastub','tools/replay']; import replay; r=replay.mask_checks(); print(len(r), [n for n,ok,w in r if not ok])"` prints the count and the failing names (rule: every `mask:` check, merged tree).
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED` (no budget touched).
- Scoped scripts run locally with `PYTHONPATH=tests/hastub`: `tests/debug_collect.py`, `tests/entities.py`, `tests/features.py`, `tests/doc_claims.py`, `tests/deployment_shape.py`, `tests/harness_headers.py`, `tests/typing_ruler.py` all pass. `tests/replay.py` reports 3 of 189 failed, all `cycle_cost` runner-class band checks (ref_ms 28.4 to 28.72 lie between bands) on this container, unrelated to the mask; `mask_checks()` itself is clean. CI is the authority.
- Toolchain refreshed with `bash tools/audit/seat/cloud-setup.sh`; numpy 2.5.4 and scipy 1.18.1 match `tests/requirements-ci.txt`.

## Unpinned sites

The `_entry_shape` call and `conf=conf` in `replay_doc.py` and `debugger.py` are `custom_components/` sites for `mutation-autofix`, and each is already killed by the checks above (M2, M3, M5, M6). The `tools/replay/export.py` `conf=conf` site is outside that lane: its in-tree mutant harness is `replay.mask_checks()` (M7).

## Red checks

none known at handoff; the CI gate had not run on this head.

## Forward-carry

none

## Friction

none
