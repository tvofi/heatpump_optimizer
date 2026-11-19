# RCA: a refresh request coalesced into a solve that read its inputs first

Seat: round-11 root-cause, class `N-dropped-refresh` (production). Instances R11 12, 12 in all, which meets the per-round, cross-round trigger. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

Home Assistant's `DataUpdateCoordinator.async_request_refresh` goes through a debouncer. If
a refresh is already running, the debouncer folds the request into it, but that refresh read its
inputs before the write that asked for the re-plan. The request is lost until the next interval,
30 min by default. #1754 added `_optimization_rerun_requested` for the direct path. It is not set
on the debounced path. D1-s1-03 drops the re-plan in 7 of 8 debounced rows, and 0 of 8 direct rows.
The sweep lists 11 more callers (away, economy, manual plan, comfort-weight reset, holiday,
thermal parameters, heat-loss reset, snapshot restore, system identification, boost, the
input-return watch, `entity.publish_then_refresh`). All 12 share one cause: the request method
itself has no knowledge of a solve in flight.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D1-s1-03` (verified, medium): planted copy: stale_request_refresh_rows=7 of 8 (debounced); null origin=direct 0 of 8; --perturb-rerun 0 of 8; perturbation: async_request_refresh records the #1754 re-run (self._optimization_rerun_requested = True) when self._optimization_running before deferring to the debouncer (harness flag --perturb-rerun).

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `D1_CENSUS_DIR=dev/audit/rounds/round11/D1/s1 PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s1/m4_race.py --part B --origin debounced` took 300 s and exited 124 (killed at the 300 s limit). The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.
 The harness did not complete on this tree, so its time is not a standing cost; the judge's reproduction above stands as the evidence.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-dropped-refresh.json`) lists 16 seams. The ledger carries 11 of the seams as instances beyond the finding. Its enumerator is cited as `python3 dev/audit/rounds/round11/D14/n_dropped_refresh.py`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (c) followed and did not produce the intended result

#1754's fix was correct for the call path it was reproduced on, a direct
`async_refresh` during a solve. Its unit was that path. D1's race step
(`dev/governance/dimensions/D1.md:50-51`) mutates each writer mid-solve, and round 10's D1 s1 seat
ran it without reporting this. The round-11 harness carries the debounced origin as an arm of its
own (`m4_race.py --origin debounced`). The library's request method, which every
other caller uses, was not in it, and the fix's mutation proof could not see a path it did not
drive. The process ran and produced a fix one call path wide.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 12 instances over the 148 releases they accumulated in, 0.081 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.081 x 15660 s | 1270 s/release |
| form | one owner: the coordinator overrides `async_request_refresh` to set the re-run flag when a solve is in flight, plus a `tests/` arm running the debounced-origin rows of `D1/s1/m4_race.py` |
| catch share q | 1.0: every caller reaches the override; the arm drives the debounced origin that all 12 seams use |
| expected benefit, q x cost | 1270 s/release |
| arm time | not measured (`dev/audit/rounds/round11/D1/s1/m4_race.py --part B --origin debounced`, re-timed by this seat) |
| standing cost, arm x 16.3 PRs | not computable |
| verdict | not computable: the form's harness did not complete on this tree (see the re-run line) |

### Countermeasure (a class barrier, proposed; not built by this seat)

The override is structural: one method, which all 12 callers already reach. The arm must
show 7 of 8 rows stale on this baseline, 0 under the override, and 0 on the direct-origin null
control. The fix PR owns both.

The finder harness did not finish inside 300 s on this tree, so it is not a gate form as it stands. The structural part of the countermeasure (one owner) has no standing cost and is proposed regardless. The arm is proposed as a single debounced row of the harness, and the fix PR times it. At the expected benefit above, any arm under 78 s per PR passes.
