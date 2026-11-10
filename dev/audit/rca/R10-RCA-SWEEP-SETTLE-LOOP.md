# R10-RCA-SWEEP-SETTLE-LOOP: `sweep.settle()` re-runs two red gates at one head up to attempt 44

Root-cause seat, `root-cause.md`, 2026-11-08. Measured at `origin/main` `4fe7d5934b`.
It ran beside the sweep fixer and edited nothing under `tools/ci/`. It made no GitHub
writes. Each figure below comes with the command or API read that produced it. The
one estimate (`P(recurrence)`) is marked as an estimate.

Trigger: **release**. The defect came in with `52f9fc5b34` (#3287, merged
2026-11-07T19:14:32Z as `5c1fa41fb9`) and shipped in v7.1.6.

## 1. Cause, reproduced

**The cause.** `tools/ci/sweep.py` `undecided()` arm 1 reads any non-gate job of
another run with `completed_at > this gate's started_at` as a source that finished
after this gate judged. Arm 1 is
`any(j.get("name") != "gate" and (j.get("completed_at") or "~") > t0 for j in jobs)`.
When a `gate` job is re-run (`POST actions/jobs/<id>/rerun`), GitHub writes a new
attempt in which **every skipped job of that run gets new stamps**, a few seconds
before the new gate starts. Every job that ran keeps its stamps unchanged. A
re-stamped skipped job is not a source and ran nothing. Arm 1 still reads it as one.

So take two ci.yml runs at a head, where both gates are red for a real reason
(nothing can turn them green):

1. Re-running A's gate re-stamps A's skipped jobs to a time after B's gate started.
   `undecided(B)` now names A, so the sweep at A's completion re-runs B.
2. Re-running B re-stamps B's skipped jobs to a time after A's latest gate started,
   so the sweep at B's completion re-runs A.

This repeats until `ATTEMPT_CAP` stops it at 44. Every re-run is a new CI
completion, and every CI completion fires `gate-sweep.yml` again.

**Measured transition.** These are #3319's two runs at head `8d4ff2f2`. Run
42469369199 is the code run and run 42469369682 is the edit run. Both have a real
red: `budget-raise-gate` failed. The listings come from
`gh api .../actions/runs/<id>/attempts/<n>/jobs`, attempts 1 to 6, and are recorded
in `dev/audit/harnesses/r10_rca_sweep_settle_loop.json`. Between attempts, the only
jobs whose status, conclusion or stamps change are the gate and the skipped jobs
(10 in the code run, 7 in the edit run). The latest non-skipped `completed_at` stays
10:21:40Z (code) and 09:59:09Z (edit) across all six attempts. The skipped jobs'
latest `completed_at` falls 2-21 s before each attempt's gate start. In the code
run, for example, it is 10:23:18 against a gate start of 10:23:22, then 10:25:17
against 10:25:20, and so on. The live alternation was: edit attempt 2 at 10:22:32,
code attempt 2 at 10:23:22, edit attempt 3 at 10:24:27, code attempt 3 at 10:25:20,
and onward. The code run reached attempt 44 at 11:48:43Z, 87 minutes after its
first gate.

**Reproduction, closed loop.** The harness is
`python3 -I dev/audit/harnesses/r10_rca_sweep_settle_loop.py replay [--ci DIR]`.
It runs the real `sweep.main` against the recorded head. Each re-run it posts
becomes that run's next attempt, with the recorded attempt-2 transition applied:
the changed jobs are shifted to the new gate start, the gate goes red again for
its recorded duration, and the attempt's completion fires the sweep again. The
harness stops at a fixed point or at GitHub's 50-attempt ceiling.

