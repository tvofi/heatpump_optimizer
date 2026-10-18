Design review: revise

Round-2 re-review seat for group R10-CI-LAYOUT. Independent: neither a designer nor the
revision author. Reviewed:
- revision 1, `probe/design-ci-rev1` at `485ae940` (`DESIGN-P1.md`, `DESIGN-P2.md`,
  `RESPONSE.md`, `measure/`), cited `P2:<line>` and `P1:<line>`;
- against round 1, `probe/design-ci-review` at `f7b28312` (12 items, verdict revise);
- originals `b7a76185` and `7fdd39c4` for context.

Policy read from `origin/main` (`89e33859`): `CLAUDE.md`, `judge.md`, `fix-review.md`,
`ci-autofix.md`, `gate-scoping.md`, `orchestrator.md`. Main has moved 3 commits since the
revision's tree `07a09406` (#2423: `tools/policy/agreement.mjs`, `agreement_py.py` and
`policy_lint.mjs`). All three are section 9 readers, so the fixer re-reads those rows
at the then-current main. Nothing else in the revision depends on those commits.

Every command below was run by this seat. This seat's own instruments are under
`tools/` and its outputs under `ev/`, each one disclosed as this seat's
(`fix-review.md` step 9).

## Re-runs of every changed instrument

Each re-run is byte-identical to its committed output (`ev/reruns/`):
- `gate_sim.py`: `GATE-SIM rc 0`;
- `gate_replay2.py measure/p2/raw measure/rev/reaches_cc.txt`: `GATE-REPLAY2 rc 0`, 22/22;
- `verdict_wait.py`: 8.07 runner-hours;
- `check_writers.py`;
- `unitcheck2.py self-test …`: `SELF-TEST ok (12/12)`;
- `c1_counterfactual.py` at `--boost 480` and at `--sweep`.

Two outputs differ from a committed file, and both differences are as stated:
- `c1_counterfactual.py` at the default equals phase 2's `c1_counterfactual.txt` plus the
  one `boost charged 239.1 s` line. At 480 s it equals round 1's
  `c1_counterfactual_boost_480.txt` plus that line.
- `c1_consumers.sh 07a09406` equals `c1_consumers.txt`, and `origin/main` gives the same
  output.

The numbers reproduce. The findings below concern what the simulator models and what
GitHub actually does.

## The twelve items

| item | verdict | short reason |
|---|---|---|
| 1 | resolved as stated; **reopened by N1** | case E is fixed by separate lanes. But the new `refresh`/sweep re-runs re-enter those lanes and cancel live runs, including code runs, on events anyone can cause |
| 2 | **resolved** | applicability comes from the event; the prelude must succeed and agree; kind is read from `run-name` (M-1); sources must be at the live base. Plants B–B4, I2 and I3 are refused (re-run) |
| 3 | **resolved** | every code unit is guarded on `needs.prelude.outputs.kind == 'code'` (P2:228-234); cases C and D3 pass |
| 4 | **not resolved** | under the every-suite reading (the reason the sweep exists), convergence depends on a simulator artefact (N2). With faithful re-run timing, a common sequence ends red under all three readings |
| 5 | **not resolved** | the wait polls `code-scanning/analyses?ref=…&sha=<head>`, and that endpoint has no `sha` parameter; a PR analysis is recorded on `refs/pull/N/merge`. So the wait is satisfied by an earlier head's analysis, or by none (detail below) |
| 6 | **resolved** | the approvals are kept and retargeted; M-3 is specified; the tool, `nudge.md:85`, `INSTRUMENTS.md:36` and `hpo-runs` are named (P2:691-715) |
| 7 | **resolved** | four inputs on `ci.yml` and on the stub, passed as `workflow_call` inputs; `DISPATCH` keeps `-f recheck=true` (P2:172-176, 218, 847) |
| 8 | **resolved** | W1 is made at its source in PR 1 (P1 2(c), P1:491-493); `c1_consumers.sh` reproduces (10 files); the numbers are at measured cost; "upper bound" and "as fast" are withdrawn |
| 9 | resolved for every plant round 1 named; **new hole N3** | the static half refuses round 1's P1, P2 and P3 (re-run). It is blind to step **order** |
| 10 | **resolved** for `gate_replay2` (it imports `gate_model.gate`) | the hooks' null control, `gate_sim`, is itself defective (N2) |
| 11 | **not resolved** (small) | two keyed readers of the `pr-contract` check name are missed: `tools/pr/prepr.sh:935-938` and `tests/entities.py:25883-25893` (N4) |
| 12 | **resolved** | (a) P2:790-793; (b) P2:145-149; (c) P2:506-509, with the replay rows; (d) P2:919; (e) P2:664-671 |

