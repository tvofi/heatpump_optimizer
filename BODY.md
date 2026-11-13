R10-GATE-DEFER-BARRIER, part 1 of 2 (carries 0-4): every call of `merge_train.classify` must state how it read the deferral of a red `gate`, and the function checks that itself when it runs. Carries 5-10 are part 2 and are not answered here.

Carry map, unchanged since the last round except Carry 3's barrier:
- Carry 0: `dev/audit/rca/r10-gate-busy-defer-2.md` section 1 is marked superseded.
- Carry 1: `dev/audit/harnesses/r10_gate_defer_barrier.py`, the finder harness.
- Carry 2: class `N-provisional-gate-red-read-final`, recorded as barriered in `bugclasses.json`.
- Carry 3: the readers. The `orchestrator_tick` readers go through `classify_at`, `merge_pr.sh` waits out a classify WAIT, `nudge.md` step 15 reads through classify, and the barrier in `classify` itself is this pass's change.
- Carry 4: `policy_refusal` reads `gate` contexts with the same name together, and `wait_ci`'s wait is bounded by the deadline of a started run.
- Carry 5, Carry 6, Carry 7, Carry 8, Carry 9 and Carry 10 belong to part 2 and are not touched here. Carry 10's `tick_loop.sh` is not among this group's files, and no figure below was taken on a moved HEAD.

## Re-cut

Option taken: **route every read through one function, so no caller list exists**. This replaces the per-call AST scan, which earlier rounds kept patching one spelling at a time. `classify` now checks its own callers when it runs, using the value it is given and the frame that called it. A static scan cannot see that frame, but every alias, rebinding, `getattr`, `functools.partial`, `*self_test*` name and outside module still has one.

- `busy` is required, so a call that leaves it out raises `TypeError`. It must be one of two things. The first is a `Busy`, the list `gate_busy` / `gate_rerunning` / `Train._gate_busy` return. An empty `Busy` means the gate is not waiting on any run, so only those three run readers (`BUSY_MINTERS`) may create one. A non-empty one only ever turns a red into a wait, so any code may create it. The second is `FINAL`, a read that ignores deferral, accepted only from a frame in `FINAL_READERS`, keyed on (repo path, `co_qualname`). Anything else (`None`, `()`, a plain list, a missing `busy`, or `FINAL` from any other frame) raises `BlindRead`, a `TypeError`. A self-test function gets no exemption because of its name.
- The five reads that ignore deferral are the old `BLIND_CLASSIFY_READERS` rows, unchanged and now keyed by frame: `approval_owed`, the first read in `Train.classify_at` and in `Train.wait_ci`, `Train.main_green`, and `Tick._classify_reading`'s fallback. They pass `FINAL`, and the self-test lines and `r10_rca_gate_busy_defer_4.py`'s non-gate scene pass `gate_busy([], [])`.
- Deleted: `blind_classify_readers`, `busy_reads`, `_busy_candidates`, `BUSY_CORPUS`, the four-module scan and `import builtins`.
- Not chosen: deriving the reader set by resolving names across every tracked file. Static resolution cannot follow `getattr` with a computed name, a `partial` built from a variable, or code loaded with `exec`. That leaves the same enumeration race the last four verdicts blocked.

