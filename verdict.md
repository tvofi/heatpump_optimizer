Fix review: blocked 61e49d1d83ef45aa083f50a054493fa64227f615 test-red: the merge's tests/deployment_shape.py note says 180 of the 561 but the merged closures derive 182, so tests/entities.py fails its #1218 note check

bus-nonce: 34adb8bd370f247b97ca4e30a0ed35d5

Round 3 (later round over the reviewed head ef876fecadb909be228a7c686bda5fb822149ae1), delta scope: the repair `git diff ef876fecad d7324bbc58` and the main merge `f0a1881e9d` (origin/main `bb6377b4da` into `d7324bbc58`), head `61e49d1d83` merging `f0a1881e9d` onto `ef876fecad`.

## Block

- At this head `tests/entities.py` fails `and the lane's docstring records those measured numbers as the selection-cost note (#1218)` with `the note cites numbers this tree derives: 122 production files; 182 of 561 pairs at >= 0.80; 435 pairs comparable; ... missing markers -> ['182 of the 561']` (`ev/run_tests_entities.py.log:1591`).
- `_d308_pairs`' predicate, re-run on `tests/closures.json` (`ev/d308_count.py`, `ev/d308_count.txt`):
  - head `61e49d1d83`: 182 pairs;
  - main `bb6377b4da`: 182;
  - pre-merge branch `d7324bbc58`: 180.
- The hand-resolved hunk in `tests/deployment_shape.py` carried the branch's pre-merge 180 forward. The ledger driver's merged `tests/closures.json` moves 4 pairs relative to main:
  - Two leave: `boost_drift_replay.py`/`config_flow_steps.py` and `config_flow_steps.py`/`plan_view.py`. Each goes from 0.802 to 0.794, not the 0.800 to 0.792 the note states.
  - Two enter: `env_drift.py`/`manual_plan.py` and `golden.py`/`manual_plan.py`.
  - The net is 182. The body's `## Head` claim that "this branch's two-pair movement holds on main's tree (182 - 2)" does not hold at this head.
- The merge hunks were checked as follows:
  - `tests/features.py` is a pure union: the sorted +/- line sets of the PR side `5594a34a49..d7324bbc58` and the merge side `bb6377b4da..f0a1881e9d` are identical.
  - The `docs/architecture.md` and `claims.py`/`.json`/`.md` counts (103 modules, 37 importers) are correct: `claims.py` rc 0, `arch_modules_on_disk=103`, `ha_module_level_importers=37`.
  - The `all 122 files` count in `deployment_shape.py` is correct.
  - Only the pair count and its narrative are wrong.
- Repair (test docstring only): in `tests/deployment_shape.py`'s #1218 note, write `182 of the 561` and `all 182 among the 435`. Rewrite the parenthetical to the measured movement at the merged closures: the two `config_flow_steps.py` pairs leave at 0.794 and the two `manual_plan.py` pairs enter. Re-run `PYTHONPATH=tests/hastub python3 tests/entities.py`.

## Findings

None beyond the block.

## Evidence

- RESULT previous block (`tests/config_flow_steps.py` unrecovered `too_many_fault_text_entities`): resolved. `d7324bbc58` adds `await recover(flow, "entities_pump", {key: members[:4], **SAVE_CLOSE})`. At the head `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py` exits 0 with `ALL 691 checks PASSED`, `ok after its entities_pump error the same flow finishes` (`ev/config_flow_steps_head.log`).
- RESULT mutant: I deleted that line at the head. The run then exits 1 with `1 of 690 checks FAILED`, `UNRECOVERED options/entities_pump/too_many_fault_text_entities` (`ev/mutant_no_recover.log`). I restored the file, and `git status` was clean.
- RESULT merge-side local runs at the head (`PYTHONPATH=tests/hastub`, `ev/run_status.txt`):
  - rc 0: `deployment_shape.py` (`ALL DEPLOYMENT SHAPE CHECKS PASSED`; it does not check the pair count), `dev/audit/rounds/round4/D6/claims.py`, `structure.py` (`STRUCTURE RATCHET PASSED`) and `doc_claims.py` (`ALL 443 checks PASSED`).
  - `entities.py` hit this seat's 600 s timeout (rc 124) after printing the FAIL above. It also printed `a3:*` and `a4:bridged` FAIL lines. I did not attribute those to this PR, and the block rests only on the #1218 line, which is a deterministic count re-derived independently in `ev/d308_count.txt`.
- RESULT merge with main: `git merge-tree --write-tree origin/main 61e49d1d83` exits 0 at origin/main `bb6377b4da` (`ev/merge-tree.txt`).
- RESULT version: `VERSION`, `RELEASE_NOTES.md` and `manifest.json` have an empty diff from main `bb6377b4da` at this head.
- RESULT carry: `review_carry.py ef876fecad 61e49d1d83` prints `FRESH-REVIEW`.
- RESULT CI: `merge_train.py classify 61e49d1d83 --pr 3870` printed `WAIT ... pending: gate red: none` through the last poll (`ev/classify.log`). The block does not rest on CI: it rests on the local reproduction above. `tests/entities.py` runs under the required `tests / fast (3.14)` and so under `gate`.
- RESULT not re-checked: the driver-resolved `tests/structure_budgets.json` and claim files, which are outside the orchestrator's stated scope. `structure.py` passed at the head.
