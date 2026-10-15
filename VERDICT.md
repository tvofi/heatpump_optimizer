Fix review: merge ce4d5d5ca6518370cc05c78a9ad261fb63fcd1d6
bus-nonce: 8d9b7aca2959ea501ae431f69a088fc7

R10-I1, #2284, closing #2219. Review round 1. Measured head ce4d5d5ca6518370cc05c78a9ad261fb63fcd1d6, a detached worktree, contract `fix-review.md` current with origin/main (`git diff <merge-base>...origin/main -- dev/governance/roles/` is empty). Code delta 4098a04cf..ce4d5d5ca outside `custom_components`, `tests/*.py`, `tests/hastub` and `dev/audit/harnesses`: none. The only additions are `tests/closures.json` (3 inert reads) and the delivery row. So the stress figures taken at 4098a04cf carry, and every cheap figure below was re-taken at ce4d5d5ca.

## 1. Mutation proof (my own runner, not the fixer's)

`tools/audit/seat/features_block.py` takes only blocks that build their own fixtures. Three of the four new blocks read fixtures defined thousands of lines earlier, so I used my own `evidence/myblock.py`. It runs the features.py header, then a stated prelude, then one marker-delimited block. All four null arms pass: A 2, B 7, C 2, D 12 checks.

- RESULT M08 coordinator.py:6522 `and`->`or`: red (block B; both new weather checks FAIL, entries 48)
- RESULT M01 optimizer.py:5541 `and`->`or`: red (block C, IndexError)
- RESULT M03 optimizer.py:5557 `and`->`or`: red (block C, IndexError)
- RESULT M35 ledger.py:306 `if not (dropped)`: red (block A, clean load warned 'Quarantined 0 ...')
- RESULT M26 snapshots.py:239 same: red (block A)
- RESULT guard_flips_mine: I used my own mutant shape, stricter than the fixer's `and`->`or`. It replaces the length half `<i> < len(<seq>)` with `True`, at every LEN site that `enumerate_i1.py` returns at the head (30). get_current_action killed 12 of 12. Sweep killed 17 of 18. The survivor is coordinator.py:4060, as the body states.
- RESULT 4060_guarded: yes. I traced it with a marker on the False branch: features.py drives it False 101 times, and 8 other closure scripts drive it 0 times. With the length half replaced by True, the full `tests/features.py` exits rc=1: an IndexError at features.py:32076, the `_db_short` band check over a 20-entry `dhw_temp_trajectory` (2592 checks ok before it). So it is genuinely guarded already.
- stress.py: the diff writes no production line, so the `mutation` lane drew no mutant (green). The (b4) synthetic checks pass on CI.

## 2. Finder harnesses (d23205d13 export; sha1s match the body), base 5603ee319 and head

- forecast_keep.py: prior_kept=1 at both ends; `--mutant` 0 and `--no-prior` 0 at both ends.
- action_guards.py: live_guards=12 of 12 at both ends; `--equal` 0 at both ends.
- quarantine_warn.py: loaders_correct=2 of 2 at both ends; `--mutate` 0 of 2 at both ends. tests_naming_warning is 0 at the base and 1 at the head.
- gate_blind_2x.py --factor 2.0, under the lease: flagged_solve_arm=0 of 5 at both ends (median 1.951 at the base, 2.031 at the head, thread_factor 1.000, load1 23.5 and 26.6). It is flat by construction because it imports only the pre-existing verdicts. The production behaviour these harnesses measure is unchanged by design. What moves is the gate's kill of each mutant (section 1).
- Instrument disclosure: the stress companion `dev/audit/harnesses/r10_i1_solve_cpu_2x.py` is the fixer's own, and the body says so. I read it: it calls the production `capture_baseline_work`, `solve_cpu_median` and `solve_cpu_over_verdict`, and injects the finder's `cpu_scaler` on `optimize`. I ran it myself under the lease against `--ref 5603ee319`.

## 3. Null and both ends, the solve-CPU channel (each run under `gate_lock.py auto-lease --label revi1`, 54 of 54 judged, count_or_kernel_fired=0, thread_factor 1.000 every run)

| injected | median | flagged | load1 at start / end |
|---|---|---|---|
| 1.0 | 0.944 | 0 | 26.6 / 59.7 |
| 2.0 | 2.073 | 1 | 59.7 / 37.2 |
| 1.3 | 1.174 | 0 | 37.2 / 65.6 |
| 1.0 | 1.072 | 0 | 65.6 / 30.5 |
| 1.0 | 0.902 | 0 | 30.5 / 20.5 |

- CI Linux null at this head, `fast (3.14)` job 116546595276: "median 0.990x ... over 54 of 54", ALL 110 STRESS CHECKS PASSED, scenario thread factor 1.000.
- Per-scenario ratios in the nulls span 0.67 to 1.42. The median holds within 0.90 to 1.07 across load1 20 to 66. The flake margin to the 1.414 factor is at least 1.32x, and the 2x margin is 1.47x.
- sqrt(2) is sound: it is the log-midpoint, and the observed null spread in log terms (at most 0.10) is under a third of either margin (0.35).
- A residual, not a block: a 2x confined to the non-kernel half of the solve reads about 1.5x whole-solve. That is above the factor, but by less than my null spread. The 1.3x arm read 1.174, so this channel can read about 10% low. The body states the under-half-the-scenarios blind spot. This narrower partial-solve case is near the edge, and only the named-seam channels cover it.

## 4-15

- 4: no golden or claim file touched, and no production line changed, so `env_drift --all` has nothing to drift. Not run.
- 5: VERSION, manifest and notes heading untouched.
- 6: class rule `enumerate_i1.py` at head: seams=34 LEN=30 DROP=2 KEEP=2. Every seam is in the diff or dispositioned as the body says (4060 guarded, now confirmed by execution; 9410 KEEP false positive).
- 7: the body's Head names 665f903c2. Measured ce4d5d5ca adds only the record row on top.
- 8: the fixer's counts were re-derived under my own mutant shape, not taken.
- 10: no forward-carry.
- 11: no required check red at ce4d5d5ca. `fast (3.14)` at the superseded head 665f903c2 was cancelled, not red.
- 13: `git merge-tree --write-tree origin/main HEAD` rc=0.
- 14: no `*_budgets.json`, ledger, golden or claim file moves. The `tests/closures.json` +3 inert reads are earned: they are the three new files under `dev/audit/harnesses/`, which harness_headers.py reads, and without them nothing would need listing.
- 15: tests-only and stress-gate additions; no architecture breach.
- tests/stress.py is code-owned. Approval goes via the merge train under mandate 6175172275, not this verdict.
