Fix review: merge 56dd13aa8b3fea657ade16ec6d7b0956493af3c8

bus-nonce: 7fa7e2af1039a2d73875b517a50f6d91

Resolution-delta round. The previous verdict, verdict/3264, was `Fix review: merge 0542969c`. This round measured head 56dd13aa8b3fea657ade16ec6d7b0956493af3c8 from detached worktrees. Its merge base with origin/main is 17e1157925908bd69addb58ed824c1ac22bfa82f, which is origin/main itself, so the head already contains main.

## Findings

- The brief's precondition does not hold, and I reviewed the extra commits instead of returning unverdicted. `git log 0542969c..56dd13aa --not origin/main` holds more than the merge (ev/range-not-main.txt). It holds the conflict merge d84006e66 and two later merges of main (9391c0d5a, 56dd13aa8). It also holds three authored commits that land carry 16 / roster index 15: 83b3e0b00 (the failing test), e08021412 (the fix) and 55b86a71e (the pins). The PR body declares all three. No earlier review covered them. I reviewed them in full, which keeps coverage, so the verdict covers the resolution and carry 16. Carry: dismissed: process observation about the dispatch; this verdict covers the whole delta
- Surviving mutant on a production line of carry 16: the legacy read in `main()` is unpinned. Carry 16 requires `roster_lib.read_legacy` for the roster's cut-over. Claim: the body says "no production site of this round is unpinned", and that is false.
  - Evidence: two mutants of tools/plan/replan.py both survive `--self-test` (ev/my16.out). main-legacy-none changes `legacy=legacy)` to `legacy=None)` in `main`'s `build_plan` call. main-legacy-path passes `src` in place of `ROSTERS_DIR/<basename>`.
  - Harness and perturbation: the real CLI on roster blob df4c1694 with `--start 2026-11-07T22:00:00`, with main-legacy-none applied. R10-SAV-COMFORT moves from 1188 to 2376 min, because 5 legacy carries are priced as open again. Closure moves from 2026-11-14T00:51Z to 01:11Z (ev/figures-rederived.txt).
  - Metric: the head's figures are correct. The pin is missing, so a regression in the wiring would pass the self-test.
  - mutant_run.py generated no mutant on these lines, so the body's diff-mutant figure could not see them.
  - Fix: one self-test arm that drives `main` (or a helper it calls) with a `--roster-file` copy named wave-r10-groups.json, and asserts that a legacy carry is left out.
  - Carry: R10-FLOW-TOOLKIT-MODEL
- One phrase in the body is wrong; its total is right. `## Figures` says PREPR-CAP, ROSTER-WRITE-SWEEP, SAV-COMFORT and TICK-LEVELS drop "to 0". Re-derived, they go 3564->2376, 2376->1188, 2376->1188 and 2376->1188. Only TRAIN-MERGE-LOOP goes to 0 (2376->0). The summed 14464 is exact (ev/figures-rederived.txt). Carry: dismissed: body prose with no code consequence; the correct per-group figures are recorded here
- Roster carries 13 and 14 (0-based) of R10-FLOW-TOOLKIT-MODEL stay open: the closure rule and the disposition stages. The body says they are outside this repair's brief and "open on the roster as it stands". This PR does not settle them. They remain on this group, which stays open after the merge. Carry: R10-FLOW-TOOLKIT-MODEL

## Evidence

- RESULT merge-tree: `git merge-tree --write-tree origin/main 56dd13aa` exits 0 with tree 9c11f07496a5 and no conflict (ev/merge-tree.txt). origin/main 17e1157925 is an ancestor of the head.
- RESULT both sides survive in tools/plan/replan.py:
  - d84006e66's combined diff keeps this PR's `absorbers` and `post_closure_groups`, and main's `_owned_lane`, `_NON_PRODUCT_PREFIXES` and `INSTRUMENT_KINDS` (#3265: bdae685fb, 91ed006ba, aa5c0505b).
  - At the head, `--self-test` passes main's lane arms: 22 `lane:` and `lane null control:` checks, all ok.
  - It also passes this PR's carry-16 arms, the cadence and evidence arms, and `model self-test: 0 failed`, `null control: unmutated copy rc=0` and `self-test: 0 failed`. 61 in-table mutants report rc=1 (ev/replan-selftest.txt, wall 52 s).
- RESULT carry 16 is correct on real data. Roster blob df4c1694f8b7 was run with `--start 2026-11-07T22:00:00` on d84006e66 (before) and on the head (after), each from its own clean worktree (ev/replan-before.txt, ev/replan-after-clean.txt).
  - Before: `closure 2026-11-13T23:59:00Z | wall 145.98 h | CI 7537.5 min | batches 62`, binding chain R10-BODY-CONTRACT -> ARCH-DOCS -> CLOSEOUT-CLEANUP, critical path 133.72 h, slack 12.26 h.
  - After: `closure 2026-11-14T00:51:00Z | wall 146.85 h | CI 7312.5 min | batches 60`, binding chain R10-CLONE-2238 -> ARCH-DOCS -> CLOSEOUT-CLEANUP, critical path 112.6 h, slack 34.25 h.
  - Both match the body exactly. BODY-CONTRACT and HANDOFF-PATH each go 4752->1188, and 14464 seat-minutes in all are no longer priced.
