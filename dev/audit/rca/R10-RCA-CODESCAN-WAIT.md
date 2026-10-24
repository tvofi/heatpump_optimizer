# R10-RCA-CODESCAN-WAIT: an edit run's `pr-contract` goes red while the code run's codeql is still analysing

Root-cause seat, `root-cause.md`, 2026-10-24. Measured at `origin/main` `e97f5749b`
against the live Actions API between 13:59Z and 14:20Z. Nothing was fixed or written to
GitHub. Every figure below comes from the check-runs, runs or jobs API, or from a job
log. The commands are in section 4 and in
`dev/audit/harnesses/r10_codescan_wait_race.py`. The two estimates are marked as estimates.

## 1. What happened, reproduced

The brief names three instances: #2698 at `3383fb2a`, #2704 at `04860ee0` and #2706 at
`ea459c0b`. The check-runs API (`commits/<sha>/check-runs`) shows two mechanisms
among them, not one:

| PR, head | runs at the head (id, kind) | red check | exit path |
|---|---|---|---|
| #2698 `3383fb2a` | 40096445016 edit, 40096446203 code | `pr-contract / pr-contract` 120879819973 (edit run, 13:03:53 to 13:04:13Z), then `gate` 120879937381 (edit run) | `codescan_wait.py` step 1, `source()`: `FAIL closed: no run at this head owns a finished codeql unit for base 'main'`. The code run's `codeql / Analyze (python)` was in progress from 13:02:55 to 13:33:35Z |
| #2706 `ea459c0b` | 40099071633 edit, 40099071689 code | `pr-contract / pr-contract` 120887670093 (edit run, 13:41:45 to 13:42:10Z), then `gate` 120887888824 (edit run) | the same step-1 `Fail`. Python was in progress from 13:40:15Z to 14:10:37Z |
| #2704 `04860ee0` | 40096296956 code, 40096299978 edit | `gate` 120884717168 (**code** run, 13:27:07Z). Both `pr-contract` runs are `success` | **not `codescan_wait.py`**: `gate.py`'s defer rule, `FAIL run(s) [40096299978] at this head are still being judged; their gate decides`. The edit run's prelude was still waiting for the code run (13:00:38 to 13:28:09Z). The edit run's own gate was cancelled at 13:32:01Z because the next head, `859b74ba`, was pushed at 13:30:27Z |

So the `codescan_wait.py` defect accounts for 2 of the 3. #2704's red is the designed defer
rule (DESIGN-P2 4.1, "FAIL 'still being judged; their gate decides'"). Its run order was the
designed one, and the defer rule worked as written. The two mechanisms share one symptom
and one misreading, section 2.

**Which exit path fired: the log cannot say, and that gap is part of the finding.** The
step runs `codescan_wait.py ... > /tmp/pr-alerts.txt`. Under `set -euo pipefail`, exit 1
ends the step before the `printf` that would echo the file, so the `FAIL closed:` line
reaches no log. In both logs the only output between the command and `##[error]Process
completed with exit code 1.` is the env block (job 120879819973: 13:04:07.78Z to
13:04:10.45Z; job 120887670093: 13:42:03.92Z to 13:42:06.17Z). Three facts fix the path:

- **Elapsed time is 2.7 s and 2.2 s.** Step 4's `wait` sleeps `POLL_S` = 60 s before it can
  fail, so step 4 is ruled out. Steps 2, 3 and 5 cannot run without a source.
- **The edit run does not own codeql.** Its title is `CI edit ...`, and `prelude.workset("edit", pr)`
  is `{arch-score, budget-raise-gate, pr-contract}`. `source()` therefore searches other
  runs, and the one code run at the head had a codeql job still running.
- **Live reproduction.** At 14:00:11Z, with #2706's code-run python leg still `in_progress`
  (job 120887354588), this seat ran:

      env -u GH_TOKEN GITHUB_REPOSITORY=tvofi/heatpump_optimizer GITHUB_RUN_ID=40099071633 \
        python3 -I tools/ci/codescan_wait.py --pr 2706 --base main

  The output was `FAIL closed: no run at this head owns a finished codeql unit for base 'main'`,
  rc 1, in 3 s. **Null control**: the same command for #2704's edit run 40096299978, where
  every codeql job of the code run had completed, gave rc 0 with an empty list.
  `--self-test` printed `13 checks, 0 failed`.

