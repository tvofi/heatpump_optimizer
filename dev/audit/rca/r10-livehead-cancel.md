# R10-RCA-LIVEHEAD-CANCEL: whole-run cancels at live pull-request heads

Root-cause seat, group R10-RCA-LIVEHEAD-CANCEL. Measured at origin/main
`355d9965a7a14ec45ef8cd25fb9c75c5ced044f1`, 2026-11-07 03:57-04:20Z. Every
figure below names the command that produced it. The instrument is
`dev/audit/harnesses/livehead_cancels.py`, landed with this document. Its cache
(`--cache DIR`) holds what GitHub returned and stays out of the tree.

## 1. What happened, reproduced

The two events in the brief, each read from the run-attempt and check-run APIs:

| PR | run / attempt | head | attempt start | first job cancelled | next attempt started | canceller (annotation) |
|---|---|---|---|---|---|---|
| #3241 | 42332985078 / 1 | `96987ab3d722` | 03:13:18Z | 03:24:57Z | 03:25:29Z (attempt 2, triggering actor `tvofi`) | `The run was canceled by @tvofi.` |
| #3232 | 42329221705 / 2 | `28e4375441e6` | 03:32:55Z | 03:49:15Z | 03:50:51Z (attempt 3, triggering actor `tvofi`) | `The run was canceled by @tvofi.` |

The commands:

    gh api repos/tvofi/heatpump_optimizer/actions/runs/<id>/attempts/<n>          # start, end, triggering_actor
    gh api repos/tvofi/heatpump_optimizer/actions/runs/<id>/attempts/<n>/jobs     # cancelled jobs, completed_at
    gh api repos/tvofi/heatpump_optimizer/check-runs/<job_id>/annotations         # the canceller line

GitHub writes the canceller annotation itself. In both attempts it is on every
cancelled job read: for #3241 `instrument-self-tests` and `fast (3.14)`, and for
#3232 `mutation`, `instrument-self-tests` and `Analyze (python)`.

**Null control for the annotation.** For the same reading on runs that
`cancel_superseded.py` cancelled from inside CI, take #3275's runs 42334622520
and 42334625513. The 03:34Z run 42334641003's `cancel-superseded` job logged
`cancelled 42334622520` and `cancelled 42334625513`. Their jobs read
`The run was canceled by @github-actions[bot].` So the annotation tells apart the
credential that sent a cancel. It does not read `@tvofi` on every cancel.

Attempt 1 of 42329221705 is a different class, as the brief says. Its only
non-green job is `instrument-self-tests`, annotated
`The job has exceeded the maximum execution time of 30m0s`. It belongs to
R10-HOTFIX-SELFTEST-TIMEOUT and is not counted here.

## 2. The cause, named

**A workflow-run cancel sent under the owner's own credential (`tvofi`), at the
pull request's live head, outside every in-tree canceller, followed by a rerun
under the same credential.** In the class (section 4) this is routine. It is not
a property of either PR.

What the evidence excludes:

- **The hypothesis the brief asked to test first: a `concurrency:` cancel from an
  `edited` event or a second `synchronize`.** Refuted by the code.
  `.github/workflows/ci.yml` keys its group `CI-${{ github.run_id }}` with
  `cancel-in-progress: false`. No other run can enter a run-id group, and the
  group never cancels. No other workflow's group contains a `ci.yml` run: the
  greps of `concurrency:` over `.github/workflows/` list `dependabot-automerge`,
  `dependency-graph`, `marketplace`, `merge-main`, `nightly`, `pages` and two
  job-level `governance` groups, none of them keyed on a PR. A concurrency cancel
  is also annotated `Canceling since a higher priority waiting request ... exists`,
  not `canceled by @<login>`. On the evidence side, #3241's only `CI edit` run in
  the window (42333513736) was created at 03:20:01Z and completed at 03:23:41Z,
  76 s before the cancel, and did not cancel it.
- **`cancel_superseded.py run` (the in-run canceller).** It runs under
  `github.token`, so its cancels read `@github-actions[bot]` (the control above).
  Its own job in each attempt logged `0 superseded run(s)`. The `cancel-superseded`
  job of 42332985078 attempt 1, and of 42329221705 attempts 2 and 3, all logged
  `cancel_superseded: 0 superseded run(s) of ci.yml on <branch>`.
