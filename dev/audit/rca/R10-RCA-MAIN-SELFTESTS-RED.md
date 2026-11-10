# R10-RCA-MAIN-SELFTESTS-RED: main's instrument-self-tests stayed red from #3315 on

This is the root-cause seat for the defect R10-HOTFIX-MAIN-SELFTESTS fixes. It
follows `dev/governance/roles/root-cause.md` and
`dev/governance/rules/defect-root-cause.md`, ran beside that hotfix and never
inside it, and edits no production code. Measured at `origin/main` `0362916ac`
(2026-11-10, after the push run of `57091a694` concluded). Run and job figures
come from the Actions API; the local reproductions name their commands.

## 1. The defect

`governance / instrument-self-tests` concluded `success` on no push to `main`
from #3315's merge (`ba6fd7e8b`, 2026-11-09T08:16Z) to `57091a694`
(2026-11-10T04:47Z). Over that span `main` took 36 commits after
`ba6fd7e8b` (`git log --first-parent --format=%h ba6fd7e8b..0362916ac | wc -l`),
so 37 pushes counting #3315's own.

The 36 push runs of `ci.yml` in the window fall into three phases. Each
row's run ids are `list_workflow_runs` of `ci.yml`, `branch=main`,
`event=push`; each step name and line is from that run's
`governance / instrument-self-tests` job log. The baseline before #3315,
`0a8033305` (run 42573791732), concluded `success`.

| phase | pushes | conclusion | what the log shows |
|---|---|---|---|
| P1: #3315 `ba6fd7e8b` to `3aac11dfb` | 27 | 23 `cancelled` (timeout at 60 min, or by hand), 4 `failure` | "Install strace for the read-set measurement" fails with `sudo: The "no new privileges" flag is set, which prevents sudo from running as root.`; the five background waiters fail on `.../bg/lib.sh: No such file or directory`; every cancelled run stops inside "Refuse a self-test read set the committed table misses" before it prints. The 4 that concluded (`6d660061d`, `72a2acee5`, `53f4a051b`, `b8f67a775`) print `selftest_scope check: 106 gated step(s), 39 refusal(s)` (the first three) and `108 gated step(s), 47 refusal(s)` (`b8f67a775`), most of them `UNMEASURED` |
| P2: #3375 `2cf0f129b` to `5ab6030d7` | 5 | `failure` | only "Refuse a self-test read set the committed table misses": `109 gated step(s), 37 refusal(s)` (3 runs), then `38` (2 runs, `sweep-template` added), all `UNDER-SCOPED`, `push-names-the-host` among them |
| P3: #3361 `8652aa65c`, `57091a694` | 2 | `failure` | adds "Show the self-test scope ... refusing its own fixtures" (`FAIL the live job parses (118 steps) and its gating is consistent`), "Show the self-test scope refusing each mutant of its trace rules" (`BASELINE RED: the unmutated self-test fails`), and an `UNGATED step 'Show the workflow read runner refusing its own fixtures'` line in the drift step; `39` then `38` refusals |

Two runs (`e3295ba46`, `0362916ac`) were still in progress at the read.
Phase P1's refusal count is not a measurement of drift: with strace absent
the steps ran untraced, and the check reads the missing traces as
`UNMEASURED`. P2 is the first phase whose figure measures drift.

No job log in the window holds `exists on disk, but not in`, a failing
`git show` or a `ref_privacy` refusal: cause 2b below never failed as an
error, it showed only as a drift refusal of step `push-names-the-host`
(present in P2 and at `8652aa65c`, absent at `57091a694`; this seat did not
establish why it is absent there, and claims nothing from it).

## 2. The named causes, reproduced

