# R10-RCA-CI-CRITPATH-3: a timed gate graded which host class the runs drew

The root-cause seat for the third `GREW critical_path_minutes` on `main`, extended to the
fourth. It ran beside the fixers of `r10-hotfix-ci-critpath-3` and `-4` and not inside them
(`dev/governance/roles/root-cause.md`), and touches none of their files. Every time below is
UTC. The replay is `dev/audit/harnesses/r10_rca_ci_critpath_3/replay.py`, offline, under a
second. It grades each red with `tests/ci_ratchet.py` as of the red commit itself
(`git show <sha>:tests/ci_ratchet.py`, imported by spec), never the live file. Its fixtures,
beside it, were read from the Actions API:

- `runs.json` (11-04 05:20): 31 completed `ci.yml` push runs on `main`, numbered 3775..4056,
  with their jobs. `run_minutes` grades 29 of them; two return None. The fixture omits the
  cancelled runs 3770–3772 and 4036–4045.
- `runs_red4.json` (11-04 14:00): every `ci.yml` push run on `main` numbered 4009..4128,
  with the cancelled ones, which is the fourth red's 16-run window and the one before it.
- `ci_logs.json` (11-04 14:10): the `lane plan:` lines of two closures jobs, the per-script
  seconds of three `tests / fast (3.14)` jobs, and the runner image of every successful
  closures and fast (3.14) job in runs 3770..4128.

**Defect, third red.** `tests / ci-ratchet` on `8f286293b` (run 41397326281, job
125133539981, 06:40:46) printed `GREW critical_path_minutes: 36.5 (budget 34.267, band 1.3)`.
Every later push to `main` read the same verdict through `c3a279e32`. The merge was
`#3162`, seven delivery-row `.md` files, and cannot move CI work. Neither could the two
earlier reds: `05c0d6d5d` (seven delivery rows) and `f3ffb1c63`, whose own fix says that
"no merge grew the work".

**Defect, fourth red.** After `#3180` replaced the statistic, `tests / ci-ratchet` on
`8e90d8144` (run 41818271680, job 126550827525, 11:44:11) printed
`GREW critical_path_minutes: 29.067 (budget 21.983, band 1.3)`. The merge was `#3182`. Its
diff adds one entry to `tests/closures.json`, and the planned path is unchanged by it
(replay step 6). Replay steps 4 and 5 show that the grade moved with the host draw, not with
the work. Section 2b covers it.

## 1. Cause, reproduced

- **The grade reproduces exactly.** Replay step 1 grades the window `ci-ratchet` read at
  `8f286293b`: the 7 runs before it plus its own run, still in progress. It uses that
  commit's `run_minutes` and `critical_path_minutes`. The result is 36.5, GREW against
  35.567.
- **The work did not move.** `python3 tests/closure.py lane-plan --all-scripts --lanes 3`
  reads `tests/closures.json`'s recorded seconds. Its longest lane is 1332.8 s at
  `9f800cdca` (10-25). It is 1345.7 s at `b8a027974` (10-31), at `c7aa12165` (the last
  green), at `c3a279e32` (the last red-3 push) and at `8e90d8144` (replay step 6). On CI the
  closures lane printed `lane plan: 3 lane(s) for 34 script(s), bound 3` with lane totals
  1345.6 / 1345.7 / 1345.6 s in two jobs (replay step 3, from `ci_logs.json`). One job took
  38.2 min (job 125121503116, run 3870). The other took 20.6 min (job 125653313138,
  run 4055). These totals are recorded seconds and read no clock. That they agree shows the
  plan was the same in both runs. It does not show how fast either host was.
