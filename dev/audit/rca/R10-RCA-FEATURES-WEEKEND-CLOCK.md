# R10-RCA-FEATURES-WEEKEND-CLOCK: a features check whose verdict follows the runner's calendar day

Root-cause seat, run beside the hotfix and never inside it
(`dev/governance/roles/root-cause.md`). Base: `origin/main` at
`fdb526895c`, read 2026-11-14 01:20Z (a Saturday). The fix is
R10-HOTFIX-FEATURES-WEEKEND-CLOCK's; this seat does not touch
`tests/features.py`.

Trigger: the red-check trigger of `defect-root-cause.md`. `tests / fast (3.14)`,
a required check, went red on PR #3551 (job 132252007494, 00:08:11Z to
00:35:35Z) with one failure, `1 of 5571 FEATURE CHECKS FAILED`. The check was
"a charge-start dip that recovers is learned as neither a draw nor usage, and
a draw that does not recover keeps what main booked". The same check is red on
`main` and on every open head that runs `tests/features.py`. A cheaper detector
existed in shape (section 5), so the trigger applies.

## 1. Cause

`_chg_seq` in `tests/features.py`, about line 62313 at the base, builds its
sample sequence from the real clock:

    start = dt_util.now().replace(hour=start_hm[0], minute=start_hm[1], second=0)
    if saturday:
        start += timedelta(days=(5 - start.weekday()) % 7)

The `saturday=True` arm is moved onto a Saturday. The default arm is never moved,
so it runs on whatever day the runner's clock reads. The check (about line
62436) then asserts that the default arm teaches the **weekday** day type:

    and _chg_partial[3] == [1, 0] and _chg_partial_sat[3] == [0, 1]

On a Saturday or Sunday the default arm teaches the weekend type: `[0, 1]`,
read in the job's own FAIL line as "a 3 K settle drop recovering 1 K (0.457, 1,
[], [0, 1], True)". So the check passes Monday to Friday and fails Saturday and
Sunday on every head. Production is not wrong. The learner books the day type of
the sample's own date, which is what it should do.

