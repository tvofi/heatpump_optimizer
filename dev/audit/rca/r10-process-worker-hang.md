# RCA: the process worker's reply wait had no deadline (v7.1.2)

Group R10-RCA-PROCESS-WORKER-HANG. Trigger 1: the defect reached v7.1.2. The
fix is #3232 (group R10-EXT-3226, re-authored from the outside pull request
#3226); this seat ran beside it and touched none of its files.

## Result

- **Cause.** `_run_in_process` writes the job, then blocks in
  `pickle.load(stdout)` with no deadline while holding the module-global
  `_PROCESS_LOCK`. A worker that is alive and does not answer raises nothing,
  so the #511 fallback (`ProcessWorkerUnavailable`) never fires and every later
  job queues on the lock. The read was written that way in 8542e51cb
  (2026-09-05, "process-route the solve off the GIL", first tag v6.3.15) and
  shipped unchanged through v7.1.4.
- **Process state: (c).** Round 9's D1 seat examined this lock and this read
  and filed D1-s2-05 against the stop path; its unit (stop latency against a
  solve that ends) and the D1 method (exception injection) never put a live,
  silent peer on the other end of the read.
- **Countermeasure:** D1's method step 5 now also drives every wait on a
  peer with a live, silent one; its instrument is
  `dev/audit/harnesses/silent_peer_waits.py`. The
  per-PR static arm passes the arithmetic on one instance but is not built
  here: `## Needs tvofi`.

## The defect, reproduced

`silent_peer_waits.py --drive` runs `time.sleep(30)` in the real worker (a job
that stays alive and never answers) and waits 6 s for `_run_in_process` to
return. Each row is one run, from that tree's root:

| tree | arm | reply back within 6 s | outcome |
|---|---|---|---|
| v7.1.2 | silent | 0 | still waiting on the worker reply |
| v7.1.2 | silent, `--reply-timeout 2` | 0 | the tree has no `PROCESS_REPLY_TIMEOUT_S` to set |
| v7.1.2 | `--answer` (null control) | 1, 0.10 s | returned |
| main 9cbd7dd0d | silent | 0 | still waiting on the worker reply |
| main 9cbd7dd0d | `--answer` | 1, 0.10 s | returned |
| #3232 head 0e59de557 | silent (shipped 1800 s deadline) | 0 | waiting, inside its deadline |
| #3232 head 0e59de557 | silent, `--reply-timeout 2` | 1, 2.00 s | raised `ProcessWorkerTimeout` |
| #3232 head 0e59de557 | `--answer` | 1, 0.10 s | returned |

The perturbation is the deadline: at the fix it moves the reply from
"waiting" to a timeout at the deadline; at v7.1.2 and main there is no
deadline to move.

## Why the worker went silent: known and unknowable

Known, from #3226's body: the last completed optimisation was 09:02:28, none
followed until a restart at about 10:11, and `systemmonitor` CPU rose from
about 14-15 % to a flat 37-39 % at 09:15 with memory flat at about 49 %. On a
four-core Raspberry Pi 4 that rise is about one core. The worker runs one
GIL-bound job at a time, so the worker was **computing**, not blocked on I/O:
a job that did not finish, not a worker that died or deadlocked. Memory flat
rules out a leak or swap storm as the driver.

Known, from the code at v7.1.2: no job the worker runs has a wall-clock bound.
`optimizer.py`'s L-BFGS-B passes `maxiter`, which bounds iterations and not the
cost of one; the substep count in `thermal_model.py`'s `_substeps_and_loss`
(`n_sub = max(1, int(np.ceil(worst * dt_hours / EULER_MONOTONE_MAX_RATIO)))`)
has a floor and no cap; `dhw_planner.py`'s `linprog(..., method="highs")`
passes no `time_limit`. Round 9 demonstrated one route to an unbounded solve
(D1-s2-02: one forecast row at wind 1e12 m/s ran a solve past 60 s against
3.45 s healthy). Its fix bounds the forecast rows (`_FORECAST_FIELD_RANGE`,
wind 0-100 m/s, before v7.1.2); the lead that would bound the substep count
whatever the input (`dev/audit/rounds/round9/leads.json`, symbol
`ThermalModel._stability_substeps`, owner D1-s4) was not built.

**Unknowable from the evidence:** which job ran (solve, diagnosis, sysid,
recovery, sensor advisor), on which inputs, and why it did not finish. The
child is a separate interpreter; Home Assistant's shutdown dump printed only
the parent's threads, and no diagnostics bundle or worker stack exists. This
seat did not measure whether any input reachable at v7.1.2 drives a solve past
55 minutes.

## Why the stop did not free the lock: not reproduced

The stop path at v7.1.2 terminates the child before it takes `_PROCESS_LOCK`
(1c4d70fdd, round 9 F1.5 for D1-s2-05, first tag v6.7.11), on the premise that
the child's death ends the parent's read. The field trace shows the stop
thread still at `with _PROCESS_LOCK:` and the solve thread still in
`pickle.load(stdout)` through every shutdown stage.

