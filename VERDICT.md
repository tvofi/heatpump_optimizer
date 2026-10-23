Fix review: blocked 577ec62dbb35f2353902b5bbe5adb37b69805af2 mutation-unpinned: coordinator.py:9568 RETURN_DEL return active, ret, added by this diff, is refused by the mutation lane at this head, job 120235979635, as at 5b068048, job 120230312005; CI's pin run timed out on it a second time, job 120236183357, so no bot pin comes and the lane stays red; the barrier kills it, replay.kernel_checks 3 of 5 under the mutant, so a recorded killed_by pin is owed

bus-nonce: 0d5b2b364ff8c8e510778510c8fdba8e

PR #2632, group R10-LOOP-CPU (roster origin/handoff/audit-r10-roster), round 3. Measured head 577ec62dbb35f2353902b5bbe5adb37b69805af2 (ev/HEAD.txt), in detached worktrees.
Contract read from origin/main f38f9185 (the head's merge base; `git diff merge-base...origin/main -- dev/governance/roles/` is empty).

**Head moved after measurement.** The PR head is now 2f66e909ea99ffef43bc5ef5c5b9bee542c9c3b9, the github-actions[bot] commit `ci: pin killed mutants` (ev/head-moved.txt). It adds one ledger file only, the pin for `_expire_away_override` GUARD_OFF (M3, killed by tests/features.py in CI). It does not pin 9568 RETURN_DEL, so the blocker below holds at 2f66e909 too. Every number in this verdict was taken at 577ec62.

## The blocker (brief item c)

- The `mutation` lane's red at 5b068048 is `MUTATION TABLE REFUSED -- 4062 unpinned site(s) against 4062 at the ratchet base f38f9185, 1 of them added by this diff`: `ADDED UNPINNED coordinator.py:9553 RETURN_DEL: return active, ret` (ev/mutation-5b068048-120230312005.log).
- **It is not gone at this head.** The head reads the same refusal at the same site, now line 9568 (ev/mutation-head-120235979635.log).
- **The body's answer has failed again.** The body answers this site in `## Red checks` (the `mutation` and `mutation-pins (1)` bullet, read at ab6216ce) and in `## Unpinned sites`. Both answers rest on "re-measured by CI's next pin run" and "`mutation-autofix` pins what CI kills". That next pin run is job 120236183357 at this head, and it timed out on the site again: `UNPINNED ...:9568 RETURN_DEL -- skip-timed-out in tests/features.py`, `PIN KILLED: 1 pinned, 1 left unpinned (... 1 timed out ...)`.
- **No bot pin will come.** mutation-autofix pins only killed mutants (ci-autofix.md, `mutation_table.apply_pins`). This is the second consecutive pin run to time out on this site through features.py, after ab6216ce's job 120155543073. Waiting on the bot does not converge.
- **The mutant is genuinely killed.** I applied M4 (`return active, ret` -> `pass`) at this head and ran `replay.kernel_checks()` (ev/M4-barrier.txt, ev/M4.diff, ev/barrier.py). It reads 5 of 5 unmutated and 3 of 5 mutated. The two that fail are `P10: an armed system identification ...` and `P10: an away override's recovery estimate ...`, which confirms the body's M4.
- **What is owed.** A recorded disposition for coordinator.py:9568 RETURN_DEL, as the refusal itself asks: a `killed_by` pin naming the driver that kills it within budget (tests/entities.py, which runs the barrier), or a features.py check that kills it before the pin run's timeout. Then the body's mutation answer should name the 5b068048 and head runs. `ci_predict.py` listed this site before the handoff (the body's own `## Unpinned sites`), so the repair was visible before handoff.

## RESULT lines

### (a) The new tests fail at a4ccf176's code and pass at the head; each mutant turns red

Each run is whole `tests/features.py` under /opt/hpo/venv-ci (3.14.7), run through my own spawn probe (ev/probe.py). The probe wraps `subprocess.Popen`, counts process_worker spawns, and reports the live ones at exit, after the pool's own atexit.

| run | features.py | spawns | live at exit | log |
|---|---|---|---|---|
| head 577ec62 | `ALL 4310 FEATURE CHECKS PASSED`, rc 0 | 27 | 0 | ev/features-wt.log |
| head tests over a4ccf176's `custom_components/` | `2 of 4310 FEATURE CHECKS FAILED`, rc 1: both R10-LOOP-CPU checks (`pid before=3638 after=3639 handle kept=False`; `child returncode=None`) | 767 | 742 | ev/features-base.log |
| M1: pre-pipe `pickle.dumps` try deleted, `pickle.dump((fn, args), stdin, ...)` restored | `1 of 4310 FAILED`, rc 1: "a job that will not pickle degrades without touching the worker ..." (`before=3642 after=3643 handle kept=False`) | 767 | 0 | ev/features-m1.log, ev/M1.diff |
| M2: the guarded `worker.kill()`/`worker.wait()` reap deleted | `1 of 4310 FAILED`, rc 1: "a reply stream that faults reaps the child ..." (`child returncode=None`) | 27 | 1 | ev/features-m2.log, ev/M2.diff |

- 742 = the body's 740 at ab6216ce, plus the two new checks' own leaked children at round-2 code.
- M1 alone leaves 0 live because the round-3 reap still kills each faulted child. M1's red is the respawn the check pins (a worker lost per unpicklable job), not the leak.
- The mutants were applied by an exact-once replace (ev/mut.py).

### (b) Leaked children and CI's coverage, mutation and fast lanes

- **Leaked children.** 0 at features.py's exit at the head (table above).
- **coverage.** Job 120236094626 succeeded and ran `tests/features.py exit=0 wall=1097s`, with no nodata or could-not-combine line (ev/coverage-head-120236094626.log).
- **coverage-ratchet.** Job 120243722102 printed `ok package coverage 98.67 % >= 96.0 % (21822/22117 ...)`, `ok config_flow.py coverage 100.00 %` and `ok every module >= 95.0 % (0 below)`, ending `COVERAGE RATCHET PASSED`. That is against 85.89 % in the round-2 red run.
- **fast (3.14).** Job 120236094709 succeeded.
- **closures.** Succeeded, and closures-autofix was skipped.
- **mutation.** Job 120235979635 failed: the blocker above.
- **mutation-pins (1).** Job 120236183357 "succeeded" with 1 site timed out and left unpinned.
- **nightly-status.** Job 120235979624 failed. It grades main, and this diff does not reach what it reads (per the brief and fix-review.md step 11), so it is not counted against this PR.
- **Everything else.** All other runs concluded success or skipped (ev/checks-head-final.tsv).
- **pr-contract.** Ran twice at this head (04:12:11Z and 04:12:42Z), both success, after the last red run concluded (mutation at 04:12:23Z).

### (c) The mutation red at 5b068048

Not met; see the blocker above.

### (d) `Closes #2237`

Intended. #2237 is "[R10-P10] CPU work ... starves the loop", class P10, finding D14-s1-01 (ev/issue-2237.txt). The roster group lists `issues: [2237]` and `fixes: [2237]`.

### Other checks

- **Merge.** `git merge-tree --write-tree origin/main 577ec62d` gives tree e5bcd2ff, rc 0, no conflict (ev/merge-tree.txt). origin/main was f38f9185 at that point, and is c26499e0 now.
- **Finder's harness.** `dev/audit/rounds/round10/D14/s1/p10_seams.py` has sha1 c8ba174c at both ends (ev/finder-harness.txt).
  - `--away`: 30.50 loop kernel calls per cycle at fef4a135 (183 over 6 cycles), 0.00 at the head.
  - Null control, `--away --deficit 0`: 0.00 at both ends.
- **Class census.** The body's grep returns 6 sites at the head (ev/class-census.txt), and each matches its disposition in the body. The `pipes missing` branch re-raises with the handle still installed, so it leaves no unheld child.
- **Structure.** `tests/structure.py` passes at the head (ev/structure-head.txt). The only budget movements in the branch are `class_excess_loc` going down, 18268 -> 18258, and `recorded_at`.
- **Untouched files.** VERSION, the manifest, RELEASE_NOTES.md and both claim files are untouched in the three-dot diff.
- **Not re-derived by me:**
  - the body's archscore dS +0.1687;
  - the carry-audit counts;
  - the scoped-gate line `25 TEST SCRIPT(S) PASSED`.

Round 3: a fourth round would owe a re-cut under fixer.md, though the repair owed here is a ledger pin, not a code change.