- **`cancel_superseded.py sweep` (the orchestrator's pass, operator
  credential).** `sweep_plan` bounds each branch's cancel by the id of the newest
  run at the live head and passes `live_sha` to `candidates()`, which keeps only
  `head_sha != live_sha`. A run at the live head is outside its reach by
  construction (`tools/pr/cancel_superseded.py`, `sweep_plan` and `candidates`).
  The brief quotes its 03:46Z pass as `cancelled 0, kept 7 (live head)`.
- **Runner loss.** No cancelled job read carries `The runner has received a
  shutdown signal`. Each carries `canceled by @tvofi` and then `The operation was
  canceled.`, which is GitHub's line for a requested cancel.
- **The account job cap.** GitHub queues a job over the cap and never cancels
  it, so the cap cannot be the canceller. It can still be the motive (next
  section).
- **An in-tree tool that cancels and then reruns.** A locator pass over
  `tools/`, `.claude/`, `.github/`, `dev/governance/` and `tests/` found two
  cancel sites:
  - `cancel_superseded.py`, excluded above;
  - `tools/audit/seat/ci_probe.py`'s `cancel` subcommand, a plain
    `POST actions/runs/<id>/cancel` with no live-head check, under the caller's
    `gh` and with no in-tree caller.

  It found no cancel-then-rerun path. The reruns are `merge_train.py`'s `unstale`
  (`POST .../rerun` of a run already completed) and `infra_rerun`
  (`rerun-failed-jobs`, attempt 1 only), `gate.py refresh` and `sweep.py judge`
  (gate job only, under `github.token`), and `codeql-triage-poll.sh`. None of
  them sends a cancel.

**What is unknowable from GitHub.** Which process sent the two cancels. The
annotation names a credential, not a seat. Every operator-side seat, the owner's
browser and any relay holding the owner's token read the same `@tvofi`. A
user-owned repository has no audit-log API that would name the client. The seat
that holds the answer is whichever one sent `POST actions/runs/42332985078/cancel`
near 03:24:57Z and `POST actions/runs/42329221705/cancel` near 03:49:15Z, and
then the reruns 32 s and 96 s later. Only the orchestrator can read those
transcripts. This seat cannot.

**The motive, as far as the tree can show it.** P267
(`dev/programme/triage/s6-batch56.md`) accepted an owner-directed rule on
2026-10-28: when the account's job limit binds, *"POST actions/runs/<id>/cancel
for the victim's active runs at its live head"*, then resume with
`rerun-failed-jobs`. The rule was bounded: one pause per 5 min, a `never_pause`
list, a `paused.json` record and `PAUSE` and `RESUME` log lines. It was carried
into R10-TRAIN-OVERLAP-GRADE and has not landed.
`grep -rn "paused.json\|PAUSE #\|never_pause" tools dev/governance .claude dev/audit/config`
returns nothing at `355d9965`. A hand-run pause would produce exactly this
shape: a live-head cancel under the operator's credential, then a later rerun.

The observed reruns do not match the rule's resume. #3241's attempt 2 re-ran its
`cancel-superseded` job under a new job id with a fresh log, although that job
had passed in attempt 1. That is a full `rerun`, not `rerun-failed-jobs`.

The job-cap reading supports the pause motive only weakly:

- Near the #3232 cancel, main's push run 42335419215 had four jobs queued 2 min
  15 s to 3 min 20 s (03:45:41Z to 03:47:56-03:49:01Z). All of them had started
  before the 03:49:15Z cancel.
- Near the #3241 cancel, no job of the 18 attempts active from 03:22 to 03:28Z
  waited 2 min or more.

So the motive cannot be named either. It is recorded as the leading candidate,
not as the cause.

## 3. Process state: (a), the process did not exist

No process existed that bounds, records or explains a cancel at a live head
sent from outside CI.