Here the premise holds: with the silent job in flight, `--drive` fires
`_shutdown_process_pool` and reads `stop_elapsed_s=0.00` and
`reply_released_after_stop=1` at v7.1.2, main and #3232's head; a
CPU-spinning job (`sum(range(10**14))`) reads the same at v7.1.2 (a scratch
probe, not committed). So on that install the child did not die, or its death
did not close the pipe. Candidates the evidence cannot separate: a child in
uninterruptible sleep, where a signal waits; or a second holder of the pipe's
write end. Neither is observable without a process listing from that host.
#3232 bounds the stop regardless (`_SHUTDOWN_LOCK_TIMEOUT_S`, 5 s).

## Process state: (c)

The process existed and was followed; its unit did not reach a live, silent
peer.

- **D1 found the lock and the read, not the missing deadline.**
  `dev/audit/rounds/round9/batch1-findings.json` D1-s2-05: "`_run_in_process`
  holds [the lock] for the whole transport round trip (pickle.dump ..
  pickle.load, i.e. the entire solve) ... (30-70 s solves, or the D1-s2-02
  runaway)". The seat knew a solve could run unbounded with the lock held. Its
  `phenomenon_property` is "the stop reap completes in bounded time
  independent of solve duration", and its metric is stop latency against a
  real, finite solve. The fix met that property; the cycle's own wait was
  outside the unit.
- **The check supplies its own premise.** `tests/features.py`'s
  `_f15_reap_under_solve` parks the solve thread on an `Event` that the double
  handle's kill sets: "a real solve parks reading the worker's pipe, which dies
  with the worker". The check reads green because the double, not a pipe,
  ends the read.
- **D1 step 5 injects exceptions.** A silent peer raises none, so "does it
  recover on the next cycle" never ran against one.
