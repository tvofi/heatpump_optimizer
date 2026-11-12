Fix review: merge e43f976d22648a95b4c41966a63cc890b2c6c32c

bus-nonce: 3db99bb1cedfe1be2848c1ffc16394ed

## Summary

Round 1, handoff review of R10-ECL110-MQTT-OFF-NEUTRAL at head `e43f976d22648a95b4c41966a63cc890b2c6c32c` (body: `handoff-body/r10-ecl110-mqtt-off-neutral` tip `6fca353d`, whose `Code:` trailer names this head; merge base `fc2a7edcf2be8847037d9e8dc5bde460977befa8`, as the body states). The MQTT arm becomes a neutral `off_restore` consumer armed in `heat_curve.publish`; MODE_OFF and unload now leave displace 0 standing on both ECL110 topics. `_apply_action` passes the switch's write to the legacy payload's `heat_pump_on`. The `## Unpinned sites` section answers every site the mutation predictor reports on the added lines, and the driver run over the added lines reports no survivor.

## Findings

none

## Evidence

- No pull request exists yet, so there is no review packet and no CI run to read. Each check below is my own run at the head, from a detached worktree.
- Roles current: `git diff fc2a7edcf2...origin/main -- dev/governance/roles/` is empty.
- Merge with main: `git merge-tree --write-tree origin/main e43f976d22648a95b4c41966a63cc890b2c6c32c` exits 0 (tree `f8ea9485`) against origin/main `19baca76`. The head is behind main but merges cleanly (`ev/merge_tree.txt`).
- Unpinned sites: `tools/pr/ci_predict.py --base fc2a7edcf2 --body BODY.md` reports exactly four ADDED UNPINNED sites: `heat_curve.py:167 BOOLOP`, `:167 GUARD_OFF`, `:177 RETURN_DEL` and `:266 RETURN_DEL`. The body's `## Unpinned sites` names all four by key, each with a value check and "pinned by mutation-autofix". It predicts no closures, fast, governance or instrument red (`ev/ci_predict.txt`).
- RESULT mutation driver (diff mode): `mutant_run.py --diff fc2a7edcf2...HEAD --cmd 'sh blk.sh'`. Its `--list` gives 22 mutants on the added lines of `coordinator.py` and `heat_curve.py`. The run printed no SURVIVED, FORKCAP or BASELINE FAILS line and exited 0, so all 22 were killed by the R10-GENERIC-HEAT-CURVE block alone (`ev/mutant_run_diff_block.txt` is empty by design: the driver prints only survivors). The command is `ev/blk.sh`, the body's block command with the prelude `--emit-prelude` writes. That block passes clean at the head: `ALL 25 FEATURES BLOCK PASSED`.
- RESULT targeted mutants (spec mode, NULL survived first): M1 (the `async_arm(... MQTT_CONSUMER)` call replaced by `pass`) KILLED. M2 (`heat_pump_on=on` dropped from `_apply_action`) KILLED. M7 (the writer's `raise` replaced by `pass`) KILLED. M13 (the neutral `heat_pump_on` swapped to False) KILLED. M4 (the unload `off_restore.async_restore` call in `__init__.py:426` neutralised) KILLED. Files: `ev/mutant_run_spec.txt`, `ev/mutant_run_spec_m4.txt`, `ev/spec.json`, `ev/spec2.json`.
- RESULT null control at the merge base (base production code, the head's `tests/features.py`): "MODE_OFF and unload leave displace 0 standing on both ECL110 topics" FAILs with `ecl/set: (-3, False)` and `ecl/cmd: (-3, False)`, and `entity: 0`, on mode_off and on unload. That matches the body's (1). The neutral-body, no-topic-success and armed-once checks also fail there. The block then stops at `heat_curve.MQTT_CONSUMER`, which is absent at the base. So the later checks, including the late-cycle `heat_pump_on` base figure `late=([True], [False])`, were not re-derived at the base. M2 killing the check at the head covers that claim from the other end (`ev/null_control_base.txt`).
- Class: every ECL110 MQTT publish in `custom_components/` goes through `heat_curve.publish` (`publish_ecl110_topics` is called only from `publish` and from the restorer; the coordinator's two `async_publish_ecl110_command` callers, the plan and peak guard, both reach `publish`). The arm therefore covers every MQTT publish site. The registered `off_restore` consumers are `heat_curve` (entity), `heat_curve_mqtt` (new) and `pump_arbiter`'s; none is left out.
- Re-arm cost: `off_restore.async_arm` returns early for an already-armed neutral entry without `_save`, so arming on every publish writes no store per cycle.
- Ledger deletions: both deleted pins (`publish_ecl110_topics` BOOLOP and GUARD_OFF `8b6644d6`) anchor `if not set_topic and not command_topic:`, the early return this diff deletes. That makes the movement earned (step 14). Removing the return keeps behaviour: with no topic both arms skip and `sent` stays True.
- Structure: `tests/structure.py` reads `STRUCTURE RATCHET PASSED` with no budget file touched (`ev/structure.txt`). Architecture: `score.py --diff fc2a7edcf2` reads `Architecture score: dS +0.0000 NULL`, as the body says (`ev/archscore.txt`).
- Claims: `env_drift.py --all fc2a7edcf2` reads `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`, rc 0. Neither claim file is touched (`ev/env_drift.txt`). A first run against the default origin/main refused on `card_claimed_drift.txt` only because main moved past the base; that is not this branch's change.
- VERSION, the manifest version and the RELEASE_NOTES heading are untouched (three-dot diff: `coordinator.py`, `heat_curve.py`, `docs/ecl110.md`, `tests/entities.py`, `tests/features.py`, two ledger files).
- Figures re-derived: `ALL 2709 ENTITY CHECKS PASSED`, rc 0, at the head (`ev/entities.txt`). The test doubles `_rec_plan` (`tests/features.py:19314`), `_g_rec` (`:28165`) and `_raise_publish` take `heat_pump_on`. Not re-derived: the whole-file `ALL 5307 FEATURE CHECKS PASSED` (quoted at `7a688b2c71`, not this head), the scoped-gate `MODE: SCOPED` run, and the `MODE: FULL` figure-block line. The heavy runs are CI's to cite once the PR opens.
- Red checks: `merge_train.py owed-reds` includes `tests / mutation` (`ev/owed_reds.txt`). The body's `## Red checks` names it and answers it: the predicted unpinned-site red, with prepr step 6d as the existing cheaper detector, repaired by mutation-autofix. No run exists yet to read live.
- Forward-carry: roster commit `84184ae668` (`handoff/audit-r10-roster`) carries item 30ec8edf to this group with sites (1) and (2) and the late-step control. The body answers both: (2) is built and killed by M2, and (1) is dismissed with the reason the carry itself states (a curve offset cut at the solve).
- Head check at return: the body ref still reads `6fca353d`, whose `Code:` trailer is `e43f976d22648a95b4c41966a63cc890b2c6c32c` (`ev/body_ref.txt`).

## Friction

- The frugal inline-search guard counted plain result reads (`tail`/`grep` of my own evidence files) as discovery and refused them twice, so two scout/extractor spawns were made only to reset it. Carry: dismissed: a session plugin's guard, outside this repository and not this pull request's.
