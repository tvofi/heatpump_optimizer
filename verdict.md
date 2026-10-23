Fix review: merge edc3158d23d19fa9270edaab06293c1ee5a92299

bus-nonce: 8ef895202d8d2525c53ef3fd69926f7b

PR #2632, group R10-LOOP-CPU (roster origin/handoff/audit-r10-roster at 7c5ca6bf), round 4. Measured head edc3158d23d19fa9270edaab06293c1ee5a92299 (ev/HEAD.txt), from detached worktrees. Merge base a6620c30adcdf0d9529ee66977694bfa2a06d5c3 = origin/main. Contract read from origin/main: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty. I re-read the head before writing: `refs/heads/fix/r10-loop-cpu` is still edc3158d. The verdict is merge, so no re-cut is owed.

## Findings

- **Six branch commits carry tool-attribution trailers.** Brief item (5), "commits carry no footers", does not hold. add0c102, a1e2138c, 2854b138, 3d87e591 and 1b4fbc55 each carry `Co-Authored-By` and `Claude-Session` trailers, and 86b3fe71 carries `Co-Authored-By` (ev/trailers.txt, values redacted). All six are round-1 commits, authored 21:07Z to 23:16Z on 2026-10-22. The owner's ban landed as a guard in a4b27986 at 23:07Z. That guard judges only what a push publishes first, so it never charges these commits. Round 4's own commits (05ec7931, 8d25663f, 221ff40f, aeb582c6, edc3158d) carry none. Removing the trailers means rewriting a reviewed, published branch, or squash-merging. A plain merge commit carries them into main's history. Carry: dismissed: published before or at the guard's landing and outside its first-publication rule; whether to squash is the merging seat's call
- **Two R10-LIVESTATE controls are not yet on the roster.** The body's `## Forward-carry` names two controls beyond cccbf4fb's guard check: the keystone on `_expire_away_override`'s returned pair, and the features.py check `an unexpired away override is not re-persisted each cycle; a lapsed one is cleared and saved once`. The body says neither is on the roster, and the roster at 7c5ca6bf confirms it (`grep -c` prints 0). The carried finding itself is present, with its control stated as a precondition: the awaiting `_resolve_away`, the publish guard, and the guard check, red as `if True:`. So I do not read this as `carry-missing`. The two extra controls are in-tree tests that fail by name the moment a reshape breaks them. The keystone ends features.py at check 1, and its ledger pin anchors `return active, ret`. A seat reshaping the expiry into copy-then-publish should know that before it starts, so the roster append is still owed. Carry: R10-LIVESTATE
- **Round-2 item 9b5e6fd8, "CI is not settled at this head".** It does not apply at this head. It described ab6216ce, where mutation-pins (1) was still running and mutation was red. At edc3158d every check run has concluded, none red, and the mutation lane passed (Evidence). Carry: dismissed: settled at edc3158d, every check concluded green including mutation (item 9b5e6fd8)
- **Round-2 item 325975e1, "Round 1's two dismissed findings stand".**
  - Its HASTUB_TZ half still applies at this head and predates it. With `HASTUB_TZ=Europe/Stockholm`, tests/features.py reads `4 of 4323 FEATURE CHECKS FAILED` at the base a6620c30 and `4 of 4328` at the head. The same four checks fail at both ends: the house-meter preference check, the naive/aware timestamp check, and the R9-F1.1 N-shared-config pair. Without the variable the head reads `ALL 4335 FEATURE CHECKS PASSED`.
  - R10-FLY-SUITE-ENV-FLAKES (stage not-started) owns this in its brief and carries. The house-meter check is new since round 1's list, and that group should see it.
  - Its architect-note half (the after-edge ruling) is the orchestrator's. R10-LIVESTATE's `after` already includes R10-LOOP-CPU, which serialises the touched hunks.
  - Carry: R10-FLY-SUITE-ENV-FLAKES (item 325975e1)

## Evidence

### (1) The round-3 block is settled

