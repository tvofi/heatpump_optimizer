# R10-RCA-CI-CRITPATH-3: a timed gate graded which host class the runs drew

The root-cause seat for the third `GREW critical_path_minutes` on `main`. It ran beside the
fixer of `r10-hotfix-ci-critpath-3` and not inside it (`dev/governance/roles/root-cause.md`),
and touched none of that fixer's files. Every time below is UTC. The runs and jobs were read
from the Actions API at 2026-11-04 05:20. The replay is
`dev/audit/harnesses/r10_rca_ci_critpath_3/replay.py`. It runs offline in 0.3 s over
`runs.json` beside it: 29 completed `ci.yml` push runs on `main`, 3770..4056, with their jobs.

**Defect.** `tests / ci-ratchet` on `8f286293b` (run 41397326281, job 125133539981, 06:40:46)
printed `GREW critical_path_minutes: 36.5 (budget 34.267, band 1.3)`. Every later push to
`main` read the same verdict through `c3a279e32`. The merge was `#3162`, seven
delivery-row `.md` files, and cannot move CI work. So did the two earlier reds:
`05c0d6d5d` (seven delivery rows) and `f3ffb1c63`, whose own fix says that
"no merge grew the work".

## 1. Cause, reproduced

- **The grade reproduces exactly.** `replay.py` step 1 feeds the window `ci-ratchet` read at
  `8f286293b` to the tree's own `run_minutes` and `critical_path_minutes`. The window is the
  7 runs before it plus its own run, still in progress. The replay gives 36.5 and GREW
  against 35.567.
- **The work did not move.** `python3 tests/closure.py lane-plan --all-scripts --lanes 3`
  reads `tests/closures.json`'s recorded seconds. Its longest lane is 1332.8 s at `9f800cdca`
  (10-25) and 1345.7 s at `b8a027974` (10-31), `c7aa12165` (the last green) and `c3a279e32`
  (the newest red). On CI the closures lane printed `lane plan: 3 lane(s) for 34 script(s)`
  with the same three lane totals in both a 37.4-min run (job 125121503116, run 3870) and a
  20.0-min run (job 125653313138, run 4055).
- **The host slowed every script by the same factor.** Those two jobs ran the same 34
  scripts. Summed script time was 97.7 min in the slow job and 52.7 min in the fast one, a
  ratio of 1.85. The largest absolute deltas show the same scaling: `entities.py` 23.3 vs
  13.9, `features.py` 17.7 vs 8.8, `stress.py` 15.5 vs 7.4. No script's share changed.
  The job log prints neither CPU model nor `nproc`, so the host class has no name here.
  The lane cap is fixed at 3 (`tests/closure.py` `LANE_CAP_CI`), so the plan did not vary.
- **The lanes are bimodal, and the 8-run median flips with the mixture.** In the 29 runs,
  `tests / closures` took either 18.6–29.3 min or 33.7–40.0 min. `tests / fast (3.14)` was
  split the same way, at about 18–25 and 30–35 min. Replay step 2 counts slow closures draws
  among the runs the median actually reads. It finds 3 windows with under half slow (max
  median 33.767, ok) and 6 windows with over 70 % slow (min median 39.667, GREW). The
  windows in between are mixed because the fast lane draws its host independently. From
  run 3865 (05:24 on 11-02) the slow class won most draws: 13 of the next 19 closures
  jobs were slow, against 5 of the 12 before. The median moved from the fast mode to the
  slow mode, and the work moved by zero.
- **What else the cause reaches.** `critical_path_minutes` is the only timing row in any
  `*_budgets.json`. The other rows of `tests/ci_budgets.json` are counts (`script_runs_*`,
  `archscore.*`). `orchestrator_tick.py:381` reads the same budget only to bound a
  WAITING line, and grades nothing. So the class stops at this one row, and it has hit
  that row three times.

| red | onset (push) | hotfix merged | red for | the hotfix's reading |
|---|---|---|---|---|
| 1 | `f3ffb1c63` 10-25 20:21 | `#2839` 10-26 00:58 | 4.6 h | runner queue, so grade work instead of wall |
| 2 | `05c0d6d5d` 10-31 10:43 | `#3045` 11-01 14:39 | 27.9 h | 8-run median spread, so a 1.3 band |
| 3 | `8f286293b` 11-02 06:01 | open (dispatched 11-04 05:13) | ≥ 47 h | — |

