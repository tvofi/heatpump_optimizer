R10-FLY-REPLAY-MASK repairs the empty-replay refusal (`seal` refusing "entity id(s) not masked to a role or a hashed id"). The mask now takes roles from the same entry keys and items that `sanitise` keeps, through the one predicate `_entry_shape`. Round 3 of the repair: round 2's `prepr` step 6d refused the body for omitting two unpinned `replay_doc.py` sites.

Closes #3219's finding R10-FLY-REPLAY-MASK.

## Head

`2aafd3e36b61cde40c0a1a317957fffa4750e11f`, the fix merged with PR head `651468bb` (the bot pin commit) and with `origin/main` at `7c274274830ce553b8faec9574837de91a2be234` (merge base with main equals that tip, measured 2026-11-05 with `git merge-base origin/main HEAD`). `prepr.sh` was run once, on this head.

## What changed

- `_role_claims` (`replay_doc.py`): with `conf`, each kept entry value goes through `_entry_shape(key, value)`, the function `sanitise` applies, so the roles `entity_roles` hands out cannot disagree with what `_unmasked` re-derives from the sanitised entry. Alternatives: (a) delete the list filter only: leaves `_entities` lists with non-id items refused; (b) a second hand-copied `endswith("_entities")` predicate: duplicates the concept and can drift; both lost to the shared function.
- Round 3: the `if value is _DROP: continue` that followed the `_entry_shape` call is deleted. Its mutant (`if False:`) survived `replay.mask_checks()`, and no check can kill it: the only consumer of `_role_claims` is `entity_roles.claim`, which ignores any value that is not a `str` matching `ENTITY_ID`, and a `_DROP` is a bare `object()`. The branch was an equivalent mutant, so I took the deletion over a check that cannot fail (owner-directed alternative was a new check reaching the skip; it cannot exist for this reason, shown by the mutant below). Design choice: `_role_claims` yields the sentinel and the consumer's id test passes it over; the comment at the call says so.
- Checks in `tests/replay.py` (`mask_seam_checks`, `_conf_reaches_writers_checks`) from round 2, unchanged: `mask:id_in_list_under_a_kept_key_beside_a_non_id_seals_masked`, `mask:id_in_list_under_an_entities_key_beside_a_non_id_seals_masked`, `mask:build_export_passes_conf_to_document`, `mask:debugger_replay_document_passes_conf_to_document`.

## Mutation proof

Harness: `replay.mask_checks()` (PYTHONPATH `tests/hastub:.`, `tests` and `tools/replay` on `sys.path`), each mutant one line, restored after. Null control first.

- null at this head: 23 checks, none failed.
- `if conf is not None:` (the `_entry_shape` guard) turned `if False:`: killed by `mask:id_in_list_under_an_entities_key_beside_a_non_id_seals_masked`.
- `value = _entry_shape(str(key), value)` replaced by `pass`: killed by the same check.
- the deleted `if value is _DROP:` guard, measured at `1e25dcd8` as `if False:`: 0 failed (survived). Equivalent by the consumer argument above, so deleted rather than pinned.
- earlier mutants of the `conf=conf` call sites (`mask_ids`, `document`, `debugger.py`, `tools/replay/export.py`) are untouched by this round's one-hunk change.

## Null control

The base refuses `legacy_probe_entity` configured off the allowlist; the blocked round-1 head refused the kept-key list `after_save: ["abc", <id>]` the base sealed; this head seals both, and `mask:planted_unmasked_id_still_refused` still refuses a planted unmasked id.

## Escaped class on the live export of 2026-11-04

I cannot read the owner's live export and did not. The reachable class, by reasoning and not measured: an entity id configured under an entry key off the installed allowlist (a key `sanitise` drops); `entity_roles` gave it a role from the dropped key, `seal` re-derived a different role from the sanitised entry and refused the whole replay. No id is quoted anywhere in this diff, tests or body.

## Figures

- `python3 -c "import sys; sys.path[:0]=['tests','tests/hastub','tools/replay']; import replay; r=replay.mask_checks(); print(len(r), [n for n,ok,w in r if not ok])"` with `PYTHONPATH=tests/hastub:.`: prints the count and failing names (every `mask:` check).
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED`; the scripts it names and `PYTHONPATH=tests/hastub` runs: `debug_collect`, `deployment_shape`, `doc_claims`, `entities`, `features`, `harness_headers`, `typing_ruler`, `config_flow_steps` all exit 0 on the tree without the step-ref `PR-BODY.md`; `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. `golden`, `env_drift`, `arch_score_head`, `finite_boundary`, `manual_plan` are CI's.
- Toolchain: `bash tools/audit/seat/cloud-setup.sh`; numpy 2.5.4 and scipy 1.18.1 match `tests/requirements-ci.txt`.

## Unpinned sites

- custom_components/heatpump_optimizer/replay_doc.py:535 GUARD_OFF (`if conf is not None:`, the `_entry_shape` guard in `_role_claims`): killed by `mask:id_in_list_under_an_entities_key_beside_a_non_id_seals_masked`; pinned by `mutation-autofix` after the push.
- the former `if value is _DROP:` guard at the `:537` site of the round-2 head: no longer exists at this head; the equivalent skip is deleted, so the site is gone, not unpinned.
- The `tools/replay/export.py` `conf=conf` site is outside the `custom_components/` lane; its in-tree mutant harness is `replay.mask_checks()`, killed by `mask:build_export_passes_conf_to_document`.

## Red checks

- `tests / mutation` and `tests / mutation-autofix`: this branch's own, from the two sites above, answered by the table above; cheaper detector: `prepr.sh` step 6d, which caught it at the round-2 handoff (the cheapest detector, already standing).
- `governance / delivery-status` and `tests / nightly-status`: red on main's ancestry at base `7c274274830ce553b8faec9574837de91a2be234`, not this branch's; the diff touches none of their scripts, `ci.yml`, `tests.yml`, `nightly.yml`, `governance.yml`, the plan or `HANDOVER.md`, so the orchestrator owns them on `main`.

## Forward-carry

none

## Friction

none
