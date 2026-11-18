Fix review: blocked 8518497c1ad76bdd06e5025532e9ac3eea2558ae ci-red: tests / mutation refuses 5 added sites the block kills but no killed_by row pins

bus-nonce: 403c95946b5d236bae1d637934c36118

## Block

- Required `tests / mutation` is red at this head, so `gate` is red and `merge_train.py classify 8518497c1ad76bdd06e5025532e9ac3eea2558ae --pr 3711` exits 1 (`RED 8518497c1ad76bdd06e5025532e9ac3eea2558ae pending: none red: gate`). Re-run here at the head, `python3 tests/mutation_table.py --scope changed --base origin/main --max 10 --jobs 3` prints `MUTATION TABLE REFUSED -- 2096 unpinned site(s) against 2091 at the ratchet base 7c2f4c30cab5..., 5 of them added by this diff`: `room_history.py:124 GUARD_OFF`, `:182 CMP_BOUND`, `:276 CLAMP_DROP`, `:302 RETURN_DEL`, `:334 CMP_BOUND` (ev/mutation_table_scope_changed.txt). The bot commit that is this head (`ci: pin killed mutants`, 32 rows) left these five out, and the autofix lanes are skipped at their own commit, so nothing further repairs it at this head.
- These are not survivors. Each mutant, applied by hand at the head and run with the body's features-block CMD (pycache cleared per run), is killed: 124 GUARD_OFF 1 FAIL, 182 `<=` KeyError, 276 clamp dropped 1 FAIL, 302 `return r` deleted TypeError, 334 `<=` 1 FAIL (ev/mutant_*.txt). The repair is mechanical: `python3 tests/mutation_table.py --pin-killed --base origin/main` (features.py runs about 17 min per mutant here, so give the drive enough budget), or a mutation-autofix run on a new head. The code and tests need no change. A `merge` at this red would be refused (C8).

## Evidence

- Setup: `cloud-setup.sh --check` OK; role contract current against origin/main (the roles diff touches only proposal-triage.md and root-cause.md). This is the first round reviewed on this seat's record: the earlier seat on this dispatch left no probe ref.
- Merge with main: `git merge-tree --write-tree origin/main 8518497c1ad76bdd06e5025532e9ac3eea2558ae` rc 0, no conflict (ev/merge_tree.txt).
- RESULT features block at head: `ALL 40 FEATURES BLOCK PASSED` rc 0 (ev/features_block_head.txt). This matches the body's 40.
- Mutation proof, departure 1 ("first reading"): with `room_history.py:115` set to `if True:` (each reading overwrites, so the last reading wins), 4 of 40 checks fail. They include `independent calling reads separable ...`, whose 10-minute arm reads `b_k_per_h` 0.498 and 0.685 against the simulated 2.0. That re-derives the body's "0.50 K/h" (ev/mutant_first_reading.txt).
- Version: `git diff merge-base...head` touches none of VERSION, the manifest, RELEASE_NOTES.md, the claim files or any `*_budgets.json`. CI's pr-contract prints `no version edit`.
- Claims: no claim file is touched. Golden drift was not re-run here; the body's `NO UNCLAIMED DRIFT` is taken as the figure it states.
- Actuator writes (step 16): none. The production diff adds a best-effort cycle step, an unload flush, a diagnostics key gated on a record, a store domain and a sensor.
- Class (step 6): the body's enumeration rules (`QuarantiningStore(` sites, `_best_effort_cycle_step(` sites) are named. The new store's `_FR_STORES` and `DOMAINS` coverage is enforced by features.py's AST walk and finite_boundary.py arm 1, and both pass in CI at this head.
- Finder's harness: none. #3616 is an outside report, as the body discloses (step 9). The block is the fixer's instrument.
- Architecture: the `arch-score` check is green. The body discloses `dS -0.0121 WORSENS (inadmissible: coord_footprint 2502->2523)`; not re-derived here.
- `pin_killed_partial_tail.txt`: a local `--pin-killed` drive, stopped after its baselines and null control. features.py was too slow here for it to finish, so the hand-run kills above stand in for it.
- CI at this head: red `tests / mutation`, `pr-contract / pr-contract` and `gate`. Every other required context is green.

## Red checks

- `tests / mutation`: owed. The body's `## Red checks` answers it for the earlier heads 1fe21304 and 9597676033 and expected mutation-autofix's next pin run to clear the sites. At this head five remain, and the autofix that ran did not pin them. Note: root-cause-detectable: `tests/mutation_table.py --scope changed` (seconds) shows the five at this head before any handoff.
- `pr-contract / pr-contract`: `figure-block scope-line names another head (3b28652da775, this is 8518497c1ad7)`. The bot push moved the head under the body. This is paperwork (C5). Note: body-stale: refresh the figure block and `## Head` at the new head.
- `gate`: the aggregate of the two above; it has no cause of its own.

## Findings

- Note: body-stale: `## Head` names 3b28652da775. The head is the bot's pin commit 8518497c1ad7, and `## Unpinned sites` / `## Red checks` still describe 37 remaining sites. Carry: R11-OUTSIDE-ROOMS-P3 | dismissed: paperwork the fixer refreshes with the pin commit that clears the block

## Friction

none