- **The keystone goes red under the round-3 mutant.** M4 is the round-3 timed-out mutant (RETURN_DEL, `return active, ret` -> `pass`, ev/M4.diff). Under it, whole tests/features.py prints `FAIL keystone: ... [(None, None, ['persist_override'])]` and `1 of 1 FEATURE CHECKS FAILED`, rc 1, wall 1.70 s (ev/features-M4.log). The round-3 pin runs timed out on this mutant at 3 x the driver's measured seconds. CI's driver baseline at this head is 360 s, so the budget is about 1080 s; the mutant now dies 2-3 orders of magnitude inside it.
- **M3 also goes red.** M3 is GUARD_OFF, `if active != ...` -> `if False:` (ev/M3.diff). The keystone is red, `[((True, ...18:00...), (False, None), [])]`, rc 1, 1.79 s (ev/features-M3.log).
- **Null: the unmutated head passes.** It prints `ok keystone: ...` as check 1, both R10-LOOP-CPU worker checks `ok`, the D14-s1-01 guard check `ok`, and `ALL 4335 FEATURE CHECKS PASSED`, rc 0 (ev/features-head.log).
- **CI's mutation lane at this head.** Job 120375371389 printed `MUTATION TABLE PASSED` and `PIN RE-VERIFICATION: 3 reproduced, 0 not reproduced`. That includes `coordinator.py:9701 RETURN_DEL -- killed by tests/features.py`, the round-3 site after main's line drift. It reports 4020 unpinned sites against 4022 at the ratchet base, so no site was added unpinned, and `0 survivor(s) of 3 evaluated` (ev/mutation-120375371389-excerpt.txt). The run was not inconclusive: the features.py and entities.py baselines read rc=0 failed=0, and the null control survived.

### (2) Off the event loop: the finder's harness at both ends

The finder's harness is `dev/audit/rounds/round10/D14/s1/p10_seams.py`, sha1 c8ba174c at both ends. I ran it as `HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub`, venv-ci python 3.14 (ev/finder-base.txt, ev/finder-head.txt).

| run | base a6620c30 | head edc3158d |
|---|---|---|
| `--away` | `loop_kernels_all=183`, `loop_kernels_away_seam=183`, 30.50 per cycle | 0, 0, 0.00 |
| `--away --deficit 0` (null control) | 0, 0, 0.00 | 0, 0, 0.00 |
| `worker_kernels` | 70 | 70 |

- RESULT `--away`: the loop-kernel delta is -183 calls over 6 cycles.
- RESULT null: the delta is 0. The roster's carried null ("with the deficit at 0 the count reads 0 before and after") holds.
- RESULT head `--away --perturb`: `loop_kernels_away_seam=183`, `loop_kernels_all=2625` (ev/finder-head-perturb.txt). The harness still sees the seam at the head, so the 0 is not vacuous.
- **The interval replay.** Its move (`_replay_interval` -> `_replay_step` in the worker) was measured in round 1 with the barrier `replay.kernel_checks()`. That production code is unchanged since: the branch-own diff over custom_components, features.py, replay.py and dst_checks.py has the same `git patch-id --stable` (e5cc819d) at 4bae3ae2 and at edc3158d.

### (3) archscore

- **Re-derived.** `score.py --diff a6620c30 edc3158d` gives `dS +0.1687 WORSENS (inadmissible: coord_footprint 2471->2473)`, with `params_over_10 8 -> 7 +0.1699` (ev/archscore.txt). The dS and the +2 match the body. The body's absolute figures, 2489 -> 2491, were read against its own base bfd61aaf, not this head's merge base: the body says "this head" of 4bae3ae2. The delta is identical.
- **The justification holds.** I planted the two obvious alternative placements on the head (ev/plant.diff, ev/plant2.diff):
  - Moving the expiry write-back into away.py (`expire_state`, which writes the AwayState there) clears the coord_footprint rise. It reads `dS -0.6574 WORSENS (inadmissible: shared_inplace_writes 17->19)` (ev/archscore-plant.txt), which re-derives the body's round-1 claim.
  - A pure `expire_lapse` in away.py, with the coordinator keeping the writes, leaves `coord_footprint 2471 -> 2473` unchanged (ev/archscore-plant2.txt).
  - Either reshape also touches the away override path that R10-LIVESTATE owns next, and the carry tells this group not to reshape it.
  - So I find no sounder placement inside this group's mandate. The +2 is the publish guard plus the sync expiry split that the P10 await requires; the gate's own `## Architecture score` section names it, and arch-score is green at this head.
