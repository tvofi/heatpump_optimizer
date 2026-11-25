Fix review: merge 0d68ee30548a3806413e0e2cf03dbccb2a76ff33

bus-nonce: d0e16720bc92ef1961d87bbb705609be

Note: ci-unreadable: `merge_train.py classify 0d68ee30548a3806413e0e2cf03dbccb2a76ff33 --pr 3738` exits 2 (unreadable) on every run from 05:12:39Z to 05:15:08Z: `REFUSE selftests: the head's governance / instrument-self-tests job 138967739812 concluded cancelled, which reads no step: re-run it: an introduced red cannot be ruled out (fail closed)`. The job ran from 03:58:58Z to 04:29:01Z, about the 30-minute wall. Steps 1-125 are success or skipped. Step 126, "Show the CI predictor (tools/pr/ci_predict.py) predicting pr-contract's carry refusal", is `cancelled` after 2 minutes, and every later step is skipped. The check is not in the `owed-reds` set (ev/owed_reds.txt). The PR's own commits in this delta touch no instrument path. This seat makes no GitHub write, so it cannot re-run the job. The train must re-run it before the merge. Carry: dismissed: a cancelled run carries no verdict; the orchestrator re-runs it before the train merges
Note: stale-figure: the body's `## Figures` still says the local coverage re-measure of `room_history.py`, `room_record.py` and `draw_range.py` "was still running ... its numbers replace this line". The body's `## Head` says instrument-self-tests "re-runs at this head", but it was cancelled again at this head. CI's `tests / coverage-ratchet` (job 138984512903) is success at this head, so that substance is measured. Carry: dismissed: paperwork on body figures; the coverage substance is CI-measured green at this head

Round 7, delta only (tvofi 2026-11-09, fix-review.md step 12). The reviewed head is 310c601f4078a394fe527329a6a1fd8e1368cca0, round 6 verdict `merge` (probe/rev-3738-8cf5054b 64025f2c). This head is 0d68ee30548a3806413e0e2cf03dbccb2a76ff33. The packet's `## Review scope: full` line comes from verdict/3738, which records no verdict at 310c601f. The round-6 verdict on its probe ref names 310c601f, so this seat reviews the delta, as dispatched. No earlier round's block is open, so the fourth-round re-cut rule does not apply.

## Delta
- The PR's own non-merge commits in 310c601f..0d68ee30 are:
  - 3d58d9384c, bot: one pin, `mode_superseded.BOOLOP.e8c41bd1`.
  - 0275a76bf3: `tests/features.py`, where the `_SgUpstreamDebouncer` rig passes `loop=get_running_loop()` to its two eager Tasks.
  - 447c6c42ce: `structure_budgets.json` `coordinator_attrs` 135 -> 134, plus `recorded_at`.
  - 4a51684f30, bot: closures re-record.
  - 086186b85d: eight `killed_by` pins.
  - 5a7b1914d3, bot: the same eight pins.
- No production delta. The PR's own production diff (`git diff <mb> <head> -- custom_components`) differs between 310c601f (mb eaaaf24e) and this head (mb 3210fcd7) only in `index` lines and hunk offsets (ev/prod_diff_interdiff.txt). This is not widened: no reviewed functionality moved.
- Merges (`git show --remerge-diff`, ev/remerge_*.txt):
  - 8895b799a6, 47a5726f66 and 0f6b683470: LEDGER-MERGE only (closures as sets).
  - 0a349d4716 and 0d68ee3054: empty.
  - 718e98c6e9: conflicts in `dev/audit/rounds/round4/D6/claims.{json,md,py}`, `docs/architecture.md` and `tests/deployment_shape.py`. Each one is a count that both sides moved. Each was resolved to main's value plus `solve_gate.py`: 101 -> 102 modules, 120 -> 121 package files, and 36 `homeassistant` importers with the other 65 free of it. These were re-derived at the head (Evidence).
