Fix review: merge e3622cb3d8c4f718370cc687ea1087d09da0da82

bus-nonce: 39a8735eddbccf8506da451262fc7934
pending-ci: gate

## Round

Fifth review of #3499 and the first of the re-cut (fixer.md: four blocked rounds 1aec0e57, 44e0b74b, ba5d3b25, 3785b0d0). The re-cut was reviewed as a whole against R10-GATE-DEFER-BARRIER carries 0-4, not as a delta. Head measured: e3622cb3d8c4f718370cc687ea1087d09da0da82, which is the authored handoff df4af48ad90561c6259435441507f1451cad3913 merged into the PR branch. The body's `## Head` names both. The second parent's diff to the head is main's content, already merged at 9e12d95124.

## Verdict basis

- The class the last verdict called open (`class-open`: reader spellings the per-call AST scan missed) is closed at every seam the body's enumeration returns. `classify` now checks its caller at run time. Neither my plants nor the fixer's could reach a final read through alias, rebinding, getattr, partial, a `*self_test*` name, an outside module, no busy, `()`, `None` or a minted `FinalRead()`. The rule returns the 5 `FINAL_READERS` frames, and each is in the diff.
- Direct gate-conclusion reads that bypass `classify` are scoped out honestly. The carry exists on origin/handoff/audit-r10-roster at 9e7bdd2d42e4cabe1b6ddb1bb095a28a60359625, `wave-r10-groups.json`, R10-CI-PRIORITY-PAUSE carry index 11 ("From r10-gate-defer-barrier, body item 6e06de7f"). It states its control as a precondition: plant both shapes, both read red now, and a fix must turn each into a refusal.
- `## Red checks` answers the owed reds with established causes for the two I spot-checked (below). For the other two it records that no cause is claimed, and it establishes that the failing commit is not on this branch. That answers the trigger. Per fix-review.md step 11, I check that the trigger was answered, not the answer itself.
- No defect found warrants a fifth block. The survivors below are a narrow gap in the empty-`Busy` predicate, in the same domain as the body's carried residual, and they are carried to the same group.

## Findings

- Three of my eight reviewer plants against the barrier get past it and read a red `gate` as final from an unregistered frame (`ev/reviewer-plants.txt`). The cause is that `Busy.__init__` checks emptiness only when the object is built, and `classify` trusts `isinstance(busy, Busy)` when it reads. The three are (1) `b = Busy(["x"]); b.clear()`, an in-place mutation of a non-empty Busy minted anywhere, (2) `copy.copy(gate_busy([], []))`, and (3) `Busy.__new__(Busy)`. Case (2) is within the body's disclosed residual ("an empty Busy that a real minter built from made-up runs"). Cases (1) and (3) are not, and they contradict the body's sentence that only `BUSY_MINTERS` "may create" an empty one. I judge them non-blocking. (3) is deliberate circumvention. (1) is in the same predicate domain as the carried residual: the barrier checks that a reading was stated, not that the value read is still the minted reading. A candidate fix is to make `Busy` immutable (a tuple subclass) or to record the mint on the instance and check it in `classify`. Re-measure: run the three plants from `ev/reviewer-plants.txt`. Each must raise `BlindRead`. Carry: R10-CI-PRIORITY-PAUSE
- Six diff-mutant survivors from the body's `prepr.sh` draw are on lines this pass did not change (`git diff 3785b0d0 df4af48a` touches none of them). They are an equivalent settle constant, `sib` read for truthiness, the self-test call that `MUTANT_CMD` cannot see, and three fixture constants. I accept the body's disposition. Carry: dismissed: equivalent mutants and self-test fixture constants on lines this pass did not change

## Evidence