- `cancel_superseded.py` holds this repository's live-head rule ("a run on a
  head that has already been superseded has no standing to cancel anything").
  Its unit is its own two callers, the `ci.yml` job and the orchestrator's
  `sweep`. It binds no other sender of the same POST. `ci_probe.py cancel` sends
  that POST with no live-head check.
- P267's bounded pause is a triage carry, not a process in force. No tool,
  `paused.json` or log line exists to obey or disobey. That makes this (a), not
  (b).
- No instrument read the canceller. The runs listing shows only a run's latest
  attempt, so a cancelled attempt 1 that a rerun replaced is invisible to
  `gh run list` and to `superseded_runs.py`. That harness measures the opposite
  class: runs that should have been cancelled and finished. The bus reads the
  latest gate. It saw `cancelled` and refused the dispatch, and nothing upstream
  recorded who had cancelled or why. So the brief arrived with "no known cause".

## 4. How far the class reaches

The rule, from `livehead_cancels.py`'s docstring: a cancelled `pull_request`
attempt of `ci.yml` off main is IN CLASS when its canceller annotation names a
login other than `github-actions[bot]` and its head is the branch's live head at
the cancel time. The live head is the head SHA of the newest `ci.yml`
pull_request run created by then.

    python3 dev/audit/harnesses/livehead_cancels.py --cache DIR --fetch \
        --since 2026-11-04T00:00:00Z --until 2026-11-07T04:00:00Z --list

The run read 1631 attempts and attributed 344 cancelled attempts. It took 19 min
wall-clock (attempts 4.5 min, annotations 14.5 min).

    CANCELLED    125  by=@github-actions[bot]         head=superseded
    CANCELLED    141  by=@tvofi                       head=live
    CANCELLED     27  by=@tvofi                       head=superseded
    CANCELLED     31  by=timeout                      head=live
    CANCELLED      1  by=timeout                      head=superseded
    CANCELLED      1  by=timeout+@github-actions[bot] head=superseded
    CANCELLED      1  by=timeout+@tvofi               head=live
    CANCELLED     16  by=unattributed                 head=live
    CANCELLED      1  by=unattributed                 head=superseded
    CLASS live-head external cancels: 142, minutes lost 2586.3 (attempt start to cancel)
    NULLCONTROL-HEAD live=0 class=0
    NULLCONTROL-BOT class=0

Both events in the brief are in the `--list` output (`42332985078/1`, 11.8 min,
and `42329221705/2`, 16.8 min). #3275's two bot cancels read
`@github-actions[bot]` / `superseded`, outside the class. The null controls force
every head superseded and every canceller to the bot, and both print 0. So the
class count is not something the classifier produces whatever its input.
`--selftest` drives the same rule on synthetic attempts.

**Live-head proxy, and which way it errs.** A push that started no run is
invisible to the proxy, so the proxy can read a superseded attempt as live and
never the reverse. The 142 is an upper bound on live-head cancels. The 141 is
exact for "cancelled by `@tvofi`".

What followed each of the 142, by a scratch reading over the same cache (the
next attempt of the same run, or a run of the same kind at the same SHA that was
alive at the cancel):

| what followed | attempts | minutes run before the cancel |
|---|---|---|
| restarted: a later attempt of the same run | 70 | 1584.9 |
| dropped: no later attempt and no twin | 67 | 848.4 |
| duplicate: a twin run was alive at the cancel | 5 | 153.0 |

- **Restart gap (cancel to next attempt start).** Minimum 22 s, median 816 s,
  maximum 7496 s. 17 of the 70 restarts came within 120 s, as both events here
  did.
- **PR merged or closed within 10 min of the cancel.** 0 of 142, by the pulls
  API on each PR the run title names. These were not cleanup after a merge.
- **Cadence in the brief's hour.** Seven class cancels between 02:38 and 03:50Z,
  each restarted: #3272 02:38, #3264 02:54, #3274 03:16, #3241 03:24, #3267
  03:34, #3273 03:41, #3232 03:49. About one every 8-10 min, with no common
  failing or long-running job.