The brief named three causes; the run logs add a fourth that came first
(2d). All four are reds of one job whose design (#3315, R10-CI-SELFTEST-SCOPE)
measures the read-set table on `main` only, which is why the analysis below
treats them as one defect with one process.

### 2a. Table drift: `tools/ci/selftest_closures.json` misses what steps read

The drift check (`selftest_scope.py check`, step `drift`) runs on every push
to `main` and refuses any gated step whose committed entry misses a file,
probe, directory or flag the push run measured. At `57091a694` (run
42758119155, job 129637321760) it printed
`selftest_scope check: 109 gated step(s), 38 refusal(s)`: 37 `UNDER-SCOPED`
lines and the UNGATED line of 2c.

Which side moved, by `git log`: the missed paths are files `main` added or
newly imported after the table was recorded, not files the table once named.
`git log --diff-filter=A --format='%h %ad' --date=short -1 -- <path>` per
missed path: `tools/audit/seat/topic_grammar.py` a7fd743e5 2026-11-08,
`tools/audit/seat/gh_read_run.py` e79a0e78b 2026-11-08 (#3361),
`tools/audit/seat/bottleneck_check.py` 7f28b6433 2026-11-07,
`tools/audit/seat/hooks_setup.py` f0c6bbfd7 2026-11-07,
`tests/mutation_ledger/killed_by/heat_curve.py` d7d4c511b 2026-11-08,
`tools/ci/selftest_scope_mutants.sh` f27e09c38 2026-11-09. The table moved
less: its last change on `main` is #3375 (`2cf0f129b`), which added one step's
entry (108 to 109 steps, `git diff --stat 2cf0f129b^1 2cf0f129b --
tools/ci/selftest_closures.json`: 26 insertions, 0 deletions) and re-recorded
no other. Nothing re-recorded the table wholesale after #3315 merged.

The measurement the repair needs already existed on every red push: the
`drift` step's `--write` uploads the run's own measured table as the
`selftest-closures` artifact (run 42758119155: artifact 13737009763). The
docstring of `tools/ci/selftest_scope.py` states the repair as
"`--write` saves the run's own measurement, which main uploads as the
`selftest-closures` artifact: commit that file, or re-record with `record`
(Linux, strace)". No seat, job or tick names who commits it. The hotfix brief
does it by hand: R10-HOTFIX-MAIN-SELFTESTS step 3, "Union
tools/ci/selftest_closures.json with main's later measurements, artifacts
13735714488 and 13737089304".

The drift is not a one-off of #3315's landing. #3315's own branch re-recorded
the table three times while it was open because `main` moved under it:
`2ff33ff92` ("re-record the 47 steps main's delta reaches"), `d9990a12f`
("gate main's new gantt-drift self-test step and record its read set"),
`a751546c5` ("gate main's plan-public, outside-intake and hooks-setup
self-test steps and record their read sets").

### 2b. A read set that moves every merge: `ref_privacy.added_lines`

`tools/audit/seat/ref_privacy.py` `added_lines` runs `git show REV:path` for
both sides of every path `git diff --name-only base ref` lists. For a path
absent on one side, git does not stop at the object store: to print
`fatal: path '<p>' exists on disk, but not in '<rev>'` it stats the worktree
path. So every step that calls it reads the push's own added and deleted
files, and no committed table can ever hold that set.

Reproduced at `origin/main` with `strace -f -qq -e trace=%file git show
<rev>:<path>`:

- absent side (`HEAD~400:tools/audit/seat/gh_read_run.py`, a file added
  later): the trace holds `"tools/audit/seat/gh_read_run.py"`, the worktree
  path, beside the revision spec;
- present side (`HEAD:tools/audit/seat/gh_read_run.py`), the null control:
  only the revision spec; no worktree path is touched.

On `main` this showed as an `UNDER-SCOPED` refusal of step
`push-names-the-host` (phase P2), never as an error: `added_lines` captures
git's stderr and reads an absent side as empty, so the step passed and only
its read set moved.

`selftest_scope.py`'s docstring lists the class as a stated blind spot ("a
step whose behaviour depends on the environment rather than the tree is not
scoped by any table"); `added_lines` is an instance whose environment is the
event's diff. The hotfix's fix (show only the sides that exist, from
`--name-status`) is R10-HOTFIX-MAIN-SELFTESTS's, not this seat's.

### 2c. #3361 landed an ungated step

#3361 (`8652aa65c`, merged 2026-11-10T04:34Z) added the step "Show the
workflow read runner refusing its own fixtures" with `if: ${{ !cancelled()
}}`, which reads no `steps.scope.outputs.<id>`.

Reproduced with `python3 -I tools/ci/selftest_scope.py --self-test` in
detached worktrees:

- at `5ab6030d7` (`8652aa65c^1`): `selftest_scope self-test: 103 checks, 0 failed`;
- at `8652aa65c`: `FAIL the live job parses (118 steps) and its gating is
  consistent`, `103 checks, 1 failed`.

**This red was visible on #3361's own pull request and merged anyway.** Run
42748431595 ("CI code pr=3361", head `825f54927`, the merged head) concluded
`failure` with one red job, `governance / instrument-self-tests` (job
129632432183), at one step: "Show the self-test scope
(tools/ci/selftest_scope.py) refusing its own fixtures". #3361's body names
no such red: its `## Red checks` answers only a `gate` deferral, and it states
`CI PREDICT: no closures, fast, governance or instrument red predicted`, a
figure taken against `51cd5ec8a`, before #3315 landed the gating check it
later failed. Two rules let that through as written:

- `instrument-self-tests` is not a required context (`governance.yml`: "not
  a required name");
- "Only a red on a required check is owed an answer (tvofi, 2026-11-07)"
  (`defect-root-cause.md`, Enforcement). So no reviewer verdict was owed a
  block on it.

### 2d. The push-only arm first ran on `main`

Everything #3315 added for a push (the `strace` install step, the tracing
wrapper `tools/ci/selftest_step.sh` under `SELFTEST_TRACE`, the `drift`
step) runs only when `github.event_name == 'push'`, which a pull request
never is. Its first execution was #3315's own merge. There, "Install strace"
failed on the runner's no-new-privileges sudo (phase P1, quoted above), the
launcher step was skipped after it so every waiter read a `lib.sh` no step
wrote, and the untraced job hit its 60-minute push timeout. The workflow
comment records the push path as "measured locally: about 34 minutes for
both", on a Linux host where sudo works. #3375 (`2cf0f129b`,
R10-HOTFIX-SELFTEST-SCOPE-HANG) repaired it: `f27e09c38` "untraced ungated
steps", and `if: ${{ !cancelled() }}` on the launcher with the comment
"without its launcher each read a lib.sh no step wrote (run 42623897209)".
So phase P1 hid 2a for 27 pushes: the drift step could not report.

