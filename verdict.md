Fix review: merge 44524f9a7f2b14bdb7cea805fcc756db6e2e1b06

bus-nonce: ff642236295c9a3daca2b117f40859c2
pending-ci: tests / mutation, tests / closures

## Scope

Round 4 of #3841 (verdicts at 8b127c6d, b0ee904f, b53176e2 before it); a delta round over `git diff d9d48364 44524f9a`, as dispatched. The packet's `## Review scope` line read `full` only because verdict/3841 names b53176e2, not d9d48364; d9d48364 descends from b53176e2 through the bot's `bf58a82d54` pins, its main merge `534bde9fe4` and `0d024e2804` (structure re-record on main). The PR's own non-main commits in b53176e2..44524f9a are `a863095571` (tests and ledger only), `bf58a82d54` and `0d024e2804`; every `custom_components/` line in the delta comes from main (#3866, #3873 and others), already reviewed and merged there, so the delta does not widen the scope.

## Evidence

- Prior finding (verdict/3841 at b53176e2, tests-red, five added sites alive): each re-mutated at 44524f9a in a detached worktree, full `tests/features.py` run (PYTHONPATH=tests/hastub), file restored. Unmutated baseline: `ALL 6204 FEATURE CHECKS PASSED`, rc 0 (ev/full-base.log.tail).
  - dhw_planner.py:96 GUARD_OFF (`if False:`): killed. The new check "the next DHW window on an empty horizon is None ..." FAILs with `IndexError('index 0 is out of bounds ...')` (ev/partial-M1-killed-by-monitor-expiry.log.fails; that run was cut short when its watcher expired, after the FAIL had been printed).
  - dhw_planner.py:99 CMP_BOUND (`<` -> `<=`): killed, `1 of 6204 FEATURE CHECKS FAILED`, rc 1, same check (ev/full-M2-*).
  - sysid.py:2504 GUARD_OFF (`if False:`): killed, `1 of 6204 FEATURE CHECKS FAILED`, rc 1: "arm_refusal answers a press on an armed experiment ..." `[True '']` (ev/full-M3-*).
  - sensor.py:545 RETURN_DEL (`return None` -> `pass`): survives, rc 0, matching its `survivor_triage` verdict `equivalent`. The deleted statement is the last one of `_open_saving`, so the method still returns None on every input (read at the head, sensor.py:538-545).
  - dhw_schedule.py:566 CMP_BOUND (`start > h` -> `start >= h`): survives, rc 0, matching its `equivalent` verdict. At the head, `_parse_one_range` raises on `start == end` except `00:00-00:00`, which it maps to FULL_DAY (dhw_schedule.py:291-298). I traced the window lists that reach `hours_until_next_window` without going through the parser: dhw_planner.py:565/571 and thermal_model.py:869 return `[FULL_DAY]` = (0, 24), and the learned windows go back through `parse_windows` (dhw_planner.py:584). None of them is zero-length, so `hour_in_windows` returns first whenever `start == h`. That trace is mine (a read-only extraction), not an instrument's.
  - Null control (a trailing comment on dhw_planner.py:96): `ALL 6204 FEATURE CHECKS PASSED`, rc 0 (ev/full-M0-*).
  - The five ledger files are present at the head (ev/ledger-five.txt).
- Main merges in the delta: I compared each merge commit's tree with `git merge-tree --write-tree` of its parents. 44524f9a7f and e35df9d9d3 are identical to the automatic merge. 78bf3efa43 differs only in tests/deployment_shape.py, which hand-resolves a docstring conflict: the selection-cost figure reads 182, with the branch's and main's histories joined. It is a test docstring, and CI's tests lanes grade it.
- `git merge-tree --write-tree origin/main 44524f9a`: rc 0, no conflict; merge base == origin/main 91773476ed (ev/merge-tree.txt).
- VERSION, manifest.json and RELEASE_NOTES.md: untouched in d9d48364..44524f9a.
- tests/structure_budgets.json in the delta: class_excess_loc 17253 -> 17251 and max_class_loc 7823 -> 7821, from main; downward only.
- CI at 44524f9a (check-runs API, 19:41Z): `governance / instrument-self-tests` success (the packet's `introduced-red` refusal was its in-progress state, now concluded), `tests / fast (3.14)` success, `tests / typing` success, `validate / validate-hacs` success, `budget-raise-gate` success, `arch-score` success. `tests / mutation` and `tests / closures` are still in_progress, and `gate` is red only behind them. `merge_train.py classify` printed `WAIT 44524f9a... pending: gate red: none` from 18:50Z to 19:41Z (ev/classify-last.txt); it named no context, so the pending-ci line above names the two in-progress jobs from the check-runs API.
- Reds outside the owed set: `tests / nightly-status`, `tests / nightly-ha (stable)` and `tests / nightly-ha (2025.2.0)` are red. `merge_train.py owed-reds` prints `tests / mutation`, `tests / typing` and `validate / validate-hacs`, so none of these three is owed an answer or blocks.
- Body figures: the head line (44524f9a, code head 78bf3efa) matches what I measured. The body's `mutation_table.py --list` re-read is not re-derived here; the ledger files above stand in for it.
