blocked d92ffb8726d943bf336b1abd69c5aff066293820 transport-in-tree: handoff/round9/fix/F9.3-body.md and handoff/round9/fix/resume/F9.3.md ship in the PR diff; the body says they ride above the code head and are not part of the PR

# R9-F9.3 fix review, PR #1783, round 1

Measured head: `d92ffb87` (code `2c206fa9` + main merge `f752cc51` + delivery row).
Live head when posted: `fd18ede2`. That commit is the ci-autofix bot's `ci: re-record closures`, and it touches only `tests/closures.json`. Every figure below was taken at `d92ffb87`. No production or test code changed after that commit, so the figures still hold.
Environment: Linux cloud box, Python 3.14.7 (the same line as CI, not 3.14.0rc2), hash-pinned `requirements-ci.txt`, `OPENBLAS_CORETYPE=Haswell`, 1 thread.
Evidence directory: `/mnt/project-files/audit-r9/fix/evidence/F9.3-review-d92ffb87`.

## Blocking finding

1. **The PR carries its handoff files.** `git diff origin/main...d92ffb87` adds `handoff/round9/fix/F9.3-body.md` (238 lines) and `handoff/round9/fix/resume/F9.3.md` (107 lines). They enter through 08306f68, 73072cde and ac66363d (the resume note) and through 21a9d614 (the body draft). All of these are ancestors of the code head `2c206fa9`. They are not stacked above it. The body makes two claims about these files. It says "The resume note and this body ride in a transport commit stacked above the code head and are not part of the pull request". It also says the code head "removes the resume note". Both claims are false at `2c206fa9`, `d92ffb87` and `fd18ede2`. This breaks the standing rule that a code head must have no `handoff/round9/fix/resume` files in its ancestry. `tests/closure.py:251` also records that these notes "are not on main".
   *Fix:* rebuild the chain on a new `-v5` branch without the resume and body commits, or add a commit that deletes both files. The first option is cleaner because it leaves no ancestry. Then correct the Head section of the body.
   *Side note for the orchestrator:* main already carries two such files, `handoff/round9/fix/resume/EG-B10.md` and `F7.5.md`, merged with #1779 and #1781. Nothing gates this. It recurs across three PRs.

## Checks that passed (RESULT lines)

- `finite_boundary.py` at the head: `ALL 67 FINITE BOUNDARY CHECKS PASSED`, `RESULT domain_stores=13 domain_fields=1231 domain_probes=764 domain_refused=0 domain_unreached=0`. These match the body.
- `typing_ruler.py --mypy` (3.14.7, the typing lock installed with `--no-deps` as CI does): `ALL 9 typing-ruler checks PASSED`.
- `mutation_table.py --scope changed --base origin/main --max 10 --jobs 3` (base `1f1ec731`): `0 survivor(s) of 10 evaluated`, `MUTATION TABLE PASSED`, rc 0. The null control survived. The unpinned count went from 3581 to 3576. CI's mutation lane at `d92ffb87` was still running when this was posted. It uses the same Python line, so no interpreter gap is expected, but that lane's result is the authoritative one.
- My own 16 mutants were run against `finite_boundary.py` (`own_mutants.txt`). 15 were killed: the fuse-advisor, snapshot, month-report and score-day `admitted` gates; the comfort clip; the CUSUM cap; `_learned_pair` positivity; the draw floor; the ledger meta count; the freq `OverflowError`; the lead-count floor; the gains floor; the aperture `n` floor; the wear month floor; and the `in_domain` upper bound. One survived: M7, which deletes the `_log_off_domain(self, data)` call. That is acceptable, because the call only writes a debug log.
- The finder's harnesses from evidence commit `79aa98ec` were run from exports of `a15e3e33` and `d92ffb87`, with sha1 values matching the body. Both ends gave the same results: `stuck_after_day=0`, `duty_targeted_stuck=0`, `v2_one_bad_cell_flagged_migrated=0`, `price_model_silent_invalid=0`, `peak_tracker_silent_invalid=0`, `p1_escaping_mutants=0` of `mutants=4027`. The results are flat by design, as the body says. The companion that moves is `domain_refused`.
- Step 6, class enumerator: the P1 enumerator (sha1 `59212b6b`) gives `numfield_seams=28 numfield_unguarded=13 dtnaive_instance=0 fixture_clean_unguarded=0` at both ends. The body dispositions all 13, so no seam is class-open.
- Whole-tree gates at the head (which already contains main `1f1ec731`): `codeowners_gap --check` gives `uncovered_files=0`, `policy_lint.mjs` gives 0 errors, `policy_lint --budgets` exits 0, and `structure.py` passes. `git merge-tree` against main is clean.
- `VERSION`, the manifest version and the notes heading are untouched. The structure re-record only moves down (9034 to 9023). The contract diff is empty against main.
- Checks: nothing is red on `d92ffb87` so far. The bot commit came from the `closures` job, not from a red check.
- Adversarial probes: store imports cause no import cycle (each module was imported alone). `_log_off_domain` costs about 7 ms on a 672-sample accuracy payload, and `_tries()` about 0.14 ms. The fuse-advisor, month-report and snapshot-summary writers have kept a stable key set since they were introduced, so an upgrade does not drop a stored record for an undeclared legacy key.

## Non-blocking notes

- `in_domain` of `choice` accepts `True` for the lead bucket `1` (`True in (1, ...)`). This is harmless.
- Arm 6's in-domain probe never tries a negative value for a domain that is unbounded below. That is why it missed item 2 below.

## The five found-but-not-fixed items

1. **The fresh-install DHW pattern (cells of 0.1, below the 0.2 floor) is renormalised at the first restart.** A later stage should take this: R9-EG-B8 (the DHW block). Its brief should say that the stored profile's writer domain must equal what `normalize_profile` admits, or the first save must normalise. No user-visible cost has been measured.
2. **`_async_load_energy_totals` floors each total at 0** (`coordinator.py`, `max(self._energy_totals[key], float(value))`). The cost accumulators are `SensorStateClass.TOTAL` (sensor.py `_AccumulatingCostSensor`) and DOMAINS declares them `_R`. A negative lifetime cost therefore reloads as 0, and HA's long-term statistics record a positive cost step at each restart. This is a P1 instance: the loader refuses an in-domain value. The bug predates this PR.
   *Where it belongs:* the P1 class this PR owns. Fix it here while the head is re-cut anyway: floor only the `_energy_kwh` keys, and add a negative in-probe for domains unbounded below. If the fixer declines, carry it to R9-EG-B4's brief, the store seam.
3. **A `score_day` book stored as `{"free_streak": n}` has no day and is dropped on reload.** This is a real writer shape (`_close_score_day`, the free-day branch). A restart between the midnight close and the first fold resets the #908 streak. The loader dropped it before this PR too. The declaration `score_day/day: _DAY` (not null) disagrees with the writer. The impact is small.
   *Where it belongs:* this PR, where declaring `day` as null-able and admitting a streak-only book is a small change. If the fixer declines, no action.
4. **The snapshot lead of 0 bounds a future `lead_pending` to now.** No action: the snapshot record is opaque, and restore never reads it.
5. **`store_fuzz.py` reads `flow_bias_bad=6` at both ends.** No action. The harness predicate `abs(bias_k) > FLOW_BIAS_CLAMP_K` predates the deliberate asymmetric clamp (`flow_lift.py:236`, up to `FLOW_SUPPLY_MAX_C`). The harness is stale; there is no defect.
