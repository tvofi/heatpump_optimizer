# R10-RCA-FLUSH-DISPATCH: the stamp's record flush dispatches all of Nightly to run one job

This is the root-cause seat for the owner's ruling of 2026-11-07: a stamp that
dispatches a whole Nightly run is a defect with hotfix priority. It follows
`root-cause.md` (under `dev/governance/roles/`) and
`dev/governance/rules/defect-root-cause.md`. It ran beside the fixer of
R10-FLY-STAMP-FLUSH-COST, never inside it, and edits neither
`tools/release/stamp.py` nor `.github/workflows/nightly.yml`. It was measured at
`origin/main` `516ad1b6b` on 2026-11-07, and the run figures come from the
Actions runs and jobs API after every run named below had concluded. Each
figure is reproduced by `dev/audit/harnesses/r10_rca_flush_dispatch.py`, with
the command beside it. The triage that ruled the fix is
`dev/programme/triage/s6-batch132.md#P404` on `origin/handoff/audit-r10-roster` (commit `6db424629`), not yet on main.

## 1. The defect, reproduced

`dispatch_record_beat` in `tools/release/stamp.py` posts `{"ref": "main"}` to
`actions/workflows/nightly.yml/dispatches`, with no inputs. In `nightly.yml`,
every heavy lane is gated on `github.event_name != 'push'`: `mutation-nightly`,
`mutation-ledger` (four shards), `slow` and `nightly-ha` (two arms). On
`workflow_dispatch` that condition is true. So a flush that wants one job,
`record-autofix`, starts ten. The stamp may send up to `FLUSH_MAX_DISPATCHES` =
3 per run.

Command: `python3 -I dev/audit/harnesses/r10_rca_flush_dispatch.py runs 42344537787 42346251204 42353878060 42357667261 42364230438 42367391498 42369836867`

| run | created | sha | runner-min | record-autofix min | shards ok | ledger-push | lost ledger min |
|---|---|---|---|---|---|---|---|
| 42344537787 | 05:52Z | be813ecd | 1053 | 1 | 4 | cancelled | 788 |
| 42346251204 | 06:16Z | be813ecd | 943 | 1 | 1 | cancelled | 127 |
| 42353878060 | 08:04Z | 0e9c508c | 410 | 1 | 0 | cancelled | 0 |
| 42357667261 | 08:57Z | 62bcca76 | 187 | 1 | 0 | cancelled | 0 |
| 42364230438 | 10:30Z | c9c88336 | 538 | 1 | 0 | cancelled | 0 |
| 42367391498 | 11:15Z | 08fd676e | 305 | 1 | 0 | cancelled | 0 |
| 42369836867 | 11:50Z | 08fd676e | 120 | 1 | 0 | cancelled | 0 |

`RESULT runs=7 runner_min=3557 record_autofix_min=6 cancelled=7 lost_ledger_min=916`

- A run's runner-minutes are the sum, over its jobs, of completed_at minus
  started_at, so a cancelled job counts up to its cancel. Each per-row
  `record-autofix` figure is rounded, which is why the sum prints 6.
- All seven ended `cancelled`. The four started before 09:00Z were cancelled at
  09:38Z to 09:43Z, the other three at about 12:09Z (`updated_at`). The triage
  counted four hand cancels because three runs were still in progress when it
  read them at 12:05Z.
- **Lost ledger work** is the minutes of `mutation-ledger` shards that ended
  `success` in a run whose `mutation-ledger-push` did not. That is 916
  runner-min across five finished shards in two runs, which never landed.
- **Null controls.** These come from the same harness:
  `runs 42320317707 42372556020`. 00:47Z's `schedule` run took 903 runner-min,
  its ledger push ended `success` and it lost 0. That is the cost Nightly is
  meant to pay, once a night. A `push` run on main, 42372556020, ran 0
  runner-min of lanes, because every heavy job skipped. So the instrument
  reads 0 lost where nothing was lost, and 0 lanes where the lanes skip.