Each hotfix was correct about the symptom it was shown. Each one left the gate grading
elapsed time on hosts the repository does not choose.

## 2. Process state: (c) — followed, and it did not produce the intended result

The process is the ratchet's own calibration rule (`tests/ci_ratchet.py:46-51`, `:106-112`).
It grades the 8-run median, records the p90 of a wider window, and sizes the band "at the
measured maximum |8-run median − window median| over 145 runs, 1.3 … never padded". Hotfix
2 followed it to the digit: it reproduced the p90 34.267 exactly and set the band at the
measured 1.300.

It did not produce the intended result because the measure assumes unimodal noise around
the work. The lane timings are a two-class mixture. Under a mixture, a median's spread
measured in a sample where the slow class stays under half says nothing about a day when
it goes over half. The bimodality was already in the calibration-era data, so this is not
a precondition that changed underneath the process (d). Hotfix 1's own message says the
work was "flat at 20.1..34.65 min" over 40 runs. In this sample both modes appear before
the step: runs 3779–3838 hold both 21–25 and 34–39 min closures jobs. It is not (b), since
nothing was skipped. A firmer instruction would only repeat the calibration that was
followed.

## 3. Cost test

`cost(countermeasure, recurring) < cost(defect) × P(recurrence)`, in wall-clock.

- **P(recurrence)** is measured from the table above: 3 occurrences in 8.4 days
  (10-25 20:21 → 11-02 06:01), so 0.36 a day. The windows do not suggest a falling rate:
  6.6 days, then 1.8.
- **cost(defect)** has two parts. One is red-main time: 4.6, 27.9 and ≥ 47 h, a mean of
  ≥ 26.5 h each. The other is three seats per occurrence (fixer, review, and here
  root-cause). The red also blinds the gate: 19 pull requests merged onto `main` while it
  was red on 11-02 (06:41–21:10). Any real growth among them reads as the same GREW.
  Taking only the red time gives 26.5 h × 0.36 a day ≈ 9.5 h of red main a day.
- **cost(countermeasure, recurring)** is the planned critical path below. `replay.py` step 3,
  which includes a `lane-plan` subprocess, takes 0.27 s wall. Say 300 runs a day, which
  rounds up the 286 run numbers between 3770 and 4056 over 29 h. That is about 80 s a day.

80 s a day against about 9.5 h a day: the test passes by more than two orders of magnitude.

## 4. Countermeasure — proposed, owner's decision, not landed

This changes what a ratchet row grades, and that is policy (CLAUDE.md rule 2). It also
touches `tests/ci_ratchet.py` and `tests/ci_budgets.json`, which the parallel hotfix owns.
So it is a draft for the owner, aimed at state (c): replace the measure, not the
instruction.

**Grade the planned critical path, not elapsed minutes.** The new row is the longest lane of
`closure.lane_plan(--all-scripts, 3 lanes)` over `tests/closures.json`'s recorded seconds.
Today it reads 1345.7 s. `critical_path_minutes` would be kept as a printed observation that
does not gate, or as a nightly trend with a band sized to the mixture.

- **It is host-invariant by construction.** CI printed the same lane totals on the 37.4-min
  and the 20.0-min host. Replay step 3's null control gives the same tree the same value
  twice.
- **It detects growth.** Add 300 s to `tests/stress.py`'s recorded seconds and the planned
  path goes 1345.7 → 1445.7 (replay step 3). Every run must show this.
- **It is diff-attributable and runs at PR time.** The value moves only with a
  `tests/closures.json` change. That makes it a cheaper, earlier detector:
  `tools/pr/prepr.sh` could grade it in under a second. Today the timing row can only ever
  go red on `main`, after the merge.

What it does not cover, stated so nobody over-reads it:

1. **Only the closures lane.** The fast lane's work would need the same recorded-seconds
   table before it could join.
2. **The recordings lag real growth.** Recorded seconds change only when a branch
   re-records (`stable_seconds` smooths them). A script that slows without a re-record is
   invisible until one happens.
3. **Runner-level regressions.** A setup step growing, for example, never reaches the
   recordings. The timed observation is what would still show these.

If the owner refuses: the alternative is to keep a timed gate and size its band from a
sample that holds a slow-majority day. The 11-02 windows reach a median of 40.909 on
unchanged work, 6.6 min over the budget. A band that wide would hide 6.6 min of real growth
indefinitely. That trade is worse than grading the plan, and it is why this seat does not
propose it.

