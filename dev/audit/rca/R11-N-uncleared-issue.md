# RCA: a raised repair issue the recovery path never clears

Seat: round-11 root-cause, class `N-uncleared-issue` (production). Instances R11 4, 4 in all, which meets the per-round, cross-round trigger. The trigger counts the classes minted in R11 with the same nearest class (`N-no-expiry`) as one (`fold_ledger.py` `_group_counts`): `N-stale-step-actuation`, `N-unbounded-retention`, `N-uncleared-issue`, `N-unreleased-hold`, 16 instances together. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

A failure path raises a persistent repair issue (`ir.async_create_issue`), and the success
path that follows does not delete it. Or it deletes it under a guard that does not hold after a
restart. D1-s1-01's case: a stop during a worker reply makes `_await_optimize` fall back and raise
`solve_worker_fallback`. `_clear_worker_fallback` returns early when no cause is latched in this
process, so after a restart the issue outlives the condition indefinitely. The sweep's three more
seams are the grid-fee audit issue, the optimizer run issue and the legionella switch issue. Each
creation site was written with its own delete, or with none. No helper pairs the two.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D1-s1-01` (weakened, low): planted copy: stale_fallback_issues_after_restart=0 in main and null; stop arm 0 -> 1 only under --perturb; runner (worktree) got 1 vs expected 1 at tf 1.181; perturbation: _clear_worker_fallback deletes the issue whenever no cause is latched in this process (drop the early return after the pop); harness flag --perturb.

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s1/m1_stop_midsolve.py --arm stop_midsolve` took 8.9 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-uncleared-issue.json`) lists 4 seams. The ledger carries 3 of the seams as instances beyond the finding. Its enumerator is cited as `python3 dev/audit/rounds/round11/D14/sweep/enum_uncleared_issue.py`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (c) followed and did not produce the intended result

D1's guards step (`dev/governance/dimensions/D1.md:52-53`) asks of each handler of
`enumerate.py d1-excepts` that it logs once and recovers. Round 10's D1 s3 seat ran it. Its unit is
the handler and the coordinator's own state, so a raised repair issue is not part of what
"recovers" means there. The clear side of an issue, and a restart between raise and clear, were
driven for the first time by this round's stop-midsolve arm. The step was followed, and it did not
reach the object that outlives the condition.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 4 instances over the 148 releases they accumulated in, 0.027 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.027 x 15660 s | 423 s/release |
| form | a static `tests/` arm pairing every `async_create_issue` issue id with an `async_delete_issue` of the same id, plus a reasoned list for issues that are cleared only by the user |
| catch share q | 0.5: the arm catches the never-deleted half; a delete behind a restart-unsafe guard (the judged case) needs the lifecycle probe, which stays an audit instrument |
| expected benefit, q x cost | 212 s/release |
| arm time | 0.5 s (an estimate: one AST pass over the package; the sweep's enumerator is not tracked, so it could not be timed) |
| standing cost, arm x 16.3 PRs | 8.1 s/release |
| verdict | passes by 26.0x |

### Countermeasure (a class barrier, proposed; not built by this seat)

The arm refuses an issue id with no delete anywhere in the package, outside the reasoned
list. It must show red on a planted copy with one delete removed and green on the fixed tree. The
judged half (a delete that a restart skips) gets the fix's own regression test, which is D1-s1-01's
`--perturb` arm. A pairing helper that creates and later clears by key would make both halves
structural, and the fix PR may choose it over the arm.
