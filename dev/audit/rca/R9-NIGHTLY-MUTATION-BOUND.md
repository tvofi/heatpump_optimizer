# RCA-1565: the nightly mutation lanes bound each driver below the pool factor they measure

The countermeasure seat for `bugclasses.json`'s `RCA-1565-mutation-timeouts`
("CI mutation job 90-minute timeouts"), which it found at `status: partial` with
`process_state` and `cost_test` owed and which this PR moves to `done`. It lands
the two missing parts and the fix, and ran beside the fix, not inside it
(`dev/governance/rules/defect-root-cause.md`).

- Base measured: `origin/main` at `b2b6acd64` (2026-10-09). Every bound below is
  re-derived there with the tree's own `driver_timeout`, not carried from the
  diagnosing seat. Where a figure IS that seat's and was not re-taken, the line says
  so.
- Evidence: `/Users/timmalmstrom/hpo-seats/fix-nightly-bound/logs/` --
  `bounds_reproduction.txt`, `pool_tables.txt`, `enum_factor_rule.txt`,
  `enum_figures.txt`, `red_jobs_1003_1007.txt`, `jobs_1008.txt`,
  `record_autofix_nights.txt`, `schedule_created.txt`, the CI job logs
  `job-{111162760555,111397325352,111692063912,112192034609,112708108856,112708109541,112708109605,113233890923}.log`,
  and the `entities.py` failing/mutation/green arms. §7 names the command behind
  every figure. GitHub reads against `tvofi/heatpump_optimizer`.