## 5. Why `main` sat red with no seat reacting

Measured from git only. The tick board itself is stdout-only and was never persisted:
`heartbeat/orchestrator` holds one `TICK-PASS` in all its history, at 11-04 05:19. So this
seat cannot confirm from the record what any pass of the board printed.

| phase | interval | what the record shows |
|---|---|---|
| driving, main red | 11-02 06:40 → 21:06 (14.4 h) | 108 `dispatch:` commits (a dispatch writes two, as this seat's own did), 32 `roster_edit`, 19 PR merges onto red `main`; no dispatch for the red (the only ratchet-named dispatch is `fixer-r10-machinery-ratchets`, an unrelated group) |
| not driving | 11-02 21:06 → 11-04 05:13 (32.1 h) | no dispatch, roster edit or merge by any seat; only bot commits (`#3178` record merge 00:48, `ci: record nightly kills` 04:23) and `state_docs.py` regenerations about twice an hour (no gap over 2 h), run by a loop still alive |
| dispatch | 11-04 05:13 | `dispatch/fixer-r10-hotfix-ci-critpath-3` and this seat |

The brief's "about 25 h" runs from the last red push run (`c3a279e32`, concluded
11-03 04:58) to the dispatch, which is 24.3 h. Red to dispatch was 46.5 h in all.

- **The expedite rule existed.** `dev/governance/roles/nudge.md:105` says: "An expedite item
  (red main, quota exhaustion, outage, security) bypasses the caps, one at a time." In the
  driving phase it was not acted on, while about 54 other dispatches went out. Each one is a
  pair of commits.
- **The durable record cannot tell (b) from (c).** The only durable per-pass artifact is the
  state docs, regenerated 106 times between 11-01 18:00 and 11-04 07:00. They carry no main-red line:
  `FLOW-BOARD.md`'s `ci-red:N` counts pull requests in the blocked mix (8a867118f, 12:04 on
  11-02; 41769608c, 12:30 on 11-03). The board line `REQUIRED not green … a red main admits
  nothing` (`orchestrator_tick.py:1393`) is printed with `flag=True` and goes nowhere else.
  There is no record of whether the driver saw it and went on (b) or never had it in front of
  them (c). This seat records the state as **undetermined between (b) and (c)**, not as (b).
- **The not-driving phase owes nothing.** With no driver, nothing merged and nothing could:
  the bottleneck was the absent session, red or not. The red added no cost beyond delaying
  its own fix. A countermeasure there would have to drive a session, which is outside this
  defect. Recorded refusal: cost(defect) is about 0 for this phase.
- **For the driving phase**, one draft for the owner serves either state. The dispatch gate
  that already runs before every dispatch (`tools/audit/seat/pr_cap.py dispatch-gate`) would
  refuse a non-expedite dispatch while `main`'s required checks are red. That turns the
  expedite rule into a stop instead of a reading. Its standing cost is one check-runs read
  per dispatch, which the tick already makes. Its value: in this occurrence it would have
  stopped the first of about 54 dispatches at 06:40 and forced the hotfix dispatch then,
  rather than 46.5 h later. Not built: it changes what a seat must do, so it is policy.

## 6. Also found: no root-cause record reached the first two reds

`grep -rn 'CRITPATH' dev/audit/rca` finds nothing. The delivery rows of `#2839` and `#3045`
record no cause or process state. The cause is a reach gap in the enforcement:
`defect-root-cause.md` enforces its second trigger at "a check that went red on a commit in
the branch", checked by the fix reviewer. `tests / ci-ratchet` runs only on a push to `main`
(`tests.yml:2265-2267`), so it can never be red on a branch. The enforced trigger cannot
reach any red from a push-only check. This document is that check's first root-cause record.
Whether the rule should name push-only checks is the owner's call.

## Return

- **State:** (c) for the defect. Undetermined between (b) and (c) for the 14.4 h driving
  phase. For the 32.1 h undriven phase, a recorded refusal (cost ≈ 0).
- **Cost test:** passes. About 80 s a day standing against about 9.5 h a day of red main
  (P = 0.36 a day, mean red ≥ 26.5 h).
- **Countermeasures:** two drafts for the owner, neither landed. First, grade the planned
  closures critical path at PR time and keep elapsed minutes non-gating. Second,
  `dispatch-gate` refuses non-expedite dispatches while `main`'s required checks are red.