- HEAD: `ev/HEAD.txt`, e3622cb3d8c4f718370cc687ea1087d09da0da82. Merge base with origin/main is f44e761c19dc07fff222bbd6a323bdc847ea9f04.
- `git merge-tree --write-tree origin/main e3622cb3`: rc=0, so it merges cleanly (`ev/merge-tree.txt`).
- Mutation proof, the fixer's mutant harness re-run by me: `RESULT mutants=6 survived=0 stale=0 baseline_failed=0`, rc 0 at the head (`ev/mutants-head.txt`). With `--plants-only` at an export of 3785b0d097bc22410f42eae7ba3129c5fece1c61: `RESULT plants=6 survived=6`, rc 1 (`ev/mutants-3785b0d.txt`). The last verdict's finding reproduces before the fix and is closed after it.
- Reviewer mutant, which deletes the `raise BlindRead` branch of `classify` (`deferred = set()`): `merge_train.py --self-test` FAILs three checks, the 9x4 plant check (the direct call passes), "barrier null" and "refusal names the caller's frame" (`ev/reviewer-mutant-blindread-deleted.txt`).
- Reviewer mutant, which deletes `Busy.__init__`'s minter check: the 9x4 plant check FAILs on "busy rebound to an empty Busy" (`ev/reviewer-mutant-minter-deleted.txt`). The tree was restored afterwards and `git status` is clean.
- Finder harness `dev/audit/harnesses/r10_gate_defer_barrier.py` at the head: no DEFECT, rc 0, with `under_started=[]` and `under_queued_null=['TIMEOUT']` (`ev/finder-head.txt`). At an export of merge base f44e761c19: `DEFECT policy`, `DEFECT under`, rc 1 (`ev/finder-base.txt`). The null arms hold at both ends (`policy_null_ok=True`, `under_queued_null=['TIMEOUT']`). The harness is committed in the diff, and it is the fixer's: per fix-review.md step 9, the group's finder harness did not exist before this PR.
- Self-tests at the head (`ev/selftests.txt`): merge_train 679/0 failed, orchestrator_tick 317/0, merge_pr.sh 26/0. These match the body's figures. `tests/structure.py`: STRUCTURE RATCHET PASSED. `env_drift.py --claims-only origin/main`: ok.
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`: ALL 2709 ENTITY CHECKS PASSED, rc 0 (`ev/entities.txt`).
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched in the three-dot diff (`ev/version-check.txt`). No golden fixture or claim file is in the diff. No `*_budgets.json` is touched.
- Class enumeration: `classify(` call sites outside self-tests are `approval_owed`, `Train.classify_at` (FINAL then Busy), `Train.wait_ci` (FINAL then Busy), `Train.main_green`, `Tick._classify_reading`'s nested run (`mt.FINAL`), and `r10_rca_gate_busy_defer_4.py`'s guarded reads. FINAL is passed only from the five registered frames.
- Direct gate-conclusion readers (the carried residual) were located across tools/. These delegate the red decision to classify: the tick's NOT REVIEWABLE line (`orchestrator_tick.py:1258`, via `_classify_reading`), `ci-watch.sh`'s `gate_deferred`, `review_packet.py`'s `required_reading`, `bus.sh`, and `merge_pr.sh` (classify CLI at :320). These read the raw conclusion and are main-, settle- or metric-side: `tools/release/stamp.py` `gate_verdict`, `tools/ci/ruleset_cutover.py`, `tools/ci/sweep.py` (the settler itself), `scorecard.py`. All of them fall inside the body's carried category.
- Red-check spot-check, 2 GitHub API reads. Job 131159081242 is `tests / fast (3.14)`, failure at the step "Run the suite", head_sha 112f0d777b8f, branch fix/r10-duty-switch-restart-learning, run named "CI code pr=3461". Job 131175916370 is `tests / coverage-ratchet`, failure at the step "Ratchet the floor and the pragma count with the base's grader", same head and run. Both match the body. 112f0d777b and 6b16a9f896 are ancestors of origin/main.
- Figures I could not re-derive. The body twice names the merge base as 8c10361eb1. At this head `git merge-base origin/main HEAD` is f44e761c19, and both are ancestors of the head. The body's "213 commits" in 8c10361eb1..9e12d95124: `git rev-list --count` gives 247 (all commits, branch included). The body's split was not re-derived. I re-ran the finder harness at f44e761c19 instead of 8c10361eb1. It reads DEFECT there too, so the conclusion holds.
- Archscore `dS +0.0081 IMPROVES` is cited from the body (figure_lint resolved), not re-run.
- CI at the head: `merge_train.py classify e3622cb3 --pr 3499` polled about every 60 s from 03:52Z to 04:17Z, then checked again at 04:20Z. Every poll returned rc 3: `WAIT e3622cb3d8c4f718370cc687ea1087d09da0da82 pending: gate red: none` (`ev/classify.txt`, `ev/classify-polls.txt`). No red at the head. The relay posts this once CI is green at this head. `refs/pull/3499/head` is still e3622cb3d8c4f718370cc687ea1087d09da0da82 at return.

## Friction

none
