Fix review: merge 29370fdbb59aeb18da82ebe9612e7c036e9dc29c

bus-nonce: ef5a786830dadd020d5ec807adbba15b

## Evidence

Round 1, handoff review at the handoff tip 29370fdbb59aeb18da82ebe9612e7c036e9dc29c (the body's `## Head`, matched). No pull request exists, so there is no review packet and no CI to read: no check run exists at this head, so no red is owed an answer (step 11). The body's `tests / mutation` prediction is in `merge_train.py owed-reds`' set (ev/step7.txt) and the body answers it under `## Red checks`.

- Merge: `git merge-tree --write-tree origin/main 29370fdbb59aeb18da82ebe9612e7c036e9dc29c` exit 0, tree 7ee9e17080 (origin/main f44e761c19); ev/merge-tree.txt. Part 1 (6b9e873394) is not on main, so the range from merge base 4145f28526 carries it; production review below is the part-2 delta `git diff e1d9352478 29370fdbb59aeb18da82ebe9612e7c036e9dc29c -- custom_components/` (ev/p2-prod.diff).
- Role contracts: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` empty.
- RESULT section-harness head: `ALL 70 DUTY-SWITCH SECTION CHECKS PASSED` (ev/section-head.txt), matching the body's 70.
- RESULT mutants, each alone on the section harness, restored after (ev/mut-*.txt): order `in usable` 6 fail; next-step condition dropped 1; off time dropped 5; whole-step bound `<=` 1; booking cap `scale = 1.0` 1; decay cap dropped 1; unloaded record latching 1; latch decided every read 2; `whole` ignored 5; share end `<=` 1; mine beyond the body: `_share` passing no next duty 5, next duty read from the same step 1, `N_CAP = 3.0 * N_ON` 1. Every figure the body lists for these reproduces. None survives.
- RESULT factory-reset block (features_block.py, `from heatpump_optimizer import const as _fr_const` to `R.section("Runtime parameter updates")`, prelude from `--emit-prelude`): head `ALL 32 FEATURES BLOCK PASSED`; `("duty_switch", None)` dropped from `_FACTORY_VOID`: `2 of 32 FEATURES BLOCK FAILED`, the two the body names (ev/step1.txt, ev/step3.txt). The failing-first claim at the pre-coordinator commit is not re-run: the same mutant reproduces its `after (True, 6.0)` line.
- The body's "the undo restores it": a mutant keying on the name (`_async_store_documents` returns None for `duty_switch`, so the undo point holds no record) leaves the block at 32 of 32 (ev/step2.txt); dropping the store from `_restored_stores` itself is killed by the void checks (the zip truncates). Judged under Findings.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED (ev/step5.txt). `score.py --diff 4145f28526`: `Architecture score: dS +0.0000 NULL` (ev/step6.txt). The body's `coord_footprint 2506 -> 2517` control at an earlier commit is not re-derived.
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` under the session's env lines: `ALL 2709 ENTITY CHECKS PASSED`, rc 0 (ev/entities.txt). Without `PYTHONPATH=tests/hastub` it fails importing homeassistant: the environment, not the tree.
- `node tools/policy/brief_lint.mjs` rc 0 (ev/step9.txt).
- Untouched: `VERSION`, the manifest, `RELEASE_NOTES.md`, `tests/golden/` and both claim files show no diff from the merge base; `env_drift.py --all` not run, since no fixture or claim file is in the diff and the solver path is not touched.
- The figure-block line `MODE: SCOPED -- 22 script(s) run, 11 scoped out.` is not re-derived: the gate is CI's heavy run and none exists before the PR.
- Forward-carry: `handoff/audit-r10-roster` at d1f929f3dae5809baa106364d4feb9dedf46b803, `dev/programme/rosters/wave-r10-groups.json`, group R10-DUTY-SWITCH-PLANNER-PRICE carry[2] holds the body's carry verbatim, with its control (the two section checks) and a re-measurement instruction (ev/roster.json).
- Class (step 6): the body names no enumeration rule; the group's seams are its roster carries 0-8, each dispositioned in the body, and the two production seams (the arbiter's split reader, the store's factory-reset void) are both in the diff.
- Architecture (step 15): the arbiter only delegates; the learned decision and its per-step latch live on the duty-switch record, as the body's design note states; no breach found.
- Head re-read before return: 29370fdbb59aeb18da82ebe9612e7c036e9dc29c.

## Findings

- The body's claim that the factory-reset undo restores the duty-switch store has no check of its own: a name-keyed mutant emptying only that store's undo document survives the 32-check block, since `_fr_learned` reads `_learner_snapshot_payloads()`, which omits duty_switch. The undo rides the same `_FACTORY_VOID`/`_restored_stores` zip every store does, and every edit to that zip short of naming the store is killed by the void checks. Carry: dismissed: only a mutant that special-cases the store by name survives; the shared undo path is pinned by the void checks and by `_async_store_documents`' killed RETURN_DEL

## Friction

none