- **The host slowed every script.** The closures job logs print no per-script seconds, so
  this is measured on the fast lane, whose logs do. Fast (3.14) job 125436393198 (run 4009,
  20.4 min) and job 126534731510 (run 4128, 33.4 min) ran the same 33 scripts with none
  added. Summed script time was 1824 s against 3137 s, ×1.72. Every one of the 14 scripts
  of at least 10 s was slower, by a ratio of 1.26..3.09 (replay step 5). For example,
  `features.py` took 359 s against 673 s, and `stress.py` 187 s against 367 s. Neither log
  prints a CPU model, so the host class has no name here. This per-script comparison
  crosses an image change: run 4009 ran image 20261025.179.1 and run 4128, the only
  fast (3.14) job on image 20261101.186.1, ran that one, so the ×1.72 exhibit is confounded
  with the image and by itself does not separate host from image. The claim that the image
  does not separate the classes rests on the wider set: the fast (3.14) jobs of runs
  3770..4116 all ran image 20261025.179.1, at 17.7..34.9 min, and run 4035 of that image
  took 27.3 min against run 4009's 20.4 min. No per-script log was kept for run 4035, so
  the same-image slow comparison is by job minutes only.
- **The lanes are bimodal, and the 8-run median flips with the mixture.** In the 29 graded
  runs of `runs.json`, `tests / closures` took either 18.6–29.3 min or 33.7–40.0 min.
  `tests / fast (3.14)` was split the same way, at about 18–25 and 30–35 min. Replay step 2
  counts slow closures draws among the runs the median actually reads. It finds 3 windows
  with under half slow (max median 33.767, ok) and 6 windows with over 70 % slow (min median
  39.667, GREW). The windows in between are mixed because the fast lane draws its host
  independently. From run 3865 (05:24 on 11-02) the slow class won most draws: 13 of the
  next 19 closures jobs were slow, against 5 of the 12 before. The median moved from the
  fast mode to the slow mode, and the work moved by zero.
- **What else the cause reaches.** `critical_path_minutes` is the only timing row in any
  `*_budgets.json`. That is still true at `8e90d8144`. The other rows of
  `tests/ci_budgets.json` are counts (`script_runs_*`, `archscore.*`).
  `orchestrator_tick.py:381` reads the same budget only to bound a WAITING line, and grades
  nothing. So the class stops at this one row, and it has hit that row four times.

| red | onset (push) | hotfix merged | red for | the hotfix's reading |
|---|---|---|---|---|
| 1 | `f3ffb1c63` 10-25 20:21 | `#2839` 10-26 00:58 | 4.6 h | runner queue, so grade work instead of wall |
| 2 | `05c0d6d5d` 10-31 10:43 | `#3045` 11-01 14:39 | 27.9 h | 8-run median spread, so a 1.3 band |
| 3 | `8f286293b` 11-02 06:01 | `#3180` 11-04 09:26 | 51.4 h | host draw, so price each job at its fastest of 16 runs |
| 4 | `8e90d8144` 11-04 11:03 | open (`r10-hotfix-ci-critpath-4` dispatched 11:46) | ≥ 2.9 h at 14:00 | — |

Red 3 ended under its own statistic before `#3180` merged. Run 4080 (`a9c2f90fc`, pushed
08:13) graded 35.1 against 35.567, because the median fell back with the draw. On that rule
the red lasted 50.2 h. The table keeps the rule the earlier rows use: onset to hotfix merged.

Each hotfix was correct about the symptom it was shown. The first three each left the gate
grading elapsed time on hosts the repository does not choose. Red 4 is that cause's next
instance.

## 2. Process state: (c) — followed, and it did not produce the intended result

The process is the ratchet's own calibration rule, as the red commit ran it
(`git show 8f286293b:tests/ci_ratchet.py`, lines 41–52 of the module docstring and the
`BAND_KEYS` comment at lines 106–111). It grades the 8-run median, records the p90 of a
wider window, and sizes the band "at the measured maximum |8-run median − window median|
over 145 runs, 1.3", "never padded". Hotfix 2 followed it to the digit. It reproduced the
p90 34.267 exactly and set the band at the measured 1.300.

It did not produce the intended result because the measure assumes unimodal noise around
the work. The lane timings are a two-class mixture. Under a mixture, a median's spread
measured in a sample where the slow class stays under half says nothing about a day when
it goes over half. The bimodality was already in the calibration-era data, so this is not
a precondition that changed underneath the process (d). Hotfix 1's own message says the
work was "flat at 20.1..34.65 min" over 40 runs. In this sample both modes appear before
the step: runs 3779–3838 hold both 21–25 and 34–39 min closures jobs. It is not (b), since
nothing was skipped. A firmer instruction would only repeat the calibration that was
followed.