- **Since the flush shipped.** Command: `since 2026-10-26T02:31:17Z`, from the
  merge of #2836.
  - It prints `RESULT runs=26 runner_min=15909 record_autofix_min=33 cancelled=7 lost_ledger_min=916`.
  - `since 2026-10-21T00:00:00Z`, from the day `nightly.yml` was created
    (`abf4f40b7`), prints the same 26. So no `workflow_dispatch` of
    `nightly.yml` ran in the five days before the flush shipped.
  - The 26 include any hand dispatch, because the API names `tvofi` as the actor
    on every run. So 15909 runner-min is an upper bound on the flush's share.
    The stamp logs the triage read attribute 5 of 11-07's 7 dispatches to the
    stamp.

## 2. The named cause

The flush rule treated a **job** as the unit of dispatch. The GitHub API
dispatches a **workflow**, and here the one job the rule wanted shares its
workflow with every heavy Nightly lane.

- **The rule's origin:** triage P88 (`dev/programme/triage/s6-batch19.md`,
  2026-10-24), risk (b). It reads: "The stamp step therefore dispatches
  `record-autofix` first and waits for its merge, which works because a
  dispatch run flushes whatever the count. That step goes in the carry."
- **The carry:** `dev/programme/rosters/wave-r10-groups.json`, group
  R10-FLOW-RECORD-PITCH. It says the same: "The stamp step dispatches
  `record-autofix` and waits for its merge."
- **P88's `Cost:` line** prices the batching change as "No new file, no API
  calls, no Pi cost". The stamp step is not priced at all.
- **The job's home:** `record-autofix` had moved into `nightly.yml` on
  2026-10-21 (`abf4f40b7`, R10-CI-LAYOUT PR 1). That was three days before P88,
  so the cost was already true when the rule was written. The rule did not
  change underneath it.
- **The implementation:** `6b1aa629f` (#2836 round 2, merged `28800999b`,
  2026-10-26) implemented the carry as written. Its author saw the cost and
  recorded it as a fact, not as a cost: `FLUSH_MAX_DISPATCHES` carries the
  comment "Open, merge, and one retry: each dispatch also runs every nightly
  lane." The PR body states the bound (`FLUSH_MAX_DISPATCHES` = 3) and gives no
  runner figure.

Which side moved, by `git log`: `nightly.yml`'s heavy-lane `if:` lines are those
of `abf4f40b7`, and `dispatch_record_beat` is unchanged since `6b1aa629f`. The
dispatch was added onto an existing workflow shape, not the reverse.

## 3. The process state: (c)

**(c) The process was followed and did not produce the intended result.**

The process is the triage cost gate, `dev/governance/roles/proposal-triage.md`
lines 11 to 16. A proposal is wired in only when its benefit clearly outweighs
"everything it adds", and the list includes "standing CPU on the Pi-class
target or CI runners".

- **It was present and obeyed.** P88 carries a `Cost:` line and a `Binding:`
  with measured savings. The seat priced what it believed it was adding: one
  dispatch of a one-minute job, in a risk note. Under that model, nothing was
  owed to the runner dimension.
- **It produced the wrong result** because the model's unit was wrong. Nothing
  in the gate turns "dispatch job X" into the set of jobs that dispatch
  actually runs. `proposal-triage.md` names CI runners as a dimension, but no
  line says how to price a workflow run a change triggers. The extractor's read
  of `proposal-triage.md`, `fixer.md` and `fix-review.md` found no such line in
  any of them.