## 2. The cause, named

**Cause.** The verdict ordering rests on run ids, and GitHub does not assign run ids in
the order the events happened. `app_push.sh` pushes the head and then edits the body
within the same second. That fires a `synchronize` (code) run and an `edited` (edit) run
at one head, and in 27 of 94 measured pairs the edit run got the **lower** id (section 4).
The edit run's prelude waits only for runs with a lower id
(`prelude.wait_earlier`: `r["id"] < ctx["run_id"]`), so it does not wait at all. Its
`pr-contract` then reaches `codescan_wait.py` step 1 while the code run's codeql is still
analysing, and step 1 fails at once. Only step 4 polls.

The design states the ordering as a guarantee, DESIGN-P2 (`archive/probe/design-ci-rev4`
`1371a0a6`), section 2.3: "**On `kind != code` the prelude waits** until every **earlier**
`ci.yml` run at this head has completed: every run with a lower run id ... waiting for
every earlier run needs no kind and orders the runs: each verdict run's `gate` is first
judged after every earlier run's `gate` has completed." Section 4.3 step 1 then relies on
that guarantee: "else the code run 4.1 would take `codeql` from (newest run at this head
... whose `codeql` jobs have completed). None → FAIL, as the gate would." The implementation
follows both exactly. `codescan_wait.py`'s self-test case 6 pins the FAIL as intended
behaviour: "no finished codeql unit at this head for an edit run FAILs".

