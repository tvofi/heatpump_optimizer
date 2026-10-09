# RCA-1565: the nightly mutation lanes bound each driver below the pool factor they measure

The countermeasure seat for `bugclasses.json`'s `RCA-1565-mutation-timeouts`
("CI mutation job 90-minute timeouts", `status: partial`, its `process_state`
and `cost_test` owed). It lands the two missing parts and the fix, and ran
beside the fix, not inside it (`dev/governance/rules/defect-root-cause.md`).

- Base measured: `origin/main` at `b2b6acd64` (2026-10-09). Every bound below is
  re-derived there with the tree's own `driver_timeout`, not carried from the
  diagnosing seat.
- Evidence: `/Users/timmalmstrom/hpo-seats/fix-nightly-bound/logs/`
  (`bounds_reproduction.txt`, `pool_tables.txt`, the three CI job logs
  `job-11270810960{5,41}.log` / `job-113233890923.log`, and the `entities.py`
  failing/green arms). GitHub reads against `tvofi/heatpump_optimizer`.

**The defect in one sentence.** The nightly mutation lanes bound every driver's
first run by `max(--timeout floor 1200 s, TIMEOUT_SCALE 3 x that driver's
*solo-gate* recorded seconds)`, while the lane drives the same script inside a
3-worker pool at 1.3-3.3x that recording; `closure.SECONDS_BAND = 2.0`
deliberately keeps a committed value up to 2x below the cost CI last measured,
so the surviving headroom is `TIMEOUT_SCALE / SECONDS_BAND = 1.5x` against a pool
factor the tree's own comment states reaches 3.4x. This reddened four of the six
consecutive scheduled runs from 2026-10-03 to 2026-10-08 (last green
`36984959667`, 2026-10-02T08:36:04Z).

## 1. The mechanism, reproduced from the committed table

`tests/mutation_table.py`'s `driver_timeout(floor, seconds)` is
`max(floor, ceil(TIMEOUT_SCALE x seconds))`, and `main()` seeds `seconds` from
`recorded_seconds()` -- the solo-gate recording in `tests/closures.json` -- for a
driver's first (baseline) run. Deriving that at each red night's head with the
tree's own function (`bounds_reproduction.txt`) reproduces, to the second, the
timeout CI printed:

| scheduled run | head | `boost_drift_replay.py` recording | derived bound | CI printed |
|---|---|---|---|---|
| 10-03 `37108891698` | `2e569748a` | absent (`None`) | `1200` (the floor) | pool cost >= 1573 s |
| 10-04 `37189092011` | `fb11a0172` | absent | `1200` | " |
| 10-05 `37288195257` | `a1da8d381` | absent | `1200` | " |
| 10-07 `37595831734` | `be0cb8213` | `{seconds: 525.3, rc: 0}` | `1576` | `timed out after 1576s` (job `112708109605`) |
| 10-08 `37753990323` | `816547efe` | `{seconds: 800.2, rc: 0}` | `2401` | `timed out after 2401s` (job `113233890923`) |

The bound the committed table implies **equals the timeout the lane printed**, so
the mechanism is shown to produce the observed failure, not asserted. On 10-07 the
same script's baseline completed in the sibling `mutation-ledger` lane at **1573 s
against the 1576 s bound -- three seconds of margin** (job `112708109541`); the
next night the pool cost exceeded 2401 s and died. At this merge base the
recording has been re-recorded to 1489.6, giving a bound of **4469 s** -- the
number moved, the mechanism did not: 4469 clears the largest pool cost measured
for that driver in the window (1573 s) by 2.8x only because a human/bot happened
to re-record it high.

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

The honest factors run 0.47-3.27 (`structure.py` reached 3.27 on 10-07);
`env_drift.py`'s apparent 500-800x is the declared stub recording (0.6-0.9 s,
`closure.py` #934), whose real cost is the `--all` run -- it is protected by the
**floor**, not the scale, and is excluded from the factor range. Only
`boost_drift_replay.py` sat above the floor with a factor at the scale, which is
why it is the driver that reddened.

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
serial sweep to a 3-worker pool whose cost factor is 1.3-3.3x the solo recording,
plus a band that keeps a value up to 2x stale by design. For `(d)`,
`defect-root-cause.md`: "the countermeasure is rarely a new rule: it is making the
process notice its own precondition change." That is the form taken below -- the
lane persists the pool cost it measures and bounds by it, so a precondition change
moves the bound.