What the barrier does not prove (this is the narrowed claim, and `bugclasses.json`'s `barrier` text now says the same):
- A function that reads the conclusion of a `gate` check run directly, without calling `classify`, is not covered. `merge_pr.sh`'s raw read keeps its own ordering check. Perturbation: a function returning `latest[GATE]["conclusion"] == "failure"` reads red and nothing refuses. Carry: R10-CI-PRIORITY-PAUSE
- An empty `Busy` that a real minter built from made-up runs is accepted. Perturbation: `classify(l, r, gate_busy([], []))` from any frame reads a red `gate` as final. The barrier checks that a reading was stated, not that its inputs were the head's runs. Carry: R10-CI-PRIORITY-PAUSE
- The check runs when the call runs. A new reader that no test calls is refused the first time it runs, as a `BlindRead`, before it can return a verdict. It is not refused when the self-test runs. Carry: R10-CI-PRIORITY-PAUSE

Kept from the earlier rounds, unchanged in this pass: `policy_refusal` reads `gate` contexts with the same name together, `wait_ci`'s wait under a started run is bounded by its deadline, `merge_pr.sh` has its classify WAIT, the `orchestrator_tick` readers go through `classify_at`, and `bugclasses.json`, `finding.schema.json`, `nudge.md` step 15 and the finder harness are as before. A disclosed self-correction: the previous body said "every reader of the gate conclusion reads it through classify". That was never measured. The first bullet above replaces it.

## Head

df4af48ad90561c6259435441507f1451cad3913, four commits on 3785b0d097bc22410f42eae7ba3129c5fece1c61. Measured against origin/main f44e761c19dc07fff222bbd6a323bdc847ea9f04 at 2026-11-13T01:43:03Z. Commit 718cbfdf0e31e9707626797c2cc787aa08509877 is broken: a scripted revert rewrote four unrelated `return ""` lines, and its self-test crashes. The next commit restores them, and `git diff d8222749b883175e0255d9f703a927d0e18630b8 df4af48ad90561c6259435441507f1451cad3913` is the seven added lines of the repr check alone. No CI run at this head is claimed.

## Mutation proof

- `python3 -I dev/audit/harnesses/r10_gate_defer_barrier_mutants.py` (sha1 38d52c4cad9c8d8a6a417d5f004f9961d6b4135a) at this head. PLANT arm, one reader for each shape the fourth verdict named (import alias, rebinding, getattr, functools.partial, a function named `*self_test*`, a module outside the four): each is planted into a copy of the tree and run on a red `gate`. Result: `RESULT plants=6 survived=0`, every one refused with `BlindRead`. SOURCE arm, which changes the checks' conditions (FINAL from any frame, any value accepted, an empty Busy created anywhere, the frame read one level too shallow, frames keyed by basename, frames keyed by path only): `RESULT mutants=6 survived=0 stale=0 baseline_failed=0`, exit 0.
- Before the fix: the same harness with `--tree "$D" --plants-only`, where `$D` is `git archive 3785b0d097bc22410f42eae7ba3129c5fece1c61 tools/audit/seat tools/ci`, prints `RESULT plants=6 survived=6`. Every plant reads `red` and that tree's barrier self-test stays green. That is the verdict's finding, reproduced.
- Diff-mutant pass: `tools/pr/prepr.sh` at this head, with `MUTANT_IN_PLACE=1 MUTANT_CMD="env PYTHONPATH=tests/hastub python3 tools/audit/seat/merge_train.py --self-test"`, gave `PRE-PR: df4af48ad90561c6259435441507f1451cad3913 ... rc=0`. The draw is the first 40 mutants of the branch's added lines (`mutant_run.py --diff <merge-base>...HEAD`). It had 6 survivors:

```
SURVIVED tools/audit/seat/merge_train.py:2248 CONST_SWAP  while k < self.polls or (last_def and not deferring and k <= last_def + 3) or self._sibling_in_deadline(deferring):
SURVIVED tools/audit/seat/merge_train.py:2273 CONST_SWAP  sib = [r[1] for r in rows]
SURVIVED tools/audit/seat/merge_train.py:5982 CALL_DEL  pass
SURVIVED tools/audit/seat/merge_train.py:6779 CONST_SWAP  t = Train("o/r", Path(d), None, "", (), 2, run=run, sleep=lambda s: None, log=lambda s: None, polls=polls,
SURVIVED tools/audit/seat/merge_train.py:6792 CONST_SWAP  started = lambda st, ago: _jl([{"id": 42237558474, "status": st, "run_started_at": iso(ago)}])
SURVIVED tools/audit/seat/merge_train.py:6794 CONST_SWAP  [started("in_progress", 5001)] * 7 + [done], polls=3)
```

Disposition: this pass introduced two survivors, and both are now killed. The first was `FINAL`'s `__bool__`, which nothing read; it was deleted by turning `FINAL` into the plain `FinalRead` class. The second was `FinalRead.__repr__`'s return, now killed by the self-test check "a refusal names the caller's frame and the busy it was given": with the return deleted, the block raises `TypeError: __repr__ returned non-string`, measured on a tree copy. None of the six above is on a line this pass changed. `git diff 3785b0d097bc22410f42eae7ba3129c5fece1c61 df4af48ad90561c6259435441507f1451cad3913` touches none of them, so they are the same sites as the earlier rounds' list, at shifted line numbers:
  - The `last_def + 2` settle count, and `sib = [r[0] for r in rows]`, which is read only for truthiness and in a log line.
  - The `_gate_reader_barrier_self_test(check)` call in `_self_test`. Deleting it cannot fail the self-test that is also `MUTANT_CMD`. The harness above drives that block directly.
  - Three fixture constants in `_gate_race_self_test`.
Carry: dismissed: equivalent mutants and self-test fixture constants on lines this pass did not change

## Null control

- The positive side: a `FINAL` read from each of the five `FINAL_READERS` frames is accepted, and an empty `Busy` created by a `BUSY_MINTERS` frame reads final (self-test checks "P436 barrier null" and "an empty Busy is minted by a BUSY_MINTERS frame"). Without this, a barrier that refused every call would pass all the refusal checks. The source mutant "frame read one level too shallow" is caught only by this check.
- Each part of the key is checked separately. A registered qualname in `proof_watch.py`, a registered path with an unregistered qualname (`Tick._classify_reading` in `merge_train.py`), and a registered basename in another directory (`dev/audit/harnesses/merge_train.py`) are each refused. The "keyed by basename" source mutant survived until the last of these was added.
- Finder harness `dev/audit/harnesses/r10_gate_defer_barrier.py` (sha1 d47dcf2083e9c02abae85ec6c08a5cc9a11c28f7): at an export of the merge base 8c10361eb1fea539dc5acb8f7442eac2810faa47 it prints `DEFECT policy` and `DEFECT under` and exits 1. At this head it prints no `DEFECT` and exits 0.

## Figures

- Rule that enumerates the reader seams: every frame that calls `classify` and returns a verdict on a red `gate` without deferral. That set equals the `FINAL_READERS` keys, because any other frame raises. The planted set is `PLANTED_READERS`: 9 spellings (the six from the verdict, plus no busy, a literal `()`, and an empty `Busy` bound to a name), each planted into 4 modules (`merge_train.py`, `orchestrator_tick.py`, a planted module under the integration directory, a path outside the tree), 36 reads in all. Self-test "P436 barrier: each of the 9 planted deferral-blind readers, planted in each of 4 modules, refuses a red gate": `passed: []`. Seams and what happens to each: the six spellings from the verdict and the three value spellings are closed in this diff. A conclusion read that bypasses `classify` and an empty `Busy` built from made-up runs are the narrowed residuals under `## Re-cut`. Both are carried.
- `python3 tools/audit/seat/merge_train.py --self-test`: 679 checks, 0 failed. `orchestrator_tick.py --self-test`: 317, 0 failed. `proof_watch.py --self-test`: 47, 0 failed. `review_packet.py --self-test`: 123, 0 failed. `bash tools/audit/seat/merge_pr.sh --self-test`: 26, 0 failed.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 2 script(s) run`. `tests/doc_claims.py`: ALL 343 checks PASSED. `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`: ALL 2709 ENTITY CHECKS PASSED. Of `run_always`: `tests/env_drift.py --claims-only origin/main` printed claims hygiene ok, `tests/closure.py selftest` printed ALL 118 closure shrink pins PASSED, `tests/layout.py` printed ok, and `tests/harness_headers.py` printed ALL 115 HARNESS HEADER CHECKS PASSED. `tests/stress.py` and everything else is left to CI.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, no budget touched. `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0081 IMPROVES`, over the whole branch.

## Red checks

No CI run exists at this head yet. Every failed job of the six failed `CI code` runs on `fix/r10-gate-defer-barrier` (PR heads 1aec0e574b, 44e0b74b55 twice, ba5d3b2527, 27f37247b9, 9e12d95124) was read, across all attempts. None is one of the four owed reds below; at those heads the owed reds were `arch-score / arch-score`, `pr-contract / pr-contract` and `gate` at 44e0b74b55, answered in the earlier rounds' bodies. The four below come from the ancestry the body check reads. Its base is the merge base of origin/main and this head, 8c10361eb1. The pull request's head 9e12d95124 merged origin/main f44e761c19 at dfa5bbf6e2, so the range 8c10361eb1..9e12d95124 holds 213 commits of main and of other pull requests that were merged into it. The four reds stand on those commits, and none was reached by a commit of this branch. Reds outside `merge_train.py owed-reds` (`tests / nightly-status`, `governance / instrument-self-tests` and the rest of the listed names) are not owed and not answered here.
- `tests / fast (3.14)`: the "Run the suite" step failed at 112f0d777b (#3461's head, job 131159081242 of run 43210133740) and at 6b16a9f896 (#3518's head, job 131425968347 of run 43287618955). Neither commit is this branch's; each is answered on its own pull request, both merged before f44e761c19. Cheaper detector: none is owed here, because this branch did not turn the check red. The trigger in `defect-root-cause.md` belongs to the pull request that did.
- `tests / coverage-ratchet`: the step "Ratchet the floor and the pragma count with the base's grader" failed at 112f0d777b (#3461's head, job 131175916370 of run 43210133740). That is not this branch's commit. Cheaper detector: none is owed here, for the same reason.
- `governance / wave-script`: the failing commit was not identified within this seat's read budget. Established: it is not on any `fix/r10-gate-defer-barrier` run, read as above, and not on main's f44e761c19 push run 43325003990, whose only failed job is `governance / instrument-self-tests`. So it stands on another pull request's commit inside 8c10361eb1..f44e761c19. Cheaper detector: none is owed here, because this branch did not turn the check red. No cause is claimed.
- `tests / mutation`: the same as `governance / wave-script`. The failing commit was not identified within the read budget. It is not on any of this branch's runs or on main's f44e761c19 push run, and at #3461's 2e1e33a70a all four `tests / mutation` runs concluded success. Cheaper detector: none is owed here, because this branch did not turn the check red. No cause is claimed.

## Forward-carry

- The three residuals under `## Re-cut` (a gate-conclusion read that bypasses `classify`, an empty `Busy` built from made-up runs, and refusal only at run time) go to R10-CI-PRIORITY-PAUSE, the one live group that edits the train's gate-conclusion readers (`merge_train.py`, `orchestrator_tick.py`) and that is receivable on both main's roster, which pr-contract reads, and the round roster. R10-NUDGE-RETIRE also touches `merge_pr.sh`, but it exists only on the round roster, so pr-contract cannot resolve it. Re-measure: plant `latest[GATE]["conclusion"] == "failure"` and `classify(l, r, gate_busy([], []))` in a new function. Both read red at this head, and a fix must turn each into a refusal. Carry: R10-CI-PRIORITY-PAUSE
- Section 5.2 of `dev/audit/rca/r10-gate-busy-defer-2.md` (a fresh dispatch where a re-run would replay a stale pinned program) is still needed under the at-once program. Re-measure it with that document's `census` arm after #3473 lands. Carry: dismissed: the seam is #3473 (R10-HOTFIX-GATE-REDISPATCH-LOOP), whose roster row is carries-open and not receivable; the relay folds this instruction when #3473 lands

## Friction

none

## Approval

Policy file changed: `dev/governance/roles/nudge.md` step 15 (unchanged in this pass). This seat holds no approval and claims none. Merge waits on `@tvofi`'s approving review of the head, per `CLAUDE.md`.