## 2b. The fourth red: the same state, one statistic later

**#3180 followed the calibration rule too.** It recorded 21.983 as the largest of the 25
sixteen-run windows over 40 runs. It kept the band at 1.3 against a measured
window-to-window excess of 0.55 (its reason in `tests/ci_budgets.json` at `8e90d8144`). Its
statistic, `window_work_minutes`, prices each job at its fastest successful run among the
newest 16. That assumes every heavy job draws at least one fast host per 16 runs. The
module named the failure mode itself: "fifteen of sixteen runs drawing slow moves it as
growth would" (`git show 8e90d8144:tests/ci_ratchet.py`, the `window_work_minutes`
docstring at line 662).

**What the data show** (replay steps 4 and 5):

- The record's largest window priced fast (3.14) at 17.73 min. The window at `616868bdc`
  (runs 4009..4116) priced it at 20.38, on run 4009, and graded 22.367, which is ok. That
  matches the 22.367 the CI job printed there.
- One push later the window at `8e90d8144` (runs 4015..4128) had lost run 4009. Its 15
  successful fast (3.14) runs all took 27.3 min or more. The price became 27.33 (run 4035),
  and the chain `prelude` 0.37 + fast (3.14) 27.33 + `ci-ratchet` 1.37 reads 29.067, GREW.
  Nothing grew: replay step 5 shows the same 33 scripts, each slower on the slow draw.
- Run 4009 was the last fast-host draw of the fast lane. Fast (3.14) ran under 26 min in 14
  of 28 runs from 3770 to 4009, and in 0 of 16 after. In the same 16 runs the closures lane
  still drew under 27 min 7 times. If draws were independent at the earlier rate of 1 in 2,
  0 of 16 would have a probability of 0.5^16 ≈ 1.5 × 10⁻⁵. So the fast lane's draws are not
  independent from run to run. The runner image is the same throughout. What does correlate
  them is not in the logs.

**State: (c).** The rule was followed and the measure was still wrong for a mixture. The
40-run calibration sample never held a 16-run stretch without a fast fast-lane draw: the
newest recorded window still contained run 4009. So the sample could not price the case
the docstring named. The draw pattern did change after 4009, and one could read that as (d).
But the failure was predicted in the statistic's own text, and the calibration was the
process that should have tested it. The countermeasure is the same as in section 4: stop
grading elapsed time. It is not a fifth recalibration.

## 3. Cost test, re-taken at four occurrences

`cost(countermeasure, recurring) < cost(defect) × P(recurrence)`, in wall-clock.

- **P(recurrence)** is measured from the table: 4 onsets in 9.61 days (10-25 20:21 →
  11-04 11:03), which is 0.42 a day. The gaps were 5.6, 1.8 and 2.2 days, so the rate is
  not falling.
- **cost(defect)** has two parts. The first is red-main time: 4.6, 27.9 and 51.4 h for the
  closed reds, a mean of 28.0 h. With red 4 at its lower bound of 2.9 h the mean is
  ≥ 21.7 h. The second is three seats per occurrence: fixer, review and root-cause. The red
  also blinds the gate. 19 pull requests merged onto `main` while it was red on 11-02
  (06:41–21:10), and any real growth among them reads as the same GREW. Taking only the red
  time gives ≥ 21.7 h × 0.42 a day ≈ 9.0 h of red main a day.
- **cost(countermeasure, recurring)** is the planned critical path below. The whole replay,
  including a `lane-plan` subprocess and two git reads, takes 0.31 s here. The run count is
  rounded up to 300 a day: the run numbers moved 4056 − 3775 = 281 in the 28.6 h between
  those runs (11-01 23:46 → 11-03 04:23), about 236 a day. That makes about 90 s a day.

90 s a day against about 9.0 h a day: the test passes by more than two orders of magnitude.

## 4. Countermeasure — proposed, owner's decision, not landed

