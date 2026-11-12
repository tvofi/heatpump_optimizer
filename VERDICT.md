Fix review: merge a98c71de318ebdd7ba7eb6e5219866436152035c

bus-nonce: 3b24196c224ac55f638d848d0666ee7c

## Round

This is a later round over the reviewed head d0c9eb66497bfd1cb2931bae2c7bddcfa3271e71. It is round 2 for this diff (carry 1, P447, STAMP-HOLD). Counting the first part's two blocks, it is the fourth review on the topic, and the body opens with the `## Re-cut` that `fixer.md` owes from the fourth round. Scope (fix-review.md step 12): the delta `git diff d0c9eb66 a98c71de` and each of the previous verdict's (b9137b16, `blocked d0c9eb66 hold-unrefreshed`) block items. The delta's non-merge commits are e5b862ba and 1012ff44 (both tools/audit/seat/merge_train.py; 1012ff44 also re-recorded tests/closures.json), the merge 70ecfa6a of origin/main 43e95474 (it takes tests/closures.json from main), and a98c71de (dev/programme/carries/carry-201.json). The delta touches no `custom_components/` code, so the scope is not widened.

## Prior block items

- **The train-hold refresh in the stamp-hold wait is cleared.** `Train.stamp_hold_wait` now calls `self.hold_refresh()` before each `self.sleep(STAMP_HOLD_POLL_S)`. That matches HOLD_REF's "refreshed before every sleep" contract, so a wait of up to 7200 s no longer lets the train-hold age past the record beat's 3600 s. A new self-test case arms `hold_armed` and counts the refreshes against the polls (3 == 3). Its mutant K (refresh -> `pass`) is KILLED.
- **The fail-open read of a future-dated hold is cleared.** `stamp_hold_age` now returns a negative age as is. The wait reads that age as live and bounds it with `max(age, waited)`, where `waited` counts poll seconds, so a hold dated ahead of this clock still reaches the take-over at 7200 s. Two self-test cases pin this: a future-dated hold that clears, and one that never clears and is taken over after exactly STAMP_HOLD_MAX_AGE_S // STAMP_HOLD_POLL_S polls. The unreadable-date branch (no wait) has its own case. The body states the decision. Mutant E (fail open again) is KILLED, and so are R, L, M, T and my own U (see Evidence).
- **The body is cleared.** It is now this diff's body. It names carry 1 as built here, and its `## Mutation proof`, `## Null control` and `## Figures` cover `stamp_hold_wait`/`stamp_hold_age`. Its self-test figure (669) matches this head. It also discloses that the earlier bodies numbered the carries wrongly: the first part's carries are 16/17, not 17/18.
- **The prior survivors of rollup_states/record_drafts are cleared.** X14, X16 and X17 are now KILLED, each by its new named check. X10 (`(stamp, i) >= best[name][0]` -> `>`) still survives, but it is an equivalent mutant: `i` is the `enumerate` index, so it is unique, and a `(stamp, i)` key can never equal an earlier one. `>=` and `>` therefore decide every comparison the same way. The new "equal stamp ... in both list orders" check pins the behaviour that X10 was raised about. I do not count it.

## Findings

- Residual: the mutant V (move `self.hold_refresh()` from before the sleep to after it) survives the self-test, because the test counts refreshes per poll and does not check their order against the sleeps. It is equivalent in practice. With STAMP_HOLD_POLL_S = 30, either order keeps the train-hold age within one poll interval plus the previous phase, far below HOLD_MAX_AGE_S 3600. The contract wording "before every sleep" is still not pinned by the test. Carry: dismissed: equivalent in practice at a 30 s poll against a 3600 s staleness bound; no behaviour the record beat can observe

## Evidence

