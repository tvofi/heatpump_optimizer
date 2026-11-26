Fix review: merge 3da16553914c71017ee25fd98486f2125083016c

bus-nonce: 0a30ac48feda2a9a7640ebbbf5999406
pending-ci: gate

## Scope

Delta round (later round over the previous verdict `blocked 625cc2c2aef154c507b37cefb015b1c40b27bde7` on a main conflict in coordinator.py, pump_arbiter.py and tests/entities.py). Scope: `git diff 625cc2c2ae 3da1655391`, read as the resolutions of every PR-side merge in that range (`git show --remerge-diff` on each merge in `625cc2c2ae..3da1655391 ^origin/main`). The previous verdict's one finding (the main conflict) is resolved. No production delta beyond the conflict resolutions, so the scope is not widened.

## Evidence

- RESULT merge-tree: `git merge-tree --write-tree origin/main 3da1655391` (origin/main `dbdc71faea`) exits 0, tree 133173eb63, no conflicting path (ev/merge-tree.txt). The head's second parent is `dbdc71faea`, so it already contains current main.
- RESULT resolutions: four PR-side merges in the range carry a hand resolution; all others remerge with no diff (only ledger-driver files).
  - `3654956d84` (ev/remerge-3654956d84.txt): coordinator.py keeps this branch's `early_cutoff.arm(held, inputs, boosts, on_unload)` call and main's off-restore block (`_plan_let_go`, `off_restore.async_cycle`); main's extra `_ctx_of(self)._opt_config` argument is dropped, which is correct because `early_cutoff.arm` at the head takes no `opt_config` (it reads `ArbiterInputs.opt_config`) and its one call site matches (checked by `git grep` at the head). pump_arbiter.py keeps both `opt_config` and `entry` fields. tests/entities.py keeps main's `("circulation.py", "command")` and drops main's `_async_update_data`/`_async_first_refresh_light` allowances, which this branch's `_fail_update_held` latch removes; entities.py passing at the head confirms the allowance matches the code. A union of both sides' behaviour.
  - `d13c3e840a` (ev/remerge-d13c3e840a.txt): boost.py `.store` import is the union `admitted, load_mapping, save_held`.
  - `dcdb80d974` and `74a0197a20` (ev/remerge-*.txt): tests/features.py keeps both sides' blocks entire; the only edit replaces the conflict separator with the `)` closing this branch's last `R.check(`.
- RESULT features.py at head (worktree, `PYTHONPATH=tests/hastub`): `ALL 6235 FEATURE CHECKS PASSED`, RC=0 (ev/features-tail.log). The `# R11-SEAM-cycle-reporting: how a failure is reported` block header occurs once and `R.section("#3616 R11-OUTSIDE-ROOMS-3B: the room lift on the solve's record, ...")` once.
- RESULT entities.py at head: `ALL 2779 ENTITY CHECKS PASSED`, RC=0 (ev/entities.log; the `FAIL a3:`/`a4:`/`hb:` lines inside it are self-tests' planted negative controls, the exit code is 0).
- RESULT structure.py at head: `STRUCTURE RATCHET PASSED`, RC=0 (ev/structure.log).
- RESULT budgets: `git diff origin/main 3da1655391 -- '*budgets*.json'` moves only tests/structure_budgets.json, every row down or equal: class_excess_loc 17228 -> 17224, max_class_loc 7821 -> 7813, module_excess_loc 21753 -> 21741, recorded_at only otherwise (ev/budgets-vs-main.diff). No budget rises, so no raise is owed. The PR-side `structure: re-record` commits 5be21e3d57 and 8b7a4d2e18 move only `recorded_at` (bodies and diffs read).
- RESULT version: three-dot diff touches no VERSION or RELEASE_NOTES.md; manifest.json's only three-dot change is `quality_scale` platinum -> gold, already in the reviewed diff at 625cc2c2ae (D10-s3-01), and not in the delta. The manifest `version` is main's.
- RESULT CI: `merge_train.py classify 3da1655391 --pr 3845` printed `WAIT ... pending: gate red: none` (rc=3) at every poll from about 07:25Z to 08:02Z (ev/classify.txt); hence `pending-ci: gate`. The only red check run at the head is `tests / nightly-status`, which is not in `merge_train.py owed-reds` (coverage-ratchet, fast (3.14), mutation, typing, validate-hacs), so no answer is owed; the body answers it anyway, and its codeql runner-loss answer stands (`codeql / Analyze (python)` reads success at this head, job 139754700564).
- RESULT head re-read: `refs/heads/fix/r11-seam-cycle-reporting-pr` is still 3da1655391 at 08:02Z.
- RESULT runs: features.py and entities.py were each run alone at the head; a combined run hit this host's 30-minute background limit and was restarted.
- Note: body: the `## Head` section says of `dcdb80d974` that no production or test file conflicted, and of `74a0197a20` that resolutions inside the code head are "described below" without describing one; both merges hand-resolved a tests/features.py conflict (union, verified above).

## Findings

none

## Friction

none