- **The #511 fallback checks drive only a worker that fails**:
  `tests/features.py`'s #511 block (an unpicklable job, an absent module), the
  unpicklable-result job (#524), and `tests/replay.py`'s `InProcessWorker` and
  `unusable` arms. No check submits a job to a worker that stays alive and
  silent; the two children that do stay silent (`_G525_STUBBORN`,
  `_G533_STUBBORN`) time the stop path and are never sent a job.
- **D3, D9, D15 could not have read it.** D3 deletes lines that exist; a
  missing deadline is not a mutant. D9's worker harness
  (`dev/audit/rounds/round9/D9/s1/worker_rss.py`) drives finite jobs for
  memory. D15 needs a bundle, and its rule reads a gap with no cycle rows as
  downtime, not a lead.

Not (a): D1's brief hunts "ways the integration wedges", and round 9 read this
code. Not (b): each seat ran its method. Not (d): the read was unbounded from
8542e51cb, before rounds 8-10 began on 2026-10-07.

## The class: a synchronous wait on a peer with no deadline

Rule: `silent_peer_waits.py --scan <package>` (AST; the reasons are in its
header). Run over every `v*` tag (158, v2.3.0-beta.1 2026-08-20 to v7.1.4
2026-11-06), from `git archive <tag> custom_components`:

| first tag | site (function) | disposition |
|---|---|---|
| v6.3.15 | `coordinator.py` `_run_in_process`: `pickle.load(stdout)` | **the defect**; #3232 moves it into `_read_reply` behind a deadline |
| v6.3.15 | `process_worker.py` `run_worker`: `pickle.load(stdin)` | by design: the idle worker waits for its parent; the parent's close is EOF |
| v6.4.0 | `coordinator.py` `_shutdown_process_pool`: `worker.wait()` | after `kill()`; `waitpid` returns once the child is dead (#533) |
| v7.0.5 | `coordinator.py` `_run_in_process`: `worker.wait()` | after `kill()`, same |
| (`with`) | `with _PROCESS_LOCK` in `_run_in_process` and `_shutdown_process_pool` | bounded only by its holder's wait: unbounded at v7.1.2, bounded at #3232 (1800 s reply, 60 s per frame; the stop path takes it with a 5 s timeout) |

At #3232's head the scan returns six sites, as at v7.1.2 and main: the
descriptor-less `pickle.load(stdout)` in `_read_reply` (the in-memory test
doubles) and the deadline-bounded `pickle.load(_frame_reader(...))` replace
the defect and the stop path's `with`. **The count does not move with the
fix**; only the dispositions do, which is why the scan is an enumerator and
not a pass/fail check. `_PROCESS_LOCK` is the package's only `threading`
primitive, and the worker's pipes are its only IPC channel.

## Cost test

Unit: wall-clock seconds per release.

- `cost(defect)`, one occurrence: the install's outage, 09:02 to about 10:11
  (about 4,140 s), plus #3232's review, created 2026-11-06T00:16Z, last
  updated 20:03Z (about 71,200 s, 38 commits, re-cut at round 4): about
  75,000 s. Lower bound: the contributor's time and other installs are not
  counted.
- `P(recurrence)`: one deadline-less site with a live peer was created in 158
  release tags (the scan above), so 1/158 = 0.0063 per release. In the 54 tags
  after v6.3.15 no further one was added. Expected: 75,000 x 0.0063 = about
  475 s per release.
- **D1 step 5's wait arm**, recurring: one scan (median 0.67 s over 5 runs, a standalone
  process) and three drives (about 21 s at `--cap 6`) per D1 round, plus about
  15 minutes to disposition six sites. Taking ten rounds over the 158 tags
  (an upper bound: rounds 1-2 predate some of these tags) gives 0.063 rounds
  per release, so about 58 s per release. **Passes** (58 < 475).
- **A per-PR static arm** in `tests/entities.py`: 0.67 s per run; the merge
  commits per release (5,594 in v6.3.15..v7.1.4 over 55 tags, about 102) bound
  the runs from below, so at least 68 s per release, plus about 600 s of
  disposition review for each by-design site (three in 55 tags: about 33 s
  per release): about 100 s per release. Against 475 s it passes. Against
  what step 5's wait arm leaves, it is the window between a site landing and the next D1
  round: 8542e51cb landed 32 days before round 9 began. On one instance, the
  margin is within the estimate's error.

## Countermeasure: D1 method step 5, waits

`dev/governance/dimensions/D1.md` step 5 ("Guards, waits") now also drives
every wait on a peer (pipe, child, lock) with a peer that stays alive and
silent: the wait must time out and free what it holds. `--scan` enumerates the
sites for disposition, `--drive` is the process-worker arm, and `--answer` is
its null control.

The brief sat at its line and token caps (`policy_lint.mjs`'s `[budgets]`). The
arm is paid for by tightening step 5's own wording and step 6's #1090
sentence, so no cap moved. It changes the
unit that missed the defect (state (c)), not the instruction's force. It is
policy, so it merges only on the owner's approving review.

**Shown to detect:** the table under "The defect, reproduced". The drive reads
0 at v7.1.2 and at main, and 1 with `ProcessWorkerTimeout` at 2.00 s at
#3232's head under the deadline perturbation. `--answer` reads 1 at 0.10 s on
every tree, so the arm does not go green by skipping and does not fire on a
healthy reply.

## Needs tvofi

1. **The per-PR static arm.** It passes the cost test by about 4x on a single
   instance, so this seat does not refuse it. It cannot land green before
   #3232 merges. Its dispositions must key on the enclosing function: the
   defect and #3232's descriptor-less fallback share file, call and snippet,
   `pickle.load(stdout)` (`fixer.md` step 14). It reads only literal call
   shapes, so a bare `os.read` on a pipe passes it. Proposed: build it after
   #3232 merges, as a `tests/entities.py` arm over `--scan`'s sites with a
   reasoned registry keyed on (file, function, call). Otherwise, record the
   refusal.
2. **The substep cap lead** (round 9 leads.json, D1-s4): it bounds a runaway
   solve whatever the input. It is the remaining code-side candidate for why
   the worker computed for about 55 minutes. It is a D1/D2 finding for round
   11, not this seat's.

## Figures

Every command runs from the tree it names, with
`PYTHONPATH=<root>/tests/hastub:<root>/custom_components`.

- Drive rows: `python3 dev/audit/harnesses/silent_peer_waits.py --drive --cap 6 --silent 30 [--reply-timeout 2 | --answer]`.
  Trees: v7.1.2; main 9cbd7dd0d; #3232's head
  0e59de5574d72746dbcd3fa1319d3ad3dd64776b.
- Site table: `python3 dev/audit/harnesses/silent_peer_waits.py --scan <root>/custom_components/heatpump_optimizer`.
  It prints `RESULT unbounded_sites=6` at v7.1.2, main and #3232's head. Per
  tag, the same scan runs over `git archive <tag> custom_components` for every
  `git tag -l 'v*'` (158). It returns 0 sites up to v6.3.14 and 2 at v6.3.15,
  then 3 from v6.4.0 and 4 from v7.0.5. That tag scan counted calls only; the
  `with`-lock arm was added after it.
- Merge commits per release: `git log --merges --oneline v6.3.15..v7.1.4 | wc -l`
  (5,594) over `git tag -l 'v*' --sort=v:refname | awk '/^v6.3.15$/{f=1} f' | wc -l`
  (55).
- First tags: `git tag -l 'v*' --contains 8542e51cb --sort=v:refname | head -1`
  (v6.3.15); the same for 1c4d70fdd (v6.7.11).
- Round start dates: `git log --reverse --format=%ad --date=short -- dev/audit/rounds/round9 | head -1`
  (2026-10-07; round8 is the same and round10 is 2026-10-15).