**The premise was measured, but not in the unit the code keys on.**
`measure/rev/verdict_wait.py` on the design ref defines "an earlier code run" as one
"created at or before the verdict" (`t(r["created_at"]) <= t(v["created_at"])`). It
compares `created_at`, never `id`, and its sample (13 of 14 edits land "0-4 s after the
code event") comes from the layout before the umbrella, when the code and edit runs
belonged to different workflow files and their relative ids were irrelevant. At 0 s
apart, `created_at` cannot order two runs, and the id order is GitHub's.

**What else the same cause reaches.**

1. **The defer-rule red (the #2704 shape) is the same race seen from the other side.** It
   is designed: in an ordered pair the code run's `gate` defers to the later edit run. But
   it writes a red `gate` check at the head, which stays red until the later gate decides.
   Across the window, `gate` attempts whose log carries `still being judged` number 87 (45
   on code runs, 42 on edit runs) at 57 of 100 PR heads. This seat read each red `gate`
   job's log, `FAIL ` lines only. Whether `gate-sweep.yml` re-judged each of them green was
   **not checked**.
2. **The tick reads both reds as owed to the fixer.** `orchestrator_tick.py`'s `one_pr` takes
   the latest check run of each name (`self.latest(runs)`). While the code run's codeql
   is still analysing, the latest `pr-contract / pr-contract` at the head is the edit run's
   red one. When the required set includes it or `gate`, the tick prints "NOT REVIEWABLE
   ... concluded red -- back to its fixer, never a reviewer (K15 (d))". That is the false
   "back to fixer" the brief reports. The tick's output is not in the API, so this seat
   did not count the misreads. The brief's figure of 3 is reported, not measured.
3. **A hand re-run made too early fails the same way.** #2675 re-ran at 01:11:27Z, before
   its last leg finished at 01:25:47Z. #2696 re-ran at 11:33:49Z, before 11:38:20Z. Both
   failed again.
4. **Searched and not reached**: the review kind (`BODY_ON_REVIEW` = `budget-raise-gate`
   only) runs no `pr-contract`, so it never reaches `codescan_wait.py`. A label run owns no
   unit.

## 3. Process state

**(c) The process was followed and did not produce the intended result.**

- **The process.** The R10-CI-LAYOUT design went through five design-review rounds
  (`probe/design-ci-review5` `afc00bfe`, which approved rev4). Its premise was measured,
  and the race was even simulated: section 4.1's "rev2" and "rev3" notes record
  `gate_sim.txt`, `timing_perturb.py` and `rerun_tail.py`, scored "0 END-BAD on every arm".
  The fixer built U6 to the design. The U6 commit is `3ea7a4616`, which says "pr-contract
  becomes a workflow_call callee with the code-scanning wait". Its self-test pins the
  designed FAIL.
- **Obeyed, and wrong.** The perturbations varied timing. None of them varied which of
  two same-second runs gets the lower id. The measurement keyed on `created_at`, the code
  keys on `id`, and the design's sentence "orders the runs" equates the two.
- **Not (a).** The ordering rule exists and the design states it.
- **Not (b).** Nothing was skipped: the implementation matches DESIGN-P2 line for line,
  and the self-test asserts the designed outcome.
- **Not (d).** No precondition changed after the design. The umbrella's single
  `ci.yml`, which puts code and edit runs in one id sequence, is the design's own subject.
  The paired push and body edit is the flow the design measured ("13 of the 14 edits land
  0-4 s after the code event"). The inversion was possible from the first umbrella run.

The countermeasure therefore changes the **unit** the ordering keys on. It does not add a
firmer instruction.

**Root-cause trigger 2: a cheaper detector existed.** The failure was reachable at design
time, with no runner. A `verdict_wait.py` arm or a `gate_sim` arm that swaps the ids of a
same-second code and edit pair would have shown the edit verdict reading a codeql unit
that had not finished. One self-test case would have shown it too, in `prelude.py` or
`codescan_wait.py`: an edit run with the lower id beside an in-progress code run must not
go red. Either costs 0 s at runtime and under a second in `governance`'s self-test step.
The cheaper detector is therefore the self-test case, and case 6 as written asserts the
opposite.

## 4. Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

**Instances, measured.** Command, window fixed at its end:

    env -u GH_TOKEN python3 -I dev/audit/harnesses/r10_codescan_wait_race.py \
      --since 2026-10-22T00:00:00Z --until 2026-10-24T14:15:00Z --rows

It printed:

- 202 `ci.yml` pull_request runs. The earliest `ci.yml` run in the window was created at
  2026-10-23T05:35:36Z: the minimum `created_at` of `actions/workflows/ci.yml/runs?created=>=2026-10-22`.
- edit runs at a head with a code run: **INVERTED 27, ORDERED 67**.
- **RED edit runs: 13 INVERTED, 0 ORDERED.** That is 23 job attempts at 13 heads on 12 PRs:
  #2656, #2657, #2673 (two heads), #2675, #2681, #2690, #2692, #2696, #2698, #2706, #2707
  and #2709.
- RERUN attempts among the red: 10, of which **FRESH 2** (the job ran again and failed
  again: #2675 and #2696) and **CARRIED 8** (GitHub copied the red job into a re-run of
  other jobs, such as `gate-sweep`'s gate re-runs).
- Fresh re-runs that went green. These are not in the harness's red counts. This seat read
  them from `actions/runs/<id>/jobs?filter=all`: #2673 at `c4033588` (22:11:39Z) and at
  `ac6dc132` (23:43:24Z), and #2675 (01:30:16Z). That makes **3 green and 2 red of 5 hand
  re-executions**.

**The null control and the prediction hold.** No ORDERED edit run is red (0 of 67). Of the
14 INVERTED edit runs that are not red, 8 had every codeql leg completed before the edit
run's `pr-contract` started. A scope stand-down finishes in about a minute. One more
(`308d7386`, #2699) had a leg finish 11 s after the job started, before the wait step ran.
Four were still queued or running at read time (`ce69a3f2`, `49400254`, `dba7f86b` and
`ae77c415`). One (`d7505428`, #2649) had neither a `pr-contract` job nor a codeql leg. Every red head is INVERTED, and its
codeql had not finished when `pr-contract` started (`leg_unfinished True`, `--rows`).

**cost(defect), one instance.**

- The red check stays at the head until someone re-runs it after the code run's last leg
  finishes. Across the 12 red heads whose legs have finished, the time from the edit run's
  `pr-contract` start to the last leg's completion (`--rows`) runs from 0.4 to 29.7 min,
  with a median of 28.1 min. For 3383fb2a it was 13:03:53 to 13:33:35Z; for ea459c0b,
  13:41:45 to 14:10:37Z. A re-run inside that window fails again (2 of 5).
- One hand re-run plus one tick round that reads a false "back to fixer": **an estimate of
  10 min** of orchestrator attention per instance. The basis is the same as
  R10-HANDOFF-PREPR-BOUNCE's round trip. It is an input, not a finding.
- When the false "back to fixer" dispatches a fixer seat, the cost is a seat session. That
  is not measured.

**P(recurrence).** 13 instances in about 32.7 h of umbrella PR traffic (05:35Z
2026-10-23 to 14:15Z 2026-10-24), which is about 9.5 a day. 13 of 94 code-and-edit pairs
is 14 %. At 10 min each, that is **about 95 min a day**, for as long as heads keep arriving
in the push-then-edit pattern.

### Candidate countermeasures (not built here: carried, section 5)

| id | change | standing cost | passes? |
|---|---|---|---|
| M0 | do nothing | 0 | loses: about 95 min a day of attention, and false fixer dispatches |
| M1 | a verdict run's prelude waits for every **code** run at the head, whatever its id, not only lower ids (a code run never waits, so no cycle forms) | runner wait on 27 of 94 edit runs, the same wait the 67 ordered edit runs already pay (DESIGN-P2's measured verdict wait has a 1406 s median); no wall time on the merge path, where the code run's own gate decides | passes |
| M2 | `codescan_wait.py` step 1 polls, within its bound, for the code run's codeql to complete, instead of FAILing on the first read | none on a healthy head. But the 600 s bound is shorter than the 28.1 min median above, so the bound must grow, or the step must still fail on the slow leg | fails alone; M1 is the fix |
| M3 | the step echoes `codescan_wait.py`'s `FAIL closed:` line to the log (`tee`, or stderr), so the exit path is readable | 0 s | passes; repairs the instrument gap in section 1 |
| M4 | self-test cases: `prelude.py` (an edit run below a busy code run waits) and `codescan_wait.py` (case 6 restated as "an edit run whose code run is still analysing does not FAIL, because its prelude waited") | under 1 s in `governance` | passes; the detector owed by trigger 2 |
| M5 | the tick ignores a red `gate` whose log says `still being judged`, and a red edit-run `pr-contract` while a code run at the head is still running | one log or jobs read per red PR head per tick | owner's or orchestrator's call; not costed here |

## 5. Countermeasure: carried, not built

M1, M3 and M4 are the countermeasure for state (c). They change what the ordering keys on
and add the test the design lacked. They are carried to the group that owns the umbrella's
job graph, following the brief's routing (triage P62, `dev/programme/triage/s6-batch4.md#P62`):

Carry: R10-CI-LAYOUT-P2

`R10-CI-LAYOUT-P2` is on main's roster, `dev/programme/rosters/wave-r10-groups.json` at
`e97f5749b`, so no roster SHA is needed. The brief's triage citation does not resolve
here. `dev/programme/triage/s6-batch4.md` is not on `origin/main`. The one fetched ref that
carries it, `wip-sync/ext-wt-8aef46d4` `3545ece63`, lists P54 to P59 and no P62. This
record states that, and does not invent P62's wording.

The carried fix must demonstrate the following, as `defect-root-cause.md` requires for a
check-shaped countermeasure:

- M4's new case fails on `e97f5749b`'s `prelude.py` and `codescan_wait.py` (the inverted
  pair goes red) and passes once M1 is in.
- A null control: an ordered pair still waits exactly as today.
- The harness above, run before and after over a window that straddles the change, prints
  `RED ... 0 INVERTED` after it.
- M5 is the orchestrator's: `orchestrator_tick.py` is a seat instrument, not a CI unit. It is
  recorded here so the carried group can decide whether the umbrella removes its cause
  (M1 removes the codescan red, but not the designed defer red of the #2704 shape).

## 6. Not covered

- How many tick passes printed a false "back to fixer". The tick's output is not in the
  API.
- Whether every defer-rule red `gate` (87 attempts) was later re-judged green by
  `gate-sweep.yml`.
- Whether GitHub's id order for two same-second events is stable in any direction. 27 of 94
  is a rate over this window, not a mechanism.
- This defect is not in `dev/audit/config/bugclasses.json`. The nearest row,
  `N-p2b-assembly-reader`, is a reader meeting a sibling unit's change at assembly; here the
  premise was wrong inside one design. No row was added: the brief asks for the record, and
  registering a class is the judge's or orchestrator's call.