## 3. The process state: (c)

**(c) The process was followed and did not produce the intended result.**

The process is #3315's own design for keeping the table true, quoted from
`.github/workflows/governance.yml` (job `instrument-self-tests`): "a push to
main runs each under strace ... and refuses a table that misses what it read
(`drift`), so a wrong closure turns main red within one merge", with its
repair stated in `selftest_scope.py`'s docstring (quoted in 2a), and the
orchestrator tick's main-red arm as the trigger for a repair seat
(`tools/audit/seat/orchestrator_tick.py` `red_brief`: "A main-red lane
becomes a FIXER DISPATCH BRIEF, required or not").

- **Present and obeyed.** The `drift` step ran and refused on every push run
  that reached it; the artifact was uploaded; the tick's arm produced
  dispatch briefs, and the orchestrator dispatched two hotfix seats and this
  RCA seat against this one job inside the window:
  R10-HOTFIX-SELFTEST-SCOPE-HANG (#3375, merged 2026-11-10T01:47Z) and
  R10-HOTFIX-MAIN-SELFTESTS (in progress).
- **Wrong result.** The design converts drift into a red `main` and then into
  a fixer seat. The drift rate is a property of ordinary merges (2a: six
  missed paths added by six commits over 2026-11-07 to 2026-11-09; #3315's branch
  re-recorded three times in its own life), while a hand repair is one fixer
  cycle and lands a table measured at a base `main` has already left. So the
  repair is outrun: no push in the window concluded green.
- **Why the PR-side gates did not stop 2c.** Each was obeyed. The job is
  non-required by design; the answer rule covers required reds only; and
  `tools/pr/ci_predict.py` predicts `instrument-self-tests` reds through three
  hand-added arms (REF PRIVACY, WIRING, SEAT MUTANT SELF-TEST), each written
  after an earlier escape, and none for `selftest_scope.py`'s own gating
  check. `prepr.sh` exited 0 at #3361's head (its body, `## Head`).

**Not (a).** A process existed for every arm: detection (`drift`), a stated
repair (commit the artifact), and a trigger (the tick's main-red brief). They
ran.

**Not (b).** No seat skipped a step it owed. #3361's red was not owed an
answer under the 2026-11-07 ruling; the hotfix seats were dispatched as the
tick briefed them. A firmer instruction ("commit the artifact", "answer every
instrument red") would be obeyed and still be outrun by the merge rate for
the first, and contradict an owner ruling for the second: the (c)-as-(b)
error `root-cause.md` section 2 warns of.

**Not (d).** No precondition moved after the design was made: the merge rate
and `main`'s habit of adding imported tools were already visible on #3315's
own branch (its three re-records), before it merged.

## 4. How far the class reaches

The class is **a gated step's measured read set that is false on `main`
without a seat writing it**. Three shapes, each with the rule that enumerates
it.

1. **Tree drift (2a).** Enumerator: the `drift` step itself on any push,
   `python3 -I tools/ci/selftest_scope.py check --traces DIR`. At `57091a694`
   it returns 38 refusals over 109 gated steps (the run's own summary line).
   Every one is this class; none is closed by anything but a re-record.
2. **A read set that is a function of the event, not the tree (2b).**
   Enumerator, static: files that both list a diff's names
   (`--name-only`, `--name-status`, `diff-tree`) and run `git show REV:PATH`:

       for f in $(git grep -lE '"show", *f"\{' -- tools tests); do
         grep -qE -- '--name-only|--name-status|diff-tree' "$f" && echo "$f"; done

   It returns 23 files at `0362916ac`. It over-approximates (a file may list
   names and show a fixed path); which of them a gated step reaches with an
   absent side is what the `drift` step measures, and its refusals at
   `57091a694` name the `.gitattributes` and `dirs` probes of the push's own
   new paths under steps `temp-or-machine-path`, `throwaway-git-helper`,
   `policy-lint-mutants`, `prepr` and `beatd`. A second instance, not of the
   `git show` shape, is named by the hotfix brief: beatd's recorded read set
   (80, 20 and 235 files across three runs) is suspected timing-dependent
   (R10-HOTFIX-MAIN-SELFTESTS step 4). Disposition: both are the hotfix's;
   the other files the static rule returns are unreached by any refusal and
   carry no finding.
3. **A step added or changed without its gating (2c).** Enumerator:
   `selftest_scope.wiring_gaps(selftest_scope.workflow_steps(root))`. It
   returns one gap at `8652aa65c` and none at `5ab6030d7`. Two earlier PRs
   added steps after #3315 and gated them themselves (`977fd0033`
   topic-grammar, `bb84b1bd2` bottleneck alert), so the rule was known and
   usually kept.

The same symptom recurs in round 10 independently of #3315: the roster on
`handoff/audit-r10-roster` holds four main-red hotfix groups on this one job,
R10-HOTFIX-SELFTEST-TIMEOUT (#3275, merged 2026-11-07T23:39Z),
R10-HOTFIX-MAIN-IST-RED (#3307, merged 2026-11-08T06:58Z),
R10-HOTFIX-SELFTEST-SCOPE-HANG (#3375) and R10-HOTFIX-MAIN-SELFTESTS. Only the
last two are this design's.

## 5. The cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

Unit: wall-clock, per occurrence, over the round.

**cost(defect), this occurrence.**

| measure | value | how measured |
|---|---|---|
| main pushes with no green instrument-self-tests | 37 | `git log --first-parent` above, run table section 1 |
| span red or unconcluded | 20.5 h (08:16Z to 04:47Z next day) and open at the tip | run `created_at`, section 1 |
| hotfix and RCA seats dispatched on it | 3 (SCOPE-HANG, MAIN-SELFTESTS, this) | roster |
| a new cause landed under the standing red | 1 (#3361's UNGATED, 2c) | run 42748431595 |
| one traced push run | up to 60 min of runner per push | job `timeout-minutes` for `push` |

Each hotfix seat is a fixer cycle plus a review; the window's two hotfix
merges (#3307, #3375) are not re-timed here. The masking cost is the one that
compounds: while the job is red at `main`, a pull request's red on the same
job reads as inherited, and the one-step red that was #3361's own landed.

**P(recurrence).** Of the drift shape: every merge that adds a file a gated
step imports or lists re-drifts the table. Measured in the window: six
missed paths were added by six commits over 2026-11-07 to 2026-11-09 (2a);
the first fully traced phase (P2) grew from 37 to 38 refusals within three
pushes (`sweep-template`, at `b07627250`); and #3315's branch needed three
re-records while it was open (2a). So, without a
mechanical repair, the measured rate is about one drift per day at the
round's merge rate, and P(a drift after any hand re-record lands) is close to
1 within a day. Of the ungated-step shape: 1 of 3 PRs that added a step after
#3315 (`977fd0033`, `bb84b1bd2` gated; #3361 did not).

**Countermeasure A: commit the measured table mechanically.** On a push to
`main` whose `drift` step refuses only `UNDER-SCOPED` or missing-entry lines,
a job downloads the `selftest-closures` artifact and pushes it to the
`record/autofix` branch, the route `nightly.yml`'s record-autofix already
uses (force-with-lease on `refs/heads/record/autofix`, one PR to `main`).
Standing cost: zero on a green push (skipped by `if:`); on a drifted push one
short job of a checkout, an artifact download and one push (the run's
artifact is already written: run 42758119155 spent 0.3 s uploading 34857
bytes). Its merge rides the record PR's route: #3393 (a `record/autofix` PR)
took 148 min open-to-merge with no seat time. Against an occurrence of 20.5 h
red and three seats, at a recurrence of about one per day, A passes the test.
It addresses state (c): the process stays, its repair arm stops depending on
a seat outrunning the merge rate. It needs `.github/workflows/` (code-owned),
so it is a proposal for the owner, not built here. Its detector arm owes the
demonstration `defect-root-cause.md` requires: on a drifted push it opens a
record PR whose table makes the next `check` pass; on a clean push it does
nothing.

A cannot repair shape 2 (the event-dependent set re-drifts every push) and
must not try: a record of the push's own diff paths makes the table name
paths no other push reads. Its `if:` keys on the refusal lines, and a step
whose missed paths are the push's own added files is the fixer's
(R10-HOTFIX-MAIN-SELFTESTS), not the bot's.

**Countermeasure B: predict the ungated step before the PR.** A
`tools/pr/ci_predict.py` arm that runs
`selftest_scope.wiring_gaps(selftest_scope.workflow_steps(root))` on a diff
touching `.github/workflows/governance.yml`, predicting an
`instrument-self-tests` red per gap, in the same shape as its WIRING arm.
Standing cost: the whole self-test runs in 0.79 s locally
(`python3 -I tools/ci/selftest_scope.py --self-test` at `8652aa65c`, wall
clock), and the arm calls one function of it; `ci_predict.py` takes 3.1 s at
that tree. Against one masked landing in three step additions, B passes.

Demonstrated with a scratch probe calling that function (not committed:
`wiring_gaps` is production, the probe only drives it):

- at `8652aa65c`: `wiring_gaps: 1 ["UNGATED step 'Show the workflow read runner
  refusing its own fixtures': its if: does not read steps.scope.outputs.<its
  own id>"]`, rc 1;
- at `5ab6030d7` (null control): `wiring_gaps: 0 []`, rc 0;
- at `8652aa65c` with that step given `id: gh-read-run` and
  `if: ${{ !cancelled() && steps.scope.outputs.gh-read-run == 'true' }}`
  (the fix, applied in scratch and reverted): `wiring_gaps: 0 []`, rc 0.

B addresses the same state (c): a gate that ran (`ci_predict.py`) and
predicted no red because none of its arms read this step's check.

**2d: no countermeasure, recorded.** The cheaper detector for a push-only arm
that breaks on the runner is running that arm before the merge: a
`workflow_dispatch` of the job with the push path forced on, on the pull
request's branch. Standing cost: one traced run (up to 60 min of runner, and
the push timeout) on every pull request that touches the job, or a seat step
to remember it. Recurrence: the enumerator
`git grep -c "event_name == 'push'" -- .github/workflows` returns 19 lines in
four files at `0362916ac`, the oldest arm from 2026-08-26 (`13aa7b189`,
tests.yml); this seat found one of them, #3315's, that broke on its first
push, and measured no other. Cost of this occurrence: 27 pushes, phase P1,
until #3375 merged about 17.5 h after #3315. One instance in roughly 2.5
months of push-only arms does not buy a standing 60-minute run per touching
PR, so none is built; the record stands until a second instance.

## 6. Verdict

- State: **(c)**.
- Cost test: **A and B both pass**; neither is built in this seat, which
  writes no production code. A changes `.github/workflows/`, which is
  code-owned, so it is drafted here for the owner, as `root-cause.md`
  section 5 requires; B is a `tools/pr/ci_predict.py` arm a fixer can build
  under ordinary review.
- 2d (a push-only arm first run on `main`): no countermeasure, recorded with
  its numbers in section 5.
- Shape 2 (event-dependent read sets) is not countered here: its instance is
  the hotfix's, and its enumerator is the `drift` step, which already fires
  on it.
