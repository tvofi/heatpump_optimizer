Fix review: blocked 00f1d0ecafd8a38c0786f20a7093ee20518cf486 harness: replay.py exits 1 at the head, step 1 grades 21.967 not 36.5 because the merged hotfix #3180 replaced the critical_path_minutes it imports

bus-nonce: e9467047fb5a2f2fce579a9de6f717a1

## Block

This is the first round. The head measured is `00f1d0ecafd8a38c0786f20a7093ee20518cf486`, and the PR body names it.

The record's evidence is its replay (root-cause.md: the replay reproduces its figures). At the head, that replay no longer reproduces the grade.

- At the authored head `9f959dd9c`: `1. reproduce: window at 8f286293b grades 36.5 ... GREW` and `RESULT: holds`, exit 0 (ev/replay-authored-9f959dd9.txt).
- At the PR head `00f1d0eca`, after merge `f70e23933` brought in `#3180` (R10-HOTFIX-CI-CRITPATH-3, commits 27d410595, e1637032a, 543fa4f7a): `1. reproduce: window at 8f286293b grades 21.967 ... ok` and `RESULT: does NOT hold [False, True, True]`, exit 1 (ev/replay-head.txt).

The cause: `replay.py` step 1 calls the **live** `tests/ci_ratchet.critical_path_minutes`. #3180 redefined that function as `window_work_minutes` (16 runs, each job priced at its fastest run). So the replay now grades the red window with the new statistic. The PR body's Figures line ("prints the grade reproduction (36.5 against 35.567)") is false at the head it names. Its claim that "the record's conclusions are not changed by the merge" was not checked against its own harness.

The repair is cheap, and I verified it. Load `tests/ci_ratchet.py` as of `8f286293b` (`git show 8f286293b:tests/ci_ratchet.py`, imported by spec) and grade the same window. That gives 36.5 at this head (ev/step1-with-red-sha-ratchet.txt). Pinning step 1 to the ratchet the red commit ran makes the reproduction independent of later main.

## Findings

- The record is stale against #3180 in substance, not only in the "open" cell of its table. Section 1 says each hotfix "left the gate grading elapsed time on hosts the repository does not choose". Section 4 proposes grading the planned path because the timed gate is host-sensitive. But #3180 landed a host-draw countermeasure aimed at the same cause: each job is priced at its fastest run over 16 runs, re-recorded at 21.983. The record must say how its countermeasure 1 relates to the one that landed: superseded, complementary (e.g. a PR-time detector, or what remains when all 16 runs draw slow), or refused. Otherwise the owner is asked to decide a draft against a gate that no longer exists in that form. The process-state and cost-test numbers (P = 0.36/day, mean red ≥ 26.5 h) are unaffected. Carry: R10-RCA-CI-CRITPATH-3 | dismissed: repair within this PR, same group, on re-review
- Two line citations went stale after the merge. `tests/ci_ratchet.py:46-51` and `:106-112` no longer hold the calibration rule at the head: 106-112 are imports and `ROOT`/`BUDGETS` (ev/citations-at-head.txt). Cite them at a pinned SHA (the red commit's tree). Carry: R10-RCA-CI-CRITPATH-3 | dismissed: repair within this PR, same group, on re-review
- The run count is misstated. The record says `runs.json` holds "29 completed `ci.yml` push runs on `main`, 3770..4056". The file holds 31 completed runs, numbered 3775..4056. 29 is the count `run_minutes` grades (2 return None) (ev/job-figures.txt). The cost test's "286 run numbers between 3770 and 4056" inherits the 3770. The change is immaterial to the result (281 vs 286), but the figure is not what the fixture says. Carry: R10-RCA-CI-CRITPATH-3 | dismissed: repair within this PR, same group, on re-review
- Step 3's null control does not test what the record says it shows. "The same tree twice" calls a pure function on identical input twice, so it cannot fail and controls nothing about hosts. Host invariance rests instead on the CI-printed lane totals (jobs 125121503116 and 125653313138), which the fixture does not hold (its jobs carry no ids or logs). So the replay cannot reproduce that claim. Either state the null as a determinism check only, or commit the two lane-plan log lines as the host-invariance evidence. Carry: R10-RCA-CI-CRITPATH-3 | dismissed: repair within this PR, same group, on re-review

## Evidence

- RESULT replay@00f1d0eca: exit 1, `[False, True, True]`. Step 1 gives 21.967 ok. Step 2: 3 windows under half slow with max median 33.767, and 6 windows over 70 % slow with min median 39.667, which matches the record. Step 3: 1345.7 -> null 1345.7 -> +300 s 1445.7, which matches. Runtime 0.58 s wall.
- RESULT replay@9f959dd9c (authored head): exit 0, 36.5 GREW, holds.
- RESULT step 1 with the ratchet as of 8f286293b, at the head tree: 36.5.
- Re-derived from runs.json: closures lane 18.6–29.3 / 33.7–40.0 min, matching the record. From run 3865: 13 of 19 slow vs 5 of 12 before, matching.
- Not re-derived: "a 37.4-min run (job 125121503116, run 3870)" and "a 20.0-min run (job 125653313138, run 4055)". In the fixture, run 3870's closures job is 38.2 min and run 4055's is 20.6 min. `run_minutes` (authored-head ratchet) gives 39.667 and 33.5. None of these is 37.4/20.0, and the fixture has no job ids. The summed script times 97.7 / 52.7 (ratio 1.85) and the per-script figures come from job logs not in the tree. I could not re-derive them.
- Not re-derived: 108 dispatch commits, 32 roster_edit commits, 19 merges onto red main, 106 state-doc regenerations, and the phase intervals in section 5. These are git-history counts, and the body names no rule that would let me re-run them.
- Citations still valid at the head: `nudge.md:105` (expedite rule), `tests.yml:2265-2267` (push-to-main only), `orchestrator_tick.py:381` and `:1393`.
- Mutation proof: n/a. No production line changed. The replay's step-3 perturbation (+300 s on stress.py) moves the planned path, which I confirmed.
- Merge with origin/main: `git merge-tree --write-tree origin/main 00f1d0eca` exits 0 with no conflict (ev/merge-tree.txt).
- VERSION, manifest and notes heading: untouched. The diff is 4 files under dev/ only.
- Class rule: the record names its enumeration ("the only timing row in any `*_budgets.json`"). `tests/ci_budgets.json` at the head still has exactly one timing row, `critical_path_minutes` (now 21.983).
- Forward-carry: the body says none, and the countermeasures are drafts for the owner. Whether the owner draft must now be re-cut against #3180 is the first finding above.
- CI on this head: `merge_train.py classify` was still `WAIT 00f1d0ecafd8a38c0786f20a7093ee20518cf486 pending: gate red: none` (rc 3) at 12:46 UTC (ev/classify.txt). The only check run on the head is `arm` (126523483136, skipped, 10:34). No gate workflow has started in over 2 h, probably because it is a held or draft run. I returned without waiting for a terminal state because this block does not depend on CI. The re-review owes a terminal classify on the repaired head.
- Fixer.md step 14 / metric movement: the diff moves no budget, closure, claim or golden file.