- **Why the later gates passed it.** Each was obeyed, and none reads what the
  real dispatch starts:
  - **The fixer** (`fixer.md`) implemented the carry. It has no step that
    re-prices a cost the triage did not price. The every-lane fact went into a
    code comment, and no contract routes a comment back to a cost.
  - **The mutation proof and the self-tests.** Every `flush:` arm drives
    `record_flush` with a `dispatch=` double. None asserts the payload, and
    none reads `nightly.yml`. `dispatch_record_beat` itself is a network edge
    with a written triage as its disposition (#2836 body, `## Unpinned sites`).
    So mutants `stamp-3` and `stamp-4` and the reviewer's six killed mutants
    all exercise the loop around the dispatch, never what it starts.
  - **The fix review** (comment 6405493591 on #2836) answered the brief's
    questions about the train hold, the pitch and the re-dispatch bound. Its
    verdict was `merge`. It mentions no runner cost, because neither the brief
    nor `fix-review.md` asks for one.
  - **The approval** (#2836, review 5646765539) was an agent approval under the
    mandate, on the fix review's basis.

**Why not (b).** (b) would say the seat skipped the runner dimension, and a
firmer instruction ("price CI runners") would follow. The seat did not skip it.
It held a unit under which the runner cost was one minute. A firmer
instruction would have been obeyed with the same wrong unit, which is the
(c)-as-(b) error `root-cause.md` section 2 warns of.

**Why not (d).** No precondition changed after the rule was made, because the
job's move into `nightly.yml` preceded P88 by three days.

## 4. How far the class reaches

The class is a code caller that dispatches a workflow to get a subset of its
jobs, while the workflow runs more on that payload.

- **The rule that enumerates it:** `git grep` over the tree for `/dispatches`,
  `gh workflow run`, `createWorkflowDispatch` and `repository_dispatch`, then
  `yaml.safe_load` of every target's jobs and `if:`. Docs, comments and test
  fixtures are excluded.

| caller | target | payload | wants | runs more than it wants? |
|---|---|---|---|---|
| `.github/workflows/merge-main.yml` (job `merge-main`, step `dispatch`) | `ci.yml` | `-f pr -f base` | the PR's whole gate | no, the gate is the point |
| `tests.yml` `closures-autofix` | `ci.yml` | `-f pr -f base` | the whole gate after a bot commit | no |
| `tests.yml` `claims-autofix` | `ci.yml` | `-f pr -f base` | same | no |
| `tests.yml` `mutation-autofix` | `ci.yml` | `-f pr -f base` | same | no |
| `tools/audit/seat/merge_train.py` `DISPATCH` | `ci.yml` | `-f recheck=true` | the batch's gate re-proof | no; `ci.yml`'s prelude picks the workset from the inputs |
| `tools/release/stamp.py` `dispatch_record_beat` | `nightly.yml` | `{"ref": "main"}` | `record-autofix` | **yes: 10 jobs for 1, this defect** |
| `tools/audit/seat/ci_probe.py` `dispatch` | caller-chosen | caller-chosen `-f` | operator's choice | operator-invoked, no fixed want |

- **Reach: 1 of 7 code callers.** It is the only one dispatching a multi-lane
  workflow for one job.
- **Dispatch targets:** of the eight workflows that declare
  `workflow_dispatch`, only `ci.yml` and `nightly.yml` are dispatched by code.
- **`ci.yml`** dispatches carry inputs its prelude reads, and their callers
  want the gate.

## 5. The cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

**cost(defect), one occurrence.** One occurrence is one escaped caller, over its
life, for 12 days until the owner's ruling.

| measure | value | how measured |
|---|---|---|
| dispatches | 26 | harness, `since 2026-10-26T02:31:17Z` |
| runner time, upper bound | 15909 runner-min (265 runner-h) | same command |
| of which the wanted job | 33 min | same command |
| 11-07 dispatches | 7 | `runs` command |
| 11-07 runner time | 3557 runner-min | `runs` command |
| 11-07 hand cancels | 7 | `runs` command |
| finished ledger shards discarded | 916 runner-min | `runs` command |
| 11-07 seat time | the orchestrator's hand-cancel round | not measured |
| record pull requests queued behind their own dispatch | 35 to 70 min per flush, in the triage's reading | triage P404/P403, not re-measured here |

The figures above are runner time. In wall-clock, the triage *estimates* 3 to
6 h of fleet queue over the round's remaining stamps, while the concurrency
limit binds. That is an estimate, and it is the triage's (P404), not this
seat's measurement.

**P(recurrence) after the instance fix.** R10-FLY-STAMP-FLUSH-COST is bound by
P404 to do three things:

- add `inputs.lanes` (`all` or `beat`) to `nightly.yml`, so each heavy lane
  skips on `beat`;
- make `dispatch_record_beat` post `lanes=beat`, pinned by a payload self-test
  arm with a mutant that drops the input;
- add a `tests/entities.py` pin: every heavy job skips on `lanes=beat`, and
  `record-autofix` does not.

That closes the instance and the target. What is left is a *new* code caller
that wants a subset of a multi-lane workflow and omits its scoping input.

- **The measured class frequency** is 1 instance among 7 code callers, in the
  17 days `nightly.yml` has existed.
- No class in `dev/audit/config/bugclasses.json` concerns dispatch or runner
  cost.
- **The estimate:** at most one new subset-wanting dispatch caller per release
  cycle, and P(recurrence) at most 0.1 per cycle. The basis: 1 of 7 callers
  over round 10. Six of the seven want the whole workflow. And the one
  multi-lane target now carries a scoping input with a pin.
- **Expected cost:** 265 runner-h x 0.1, about 27 runner-h per cycle, as an
  upper bound, because the next escape would meet a `lanes` input already in
  place.

**Countermeasure A: a generic dispatch-scope check.**

- **What it is:** a registry of every code dispatch caller with the jobs it
  wants. The check evaluates each target job's `if:` under the caller's payload
  and refuses where the run set exceeds the want.
- **Standing cost:** under 1 s per gate run.
- **Bound cost:**
  - an expression evaluator for `if:` lines that read `needs.prelude.outputs.*`,
    which `ci.yml`'s five callers do. Those can only be registered as "wants
    all", so the check would carry its verdict for 5 of 7 callers;
  - a registry beside a 30k-line code-owned `tests/entities.py` that
    R10-FLY-STAMP-FLUSH-COST is editing now.
- **Benefit:** it protects one residual shape whose measured reach outside the
  instance is zero.
- **Verdict: refused under the bound** (`defect-root-cause.md`, "The bound").
  The complexity it adds exceeds what it can prevent once the instance pin
  lands. A check registering 5 of 7 callers as "wants all" would read green by
  declaration, the shape "A detector must be shown to detect" warns of.
- **Measured on a built candidate, then withdrawn.** An earlier run of this
  seat built this check, at step `50a672627` on
  `handoff-wip/r10-rca-flush-dispatch`. Its parts:
  - `tools/audit/seat/dispatch_scope.py`, 254 lines, with a regex-rewritten
    `eval` of each `if:`;
  - 7 lines in `governance.yml` running its `--self-test` only.

  This run measured it, with its file copied into the tree and then removed:
  - `--check` on `origin/main` prints `REFUSE: tools/release/stamp.py:
    dispatching nightly.yml wants ['record-autofix'] but also runs
    ['mutation-nightly', 'mutation-ledger', 'mutation-ledger-push', 'slow',
    'nightly-ha']`. That is a true red on the defect.
  - So `--check` could not be wired into CI before R10-FLY-STAMP-FLUSH-COST
    merges, and wired as `--self-test` alone it reads no call site in the tree.
  - Its `call_sites()` returned 8 sites and **no `merge_train.py`**.
    `python3 -I -c '...d.call_sites(d.ROOT)'` printed `merge_train found: False`.
    Yet `merge_train.py`'s `DISPATCH = (("ci.yml", ("-f", "recheck=true")),)`
    is a live `ci.yml` dispatch, run by `launch()`. A caller written as an argv
    tuple is invisible to its regex enumeration, so its "unregistered call
    site" arm reads green on a real unregistered caller.

  That is the bound's verdict made concrete. The check is withdrawn in this
  diff, and its fixtures are not kept.

**Countermeasure B: proposed, not landed.**

- **What it is:** a one-line addition to `proposal-triage.md`'s cost paragraph,
  addressing state (c):

  > A change that dispatches a workflow is priced by the jobs that dispatch
  > runs (each job's `if:` under the payload), in runner-minutes from the jobs
  > API on a recent run of that workflow, not by the job it wants.

- **Standing cost:** one jobs-API read per proposal that dispatches. On the
  round's record, that is under one proposal per cycle, a few seconds.
- **Expected benefit:** about 27 runner-h per cycle, from above.
- **Verdict: passes the test.**
- It is **policy**, so this seat does not land it (`CLAUDE.md`; `root-cause.md`
  section 5). It is proposed for the owner's decision.
- It changes the gate's unit, not the strength of its instruction. That makes
  it the (c) countermeasure, not a (b) one.

**No check is built by this seat.** So there is no red-on-defect and
green-on-fix demonstration owed here. The instance's check is the sibling's
entities pin and payload arm, and their red, green and null runs are that pull
request's.

## 6. Result

- **State:** (c). The triage cost gate was obeyed, and its unit, a job, was not
  what the dispatch API runs, a workflow.
- **The cost test:**
  - a generic check is refused under the bound, with reach 1 of 7 and the
    instance pin in R10-FLY-STAMP-FLUSH-COST;
  - the triage cost line passes, at about 27 runner-h per cycle against seconds,
    and is proposed to the owner.
- **The class:** `N-dispatch-overreach` in `dev/audit/config/bugclasses.json`,
  status `open`, with this document as its `_rca` `R10-RCA-FLUSH-DISPATCH`.
- **Reopen it** on a second code caller whose dispatch runs jobs it does not
  want.
- **The defect's issue:** this seat was told to post no comment. The
  **Root cause** section `defect-root-cause.md` asks for on the issue is
  therefore left to the orchestrator, who can copy this section.

## 7. Re-measured after the instance fix (R10-RCA-STAMP-FLUSH-COST)

A second root-cause seat, dispatched for the same owner ruling under the topic
R10-RCA-STAMP-FLUSH-COST, re-measured this document at `origin/main`
`73365699a` on 2026-11-08. That commit carries the instance fix, #3296 (merged
`341da0721`, 2026-11-08T04:48:27Z). The seat writes no second document: one
defect has one RCA, so its findings land here. Sections 2 to 6 stand: the cause,
state (c), the reach and the cost-test verdicts are unchanged.

- **One dispatch came after section 1's measurement.** Command:
  `python3 -I dev/audit/harnesses/r10_rca_flush_dispatch.py runs 42382408131`
  prints `RESULT runs=1 runner_min=1007 record_autofix_min=1 cancelled=0 lost_ledger_min=0`.
  The run was created at 2026-11-07T14:36:39Z, before #3296 merged, and ran
  every lane to `success`. No release tag follows it (`v7.1.5` was cut at
  12:27Z), so this seat cannot attribute it to the stamp. It counts toward the
  upper bound only.
- **Since the flush shipped, corrected.** Command:
  `since 2026-10-26T02:31:17Z` now prints
  `RESULT runs=27 runner_min=16916 record_autofix_min=34 cancelled=7 lost_ledger_min=916`.
  That is section 1's 26 runs and 15909 runner-min plus the one run above. So
  2026-11-07 had 8 dispatches and 4564 runner-min, not 7 and 3557. Of those 8,
  the 7 cancelled runs are the ones section 1 lists. The figures in section 5
  move by the same 1007 runner-min. P(recurrence) at 0.1 per cycle gives about
  28 runner-h per cycle, against section 5's 27. Neither verdict changes.
- **No dispatch since the fix.** Command: `since 2026-11-08T04:48:27Z` prints
  `RESULT runs=0`. As a null control, the same instrument found 27 dispatches
  in the window above, so 0 is a reading rather than a blind read. The fix's
  `lanes=beat` payload has not yet run in production. The next stamp's flush is
  the first one: a run titled `Nightly record beat` that has `record-autofix`
  as its only non-skipped job.
- **The fix as landed.** At `73365699a`, `tools/release/stamp.py` has
  `RECORD_BEAT_PAYLOAD = {"ref": "main", "inputs": {"lanes": "beat"}}`. At the
  fix's merge base `d2e4d2d10`, the post was `json.dumps({"ref": "main"})`.
  The `nightly.yml` `lanes` input and the `tests/entities.py` pin that section
  5 premised P(recurrence) on are both in the tree.
- **The class search, re-run.** Section 4's `git grep` rule, at `73365699a`,
  finds the same code callers, and no new ones:
  - `merge-main.yml`;
  - the three `tests.yml` autofix jobs;
  - `ci_probe.py`;
  - `stamp.py`.

  `merge_train.py`'s argv-tuple `DISPATCH` is still invisible to the grep, as
  section 5 recorded, and is still in section 4's table. The one remaining
  every-lane form is the hand recipe in `nightly.yml`'s header comment,
  `gh workflow run nightly.yml --ref main`, which verifies a red. It wants
  every lane. `stamp.py` names its one-lane hand form,
  `gh workflow run nightly.yml -f lanes=beat`.
- **Still owed:** the owner's decision on section 5's `proposal-triage.md` line
  (`_rca` `parts_missing`), and the **Root cause** section on the defect's
  issue, which section 6 left to the orchestrator.
