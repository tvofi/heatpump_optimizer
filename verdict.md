Fix review: merge 2437d0fbe077c4d82c9453b698045b6e1d35bf3b

bus-nonce: 9c89676da451c5ae462e51f39d1affd5
pending-ci: tests / closures, tests / fast (3.14), tests / replay, tests / coverage, tests / mutation-pins (1)

## Round

Round 2, a delta review over the reviewed head `22e9330193f147e8b02b0171890b9c338ef6b0e3` (blocked `reference-basis-unbumped`). Measured at head `2437d0fbe077c4d82c9453b698045b6e1d35bf3b` from a detached worktree; merge base with origin/main `c987209cc7a891e0e4066d4ad8dc5cf55357c5ae`. `review_carry.py 22e93301 2437d0fb` prints `FRESH-REVIEW`, so the scope is the delta (`ev/delta.diff`): 194625754d (basis bump and test), fc372c8094 (stale pin deleted), 3b64f939 (hand-driven merge of origin/main c987209cc7, v7.1.16) and 2437d0fb (merge of 3b64f939 into the previous head, adding only the delivery row). The only production delta on the branch side is `ledger.py`'s `REFERENCE_BASIS` 1 -> 2 and its comment. That line is read in two places, `ledger.py:370` (the first-booking stamp) and `ledger.py:513` (the old-basis test), and the delta does not widen the review past them.

## Findings

- Body figure: `## Mutation proof` gives the `REFERENCE_BASIS = 1` mutant as `1 of 5 FEATURES BLOCK FAILED`. Re-run at this head with the body's own command, it is `2 of 5`: both "a month's first savings booking stamps the reference in force, once" (stamp `{'sum': 1.0}` against the literal 2.0) and "a month stamped 1, the spread reference, states no saving after the change" (`old_basis False`, `savings_sek 0.0`) fail (`ev/mut_basis1.log`). The kill the body claims holds and is stronger than stated. Only the count is wrong, so the verdict does not turn on it. Carry: dismissed: a body miscount in the conservative direction; the kill it supports is re-derived at 2 of 5
- Body account of the merge: `## Head` says any resolution inside the code head "is described below", and none is described. The resolution in `tests/golden/claimed_drift.txt` moves the eight claim lines from under the part-2 reason block (`Direction per fixture, branch vs base:`) up to under the 7.1.16 header, so that reason block now ends with nothing after it. Content is complete and `env_drift.py --all` honours every claim (see Evidence), so this affects how the file reads, not what it says. Carry: dismissed: cosmetic placement inside a claim file that the next stamp empties; no claim, entry or reason lost

## Evidence

- (a) The previous block is resolved. At this head `ledger.py:76` reads `REFERENCE_BASIS = 2`, and its comment names basis 1 as the v7.1.15 spread reference. Mutation proof, run with `features_block.py` from `# R10-HOTFIX-SAV-ESTIMATE: a month's reference basis.` to `# A v1 month holding lines but no savings yet`, using a prelude from `--emit-prelude` at this head:
  - Head: `ALL 5 FEATURES BLOCK PASSED`, rc=0 (`ev/mut_head.log`).
  - Mutant `REFERENCE_BASIS = 1`, the reviewed head's value: `2 of 5 FEATURES BLOCK FAILED`, rc=1 (`ev/mut_basis1.log`). The new check "a month stamped 1 ... states no saving after the change" is among the failures.
  - So the check the block asked for exists and fails at the blocked head's value. Restored afterwards; the worktree is clean.
- Killed-by pin `ledger.py/@module.CONST.2df661b8` (old `REFERENCE_BASIS = 1`) is deleted because its line no longer exists. The new line is unpinned until `mutation-autofix` pins it (`ci-autofix.md`), and the body's `## Red checks` / `## Unpinned sites` name it.
- (b) The merge 3b64f939, `tests/golden/claimed_drift.txt` at the head against both parents (`ev/merge_files.diff`, `ev/claimed_drift_head.txt`):
  - Against main c987209c, the head adds exactly the branch's footprint:
    - The eight valved `baseline_cost` claims, with directions.
    - Six suspended may-drift entries in the two-line restore form: valve_storage_smart_write, wood_two_tank, wood_two_tank_smart_write, wood_coil, valve_upper_direct_slab and valve_storage.
    - The part-2 reason block.
  - `claims-for: 7.1.16` and main's v7.1.16 header are kept.
  - Against the branch fc372c80, the only differences are the claims-for/header update to 7.1.16 and the eight claims' position. Nothing is dropped.
  - `card_claimed_drift.txt` at the head is byte-identical to main's.
- Claims against drift, `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all` at this head against origin/main: every one of the eight claims reports `CLAIMED ... leaves moved` with the claimed direction and values, then `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56`, rc=0 (`ev/env_drift_all.log`). Every claim moved and every move is claimed. The default mode run also reads rc=0 (`ev/env_drift_head.log`).
- `tests/structure_budgets.json` at the head:
  - `class_excess_loc` is 17470, below both parents (main 17503, branch 17481).
  - `recorded_at` is e23124ff. Every other key equals main's.
  - `python3 tests/structure.py` at the head gives `RESULT class_excess_loc=17470`, rc=0 (`ev/structure_head.log`). No budget is raised.
- `VERSION`, the manifest and the `RELEASE_NOTES.md` heading: the delta's changes to them are main's v7.1.16 stamp brought in by the merge. The three-dot branch diff against c987209c does not touch them.
- Merge with main: `git merge-tree --write-tree origin/main 2437d0fb` gives tree 923fa896..., rc=0, no conflict (`ev/merge_tree.log`). origin/main is the merge base c987209c.
- Roles current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- (c) The body and the head: `## Head` names `2437d0fbe077c4d82c9453b698045b6e1d35bf3b` as the head and describes it as the authored code head 3b64f939 plus a merge into the previous head. That matches the parents I read: 2437d0fb = 22e93301 + 3b64f939, and 3b64f939 = fc372c80 + c987209c. The body's "the head is fc372c80" sentence describes the authored code commits, which is consistent. The body describes this head, apart from the two body findings above.
- Gate red in the body: the one scoped-gate red at fc372c80 was the weekend-clock check owned by R10-HOTFIX-FEATURES-WEEKEND-CLOCK, #3578. That PR is merged on main and inside this head through c987209c.
- Not re-derived here; the previous round's evidence stands for code the delta does not touch: the residual attribution, census, Carry 9 / Carry 10 figures and the restated-pin null control. Carry: dismissed: evidence, not a finding
- CI: see the classify lines below (`ev/classify.log`).
- CI at this head:
  - `merge_train.py classify 2437d0fb --pr 3574` was polled from 03:22 to 03:57 UTC. It printed `WAIT 2437d0fbe077c4d82c9453b698045b6e1d35bf3b pending: gate red: none`, rc=3, every time (`ev/classify.log`).
  - The live check runs at 03:58 UTC: `tests / closures`, `tests / fast (3.14)`, `tests / replay` and `tests / coverage` are in progress, and `tests / mutation-pins (1)` is queued.
  - `tests / mutation` is completed failure. This is the predicted `ADDED UNPINNED ledger.py:76 CONST: REFERENCE_BASIS = 2`. The body's `## Red checks` names it and answers it: the cheaper detector `ci_predict.py` fired before handoff, and `mutation-autofix` pins the site. My mutation proof shows the site is killed.
  - `gate` and `tests / nightly-status` are failures that classify does not count as gate reds. I did not judge them beyond classify.
  - The review is otherwise complete, so I am returning `merge` with `pending-ci:`.