- **structure.py.** At the head it prints `STRUCTURE RATCHET PASSED` (ev/structure-head.txt). The only budget move against main is `class_excess_loc` 18244 -> 18234, which is down (ev/budgets.diff). No budget is higher than main's.

### (4) The two unrouted items

They are under `## Findings` above, each with its own `Carry:` naming the item id. Before this verdict, carry_audit read `CARRY-AUDIT #2632: 7 finding item(s): 5 routed, 2 unrouted` (ev/carry-audit-before.txt).

### (5) Merge, ledger, CI, version

- **Merge.** `git merge-tree --write-tree origin/main edc3158d` gives tree 11c208aa, rc 0, no conflict and no claim-driver line (ev/merge-tree.txt).
- **The ledger.** `git diff a1fb830e edc3158d -- tests/mutation_ledger` is not empty: 26 files. Every one of them is main's movement since a1fb830e. No ledger path at the head differs from both a1fb830e and origin/main, and each of the branch's four own ledger files is byte-equal to a1fb830e's (ev/ledger-check.txt). That includes the 221ff40f conflict file `..._expire_away_override.RETURN_DEL.67e36ad4.json`, whose diff to a1fb830e is 0 lines and whose reason names c6ef0668. So the substantive property holds, but not the literal empty diff the brief states.
- **The scoped gate.** At the head, `tests/closure.py select --diff <merge-base>` prints `MODE: SCOPED -- 23 script(s) run, 10 scoped out.` (ev/scope-select.txt). `ci_predict.py --base origin/main` prints `CI PREDICT: no closures or fast red predicted against a6620c30adcd` (ev/ci-predict.txt). I did not run the gate itself; CI's heavy runs are cited.
- **CI**, from one bulk check-runs read at the head after all runs concluded (ev/checks-head.json, ev/checks-head.tsv): 41 runs, none failure or cancelled.
  - mutation 120375371389 success, read in its log above.
  - fast (3.14) 120375504577 success.
  - coverage and coverage-ratchet success.
  - closures success, with closures-autofix skipped.
  - arch-score, budget-raise-gate, typing and env-matrix success.
  - nightly-status and delivery-status success.
  - pr-contract 120375367781 and 120375612866 success.
  - No red check at this head, so step 11 owes nothing new. The body's `## Red checks` answers the earlier heads' reds, and round 3's mutation red is answered by the keystone and its pin.
- **Version.** VERSION, the manifest, RELEASE_NOTES.md and both claim files are untouched in the three-dot diff. No golden fixture moved, so env_drift has nothing to compare.
- **Head and carry (steps 7 and 12).**
  - The body's `## Head` names edc3158d.
  - It also keeps a stale paragraph naming 015df0a2, which is not an ancestor of this head. That was an earlier merge attempt.
  - The resolution delta from the body's measured 4bae3ae2 to edc3158d is: main merges, plus the a1fb830e ledger file resolved to the bot's version. I judged it above.
- **Forward-carry (step 10).**
  - bf112946 (R10-FLY-SUITE-ENV-FLAKES, `correcting the carry above`) and cccbf4fb (R10-LIVESTATE) are both ancestors of the roster tip, and each states its control.
  - On the two extra LIVESTATE controls, see `## Findings`.
- **Not re-derived:**
  - the body's `25 TEST SCRIPT(S) PASSED` scoped-gate count;
  - the pin run's 549 s baseline;
  - the round-1 `shared_inplace_writes 17 -> 19` as measured before the split (I re-derived the same figure through plant 1 instead).
