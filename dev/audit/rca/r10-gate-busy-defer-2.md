# R10-RCA-GATE-BUSY-DEFER-2: a gate fix does not reach a run created before it merged

Root-cause seat (`dev/governance/roles/root-cause.md`), run beside the fixer of
R10-HOTFIX-GATE-BUSY-DEFER (topic r10-gate-busy-defer-2). First measured at
origin/main `294a880da`, which carries #3246's merge `355d9965a`, on 2026-11-07, and
re-cut against origin/main `b4ec2f332`, which also carries #3276's merge `812bb8747`
(R10-HOTFIX-GATE-BUSY-DEFER reopened: the edit/code-run half below). This seat
changed nothing in `tools/ci/`. The live figures are for the window
2026-11-07T03:45:14Z (#3246 merged) to 2026-11-07T04:50:21Z, and the harness prints
them again for any window.

## Result

- **Cause.** `ci.yml` restores `tools/ci/*.py` from the event payload's
  `pull_request.base.sha`. A re-run replays that payload. `refresh` (`gate.py`
  `refresh()`) and `gate-sweep.yml` (`sweep.py`) re-judge a gate through the
  job-rerun API, so each re-run of a run created before #3246 merged ran the
  programs #3246 fixed. Every mutual deferral since the merge ran those programs.
  The reported cause, "#3246's fix missed these shapes", is wrong. Replayed through
  the fixed `gate.py`, the listings GitHub served decide every pair.
- **#3263 is a second defect with its own cause, fixed by #3276.** Run
  42338396358's 2-second red is the edit/code-run deferral. It ran the program
  pinned `294a880da`, which carries #3246 and still had gate.py's at-once bound
  for a deferring edit gate (C3, `fa921fd59`; #3246 widened it). The bound was a
  workaround: `prelude.judging()` read the deferring edit run's skipped
  `pr-contract` caller, listed completed under its bare name, as an owed unit, so
  that run looked busy to every gate and prelude at its head, and a wait on it
  would have closed a cycle. #3276 (`812bb8747`) made `judging()` read such a
  caller as a unit the run never ran and deleted the bound. As of main now, the
  at-once red is an instance of that defect, not of #3246's race and not a
  design. Section 1 gives its cause, section 3 its process state, section 4 its
  cost, and the replay arm scores it (`C3-AT-ONCE` is a defect class).
- **Process state: (c), twice.** For the stale pin: the fixer's harnesses, the
  mutation proof and the review's step 11 all ran and passed. Their unit is one copy of the gate program
  per scene. The review read the live reds' `programs restored from <base>` lines
  and dismissed them until "this fix lands". Landing the fix does not reach those
  runs. For the at-once bound (section 3): the self-test case pinned the bound
  ("publishes the deferral at once"), the symptom, and not the property a
  deferring run owes, that it is judging.
- **Cost test: passes** for the countermeasure below, proposed and not built,
  because it edits `tools/ci/`. It costs one tree compare per re-run. Against it,
  21 red gates on 7 PRs in the first 65 minutes after the
  merge, and 3 gate-program fixes merged on main in the 7 days before.
- **Built.** `dev/audit/harnesses/r10_rca_gate_busy_defer_2.py` replays the real
  run and job listings of both evidence pairs, of one more pair and of three
  edit/code-run scenes through a chosen program copy. It is red at the three
  pinned bases the live gates ran and at `294a880da` (the C3 scenes), and green
  at `812bb8747` and at this tree. Its `census` arm sorts every gate since a time
  into pinned-stale and pinned-fixed.

## 1. The cause, reproduced

### What each live gate ran

Every `gate` job prints `programs restored from <sha>` (ci.yml's prelude and gate
steps, `PINNED: ${{ github.event.pull_request.base.sha || ... }}`). The `pins` arm
reads that line from each recorded gate's log and asks whether the sha carries
`355d9965a`:

    python3 dev/audit/harnesses/r10_rca_gate_busy_defer_2.py pins

| scene | gate run, attempt | started (Z) | pinned | carries 355d9965? | live verdict |
|---|---|---|---|---|---|
| #3261 pair | 42307493684 #8 | 04:25:54 | 28482ece | no | FAIL, defers to 42307798573 |
| #3261 pair | 42307798573 #8 | 04:25:45 | 28482ece | no | FAIL, defers to 42307493684 |
| #3265 pair | 42332777827 #4 | 04:06:14 | f2a01514 | no | FAIL, defers to 42333388705 |
| #3265 pair | 42333388705 #4 | 04:06:18 | f2a01514 | no | FAIL, defers to 42332777827 |
| #3255 pair | 42321825054 #5 | 04:40:16 | 80016a71 | no | FAIL, defers to 42322943199 |
| #3255 pair | 42322943199 #4 | 04:40:22 | 80016a71 | no | FAIL, defers to 42321825054 |
| #3263 C3 | 42338396358 #1 | 04:27:28 | 294a880d | yes | FAIL, defers to code run 42338396871 |
| #3261 C3 | 42338828285 #1 | 04:33:11 | 294a880d | yes | FAIL, defers to code run 42338828950 |
| #3241 C3 | 42338898175 #1 | 04:34:22 | 294a880d | yes | FAIL, defers to code run 42338897730 |

`RESULT pins gates=9 stale=6`. Each of the six mutual-deferral gates is a re-run
attempt (#4, #5, #8) of a run created before 03:45:14Z. The original runs were
created at 22:48Z and 22:51Z (#3261), 03:10Z and 03:18Z (#3265), and 01:02Z and
01:14Z (#3255). `github-actions[bot]` triggered them through `refresh` and the
sweep, according to the attempts API's `triggering_actor`. #3261's two runs reached
attempt 10, all at `28482ece`, and attempts 4 to 6 and 8 to 10 each deadlocked the
same way.

### The same listings through each program

The `replay` arm rebuilds each scene's run and job listing from the recorded job
timestamps, at the gate's first read (job start + 20 s). It then calls
`gate.judge()` from the program copy `--ci` names. The two gates of a pair overlap
in time, as they did live, and the arm refuses a fixture where they do not.

    for c in 28482ece f2a01514 80016a71 294a880d; do
      git archive $c tools/ci tools/pr | tar -x -C $D/$c
      python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_2.py replay --ci $D/$c/tools/ci; done
    python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_2.py replay      # this tree's tools/ci

| program | #3261 pair | #3265 pair | #3255 pair | three C3 scenes | rc |
|---|---|---|---|---|---|
| 28482ece (pre-fix) | DEADLOCK | DEADLOCK | DEADLOCK | C3-AT-ONCE, naps 0 | 1 |
| f2a01514 (pre-fix) | DEADLOCK | DEADLOCK | DEADLOCK | C3-AT-ONCE, naps 0 | 1 |
| 80016a71 (pre-fix) | DEADLOCK | DEADLOCK | DEADLOCK | C3-AT-ONCE, naps 0 | 1 |
| 294a880d (#3246's fix) | DECIDED: PASS, PASS after 1 nap | DECIDED: PASS, PASS | DECIDED: PASS, PASS | C3-AT-ONCE, naps 0 | 1 |
| 812bb8747 (#3276, main) | DECIDED: PASS, PASS (naps 0, 0) | DECIDED: PASS, PASS | DECIDED: PASS, PASS | DEFERRED, naps 12 | 0 |
| this tree's tools/ci (origin/main `b4ec2f332` merged) | as 812bb8747 | as 812bb8747 | as 812bb8747 | as 812bb8747 | 0 |

In every pre-fix row, the replay gives the same deferral ids the live logs print.
#3246's program decides all three pairs. The lower gate passes at once beside
the higher's started gate. Under that program, in #3261, the higher gate waits one poll, then passes. (Superseded at `5c1fa41fb`: that gate now publishes the deferral at once, and gate-sweep's `settle` re-runs it; `dev/audit/rca/r10-gate-defer-read-final.md` measures that program. §5.2's fresh dispatch stays needed, because `settle` re-runs through the same job-rerun API, so a re-run of a run created before a fix merges replays the old pinned program.)
Under #3276's `judging()` the higher gate no longer waits at all (naps 0 and 0).
Since #3287 (`5c1fa41fb`), no deferring gate waits: it publishes the deferral red at once,
and `gate-sweep.yml`'s `settle` re-runs it. The three pairs still decide through that
program (naps 0), and the c3 scenes read `C3-AT-ONCE`, which is now its design. The readers
that take that red as final, and a `settle` loop on content reds, are in
`dev/audit/rca/r10-gate-defer-read-final.md`.
None of the six live reds would have happened if the re-run had executed main's
`gate.py`.

The three C3 scenes read `C3-AT-ONCE` through `294a880d` and `DEFERRED` with
naps 12 through `812bb8747` and this tree. The 12 naps are the wait bound
(`GATE_WAIT_MAX_S` 720 s at `POLL_S` 60 s): the recorded code run had not finished
its units by then (29 minutes in progress at the recording), so the gate waited
the bound and then published the deferral for the sweep. That is the designed
bounded outcome. The replay cannot show the wait cycle `judging()` made, because
a single-gate scene judges one gate beside a code run listed as recorded; the
fixture self-test #3276 added to `gate.py` pins it.

### #3263: the at-once red, an instance of the defect #3276 fixed

Run 42338396358 is an edit run. Its prelude left `pr-contract` to code run
42338396871 (`WORKSET: arch-score budget-raise-gate`). That code run's `gate` had
not started. Under the program it ran (`294a880da`) `judge()` set the wait bound to
0 (`deferring(...) and not all(started(r) ...)`) and published
`FAIL run(s) [42338396871] ...` at once. The replay gives this verdict, with 0 naps,
under `28482ece`, `f2a01514`, `80016a71` and `294a880d`. The other two
fixed-pin reds in the window, on #3261's new head and on #3241, have the same
shape. This record first called the red designed because `gate.py`'s docstring
and #3246's own race harness (`prelude` scene, UNDECIDED-RED 1) both did.

**Cause.** The at-once bound dodged a cycle that `prelude.judging()` made. A
deferring edit run never expands `pr-contract`: GitHub lists its skipped caller
as `pr-contract` completed, under the bare name. `judging()` looked up the unit's
expanded job names, found them absent, and read the unit as owed. The deferring
run then never counted as judging, so it looked busy to every gate and prelude at
its head, and a gate that waited on it would wait on a run that waited on it. The
bound cut the wait, and published a red instead. #3276 (`812bb8747`) reads a caller
listed completed under its bare name as a unit the run never ran, and deletes the
bound and `deferring()`. Its tree is main's `tools/ci/prelude.py` `judging()` and
`tools/ci/gate.py`'s DEFERRAL docstring ("No gate is exempt from the wait"). That
cause is recorded in #3276's commit message and in that docstring; this record
adds the process state and the cost, which neither carries.

**What it cost.** A red `gate` on the PR until the code run's gate is listed. At
the recording, the code run had been in progress for 29 minutes. The census counts
3 such reds in the first 65 minutes after #3246 merged (the `fixed` row, all C3),
on PRs #3241, #3261 and #3263.

**Process state.** (c), as for the stale pin: a process ran and passed. The checks
that existed pinned the bound: `gate.py`'s self-test case "publishes the deferral
at once", #3246's `prelude` scene and C3's decision all treated the at-once red as the specification, and #3276 rewrote the self-test case from "publishes the deferral at once" to "waits on it, then judges". The property the bound stood in for, "a deferring run is judging", was
checked by none. Fixer step 11 asks a check to pin the artifact it reads, here the
run's listed state, and not the outcome the author expected. Not (d): the
`pr-contract` skip is C3's own design (R10-CI-SLIM, `fa921fd59`). Not (b): no rule
is missing; step 11 states this one. Not (a): the cheaper detector was the live red itself, read as designed.

**Countermeasure.** Landed by #3276, which deleted the bound and pinned the
property with a fixture self-test of the recorded listings (a pin on the artifact
read). This seat's `replay` arm now scores `C3-AT-ONCE` as a defect: rc 1 at
`294a880d`, rc 0 at `812bb8747` and this tree. Standing cost: none; the arm runs
no gate and no CI lane (section 4). Until this pull request merged, the arm
was blind to it: `classify()` returned the single-gate scene's class but only
`DEADLOCK` and `HALF-DEFERRED` set the exit code, so at `294a880d` the at-once red
read rc 0. That blindness is fixed, in the same pull request, by `DEFECTS`.

## 2. Why the harnesses, the mutation proof and the review passed it

- **`r10_gate_defer_race.py`** builds every scene by hand: `2754`, `2754-red`,
  `editcode`, `pair`, `cascade`, `single` and `prelude`. `Head.__init__` puts one
  `--ci` directory on `sys.path` and imports `prelude`, `gate`, `ghapi`,
  `codeql_scope` and `sweep` from it. Every run in a scene is judged by the same
  copy. No scene gives a run the program of its own base, so in the harness "the fix
  is in `tools/ci`" means "every gate runs the fix".
- **`r10_ci_gate_core.py`** compares the port against the design model (`replay`,
  `sim`). It also mutates the single in-tree `gate.py`/`prelude.py`, one mutant at a
  time (`mutants`, 23 rows, 0 survivors). The mutation proof answers "does a test
  see the predicate move". It does not ask which copy of the predicate a live run
  executes.
- **The review** (`origin/verdict/3246`, verdict `merge 2a0d228c`) read the live
  reds at the PR's own head. Attempt 2 of both edit runs printed
  `programs restored from b36679ce...`, and the verdict concluded: "main's gate
  cannot judge this mutual pair until this fix lands". The fixer's body gives the
  same key: "a `gate` red reading `programs restored from <base>` with a mutual
  `FAIL run(s)` deferral is the same pinned-main defect". Both name the signature
  correctly. Both assume that landing the fix changes what such a run executes on
  its next attempt, and it does not. A run's pin is its payload's `base.sha`, fixed
  when the run is created. The fixer and the reviewer each saw this shape twice
  before the merge (attempt 2 at 8af5fa58 pinned 5421413b, and at 2a0d228c pinned
  b36679ce), because #3246's own PR's re-runs were pinned to pre-fix bases.

## 3. Process state: (c)

For the stale pin, the process is `fixer.md` step 3 (the finder's harness at both ends), step 2 (the
mutation proof), and `fix-review.md`'s reading of every red check. It existed, it
was followed, and it measured correctly what it measures, which is the gate
predicate in one program copy. It did not produce the intended result, "the red
stops once this merges", because its unit leaves out where the program is
deployed. The predicate is fixed at `main`. The executed copy is fixed per run, at
the run's creation. The signature of the gap was read and recorded, and it was
attributed to the defect itself.

The other states were ruled out:

- **Not (d).** The pin from the payload is not new. It dates from `85d13b859`
  (2026-10-23, the CI umbrella), before #3246 and before the R10-GATE-DEFER design.
  Nothing changed underneath the process.
- **Not (b).** No rule asks a fixer of a pinned program whether the fix reaches runs
  that are already open.
- **Not (a).** The checks that would have shown it existed and ran: the fixer's
  body and the review both read the `programs restored from` line.

**Reach of the class.** Every program ci.yml restores from the base is in the
class: `tools/ci/*.py`, `tools/pr/codeql_scope.py` and `tests/closure.py` (the
prelude and gate restore), `tools/pr/cancel_superseded.py` and the `refresh`
restore. A fix to any of them takes effect only for runs created after it merges.
A re-run of an older run replays the old behaviour, and does so until
`ATTEMPT_CAP` (45) or a new push. The class search
(`git log --first-parent --since=<d> origin/main -- 'tools/ci/*.py' tools/pr/codeql_scope.py tests/closure.py tools/pr/cancel_superseded.py`)
returns, at origin/main `b4ec2f332` on 2026-11-07 (15:02Z), 30 first-parent commits since `2026-10-23T00:00:00Z` and 15 since `2026-10-31T00:00:00Z`. `git log --since` anchors a bare date at the current time of day, so the time is written; the count still grows with each merge to those paths, so the record relies on the order of magnitude and on the rule. Over `tools/ci/gate.py` and `tools/ci/prelude.py` alone, the same rule returns 4 merges since `2026-10-31T00:00:00Z`, each a fix to a red `gate`: #3205 (R10-HOTFIX-GATE-STALE-JOBS), #3230 (R10-CI-SLIM), #3246 and #3276. A fix to a grader that a PR's `pr-contract` re-run
reads has the same reach. `pr-contract.yml` already avoids the payload base for
the main ref ("THE MAIN REF IS FETCHED, NOT THE PAYLOAD'S `base.sha`: a re-run
replays the payload"), so the hazard is known in one workflow and not handled in
the other.

## 4. Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

**The defect, measured once.** Census rule: every `gate` job that started in the
window on a ci.yml run. A gate is pinned stale when its `programs restored from`
sha lacks `355d9965a`, pinned fixed when it carries it, and unpinned when it has
no such line (push runs, cancelled jobs). Command:

    python3 dev/audit/harnesses/r10_rca_gate_busy_defer_2.py census \
      --since 2026-11-07T03:45:14Z --until 2026-11-07T04:50:21Z

    CENSUS stale: gates=46 {'defer': 21, 'other-red': 1, 'pass': 24} prs=['pr=3232', 'pr=3241', 'pr=3255', 'pr=3261', 'pr=3265', 'pr=3271', 'pr=3273'] reruns=36 defer_job_s=685
    CENSUS fixed: gates=3 {'defer': 3} prs=['pr=3241', 'pr=3261', 'pr=3263'] reruns=0 defer_job_s=81
    CENSUS unpinned: gates=5 {'cancelled': 4, 'other-red': 1} prs=[] reruns=3 defer_job_s=0

36 of the 46 stale gates were re-run attempts (attempt > 1).

Within 65 minutes of the merge, the stale gates published 21 deferral
reds on 7 PRs. The fixed gates published 3, all of them the at-once edit/code-run red of section 1, and no mutual deferral. Null control: had the fix not
reached new runs either, the fixed row would hold mutual deferrals, and it holds
none. Had the census called everything stale, the fixed row would be empty, and it
holds three. Each stale mutual pair stays red until a new push creates a fresh run.
For example, #3261 at `7871b3e3` was re-run to attempt 10 and was cleared only by
its new head `f984b187` at 04:31Z. While a pair stays red, `merge_train.py
classify` reads the head as `RED ... red: gate`, as the #3246 review's
`classify_log.txt` recorded at that PR's head. This seat did not measure reviewer dispatches delayed: no API records
them, and the bus log is not in this tree.

**P(recurrence).** 4 merges to `gate.py`/`prelude.py` since `2026-10-31T00:00:00Z`, each a gate fix merged while PRs had open runs (section 3), and 30 commits to pinned programs since `2026-10-23T00:00:00Z` (the rule and the tip are section 3's). Every one of them leaves the open PRs' re-runs on the
old copy.

**The countermeasure's standing cost.** Before `refresh` or the sweep re-runs a
`gate` job, they compare the run's pinned base (the sha its gate log's
`programs restored from` line printed, which is the payload's `base.sha`) with the base tip, over the
restored paths. One `git diff --quiet <pin> origin/<base> -- <paths>` in a full-history checkout
took 0.0035 s here (`28482ece` against `294a880d`, rc 1, the trees differ; the same
sha on both sides gives rc 0, the null). It is paid only on
re-runs, not on every gate. When the trees differ, the re-run is replaced by a
`workflow_dispatch` of ci.yml with `pr=N base=<base>`. ci.yml already pins that
event to `origin/<base>` (its `INPUT_BASE` branch), and `gate()` already refuses a
dispatch that does not name the open PR headed by its SHA. That costs one fresh run in place of a re-run of one job, about the
code-run length once per open PR per pinned-program merge. A re-run that replays a
fixed defect costs that run anyway, plus the red.

Unit, per gate-program merge: under 0.01 s of compare per re-run, against the window's
21 red gates on 7 PRs, each of which needs a fresh push or a
manual dispatch to clear. **The test passes.**

The harness costs nothing standing. It runs no gate and no CI lane. Its `replay`
arm takes 0.08 s wall (`date +%s.%N` around it).

## 5. Countermeasure

### 5.1 Built: the real-listing replay, shown failing and passing

`dev/audit/harnesses/r10_rca_gate_busy_defer_2.py` and its fixture
`r10_rca_gate_busy_defer_2.json` (sha1 f926d6a67b5582c172f49cb436a09e7ff7b63b70,
recorded 2026-11-07T04:47:56Z by `record`). It addresses state (c)'s unit: it
judges listings GitHub actually served, and it names the program copy.

- **Red on the defect:** rc 1 at `28482ece`, `f2a01514` and `80016a71`, the three
  bases the live gates ran (DEADLOCK on all three pairs), and rc 1 at `294a880d`
  (`C3-AT-ONCE` on the three edit/code-run scenes, the pairs DECIDED).
- **Green on the fixes:** rc 0 at `812bb8747` and at this tree's `tools/ci`
  (origin/main `b4ec2f332` merged): DECIDED on all three pairs, DEFERRED with
  naps 12 (the bounded wait) on the three C3 scenes.
- **Null controls:**
  - Scoring: a copy of the harness with `DEFECTS` reduced to `("DEADLOCK",
    "HALF-DEFERRED")` (the harness as first handed off) gives rc 0 at `294a880d`;
    the unmutated copy, relocated the same way, gives rc 1. The arm moves.
  - The C3 scenes read `C3-AT-ONCE` with naps 0 under every program before
    `812bb8747` and `DEFERRED` with naps 12 after it, so the class tells the at-once
    publication from the bounded wait.
  - Mutant M17 (busy()'s tie-break deleted) on this tree's `gate.py` **survives**
    the arm at this head: rc 0, the three pairs DECIDED. Under #3276's `judging()`
    the pair no longer reads each other busy, so the tie-break is not what decides
    these listings, and `gate.py --self-test`'s M17 row pins it. M24 (`all` to `any`
    in the bound) names code #3276 deleted and is not run. The arm does not replace
    the self-test.
  - The arm refuses, and does not go green, on a fixture whose pair gates did not
    overlap, and on a gate that never started.

It can run against any proposed `gate.py` (`--ci`), and a fix to the gate can be
re-proven on real listings before it merges.

### 5.2 Proposed, not built: re-judge a stale-pinned gate with a fresh run

This change is in `tools/ci/` (`gate.py` `refresh()` and `sweep.py`), and this seat
may not edit `tools/ci/gate.py`. Its owner is the gate's fixer and the orchestrator.

> Before a job re-run, compare the run's pinned base with the base tip over the
> restored paths. If they differ, dispatch ci.yml with `pr=N base=<base>` instead,
> and print `STALE-PIN <pin>: re-judged by a fresh run`.

The detector for this change is the `census` arm. After a pinned-program merge, it
shows stale reds that the next re-run cycle still leaves. With the change, a stale
pin is never re-run, so the stale row's `reruns` count drops to 0 after the merge.

### 5.3 Until then, the operational step

After merging a change to a pinned program, dispatch ci.yml
(`workflow_dispatch`, `pr=N`, `base=main`) for each open PR whose latest gate is
red with a `programs restored from` sha that lacks the merge. The census arm lists
them. A re-run of the old run does not clear them.

### Refused

- **Re-running harder, or raising `ATTEMPT_CAP`.** Every attempt replays the same
  copy. #3261 reached attempt 10 with nothing changed.
- **Pinning to `origin/<base>` at job time instead of the payload's `base.sha`.**
  That would make every grader judge with a base newer than the one the PR was
  checked against, which is the stamp trap `pr-contract.yml` documents. It would
  also let a merge to main change a verdict mid-run. A fresh dispatched run keeps
  one base per run.
- **A self-test case for "the fix reaches old runs".** That property is the
  workflow's, not `gate.py`'s. No in-process test of `gate.py` can see it.

## Carries

- To the R10-HOTFIX-GATE-BUSY-DEFER fixer (topic r10-gate-busy-defer-2) and the
  orchestrator: #3263's red was not designed; #3276 fixed it, and section 1 records
  its cause, process state and cost. Another change to busy() or judge() cannot
  remove the six stale reds, because they never ran busy() as it stands on main.
  Re-prove any gate change with `replay --ci <export>`; `C3-AT-ONCE` now fails it.
  Since #3287 made the at-once deferral the design, `replay` exits 1 at main on the
  three c3 scenes alone: read their `C3-AT-ONCE` as that design, not a regression
  (`dev/audit/rca/r10-gate-defer-read-final.md` section 3).
- To the orchestrator, now: #3265 and #3255 at their recorded heads, and any other
  PR the census lists as stale-red, need a fresh dispatched run (5.3), not a
  re-run.
