Fix review: blocked ef876fecadb909be228a7c686bda5fb822149ae1 ci-red: tests/config_flow_steps.py fails main's unrecovered-flow-error check on this PR's too_many_fault_text_entities, so tests / fast (3.14) and gate are red

bus-nonce: b96a42f81802db811e8baf4b6764c0e8

Round 2 (later round over the reviewed head 9f133225f72bc9581a411bdc40d544dd447f78ee), delta scope, head ef876fecadb909be228a7c686bda5fb822149ae1, merge base 5594a34a49404109b8e0f18bd5be18ddbb667cdf.

## Block

- At this head `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py` exits 1 with `1 of 690 checks FAILED` (`ev/config_flow_steps_head.log:812`):
  `FAIL every rendered flow error is recovered on the flow that rendered it  [options/entities_pump/too_many_fault_text_entities]`, `UNRECOVERED options/entities_pump/too_many_fault_text_entities`.
- The check comes from main (`94125c37ed`, "config_flow_steps: track rendered flow errors per instance, refuse an unrecovered one"). On origin/main `7f7e05118f` the same script prints `ALL 684 checks PASSED` (`ev/config_flow_steps_main.log`), so the red exists only on the merged tree. The PR adds the `too_many_fault_text_entities` error on the options telemetry page. Its test (`five fault-text entities are refused …; null control, four save`) never finishes the flow that rendered the error. The rooms page check beside it (`after its rooms error the same flow finishes`) shows the shape main's census now requires.
- This is the red on the required `tests / fast (3.14)` (job 138978772934, `1 TEST SCRIPT(S) FAILED`), and through it on `gate` (`FAIL tests / fast (3.14): failure (run 45541418514)`). Both names are in `merge_train.py owed-reds`. The body's `## Red checks` answers `tests / fast (3.14)` only for the #1218 note red at `7a666abfe9`, not this one.
  - I could not open the fast job's full log: its blob host is refused by this seat's proxy, and the MCP tail shows only the summary. The attribution rests on my local reproduction at the head. config_flow_steps is in the CI wall-clock list of scripts that ran.
- Repair: in the options fault-text test, after the five-entity refusal, submit four entities on the same flow and check that it finishes. This is a test-only change; the production cap is correct.

## Findings

None beyond the block. The previous verdict's lifecycle block and its three surviving mutants are all resolved at this head (Evidence).

## Red checks

- `tests / fast (3.14)`: red at this head. The cause is the block above. Not answered in the body for this head.
- `gate`: red only through `tests / fast (3.14)` (gate job 138995154315).
- `tests / nightly-ha (stable)`, `(2025.2.0)` and `nightly-status`: red, but not in the owed-reds set, so neither answered nor a block.

## Evidence

- RESULT previous block (failed setup leaves a live listener): resolved. `_ended` is registered through `entry.async_on_unload` and runs the once-only `_release`, then saves as a task kept on `rec.ending`. The next `async_setup` awaits `old.ending` before it loads (`fault_log.py:297-330`). The new check drives the failed-setup path against the unload-path null control: `failed == unload == (0, 0, [P3 row], 1, 1)`.
- RESULT mutation proof (`ev/mut_driver.py`, `ev/mutants.txt`): the fault-record block of `tests/features.py` passes at the head (`ALL 26 FEATURES BLOCK PASSED`, `ev/block_head.log`). The runner is `tools/audit/seat/features_block.py`, with its prelude from `--emit-prelude` and `PYTHONPATH=tools/devices`. I ran 9 mutants one at a time, restoring the file after each, and all 9 were KILLED:
  - the previous survivors F (`if part.strip()`), K (`[-EPISODES_MAX:]`) and L (`max(now_s, start_s)`);
  - X1 `_ended` not registered, X2 no `await old.ending`, X3 `_ended` releases without saving, X4 `_release` ignoring `closed`, X5 `async_close` skipping its save, X6 `_release` skipping the timer.
  - `git status` was clean afterwards.
- RESULT widening: none. The delta's production change is `fault_log.py` only. The `__init__.py` delta (the second `off_restore` pass) arrives from main, and the PR's own `__init__` lines are unchanged since round 1. I found no risk outside `fault_log.py` that CI would not detect. A failed `_save` is swallowed inside `_save`, so `await old.ending` cannot raise into setup.
- RESULT merge: `git merge-tree --write-tree origin/main ef876fecad` exited 0 at origin/main `7f7e05118f` (`ev/merge-tree.txt`).
- RESULT version: `VERSION`, `RELEASE_NOTES.md` and `manifest.json` have an empty diff from the merge base.
- RESULT CI: `merge_train.py classify ef876fecad --pr 3870` printed `RED ef876fecadb909be228a7c686bda5fb822149ae1 pending: none red: gate`, rc 1 (`ev/classify.log`).
- RESULT local runs at the head with `PYTHONPATH=tests/hastub`, all rc 0 except config_flow_steps: entities, structure, finite_boundary, deployment_shape, doc_claims, debug_collect, manual_plan and guard_pins (`ev/run_status.txt`). I did not use the full features.py run for this verdict; the fault-record block above is the part this delta touches.
- RESULT figures not re-derived: the round-4 mutation-table summaries and the #1218 count `180 of the 561` (CI's `tests / mutation` and `entities.py` at the head are green, and entities passed locally). I also did not re-derive the archscore NULL.