**The defect in one sentence.** The nightly mutation lanes bound every driver's
first run by `max(--timeout floor 1200 s, TIMEOUT_SCALE 3 x that driver's
*solo-gate* recorded seconds)`, while the lane drives the same script inside a
3-worker pool whose cost this document measures at **0.47x-3.27x** that recording
(§2's enumerator); `closure.SECONDS_BAND = 2.0` deliberately keeps a committed
value up to 2x below the cost CI last measured, so the worst-case headroom over
the script's true solo cost is `TIMEOUT_SCALE / SECONDS_BAND = 1.5x`. The bound
therefore trips whenever a driver's pool factor exceeds `3 x (committed / true)`
-- at worst `1.5`, against a measured factor that reaches `3.27` and a
`boost_drift_replay.py` factor of `>= 3.00` on both nights it died. A factor below
1 (the range's low end) is not a hazard; it is a recording that was stale *high*.

**How many nights this arm reddened: two of the six, not four.** Six consecutive
scheduled runs concluded `failure` from 2026-10-03 to 2026-10-08 (last green
`36984959667`, 2026-10-02T08:36:04Z), and they had **five** distinct causes. The
bound arm below is the cause on **10-07 and 10-08**; 10-03 and 10-04 reddened on
its sibling -- the `EXCLUSIVE`-under-`--scope-full` null-control arm, which §5
routes to the owner and this PR does **not** fix; 10-05, 10-06 and 10-07 reddened
on `record-autofix`. The two arms together are the "4 of 6" the diagnosing seat's
cost test uses, and §4 keeps that family figure labelled as such. Per-night
attribution, each from that run's own failing-job list and job log
(`red_jobs_1003_1007.txt`, `jobs_1008.txt`, `record_autofix_nights.txt`):

| night | failing job(s) | arm | CI's own printed text |
|---|---|---|---|
| 10-03 | `mutation-ledger` | `EXCLUSIVE` null control | `MUTATION TABLE REFUSED -- the null control …__init__.py:42 NULL_COMMENT was killed by tests/harness_headers.py (… rc=-24 …)` |
| 10-04 | `mutation-ledger` | `EXCLUSIVE` null control | `MUTATION TABLE REFUSED -- … accuracy.py:42 NULL_COMMENT was killed by tests/stress.py (… 8.0x … vs its own budget 7.9x …)` |
| 10-05 | `record-autofix` | record lane | `record-pr open: POST …/pulls returned HTTP 401` |
| 10-06 | `record-autofix` | record lane | `record-pr open: POST …/pulls returned HTTP 422` |
| 10-07 | `record-autofix`, `mutation-ledger`, `mutation-nightly` | **bound** + record lane | `timed out after 1576s`; ledger: the null control `was timed out under tests/boost_drift_replay.py`; `Process completed with exit code 128` |
| 10-08 | `closures`, `mutation-nightly`, `nightly-ha` x2 | **bound** + two new causes | `timed out after 2401s` |

## 1. The mechanism, reproduced from the committed table

`tests/mutation_table.py`'s `driver_timeout(floor, seconds)` is
`max(floor, ceil(TIMEOUT_SCALE x seconds))`, and `main()` seeds `seconds` from
`recorded_seconds()` -- the solo-gate recording in `tests/closures.json` -- for a
driver's first (baseline) run. Deriving that at each night's head with the tree's
own function (`bounds_reproduction.txt`) reproduces, to the second, the timeout CI
printed on the two nights it printed one. Columns 3-4 are measurements (the
committed table, the job log); column 5 is marked where it is an **inference**
rather than something CI printed:

| scheduled run | head | `boost_drift_replay.py` recording | derived bound | that night's lane output for this driver |
|---|---|---|---|---|
| 10-03 `37108891698` | `2e569748a` | absent (`None`) | `1200` (the floor) | **no timeout printed** -- the lane refused on the `EXCLUSIVE` null control. *Inferred* exposure only: the floor is below the 1573 s this script measured in the pool on 10-07 |
| 10-04 `37189092011` | `fb11a0172` | absent | `1200` | **no timeout printed** -- refused on the `EXCLUSIVE` null control; same *inferred* exposure |
| 10-05 `37288195257` | `a1da8d381` | absent | `1200` | **no timeout printed** -- that night reddened on `record-autofix` alone; same *inferred* exposure |
| 10-07 `37595831734` | `be0cb8213` | `{seconds: 525.3, rc: 0}` | `1576` | `timed out after 1576s` (job `112708109605`) -- **printed** |
| 10-08 `37753990323` | `816547efe` | `{seconds: 800.2, rc: 0}` | `2401` | `timed out after 2401s` (job `113233890923`) -- **printed** |

The bound the committed table implies **equals the timeout the lane printed** on
both nights it tripped, so the mechanism is shown to produce the observed failure,
not asserted. On 10-07 the same script's baseline completed in the sibling
`mutation-ledger` lane at **1573 s against the 1576 s bound -- three seconds of
margin** (job `112708109541`); the next night the pool cost exceeded 2401 s and
died. At this merge base the recording has been re-recorded to 1489.6, giving a
bound of **4469 s** -- the number moved, the mechanism did not: 4469 clears the
largest pool cost *completed* for that driver in the window (1573 s) by 2.8x only
because a human/bot happened to re-record it high. That is what happened next: the
10-09 scheduled run `37909555545` (head `c518447eb`) concluded **success**, ending
the streak without this fix, on the luck of that re-recorded number.


## 2. The pool factor the lane itself measures

Each nightly prints `baseline <script>: rc=… <N>s` per driver, inside the
3-worker pool. Comparing those against the committed solo recording at the same
head (`pool_tables.txt`, from the three job logs) gives the pool/solo factor per
driver. The long drivers on 2026-10-08 (job `113233890923`):

| driver | solo | pool | factor | bound | margin |
|---|---|---|---|---|---|
| `boost_drift_replay.py` | 800.2 | **2401 (rc 124)** | **3.00** | 2401 | **0 -- timed out** |
| `features.py` | 282.5 | 772 | 2.73 | 1200 (floor) | +428 |
| `optimality.py` | 130.7 | 298 | 2.28 | 1200 | +902 |
| `structure.py` | 5.7 | 13 | 2.28 | 1200 | +1187 |
| `stress.py` | 616.7 | 430 | 0.70 | 1851 | +1421 |
| `entities.py` | 196.6 | 140 | 0.71 | 1200 | +1060 |
| `env_drift.py` | 0.9 (stub) | 524 | -- | 1200 (floor) | +676 |
| `harness_headers.py` | 167.0 | 211 | 1.26 | 1200 | +989 |

The table above is the long drivers only, a subset of the rows the enumerator
reads. **The rule for the factor range** (`enum_factor_rule.txt`, which prints
every row it counts): over every `baseline tests/X: rc=… Ns` row in the three
parsed job logs, factor = `N / the committed solo recording for X at THAT run's
head` (`git show <head>:tests/closures.json`), excluding (a) `tests/env_drift.py`,
whose committed recording times the declared stub (`closure.py` #934) and whose
real cost is the `--all` run, and (b) any driver whose solo recording is under 1 s,
below the log's own 1-second resolution. That gives **51 rows**:

| job log | head | rows | min factor | max factor |
|---|---|---|---|---|
| `112708109605` (10-07 nightly) | `be0cb8213` | 16 | 0.47 (`harness_headers.py`: 449.2 -> 209) | 3.00 (`boost_drift_replay.py`: 525.3 -> 1576, **censored**) |
| `112708109541` (10-07 ledger) | `be0cb8213` | 16 | 0.47 (`harness_headers.py`: 449.2 -> 209) | 3.27 (`structure.py`: 5.2 -> 17) |
| `113233890923` (10-08 nightly) | `816547efe` | 19 | 0.62 (`block_duty.py`: 1.6 -> 1) | 3.00 (`boost_drift_replay.py`: 800.2 -> 2401, **censored**) |

So the range this document quotes is **0.47-3.27**, and both ends are rows in the
table above rather than a summary of it. **Censored** means the run was killed at
its bound, so its "pool" column is the bound it hit and its factor is a *floor*,
not a measurement: `boost_drift_replay.py`'s true factor on both nights was
`>= 3.00`. The one uncensored measurement of that driver is 10-07's ledger lane,
1573 s / 525.3 s = **2.99**. `env_drift.py`'s apparent 500-800x is the stub, and it
is protected by the **floor**, not the scale. Only `boost_drift_replay.py` sat above
the floor with a factor at the scale, which is why it is the driver that reddened.

## 2b. Class search: where else this shape reaches

`root-cause.md` §3/§6 make the class search part of the deliverable, so it is
recorded here and not only in the diagnosing seat's scratch. Each member below was
re-measured at this head; where the diagnosing seat's §3 was wrong, the correction
is stated rather than carried.

1. **A `closures` red on `main` has no repair lane -- confirmed.** `closures-autofix`'s
   job condition at this head is `!cancelled() && github.event_name ==
   'pull_request' && needs.closures.result == 'failure' && …head.repo.full_name ==
   github.repository`, so the bot `ci-autofix.md` names as the repair for `INERT
   READS` cannot fire on the only event where an on-`main` staleness shows. Measured
   on the 10-08 schedule run `37753990323`: job **`113252338415` `closures-autofix`
   -> `skipped`** while `closures` failed beside it (`jobs_1008.txt`). The repair that
   day was therefore two hand edits to the committed table, both in the tree:
   `b416093e9` "fix: inert_reads entry for git_auto_maintenance_race.sh (main
   closures red after #2051)" and `387128bb3` "closures: list the new harness among
   harness_headers.py's inert reads". The sanctioned re-derivation is Linux-only
   (`strace` records the inert dimension; the diagnosing seat dates the container
   lane's removal to 2026-10-04, not re-measured here). Same shape as this RCA:
   **a check that only runs where its repair cannot.**
2. **`record-autofix` -- the class member stands, the named defect does not
   (correction).** The diagnosing seat's §3.2 reported that its job "has **no
   `if:`**". It has one, at both the head that seat measured (`83f7ca558`) and this
   one: `!cancelled() && github.ref == 'refs/heads/main' && (github.event_name ==
   'push' || github.event_name == 'schedule' || github.event_name ==
   'workflow_dispatch')`. So it is main-scoped **by design** and deliberately admits
   `schedule` and `push`; what it does there is PR-shaped work (it opens the record
   pull request), and that is what reddened three nights -- `HTTP 401` (10-05),
   `HTTP 422` (10-06), `Process completed with exit code 128` followed by `the
   record step did not run; a beat owed cannot be distinguished from one skipped`
   (10-07), each read off its own job log (`record_autofix_nights.txt`). The honest
   finding is narrower than "a missing condition": a lane whose work presupposes an
   event it is scheduled on, whose three refusals are three different faults (a
   credential, a request body, a git exit) rather than one cause. Not this PR's to
   fix, and nothing in the tree carries it: `record-autofix`'s three live rows are
   about other properties of the same job -- #1957 its writer identity (the
   delivery-row beat as the `hpo-author` App), #1962 its transport (head/base, its
   own branch under lease, self-reported API failures), #1974 its lookup of the open
   record PR by `head=<owner>:record/autofix` (each title read at this head, all
   three closed). None is about the event it runs on.
3. **The bound reaches the pull-request gate too.** `driver_timeout` is shared by
   every scope, and a driver with **no** recorded entry gets the bare 1200 s floor in
   any scope, so the 10-03/04/05 rows above were armed on a pull request whenever the
   draw put that driver in play. Sampled rather than enumerated: the two PR-gate
   `mutation` reds on 2026-10-09 were different causes (an unpinned-count refusal and
   a ledger/inventory disagreement -- the diagnosing seat's jobs `113703687732`,
   `113615566185`, not re-sampled here). On this PR's own round-1 head the lane
   exercised no bound at all: the review read job `113815002602` as `MUTATION TABLE
   -- scope changed: no production code line added or modified against the base` /
   `MUTATION TABLE PASSED (empty scope)`, with the unpinned count identical at both
   ends -- so the empty scope is "none was evaluated", not "no mutant survived".
4. **`mutation-ledger-push`'s success gate is the trap that shaped §5's carrier.**
   Re-read at this head: `… && needs.mutation-ledger.result == 'success'`, so the one
   job holding a `main` writer does not run on exactly the nights the measurement is
   needed. §5 item 3 records the choice that follows.
5. **Not reached.** `slow` (`timeout-minutes: 150`) and `nightly-ha`
   (`timeout-minutes: 45`) never call `driver_timeout` -- neither job's YAML mentions
   it or `mutation_table.py` -- so they are exposed to their job timeout alone.
   `delivery-status` reads delivery rows, not run metadata: `governance.yml` contains
   no `actions/runs` reference at all, so a stranded scheduled conclusion cannot reach
   it. The two reporters of `main`'s state read different inputs and neither reads the
   other's, which is why one green reporter never implies the other.
6. **The reporter's remedy is obtainable but expensive.** `nightly_status.py`'s
   `OWED_WHEN_RED` (line 206) sends its reader to `gh workflow run tests.yml --ref
   main`, and the same file refuses a dispatch whose branch is not the default (line
   547: `run.get("head_branch") != default_branch`), so a branch dispatch -- the
   shorter path a seat naturally takes -- can never turn the reporter green. Not a
   mis-instruction (a dispatch is legitimate to test one's own branch); it is the
   remedy's cost, 45-70 min per attempt, and the reason a red nightly stays visible
   for a working day.


## 3. Process state: **(c)**, with a **(d)** arm

`(c) -- the process was followed and did not produce the intended result.` Every
safeguard was present and obeyed, and each was wrong for this precondition:
`TIMEOUT_SCALE = 3` with its comment naming the earlier failure it repaired
(`features.py` 95 s -> 833 s against a 1200 s limit, R9-F10.12); `SECONDS_BAND =
2.0` with tvofi's 2026-10-08 reason ("Recordings of one script vary 0.3x-3.4x run
to run … 60 of 72 rewrites over 21 merges were inside 2x"; "keep SECONDS_BAND
below TIMEOUT_SCALE"); `EXCLUSIVE` + `deferred_drivers()`. The scaling rule was
sound for the precondition it was written under -- one serial sweep, a script's
cost drifting slowly -- and the lane judged its own bound while the suite was
green: on 10-08 `fast` ran `boost_drift_replay.py` green at 800.2 s
(`recorded: {seconds: 800.2, rc: 0}`) while the pool's bound for the same script
was 2401 s and its pool cost exceeded it.

The `(d)` arm inside it: the precondition changed underneath the rule -- from a
serial sweep to a 3-worker pool whose cost factor this document measures at
0.47x-3.27x the solo recording (§2), plus a band that keeps a value up to 2x
stale by design. For `(d)`, `defect-root-cause.md`: "the countermeasure is rarely
a new rule: it is making the process notice its own precondition change." That is
the form taken below -- the lane persists the pool cost it measures and bounds by
it, so a precondition change moves the bound.

Not `(a)`: both the reporter (`nightly_status.py`, `delivery-status`) and the
registry entry (`RCA-1565-mutation-timeouts`) existed. Not `(b)`: repairs landed
the same day each red appeared (`b416093e9`, `74689d11d`, `387128bb3`, all
2026-10-08); the instruction was obeyed.

**`baseline_refusal`'s own docstring was the check that should have caught it, and
was itself wrong.** It claimed "a red here is `fast`'s red restated" and printed
"Fix the suite first" -- false for a *timeout*, which no cheaper check measures,
while the same head's committed entry said `rc: 0`.

## 4. Cost test (wall-clock, per occurrence, over this release cycle)

**cost(the red nightly, recurring).** Two figures, kept apart because they price
different things. **The bound arm this PR fixes fired on 2 of the 6 red nights
(10-07, 10-08) = P(recurrence) 0.33/night.** The bound *and* its `EXCLUSIVE`
null-control sibling together fired on 4 of the 6 (10-03, 10-04, 10-07, 10-08) =
0.67/night, and the registry lists the family as a *recurring lane* defect -- but
(iv) below is the sibling's price and is the owner's, so the figure this PR's
countermeasure is tested against is 0.33/night. Voided lane work per night the
bound trips, from each job's own start/stop stamps (`gh api
…/actions/jobs/<id>`): 10-07 `mutation-nightly` 08:44:55->09:48:18Z = **63.4 min**
and `mutation-ledger` 08:44:54->09:49:08Z = **64.2 min** (127.6 min); 10-08
`mutation-nightly` 09:03:24->10:15:50Z = **72.4 min** -- verdicts thrown away by
`baseline_refusal` / `null_control_refusal` in the nightly's most expensive lane.
The diagnosing seat measured, over the one day it queried exhaustively, 14 of 24
pull-request `tests.yml` runs concluding `failure` on `nightly-status` alone
(515 CI-min, mean 36.8 min; `/Users/timmalmstrom/hpo-seats/rca-nightly-red/logs/pr_only_nightly.txt`
-- **that seat's measurement, not re-taken here**), i.e. ~84 PR runs and ~3090
CI-min carrying an unrelated red over six nights.

Time-to-notice is bounded by the cron's dispatch delay, not by the fix. **Rule and
enumerator** (`enum_figures.txt`): `tests.yml:119` declares `cron: "17 2 * * *"`
(02:17Z), so the delay is each run's `created_at` minus 02:17Z, over
`gh api "repos/tvofi/heatpump_optimizer/actions/workflows/tests.yml/runs?event=schedule&per_page=12"
--jq '.workflow_runs[] | [.id,.created_at,.conclusion] | @tsv'`. Across those twelve
runs the delay is **5 h 54 m to 6 h 53 m** (min run `37108891698` 2026-10-03T08:11:57Z,
max run `37909555545` 2026-10-09T09:10:23Z); the diagnosing seat's narrower
"6 h 19 m - 6 h 53 m" was the same rule over four runs. A repair merged at 15:59Z
on 10-08 therefore could not be *seen* in the nightly before ~09:00Z on 10-09
unless somebody paid for a `--ref main` dispatch (45-70 min).

**cost(countermeasure, recurring).** (i) The verdict wording adds **0 s** -- one
more printed line on the night it fires. (ii) Persisting the pool measurement is a
file write plus one `actions/cache` save/restore pair per nightly lane: the cache
backend is the same one the drift-baseline already uses, and the save is seconds
against a 60-72 min lane. (iii) Bounding by `max(solo, pool)` adds **0 s to a
healthy run** -- the bound only changes what happens when a run exceeds it, and
the lane is already capped by `--budget-minutes 270` and `timeout-minutes: 330`.
Worst case, a genuinely hung driver is waited out longer, inside a budget the job
already enforces.

The test clears on the figures re-measured here alone, without the diagnosing
seat's PR-run number: 127.6 min of voided lane work on 10-07 and 72.4 min on 10-08
(200 min over the two nights the bound arm fired) against a standing cost of 0 s on
a healthy run plus seconds of cache traffic -- and P(recurrence) 0.33/night for the
arm this PR fixes. Adding the seat's 51 CI-min/day of unusable PR verdicts widens
the margin by an order of magnitude but is not what the conclusion rests on.

**(iv) Not built, routed to the owner.** Honouring `EXCLUSIVE` under `--scope full`
(deferring `harness_headers.py` and `stress.py` to run alone) is the *other* arm --
the null-control "kills" of 10-03/10-04 -- and costs **+641 s (10.7 min) per
nightly lane, ~21 min/night** (Oct-8 pool baselines 211 s + 430 s, x2 lanes).
`tests/mutation_table.py` states "Dropping the pair is an unpinned-count raise",
which is `budget-raise-gate` (decision 0013), the owner's approving review, not a
seat's. Out of scope here; the honest recommendation is to ask, not build.

## 5. Countermeasure (landed in this pull request)

All of it is `tests/` code plus one workflow carrier; no policy file, no new lint
class, no budget raised, and `SECONDS_BAND` is **not** re-tuned (tvofi set it
2026-10-08 for merge-text hygiene -- a different concern; decoupling the *bound*
from the *band* is the fix).

1. **`baseline_refusal` names a timeout as a timeout** (`tests/mutation_table.py`).
   A baseline whose only fault is `rc = TIMEOUT_RC` is reported separately from a
   failing check: it prints the bound tripped, the committed solo recording and its
   `rc`, the factor, and -- when the committed entry says `rc: 0` -- "the recording
   is STALE, not the suite", with the re-record remedy. It no longer says "Fix the
   suite first" for a timeout, and the docstring's "a red here is `fast`'s red
   restated" is qualified: true for a failing check, false for a timeout.
2. **The bound covers the measured pool cost** (`seed_pool_seconds`). `main()` now
   seeds each driver's basis as `max(committed solo recording, last measured pool
   cost)`, so `driver_timeout` yields the RCA's `max(floor, ceil(TIMEOUT_SCALE x
   max(recorded, pool_recorded)))`. Decoupled from `SECONDS_BAND`; a driver with no
   pool measurement keeps its solo recording, so a bound never shrinks.
3. **The pool measurement persists** (`pool_seconds` / `write_pool_seconds`, and a
   `.github/workflows/tests.yml` carrier). `main()`'s `finally` writes the measured
   pool cost -- prior seed merged with this run's -- into the `--drain` directory,
   so it survives even the night the lane refuses on its own bound. Both nightly
   lanes restore the prior measurement from `actions/cache` and pass it as
   `--pool-seconds`; `mutation-ledger` saves the fresh one with `if: always()`.

   **Why the cache and not the natural carrier.** The RCA named `mutation-ledger-push`
   as the writer on `main` and flagged the trap: that job is gated
   `needs.mutation-ledger.result == 'success'`, so on exactly the nights the
   measurement is needed it does not run. Pushing through it would also widen the
   `hpo-ledger` App's write-set, which decision 0011 pins to "new files under
   `tests/mutation_ledger/killed_by/` and nothing else" -- a policy change this
   seat does not own. `actions/cache` is the RCA's named alternative ("or the lane's
   artifact"), is already pinned in this workflow (the drift-baseline), needs **no
   write grant and no secret** (so the measuring job keeps decision 0011's
   invariant), and adds **no** job to the four that override the read-only floor.
   The save rides `mutation-ledger` itself, which runs on the schedule whatever the
   drive concluded, with `if: always()`.

   **Named limitation, and why the obvious fix was not taken.** A baseline that
   *times out* contributes no `measured_pool` entry (the write is inside the
   pre-existing `if not run.timed_out`), so on a **cold cache** a driver whose pool
   cost already exceeds `3 x` its solo recording forwards the prior seed unchanged
   instead of learning the bound it just proved too small; that driver needs a human
   or CI re-record, which the new refusal text names. This is not a regression -- the
   seeded bound is `>=` the unseeded one for every driver at every head, since
   `max(solo, pool) >= solo` and `driver_timeout` is monotonic -- and it is the form
   the diagnosing seat's §5 item 2 prescribed. Recording the *bound* a timeout hit as
   if it were a measurement would self-heal that case in one night, and was rejected:
   a hang and a merely slower driver are indistinguishable from `run_script` (its own
   comment, R9-F10.12), so a genuinely hung driver would ratchet its bound by
   `TIMEOUT_SCALE` every night without limit and eat the lane's `--budget-minutes 270`
   -- trading a one-night under-bound for an unbounded cost. A censored value is a
   floor on the truth, not a measurement, and the tree already refuses to treat one as
   a measurement.

## 6. Null control (re-taken at this merge base)

The fix keys on "bound below the cost the lane itself measured", so a driver whose
recording is honest is untouched and nothing is skipped to reach green. Committed
solo seconds via the tree's own `recorded_seconds()` at `b2b6acd64`; pool costs are
the CI-measured values (job `113233890923`). `tests/entities.py` drives all five as
a check ("RCA-1565 null control"): for `features.py` (solo 730.5, pool 772),
`stress.py` (760.6, 434), `entities.py` (259.6, 142), `env_drift.py` (0.9 stub, 524)
and `harness_headers.py` (199.0, 211), the seeded bound still covers the pool cost,
the seed never lowers a bound (`max(solo, pool) >= solo` and `driver_timeout` is
monotonic), and `env_drift.py` stays **floor**-bound at 1200 rather than scaled --
the fix reads flat on it, which is the point. A second null control pins the
wording: a real red baseline (a failing check, not a timeout) still says "Fix the
suite first" and names the check.

## 7. Figures (the command that printed each)

- **Six consecutive red scheduled runs; last green `36984959667`; the streak ended
  on `37909555545` (10-09, `success`).**
  `gh api "repos/tvofi/heatpump_optimizer/actions/workflows/tests.yml/runs?event=schedule&per_page=12"
  --jq '.workflow_runs[] | [.id,.head_sha[0:9],.created_at,.conclusion,.status]|@tsv'`
  (`schedule_created.txt`).
- **The per-night arm attribution (the opening table).** `gh api
  "repos/tvofi/heatpump_optimizer/actions/runs/<run>/jobs?per_page=100"
  --jq '.jobs[] | select(.conclusion=="failure") | [.id,.name,.conclusion]|@tsv'`
  for runs `37108891698 37189092011 37288195257 37440269774 37595831734`
  (`red_jobs_1003_1007.txt`) and, without the `select`, `37753990323`
  (`jobs_1008.txt`, which is also where `closures-autofix -> skipped` is read).
- **CI's own refusal text per night.** `gh api
  repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs --allow-escape-sequences`,
  ANSI-stripped: `111162760555` (10-03 `harness_headers.py … rc=-24`),
  `111397325352` (10-04 `stress.py … 8.0x … budget 7.9x`), `111692063912` (10-05
  `HTTP 401`), `112192034609` (10-06 `HTTP 422`), `112708108856` (10-07
  `exit code 128`), `112708109605` / `113233890923` (`timed out after 1576s` /
  `2401s`), `112708109541` (the 1573 s completed run). The three record-lane logs
  are grepped into `record_autofix_nights.txt`.
- **The reproduced bounds (1200 / 1576 / 2401 / 4469).** `bounds_reproduction.txt`:
  `git show <head>:tests/closures.json` for each night's `boost_drift_replay.py`
  recording, through `mutation_table.driver_timeout(1200, seconds)`.
- **The pool/solo factor table, and the 0.47-3.27 range with its exclusion rule.**
  `pool_tables.txt` prints every driver row; `enum_factor_rule.txt` prints the
  range under the rule §2 states (exclude the `env_drift.py` stub and any solo
  recording under the log's 1-second resolution), 51 rows over the three logs, each
  end named with its driver and its two inputs.
- **The cron-to-dispatch delay (5 h 54 m - 6 h 53 m over twelve runs).**
  `enum_figures.txt` part (2): `created_at` from the runs query above minus the
  `02:17Z` that `tests.yml:119`'s `cron: "17 2 * * *"` declares, printed per run.
- **Voided lane work (63.4 / 64.2 / 72.4 min).** `gh api
  repos/tvofi/heatpump_optimizer/actions/jobs/<id> --jq '[.started_at,.completed_at]|@tsv'`
  for `112708109605`, `112708109541`, `113233890923`.
- **The job conditions §2b quotes** (`record-autofix`, `closures-autofix`,
  `mutation-ledger-push`). Parsed from this head's own YAML, not from a comment:
  read each job's block up to `steps:` and take its `if:` -- the same derivation
  `tests/entities.py`'s `_gh_if` uses. `record-autofix`'s is
  `!cancelled() && github.ref == 'refs/heads/main' && (push || schedule ||
  workflow_dispatch)`, which is the correction to the diagnosing seat's "no `if:`";
  `git show 83f7ca558:.github/workflows/tests.yml` prints the same block, so the
  claim was already stale at the head that seat measured.
- **Failing arm, surgical mutations, green arm.**
  `PYTHONPATH=tests/hastub python tests/entities.py`, the five checks named
  "RCA-1565 …": with the merge-base `tests/mutation_table.py`,
  `entities_FAILINGARM.txt` = "3 of 2239 ENTITY CHECKS FAILED" (both null controls
  green); with `seed_pool_seconds`'s fold neutered, `entities_MUTA.txt` = "1 of
  2239"; with `baseline_refusal`'s timeout arm neutered, `entities_MUTB.txt` =
  "1 of 2239"; with the fix, `entities_FINAL.txt` = "ALL 2239 ENTITY CHECKS
  PASSED".
- **`fold_ledger.py check` clean at both ends.** `python3 -I
  tools/audit/fold_ledger.py check` at `b2b6acd64` and at this head: "28 classes,
  549 instances, 39 in-tree judge survivors, 101 rca entries / 0 violation(s)".

The two enumerators (`enum_factor_rule.txt`, `enum_figures.txt`) are one-off probes
over the eight job logs named above and stay in the seat's scratch, which
`fixer.md` step 18 permits; what a later seat reruns is in the tree -- the
`entities.py` checks named "RCA-1565 …", which drive `mutation_table`'s own
functions, and the `gh api` / `git show` commands above, which need no probe. Each
figure's rule is stated beside it so the number is re-derivable without the probe:
the factor range's rule is §2's two exclusions, the delay's is `created_at` minus
the `02:17Z` that `tests.yml:119` declares.

