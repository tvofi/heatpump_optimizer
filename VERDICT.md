Fix review: blocked 779c94324f7f15a17938526cc6e2c875170fabc0 mutation-vacuous: orchestrator_tick one_pr _classify_red call-site deleted; _classify_red except-branch flipped to fail open

bus-nonce: 1201d1a9e984cc9e4ead1050694a1e72

## Block

Round 1 (first review). Carry 9's production change is two parts: the helper `Tick._classify_red` and its use in `Tick.one_pr` (`tools/audit/seat/orchestrator_tick.py:1220-1221`, the lines that clear `self._red[n]` when classify does not read RED). The self-test exercises only the helper, called directly at `:4156`/`:4158` with `mt.Train.classify_at` monkeypatched. Two mutants survive `python3 tools/audit/seat/orchestrator_tick.py --self-test` at this head (305 checks, 0 failed under each; ev/mutants-head.txt):

- M3: delete the two `one_pr` lines `if red and required is not None and not self._classify_red(head, runs, required):` / `self._red[n] = []`. With this the tick reads the gate conclusion alone again, which is the merge-base behaviour the body's Null control describes. No check fails. The behaviour carry 9 claims, "the red-unowned level reads merge_train's classify, not the gate conclusion", is not pinned at the level that prints it.
- M4: flip `_classify_red`'s `except (mt.Stop, OSError, ValueError): return True` to `return False`. That makes it fail open, against its docstring's "fail closed ... an unread classify is RED". No check fails.

The body's named carry-9 mutant (`_classify_red` returning True unconditionally) is killed: 1 failed, "carry 9: a deferral red classify reads WAIT is not red-unowned". But it mutates only the helper's return value, not the wiring. What would fix it: one `one_pr` case with `required` set, a `gate` failure, and `classify_at` stubbed to `wait`. It asserts that no RED-UNOWNED line or `_red[n]` entry results, with the `red` stub as null control. A second case raises `mt.Stop` from `classify_at` and asserts that the red stands.

## Evidence

- Head reviewed: 779c94324f7f15a17938526cc6e2c875170fabc0 (ev/HEAD.txt). The body's figures were taken at 88a5ebe1415d4c420ccca7d649d432692fc28709. `review_carry.py 88a5ebe1 779c9432` prints CARRY: the range is a main merge (91811f03dd) plus the delivery row. The body names 779c9432 as head.
- Roles current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Merges with main: `git merge-tree --write-tree origin/main 779c9432` exit 0, tree 81efd52575f6d0ac7d89e72060b6452de44fc10e.
- Self-tests at head (ev/selftests-head.txt, ev/orch-head.txt), re-run by me:
  - beat_jobs: 195 checks, 0 failed, with PYTHONPATH=tests/hastub.
  - owed_unactioned: 59, 0 failed.
  - remerge_main_selftest: 2, 0 failed.
  - orchestrator_tick: 305, 0 failed.
  - The four figures in the body re-derive as 0 failed.
- Mutants killed:
  - carry 13: plan_cap_unread, killed by "plan-beat: the overlay's plan_coordinator_cap is handed to replan as --coordinator-cap". The null-control check "no plan_coordinator_cap leaves replan its own default" passes. replan.py defines `--coordinator-cap` at tools/plan/replan.py:3171 (type=int, default 2), so the pass-through hits a real flag.
  - carry 15: `remerge_main_selftest.py --mutant` gives 1 failed (the detached-worktree check). The attached null control stays ok.
  - carry 10: with the CAP_NOTICE skip disabled, owed_unactioned --self-test exits 1 with `Unreadable: an owed line names no topic ... capped at 8 of 11`. That is killed, though by a crash rather than a named FAIL line.
  - carry 9 helper: `_classify_red`→True gives 1 failed.
- VERSION, the manifest version, RELEASE_NOTES heading and both claim files are absent from the three-dot diff (ev/changed-files.txt). No golden fixture moved, so step 4 has nothing to compare.
- The new file tools/audit/seat/remerge_main_selftest.py is classified: it was added to tests/closures.json.
- Finder's harness: none. This group is roster carries, and each self-test is the fixer's own instrument.
- CI: `merge_train.py classify 779c9432 --pr 3425` printed `WAIT ... pending: gate red: none` on every poll (ev/classify.log). The digest's earlier `gate failure` (id 130265454654) is superseded by a pending run. No concluded red at this head is owed a `## Red checks` answer yet. This verdict's block is independent of CI.
- review_packet refusal `hot-file: #3384 ... shares tools/audit/seat/orchestrator_tick.py` is the train's sequencing concern. It does not bear on this patch.

## Findings

none
