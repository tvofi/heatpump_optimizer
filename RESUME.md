# #2066 cop-floor: resume

State: **round 10 handed off** at code head `c2ba6891635278379a076a5385653889ede4bb2d`,
published to `handoff/r9-cop-duty-floor` (from round 9's `386b7e2ff`); body on
`handoff-body/r9-cop-duty-floor`. Seat worktree `/Users/timmalmstrom/hpo-seats/live-cop-floor/wt`,
evidence `/Users/timmalmstrom/hpo-seats/live-cop-floor/ev/r10/`. `fix/cop-duty-floor` was NOT
touched -- the orchestrator moves the PR head. Round 9 blocked on `conflict` alone; this round
resolves it.

## What round 10 did
- `git merge origin/main` **twice** (merge, never rebase): first `23d354970`, which had the eight
  conflicts round 9 blocked on, then `7cd5a588c`, which merged **clean** (rc=0, no `CONFLICT`).
  `git merge-base origin/main HEAD` is now `7cd5a588c`, both merge base and ratchet base.
- Ledger: took **main's** row for all seven (same `anchor`/`old`/`killed_by`, differ only in `reason`;
  main's is the seat-measured 7a record). Verified before picking: each of main's nine digests of the
  ten formerly-added sites reads exactly 1 row (`git ls-tree -r --name-only origin/main`).
- features.py: **union, not a pick**. Kept main's auto-merged final 7a block + this branch's 351-line
  COP block; deleted the branch's carried copy of #2065's round-3 agreement-bound pair (25 lines,
  anchors `ac5977ac`/`bae80808`) because main rewrote those checks and its own killed_by rows name the
  rewrites as the killers. Result `R.check(` 3571 = main's 3548 + 23; union_proof.py: 0 main names
  lost, 23 HEAD-only names, all of them the COP block.
- `tests/closures.json` / `tests/structure_budgets.json` came through the `ledgermerge` driver
  (`LEDGER-MERGE: resolved`, 21 sets unioned, no refusal). Branch's closure delta over main is now
  ONE line: `dev/audit/harnesses/cop_duty_floor.py`.
- Re-derived, not carried: claims.py 125/123/0-false, 75/75/0, 27 importers (rc=0, committed evidence
  byte-identical after the run); census 33/528/29/406/**123**/18, 93 files, 75 modules, rule
  re-calibrated on this tree (min 385 / mean 195 do NOT reproduce base's 120; max and Jaccard do, and
  `tests/entities.py::_d308_pairs` uses Jaccard); ha_rule 75/27/28/47/['inputs'].
- **One silent-agreement fix in the tree** (`025b779c4`): the deployment_shape docstring's "#2066's
  merge brought draw_range.py and flow_meter.py..." clause. Main alone now reads 123, so the cause was
  #2065's merge; no instrument reads cause clauses (it does read the numbers), so it was hand-corrected
  and the four-tree control recorded: 120 / 120 / 123 / 123, pairs 59/74=0.7973 -> 60/75=0.8000.
- **The consequence: `mutation`'s refusal cause is gone.** `added by this diff 0`, `added_keys 0`,
  `ratchet_refusal None`, `unpinned 4602 <= base 4617`, ci_predict prints no warning. CI's own
  `--scope changed --base origin/main --max 10 --jobs 3` prints no `MUTATION TABLE REFUSED`; it stops
  at `INCONCLUSIVE`, **exit 0** -- on `baseline tests/env_drift.py: rc=124 ... 1200s` (this box's own
  pool bound under ~12 resident features lanes) and, on the earlier run, on the `features.py` red
  baseline. Neither is the diff.
- `--normalize` at the merged tree (throwaway detached worktree, removed): 1397 dispositions, 0 retired
  keys, aggregate ledger sha1 unchanged `631c1de6581d...`, tree byte-unchanged.
- Gates local: structure PASSED (four caps DOWN vs live main, all at measured); entities ALL 2250
  PASSED at this head (2243 at `025b779c4`; its 46 ungraded `a3:`/`a4:` report lines are the identical
  multiset at every head); deployment_shape PASSED; guard_pins 50/50; harness_headers ALL 109 at
  `025b779c4` but 12 FAILED at this head, all twelve one harness (`D7/sysid_estimator_frontier.py`)
  hitting its 900 s wall limit under the same box load -- the branch touches nothing under
  `dev/audit/rounds/round4/D7/`; **the null control for that failure**: run alone afterwards, the same
  harness exits 0 with its 14 RESULT lines in 52 min wall at **215 s user CPU / 7 % CPU / load1 221**
  (`d7_frontier_alone.out`) -- starved, not broken; closure selftest 57; layout ok; brief_lint rc=0
  with 0 findings on both carry files. Harness re-run: 31 RESULT lines, rc=0, `diff` vs round 9's
  capture empty (the files it drives, `accuracy.py` and `draw_range.py`, are byte-identical at every
  head). `features.py` is `1 of 3958 FAILED` at `025b779c4` (the macOS `R9-F2.1 P3` BLAS float); **the
  run at this head was killed by the box** (SIGTERM; other seats' features lanes resident), so no
  final-head features count exists here -- CI's `fast (3.14)` owns it.
- Ancestry reds re-enumerated over 32 commits: 25 rows / 5 names -- mutation 12, nightly-status 7,
  fast (3.14) 3, briefs 2, nightly-ha (stable) 1. Fell from round 9's 40 because #2065's commits left
  the range when it merged. `prepr` re-derives the same five and reports them answered.

## Next
1. Orchestrator: App-push this head to `fix/cop-duty-floor` -> the `pull_request` run. `mergeStateStatus`
   should leave `DIRTY` (main is an ancestor of the head), so CI will finally run at a head of this PR.
2. What CI can answer and this box cannot: whether `mutation` is now green (the drive needs the Linux
   floats), and what the pins matrix says for the `6deb0603` pair at `coordinator.py:4562`
   (`CMP_BOUND` + `GUARD_OFF`) -- 2 sites in the pool, charged by nobody. If the matrix reports either a
   survivor, the disposition comes back to this lane (round 8 already drove the CMP arm: survivor).
3. RCA seats still owed (not this body's to write): the line-shift recurrence; and the narrowed class --
   a body that defers a *measured survivor* to `mutation-autofix` is falsified by no check.
4. If main moves again before the merge, re-run the conflict read before resolving:
   `git merge-tree --write-tree origin/main HEAD`. The branch's own ledger surface is 51 added
   `killed_by` rows plus 2 renames (the `flow_lift_power_floor_kw` -> `nameplate_power_floor_kw` pair);
   11 of the added rows name `draw_range.py` (`follows_ask`'s nine and two `@module.CONST`), because
   `follows_ask` is this branch's function, not #2065's. `ev/r10/resolve_markers.py`,
   `drop_stale_dr3.py` and `union_proof.py` are the instruments that did it this round; reuse them
   rather than resolving by hand.
