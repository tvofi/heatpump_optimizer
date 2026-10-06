Closes #1939

The debug collector, its learning-page option, the `debug_collect` action, the finalize button and the `hpo-debug/1` bundle. The ring is the `debug` store. The collector listens to the coordinator, so `coordinator.py` names no debugger.

This head clears the reds measured on `8f75654777b9f10c07977386a00376d8a6f57280`. The catalogue headers still named the counts from before `debugger.py` and the debug-collection option, so `tests/harness_headers.py` exited 1 and the closure merge refused the batch. `config_flow` is float-free and now emits `debug_collect_enabled`; the fixture is re-recorded and claimed. `tests/features.py`'s Linux recording, rc 0, reads `services.yaml`; that path is in the committed closure. `tests/finite_boundary.py`'s top-level `_kept` collided with `debugger._kept`; the local is renamed `_finite_payload` because it is a sanitized payload, not that function.

`origin/main` at 2026-10-06T13:15:42Z is `96683e6e7eecc2d35b5fa4cb632bfc0b2894e2ff`. `git merge-tree --write-tree origin/main HEAD` conflicts in `custom_components/heatpump_optimizer/diagnostics.py`. This head does not contain that tip. The measurements below are against merge-base `6568f70aed61f3197beed2ff4822fda473a5a785`.

## Head

fd23d5b5cee3b6b812b05aea08366fdc40d3b347

## Mutation proof

`RESULT arch_modules_on_disk` in `tools/audit/round4/D6/claims.py` set from 71 to 70, then `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`. Failed check: `tools/audit/round4/D6/claims.py RESULT arch_modules_on_disk matches header` with header `70` and printed `71`. Restored. The same script on the restored tree passed.

The `store.py` container-at-scalar proof stands at `6ddebd3120e7e59a1a223d89e9f9a3b36c102314`. The merge of `6568f70aed61f3197beed2ff4822fda473a5a785` does not touch that predicate.

## Null control

Restored header, `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: `ALL 105 HARNESS HEADER CHECKS PASSED`.

`PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 6568f70aed61f3197beed2ff4822fda473a5a785`: exit 0. `CLAIMED config_flow` names the three `debug_collect_enabled` leaves. Closing lines: `NO UNCLAIMED DRIFT` and `NO STALE FIXTURE`.

## Figures

`python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` at `6568f70aed61f3197beed2ff4822fda473a5a785`, 2026-10-06T13:15:42Z — mode line `MODE: SCOPED -- 29 script(s) run, 2 scoped out.` `tests/stress.py` is in `scope.run` and was not run.

`PYTHONPATH=tests/hastub python3 tools/audit/round3/D5/option_doc_coverage.py` — `RESULT option_fields_rendered=199 count`, `RESULT option_schema_keys_rendered=232 count`, `RESULT option_fields_undocumented=0 count`.

`PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/claims.py` — `RESULT arch_modules_on_disk=71 modules`, `RESULT arch_map_listed=71 modules`, `RESULT ha_module_level_importers=27 modules`.

`PYTHONPATH=tests/hastub python3 tests/harness_headers.py` on `9d28d1448e65c88ce29d339dd98f02a868307739` — `ALL 105 HARNESS HEADER CHECKS PASSED`.

`PYTHONPATH=tests/hastub python3 tests/golden.py --record --only config_flow` — recorded `config_flow`. Leaf diff against the previous fixture: nine new leaves, all under `debug_collect_enabled`, none removed, none changed.

`PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 6568f70aed61f3197beed2ff4822fda473a5a785` — exit 0, `NO UNCLAIMED DRIFT`, `NO STALE FIXTURE`. `claims-for:` equals `VERSION` `6.7.16`.

`python3 tests/structure.py` — `STRUCTURE RATCHET PASSED`.

`python3 tests/closure.py no-copies` on `fd23d5b5cee3b6b812b05aea08366fdc40d3b347` — `closure: no test file defines a symbol production also defines`.

Closures job 112237571054 log: every `done <script> (exit N)` line is `exit 0`, including `tests/features.py` and `tests/harness_headers.py`. That N is `closure.py record`'s exit. Artifact `closure-recordings` of run 37453972072: `tests/features.py` rc 0, `tests/harness_headers.py` rc 1. File-set difference of that features recording against the committed closure before this commit: only `custom_components/heatpump_optimizer/services.yaml` added.

`./tests/derive_closures.sh --single tests/features.py` on this host: recorder exit 0, script rc 1. The only failing check in the kept output is `R9-F2.1 P3: the shipped storage plan is no worse on its own objective than the half-price floor's plan refined under it` with shipped `110.4366` and seeded `110.1297`. That recording's file set is missing `tests/hastub/homeassistant/components/binary_sensor.py`, `tests/replay.py` and `tests/replay/synthetic-dhw-only.json` relative to the Linux rc 0 recording, so it was not merged. `python3 tests/closure.py merge --in-dir <the Linux features.py.json> --partial` wrote the Linux set, rc 0.