| `sweep.py` at | world | RESULT |
|---|---|---|
| `origin/main` `4fe7d5934b` (includes `955bb88096`) | recorded re-stamp | `reruns=86 max_attempt=44 sim_minutes=72 alarm=yes` |
| `52f9fc5b34` (#3287) | recorded re-stamp | `reruns=86 max_attempt=44 sim_minutes=72 alarm=yes` |
| `52f9fc5b34^` (before #3287, no `settle`) | recorded re-stamp | `reruns=0 max_attempt=1` |
| `origin/main` | `--no-restamp` (the hand-written fixtures' world) | `reruns=1 max_attempt=2 alarm=no` |
| candidate copy: arm 1 skips `conclusion == "skipped"` | recorded re-stamp | `reruns=1 max_attempt=2 alarm=no` |

The replay matches the live order and spacing: its re-runs post at 10:22:25 and
10:23:11 against the live 10:22:32 and 10:23:22. The candidate row is a control for
the harness and not a proposed fix, because the fix is the fixer's. That candidate
also passes the existing `sweep.py --self-test` (`52 checks, 0 failed`). The current
self-test therefore cannot tell a fixed arm 1 from a broken one.

**Which side moved.** GitHub's behaviour predates #3287. The fixture #3287 committed,
`tools/ci/fixtures/gate_busy_defer_runs.json`, already has two runs that show it:
42307493684 and 42307798573, both at attempt 10 on 11-06/07. Their skipped jobs
carry 04:29:06-15Z, seconds before their 04:29:09-10Z gates. In 42307493079
(attempt 3), the skipped jobs' `started_at` is 04:25:49Z while their `completed_at`
is still 22:49-23:21Z the night before. What moved was the code. #3287 added arm 1
and a `settle` branch that acts on it. Before #3287 the sweep re-ran only beside a
green, newest-covering gate.

## 2. Process state: (c), followed and did not produce the result

The process was obeyed at every step:

- `fixer.md`: failing test first, mutation proof, and the finder's harness at both
  ends.
- The recorded-fixture replay (`r10_gate_busy_defer_3.py replay`).
- An adversarial `fix-review.md` review at the head.

Evidence for the convergence claim:

- **The claim.** `sweep.py`'s module docstring says: *"A re-run judges after every
  such job finished and beside no gate starting, so it is never re-run again: the
  branch cannot loop."* `undecided()`'s docstring adds *"re-judged, it is final,
  and nothing loops"*.
- **What pinned it.** In #3287's `sweep_selftest.py`, the `run(..., units=...)`
  helper builds each non-gate job as `{"name": "u<k>", "completed_at": c}`. It has no
  `conclusion` field, so "skipped" cannot be written in that fixture language. The
  two "(no loop)" checks are `settle null: that lower gate re-judged red ...` and
  `settle null: the same reds judged after every source finished, apart, are final`.
  Each asserts `posts == []` for **one sweep pass** over a static world in which a
  re-run moves nothing but the gate. Neither feeds a re-run back into the world.
- **The replay.** `r10_gate_busy_defer_3.py replay` runs one sweep at the code run's
  recorded completion, judges each re-run once, and stops. It is open loop, so a
  re-run's effect on the next sweep is never computed. Its fixture recorded one
  attempt per run, the latest, so nothing compared stamps across attempts, even
  though the attempt-10 rows showed the re-stamp.
- **The review.** `refs/heads/verdict/3287` (`5e67c246a4`, merge at `16452e4530`),
  focus 2, says: *"`settle` leaves nothing unjudged and loops nowhere in the cases
  I checked ... Every re-run judges after every source and the peer gate
  concluded, so no `undecided()` arm fires again (S3 and S4 kill the no-loop
  nulls)."* Its live evidence (focus 4) was a head where the re-run gates turned
  **green** (17:12Z). A green re-run ends the loop at the first step, so the review
  never saw a red-red head re-run.

This is not (b): every step ran and passed. It is not (d): the re-stamp was already
in the fixture #3287 recorded. It is not (a): a self-test, a replay and a review
covered `settle`. What none of them checked is the property itself. "Cannot loop" is
a property of the closed system, the sweep together with GitHub's re-run, and every
instrument evaluated one pass of the sweep against a world the re-run does not
change. That was a premise nobody tested, not an instruction nobody followed. A
firmer instruction to the fixer or reviewer would not have helped.

## 3. Class search

Every reader of a job's `completed_at` under `tools/`, at `origin/main`
(`git grep -n completed_at -- tools/ .github/`, fixtures excluded):

| site | reads | re-stamp exposure |
|---|---|---|
| `tools/ci/sweep.py:77` `undecided()` arm 1 | any non-gate job's `completed_at` | **the defect** |
| `tools/ci/sweep.py:76,79` arms 2-3, `covers_newest` | the gate's own stamps, run `created_at` | none: a gate re-run is a real judgement |
| `tools/ci/gate.py` (production `judge`/`busy`/`deferral`) | status and conclusion only | none |
| `tools/ci/gate.py:660,738` | inside `self_test()`'s recorded replay `at_time()` | test-only. A re-attempted skipped job reads as not yet completed before its re-stamp time. It errs toward under-reporting and affects no verdict |
| `merge_train.py:551` `sweep_settling` | green GATE check-runs' `completed_at` | none: gate only |
| `merge_train.py:761` `infra_due` | failed jobs, attempt 1 only | none |
| `orchestrator_tick.py:1441` | any check run with `completed_at` after a worker's dispatch, read as "CI completed since dispatch: OK" | same shape. A sweep re-run, or the skipped check runs it re-stamps, reads as CI activity at the worker's head. The worker line says OK while the worker did nothing. Whether check runs carry the job re-stamp was **not measured** here. Effect: a liveness false-OK, never a re-run |
| `ci_critpath.py:182` | ran jobs only (`conclusion not in (None, "skipped")`) | none |

Wider shape: the sweep is an actor triggered by CI completions that creates CI
completions. Its only loop bound is `ATTEMPT_CAP`, so any false-positive predicate
in it costs up to 44x. `ci-autofix.md` gives the bot's own pushes an explicit loop
guard, the subject check. The sweep has no counterpart that compares a re-run's
inputs with the previous attempt's. That is the fixer's design question, forwarded
in section 5.

## 4. Cost test

**cost(defect), measured.** These are ci.yml runs, from
`gh api --paginate .../workflows/ci.yml/runs?created>=2026-11-06T22:00:00Z`, read
at 11:52:46Z, then
`r10_rca_sweep_settle_loop.py census <tsv> --since ... --until ... --alarm N`:

| window | hours | runs | re-attempts | runs >= 10 | runs >= 20 | runs >= 44 | max |
|---|---|---|---|---|---|---|---|
| pre-merge 2026-11-06T22:00Z to 11-07T19:14:32Z | 21.2 | 465 | 428 | 4 | 0 | 0 | 17 |
| post-merge 11-07T19:14:32Z to 11-08T11:52:46Z | 16.6 | 324 | 1618 | 48 | 32 | 17 | 45 |

- Re-attempts went from 20/h to 97/h, about 1280 more than the pre-merge rate
  predicts over 16.6 h.
- `gate-sweep.yml` listed 1000 runs (the API's cap) created 07:53:04Z to 11:50:13Z
  alone. That is 904 run-minutes created-to-updated, median 23 s each.
- A sampled gate attempt holds its runner 30-38 s.
- 17 PR heads were left red at the cap until someone pushed again.
- The 810 runner-minutes and 1089 re-attempts in the brief are the orchestrator's
  figures over its own window. They were not re-taken here.

**Per occurrence, wall-clock.** The loop runs from its start until someone
notices. Here that was about 16 h. The first post-merge run that reached attempt 10
was created 19:29Z, and this RCA was dispatched at about 11:50Z the next day. For
those 16 h the account's concurrent-job cap was shared with the loop. One looping
pair takes about 87 min to reach the cap, measured on #3319.

**P(recurrence), estimate.** The sweep's re-run predicates changed 3 times in R10
(`85b72e824d`, `52f9fc5b34`, `955bb88096`), and a fourth change is in flight. One of
those changes produced a runaway. The pre-merge window also has 16-17-attempt runs
(#3265, 03:10Z and 03:18Z), so the predecessor design re-ran heavily too. The basis
is 1 runaway in 3 landed changes, with at least 1 change per release cycle at
R10's rate. Estimate: P ≈ 0.25 to 0.33 per release cycle.

**The two countermeasures.**

| | detector | standing cost | wall-clock saved per occurrence | verdict |
|---|---|---|---|---|
| A | closed-loop convergence replay in the sweep's self-test | 0.12-0.25 s per self-test run (`time -p`) | the whole occurrence: it is red at the PR, before release (about 16 h of loop and 17 stranded heads) | 0.25 s ≪ 16 h x 0.25: **build** |
| B | runtime loop alarm: some open-PR ci.yml run at attempt >= 20 | one listing call, 2.84 s (`time -p gh api ...runs?created>=...`), every 1800 s in the background beat: about 2.3 min/day of beat time, 0 s of seat time | about 15 h: it fires within about 40 min of loop start (2 min/attempt) plus up to 30 min of beat interval, against the measured 16 h | 2.3 min/day ≪ 15 h x 0.25: passes, **propose** |

## 5. Countermeasure

**A, state (c), adopted. Carried to the fix, not built in this seat.** The sweep's
convergence claim gets pinned closed loop. The self-test, or a harness the fixer
runs at both ends, iterates sweep, re-run, recorded GitHub transition and completion
until it reaches a fixed point. It runs on a recorded **attempt-to-attempt** listing
pair, not a single listing or a hand-written world. It asserts that re-runs per
head stay bounded, for example `max_attempt <= 3`, on a red-red head.

This maps directly onto the state finding. The instruments were followed, and
they evaluated the wrong property: one pass instead of the closed loop. On the
brief's question: recording fixtures from real API listings is **necessary, not
sufficient**. #3287 recorded real listings, and they contained the re-stamp. What
was missing was the *transition* (attempt n against n+1) and a loop that consumes
it. `sweep_selftest.py` belongs to the fixer's lane, so this goes to the fix's
brief by `finding-propagation.md`. `r10_rca_sweep_settle_loop.py replay --ci <tree>`
is offered as the finder's harness at both ends.

Demonstration (section 1 table):

- **Red on the defect.** `origin/main` and `52f9fc5b34` give `reruns=86 max_attempt=44`.
- **Green once fixed.** The candidate arm-1 copy gives `reruns=1 max_attempt=2`.
- **Null control, not green by skipping.** The `--no-restamp` world at `origin/main`
  gives `reruns=1`. A world without the re-stamp hides the defect, so the check's
  power comes from the recorded transition. The pre-#3287 tree gives `reruns=0` on
  the same real red, which is correct: a genuine red head is not re-run.

**B, proposed to proposal triage, not built, not a control until it is.** This is a
`beat_jobs.py` row, `attempt-watch`, every 1800 s. It reads one
`actions/workflows/ci.yml/runs?created>=<now-6h>` page and writes
`attempt-watch: RUNAWAY run=<id> attempt=<n> pr=<N>` to the digest for any run at
attempt >= 20. It catches a runaway from any cause: this predicate, the next one, or
a relay or autofix loop.

The threshold comes from the census. At 20 the pre-merge window flags 0 runs and the
post-merge window flags 32. At 10 the pre-merge window flags 4 runs, the
predecessor design's 10-17-attempt runs, which would be noise. Demonstrated with the
same predicate: `census --alarm 20` gives `at_or_over_alarm=0` before the merge and
`32` after it, and `replay` gives `alarm=yes` on the defect and `alarm=no` with the
candidate.

B is not built here because it edits `tools/audit/seat/beat_jobs.py`, an instrument
under the ratchet with its own self-test and owner. The cost test passes, so triage
decides the slot. It does not depend on A.

**Policy draft, owner approval required, not in this diff.** `fixer.md`, one line:
*"A claim that a self-triggering automation converges (cannot loop) is pinned by
iterating it to a fixed point over a recorded transition, never by a one-pass
null."* State (c). Proposed only.

## Carries

- To the sweep fixer (R10-SWEEP-SETTLE-LOOP), through the orchestrator:
  - Countermeasure A.
  - The harness as the finder's harness at both ends.
  - Notice that the current self-test passes a fixed arm 1, so a failing test
    first needs the recorded transition.
  - The design question in section 3: whether a re-run should require some input
    to have changed since its previous attempt.
- To proposal triage: countermeasure B, with section 4's numbers.
- To the tick's owner: `orchestrator_tick.py:1441` counts re-stamped or swept
  completions as worker CI activity (section 3). Not measured. A brief entry, not an
  issue.