This changes what a ratchet row grades, and that is policy (CLAUDE.md rule 2). It also
touches `tests/ci_ratchet.py` and `tests/ci_budgets.json`, which the hotfix seats own. So it
is a draft for the owner, aimed at state (c): replace the measure, not the instruction.

**Grade the planned critical path, not elapsed minutes.** The new row is the longest lane of
`closure.lane_plan(--all-scripts, 3 lanes)` over `tests/closures.json`'s recorded seconds.
Today it reads 1345.7 s. `critical_path_minutes` would be kept as a printed observation that
does not gate, or as a nightly trend with a band sized to the mixture.

- **It reads no clock.** Its only input is the recorded-seconds table. CI printed the same
  lane totals in a 38.2-min and a 20.6-min closures job (replay step 3). Replay step 3's
  repeat is a determinism check only. It calls a pure function twice on one input, so it
  cannot fail and controls nothing about hosts.
- **It detects growth.** Add 300 s to `tests/stress.py`'s recorded seconds and the planned
  path goes 1345.7 → 1445.7 (replay step 3).
- **It is diff-attributable and runs at PR time.** The value moves only with a
  `tests/closures.json` change. That makes it a cheaper, earlier detector:
  `tools/pr/prepr.sh` could grade it in under a second. The timed row runs only on a push to
  `main` (`tests.yml:2265-2267`), so it can only ever go red after the merge.

**How it relates to what #3180 landed: complementary, not superseded.** `#3180` kept a timed
gate and made it narrower. It goes red only when a heavy job draws no fast host in 16 runs,
where the median went red when the slow class took half. Red 4 is exactly that case, 15 of
15. The draft removes the host from the grade instead.

- **Would it have prevented red 4?** As the gate, yes. The planned path read 1345.7 s at red
  3 and at red 4 (replay step 6), so nothing would have gone red.
- **Would it have caught growth there?** No. Red 4 was carried by the fast lane, and the
  draft grades only the closures lane (limitation 1 below). Had the fast lane really grown,
  the draft would have missed it, and the non-gating observation would have shown it.
- **What #3180 still adds beside it.** As that observation, a fastest-of-16 reading is a
  better trend than a median. A move in it is worth a look, but it must not gate.

What the draft does not cover, stated so nobody over-reads it:

1. **Only the closures lane.** The fast lane's work would need the same recorded-seconds
   table before it could join. Red 4 sat in that lane.
2. **The recordings lag real growth.** Recorded seconds change only when a branch
   re-records (`stable_seconds` smooths them). A script that slows without a re-record is
   invisible until one happens.
3. **Runner-level regressions.** A setup step growing, for example, never reaches the
   recordings. The timed observation is what would still show these.

If the owner refuses: the alternative is to keep a timed gate and size it from a sample that
holds the worst draw. Red 3's windows reach a median of 40.909 on unchanged work, 6.6 min
over that budget. Red 4's statistic read 7.08 over its record with the fast lane alone
mispriced by 9.6 min (27.33 against 17.73). A margin that wide would hide that much real
growth indefinitely. That trade is worse than grading the plan, and it is why this seat
does not propose it.

## 5. Why `main` sat red with no seat reacting (red 3)

Measured from git only. The counts below are over unique commits on every `origin` ref
fetched 11-04 14:05 (`git log --remotes --since … --until … --format='%H %s' | sort -u`),
matched by subject: ` dispatch:`, `roster_edit`, and
`state: … regenerated (state_docs.py)`. PR merges are first-parent `Merge pull request`
commits on `origin/main`. The tick board itself is stdout-only and was never persisted:
`heartbeat/orchestrator` holds one `TICK-PASS` in all its history, at 11-04 05:19. So this
seat cannot confirm from the record what any pass of the board printed.