Not `(a)`: both the reporter (`nightly_status.py`, `delivery-status`) and the
registry entry (`RCA-1565-mutation-timeouts`) existed. Not `(b)`: repairs landed
the same day each red appeared (`b416093e9`, `74689d11d`, `387128bb3`, all
2026-10-08); the instruction was obeyed.

**`baseline_refusal`'s own docstring was the check that should have caught it, and
was itself wrong.** It claimed "a red here is `fast`'s red restated" and printed
"Fix the suite first" -- false for a *timeout*, which no cheaper check measures,
while the same head's committed entry said `rc: 0`.

## 4. Cost test (wall-clock, per occurrence, over this release cycle)

**cost(the red nightly, recurring).** The bound/null-control mechanism fired on 4
of the 6 red nights (10-03, 10-04, 10-07, 10-08) = **P(recurrence) 0.67/night**,
and the registry already lists it as a *recurring lane* defect. Voided lane work
per night the bound trips, from each job's own start/stop stamps (`gh api
…/actions/jobs/<id>`): 10-07 `mutation-nightly` 08:44:55->09:48:18Z = **63.4 min**
and `mutation-ledger` 08:44:54->09:49:08Z = **64.2 min** (127.6 min); 10-08
`mutation-nightly` 09:03:24->10:15:50Z = **72.4 min** -- verdicts thrown away by
`baseline_refusal` / `null_control_refusal` in the nightly's most expensive lane.
The diagnosing seat measured, over the one day it queried exhaustively, 14 of 24
pull-request `tests.yml` runs concluding `failure` on `nightly-status` alone
(515 CI-min, mean 36.8 min; `/Users/timmalmstrom/hpo-seats/rca-nightly-red/logs/pr_only_nightly.txt`),
i.e. ~84 PR runs and ~3090 CI-min carrying an unrelated red over six nights.
Time-to-notice is bounded by the cron's measured 6 h 19 m - 6 h 53 m dispatch
delay, not by the fix.

**cost(countermeasure, recurring).** (i) The verdict wording adds **0 s** -- one
more printed line on the night it fires. (ii) Persisting the pool measurement is a
file write plus one `actions/cache` save/restore pair per nightly lane: the cache
backend is the same one the drift-baseline already uses, and the save is seconds
against a 60-72 min lane. (iii) Bounding by `max(solo, pool)` adds **0 s to a
healthy run** -- the bound only changes what happens when a run exceeds it, and
the lane is already capped by `--budget-minutes 270` and `timeout-minutes: 330`.
Worst case, a genuinely hung driver is waited out longer, inside a budget the job
already enforces. Against 51 CI-min/day of unusable PR verdicts and 72-128 min of
voided lane work per night, (i)+(ii)+(iii) clear the test by orders of magnitude.

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

- **Six consecutive red scheduled runs; last green `36984959667`.**
  `gh api "repos/tvofi/heatpump_optimizer/actions/workflows/tests.yml/runs?event=schedule&per_page=12"
  --jq '.workflow_runs[] | [.id,.head_sha[0:9],.created_at,.conclusion,.status]|@tsv'`.
- **The reproduced bounds (1200 / 1576 / 2401 / 4469).** `bounds_reproduction.txt`:
  `git show <head>:tests/closures.json` for each night's `boost_drift_replay.py`
  recording, through `mutation_table.driver_timeout(1200, seconds)`.
- **The pool/solo factor table.** `pool_tables.txt`: each job's `baseline <script>:
  … <N>s` lines (`gh api …/actions/jobs/<id>/logs`, ANSI-stripped) against
  `git show <head>:tests/closures.json`, factor = pool / solo.
- **CI's printed timeouts (1576 / 2401) and the 1573 s completed run.**
  `job-112708109605.log`, `job-113233890923.log`, `job-112708109541.log`.
- **Voided lane work (63.4 / 64.2 / 72.4 min).** `gh api
  repos/tvofi/heatpump_optimizer/actions/jobs/<id> --jq '[.started_at,.completed_at]|@tsv'`
  for `112708109605`, `112708109541`, `113233890923`.
- **Failing arm (3 checks red) and green arm (all pass).**
  `PYTHONPATH=tests/hastub python tests/entities.py` with the merge-base
  `tests/mutation_table.py` (`entities_FAILINGARM.txt`: "3 of 2239 ENTITY CHECKS
  FAILED") and with the fix (`entities_GREENARM.txt`: "ALL 2239 ENTITY CHECKS
  PASSED"); the five checks are named "RCA-1565 …".
- **`fold_ledger.py check` clean.** `python3 -I tools/audit/fold_ledger.py check`.