- RESULT null control: the head on the same roster with all 661 carry marks stripped is identical to d84006e66 on the marked roster. No group differs in duration, start or finish, and the summary is equal. This re-derives the body's whole-roster control (ev/figures-rederived.txt).
- My first "after" runs were contaminated, and I discarded them. They ran in the worktree where round 1's mut.py was mutating replan.py at the same time, which gave CI 7537.5 / batches 62. They are kept in ev/contaminated/ only to disclose this. Every figure above comes from clean worktree wtc.
- RESULT mutation proof on carry 16. This is my own harness, disclosed as mine (ev/my16.py, ev/my16b.py).
  - Killed: pending-ignores-legacy, pending-all, left-count-zero, added-gt, then-le, then-max, then-no-pending, then-plus-added-dropped, added-unmarked-all, absorbed-left-out-dropped, held-left-out-dropped and build-legacy-none.
  - Survived: main-legacy-none and main-legacy-path (see `## Findings`).
  - The fixer's in-table mutants all report rc=1 in --self-test: held-open-pending, absorbed-pending, appended-carries-open, held-measured-pending, pending-left-out and legacy-threaded.
- RESULT the body's diff-mutant run, re-run by its own command over `d84006e66...55b86a71e --path tools/plan/replan.py`: 15 survivors, all at self-test fixture lines 661-697, which matches the body (ev/diff-mutants-carry16.txt). The total of 39 is not re-derived, because `--report-only` lists only survivors.
  - The same command over `d84006e66...HEAD` at 56dd13aa sweeps main's sweep_gantt.py, because that range now spans main's merges. That run is not this PR's figure.
- RESULT the finder's harness: there is no committed finder harness for this group. I re-ran the earlier reviewers' scripts from verdict/3264 unchanged, each in its own worktree at the head.
  - mut.py: 15 anchored mutants killed (credit-lane: ANCHOR 0, as in round 3) (ev/r1-mut.out).
  - m2.py: credit-lane-r2, credit-done-r2, squash-fallback-dropped, squash-longest, since-prod-lane and since-substantive are killed. merge-topic-lastseg, merge-topic-lower and merge-re-anchor survive. Round 2 judged those three equivalent, and that is unchanged (ev/r2-m2.out).
  - mutg.py: 4 of 4 gantt_drift mutants killed (ev/gantt-mut.out).
  - Every worktree was clean after its run.
- RESULT the other self-tests at the head (clean worktree):
  - gantt_drift.py --self-test: 45 checks, 0 failed.
  - plan_page.py --self-test: 67 checks, 0 failed.
  - tests/structure.py: STRUCTURE RATCHET PASSED.
- RESULT scope: the three-dot diff touches 9 files (ev/diff-files.txt). None is custom_components, VERSION, the manifest, RELEASE_NOTES.md or a *_budgets.json. dev/programme/delivery/3264.md is in the diff, and gantt_drift.py was classified in tests/closures.json in an earlier round. The structure_budgets.json change between 0542969c and the head is main's content, outside the three-dot diff. The review roles are unchanged between the merge base and main (an empty diff).
- RESULT `## Head` names 56dd13aa8b3f, the head I measured.
- RESULT checks: the head has 68 check runs, all on one page. Two `gate` runs concluded red:
  - 128581984342 (run 42428588462, ended 00:53:23Z) and 128581829645 (run 42429932725, ended 00:52:32Z).
  - Both logs read `FAIL run(s) [42428588857] at this head are still being judged; their gate decides`. Both are edit-run deferrals. That run's own `gate`, 128582492626, concluded success at 00:55:31Z.
  - `pr-contract / pr-contract` 128582253262 started at 00:53:50Z, after the last red concluded, and ended in success. Under fix-review.md step 11, that run is the evidence that the body check passed.
  - The body's `## Red checks` predates these deferrals. Its standing line already names gate-deferral reds as the instrument owned by R10-PROCESS-SLIM (#3245).
- CI: `merge_train.py classify 56dd13aa8b3fea657ade16ec6d7b0956493af3c8 --pr 3264` gave RED (gate) at 00:55:41Z, before the deferred gate concluded, then WAIT, then `GREEN 56dd13aa8b3fea657ade16ec6d7b0956493af3c8 pending: none red: none` with rc=0 (ev/classify-final.txt).
- Routing is unchanged since rounds 1 to 3: carries 1 and 7 (brief index) go to R10-BODY-CONTRACT, and 4, 5 and 6 are dismissed as duplicates. The resolution delta does not touch them.