- Head reviewed: a98c71de318ebdd7ba7eb6e5219866436152035c (ev/HEAD.txt). The body's `## Head` names the same SHA. The handoff body is BODY.md at handoff-body/r10-train-residue-p2 3fa0c3f1a1c6e8da220af66ffb8c89f5e95d6bef. Roles: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- No pull request exists yet, so there is no review packet and no CI run to read. `## Red checks` is not owed at this point, because no required check has run. `merge_train.py owed-reds` was read (ev/owed-reds.txt). The body's "Red checks: none" covers this head. The three `prepr.sh --self-test` 6b rows that 1012ff44 turned red were local, not a CI check. The body discloses them, gives their cause (the over-wide entities recording) and repairs them by taking tests/closures.json from main.
- RESULT `python3 tools/audit/seat/merge_train.py --self-test` at the head: rc 0, "669 checks, 0 failed". All the stamp-hold, P608 and P609 pin lines print ok (ev/selftest-head.txt). This matches the body's 669.
- RESULT `python3 tools/release/stamp.py --self-test` at the head: rc 0, `RESULT stamp_self_test=pass` (ev/stamp-selftest-head.txt). stamp.py is unchanged since d0c9eb66, where its S1-S5 mutants were all KILLED.
- RESULT mutants (ev/mutants.txt, ev/mutants-prior.txt; the driver is ev/mut.py, mine and not the fixer's). Each mutant is one exact replacement in its own worktree of the head, run through the full self-test under `ulimit -v 2 GiB` and a 200 s timeout:
  - A drop `stamp_hold_wait()` in `land`: KILLED, 5 FAIL.
  - B drop the `real` guard: KILLED.
  - E negative age -> None: KILLED.
  - K refresh -> pass: KILLED.
  - R unreadable date -> 60.0: KILLED.
  - L drop `waited +=`: KILLED (MemoryError, no termination).
  - M bound -> `age`: KILLED (MemoryError).
  - T bound -> `if False`: KILLED (MemoryError).
  - U bound -> `waited` only: KILLED ("a hold past the age bound ...").
  - V refresh after the sleep: SURVIVED (equivalent in practice, Findings).
  - X10: SURVIVED (equivalent, see Prior block items).
  - X14, X16, X17: KILLED.
  - The body's nine mutants (A, B, E, K, R, L, M, T) reproduce as killed.
- Null control: the self-test's "no hold runs the merge as today with no wait" passes (0 polls, merge runs).
- RESULT `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` at the head: rc 0, "ALL 2709 ENTITY CHECKS PASSED", 7m06s (ev/entities.txt). The FAIL-shaped lines in it are the script's own planted-fixture output.
- Closure repair: `git diff $(merge-base origin/main HEAD)...HEAD -- tests/closures.json` is empty, so the file is byte-identical to main and the over-wide 1012ff44 recording is gone (ev/untouched.txt). The merge 70ecfa6a against main's parent changes only the PR's own files (merge_train.py, stamp.py, delivery/3498.md).
- Merge: `git merge-tree --write-tree origin/main a98c71de` rc 0, with no conflict (ev/merge-tree.txt).
- VERSION, the manifest, RELEASE_NOTES.md and the golden/claim files are untouched three-dot (ev/untouched.txt), so env_drift has nothing to compare.
- Forward-carry: the body's `Carry: #201` lands as the newest entry of dev/programme/carries/carry-201.json at the head. That entry states its control (the same tree and command with only pid_max changed) and its precondition (record only with the pid ceiling raised). Its stage list names "any later seat that records a closure on a cloud seat". `node tools/policy/brief_lint.mjs`: rc 0, with "0 error(s), 0 warning(s)" for carry-201.json (ev/brief-lint.txt). `carry_audit.py check --body BODY.md --pr-group R10-TRAIN-RESIDUE-P2`: rc 0, "2 routed, 0 unrouted, 0 bad destination(s)" (ev/carry-audit-body.txt).
- This container's /proc/sys/kernel/pid_max reads 32768, matching the body's account of the cloud seat.
- RESULT `env -u BASH_ENV bash tools/pr/prepr.sh --self-test` at the head: rc 0, "542 passed, 0 failed", 5m54s (ev/prepr-selftest.txt). This matches the body's figure at this head, and the three 6b skip rows pass.
- Not re-derived: the closure-recording figures (926/4516 at pid_max 32768; 570/8 at 4194304, 0 outside the committed recording). Each needs a multi-minute strace recording with the kernel's pid ceiling changed, and none of them moves a file in this diff, because tests/closures.json is main's. The `prepr.sh --self-test` figures at 1012ff44, 14f227c5 and 43e95474 were not re-taken either.
- Head re-read before the return: handoff-body/r10-train-residue-p2 is still 3fa0c3f1, and its BODY.md names a98c71de. The remote branch refs/heads/fix/r10-train-residue-p2-pr still points at the earlier reviewed head d0c9eb66, so the handoff head a98c71de, fetched by SHA as the dispatch gives it, has not been pushed to that branch yet. No PR exists. Whoever opens the PR must push exactly a98c71de; any other head is outside this verdict, and `review_carry.py` decides whether this verdict carries to it.
