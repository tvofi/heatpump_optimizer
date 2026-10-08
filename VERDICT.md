Fix review: merge 2629bf6a649495a05125473300995ffea4be0aa6
bus-nonce: 1ae60989f6491bc2ab13e8a2781c68f8

Round 4 of #2061: a delta review of the three-round split. The PR head 2629bf6a is the merge 49aba55c + 82860043. Its tree 88ee7a0b is byte-identical to 82860043's (`git diff 82860043 2629bf6a` is empty). I measured 82860043 in a fresh detached worktree (wt4). The live head was re-read after CI settled and is unchanged.

## Delta since my round-3 block (49aba55c)
- 0f64774f6 reverts the INERT READS downgrade. Against the merge base 4dbe5aace, `tools/pr/ci_predict.py` and `tools/pr/prepr.sh` carry no INERT READS or `warns` change, so they match main.
  - RESULT plant_inert.sh (harness only): `predict rc=1`, case=skip.
  - RESULT plant_inert_scoped.sh (harness plus a tests/wood_advisor.py comment, the round-3 hole): `predict rc=1`, case=scoped, rederive=['tests/wood_advisor.py']. Both refuse again, as on main.
- dd415b926 carries the item to R9-RO-9b as `carry-1922.json`'s first entry. Its JSON parses. It names the right predicate (the reading script is in `affected(changed)['rederive']`, or the case is full), VERDICT3's control, a remeasure recipe, and a three-plant self-test. `brief_lint`: `CARRY ok`.
- The main merge (82860043, main 4dbe5aace, which includes #2025) brought no conflict with this PR's files.
- Kept items re-checked cheaply at 82860043: the direct-push `entities.py` block runs ok (M5 and M6 were killed in round 3). tmp_paths self-test 50/0 and `--check` 0 refused. merge_train 81/0, record_row, layout and closure selftest pass, and structure.py PASSED. prepr --self-test gave 218/0, run once before the owner's no-heavy-local reminder.

## CI at 2629bf6a (check-runs API, settled; coverage is not required and is still running)
- `fast (3.14)`: `MODE: FULL`, `ALL 109 HARNESS HEADER CHECKS PASSED`, `ALL TEST SCRIPTS PASSED`.
- `mutation`: `4624 unpinned site(s) ... 4624 at the ratchet base 4dbe5aac`, `PASSED (empty scope)`. The PR changes no production line, so no count moved.
- Green: closures, instrument-self-tests, pr-contract, budget-raise-gate, delivery-status. All other required contexts are green.
- Red: `nightly-status` only. It reports last night's nightly and reads no file in this diff, so it is not this PR's (step 11).

Earlier rounds' RESULTs (cf84e0a4 round 1; the direct-push rule, rounds 2-3) stand for the unchanged code.
