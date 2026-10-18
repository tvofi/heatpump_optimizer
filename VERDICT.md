Fix review: blocked b00c4a33a77e12059933d2d9972b3853874fc310 mutation-vacuous: the receiver half of D7-arch3-04 (thermal_model.planned_draw_runs' getattr fallback) restored alone survives every check; and the new slot_floor_rule disposition exempts coordinator._solve_anchor as "not the plan step's", which FORECAST_STEP_MINUTES' own comment contradicts

bus-nonce: 4723baa02efa9f7ae45bdc1880dd260e

Round 1 for #2365. Measured head `b00c4a33a77e12059933d2d9972b3853874fc310` (re-read before posting: unchanged). Merge base `48bfc6b4e`. Between `6e5753a4a` (the body's base) and `48bfc6b4e`, `custom_components/`, `tests/features.py` and `tests/entities.py` are unchanged, and between `03bffee33` and the head only record files moved. So the body's figures transfer to this head. Every arm below ran from a detached worktree or a `git archive` export of the head (`m0`) and of the merge base (`b0`), using seat-python (venv 3.14) on a loaded host (load1 88 to 95).

## Blocking item 1: mutation-vacuous, the receiver half (fix-review step 1)

The body names two halves of the channel. One is the sender in `pump_arbiter`: the setattr, the decorator and the two floorless calls. The other is the receiver in `thermal_model`: the `getattr(planned_draw_runs, "modulation_floor", None)` fallback. The body's mutation proof restores **both** files together, so it never tests either half alone.

- Mutant m1, both files at the merge base: the block prints `2 of 3 FEATURES BLOCK FAILED`. This reproduces the body.
- Mutant m2, only `thermal_model.py` at the merge base (the fallback is back, the sender stays fixed): `ALL 3 FEATURES BLOCK PASSED`. `tests/entities.py` shows the same FAIL set as the unmutated export m0 (only git, handover and a* lines that need no archive). Across the repo outside `dev/audit/rounds`, the only reader of the attribute is this block. CI's `mutation` lane (job 117544980096, `MUTATION TABLE PASSED`) mutated only `pump_arbiter.py:344/345`. A deleted line draws no mutant, so nothing pins the receiver.
- Why it matters: the receiver is the half that makes the class impossible. With the fallback back, one `setattr(planned_draw_runs, "modulation_floor", x)` from any module re-opens the channel. Check 2 scans only `pump_arbiter.py` for setattr, so that re-opening stays green. The body says the fallback is "gone rather than defaulted", but no check holds that.
- Repair (the fixer's call): add a behavioural check. Set the attribute on the real `planned_draw_runs`, assert `planned_draw_runs(0.5) is True`, then pop it. It must fail on m2 and pass at the head. The mutation proof then names each half alone.

## Blocking item 2: architecture-unsound on added lines (fix-review step 15, fixer.md 17), slot floor

The orchestrator asked whether one owner per concern is reached, or whether a fourth implementation survives under another name. The finder's census `shape_slot_floor.py` (recovered from `1d1974df4`, sha1 a21a0766...) gives:

- base: `implementations=4 driven=3 disagreeing_probes=0` of 10, `--perturb` 2 of 10.
- head: `implementations=3 driven=3 disagreeing_probes=0` of 10, `--perturb` 2 of 10.

These match the body and the judged target ("patch 02: 3 implementations"). The fold itself is correct.

The problem is in the added P2 registry entry. It exempts `coordinator.py::_solve_anchor` as "the FORECAST GRID's anchor, not the plan step's". Two pieces of production text contradict that:

- `coordinator.FORECAST_STEP_MINUTES` is documented as "Resolution the optimizer plans at".
- `pump_arbiter._step_start` is documented as "The 15-minute step start covering now, on the solver's clock".

So the two are one concern, the solver's step covering `now`, spelled twice with two width sources: a literal `15` (and `0.25` in `_inside_silent`) against `FORECAST_STEP_MINUTES`.

Perturbation: in an export with `FORECAST_STEP_MINUTES = 30`, the PR's own `r10_slot_floor_twins.py` reads `disagreeing_probes=3` (`autumn 02:59:59.9 fold1, 12:15 edge, 23:59:59.999`). They agree today only because the constant is 15. The census probes only at the shipped constant, and the disposition records the twin as a different concept. A later seat would read that registry line as fact.

Also, the entities comment and the body say `_step_start` serves three readers: the ledger row, the silent-window lookup and "the step index". `git grep` finds only two, at `pump_arbiter.py:535` and `:879`. `step_duty` indexes by `bisect`.

Repair options, the fixer's choice under step 17:
- (a) One owner. `_step_start` and `_solve_anchor` share one floor on one width constant in a leaf module that both can import, without making `pump_arbiter` import `coordinator`.
- (b) Keep the scope the judge ruled. Then the disposition must say they are the same grid's twin, a pin must assert the two widths are one constant, and the body must drop the third reader.

## Confirmed (RESULT lines, mine)

D7-arch3-04, the finder's `dev/audit/rounds/round10/D7/arch-s3/duty_floor_channel.py` (identical in both trees), cwd = tree:
```
base RESULT leaked_reads=307381 count  reader_calls=984765  null_leaked_reads=0  reflective_writes_pump_arbiter=2  thread_factor=1.001 load1=88.02
head RESULT leaked_reads=0 count       reader_calls=1449321 null_leaked_reads=0  reflective_writes_pump_arbiter=0  thread_factor=1.001 load1=95.42
```
The claim is > 0 against = 0, with the null at 0/0, and it reproduces. The body's 140281 is a race count. I re-derived the direction, not that figure.

D7-s3-8x-slotfloor:
```
shape_slot_floor.py   b0 implementations=4 driven=3 disagreeing_probes=0/10 perturb=2/10 | m0 implementations=3 driven=3 disagreeing_probes=0/10 perturb=2/10
r10_slot_floor_twins  b0 seams=6 folded=0 driven=4 dis=0 perturb=2 identity=0 unclassified=0 | m0 seams=5 folded=1 driven=3 dis=0 perturb=2 identity=0 unclassified=0
V2 s3_82 (my own extraction of catchup/arch-b/v2_s3.py lines 1-42 + the 82 arm; the whole file raises AttributeError on tariff._plateau_aware_day_max at the head, as the body says)
                      b0 0/24686 perturb 12344/24686 | m0 0/24686 perturb 12344/24686
twins with FORECAST_STEP_MINUTES=30 (my perturbation): driven=3 disagreeing_probes=3
```
I could not re-derive the body's sha1 `15a8d534...` for `v2_s3.py`: the tree's file has shasum `0bb56483...` and blob `1130ed23...`. It is probably the hash of their scratch extraction, which is not in the tree.

Mutation, slot floor: with `_observe` put back inline (m3), `tests/entities.py` adds exactly `FAIL P2 owners: slot_floor_rule ... SEAM ['pump_arbiter.py:879 in _observe']` and the planted-sibling null-control FAIL. The features block stays green (it is flat by design). This reproduces the body.

`tests/features.py` merge (orchestrator.md 6): I took `git merge-file --union` of main `6e5753a4a` / base `92accb2cf` / branch `c4304bb1f` and diffed it against the merged `03bffee33`. They differ by one blank line only. `R.check(` counts are b 3747 / o 3750 / t 3764 / m 3767, so 3747 + 3 + 17 = 3767. No clause was lost from either side. Against the auto-merge tree of the two parents, the merge commit differs only in `tests/features.py`. Main has not touched that file from `6e5753a4a` to `48bfc6b4e`.

harness_headers: CI's `fast (3.14)` run at the head (job 117545053031) printed `ALL 109 HARNESS HEADER CHECKS PASSED`, with `sysid_estimator_frontier.py: cpu=162.3s of the 480s bound`. This confirms that the body's 12/109 local failures were host-load wall overruns. The same log has `MODE: SCOPED -- 27 script(s) run, 6 scoped out`, `ALL 4158 FEATURE CHECKS PASSED`, `ALL 2347 ENTITY CHECKS PASSED`, `STRUCTURE RATCHET PASSED`, `ALL 50 GUARD PIN CHECKS PASSED` and `NO UNCLAIMED DRIFT: 56 scenario(s)`.

Check-runs at the head, latest run per name: 30 success, 15 skipped, 0 failure, cancelled or timed_out. `closures`, `mutation` (`MUTATION TABLE PASSED`, 3 ledger sites killed by features.py), `arch-score` and `pr-contract` are success. The earlier head `d329608ae` had 15 cancelled runs, superseded by the push, none red. Red checks: none, so step 11 owes nothing.

Steps 4, 5 and 13: VERSION, the manifest, the notes heading, both claim files and every `*_budgets.json` are untouched against the merge base. `git merge-tree --write-tree origin/main HEAD` exits 0 at `0b1ddb7fd`.
Step 7: the body names the head `b00c4a33a...` and the code head `03bffee33`. Both match.
Step 10: the body's forward-carry is `none`. D2-s2-01 is carried by its own branch per ruling 6240984157, which I did not review.
Step 14: archscore `reflective_writes 17 -> 15` comes from the two removed setattr sites, so it is earned. Re-anchoring the `step_duty` mutation ledger keys is a line move with the same kill.

Evidence: `/Users/timmalmstrom/hpo-seats/r10s3/review-pump-model/evidence/` (HEAD, the harness outputs, the mutant runs, the check-run TSVs, the fast and mutation job logs).