`python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 4` — `MUTATION TABLE INCONCLUSIVE`. Baseline `tests/features.py: rc=1 failed=2 648s`. The named check is the P3 line above. `tests/env_drift.py` baseline in the same drive: `rc=0 failed=0 143s`. No `killed_by` rows written. The inventory line before the drive: `PIN KILLED -- 52 new unpinned site(s)`.

## Red checks

`closures`. Under-scoped `tests/features.py` by `services.yaml`. The closures log's `exit 0` is the recorder. The artifact rc for that script is 0, so the read is complete. Cheaper detector: the recording JSON's `rc` plus `tests/closure.py check`, both already produced by the job. Standing cost of reading the rc is the artifact. No cheaper detector exists for a file a completed run newly opens.

`closures-autofix`. `skip-failed-recording`. The failed recording is `tests/harness_headers.py`, artifact rc 1, five header mismatches (`option_fields_rendered` 198/199, `option_schema_keys_rendered` 231/232, `arch_modules_on_disk` 70/71, `arch_map_listed` 70/71, `ha_module_level_importers` 26/27). Cheaper detector: `option_doc_coverage.py` and `claims.py`, which print those RESULT lines. Standing cost is those two scripts, seconds. The headers now name the printed counts, and `harness_headers.py` passes on this head.

`fast (3.14)`. `python3 tests/env_drift.py --all` and `python3 tests/harness_headers.py`. The header mismatches use the two scripts above. The float-free fixture's staleness is `python3 tests/golden.py --only config_flow` under strict mode, one option-flow capture. Unclaimed drift is `env_drift.py --all`, which is the check that went red. Both are green on this head against `6568f70aed61f3197beed2ff4822fda473a5a785`.

`mutation`. `MUTATION TABLE REFUSED`, 52 sites added unpinned on `button.py`, `debugger.py` and `store.py`. Cheaper detector: the inventory `python3 tests/mutation_table.py` prints before any mutant runs. Standing cost is that inventory, seconds. `--pin-killed` on this host is `MUTATION TABLE INCONCLUSIVE` because `tests/features.py`'s baseline is the P3 pair. CI's `fast` job on `8f756547` did not fail `tests/features.py`. No pins were written. The 52 sites remain unpinned in this tree.

`mutation-autofix`. `skip-measure-failed`. The measure step's `tests/env_drift.py` baseline was red (the `fast` failure). Cheaper detector: that same `env_drift.py --all`, which this head passes. The local pin drive then stops on the Darwin P3 baseline, so this host still cannot record the pins. CI's features baseline was green, so the next measure is not blocked by the env_drift failure this commit clears.

`delivery-status`. The diff adds `docs/delivery/1987.md`. Job 112236938339: `DELIVERY STATUS UNCHECKED — 28 rowed, 0 pending, 0 overdue`, seven merge commits on main whose subjects `subject_number` does not recognise. Cheaper detector: `python3 tests/delivery_status.py --check`, the check itself. The unread subjects are main's merges, not this row. Not changed here.

`pr-contract` on run 37453973764 was red because `## Red checks` did not name `closures`, `closures-autofix`, `fast (3.14)`, `mutation` or `mutation-autofix`. This body names them. Cheaper detector: `tools/audit/prepr.sh`, the same contract.

`nightly-status` graded main and this diff does not reach what it reads.

## Forward-carry

none

## Friction

none