### Item 5 in detail

- **The `sha` parameter.** P2:545-546 polls
  `GET code-scanning/analyses?ref=<PR ref>&sha=<head>`. The documented parameters are
  `tool_name`, `tool_guid`, `page`, `per_page`, `pr`, `ref`, `sarif_id`, `direction` and
  `sort`; there is **no `sha`** (`ev/gh_docs_read_2026-10-18.md`).
- **Which commit an analysis is on.** `codeql.yml`'s analyze job checks out with the
  default ref (`.github/workflows/codeql.yml:198-204`). On `pull_request` that is the
  test merge, and PR analyses are listed under `refs/pull/<number>/merge` (same docs).
- **Effect, either way:**
  - If an unknown parameter is ignored, the first analysis of a category on a PR
    satisfies every later wait at every later head. The wait guards only a PR's first
    push.
  - If the fixer instead matches `commit_sha` to the head, it never matches. Every
    `pr-contract` then times out after 10 minutes and fails closed.
- **Edit runs.** On an edit run, P2:544 says "the carried code run's" uploads, so the
  merge-commit SHA to match is the source run's `github.sha`. The design does not say
  so.
- **What `check_writers.py` measures.** It times the `CodeQL` check against the
  *Analyze job's* end (P2:116-118). It does not time it against when an analysis becomes
  listable. So the claim "analysis exists ⇒ check concluded" is unmeasured.
- **Required:**
  - wait on the thing `pr-contract` actually lists: the `CodeQL` check run of app
    `github-advanced-security` at the head, `completed`, with `completed_at` after the
    newest `Analyze (*)` job's completion in the source run;
  - or, if the analyses route is kept, specify it as `ref=refs/pull/N/merge` matched on
    `commit_sha ==` the source run's `github.sha`, and measure the lag from analysis to
    check in U6.

## New defects the revision introduced

### N1 (blocking): `refresh` and `gate-sweep.yml` re-run a `gate` job, and a re-run re-enters its run's lane

**The mechanism.**
- A re-run is a new attempt of the same run, under the run's original event and
  concurrency key.