Direction (`root-cause.md` s1). `git log -S"def _chg_seq"` shows that the helper
came in with `8fa60a926d` (2026-11-11). Its first form asserted nothing about
day type, so reading the real clock was harmless then. `b6696bd6e6`
(2026-11-11 10:01Z, "Pin the deferred usage's day type and the take-back's
save", PR #3444) added the `saturday` shift and the `[1, 0]` / `[0, 1]`
assertion in the same commit. The test is the side that moved. #3444 merged on
2026-11-12 at 09:54Z, a Thursday. The first weekend clock after that merge is
2026-11-14 at 00:00Z.

Reproduced at the base with a scratch probe that shifts the hastub live clock
(`homeassistant.util.dt.now` and `utcnow`, never a frozen value) onto a target
weekday. The probe then runs the block from `def _chg_seq(` to the next block
with `tools/audit/seat/features_block.py`:

| clock | block result |
|---|---|
| real (Sat 2026-11-14) | `1 of 3 FEATURES BLOCK FAILED`, the check above |
| shifted to Wed 2026-11-18 | `ALL 3 FEATURES BLOCK PASSED` |
| shifted to Sat 2026-11-14 | `1 of 3 FEATURES BLOCK FAILED` |
| shifted to Sun 2026-11-15 | `1 of 3 FEATURES BLOCK FAILED` |

The diagnosis seat's runs in `s14/seat/diag-3551/` agree: `run_main.txt` is
red and `run_main_wed.txt` is green.

### How the fixer, the reviewer and the PR's CI all passed it

- **Every run fell on a weekday.** #3444's verdicts are on `verdict/3444` and
  `review/3444`. They are dated 2026-11-11 09:13 and 15:51 (both `blocked`),
  2026-11-11 20:57 and 2026-11-12 04:01 (`merge`), all Wednesday and Thursday.
  Every CI run of the branch was on those two days too.
- **The fixer thought about day type, but on one side only.** The body's
  mutation table has `WEEKEND_GT` and `FLUSH_WEEKEND`, both KILLED, and it
  calls the `saturday` arm "the Saturday arm". The weekend arm was moved onto
  its day. The weekday arm's precondition, that the real clock reads a weekday,
  was never stated, so it was never moved. The mutants were killed on a weekday
  clock, where the precondition held.
- **No reviewer ran the check on a weekend clock or asked about one.** No
  `VERDICT.md` on either ref contains "weekday", "weekend", "Saturday" or
  "clock" in that sense (a grep over every commit of both refs). The body has
  no such line either.
- **No rule requires a test to pin the time.** A grep of `dev/governance/`,
  `tests/README.md` and `.claude/skills/` for "real clock", "freeze",
  "dt_util.now", "datetime.now", "date.today" and "weekday" returns no rule.
  The only place the convention is written is the hastub docstring:
  "``now``/``utcnow`` are overridable so tests can freeze the clock".

## 2. Process state: (c)

The class this defect belongs to already has a barrier. The barrier's unit did
not reach this axis. The class: **a suite check whose verdict depends on a
property of the host that the gate does not pin.** Section 3 counts three
instances in round 10. Its barrier is R10-SUITE-HOST-DETERMINISM (#3170,
2026-11-05; #3320, 2026-11-08), and it has two parts:

- the nightly step "Zone-sensitive scripts under Asia/Kolkata"
  (`.github/workflows/nightly.yml`, about line 508). It runs
  `tests/features.py` and `tests/finite_boundary.py` every night under a
  configured zone that is not UTC;
- `dev/audit/harnesses/host_zone_features.py --suite`, which runs by hand. A
  `Zone@YYYY-MM-DDTHH:MM:SS` zone also moves the process clock, but only under
  `faketime`. No lane passes that form, and `faketime` is not installed on this
  seat (`which faketime` prints nothing).

The nightly is scheduled at `37 0 * * *` (`nightly.yml` line 42). Between
#3444's merge (2026-11-12 09:54Z) and 2026-11-14 00:00Z, exactly one
scheduled run falls: 2026-11-13 00:37Z, a Friday in UTC and in Kolkata
(06:07). A weekday clock passes the check. Whether that run concluded green was
not read, because the API was rate-limited for this seat; on a weekday clock the
check passes, as section 1 shows. Its unit varies the **zone** and never the
**calendar day**. So the process existed, ran, and did
not produce its intended result for this axis. That is (c), not (a).
`root-cause.md` s2: an instance of a class that already has a barrier is not
(a) because its shape is new; "the countermeasure changes the unit". It is not
(b) either. No rule told the fixer to pin the day, and a firmer instruction
would not have helped. The fixer did handle the day type deliberately and still
missed the default arm's precondition.

## 3. Class reach

The class is a suite verdict that follows an unpinned property of the host.
Instances found in the log (`git log` over `tests/`, messages and diffs):

| when | round | property | instance | how found |
|---|---|---|---|---|
| 2026-09-24 | 9 | live clock (elapsed wall time) | two-zone heat-loss mass check, `c62d55f381` | CI flake under load |
| 2026-10-23 | 10 | runner CPU load | closure recording graded the harness's CPU headroom, R10-FLY-SUITE-ENV-FLAKES (`5576bcdbac`) | CI flakes |
| 2026-11-01 to 11-08 | 10 | configured zone | four features checks red under a non-UTC `HASTUB_TZ`, R10-SUITE-HOST-DETERMINISM (`3321273307`, #3170, #3320) | audit seat and review |
| 2026-11-14 | 10 | calendar day | this defect | required check red on every head |

**Three instances in round 10.** `defect-root-cause.md` says three in one
round owe a class-eliminating barrier and not a refusal. The class is not
registered in `bugclasses.json`. This document registers the RCA, not the class
(section 7).

The calendar-day axis alone has **1** instance. Where it can reach: the suite
holds 136 `dt_util.now()`, 11 `dt_util.utcnow()`, 47 `datetime.now(` and 9
`time.time()` reads across `tests/*.py`. Of these, 83, 2, 5 and 2 are in
`tests/features.py`, which also has 210 freeze sites (`grep -cE` at the base).
Production code that varies with the day type includes the DHW learner's
weekday and weekend day types, the away mode's weekend and holiday comfort
pairs (`82c6913c2d`) and the grid fee's weekday windows (D2 brief). So the axis
is live. A count of "reads" says nothing about which reads feed an assertion
that depends on the day, and so cannot replace running the suite on other days.

Measured on the other days of the week:
- Saturday: today's CI run on #3551 is the probe. 1 of 5571 checks failed, this
  one, and no other script in the job failed.
- Sunday: `tests/features.py` in full, with the probe's live clock shifted to
  Sun 2026-11-15: `15 of 5571 FEATURE CHECKS FAILED` (12 min 40 s locally).
  The control is the same wrapper shifted to Wed 2026-11-18:
  `14 of 5571 FEATURE CHECKS FAILED`. The two FAIL lists differ by exactly one
  line, this check. The other 14 are artifacts of the wrapper (section 5 item
  1), not of the day. So on Sunday, as on Saturday, this is the only check in
  `tests/features.py` that depends on the day.

## 4. Cost test

The unit is wall-clock time per occurrence. On the CI side it is runner minutes.

**Defect cost per occurrence**, from 2026-11-14T00:00Z until the hotfix merges:

- Every open head that runs `tests/features.py` is red on a required check.
  `gh pr list --state open` at about 01:26Z listed **30 open pull requests**. **8** of
  them are on the closure gating list: 3481, 3532, 3556, 3561, 3562, 3563,
  3564 and 3567. None of these can merge until the fix lands, and the closure
  date, 2026-11-15, is a Sunday inside this window.
- CI: each `fast` job takes 27.4 min (job 132252007494). Every head pushed in
  the window wastes one, and every open head reruns one after the fix: up to
  30 x 27.4 min = **13.7 runner-hours**, while the account's job cap is the
  bottleneck.
- The window lasts until the fix merges: at least 1.5 h already (measured to
  this writing), and 48 h if nothing had been done. Seat time on top of that:
  the diagnosis seat, the hotfix fixer and its reviewer, and this seat, about
  3 to 4 seat-hours (estimate).

**P(recurrence).** The calendar axis has 1 measured instance in round 10. The
broader class has 3 in round 10, measured in section 3. The estimate for the
calendar axis is about one per round. Its basis: 1 in round 10, while the
features that vary by day type grow each round (DHW day types and the away
mode's weekend pairs both landed in round 10).

**Candidates:**

| candidate | standing cost | detects this defect? | verdict |
|---|---|---|---|
| (i) a lint in the fast lane or pre-bash hook that refuses an unpinned `dt_util.now()`, `datetime.now()` or `date.today()` in tests unless marked | under 1 s a run, plus marking or baselining the 203 existing reads (136 + 11 + 47 + 9) once and judging every new one | **No.** The helper's author handled the day type on purpose and would have marked the read. The lint sees the read, not the precondition on the day that the assertion carries. | refused: it fails "a detector must be shown to detect" |
| (ii) `tests/features.py` a second time in the nightly lane under a faked Saturday | +532 s of runner time a night as a separate step | Yes, after merge. The 2026-11-13 00:37Z nightly would have gone red about 23.5 h before the first weekend gate red (00:08Z on 2026-11-14), and no PR head would have gone red. | sound in shape |
| (ii') the same, folded into the existing Asia/Kolkata step by running it under `faketime` on the **other** day type from the real day (Saturday on Monday to Friday nights, Wednesday on Saturday and Sunday nights) | about **10 to 20 s** a night for `apt-get install faketime` (estimate, not measured), no second `features.py` run | Yes, as (ii); demonstrated below | **recommended** |
| (iii) a session-wide frozen clock for `tests/features.py` | 0 s a run; a one-off edit through an 89,838-line file with 210 existing freeze sites and 83 live reads; it changes what every live-clock check measures | It hides the axis rather than detecting it, covers one of the suite's scripts, and a gate that always sees one day moves the red onto local seats on the other days | refused for round 10: its blast radius is larger than the defect and it is not a detector |
| (iv) both day types on every PR's `fast` run | +532 s on every `fast` run, hundreds of runs a round | Yes, before merge | refused: hundreds x 9 min against about 14 runner-hours once a round |

The calendar-axis barrier costs about 10 to 20 s a night as (ii') (an
estimate), or 532 s a night as (ii). The defect costs up to 13.7 runner-hours plus up to 48 h of stall on 8
gating PRs, about once a round. **Build (ii').** Its gap: a day-sensitive bug merged
between Friday's 00:37Z nightly and Saturday 00:00Z still reaches the weekend
gate. That is about 23 h in each week, against today's exposure of every
merge. A check that is right only on weekends is caught the same way by the
Saturday and Sunday nightlies, whose clocks move onto Wednesday.

## 5. Countermeasure, specified for a fixer (not built here)

It addresses state (c): it widens the barrier's unit from zone alone to zone
and calendar day.

1. **Move every clock in the process, not one.** A shift applied only to
   the stub's live `now()`/`utcnow()` is **refused, measured**: the full
   runs in section 3 fail 14 checks that have no dependence on the day. The
   same 14 fail under a Wednesday shift: humidity and mold floor, the inlet
   probe, boost store and R10-SAV-REASONS boost booking, `_bootstrap`, and the
   `HASTUB_TZ` subprocess suite. The harness stamps states with `datetime.now(UTC)`
   (`tests/harness.py` `minutes_ago`, line 606) while production reads
   `dt_util.now()`, so a shift of whole days in one clock reads as a stale
   sensor. Subprocesses (`dst_checks.py` under the `HASTUB_TZ` subprocess
   check) do not inherit an in-process patch at all. A shift therefore needs
   libfaketime, which moves `time.time`, `datetime.now` and `dt_util.now`
   together and is inherited by children. `host_zone_features.py` already has
   this form (`Zone@YYYY-MM-DDTHH:MM:SS`, `zone_cmd`, line 155), so this
   builds on an instrument already in the tree and adds none.
2. **The nightly step runs under it.** The Asia/Kolkata step installs
   `faketime` (`apt-get install -y faketime`) and runs its two scripts under
   `faketime "<date> 08:00:00"`. It picks the date on the **other** day type
   from today's (`date -u +%u`): the coming Saturday on Monday to Friday, the
   coming Wednesday on Saturday and Sunday. The step prints the day it ran on,
   so a red names its axis. A guard line run under the same wrapper fails the
   step unless `python3 -c` reads the target weekday through `datetime.now()`
   and through the stub's `dt_util.now()`. So a missing or ignored faketime
   cannot go green by skipping.
3. **The harness keeps it runnable by hand.** On Linux,
   `host_zone_features.py --suite` with an `Asia/Kolkata@<Saturday>` zone is
   the same run. On macOS `faketime` is not present (it is not on this seat).
   That is acceptable, because the lane is nightly on ubuntu.
4. **Demonstration owed** (`defect-root-cause.md`, "a detector must be shown
   to detect"). Run on ubuntu, under the step's own wrapper:
   - at a pre-hotfix base, for example `fdb526895c`, on a Saturday date:
     exactly this one check is red;
   - at the hotfix's merge on the same date: green;
   - null control: a Wednesday date is green at both, and the step with no
     wrapper is byte-identical to today's step;
   - the guard: with the wrapper removed, the guard fails.

   Prototype figures from this seat's in-process probe at the base, which is
   sound for this block because the block reads only the stub's clock: the
   block is red on Saturday and Sunday and green on Wednesday (section 1).
   With the default arm moved onto a Wednesday (a local edit, discarded,
   standing in for the hotfix), the block is green on Monday, Wednesday,
   Friday, Saturday and Sunday and on the real clock.
5. **It stays inside the ratchet**: no budget raise is expected.
   `nightly.yml` and the stub are non-production files.

**Owner group: R10-SUITE-ENV-RESIDUE**, a live group at stage `carries-open`.
Its seam is "where the suites run": the nightly heartbeat, the hastub and
cloud environments. Size S, as a carry. It is an instrument group, so under the
closure ruling it does not hold the stamp or the catalog PR. If that group
closes first, the carry goes to R11-INTAKE-R10-RESIDUE with this path. The
nightly step is R10-SUITE-HOST-DETERMINISM's (done), so the carry builds on
that group's step and does not reopen it.

**Not proposed: a rule or brief line saying "tests pin the clock".** That
would be the (b) mistake. The author obeyed every rule in force and handled
the day type on purpose. The missing piece was a run on the other day, and no
reader supplies that.

## 6. Not verified

- How the hotfix itself is written (the fixer's seat). The figures in
  section 1 use a local stand-in edit, not the hotfix.
- Days other than Saturday, Sunday, Monday, Wednesday and Friday were not
  probed on this block, and scripts other than `tests/features.py` were not
  shifted. Today's Saturday CI covers the whole suite for Saturday only.
- The 13.7 runner-hours is an upper bound: not every open head runs
  `tests/features.py` in scope, and no per-head scope was measured.

## 7. Record

Registered in `dev/audit/config/bugclasses.json` `_rca` as
`R10-RCA-FEATURES-WEEKEND-CLOCK`, with `class: null`. The broader class of
section 3 is not registered as a `bugclasses.json` class here. Registering it
is the class owner's call, and this document gives the three round-10
instances it would cite.
