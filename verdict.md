Fix review: merge 71710c566283e302de7db598c8a6fc3045a41dbf

bus-nonce: 83d9e603fbafe230726bfa8571a3affc

## Summary

This is round 2 of the review of PR 3278 (R10-RCA-GATE-BUSY-DEFER-2), at head 71710c566283e302de7db598c8a6fc3045a41dbf. The merge base is b4ec2f332, and origin/main is now 4b5d771bd. Round 1 returned `blocked d5c4a06b rca-claim-false`. The repair commit b38e5c08 fixes the reason for that block. The head 71710c56 is a merge of b38e5c08 into 510b2a108, and its tree is identical to b38e5c08's (`git diff --stat b38e5c08b 71710c56` is empty). `review_carry.py d5c4a06b 71710c56` prints FRESH-REVIEW, so I reviewed the whole three-dot diff again.

- Block resolved. The RCA, the `_rca` subject and Carry 1 now record #3263's at-once red as a second defect that #3276 (812bb8747) fixed. They name its cause: `prelude.judging()` read a deferring edit run's skipped `pr-contract` caller as owed, and the at-once bound in gate.py dodged the wait cycle that this created. The record also gives a process state, (c), with the reasons for not (a), (b) or (d). It gives a cost: 3 such reds in the 65 minutes after #3246 merged, which the census below re-derives. It names the countermeasure #3276 landed, plus this PR's replay scoring. This matches main's `gate.py` DEFERRAL docstring as quoted in round 1.
- Round-1 instrument finding fixed. `DEFECTS` now includes `C3-AT-ONCE`, so `replay --ci` at 294a880d exits rc 1. The arm's remaining blindness is stated in its docstring: the single-gate scenes cannot show the wait cycle.
- Round-1 figures finding fixed. The recurrence rule now pins `T00:00:00Z`. At b4ec2f332 I get 30 and 15, and 4 merges to gate.py/prelude.py (#3276, #3246, #3230, #3205), which match the body exactly.
- Stale-pin half: unchanged and re-derived (pins 9/6, DEADLOCK at the three pinned bases, census).

## Findings

- Follow-up: the body's `## Red checks` was read at 510b2a108. At 71710c56, all 94 check runs (`filter=all`) contain three concluded reds the body does not name by job: `tests / nightly-status` failure (job 128458402762, run 42390094094), edit-run `gate` failure (job 128462816817, run 42390096058, KIND edit, "FAIL run(s) [42390094094] at this head are still being judged; their gate decides" after the 12-minute bound), and edit-run `gate` cancelled (job 128462907528, run 42391320858). These reds concluded at 16:31Z and 16:54Z, after the body was last set (updated_at 16:26:39Z). Each one is a class the body already answers. nightly-status is not this PR's red: the diff does not reach what it reads. The gate red is the edit-gate deferral the brief exempts. It cleared once code run 42390094094's gate passed (job 128473148504, 17:22:09Z), and the re-run gates passed afterwards (job 128471278610 success; classify GREEN at 17:24:10Z). This does not block the merge. When the body is next set, it should list these three jobs at this head. Claim: `## Red checks` is one head stale. Evidence: the check-runs API at 71710c56, and the job log of 128462816817. Harness: `merge_train.py classify`. Metric: the red job ids at the head. Perturbation: none applies, since this is a record item. Carry: R10-RCA-GATE-BUSY-DEFER-2

## Evidence

- RESULT replay (head harness, `--ci <git archive sha tools/ci tools/pr>/tools/ci`; ev/replay_*.txt):
  - 28482ece, f2a01514, 80016a71: rc 1, DEADLOCK on all 3 pairs and C3-AT-ONCE naps 0 on all 3 C3 scenes.
  - 294a880d: rc 1, pairs DECIDED (3261: PASS naps 0 and PASS naps 1) and C3-AT-ONCE naps 0.
  - 812bb8747 and 71710c56: rc 0, pairs DECIDED naps 0/0 and C3 DEFERRED naps 12.
  - All of this matches the RCA table and the body's mutation proof.
- Round-1 mutants re-run at this head, each beside the unmutated relocated copy as null (ev/mutants.txt, ev/mutants/):
  - Mutant A (DEADLOCK dropped from DEFECTS), on a fixture copy holding only the pair scenes, at 28482ece: rc 0 (killed). The null on the same copy gives rc 1. On the full fixture the same mutant stays at rc 1 at 28482ece, because the C3 scenes also count there. The scene lines still show DEADLOCK.
  - Mutant B (the 3261-pair second gate's start moved to 06:00Z): refused with "gate 42307798573 had not started by 42307493684's read", rc 1. The arm does not go green.
  - The body's scoring mutant (DEFECTS = DEADLOCK, HALF-DEFERRED) at 294a880d: rc 0. The null gives rc 1, so the mutant is killed.
  - My own extra mutant (the naps==0 test in the C3-AT-ONCE branch broken) at 294a880d: rc 0. The null gives rc 1, so it is killed.
  - M17 and M24 of gate.py were not re-run. The body discloses M17 as surviving the arm and pinned by `gate.py --self-test`, and M24's code was deleted by #3276.
- pins: `RESULT pins gates=9 stale=6` (ev/pins.txt). Fixture sha1 f926d6a67b5582c172f49cb436a09e7ff7b63b70 (ev/fixture_sha1.txt).
- census (`census --since 2026-11-07T03:45:14Z --until 2026-11-07T04:50:21Z`), re-derived this time (round 1 could not):
  - stale: gates=46 {'defer': 21, 'other-red': 1, 'pass': 24}, 7 PRs, reruns=36.
  - fixed: gates=3 {'defer': 3} on #3241, #3261, #3263.
  - unpinned: gates=5.
  - All rows match the body (ev/census.txt).
- recurrence at b4ec2f332: 30 and 15; gate.py/prelude.py: 4 merges (ev/recurrence.txt).
- fold_ledger: 0 violation(s), 137 rca entries. `PYTHONPATH=tests/hastub python3 tests/entities.py`: ALL 2645 ENTITY CHECKS PASSED. structure: STRUCTURE RATCHET PASSED. `closure.py select`: MODE: SCOPED -- 1 script(s) run, 32 scoped out. All match the body.
- Classification: the new harness .py is in tests/closures.json INERT. entities passes with the fixture .json and the RCA .md added. No `*_budgets.json`, VERSION, manifest or RELEASE_NOTES.md is touched. The delivery row dev/programme/delivery/3278.md is in the diff. The roles diff against origin/main is empty.
- `git merge-tree --write-tree origin/main(4b5d771bd) 71710c56`: rc 0, tree def4a128f8c9d9d2f1fa88e733d5caf078ce4ce3. main's b4ec2f332..4b5d771bd (#3286, #3272) touches none of tools/ci, tools/pr, ci.yml, bugclasses.json or closures.json.
- The diff from d5c4a06b to 71710c56 within the PR's own files is the harness (DEFECTS, docstring), the RCA re-cut, the `_rca` entry, and closures INERT lines brought in by main's merge (#3285 and r10_sav_receipt_render). b38e5c08 is the only authored commit.
- `## Head` names 71710c56 and explains b38e5c08 and 510b2a108, so it is current. The branch tip was re-read before return: 71710c566283e302de7db598c8a6fc3045a41dbf.
- CI: `merge_train.py classify 71710c56 --pr 3278` went WAIT, then RED at 16:55:35Z (edit-gate deferral, exempt by the brief), then WAIT, then `GREEN 71710c566283e302de7db598c8a6fc3045a41dbf pending: none red: none` at 17:24:10Z (ev/classify.log).
- Packet: carry_audit at the head shows 4 routed and 0 unrouted. figure_lint shows 13 resolved, 3 not verified (git flag lists), 0 refused (ev/review-packet.md).
- The merge commit 71710c56 is authored `tvofi`. The PR author is hpo-author[bot], which pr-contract checks. Noted, not judged.