| phase | interval | what the record shows |
|---|---|---|
| driving, main red | 11-02 06:40 → 21:06 (14.4 h) | 108 `dispatch:` commits (a dispatch writes two, as this seat's own did), 31 `roster_edit`, 19 PR merges onto red `main`; no dispatch for the red (the only ratchet-named dispatch is `fixer-r10-machinery-ratchets`, an unrelated group) |
| not driving | 11-02 21:06 → 11-04 05:13 (32.1 h) | no dispatch, roster edit or merge by any seat; only bot commits (`#3178` record merge 00:48, `ci: record nightly kills` 04:23) and `state_docs.py` regenerations about twice an hour (no gap over 2 h), run by a loop still alive |
| dispatch | 11-04 05:13 | `dispatch/fixer-r10-hotfix-ci-critpath-3` and this seat |

The brief's "about 25 h" runs from the last red push run (`c3a279e32`, concluded
11-03 04:58) to the dispatch, which is 24.3 h. Red to dispatch was 46.5 h in all.

- **The expedite rule existed.** `dev/governance/roles/nudge.md:105` says: "An expedite item
  (red main, quota exhaustion, outage, security) bypasses the caps, one at a time." In the
  driving phase it was not acted on, while about 54 other dispatches went out. Each one is a
  pair of commits.
- **The durable record cannot tell (b) from (c).** The only durable per-pass artifact is the
  state docs, regenerated 108 times between 11-01 18:00 and 11-04 07:00. They carry no
  main-red line: `FLOW-BOARD.md`'s `ci-red:N` counts pull requests in the blocked mix
  (8a867118f, 12:04 on 11-02; 41769608c, 12:30 on 11-03). The board line
  `REQUIRED not green … a red main admits nothing` (`orchestrator_tick.py:1393`) is printed
  with `flag=True` and goes nowhere else. There is no record of whether the driver saw it and
  went on (b) or never had it in front of them (c). This seat records the state as
  **undetermined between (b) and (c)**, not as (b).
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
- **Red 4 did not repeat this.** The GREW printed at 11:44:11, and
  `dispatch/fixer-r10-hotfix-ci-critpath-4` was committed at 11:46:27, 2 min later.

## 6. Also found: no root-cause record reached the first two reds

`grep -rn 'CRITPATH' dev/audit/rca` found nothing before this file. The delivery rows of
`#2839` and `#3045` record no cause or process state. The cause is a reach gap in the
enforcement. `defect-root-cause.md` enforces its second trigger at "a check that went red on
a commit in the branch", and the fix reviewer checks it. `tests / ci-ratchet` runs only on a
push to `main` (`tests.yml:2265-2267`), so it can never be red on a branch, and the enforced
trigger cannot reach any red from a push-only check. This document is that check's first
root-cause record. Whether the rule should name push-only checks is the owner's call.

## 7. What this record does not cover

- **Reds 1 and 2 are not re-measured.** Their onsets, hotfix merges and readings come from
  git and their hotfix messages, not from a fixture.
- **Why the fast lane stopped drawing fast hosts after run 4009.** The logs carry no CPU
  model, and the image is the same before and after. The record shows that the draws are
  correlated, not by what.
- **Red 4's end and its hotfix.** Both are the orchestrator's. When this was written
  (11-04 14:00) `main` was still red at `8e90d8144`. This record proposes nothing for that
  hotfix's code.
- **The planned path for the fast lane.** It does not exist yet (section 4, limitation 1).
- **Red 4's driving-phase behaviour.** Only its dispatch latency is measured; no section-5
  table is taken for it.

## Return

- **State:** (c) for reds 3 and 4: a calibration followed and a measure wrong for a
  two-class host mixture. For red 3's 14.4 h driving phase, undetermined between (b) and
  (c). For its 32.1 h undriven phase, a recorded refusal (cost ≈ 0).
- **Cost test:** passes at four occurrences. About 90 s a day standing against about 9.0 h a
  day of red main (P = 0.42 a day, mean red ≥ 21.7 h).
- **Countermeasures:** two drafts for the owner, neither landed. First, grade the planned
  closures critical path at PR time and keep elapsed minutes non-gating. This complements
  `#3180`, it is not superseded by it, and it would have kept red 4 off `main`. Second,
  `dispatch-gate` refuses non-expedite dispatches while `main`'s required checks are red.
- **Self-correction against the first draft of this record:** it gave the first three onsets
  as 8.4 days apart and P = 0.36 a day. They are 7.40 days apart: 10-25 20:21 → 11-02 06:01,
  with gaps of 5.6 and 1.8 days, not 6.6 and 1.8.