- The 0275a76bf3 mechanism was checked independently with a probe outside features.py (ev/eager_probe.txt). On Python 3.13.18, `asyncio.Task(coro, eager_start=True)` with no loop raises `AttributeError: 'NoneType' object has no attribute 'is_running'`, and with `loop=get_running_loop()` it returns. On 3.14.7 both forms return. The rig change is therefore behaviour-neutral on 3.14 and is the 3.13 cure that the body names.

## Prior findings
- Round 6 Note owed-red `tests / mutation`: resolved. At this head `tests / mutation` (job 138967739829) is success. All nine sites round 6 measured killed are pinned at the head (ev/pins.txt): `async_run_optimization.GUARD_OFF` 387891d0/45582598/8bbbc8d1/b8fb4bbc, `_await_optimize.GUARD_OFF` 32e16df1, `mode_superseded` BOOLOP/RETURN_DEL e8c41bd1 and `worker_stopping` BOOLOP/RETURN_DEL 9ef45ec5. Eight are pinned `killed_by tests/features.py` and BOOLOP e8c41bd1 by `tests/entities.py`. The production lines are unchanged since round 6, where this seat's predecessor killed each with targeted block mutants, so those kills stand.
- Round 6 Note stale-figure (`## Figures` at 4e5de6bad8): still partly stale. It is re-carried as the stale-figure Note above.
- Round 6 Prior finding `tests / coverage-ratchet` red: resolved. The cause was the 3.13 eager-Task crash that 0275a76bf3 cures. At this head `tests / coverage` (138968415727) and `tests / coverage-ratchet` (138984512903) are success.

## Evidence
- RESULT head: `git ls-remote origin refs/pull/3738/head` = 0d68ee30548a3806413e0e2cf03dbccb2a76ff33 (ev/head_live.txt). The body's `## Head` names it.
- RESULT merge_tree_rc=0: `git merge-tree --write-tree origin/main 0d68ee30`, origin/main 7f7e05118f (ev/merge_tree.txt).
- RESULT version/claims: `git diff --name-only 3210fcd733...0d68ee30 -- VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt` prints nothing (ev/version_files.txt).
- RESULT structure: `python3 tests/structure.py` at the head gives `STRUCTURE RATCHET PASSED` rc 0 and `coordinator_attrs 134 <= 134` (ev/structure.log). 447c6c42ce lowers a budget and raises none.
- RESULT claims: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` rc 0 gives `claims_false=0`, `arch_modules_on_disk=102` and `arch_map_listed=102` (ev/claims.log). `git ls-files custom_components/heatpump_optimizer | wc -l` = 121, matching the resolved `deployment_shape.py` and the body.
- RESULT step 14: the delta's only metric moves are `coordinator_attrs` -1, a re-record of the merged tree with no instrument change, and pins that CI's own `--pin-killed` drive and the bot reproduced. Nothing is raised and nothing is gamed.
- CI at this head (packet digest; the live head is unchanged): success for gate, tests / fast (3.14), closures, coverage, coverage-ratchet, mutation, typing, browser, arch-instrument, closure-scope, briefs, replay, graders-head-copy, lane-proofs, governance / env-matrix, policy-docs, wave-script, pr-contract, hassfest, validate-hacs, codeql (3), arch-score and budget-raise-gate.
  - Failure: tests / nightly-ha (stable, 2025.2.0) and nightly-status. None of these is in `owed-reds` (ev/owed_reds.txt), so none is answered or blocks. The body notes nightly-ha as seen on other PRs.
  - Cancelled: governance / instrument-self-tests (first Note).
- Classify: exit 2 (unreadable) on each run (ev/classify.log). There is no WAIT, so no `pending-ci` line.
- Finder's harness: none named (packet). This delta adds no production line and no finding. Instruments used: `structure.py`, `claims.py`, `git merge-tree`/`--remerge-diff`, and an own 3.13/3.14 eager-Task probe (ev/eager_probe.py, this seat's).