- The tree measured that such an attempt takes part in its group.
  - `dev/audit/rca/R9-RC-PRCONTRACT.md:84-86` and `:188`, `:227` ("a rerunner inherits
    the group").
  - This seat read both runs back through the API (`ev/rerun_group_runs_api.json`).
    PR contract run `37315758446` was created 13:18:18Z. Its **attempt 4**, by `tvofi`,
    started 14:24:27Z and cancelled the **newer** run `37324419853` (created 14:24:15Z)
    of the same group at 14:24:37Z.
- GitHub's re-run documentation says nothing about concurrency
  (`ev/gh_docs_read_2026-10-18.md`). The tree's measurement is the only evidence, and it
  says the attempt joins the group.

**Why it bites here.** The revision puts every non-bot PR event in a per-PR lane with
`cancel-in-progress: true` (P2:186-199). Then:
- `refresh` (P2:255-261) re-runs the green `gate` of every completed run at the head;
- the sweep (P2:567-576) re-runs the red ones;
- so each re-run attempt cancels whatever is running in that lane.

**Simulated.** `tools/rerun_concurrency_sim.py` is revision 1's own `gate_sim.World`
plus exactly this one rule (`ev/rerun_concurrency_sim.txt`).
- The revision's model has 0 BAD rows; with re-runs in their group there are 3.
- **C, and R1: every retarget after a green code run.** The retarget's own `refresh`
  re-runs the old code run's `gate`. That attempt cancels the retarget's code run. No
  run ever judges the new base, so the PR is red under all three readings until the next
  push. This is deterministic, not a race.
- **R7: a second review after a green review run.** The new review run's `refresh`
  re-runs the older review run's `gate`, which cancels the new review run. The PR ends
  red. The owner's variant ("a review re-runs only `budget-raise-gate` and `gate`") then
  cannot pass on a re-review.
- **No false green was found.** Cancelled sources fail closed. These are liveness
  failures of exactly the case-E kind that item 1 was raised about.

**Item 1's outside-actor concern returns.** A review is an event anyone can cause. When
a review lands while a same-head code run is in flight (a retarget or a reopen), its
`refresh` re-runs the older code run's `gate` into the code lane and cancels that code
run.

**Across heads.** The lanes are per PR, not per head. A sweep that re-runs an old
head's code-run `gate` cancels a new head's code run in `CI-code-<pr>`
(`tools/sweep_crosshead.py`, `ev/sweep_crosshead.txt`).
- The simulator overstates this case: it lacks the sweep's "at a PR head" check.
- In reality the exposure is the window between that check and the re-run request.
- Still, the design names no guard for it.

**Required:**
- The re-run hooks must never re-enter a lane that can hold a live run.
- One shape that removes both this and item 1's pending-slot rule: give every
  `ci.yml` run a run-id `concurrency` group, and supersede within a lane with the
  tree's own `cancel_superseded.py`, keyed on the `display_title` lane, head and base.
  A re-run then joins a group of its own.
- Whatever is chosen:
  - add the re-run-joins-its-group rule to `gate_sim.py`;
  - add a new measurement, **M-5**, in U0: does a re-run attempt's `cancel-in-progress`
    cancel a newer run of its group on `ci.yml`;
  - add both to R-7.

### N2 (blocking): `gate_sim.py` finishes a hook re-run twice, which hides a mutual defer

**The simulator bug.**
- `hooks()` flips an old run to `in_progress` and schedules its `gate` 15 s later.
- But `step_run()` sees the same run `in_progress` with its old `gate_at`, and finishes
  the gate on the very next tick.
- Shown by `tools/rerun_status_fix.py`: in the scenario "edit, then review, during a
  code run", both re-run gates finish at t = 2203. They were re-run at 2202.
- So two gates that one sweep re-runs together never see each other as running.

**With faithful timing**, two arms (`ev/rerun_status_fix.txt`):
- FIXED: the attempt is `in_progress` for its 15 s;
- FIXED+SNAP: each due gate reads the same API state.

Under both, the sweep after the review run's green `gate` re-runs the code run's and the
edit run's red gates **at once**. 4.1's defer rule ("any other run at this head not
completed → FAIL", P2:468-469) then fails each on the other:
- X1 (edit and review 1 s apart during the code run) ends **red under all three
  readings**;
- so does X3 (600 s apart).
- No green completion follows, so no sweep follows. With a re-run attempt in progress,
  whether or not a hook's own re-run fires `gate-sweep.yml` again only changes which
  arm fails.
- 13 of 14 measured edits and 7 reviews arrive during code runs (P2:103-108), so this is
  the common path. It is not an edge case.
- Revision 1's "16/16 under each reading" and the ablation row (sweep load-bearing,
  9/16) both rest on the artefact.

**Required:**
- fix the simulator;
- make concurrent re-judgements unable to defer on each other. For example, the defer
  rule ignores a run whose only unfinished job is a `gate` attempt, or the sweep re-runs
  one gate at a time, newest first, and continues on its completion;
- re-score all three readings.

**Bound the attempts.** GitHub caps a run at 50 re-runs. The 51st gives "a failed check
suite", which is a red under the every-suite reading (`ev/gh_docs_read_2026-10-18.md`).
- `refresh` and the sweep add up to two attempts to every older run at a head per
  verdict event.
- The design must state that bound and what `gate.py` does near it.

### N3 (required, small): the static half of `unitcheck2.py` is blind to step order

Rows are keyed `<job>|<step name>` and compared as sets. The runtime half compares sets
too (`unitcheck2.py:140-180`). `tools/plant_unitcheck2.py` (`ev/plant_unitcheck2.txt`)
shows:
- Q1, swapping `coverage`'s "Key the per-script coverage" and "Restore the base's
  per-script coverage": **rc 0**;
- Q1b, moving the restore step to the end of the job: **rc 0**;
- Q2, the control (a step moved across jobs), is refused, and the null passes.

Order is semantic: a guard moved after what it guards, or a restore moved after the
program it restores. **Required:** hash the ordered list of step keys into each job
row, and add Q1 to the self-test.

### N4 (item 11 residual): readers of the `pr-contract` check name that section 9 does not list

Under the naming rule the check becomes `pr-contract / pr-contract` (P2:142-143).
- `tools/pr/prepr.sh:935-938` `REDS_JQ` excludes `.name != "pr-contract"` and nothing
  else. After PR 2 the local check would:
  - ask every body to answer its own contract red;
  - ask it to answer every red `gate`, which R-9 (P2:980-983) makes routine.
  The design excludes `gate` only in `pr-contract.yml` (P2:853).
- `tests/entities.py:25883-25893` pins `_PC_EXCLUSION = '.name != "pr-contract"'` as
  a substring of the contract job. That pin keeps passing on an exclusion that no longer
  excludes anything: the deadlock it exists to prevent.

`ev/readers_diff_rev1.txt` re-runs round 1's survey against the revised corpus. It lists
these only under the fixture/doc rows of `readers_triage.txt`; both are keyed.

**Required:** add both to section 9. `pr-contract.yml`, `prepr.sh` and the pin exclude
`pr-contract / pr-contract` and `gate`, and the pin checks both strings.

## Owner rulings: carried?

- **D-1 (approve): carried.** The refused branch is also specified (P2:679-689,
  P1 section 5).
- **D-2 (`arch-score` gate-required when the diff reaches `custom_components/`):
  carried.**
  - `REQUIRED` gives `arch-score` only on reach (P2:455);
  - the gate computes reach itself from a three-dot diff (P2:741);
  - `gate_replay2` shows red with reach FAIL and red without reach pass (re-run);
  - U7 plants both.
- **D-3 (keep `merge_group`): carried.** It is in `on:` (P2:170) with a run-id lane;
  `gate_model` takes the base from the queue on `merge_group`; P2:534.
- **D-4 (drop C1 in PR 1 only if the proof is shown covered): carried.**
  - `composed-proof` (`tests.yml:2766-2826`) compares a traced consume against a bare
    recording. With the producer, the consumers and `composed_proof.sh` all deleted
    (P1:491-493), nothing is left for that property to hold over.
  - `c1_consumers.sh HEAD` at PR 1's head is the stated proof, and the new `entities.py`
    pin keeps it.
- **D-5 (keep O17 with a soundness check): carried**, as U3's extracted-archive check,
  shown failing when `.py` joins python's INERT list (P2:738, P2:913).
- **Variant (a review re-runs only `budget-raise-gate` and `gate`): carried in
  `WORKSET`** (P2:459).
  - `refresh` and the sweep re-run only `gate` jobs, which is consistent with the
    variant.
  - But N1 (R7) makes a second review unable to pass.
- **Two PRs, phase 1 first; a cloud fan-out per unit: carried** (P2 sections 8 and 10;
  the stub in P1:494-502).

## What would turn this into approve

1. **N1:** re-runs cannot cancel live runs, by design and in the simulator; M-5 is added.
2. **N2:** the simulator is fixed; concurrent re-judgements cannot defer on each other;
   the three readings are re-scored; the 50-attempt bound is stated.
3. **Item 5:** wait on the code-scanning check run, or on a correctly keyed analyses
   query; the lag is measured in U6.
4. **N3:** step order is in the static half, with Q1 added to the self-test.
5. **N4:** the two readers are in section 9.

Everything else in revision 1 stands. Item 4's `gate-sweep.yml` and M-2 are the right
shape once N1 and N2 hold.

## This seat's instruments

| command | prints |
|---|---|
| `python3 -I tools/rerun_concurrency_sim.py <rev1>/measure/rev` | `ev/rerun_concurrency_sim.txt` (N1) |
| `python3 -I tools/sweep_crosshead.py <rev1>/measure/rev` | `ev/sweep_crosshead.txt` (N1, across heads; overstated, see N1) |
| `python3 -I tools/rerun_status_fix.py <rev1>/measure/rev` | `ev/rerun_status_fix.txt` (N2: AS-IS, FIXED and FIXED+SNAP arms, each with and without chaining) |
| `python3 -I tools/plant_unitcheck2.py <rev1>/measure/rev/unitcheck2.py <rev1>/measure/rev/fixtures/tests.yml` | `ev/plant_unitcheck2.txt` (N3) |
| round 1's `readers_diff.sh` over the revised corpus | `ev/readers_diff_rev1.txt` (N4) |
| GitHub MCP `get_workflow_run` 37315758446, 37324419853 | `ev/rerun_group_runs_api.json` |
| docs reads | `ev/gh_docs_read_2026-10-18.md` |

`<rev1>` is a checkout of `probe/design-ci-rev1` (`git archive 485ae940`).
