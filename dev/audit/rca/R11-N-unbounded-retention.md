# RCA: a time-window cache that never evicts

Seat: round-11 root-cause, class `N-unbounded-retention` (production). Instances R11 3, 3 in all, which meets the per-round, cross-round trigger. The trigger counts the classes minted in R11 with the same nearest class (`N-no-expiry`) as one (`fold_ledger.py` `_group_counts`): `N-stale-step-actuation`, `N-unbounded-retention`, `N-uncleared-issue`, `N-unreleased-hold`, 16 instances together. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

`HistorySource` in the card serves a 48 h reach but never drops rows older than it. On a
long-lived element whose plan dialog is panned into the past once a day, it retains 1448 more rows
per day: log 476, actionLog 152, seen keys 628 and 192 memoized overlay points. After 30 days it
holds 60 covered chunks against a reach of 4-5, and the growth has no plateau. The sweep adds
`PriceShapeLearner.days_seen` and `quarter_days_seen`, which grow by one per day of uptime. In each
case the window is a constant the reader respects and the writer ignores.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D9-s2-01` (verified, low): worktree: retained_rows_slope=1448 rows/day (log 476, action 152, seen 628); null 0; perturbation: log_rows_slope 476 -> 0.0 rows/day, memo_points_slope 192 -> 0.0; total 1448 -> 780 (actionLog and seen, untrimmed by this one line, still grow 152 + 628/day).

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `node --expose-gc dev/audit/rounds/round11/D9/s2/card_history_retained.mjs --days 30 --arm baseline` took 2.1 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-unbounded-retention.json`) lists 6 seams. The ledger carries 2 of the seams as instances beyond the finding. Its enumerator is cited as `python3 dev/audit/rounds/round11/D14/unbounded_retention_seams.py`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (c) followed and did not produce the intended result

D9 asks for retained collections with no trim (`dev/governance/dimensions/D9.md:12`), and round
10's D9 s2 seat measured a retained-bytes axis over the card. It did not report this. The growth
appears only when chunks are absorbed, and the round-11 harness drives that with a once-a-day pan
into the past over 30 simulated days. No test runs a component for simulated days, so the growth is
invisible to every short test.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 3 instances over the 148 releases they accumulated in, 0.020 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.020 x 15660 s | 317 s/release |
| form | the card's retained-rows slope arm (`D9/s2/card_history_retained.mjs`, a few simulated days) in the card lane, plus an eviction at its own window constant in each window cache |
| catch share q | 0.5: the slope arm sees the card's HistorySource (4 of the 6 sweep seams' row kinds); the price learner's two sets need the eviction and a Python test of their own |
| expected benefit, q x cost | 159 s/release |
| arm time | 2.1 s (`dev/audit/rounds/round11/D9/s2/card_history_retained.mjs --days 30`, re-timed by this seat) |
| standing cost, arm x 16.3 PRs | 34 s/release |
| verdict | passes by 4.6x |

### Countermeasure (a class barrier, proposed; not built by this seat)

Each window cache gets an eviction keyed to the window constant that its reader already
respects, which is the structural half. The slope arm must show 1448 rows per day on this baseline,
0 past the window after the fix, and 0 on the null arm. It runs in the card lane, which already
starts node. `PriceShapeLearner`'s two sets get the same eviction and a Python test over a few
simulated days. The fix PR owns all of it. The arm's measured 2.1 s is for 30 simulated days, and a
gate needs only enough days to pass the 48 h reach, so the cost below is an upper bound.