- **`record/autofix` (#3215).** It accounts for 38 of the class rows. It is the
  bot-recorded delivery PR, which the train drives. Its cancels are almost all
  "dropped". Whether that harms anything depends on the train, and this seat did
  not measure it.

## 5. Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

**Defect.** In 76 h of this window: 142 cancels, which is 45 per day, so
P(recurrence) is about 1 per day at least.

- 2586 runner-minutes were run and discarded, from attempt start to cancel.
- Each restart adds the gap plus a full rerun before the head has a gate.
- The brief's concrete cost is one reviewer dispatch per event, because the bus
  refuses a head whose latest gate is cancelled. Its two events delayed two
  dispatches by at least 11.8 + 0.5 min and 16.8 + 1.6 min of discarded run,
  plus each rerun's own run time.
- For the other 140, the delay to a dispatch depends on whether the PR was
  waiting for review at the time. This seat did not measure that, so it is not
  stated.

**Candidate countermeasures and their prices:**

1. *Re-key `ci.yml`'s concurrency group so an `edited` event cannot cancel a
   code run.* **Refused: it is a no-op.** The group is already per run id with
   `cancel-in-progress: false`, and no cancel in the class is a concurrency
   cancel (0 rows read `concurrency`).
2. *Route body edits through a path that does not trigger the group.* **Refused:
   the cause is not a body edit.** Edit runs neither enter a code run's group nor
   send cancels, and no edit run's `cancel-superseded` job cancelled anything at
   a live head.
3. *Make the dispatch seat's rerun rule explicit in tools.* **Refused here.** The
   rerun is the response to the cancel, not its cause. A sharper rerun rule
   leaves the 142 cancels in place.
4. *A live-head refusal in `ci_probe.py cancel`.* **Not built.** It would cost
   about one PR-head read per cancel and nothing per CI run. But no evidence
   shows `ci_probe.py` sent any of the 142: it has no in-tree caller, and its log
   path is the caller's. A guard on a path not shown to be used is unmotivated by
   `root-cause.md` section 5. Revisit if the orchestrator's reading (section 6)
   names it.
5. *The detector, `livehead_cancels.py`.* **Built.** It adds 0 s to every CI run
   and every session, because it runs only on demand. A reading costs about
   19 min wall-clock and about 1,000 read-only API calls per 3-day window, well
   inside the 5,000/h REST budget. It turns "no known cause" into a named
   credential, a count and a restart pattern in one run. That is the first step
   any countermeasure needs, and the only one this seat can take without knowing
   the sender.

**Verdict.** Build the detector, and refuse 1-3 as above. The class-eliminating
barrier depends on a fact only the orchestrator can supply (section 6), so
leaving it unbuilt here is not a decision against it.

## 6. Owed, and where it goes

- **To the orchestrator.** Name the process that sends `@tvofi` cancels at live
  heads: about 45 a day in this window, 17 restarted within 2 min. It is in a
  seat transcript, a relay or the owner's own hand. The countermeasure depends on
  which:
  - If it is a hand-run P267 pause, land P267's bounded pause
    (R10-TRAIN-OVERLAP-GRADE carries it), with its `paused.json`, rate limit and
    `rerun-failed-jobs` resume, and retire the hand practice.
  - If it is a seat restarting runs to "see whether it comes out differently",
    that is `.claude/skills/steward/SKILL.md` S9's prohibition, and the barrier
    is a refusal at the seat's cancel path.
  - If it is the owner, no barrier is owed, and the count is the owner's to read.

  This changes how the orchestrator's next pass must work, so by
  `finding-propagation.md` it belongs in that stage's brief. This seat cannot
  write that brief (its write scope is its return refs). The PR body names the
  destination for the orchestrator to place.
- **Re-reading.** The harness is in the tree. The class count after a
  countermeasure is the same command over a window that starts after it lands.

## 7. Not covered

- The 16 `unattributed` and 31 `timeout` live-head cancels. Timeouts are
  R10-HOTFIX-SELFTEST-TIMEOUT's. An unattributed attempt's earliest-completed
  cancelled job carried no canceller line, and this seat did not read further
  into them.
- Workflows other than `ci.yml`.
- Attempt 3 of 42329221705 was still in progress at 04:20Z. Its outcome is not
  part of this reading.
